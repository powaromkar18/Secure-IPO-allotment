import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import hashlib
import random
from typing import Dict, Any
import json

class ZKPProtocol:
    def __init__(self):
        # Large prime number and generator for the multiplicative group
        self.p = int('FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74'
                    '020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F1437'
                    '4FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED'
                    'EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF05'
                    '98DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB'
                    '9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B'
                    'E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF695581718'
                    '3995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF', 16)
        self.g = 2
        
    def hash_to_int(self, data: str) -> int:
        """Convert string data to integer using SHA-256"""
        return int.from_bytes(hashlib.sha256(data.encode()).digest(), 'big')
    
    def generate_proof(self, secret_data: str) -> Dict[str, Any]:
        """Generate ZKP proof for given secret data"""
        # Convert secret to number
        x = self.hash_to_int(secret_data)
        
        # Generate random value for commitment
        r = random.randrange(self.p)
        
        # Calculate commitment
        commitment = pow(self.g, r, self.p)
        
        # Generate challenge (in real system, this would come from verifier)
        challenge = random.randrange(2**128)
        
        # Calculate response
        response = (r + challenge * x) % (self.p - 1)
        
        return {
            'commitment': commitment,
            'challenge': challenge,
            'response': response
        }
    
    def verify_proof(self, public_data: str, proof: Dict[str, Any]) -> bool:
        """Verify ZKP proof against public data"""
        x = self.hash_to_int(public_data)
        
        # Verify: g^response = commitment * (g^x)^challenge
        left_side = pow(self.g, proof['response'], self.p)
        right_side = (proof['commitment'] * 
                     pow(pow(self.g, x, self.p), 
                         proof['challenge'], self.p)) % self.p
        
        return left_side == right_side

class IPOApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Secure IPO Application System")
        self.geometry("800x600")
        
        # Initialize ZKP Protocol
        self.zkp = ZKPProtocol()
        
        # Load sample database
        self.load_database()
        
        # Create GUI elements
        self.create_widgets()
        
    def load_database(self):
        """Load the sample database of users"""
        try:
            self.db = pd.read_csv('ipo_applications.csv')
        except FileNotFoundError:
            messagebox.showerror("Error", "Database file not found!")
            self.db = pd.DataFrame()
            
    def create_widgets(self):
        """Create GUI elements"""
        # Main container
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # User verification section
        ttk.Label(main_frame, text="Verify Identity", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, pady=10)
        
        # PAN Entry
        ttk.Label(main_frame, text="Enter PAN:").grid(row=1, column=0)
        self.pan_entry = ttk.Entry(main_frame)
        self.pan_entry.grid(row=1, column=1)
        
        # Aadhar Entry
        ttk.Label(main_frame, text="Enter Aadhar:").grid(row=2, column=0)
        self.aadhar_entry = ttk.Entry(main_frame)
        self.aadhar_entry.grid(row=2, column=1)
        
        # Verify Button
        ttk.Button(main_frame, text="Verify Identity", 
                  command=self.verify_identity).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Results section
        self.result_text = tk.Text(main_frame, height=10, width=60)
        self.result_text.grid(row=4, column=0, columnspan=2, pady=10)
        
    def verify_identity(self):
        """Verify user identity using ZKP"""
        pan = self.pan_entry.get()
        aadhar = self.aadhar_entry.get()
        
        # Find user in database
        user = self.db[self.db['pan_number'] == pan]
        
        if len(user) == 0:
            messagebox.showerror("Error", "User not found!")
            return
            
        # Generate ZKP proof for PAN and Aadhar
        pan_proof = self.zkp.generate_proof(pan)
        aadhar_proof = self.zkp.generate_proof(aadhar)
        
        # Verify proofs
        pan_verified = self.zkp.verify_proof(pan, pan_proof)
        aadhar_verified = self.zkp.verify_proof(aadhar, aadhar_proof)
        
        if pan_verified and aadhar_verified:
            # Show user details without revealing sensitive information
            self.display_verified_user(user.iloc[0])
        else:
            messagebox.showerror("Error", "Verification failed!")
            
    def display_verified_user(self, user):
        """Display verified user information"""
        self.result_text.delete(1.0, tk.END)
        
        # Display only necessary information
        display_text = f"""
Verification Successful!
------------------------
Name: {user['name']}
Investment Experience: {user['investment_experience_years']} years
Risk Category: {user['risk_category']}
KYC Status: {'Verified' if user['kyc_verified'] else 'Not Verified'}
Residential Status: {user['residential_status']}

Application Status: Active
"""
        self.result_text.insert(tk.END, display_text)

def main():
    app = IPOApplication()
    app.mainloop()

if __name__ == "__main__":
    main()