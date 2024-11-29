import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import hashlib
import random

class ZKPVerification:
    def __init__(self):
        self.p = int('FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BBE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF', 16)
        self.g = 2

    def create_proof(self, secret_data):
        x = int.from_bytes(hashlib.sha256(secret_data.encode()).digest(), 'big')
        r = random.randrange(self.p)
        commitment = pow(self.g, r, self.p)
        challenge = random.randrange(2**128)
        return {'commitment': commitment, 'challenge': challenge, 'response': (r + challenge * x) % (self.p - 1)}

    def verify_proof(self, public_data, proof):
        x = int.from_bytes(hashlib.sha256(public_data.encode()).digest(), 'big')
        return pow(self.g, proof['response'], self.p) == (proof['commitment'] * pow(pow(self.g, x, self.p), proof['challenge'], self.p)) % self.p

class UnifiedIPOSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IPO Allotment Status System")
        self.geometry("1200x800")
        self.zkp = ZKPVerification()
        
        try:
            self.db = pd.read_csv('ipo_applications.csv')
            self.db['ipo_alloted'] = [random.choice([True, False]) for _ in range(len(self.db))]
        except FileNotFoundError:
            messagebox.showerror("Error", "Database not found!")
            self.db = pd.DataFrame()
        
        self.setup_gui()
        self.load_sample_data()

    def setup_gui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create IPO tabs
        for tab_name in ["Mainboard IPO", "SME IPO"]:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=tab_name)
            
            # Search frame
            search_frame = ttk.Frame(frame)
            search_frame.pack(fill='x', padx=5, pady=5)
            ttk.Entry(search_frame).pack(side='left', expand=True, fill='x', padx=5)
            
            # Table frame
            table_frame = ttk.Frame(frame)
            table_frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            columns = ('Company Name', 'Issue Open', 'Issue Close', 'Price Band (₹)', 'Lot Size', 'Issue Size (Cr)', 'Status')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
            scrollbar.pack(side='right', fill='y')
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Application form frame (initially hidden)
            form_frame = ttk.LabelFrame(frame, text="Application Form", padding="10")
            form_frame.pack(fill='x', padx=5, pady=5)
            form_frame.pack_forget()  # Initially hidden
            
            # Store frames and trees as attributes
            setattr(self, f"{tab_name.lower().replace(' ', '_')}_tree", tree)
            setattr(self, f"{tab_name.lower().replace(' ', '_')}_form", form_frame)
            
            # Bind click event for both tabs
            tree.bind('<<TreeviewSelect>>', 
                     lambda e, tab=tab_name: self.show_application_form(e, tab))

        # Status check tab
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Check Status")
        
        content_frame = ttk.Frame(status_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10)
        
        self.pan_entry = ttk.Entry(input_frame)
        self.aadhar_entry = ttk.Entry(input_frame)
        ttk.Label(input_frame, text="Enter PAN:").grid(row=0, column=0, padx=5)
        self.pan_entry.grid(row=0, column=1, padx=5)
        ttk.Label(input_frame, text="Enter Aadhar:").grid(row=1, column=0, padx=5)
        self.aadhar_entry.grid(row=1, column=1, padx=5)
        
        ttk.Button(content_frame, text="Check Status", command=self.verify_status).pack(pady=20)
        self.status_label = ttk.Label(content_frame, text="", font=('Helvetica', 12))
        self.status_label.pack(pady=10)

        # Analysis tab
        self.setup_analysis_tab()

    def setup_analysis_tab(self):
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis")
        
        stats_frame = ttk.LabelFrame(analysis_frame, text="Market Statistics")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        stats = [
            ("Total Active IPOs:", "15"),
            ("Average Issue Size:", "₹4,500 Cr"),
            ("Success Rate:", "75%"),
            ("Average Subscription:", "12.5x")
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(stats_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky='e')
            ttk.Label(stats_frame, text=value).grid(row=i, column=1, padx=5, pady=2, sticky='w')

    def show_application_form(self, event, tab_name):
        tree = getattr(self, f"{tab_name.lower().replace(' ', '_')}_tree")
        form_frame = getattr(self, f"{tab_name.lower().replace(' ', '_')}_form")
        
        # Clear previous form contents
        for widget in form_frame.winfo_children():
            widget.destroy()
        
        selected_item = tree.selection()
        if not selected_item:
            form_frame.pack_forget()
            return
        
        # Get selected company details
        company_data = tree.item(selected_item[0])['values']
        company_name = company_data[0]
        price_band = company_data[3]
        min_lot_size = int(company_data[4])
        
        # Show the form frame
        form_frame.pack(fill='x', padx=5, pady=5)
        
        # Create form content
        content_frame = ttk.Frame(form_frame)
        content_frame.pack(expand=True, fill='x')
        
        # Company details
        details_frame = ttk.Frame(content_frame)
        details_frame.pack(fill='x', pady=5)
        
        ttk.Label(details_frame, text=f"Company: {company_name}", font=('Helvetica', 10, 'bold')).pack(side='left', padx=10)
        ttk.Label(details_frame, text=f"Price Band: {price_band}", font=('Helvetica', 10)).pack(side='left', padx=10)
        
        # Input frame
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_frame, text="Number of Lots:").pack(side='left', padx=5)
        lot_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=5)
        lot_spinbox.pack(side='left', padx=5)
        
        # Amount frame
        amount_frame = ttk.Frame(content_frame)
        amount_frame.pack(fill='x', pady=5)
        
        amount_label = ttk.Label(amount_frame, text="Total Amount: ₹0.00")
        amount_label.pack(side='left', padx=5)
        
        def calculate_amount():
            try:
                lots = int(lot_spinbox.get())
                price = float(price_band.split('-')[1].replace('₹', '').replace(',', ''))
                total = lots * min_lot_size * price
                amount_label.config(text=f"Total Amount: ₹{total:,.2f}")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number of lots")
        
        # Button frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Calculate Amount", command=calculate_amount).pack(side='left', padx=5)
        
        def submit_application():
            try:
                lots = int(lot_spinbox.get())
                total = lots * min_lot_size * float(price_band.split('-')[1].replace('₹', '').replace(',', ''))
                messagebox.showinfo("Success", 
                    f"Application submitted successfully!\n\n"
                    f"Company: {company_name}\n"
                    f"Lots: {lots}\n"
                    f"Shares: {lots * min_lot_size}\n"
                    f"Total Amount: ₹{total:,.2f}"
                )
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number of lots")
        
        ttk.Button(button_frame, text="Submit Application", command=submit_application).pack(side='left', padx=5)


    def verify_status(self):
        pan = self.pan_entry.get().strip().upper()
        aadhar = self.aadhar_entry.get().strip().upper()
        
        if not pan or not aadhar:
            self.status_label.config(text="Please enter both PAN and Aadhar numbers", foreground="red")
            return
        
        try:
            if self.zkp.verify_proof(pan, self.zkp.create_proof(pan)) and self.zkp.verify_proof(aadhar, self.zkp.create_proof(aadhar)):
                user = self.db[self.db['pan_number'] == pan]
                if len(user) > 0:
                    is_alloted = user.iloc[0]['ipo_alloted']
                    self.status_label.config(
                        text=f"Congratulations! Your IPO application is {'ALLOTED' if is_alloted else 'NOT ALLOTED'}", 
                        foreground="green" if is_alloted else "red"
                    )
                else:
                    self.status_label.config(text="No application found with given details", foreground="red")
            else:
                self.status_label.config(text="Verification failed. Please check your details.", foreground="red")
        except Exception:
            self.status_label.config(text="An error occurred. Please try again.", foreground="red")

    def load_sample_data(self):
        mainboard_data = [
            ("TPG Growth Climate Limited", "Nov 28, 2024", "Nov 30, 2024", "₹1,560.00-1,700.00", "8", "₹6,800.00", "Upcoming"),
            ("Medi Assist Healthcare", "Nov 25, 2024", "Nov 27, 2024", "₹1,080.00-1,100.00", "12", "₹4,200.00", "Upcoming"),
            ("India Shelter Finance", "Nov 22, 2024", "Nov 24, 2024", "₹890.00-1,000.00", "14", "₹3,800.00", "Upcoming"),
            ("Tata Technologies Limited", "Nov 18, 2024", "Nov 20, 2024", "₹1,280.00-1,400.00", "10", "₹8,500.00", "Upcoming"),
            ("Konstelec Engineers Limited", "Nov 15, 2024", "Nov 17, 2024", "₹745.00-900.00", "15", "₹2,800.00", "Upcoming"),
            ("Capital Small Finance Bank", "Nov 12, 2024", "Nov 14, 2024", "₹468.00-550.00", "30", "₹4,500.00", "Upcoming"),
            ("Maxposure Limited", "Nov 08, 2024", "Nov 10, 2024", "₹620.00-800.00", "25", "₹1,500.00", "Upcoming"),
            ("Popular Vehicles and Services", "Nov 05, 2024", "Nov 07, 2024", "₹920.00-1,050.00", "16", "₹3,200.00", "Upcoming"),
            ("Krystal Integrated Services", "Nov 02, 2024", "Nov 04, 2024", "₹715.00-950.00", "20", "₹1,800.00", "Upcoming"),
            ("JG Chemicals Limited", "Oct 30, 2024", "Nov 01, 2024", "₹850.00-1000.00", "18", "₹2,500.00", "Upcoming"),
            ("Afcons Infrastructure Limited", "Oct 25, 2024", "Oct 29, 2024", "₹1,200.00-1,350.00", "12", "₹7,000.00", "Open"),
            ("Godavari Biorefineries Limited", "Oct 23, 2024", "Oct 25, 2024", "₹1,503.00-1,600.00", "10", "₹5,500.00", "Closed"),
            ("Hyundai Motor India Limited", "Oct 15, 2024", "Oct 17, 2024", "₹1,960.00-2,000.00", "15", "₹9,000.00", "Closed")
        ]
        
        sme_data = [
            ("EMS Technical Solutions", "Nov 24, 2024", "Nov 26, 2024", "₹325.00", "400", "₹185.00", "Upcoming"),
            ("Deepak Chemtex", "Nov 21, 2024", "Nov 23, 2024", "₹180.00", "600", "₹120.00", "Upcoming"),
            ("RK Infratech", "Nov 18, 2024", "Nov 20, 2024", "₹245.00", "500", "₹150.00", "Upcoming"),
            ("Spectrum Technologies", "Nov 15, 2024", "Nov 17, 2024", "₹210.00", "600", "₹95.00", "Upcoming"),
            ("Green Solutions India", "Nov 12, 2024", "Nov 14, 2024", "₹165.00", "800", "₹75.00", "Upcoming"),
            ("Innovative Pharma", "Nov 09, 2024", "Nov 11, 2024", "₹280.00", "400", "₹160.00", "Upcoming"),
            ("Smart Electronics", "Nov 06, 2024", "Nov 08, 2024", "₹195.00", "600", "₹110.00", "Upcoming"),
            ("Tech Startups Limited", "Nov 03, 2024", "Nov 05, 2024", "₹225.00", "500", "₹130.00", "Upcoming"),
            ("Eco Friendly Solutions", "Oct 31, 2024", "Nov 02, 2024", "₹175.00", "800", "₹85.00", "Open"),
            ("Digital Systems India", "Oct 28, 2024", "Oct 30, 2024", "₹155.00", "1000", "₹65.00", "Closed"),
            ("Healthcare Solutions", "Oct 25, 2024", "Oct 27, 2024", "₹290.00", "400", "₹170.00", "Closed"),
            ("Renewable Energy Corp", "Oct 22, 2024", "Oct 24, 2024", "₹205.00", "600", "₹125.00", "Closed")
        ]
        
        # Clear and load Mainboard IPO data
        for item in self.mainboard_ipo_tree.get_children():
            self.mainboard_ipo_tree.delete(item)
        for item in mainboard_data:
            self.mainboard_ipo_tree.insert('', 'end', values=item)
            
        # Clear and load SME IPO data
        for item in self.sme_ipo_tree.get_children():
            self.sme_ipo_tree.delete(item)
        for item in sme_data:
            self.sme_ipo_tree.insert('', 'end', values=item)

if __name__ == "__main__":
    app = UnifiedIPOSystem()
    app.mainloop()