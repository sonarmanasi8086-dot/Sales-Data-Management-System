import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import datetime
from threading import Thread
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import defaultdict

class SalesDataApp:
    def __init__(self, root):
        # Initialize main window
        self.root = root
        self.root.title("Sales Data Management System")
        self.root.geometry("1200x700")

        # Define departments with 5-digit IDs
        self.departments = {
            "Manufacturing": {"id": "10001", "products": ["Steel Rods", "Concrete Mix", "Assembly Parts"]},
            "Services": {"id": "20002", "products": ["Consulting", "Support Plans", "Training Sessions"]},
            "Agricultural": {"id": "30003", "products": ["Fertilizer", "Seeds", "Pesticides"]},
            "Finance": {"id": "40004", "products": ["Loans", "Insurance", "Investments"]},
            "Cutlery": {"id": "50005", "products": ["Knives Set", "Spoons Set", "Forks Set"]}
        }

        # CSV file path
        self.csv_file = "db.csv"

        # Initialize or load database
        self.load_or_create_db()

        # Create tabbed interface
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create tabs
        self.data_tab = tk.Frame(self.notebook)
        self.chart_tab = tk.Frame(self.notebook)

        self.notebook.add(self.data_tab, text="Data Entry & Management")
        self.notebook.add(self.chart_tab, text="Profit Analysis Chart")

        # Build data entry tab
        self.build_data_entry_tab()

        # Build chart tab
        self.build_chart_tab()

        # Start auto-save thread
        self.auto_save_running = True
        self.auto_save_thread = Thread(target=self.auto_save_loop, daemon=True)
        self.auto_save_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_or_create_db(self):
        """Check if db.csv exists, if not create blank one, then load into memory"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                headers = ["Entry_ID", "Timestamp", "Dept_ID", "Dept_Name", 
                          "Product1", "P1_Profit", "P1_Loss", 
                          "Product2", "P2_Profit", "P2_Loss",
                          "Product3", "P3_Profit", "P3_Loss",
                          "Total_Profit", "Total_Loss", "Net_Profit"]
                writer.writerow(headers)

        self.db = []
        with open(self.csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.db.append(row)

    def get_next_entry_id(self):
        """Get next entry ID by checking last entry and adding 1"""
        if len(self.db) == 0:
            return 1
        else:
            last_id = int(self.db[-1]["Entry_ID"])
            return last_id + 1

    def build_data_entry_tab(self):
        """Build the data entry and management interface"""
        entry_frame = tk.LabelFrame(self.data_tab, text="Add New Entry", padx=10, pady=10)
        entry_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(entry_frame, text="Entry ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_id_var = tk.StringVar()
        tk.Entry(entry_frame, textvariable=self.entry_id_var, state='readonly', width=15).grid(row=0, column=1, pady=5)

        tk.Label(entry_frame, text="Timestamp:").grid(row=0, column=2, sticky='w', pady=5, padx=(20,0))
        self.timestamp_var = tk.StringVar()
        tk.Entry(entry_frame, textvariable=self.timestamp_var, state='readonly', width=20).grid(row=0, column=3, pady=5)

        tk.Label(entry_frame, text="Department:").grid(row=1, column=0, sticky='w', pady=5)
        self.dept_var = tk.StringVar()
        dept_dropdown = ttk.Combobox(entry_frame, textvariable=self.dept_var, 
                                     values=list(self.departments.keys()), 
                                     state='readonly', width=15)
        dept_dropdown.grid(row=1, column=1, pady=5)
        dept_dropdown.bind("<<ComboboxSelected>>", self.on_dept_change)

        tk.Label(entry_frame, text="Product 1:").grid(row=2, column=0, sticky='w', pady=5)
        self.product1_var = tk.StringVar()
        self.product1_dropdown = ttk.Combobox(entry_frame, textvariable=self.product1_var, 
                                              state='readonly', width=15)
        self.product1_dropdown.grid(row=2, column=1, pady=5)

        tk.Label(entry_frame, text="P1 Profit:").grid(row=2, column=2, sticky='w', pady=5, padx=(20,0))
        self.p1_profit_var = tk.StringVar(value="0")
        tk.Entry(entry_frame, textvariable=self.p1_profit_var, width=15).grid(row=2, column=3, pady=5)

        tk.Label(entry_frame, text="P1 Loss:").grid(row=2, column=4, sticky='w', pady=5, padx=(20,0))
        self.p1_loss_var = tk.StringVar(value="0")
        tk.Entry(entry_frame, textvariable=self.p1_loss_var, width=15).grid(row=2, column=5, pady=5)

        tk.Label(entry_frame, text="Product 2:").grid(row=3, column=0, sticky='w', pady=5)
        self.product2_var = tk.StringVar()
        self.product2_dropdown = ttk.Combobox(entry_frame, textvariable=self.product2_var, 
                                              state='readonly', width=15)
        self.product2_dropdown.grid(row=3, column=1, pady=5)

        tk.Label(entry_frame, text="P2 Profit:").grid(row=3, column=2, sticky='w', pady=5, padx=(20,0))
        self.p2_profit_var = tk.StringVar(value="0")
        tk.Entry(entry_frame, textvariable=self.p2_profit_var, width=15).grid(row=3, column=3, pady=5)

        tk.Label(entry_frame, text="P2 Loss:").grid(row=3, column=4, sticky='w', pady=5, padx=(20,0))
        self.p2_loss_var = tk.StringVar(value="0")
        tk.Entry(entry_frame, textvariable=self.p2_loss_var, width=15).grid(row=3, column=5, pady=5)

        tk.Label(entry_frame, text="Product 3:").grid(row=4, column=0, sticky='w', pady=5)
        self.product3_var = tk.StringVar()
        self.product3_dropdown = ttk.Combobox(entry_frame, textvariable=self.product3_var, 
                                              state='readonly', width=15)
        self.product3_dropdown.grid(row=4, column=1, pady=5)

        tk.Label(entry_frame, text="P3 Profit:").grid(row=4, column=2, sticky='w', pady=5, padx=(20,0))
        self.p3_profit_var = tk.StringVar(value="0")
        tk.Entry(entry_frame, textvariable=self.p3_profit_var, width=15).grid(row=4, column=3, pady=5)

        tk.Label(entry_frame, text="P3 Loss:").grid(row=4, column=4, sticky='w', pady=5, padx=(20,0))
        self.p3_loss_var = tk.StringVar(value="0")
        tk.Entry(entry_frame, textvariable=self.p3_loss_var, width=15).grid(row=4, column=5, pady=5)

        btn_frame = tk.Frame(entry_frame)
        btn_frame.grid(row=5, column=0, columnspan=6, pady=10)

        tk.Button(btn_frame, text="Add Entry", command=self.add_entry, 
                 bg='green', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_entry, 
                 bg='orange', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_entry, 
                 bg='red', fg='white', width=12).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Clear Fields", command=self.clear_fields, 
                 width=12).pack(side='left', padx=5)

        display_frame = tk.LabelFrame(self.data_tab, text="Database Records", padx=10, pady=10)
        display_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ("ID", "Timestamp", "Dept", "P1", "P1_Profit", "P1_Loss", 
                  "P2", "P2_Profit", "P2_Loss", "P3", "P3_Profit", "P3_Loss", 
                  "Total_Profit", "Total_Loss", "Net")

        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=15)

        col_widths = [50, 130, 100, 100, 80, 80, 100, 80, 80, 100, 80, 80, 90, 90, 90]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths[i], minwidth=50)

        vsb = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(display_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        self.refresh_tree()
        self.reset_entry_fields()

    def build_chart_tab(self):
        """Build the chart visualization tab with matplotlib"""
        control_frame = tk.Frame(self.chart_tab)
        control_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(control_frame, text="Profit Analysis Chart", 
                font=('Arial', 14, 'bold')).pack(side='left', padx=10)

        tk.Button(control_frame, text="Refresh Chart", 
                 command=self.update_chart, bg='blue', fg='white').pack(side='right', padx=10)

        self.chart_frame = tk.Frame(self.chart_tab)
        self.chart_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_chart_widget()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_chart_widget(self):
        """Create matplotlib chart widget"""
        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.update_chart()

    def on_tab_change(self, event):
        """Update chart when switching to chart tab"""
        if self.notebook.index(self.notebook.select()) == 1:
            self.update_chart()

    def update_chart(self):
        """Update chart with current data"""
        self.ax.clear()

        if len(self.db) == 0:
            self.ax.text(0.5, 0.5, 'No data available\nAdd some entries in the Data Entry tab', 
                        ha='center', va='center', fontsize=16)
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.canvas.draw()
            return

        product_data = defaultdict(lambda: {'timestamps': [], 'profits': []})

        for entry in self.db:
            try:
                timestamp = datetime.datetime.strptime(entry['Timestamp'], "%Y-%m-%d %H:%M:%S")

                p1_name = f"{entry['Dept_Name']}-{entry['Product1']}"
                p1_profit = float(entry['P1_Profit']) - float(entry['P1_Loss'])
                product_data[p1_name]['timestamps'].append(timestamp)
                product_data[p1_name]['profits'].append(p1_profit)

                p2_name = f"{entry['Dept_Name']}-{entry['Product2']}"
                p2_profit = float(entry['P2_Profit']) - float(entry['P2_Loss'])
                product_data[p2_name]['timestamps'].append(timestamp)
                product_data[p2_name]['profits'].append(p2_profit)

                p3_name = f"{entry['Dept_Name']}-{entry['Product3']}"
                p3_profit = float(entry['P3_Profit']) - float(entry['P3_Loss'])
                product_data[p3_name]['timestamps'].append(timestamp)
                product_data[p3_name]['profits'].append(p3_profit)

            except Exception as e:
                print(f"Error processing entry: {e}")
                continue

        colors = plt.cm.tab20.colors
        color_idx = 0

        for product_name, data in sorted(product_data.items()):
            sorted_pairs = sorted(zip(data['timestamps'], data['profits']))
            timestamps, profits = zip(*sorted_pairs) if sorted_pairs else ([], [])

            if timestamps:
                self.ax.plot(timestamps, profits, marker='o', 
                            label=product_name, color=colors[color_idx % len(colors)],
                            linewidth=2, markersize=4)
                color_idx += 1

        self.ax.set_xlabel('Timestamp', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Net Profit', fontsize=12, fontweight='bold')
        self.ax.set_title('Product Profit Over Time', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

        self.fig.autofmt_xdate(rotation=45)
        self.fig.tight_layout()

        self.canvas.draw()

    def on_dept_change(self, event=None):
        """Update product dropdowns when department changes"""
        dept_name = self.dept_var.get()
        if dept_name in self.departments:
            products = self.departments[dept_name]["products"]
            self.product1_dropdown['values'] = products
            self.product2_dropdown['values'] = products
            self.product3_dropdown['values'] = products

            if len(products) >= 3:
                self.product1_var.set(products[0])
                self.product2_var.set(products[1])
                self.product3_var.set(products[2])

    def reset_entry_fields(self):
        """Reset entry fields with auto-generated values"""
        self.entry_id_var.set(str(self.get_next_entry_id()))
        self.timestamp_var.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def clear_fields(self):
        """Clear all input fields"""
        self.reset_entry_fields()
        self.dept_var.set('')
        self.product1_var.set('')
        self.product2_var.set('')
        self.product3_var.set('')
        self.p1_profit_var.set('0')
        self.p1_loss_var.set('0')
        self.p2_profit_var.set('0')
        self.p2_loss_var.set('0')
        self.p3_profit_var.set('0')
        self.p3_loss_var.set('0')

    def add_entry(self):
        """Add new entry to memory database"""
        try:
            if not self.dept_var.get():
                messagebox.showerror("Error", "Please select a department")
                return

            dept_name = self.dept_var.get()
            dept_id = self.departments[dept_name]["id"]

            p1_profit = float(self.p1_profit_var.get())
            p1_loss = float(self.p1_loss_var.get())
            p2_profit = float(self.p2_profit_var.get())
            p2_loss = float(self.p2_loss_var.get())
            p3_profit = float(self.p3_profit_var.get())
            p3_loss = float(self.p3_loss_var.get())

            total_profit = p1_profit + p2_profit + p3_profit
            total_loss = p1_loss + p2_loss + p3_loss
            net_profit = total_profit - total_loss

            new_entry = {
                "Entry_ID": self.entry_id_var.get(),
                "Timestamp": self.timestamp_var.get(),
                "Dept_ID": dept_id,
                "Dept_Name": dept_name,
                "Product1": self.product1_var.get(),
                "P1_Profit": str(p1_profit),
                "P1_Loss": str(p1_loss),
                "Product2": self.product2_var.get(),
                "P2_Profit": str(p2_profit),
                "P2_Loss": str(p2_loss),
                "Product3": self.product3_var.get(),
                "P3_Profit": str(p3_profit),
                "P3_Loss": str(p3_loss),
                "Total_Profit": str(total_profit),
                "Total_Loss": str(total_loss),
                "Net_Profit": str(net_profit)
            }

            self.db.append(new_entry)
            self.refresh_tree()
            self.clear_fields()

            messagebox.showinfo("Success", "Entry added successfully!")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid numeric value: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding entry: {e}")

    def edit_entry(self):
        """Edit selected entry"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to edit")
            return

        try:
            item = self.tree.item(selection[0])
            values = item['values']
            entry_id = str(values[0])

            for i, entry in enumerate(self.db):
                if entry["Entry_ID"] == entry_id:
                    dept_name = self.dept_var.get()
                    if not dept_name:
                        messagebox.showerror("Error", "Please select a department")
                        return

                    dept_id = self.departments[dept_name]["id"]

                    p1_profit = float(self.p1_profit_var.get())
                    p1_loss = float(self.p1_loss_var.get())
                    p2_profit = float(self.p2_profit_var.get())
                    p2_loss = float(self.p2_loss_var.get())
                    p3_profit = float(self.p3_profit_var.get())
                    p3_loss = float(self.p3_loss_var.get())

                    total_profit = p1_profit + p2_profit + p3_profit
                    total_loss = p1_loss + p2_loss + p3_loss
                    net_profit = total_profit - total_loss

                    self.db[i] = {
                        "Entry_ID": entry_id,
                        "Timestamp": self.timestamp_var.get(),
                        "Dept_ID": dept_id,
                        "Dept_Name": dept_name,
                        "Product1": self.product1_var.get(),
                        "P1_Profit": str(p1_profit),
                        "P1_Loss": str(p1_loss),
                        "Product2": self.product2_var.get(),
                        "P2_Profit": str(p2_profit),
                        "P2_Loss": str(p2_loss),
                        "Product3": self.product3_var.get(),
                        "P3_Profit": str(p3_profit),
                        "P3_Loss": str(p3_loss),
                        "Total_Profit": str(total_profit),
                        "Total_Loss": str(total_loss),
                        "Net_Profit": str(net_profit)
                    }

                    self.refresh_tree()
                    messagebox.showinfo("Success", "Entry updated successfully!")
                    break

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid numeric value: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error editing entry: {e}")

    def delete_entry(self):
        """Delete selected entry"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to delete")
                return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            try:
                item = self.tree.item(selection[0])
                values = item['values']
                entry_id = str(values[0])

                for i, entry in enumerate(self.db):
                    if entry["Entry_ID"] == entry_id:
                        del self.db[i]
                        break

                self.refresh_tree()
                self.clear_fields()
                messagebox.showinfo("Success", "Entry deleted successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Error deleting entry: {e}")

    def on_tree_select(self, event):
        """Load selected entry into fields"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']

            self.entry_id_var.set(str(values[0]))
            self.timestamp_var.set(str(values[1]))
            self.dept_var.set(str(values[2]))
            self.on_dept_change()

            self.product1_var.set(str(values[3]))
            self.p1_profit_var.set(str(values[4]))
            self.p1_loss_var.set(str(values[5]))

            self.product2_var.set(str(values[6]))
            self.p2_profit_var.set(str(values[7]))
            self.p2_loss_var.set(str(values[8]))

            self.product3_var.set(str(values[9]))
            self.p3_profit_var.set(str(values[10]))
            self.p3_loss_var.set(str(values[11]))

    def refresh_tree(self):
        """Refresh treeview with current database"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for entry in self.db:
            self.tree.insert('', 'end', values=(
                entry["Entry_ID"],
                entry["Timestamp"],
                entry["Dept_Name"],
                entry["Product1"],
                entry["P1_Profit"],
                entry["P1_Loss"],
                entry["Product2"],
                entry["P2_Profit"],
                entry["P2_Loss"],
                entry["Product3"],
                entry["P3_Profit"],
                entry["P3_Loss"],
                entry["Total_Profit"],
                entry["Total_Loss"],
                entry["Net_Profit"]
            ))

    def save_to_csv(self):
        """Save memory database to CSV file"""
        try:
            with open(self.csv_file, 'w', newline='') as f:
                if len(self.db) > 0:
                    writer = csv.DictWriter(f, fieldnames=self.db[0].keys())
                    writer.writeheader()
                    writer.writerows(self.db)
                else:
                    writer = csv.writer(f)
                    headers = ["Entry_ID", "Timestamp", "Dept_ID", "Dept_Name", 
                              "Product1", "P1_Profit", "P1_Loss", 
                              "Product2", "P2_Profit", "P2_Loss",
                              "Product3", "P3_Profit", "P3_Loss",
                              "Total_Profit", "Total_Loss", "Net_Profit"]
                    writer.writerow(headers)
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def auto_save_loop(self):
        """Auto-save database every second"""
        while self.auto_save_running:
            time.sleep(1)
            self.save_to_csv()

    def on_closing(self):
        """Handle window close event"""
        self.auto_save_running = False
        self.save_to_csv()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = SalesDataApp(root)
    root.mainloop()
