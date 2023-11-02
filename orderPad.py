# Version 0.7 for Linux #

import tkinter as tk
import main as tm

def view_active_orders():
	active_orders_window = tk.Tk()
	active_orders_window.title("Active Orders")

	def refresh_orders():
		active_orders_window.destroy()
		view_active_orders()
	
	refresh_button = tk.Button(active_orders_window, text="Refresh Orders", command=refresh_orders)
	refresh_button.pack(side="bottom")

	def show_warning(warning, errorCode): 
		
		warning_window = tk.Toplevel(active_orders_window)
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

	try:
		active_orders = tm.getActiveOrders()
		active_orders.sort()
			
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

		orderLines = tm.getOrderToView(order)
		
		for line in orderLines:    
				
			label = tk.Label(new_window, text=" " + line + " ", font=("Helvetica","14"))
			label.pack()

	def clear_order(order, active_orders_window):

		tm.clearSelectedOrder(order)
		tm.updateActiveOrders()
		active_orders_window.destroy()
		view_active_orders()

	active_orders_window.mainloop()
	
view_active_orders()