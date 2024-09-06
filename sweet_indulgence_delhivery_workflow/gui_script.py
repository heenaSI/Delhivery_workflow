import tkinter as tk
from tkinter import messagebox
import subprocess
import datetime

def validate_date(date_string):
    try:
        datetime.datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def run_extract_orders():
    order_date = order_date_entry.get()
    if not validate_date(order_date):
        messagebox.showerror("Error", "Invalid order date format. Please use YYYY-MM-DD.")
        return
    
    try:
        subprocess.run(["python", "extract_odoo_orders.py", order_date], check=True)
        messagebox.showinfo("Success", "Orders extracted successfully!")
        pickup_date_label.pack()
        pickup_date_entry.pack()
        create_labels_button.pack()
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to extract orders.")

def run_create_labels():
    pickup_date = pickup_date_entry.get()
    if not validate_date(pickup_date):
        messagebox.showerror("Error", "Invalid pickup date format. Please use YYYY-MM-DD.")
        return
    
    try:
        subprocess.run(["python", "get_data_for_delhivery.py", pickup_date], check=True)
        messagebox.showinfo("Success", "Delivery labels created successfully!")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to create delivery labels.")

# Create the main window
root = tk.Tk()
root.title("Order Processing and Label Creation")
root.geometry("300x200")

# Order Date input
order_date_label = tk.Label(root, text="Enter Order Date (YYYY-MM-DD):")
order_date_label.pack()
order_date_entry = tk.Entry(root)
order_date_entry.pack()

# Extract Orders button
extract_button = tk.Button(root, text="Extract Orders", command=run_extract_orders)
extract_button.pack()

# Pickup Date input (initially hidden)
pickup_date_label = tk.Label(root, text="Enter Pickup Date (YYYY-MM-DD):")
pickup_date_entry = tk.Entry(root)

# Create Labels button (initially hidden)
create_labels_button = tk.Button(root, text="Create Delivery Labels", command=run_create_labels)

# Start the GUI event loop
root.mainloop()