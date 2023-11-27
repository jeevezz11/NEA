# Version 0.8 for Linux #

import tkinter as tk
import main as tm

def view_active_orders():
	active_orders_window = tk.Tk() # initialise the window
	active_orders_window.title("Active Orders") # give it a title

	def refresh_orders():
		active_orders_window.destroy() # resets the window by destroying it and re opening it
		view_active_orders()

	active_orders_window.bind("<Return>", lambda event=None: refresh_orders()) # if you click return on your keyboard it automatically refreshes
	refresh_button = tk.Button(active_orders_window, text="Refresh Orders", command=refresh_orders) # initialise the refresh button
	refresh_button.pack(side="bottom") # pin it to the bottom

	def show_warning(warning, errorCode): # used to display various warnings and errors
		
		warning_window = tk.Toplevel(active_orders_window) # puts the warning window on the top of the gui
		warning_window.title("Warning") # gives it a title

		label = tk.Label(warning_window, text=(warning), font=("Helvetica-Bold", 12)) # shows the warning in bold
		label.pack(padx=20, pady=20) 
		
		if errorCode == 0: # incase we're showing a warning that isn't an error
			pass
		else:
			errorLabel = tk.Label(warning_window, text=f"Error Code {errorCode}", font=("Helvetica-Bold", 10)) # else display the error code to check against the docs
			errorLabel.pack()
		
		okay_button = tk.Button(warning_window, text="          Close          ", command=warning_window.destroy) # close the warning window
		okay_button.pack(pady=10)

		warning_window.bind("<Return>", lambda event=None: warning_window.destroy()) # or close it with a key press

	try:
		active_orders = tm.get_active_orders() # get the open orders from the main script which calls the database
		active_orders.sort() # sort them for viewing
			
		canvas = tk.Canvas(active_orders_window)
		canvas.pack(side="left", fill="both", expand=True)

		scrollbar = tk.Scrollbar(active_orders_window, orient="vertical", command=canvas.yview)
		scrollbar.pack(side="right", fill="y")

		canvas.configure(yscrollcommand=scrollbar.set)

		frame = tk.Frame(canvas)

		canvas.create_window((0, 0), window=frame, anchor="nw")

		for index, order in enumerate(active_orders, start=1):
			orderDisplay = order[0:-4].capitalize()
			
			tk.Label(frame, text=f"{orderDisplay}\t\t\t", font=("bold", 16)).grid(column=0, row=(index - 1) * 3, columnspan=2, sticky="w")

			clear_order_lambda = lambda order=order: clear_order(order, active_orders_window)
			view_order_lambda = lambda order=order: view_order(order)

			tk.Button(frame, text="Clear Order", command=clear_order_lambda).grid(column=0, row=(index - 1) * 3 + 1, columnspan=2, sticky="ew")
			tk.Button(frame, text="View Order", command=view_order_lambda).grid(column=0, row=(index - 1) * 3 + 2, columnspan=2, sticky="ew")
			
		frame.update_idletasks()
		canvas_width = canvas.winfo_width()
		frame_width = frame.winfo_width()

		if canvas_width > frame_width:
			canvas.create_window((canvas_width - frame_width) // 2, 0, window=frame, anchor="nw")

		canvas.configure(scrollregion=canvas.bbox("all"))

	except:
		show_warning("There is a problem with your 'config.ini' file\nPlease make sure the correct directory is set.", "5")

	def view_order(order):

		new_window = tk.Toplevel(active_orders_window)
		new_window.title(f"{order[2:].capitalize()}")

		orderLines = tm.get_order_to_view(order)
		
		for line in orderLines:    
				
			label = tk.Label(new_window, text=" " + line + " ", font=("Helvetica","14"))
			label.pack()

	def clear_order(order, active_orders_window):

		tm.clear_selected_order(order)
		tm.update_active_orders()
		active_orders_window.destroy()
		view_active_orders()

	active_orders_window.mainloop()
	
view_active_orders()