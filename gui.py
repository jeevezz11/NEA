import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import main as tm
import fnmatch
import os
import datetime
import hashlib
from tkcalendar import Calendar
import datetime

class Menu:
    def __init__(self, root): #initialise the gui

        try:
            self.root = root
            self.root.title("Menu")  

            self.confirmation_status = False # confirmation status is used so that we know the order in progress is not confirmed

            self.customer_frame = tk.Frame(self.root, padx=10, pady=10) # initialises the frame for me to place my widgets on
            self.customer_frame.grid(row=0, column=0, columnspan=3, sticky="ew") 

            tk.Label(self.customer_frame, text="  Customer Name").pack(side=tk.LEFT) # label to enter the customer name for reeipts

            self.customer_name_entry = tk.Entry(self.customer_frame) # the entry box for the name to be entered in
            self.customer_name_entry.pack(side=tk.LEFT, padx=(5, 0))

            self.active_orders_frame = tk.Frame(root) # initialise the frame for the active orders menu
            self.active_orders_frame.grid(row=7, column=1, padx=10, sticky="ew")

            self.admin_button = tk.Button(self.active_orders_frame, text="Admin Options", command=self.admin_menu) # add the admin menu button
            self.admin_button.pack(side=tk.BOTTOM)
            
            self.view_orders_button = tk.Button(self.active_orders_frame, text="\nView Active Orders\n", command=self.view_active_orders) # adds the view active orders button 
            self.view_orders_button.pack(side=tk.BOTTOM)

            self.button_frame = tk.Frame(self.root, padx=10, pady=5) # frame to place the buttons on 
            self.button_frame.grid(row=1, column=0, rowspan=6)
        except:
            self.show_warning("Failed to initialise the menu", 8)


        button_info = [ # format: "item", command
            ("Small Fish", self.button_one_clicked),
            ("Regular Fish", self.button_two_clicked),
            ("Large Fish", self.button_three_clicked),
            ("Regular Chips", self.button_four_clicked),
            ("Large Chips", self.button_five_clicked),
            ("7\" Pizza", self.button_six_clicked),
            ("10\" Pizza", self.button_seven_clicked),
            ("12\" Pizza", self.button_eight_clicked),
            ("Kebab Wrap", self.button_nine_clicked),
            ("Mega Kebab Wrap", self.button_ten_clicked),
            ("Mega Mixed Kebab Wrap", self.button_eleven_clicked),
            ("Chicken Tikka Wrap", self.button_twelve_clicked),
            ("Small Sauce", self.button_thirteen_clicked),
            ("Large Sauce", self.button_fourteen_clicked),
            ("Can Of Pop", self.button_fifteen_clicked),
            ("Bottle Of Pop", self.button_sixteen_clicked),
            ("Total", self.button_total_clicked)
        ]

        self.buttons = [] # list for buttons so when i want to deactivate them i can just iterate through the list and just deactivate them all

        for text, command_func in button_info:
            button = tk.Button(self.button_frame, text=text, width=10, height=3, command=command_func, wraplength= 80) # here the buttons are all formatted to fit nicely on the screen
            self.buttons.append(button) 

        row_count = 0
        column_count = 0

        loop = 0
        
        try:
            for button in self.buttons:
                if loop == 16: # places the 17th button which is my total button under the rest of the buttons and spans it across so its the same width as 4 buttons
                    button.grid(row=row_count, column=column_count, columnspan=6, padx=5, pady=(15,0), sticky="ew")
                else:
                    button.grid(row=row_count, column=column_count, padx=5, pady=5)
                    column_count += 1
                    if column_count == 4:
                        column_count = 0
                        row_count += 1
                    loop += 1

            self.output_text = tk.Text(root, width=40, height=20) # output text to put the current items in the transaction into a receipt like format
            self.output_text.grid(row=0, column=1, rowspan=6, padx=10, pady=(10, 0), sticky="nsew")

            scrollbar = tk.Scrollbar(root, command=self.output_text.yview) # a scroll bar incase text goes off the screen so i can still view everything
            scrollbar.grid(row=0, column=2, rowspan=6, sticky="ns") 

            self.output_text.config(yscrollcommand=scrollbar.set) # sets the scroll bar

            self.new_order_frame = tk.Frame(root) 
            self.new_order_frame.grid(row=6, column=1, padx=10, sticky="ew")

            self.new_order_button = tk.Button(self.new_order_frame, text="New Order", command=self.new_order, state=tk.DISABLED, width=18, height=3)
            self.new_order_button.pack(side=tk.LEFT) # sets the button to start a new order

            self.remove_button = tk.Button(self.new_order_frame, text="Remove Last Item", command=self.remove_selected_line, width=18, height=3)
            self.remove_button.pack(side=tk.LEFT) # sets the button to remove the last item entered into the order 

            for button in self.buttons:
                button.config(state=tk.DISABLED) # disables all the buttons to start the process

            self.remove_button.config(state=tk.DISABLED)
            self.new_order_button.config(state=tk.NORMAL) # allows you to start a new order
        
        except:
            self.show_warning("Failed to place buttons on grid", 9)

    def show_warning(self, warning, errorCode): # used to display various warnings in the same format
        warning_window = tk.Toplevel(root)
        warning_window.title("Warning")

        label = tk.Label(warning_window, text=(warning), font=("Helvetica-Bold", 12))
        label.pack(padx=20, pady=20,)
        
        if errorCode == 0:
            pass
        else:
            errorLabel = tk.Label(warning_window, text=f"Error Code {errorCode}", font=("Helvetica-Bold", 10))
            errorLabel.pack()
        
        okay_button = tk.Button(warning_window, text="          Close          ", command=warning_window.destroy)
        okay_button.pack(pady=10)

        warning_window.bind("<Return>", lambda event=None: warning_window.destroy())


    # all button commands 
    def button_one_clicked(self):
        self.output_text.insert(tk.END, "Small Fish - £4.40\n")
        tm.addFood("sml fish") # add food function called from main script potentially going to change but atm finds the food from a text file and sorts it out in the main script

    def button_two_clicked(self):
        self.output_text.insert(tk.END, "Regular Fish - £6.90\n")
        tm.addFood("reg fish")

    def button_three_clicked(self):
        self.output_text.insert(tk.END, "Large Fish - £8.50\n")
        tm.addFood("lrg fish")

    def button_four_clicked(self):
        self.output_text.insert(tk.END, "Regular Chips - £2.40\n")
        tm.addFood("reg chips")

    def button_five_clicked(self):
        self.output_text.insert(tk.END, "Large Chips - £2.90\n")
        tm.addFood("lrg chips")

    def button_six_clicked(self):
        self.pizza_customisation_menu("7\" Pizza") # better method for adding food using a customisation menu probably going to adopt this for all buttons

    def button_seven_clicked(self):
        self.pizza_customisation_menu("10\" Pizza")

    def button_eight_clicked(self):
        self.pizza_customisation_menu("12\" Pizza")

    def button_nine_clicked(self):
        self.output_text.insert(tk.END, "Kebab Wrap - £5.50\n")
        tm.addFood("kebab wrap")

    def button_ten_clicked(self):
        self.output_text.insert(tk.END, "Mega Kebab Wrap - £9.99\n")
        tm.addFood("mega kebab wrap")

    def button_eleven_clicked(self):
        self.output_text.insert(tk.END, "Mega Mixed Kebab Wrap - £12.99\n")
        tm.addFood("mega mixed kebab wrap")

    def button_twelve_clicked(self):
        self.output_text.insert(tk.END, "Chicken Tikka Wrap - £6.50\n")
        tm.addFood("chicken wrap")

    def button_thirteen_clicked(self):
        self.sauce_customisation_menu("small")

    def button_fourteen_clicked(self):
        self.sauce_customisation_menu("large")

    def button_fifteen_clicked(self):
        self.output_text.insert(tk.END, "Can Of Pop - £1.00\n")
        tm.addFood("can of pop")

    def button_sixteen_clicked(self):
        self.output_text.insert(tk.END, "Bottle Of Pop - £1.50\n")
        tm.addFood("bottle of pop")
    
    def button_total_clicked(self):
        
        customer_name = self.customer_name_entry.get()
        customer_name = customer_name.capitalize()
        receipt = tm.doReceipt(customer_name) # this function sorts out the receipt for my records and gets the total price for the transaction

        self.output_text.insert(tk.END, receipt)
        self.output_text.see(tk.END)
        self.confirmation_status = True # the order is now confirmed

        for button in self.buttons:
            button.config(state=tk.DISABLED) # disable the buttons again

        self.admin_button.config(state=tk.NORMAL) 
        self.remove_button.config(state=tk.DISABLED)
        self.new_order_button.config(state=tk.NORMAL)
            
        tm.updateActiveOrders() # update the list of orders that are currently active so they can be managed

    def remove_selected_line(self):
        
        tm.removeLastItem() # removes the last items behind the scenes
        
        current_line = self.output_text.index(tk.INSERT) # puts you onto a new line
        current_line_number = int(current_line.split('.')[0])
 
        previous_line_index = f"{current_line_number - 1}.0" # goes back a line

        self.output_text.delete(previous_line_index, current_line) # deletes the whole line

    def new_order(self):

        try: 
            curOrders = tm.activeOrderCount()
            folderFound = tm.folderStatus() # makes sure we have a folder path 

            if folderFound == False:
                self.show_warning("Please set your program directory in the 'config.ini' file.", "1") # if there is a problem with your config file it informs the user as such 

            if curOrders > 4:
                self.show_warning(f"You already have {curOrders} orders open\nTry not to open too many orders at once.", "3") # warns you if you have too many orders open
            
            tm.newOrder() # starts the new order 
            
            self.admin_button.config(state=tk.DISABLED)
            self.output_text.delete("1.0", tk.END)
            self.confirmation_status = False # resets the confirmation status

            for button in self.buttons:
                button.config(state=tk.NORMAL) # sets all the buttons to the correct state

            self.remove_button.config(state=tk.NORMAL)
            self.new_order_button.config(state=tk.DISABLED)

            self.customer_name_entry.delete(0, tk.END)
            self.customer_name_entry.focus_set()

            number = tm.giveOrderNumber() # gets the order number to put at the top of the receipt
            self.output_text.insert(tk.END, f"Order {number}\n\n")
        except:
            self.show_warning("An unknown problem has occured\nPlease make sure the correct directory is set.", "2") # a whole number of errors could occur at this point eventually 
                                                                                                                # ill break it down so when an error is thrown it may be more useful

    def pizza_customisation_menu(self, pizza_size):
        customisation_window = tk.Toplevel(self.root) # opens pizza menu
        customisation_window.title(f"{pizza_size} Customisation")
        pizza_size = pizza_size.split('"')[0] # get the size of the pizza in inches
        pizza_size = pizza_size.strip() #.strip() gets of trailing spaces

        def custom_option_clicked(option_text, pizza_size):

            if pizza_size == "7":
                pizza_size_word = "seven"
            elif pizza_size == "10":
                pizza_size_word = "ten"
            elif pizza_size == "12":
                pizza_size_word = "twelve"

            text = tm.getPizzaPrice(pizza_size, option_text, pizza_size_word) # gets the price from my pizza database

            self.output_text.insert(tk.END, text)
            customisation_window.destroy() # closes the window

        custom_options = [
            "Margerita", "Bolognese", "Hawaiian", "Vegetarian",
            "Chicken Kiev", "Hot Shot", "Chicken Tikka", "Tuna",
            "Pepperoni", "Smokey Special", "Chicken", "Chicken And Mushroom",
            "Geordie Kebab Delight", "Plain Kebab", "BBQ Chicken", "Meat Feast",
        ]

        row_count = 0
        column_count = 0

        for option_text in custom_options:
            custom_button = tk.Button(customisation_window, text=option_text, width=10, height=3,
                                      command=lambda opt=option_text: custom_option_clicked(opt, pizza_size), wraplength=80)
            custom_button.grid(row=row_count, column=column_count, padx=7, pady=5)
            column_count += 1
            if column_count == 4:
                column_count = 0
                row_count += 1
    
    def view_active_orders(self):
        try:
            active_orders = tm.getActiveOrders()
            active_orders.sort()

            if not active_orders:
                self.show_warning("No Active Orders.","4")
            
            else:    

                active_orders_window = tk.Toplevel(self.root)
                active_orders_window.title("Active Orders")

                canvas = tk.Canvas(active_orders_window)
                canvas.pack(side="left", fill="both", expand=True)

                scrollbar = tk.Scrollbar(active_orders_window, orient="vertical", command=canvas.yview)
                scrollbar.pack(side="right", fill="y")

                canvas.configure(yscrollcommand=scrollbar.set)

                frame = tk.Frame(canvas)

                canvas.create_window((0, 0), window=frame, anchor="nw")
                
                for index, order in enumerate(active_orders, start=1):
                    orderDisplay = order[2:-4].capitalize()
                    
                    tk.Label(frame, text=f"{orderDisplay}\t\t\t", font=("bold", 16)).grid(column=0, row=(index - 1) * 3, columnspan=2, sticky="w")

                    clear_order_lambda = lambda order=order: self.clear_order(order, active_orders_window)
                    view_order_lambda = lambda order=order: self.view_order(order)

                    tk.Button(frame, text="Clear Order", command=clear_order_lambda).grid(column=0, row=(index - 1) * 3 + 1, columnspan=2, sticky="ew")
                    tk.Button(frame, text="View Order", command=view_order_lambda).grid(column=0, row=(index - 1) * 3 + 2, columnspan=2, sticky="ew")
                    
                frame.update_idletasks()
                canvas_width = canvas.winfo_width()
                frame_width = frame.winfo_width()
                if canvas_width > frame_width:
                    canvas.create_window((canvas_width - frame_width) // 2, 0, window=frame, anchor="nw")

                canvas.configure(scrollregion=canvas.bbox("all"))
        except:
            self.show_warning("There is a problem with your 'config.ini' file\nPlease make sure the correct directory is set.", "5")

    def view_order(self, order):

        new_window = tk.Toplevel(root)
        new_window.title(f"{order[2:].capitalize()}")

        orderLines = tm.getOrderToView(order)
        
        for line in orderLines:    
                
            label = tk.Label(new_window, text=" " + line + " ", font=("Helvetica","14"))
            label.pack()

    def clear_order(self, order, active_orders_window):

        tm.clearSelectedOrder(order)
        tm.updateActiveOrders()
        active_orders_window.destroy()
        self.view_active_orders()

    def sauce_customisation_menu(self, sauce_size):

        customisation_window = tk.Toplevel(self.root)
        customisation_window.title(f"Sauce Customisation")

        def custom_option_clicked(option_text):

            text = tm.customSauce(sauce_size, option_text)

            self.output_text.insert(tk.END, text)
            customisation_window.destroy() 

        custom_options = ["Garlic Sauce", "Chilli Sauce", "Curry Sauce", 
                        "Mushy Peas", "Gravy", "Ketchup"]

        row_count = 0
        column_count = 0

        for option_text in custom_options:
            custom_button = tk.Button(customisation_window, text=option_text, width=10, height=3,
                                      command=lambda opt=option_text: custom_option_clicked(opt), wraplength=80)
            custom_button.grid(row=row_count, column=column_count, padx=7, pady=5)
            column_count += 1
            if column_count == 3:
                column_count = 0
                row_count += 1
    
    def admin_menu(self):

        password_window = tk.Toplevel(self.root)
        password_window.title("Password Prompt")

        label = tk.Label(password_window, text="Enter Admin Password:")
        label.pack(pady=10)

        password_entry = tk.Entry(password_window, show="*")
        password_entry.pack(padx=10)
        password_entry.focus_set()

        def hash_password(password):

            hash_obj = hashlib.sha256(password.encode())
            return hash_obj.hexdigest() 

        correct_password_hash = tm.getAdminPassword()

        def check_password():

            entered_password_hash = password_entry.get()
            entered_password_hash = hash_password(entered_password_hash)

            if entered_password_hash in correct_password_hash:
                password_window.destroy() 
                self.open_admin_options()  
            else:
                self.show_warning("Incorrect Password Entered\nPlease Try Again", "6")
                password_entry.delete(0, tk.END)

        check_button = tk.Button(password_window, text="      Log In      ", command=check_password)
        check_button.pack(pady=10)

        password_entry.bind("<Return>", lambda event=None: check_password())

    def open_admin_options(self):
        admin_options = tk.Toplevel(self.root)
        admin_options.title("Admin Options")

        canvas = tk.Canvas(admin_options)
        canvas.pack(side="left", fill="both", expand=True)

        admin_options_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=admin_options_frame, anchor="nw")

        self.total_takings_button = tk.Button(admin_options_frame, text="\nToday's Total Takings\n", command=self.total_takings)
        self.total_takings_button.grid(column=0, row=0, padx=10, pady=5, sticky="nesw")

        self.daily_report_button = tk.Button(admin_options_frame, text="\n          Daily Report          \n", command=self.daily_report)
        self.daily_report_button.grid(column=1, row=0, padx=0, pady=5, sticky="nesw")
        
        self.void_order_button = tk.Button(admin_options_frame, text="\nVoid Order\n", command=self.void_order)
        self.void_order_button.grid(column=0, row=1, padx=10, pady=0, sticky="nesw")
    
    def total_takings(self):

        total_price = tm.getTodaysTakings()
       
        total_takings_window = tk.Toplevel(root)
        total_takings_window.title("Total Takings")

        label = tk.Label(total_takings_window, text=f"Today's total takings are {total_price}", font=(12), wraplength=110)
        label.pack(padx=20, pady=20,)

        okay_button = tk.Button(total_takings_window, text="          Close          ", command=total_takings_window.destroy)
        okay_button.pack(pady=10)

    def daily_report(self):

        def get_selected_date():
            
            selected_date = cal.get_date()
            selected_date = selected_date.split("/")

            calendar.destroy()
            
            month = int(selected_date[0])
            day = int(selected_date[1])
            year = int(selected_date[2])

            century = 2000

            date = datetime.datetime(century + year, month, day)
            date = date.strftime("%Y-%m-%d")

            try:
                report, total_price = tm.createReport(date)
                report_window = tk.Toplevel(self.root)
                report_window.title(f"Report for {date}")           
            except:
                self.show_warning("The date you've selected does not have any orders to report", "7")

            label = tk.Label(report_window, text="", font=("Helvetica", "16"))
            label.grid(row=0, column=0)
            
            currentTime = datetime.datetime.now().time()
            formattedTime = currentTime.strftime("%H:%M:%S")
            
            label_text = f"Report for {date} as of {formattedTime} today\n\n"
            
            for key, (quantity, price) in report.items():
                label_text += f"  {key.title()}: Quantity = {quantity}, Price = £{price}  \n"

            label_text += f"\nTotal Takings: £{total_price}"

            label.config(text=label_text)

        calendar = tk.Toplevel(self.root)
        calendar.title("Date Selector")

        year, month, day = tm.getCurrentDate()        

        cal = Calendar(calendar, selectmode="day", year=int(year), month=int(month), day=int(day))
        cal.pack()

        get_date_button = tk.Button(calendar, text="Get Selected Date", command=get_selected_date)
        get_date_button.pack()

    def void_order(self):
        
        void_order_menu = tk.Toplevel()
        void_order_menu.title("Void Order")

        label = tk.Label(void_order_menu, text="Enter Order Number:")
        label.pack(padx=10, pady=10)

        order_entry = tk.Entry(void_order_menu)
        order_entry.pack(padx=10)
        order_entry.focus_set()

        order_number = order_entry.get()
        
        void_button = tk.Button(void_order_menu, text="Void", command=lambda: self.void_selected_order(order_entry))
        void_button.pack(padx=10, pady=10)
        order_entry.bind("<Return>", lambda event=None: self.void_selected_order(order_entry))

    def void_selected_order(self, order_entry):
        
        order_number = str(order_entry.get())
        order_entry.delete(0, "end")

        try:
            tm.voidOrder(order_number)
            self.show_warning(f"Order {order_number} Voided", 0)
        except:
            self.show_warning("Order not found", 10)
        
if __name__ == "__main__":

    root = tk.Tk()
    app = Menu(root)
    root.mainloop()

