# Version 0.11 for Linux #

import tkinter as tk
import backend as bf # import the backend functions

def view_active_orders():
	active_orders_window = tk.Tk() # initialise the window
	active_orders_window.title("Active Orders") # add the title

	def refresh_orders():
		active_orders_window.destroy() # resets the window by destroying it and re opening it
		view_active_orders()

	active_orders_window.bind("<Return>", lambda event=None: refresh_orders()) # if you click return on the keyboard it automatically refreshes
	refresh_button = tk.Button(active_orders_window, text="Refresh Orders", command=refresh_orders) # initialise the refresh button
	refresh_button.pack(side="bottom") # pin it to the bottom

	# the functions used below are almost identical to the one's used in the main script on the main terminal and this allows for normalisation between scripts in how things look and operate 

	def show_info(info): # used to display various messages such as errors
		
		warning_window = tk.Toplevel(active_orders_window) # puts the warning window on the top of the GUI
		warning_window.title("Alert") # gives it a title

		label = tk.Label(warning_window, text=(info), font=("Helvetica-Bold", 12)) # shows the information in bold
		label.pack(padx=20, pady=20) 
		
		okay_button = tk.Button(warning_window, text="          Close          ", command=warning_window.destroy) # close the warning window
		okay_button.pack(pady=10)

		warning_window.bind("<Return>", lambda event=None: warning_window.destroy()) # or close it with a key press

	try:
		active_orders = bf.update_active_orders() # get the open orders from the main script which calls the database
			
		canvas = tk.Canvas(active_orders_window) # create the window canvas
		canvas.pack(side="left", fill="both", expand=True)

		scrollbar = tk.Scrollbar(active_orders_window, orient="vertical", command=canvas.yview) # add a scroll bar to scroll through orders
		scrollbar.pack(side="right", fill="y")

		canvas.configure(yscrollcommand=scrollbar.set)

		frame = tk.Frame(canvas) # create a frame to add widgets on to 

		canvas.create_window((0, 0), window=frame, anchor="nw")

		for index, order in enumerate(active_orders, start=1):
			orderDisplay = order[0:-4].capitalize()
			
			tk.Label(frame, text=f"{orderDisplay}\t\t\t", font=("bold", 16)).grid(column=0, row=(index - 1) * 3, columnspan=2, sticky="w")

			view_order_lambda = lambda order=order: view_order(order)
			tk.Button(frame, text="View Order", command=view_order_lambda).grid(column=0, row=(index - 1) * 3 + 2, columnspan=2, sticky="ew")

			# a key difference between this scripts version and and the main scripts version of this function is that the order pad can not clear active orders only the main terminal can the order pad can only view orders
			
		frame.update_idletasks()
		canvas_width = canvas.winfo_width()
		frame_width = frame.winfo_width()

		if canvas_width > frame_width:
			canvas.create_window((canvas_width - frame_width) // 2, 0, window=frame, anchor="nw")

		canvas.configure(scrollregion=canvas.bbox("all"))

	except:
		show_info("There is a problem with your 'config.ini' file\nPlease make sure the correct directory is set.")

	def view_order(order): # a function used to view a receipt in the GUI

		new_window = tk.Toplevel(active_orders_window)
		new_window.title(f"{order[2:].capitalize()}")

		orderLines = bf.get_order_to_view(order, date="active") # use the backend function to get the receipt info
		
		for line in orderLines:    
				
			label = tk.Label(new_window, text=" " + line + " ", font=("Helvetica","14")) # add them to the window
			label.pack()

	active_orders_window.mainloop() 
	
if __name__ == "__main__":
	view_active_orders() # start the program