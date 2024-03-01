# Version 0.9 for Linux #

import tkinter as tk # import the tkinter library for the GUI
import backend as bf # import the backend script to do the processing
import hashlib # hashing library to validate the password
from tkcalendar import Calendar # import the calendar widget to pick dates 
import datetime 
import os 
import sys # used to relaunch the python script if admin mode is enabled 

class Menu: # initialise the Menu class
	def __init__(self, root):

		try: 
			
			self.active_orders = bf.update_active_orders() # get the active orders 

			self.root = root 
			self.root.title("Menu") # name the root window

			self.elevated_privellege = bf.return_elevated_privellege() # determine wether the program is being ran in admin mode or not

			root.grid_rowconfigure(0, weight=1) # weight is used to tell the grid how much space it should take up relative to the window 
			root.grid_rowconfigure(1, weight=1)
			root.grid_columnconfigure(0, weight=1)
			root.grid_columnconfigure(1, weight=1)

			self.confirmation_status = False # confirmation status is used so that we know the order in progress is not confirmed

			self.customer_frame = tk.Frame(self.root, padx=10, pady=10) # initialises the frame for me to place my widgets on
			self.customer_frame.grid(row=0, column=0, columnspan=3, sticky="ew") 

			tk.Label(self.customer_frame, text="Customer Name").pack(side=tk.LEFT) # label to enter the customer name for reeipts

			self.customer_name_entry = tk.Entry(self.customer_frame, state=tk.DISABLED) # the entry box for the name to be entered in
			self.customer_name_entry.pack(side=tk.LEFT, padx=(5, 0)) 

			self.active_orders_frame = tk.Frame(root) # initialise the frame for the active orders menu
			self.active_orders_frame.grid(row=7, column=1, padx=10, sticky="ew")

			self.admin_button = tk.Button(self.active_orders_frame, text="Admin Options", command=self.admin_menu) # add the admin menu button
			self.admin_button.pack(side=tk.BOTTOM)
			
			self.view_orders_button = tk.Button(self.active_orders_frame, text="\nView Active Orders\n",
			command=lambda: self.view_order_menu("active")) # add an option to view active orders
			# lambda is used to allow a function to be ran with a parameter when a button is pressed

			self.view_orders_button.pack(side=tk.BOTTOM)

			self.button_frame = tk.Frame(self.root, padx=10, pady=5) # frame to place the buttons on 
			self.button_frame.grid(row=1, column=0, rowspan=6)

		except:
			self.show_info("Failed to initialise the menu") # show info is defined later in the script but it is essentially a toplevel window that can display any messgae I want it to
			
		button_info = [ # a list which stores the information of the buttons and what type of customisation is associated with each
			("Small Fish", None), # none for non-customisable food
			("Regular Fish", None),
			("Large Fish", None),
			("Regular Chips", None),
			("Large Chips", None),
			("7\" Pizza", "Pizza"), # pizza to bring up the pizza menu
			("10\" Pizza", "Pizza"),
			("12\" Pizza", "Pizza"),
			("Kebab Wrap", None),
			("Mega Kebab Wrap", None),
			("Mega Mixed Kebab Wrap", None),
			("Chicken Tikka Wrap", None),
			("Small Sauce", "Sauce"), # sauce to bring up the sauce menu
			("Large Sauce", "Sauce"),
			("Can Of Pop", None),
			("Bottle Of Pop", None),
			("Total", "Total") # the total button to confirm an order
		]

		self.buttons = [] # list for buttons so when i want to deactivate them i can just iterate through the list and just deactivate them all

		for name, customisation_type in button_info:
			
			if customisation_type == "Total": # place the total button in its assigned place with its unique function
				button = tk.Button(self.button_frame, text="Total", command=self.button_total_clicked, height=3)

			non_custom_food_lambda = lambda name=name: self.non_customisable_food_button(name) # the commands that will be ran when the button is pressed 
			custom_pizza_lambda = lambda size=name: self.pizza_customisation_menu(size) # each button will execute one of three functions depending what food is associated with that button
			custom_sauce_lambda = lambda size=name: self.sauce_customisation_menu(size)

			if customisation_type == None: # create each button
				button = tk.Button(self.button_frame, text=f"{name}", command=non_custom_food_lambda, width=10, height=3, wraplength=80)
			if customisation_type == "Pizza":
				button = tk.Button(self.button_frame, text=f"{name}", command=custom_pizza_lambda, width=10, height=3, wraplength=80)
			if customisation_type == "Sauce":
				button = tk.Button(self.button_frame, text=f"{name}", command=custom_sauce_lambda, width=10, height=3, wraplength=80)

			self.buttons.append(button) # add the button info to the llist

		row_count = 0
		column_count = 0

		loop = 0
		
		try:
			for button in self.buttons:
				if loop == 16: # places the 17th button which is my total button under the rest of the buttons and spans it across so its the same width as 4 buttons
					button.grid(row=row_count, column=column_count, columnspan=6, padx=5, pady=(15,0), sticky="ew")
				else:
					button.grid(row=row_count, column=column_count, padx=5, pady=5) # otherwise just place each button on the grid in a 4x4 layout
					column_count += 1
					if column_count == 4:
						column_count = 0
						row_count += 1
					loop += 1

			if self.elevated_privellege: # if the program is being ran in admin mode with elevated privelleges enabled

				self.admin_mode_label = tk.Label(self.button_frame, text="\n Admin Mode", font=("Helvetica-Bold", 18), fg="dark red") # add this label to the bottom of the program so the user knows
				self.admin_mode_label.grid(row=7, column=0)
	
			self.output_text = tk.Text(root, width=40, height=20, font="Arial") # output text to put the current items in the transaction into a receipt like format
			self.output_text.grid(row=0, column=1, rowspan=6, padx=10, pady=(10, 0), sticky="nsew")

			scrollbar = tk.Scrollbar(root, command=self.output_text.yview) # a scroll bar incase text goes off the screen so everything can still be viewed
			scrollbar.grid(row=0, column=2, rowspan=6, sticky="ns") 

			self.output_text.config(yscrollcommand=scrollbar.set) # sets the scroll bar

			self.new_order_frame = tk.Frame(root) # create a new frame
			self.new_order_frame.grid(row=6, column=1, padx=10, sticky="ew")

			self.new_order_button = tk.Button(self.new_order_frame, text="New Order", command=self.new_order, state=tk.DISABLED, width=18, height=3)
			self.new_order_button.pack(side=tk.LEFT) # sets the button to start a new order

			self.remove_button = tk.Button(self.new_order_frame, text="Remove Last Item", command=self.remove_last_item, width=18, height=3)
			self.remove_button.pack(side=tk.LEFT) # sets the button to remove the last item entered into the order 

			for button in self.buttons:
				button.config(state=tk.DISABLED) # disables all the food and order buttons initially

			self.remove_button.config(state=tk.DISABLED) 
			self.new_order_button.config(state=tk.NORMAL) # allows you to start a new order
		
		except:
			self.show_info("Failed to place buttons on grid")

	def show_info(self, info): # used to display important information in its own window
		self.information_window = tk.Toplevel(root) # brings it to the front
		self.information_window.title("Alert")

		label = tk.Label(self.information_window, text=(info), font=("Helvetica-Bold", 12)) # display whatever warning I need to display
		label.pack(padx=20, pady=20,)
		
		okay_button = tk.Button(self.information_window, text="          Close          ", command=self.information_window.destroy)
		okay_button.pack(pady=10)

		self.information_window.bind("<Return>", lambda event=None: self.information_window.destroy()) # allows the user to press return on their keyboard to close the window easily

	def non_customisable_food_button(self, name): # used to add the information about a non customisable food that has been added to the order to the receipt
		output_text = self.current_order.add_non_customisable_food(name) # thats the name of the food as a parameter and uses the backend function to add it to the menu
		self.output_text.insert(tk.END, output_text) # add it to the receipt
	
	def button_total_clicked(self): # the function that is ran when an order is confirmed
		
		try:
			customer_name = self.customer_name_entry.get() # get the text from the customer name text box
			customer_name = customer_name.capitalize() # capitalise the name 
		except:
			self.show_info("Customer Name Invalid") # if the name causes an issue alert the user that it can't be used instead of crashing the system
			customer_name = None # delete the invalid name

		receipt, private_key_found = self.current_order.do_receipt(customer_name) # this function sorts out the receipt for my records and gets the total price for the transaction
		
		if self.elevated_privellege: # if in admin mode it will attempt to automatically sign the receipt 
			if not private_key_found: # if there is no private key it can't do that however 
				self.show_info("Private Key not found\nOrder not signed")
		
		self.output_text.insert(tk.END, receipt) # add the total price to the receipt
		self.output_text.see(tk.END) # scroll to the end of the receipt to automatically be able to view the total price of the transaction
		self.confirmation_status = True # the order is now confirmed

		for button in self.buttons:
			button.config(state=tk.DISABLED) # disable the buttons again

		self.admin_button.config(state=tk.NORMAL) # bring back the admin menu
		self.remove_button.config(state=tk.DISABLED) 
		self.new_order_button.config(state=tk.NORMAL) # allow the user to start a new order 
			
		bf.update_active_orders() # update the list of orders that are currently active so they can be managed

	def remove_last_item(self): 
		
		self.current_order.remove_last_item_from_receipt() # removes the last item from the receipt list 
		
		current_line = self.output_text.index(tk.INSERT) # puts you onto a new line
		current_line_number = int(current_line.split('.')[0])
 
		previous_line_index = f"{current_line_number - 1}.0" # goes back a line

		self.output_text.delete(previous_line_index, current_line) # deletes the whole line to remove the last item 

	def new_order(self): # the function that is ran when a new order is started

		try: 
			self.current_order = bf.new_order() # run the backend new order function to obtain the object for the current order
			cur_order_count = bf.active_order_count() # the number of current active orders 

			if cur_order_count > 4 and not self.elevated_privellege:
				self.show_info(f"You already have {cur_order_count} orders open\nTry not to open too many orders at once.",) # warns you if you have too many orders open at the same time to potentially help manage workload and to not open too many orders at the same time
			
			self.admin_button.config(state=tk.DISABLED) # disable the admin button 
			self.output_text.delete("1.0", tk.END) # clear the text box
			self.confirmation_status = False # resets the confirmation status as the current order is not complete

			for button in self.buttons:
				button.config(state=tk.NORMAL) # sets all the buttons to their active state

			self.customer_name_entry.config(state=tk.NORMAL)
			self.remove_button.config(state=tk.NORMAL)
			self.new_order_button.config(state=tk.DISABLED)

			self.customer_name_entry.delete(0, tk.END) # delete the information from the customer name box
			self.customer_name_entry.focus_set() # set the focus to this text box so the user can just type and it will automatically type into this box to potentially speed up the order taking process 

			number = self.current_order.get_order_number() # gets the order number to put at the top of the receipt
			self.output_text.insert(tk.END, f"Order {number}\n\n") 
		except:
			self.show_info("An unknown problem has occured\nPlease make sure the correct directory is set.")

	def pizza_customisation_menu(self, pizza_size): # function for if a pizza is added to the order
		customisation_window = tk.Toplevel(self.root) # opens pizza menu
		customisation_window.title(f"{pizza_size} Customisation")
		pizza_size = pizza_size.split('"')[0] # get the size of the pizza in inches
		pizza_size = pizza_size.strip() 

		def custom_option_clicked(option_text, pizza_size): # will be ran after the choice for which pizza is being ordered has been made

			text = self.current_order.get_pizza_price(pizza_size, option_text) # gets the price from my pizza database

			self.output_text.insert(tk.END, text) # add the pizza information to the receipt on screen
			customisation_window.destroy() # closes the window

		custom_options = bf.get_toppings() # gets the toppings from my database

		row_count = 0
		column_count = 0

		for option_text in custom_options: # places the buttons to represent each topping onto the window
			pizza_button = tk.Button(customisation_window, text=option_text, width=10, height=3,
									  command=lambda opt=option_text: custom_option_clicked(opt, pizza_size), wraplength=80)
			pizza_button.grid(row=row_count, column=column_count, padx=7, pady=5)
			column_count += 1
			if column_count == 4:
				column_count = 0
				row_count += 1
	
	def view_order_menu(self, menu_usage): # this menu will be used at any point if the user wants to read receipts from inside the program for various situations
		
		todays_date = bf.current_date.strftime("%Y-%m-%d")

		if menu_usage == "active": # if its bringing up the active orders then it allows you to clear orders
			clear_order = True
			orders = bf.update_active_orders() # ensure we have the most recent set of active orders
		elif menu_usage == "signature_active": # if you're checking the signatures of orders from today it will return all the orders for the day not just the active orders
			orders = bf.return_legacy_orders(todays_date)
		elif menu_usage == "void_active": # if you're looking to void an order from today then it will also show all the orders from today but will enable the void order button aswell instead of the clear order button
			clear_order = False
			void_order = True
			orders = bf.return_legacy_orders(todays_date)
		elif menu_usage == "legacy_unsigned": # if you're looking to sign orders from the past it will use the backend function to get all the unsigned receipts from the past
			order_list = bf.get_unsigned_orders()
			orders = [f"{order[2]}.txt" for order in order_list]
			clear_order = False # you can't clear or void orders from the past
			void_order = False
		else: # if you just want to view orders from the past for any other reason then you will only be able to view them not clear them or void them
			void_order = False 
			clear_order = False # if you're viewing legacy orders you can't clear them just view them
			orders = bf.return_legacy_orders(menu_usage)

		try:
			if len(orders) == 0: # if there's no receipts to display for a specific search there is nothing to show such as if there's no currently active orders
				self.show_info("No Orders To\nDisplay.")    
			else:    
				self.active_orders_window = tk.Toplevel(self.root) # bring the window to the top level
				self.active_orders_window.title("Orders")
				
				canvas = tk.Canvas(self.active_orders_window)
				canvas.pack(side="left", fill="both", expand=True)

				scrollbar = tk.Scrollbar(self.active_orders_window, orient="vertical", command=canvas.yview) # add a scroll bar to the window
				scrollbar.pack(side="right", fill="y")

				canvas.configure(yscrollcommand=scrollbar.set)

				frame = tk.Frame(canvas)

				canvas.create_window((0, 0), window=frame, anchor="nw")
				
				for index, order in enumerate(orders, start=1): # attach an internal number to each order to be able to place a variable number of items onto this menu using enumerate
				
					orderDisplay = order[0:-4].capitalize()

					if menu_usage == "legacy_unsigned":
						order_date = order_list[index - 1][1] # if orders from different dates are being displayed at the same time as they are in this scenario the date needs to be next to each order incase you have order 2 from yesterday and order 2 from 3 days ago appearing at the same time, this way the user can view the correct order 2 that they need at the time without getting confused
						orderDisplay += f" ({order_date})"

					tk.Label(frame, text=f"{orderDisplay}\t\t\t", font=("bold", 16)).grid(column=0, row=(index - 1) * 4, columnspan=2, sticky="ew")

					if menu_usage == "signature_active": # if you're looking to validate or sign an order from today 
						
						verify_order_lambda = lambda order=order: self.verify_order_for_today(order) # add the verify button with the verify command 
						tk.Button(frame, text="Verify Order", command=verify_order_lambda).grid(column=0, row=(index - 1) * 4 + 2, columnspan=2, sticky="ew")
						view_order_lambda = lambda order=order: self.view_order(order, todays_date) # set the view command to take today's date as the date parameter
						sign_order_lambda = lambda order=order: self.sign_order_for_today(order) # add the sign order button
					
					elif menu_usage == "legacy_unsigned": # if the menu is being used to sign orders from previous days	
						
						sign_order_lambda = lambda order=order, date=order_date: self.sign_order_for_date(order, date) # allow you to sign the order but will need the date of the order
						view_order_lambda = lambda order=order, date=order_date: self.view_order(order, date) # allow you to view orders but also provided the date 

						tk.Button(frame, text="View Order", command=view_order_lambda).grid(column=0, row=(index - 1) * 4 + 1, columnspan=2, sticky="ew") # initilaise the view and sign order commands
						tk.Button(frame, text="Sign Order", command=sign_order_lambda).grid(column=0, row=(index - 1) * 4 + 3, columnspan=2, sticky="ew")
					
					else:
						clear_order_lambda = lambda order=order: self.clear_order(order, self.active_orders_window, menu_usage) # otherwise initalise the commands to clear, view and void orders
						view_order_lambda = lambda order=order: self.view_order(order, menu_usage)
						void_order_lambda = lambda order=order: self.void_selected_order(order)

						if clear_order: # depending on the given use case display the necessary buttons
							tk.Button(frame, text="Clear Order", command=clear_order_lambda).grid(column=0, row=(index - 1) * 4 + 1, columnspan=2, sticky="ew")

						elif void_order:
							tk.Button(frame, text="Void Order", command=void_order_lambda).grid(column=0, row=(index - 1) * 4 + 1, columnspan=2, sticky="ew")

						tk.Button(frame, text="View Order", command=view_order_lambda).grid(column=0, row=(index - 1) * 4 + 2, columnspan=2, sticky="ew")

				frame.update_idletasks()
				
				canvas_width = canvas.winfo_width()
				frame_width = frame.winfo_width()
				
				if canvas_width > frame_width:
					canvas.create_window((canvas_width - frame_width) // 2, 0, window=frame, anchor="nw")

				canvas.configure(scrollregion=canvas.bbox("all"))
		except:
			self.show_info("There is a problem with your 'config.ini' file\nPlease make sure the correct directories are set.")

	def clear_all_orders(self): # a function to clear all the current active orders
		
		orders = bf.update_active_orders() # get the latest record of active orders

		try:
			for order in orders:
				bf.clear_selected_order(order) # use the backend function to clear an order on every active order
			self.show_info("All orders cleared") # if successful inform the user
		except:
			self.show_info(f"Failed to clear {order}") # otherwise inform the user about which order caused an error

	def verify_order_for_today(self, order): # a function to verify the integrity of an order from today

		integrity = bf.verify_order_for_today_bridge(order) # use the backend function to determine wether the order can be verified

		if integrity:
			self.show_info("Order Signed") 
		else:
			self.show_info("Order NOT Signed")

	def sign_order_for_today(self, order): # a function to sign an order from today

		success = bf.sign_order_for_today_bridge(order) # use the backend function to sign the order

		if success:
			self.show_info("Order Sucessfully Signed")
		else:
			self.show_info("Error Signing Order")

	def sign_order_for_date(self, order, date): # a function used to sign an order from a date that isn't today 
		
		success = bf.sign_order_for_date_bridge(order, date) # use the backend function to sign the order
		
		if success:
			self.active_orders_window.destroy() # close the window and open it again with the new list of orders after signing one
			self.view_order_menu("legacy_unsigned")
		else:
			self.show_info("Order failed to sign")
		
	def view_order(self, order, date):
		new_window = tk.Toplevel(root)
		new_window.title(f"{order.capitalize()}") # the name of the window is the order number

		orderLines = bf.get_order_to_view(order, date) # use the backend function to get the receipt for the order to display it

		canvas = tk.Canvas(new_window)
		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		scrollbar = tk.Scrollbar(new_window, command=canvas.yview)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		canvas.configure(yscrollcommand=scrollbar.set)

		frame = tk.Frame(canvas)
		canvas.create_window((0, 0), window=frame, anchor=tk.NW)

		for line in orderLines: # add each line of the receipt to the window
			label = tk.Label(frame, text=" " + line + " ", font=("Helvetica", "14"), anchor="w")
			label.pack(fill=tk.X)

		frame.update_idletasks()
		canvas.config(scrollregion=canvas.bbox(tk.ALL))

	def clear_order(self, order, active_orders_window, date): # the function used to clear an active order

		bf.clear_selected_order(order) # use the back end function to clear an order
		self.active_orders = bf.update_active_orders() # update the active orders
		active_orders_window.destroy() # close and reopen the window with the new list of active orders
		self.view_order_menu(date)

	def sauce_customisation_menu(self, sauce_size): # a fucntion used to pick a specific sauce to add to an order

		customisation_window = tk.Toplevel(self.root)
		customisation_window.title(f"Sauce Customisation")

		def custom_option_clicked(option_text): # used to confirm the sauce choice and add it to the receipt 

			text = self.current_order.custom_sauce(sauce_size, option_text)

			self.output_text.insert(tk.END, text)
			customisation_window.destroy() 

		custom_options = ["Garlic Sauce", "Chilli Sauce", "Curry Sauce", 
						"Mushy Peas", "Gravy", "Ketchup"] # the sauce options

		row_count = 0
		column_count = 0

		for option_text in custom_options: # create and place the buttons for each sauce where the command is the function to confirm the option
			custom_button = tk.Button(customisation_window, text=option_text, width=10, height=3,
									  command=lambda opt=option_text: custom_option_clicked(opt), wraplength=80)
			custom_button.grid(row=row_count, column=column_count, padx=7, pady=5)
			column_count += 1
			if column_count == 3:
				column_count = 0
				row_count += 1
	
	def admin_menu(self): # function to grant you access to the admin menu
		if self.elevated_privellege: # if you're in admin mode it will automatically open the menu without asking for a password
			self.open_admin_options() # the function to open the admin menu
		else: # otherwise open a password prompt
			password_window = tk.Toplevel(self.root)
			password_window.title("Password Prompt")

			label = tk.Label(password_window, text="Enter Admin Password:")
			label.pack(pady=10)

			password_entry = tk.Entry(password_window, show="*") # show asterisks instead of the actual characters of the password while the password is being entered
			password_entry.pack(padx=10)
			password_entry.focus_set() # set the focus to the text entry bar

			def hash_password(password): # sub function to return the hash of the entered text
				hash_obj = hashlib.sha256(password.encode())
				return hash_obj.hexdigest()

			correct_password_hash = bf.get_admin_password()[0] # get the stored password hash

			def check_password(): 
				entered_password_hash = password_entry.get() # get the input from the text box
				entered_password_hash = hash_password(entered_password_hash) # hash it

				if entered_password_hash == correct_password_hash: # determine if they match
					password_window.destroy() # destroy the prompt window
					self.open_admin_options() # allow access to the admin menu
				else:
					self.show_info("Incorrect Password Entered\nPlease Try Again") # otherwise alert the user they have entered the incorrect password
					password_entry.delete(0, tk.END)

			check_button = tk.Button(password_window, text="      Log In      ", command=check_password)
			check_button.pack(pady=10)

			password_entry.bind("<Return>", lambda event=None: check_password()) # allows you to press the return key to check the password instead of clicking the log in button with the mouse to save time

	def open_admin_options(self): # the function to open the admin menu
		admin_options = tk.Toplevel(self.root)
		admin_options.title("Admin Options")

		admin_options_frame = tk.Frame(admin_options)
		admin_options_frame.pack(fill="both", expand=True)

		# Create buttons with a consistent width and increased height
		button_width = 20
		button_height = 3 

		# define and place all the buttons for the various options

		self.change_password_button = tk.Button(admin_options_frame, text="Today's Total Takings", command=self.total_takings, width=button_width, height=button_height)
		self.change_password_button.grid(column=0, row=0, pady=5, padx=5, sticky="nsew")

		self.daily_report_button = tk.Button(admin_options_frame, text="Daily Report", command=self.daily_report, width=button_width, height=button_height)
		self.daily_report_button.grid(column=1, row=0, pady=5, padx=5, sticky="nsew")

		self.void_order_button = tk.Button(admin_options_frame, text="Void Order", command=lambda: self.view_order_menu("void_active"), width=button_width, height=button_height)
		self.void_order_button.grid(column=0, row=1, pady=5, padx=5, sticky="nsew")

		self.toggle_admin_button = tk.Button(admin_options_frame, text="Toggle Admin Mode", command=self.toggle_admin_mode, width=button_width, height=button_height)
		self.toggle_admin_button.grid(column=1, row=1, pady=5, padx=5, sticky="nsew")

		self.sign_verify_files_today_button = tk.Button(admin_options_frame, text="Signatures (Today)", command=lambda: self.view_order_menu("signature_active"), width=button_width, height=button_height)
		self.sign_verify_files_today_button.grid(column=0, row=2, pady=5, padx=5, sticky="nsew")

		self.sign_all_legacy_files_button = tk.Button(admin_options_frame, text="Sign all previous files", command=self.sign_all_legacy_files)
		self.sign_all_legacy_files_button.grid(column=1, row=3, pady=5, padx=5, sticky="nsew")

		self.clear_all_active_orders_button = tk.Button(admin_options_frame, text="Clear all orders", command=self.clear_all_orders, width=button_width, height=button_height)
		self.clear_all_active_orders_button.grid(column=1, row=2, pady=5, padx=5, sticky="nsew")

		self.regenerate_keys_button = tk.Button(admin_options_frame, text="Regenerate Keys", command=self.activate_regenerate_keys, width=button_width, height=button_height)
		self.regenerate_keys_button.grid(column=0, row=3, pady=5, padx=5, sticky="nsew")

		# Configure columns and rows to expand
		admin_options_frame.columnconfigure(0, weight=1)
		admin_options_frame.columnconfigure(1, weight=1)
		admin_options_frame.rowconfigure(0, weight=1)
		admin_options_frame.rowconfigure(1, weight=1)
		admin_options_frame.rowconfigure(2, weight=1)
		admin_options_frame.rowconfigure(3, weight=1)

		# Update the layout
		admin_options.update_idletasks()

	def sign_all_legacy_files(self):
		
		self.view_order_menu("legacy_unsigned")

	def activate_regenerate_keys(self): # admin option to regenerate the public and private ecryption keys and re sign every receipt in the archives
		output = bf.bridge_regenerate_keys() # use the backend regenerate keys function
		self.show_info(output) # show the user whether it was successful or not

	def toggle_admin_mode(self): # toggle admin mode on or off 
		self.elevated_privellege = bf.toggle_elevated_privellege() # use the backend function to adjust the config file			

		python = sys.executable # close the program and automatically re open it with elevated privelleges changed so it will open in admin mode or vice versa
		os.execl(python, python, *sys.argv)

	def total_takings(self): # a funciton to display the total takings for the day so far
		try:
			total_price = bf.get_todays_takings() # use the backend function to calculate the total takings for the day
		
			total_takings_window = tk.Toplevel(root)
			total_takings_window.title("Total Takings") # create a window to display the information

			label = tk.Label(total_takings_window, text=f"Today's total takings are {total_price}", font=(12), wraplength=110)
			label.pack(padx=20, pady=20,) 

			okay_button = tk.Button(total_takings_window, text="          Close          ", command=total_takings_window.destroy)
			okay_button.pack(pady=10)
		
		except:
			self.show_info("Error retrieving total takings,\none or more of your files may not\nhave valid signatures")

	def daily_report(self): # a function to display the daily report of items sold for a specific date

		def get_selected_date(): # a function to get the date selected from a calendar widget in the correct format to match file system naming scheme 
			
			selected_date = cal.get_date() # get the date from the calendar 
			selected_date = selected_date.split("/") # split it 

			calendar.destroy() # delete the calendar widget
			 
			month = int(selected_date[0])
			day = int(selected_date[1])
			year = int(selected_date[2])

			century = 2000

			date = datetime.datetime(century + year, month, day)
			date = date.strftime("%Y-%m-%d") # format the date into the same format as the folder names

			try:
				report, total_price = bf.create_report(date) # use the backend function to create a report
				report_window = tk.Toplevel(self.root) # create a window to add the daily report to
				report_window.title(f"Report for {date}")           
			except:
				self.show_info("The date you've selected does not have any orders to report")
			else:
				label = tk.Label(report_window, text="", font=("Helvetica", "16"))
				label.grid(row=0, column=0)
				
				# add information about when the report was created to the report 

				currentTime = datetime.datetime.now().time()
				formattedTime = currentTime.strftime("%H:%M:%S")
				date = datetime.datetime(century + year, month, day)
				formattedDate = date.strftime("%d-%m-%Y")
				
				label_text = f"Report for {formattedDate} as of {formattedTime} Today\n\n"
				
				for key, (quantity, price) in report.items(): # add each item in the dictionary to the window
					label_text += f"  {key.title()}: Quantity = {quantity}, Price = £{price}  \n"

				label_text += f"\nTotal Takings: £{total_price}" # add the total takings 
				label_text += f"\n\nUnverified receipts have been omitted" # alert the user that unverified receipts will not contribute to the report
				label_text += f"\n\nA copy of this information has been made in the corresponding folder for these orders"

				label.config(text=label_text)

				# add an option to break the report down order by order to display all the receipts for a specific day

				view_all_orders_from_day_button = tk.Button(report_window, text="View By Order", command=lambda: self.view_all_orders_from_day(formattedDate))
				view_all_orders_from_day_button.grid(row=1, column=0)

		calendar = tk.Toplevel(self.root)
		calendar.title("Date Selector") # create a window for the calendar widget 

		year, month, day = bf.get_current_date() # get the current date    

		cal = Calendar(calendar, selectmode="day", year=int(year), month=int(month), day=int(day))
		cal.pack() # open the calendar where the default selected date is today's date

		get_date_button = tk.Button(calendar, text="Get Selected Date", command=get_selected_date)
		get_date_button.pack() # add a button to confirm the date you have selected

	def view_all_orders_from_day(self, date): # a function view all the orders for a specific day
		
		day, month, year = date.split("-")
		date = f"{year}-{month}-{day}" # re arrange the date to match the names of the file system 
		self.view_order_menu(date) # use the view order menu function with the date as an argument to fetch all the receipts for that date

	def void_selected_order(self, order): # a function to allow the user to void an order
		
		try:
			bf.void_order(order) # use the backend function to void an order

			self.active_orders_window.destroy()
			self.view_order_menu("void_active") # reopen the list of orders to potentially void with the voided order omitted 
		except:
			self.show_info("Error voiding order")

if __name__ == "__main__": # when run directly

	root = tk.Tk() 
	
	default_font = tk.font.nametofont("TkDefaultFont")
	default_font.configure(family="Work Sans", size="10") # set the preffered font
	
	app = Menu(root) 
	root.mainloop() # start the app

