# Version 0.10 for Linux #

import datetime
import os
import sqlite3
import file_signatures as fsig
import configparser
import re

current_date = datetime.date.today() # save the system date to a variable

try:
    with open("config.ini", "r") as conf: 
        lines = conf.readlines() # save the contents of the config file to a list
        config = {}

    current_section = None

    for line in lines:
        line = line.strip() # remove any trailing spaces

        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].strip() 
            config[current_section] = {}
        elif current_section and '=' in line:
            parts = line.split('=', 1)  # Limit the split to only one occurrence
            key = parts[0].strip()
            value = parts[1].strip()
            config[current_section][key] = value # save each parameter and it's value to a dictionary

    data = config.get('Settings', {}).get('data')
    public_key_path = config.get('Settings', {}).get('public_key_path')
    private_key_path = config.get('Settings', {}).get('private_key_path')
    elevated_privellege = config.get('Settings', {}).get('elevated_privellege') # use the dictionary to save each value to a variable

    if elevated_privellege == "True": # determine wether to load in admin mode or not
        elevated_privellege = True # this seems redundant but an issue I had when parsing the config file and just converting it to boolean was that even though elevated_privelleges = "False" the boolean value of this string was still True which meant as long as something was written in the config file no matter what it was it would always set to true 
    else:
        elevated_privellege = False

except FileNotFoundError:
    print("Config File not found") # if the file isn't found it can alert the user
except Exception as e:
    print(f"An error occurred: {e}") # if there is another type of error it can alert the user of that instead

try:
    conn = sqlite3.connect(f"{data}/database.db") # open the connection to the SQL database
    cursor = conn.cursor() # a cursor is used to allow you to use SQL queries in python
except:
    print("database.db file not found") # alert the user if the database isn't found

try:
    cursor.execute("SELECT date FROM order_number_and_date") # obtain the last recorded date
    
    last_recorded_date = cursor.fetchone() # store it to a variable
    last_recorded_date = str((last_recorded_date[0])).strip()
    
    if last_recorded_date != str(current_date).strip(): # compare it to the system date
        cursor.execute("DELETE FROM active_orders") # if the dates are different we need to delete all the active orders from the previous day if there is any
        cursor.execute("UPDATE order_number_and_date SET date = ?", (str(current_date),)) # we also need to set the date to match the current system date
        cursor.execute("UPDATE order_number_and_date SET order_num = 1") # and reset the next order number back to 1
        conn.commit() # finally we need to commit these changes so they take effect 

except Exception as e: # if the table is missing it can alert the user to make sure their database is formatted correctly
    print("Error! Ensure database.db is formatted correctly")

folder_name = current_date.strftime("%Y-%m-%d") #in this format so folders can sort by earliest created when sorted by name
today_folder = os.path.join(f"{data}/Receipts", folder_name) # the path for a folder in the reciepts folder to store the receipts for today where the name of that folder is today's date

try:
    if not os.path.exists(today_folder): # make the folder if it doesn't already exist
        os.makedirs(today_folder)
except:
    print("Error creating receipts folder, check data directory in config.ini is correct") # if there is an issue creating the folder alert the user

today_signature_path = os.path.join(today_folder, "signatures") # save the file path of where the signature files for today will be stored

try:
    if not os.path.exists(today_signature_path):
        os.makedirs(today_signature_path) # make the folder if it doesn't exist
except:
    print("Error creating signatures folder, check data directory in config.ini is correct") # alert the user if there is an error

class CurrentOrder:
    def __init__(self, order_num): # initialise the class for the current order
        self.order_num = order_num # save the order number
        self.receipt = [] # initalise an empty receipt to add items to
        # receipt will be a 2D array where each item will be formatted like this: (item_name, price)

    def get_order_number(self):
        
        return self.order_num # getter for the order number 

    def remove_last_item_from_receipt(self):

        self.receipt.pop() # removes the last item from the receipt by popping it from the list
    
    def do_receipt(self, name): # total all the items in the receipt
    
        total_price = 0.0

        for i in range (len(self.receipt)): # add the price of every item in the list together
            total_price += float(self.receipt[i][1]) # the price will be the second value of each item in the list
        
        total_price = f"{total_price:.2f}" # formatted to look like a monetary value at the end of the addition

        file_name = f"order {self.order_num}.txt" # the name of the file that will be created for the receipt
        file_path = os.path.join(today_folder, file_name) # the path for where this text file will be created

        cursor.execute("INSERT INTO active_orders (order_num) VALUES (?)", (self.order_num,)) # add the order number of the order that has just been places to the active orders table in the database to signal it is an open order
        conn.commit() # commit the change

        current_time = datetime.datetime.now().time() # get the current system time to mark the receipt with
        formatted_time = current_time.strftime("%H:%M:%S") # convert the time to this format

        with open(file_path, "w") as r: # create the reciept

            r.write(f"{current_date} {formatted_time}\n\n") # mark it with the date and time of the order

            r.write(f"Order: {self.order_num}\n\n") # as well as the order number

            if len(name) != 0:
                r.write(f"Customer Name: {name}\n\n") # if a customer name is given mark that but if there isn't just ignore it

            for item in self.receipt:
                item_name = item[0]
                item_price = f"{float(item[1]):.2f}"
                formatted_item = f"{item_name}: £{item_price}" # add each item to the receipt in this format
                r.write(formatted_item + "\n")

            r.write(f"\nTotal Price: £{total_price}") # mark the reciept with the total price of the transaction at the bottom
        try:
            if elevated_privellege: # if the manager is placing this order in admin mode
                signature = fsig.sign_file(private_key_path, file_path) # it will automatically attempt to sign the file using the function from the previous script
                fsig.save_signature(signature, signature_file_path=f"{today_folder}/signatures/{file_name}.signature") # it will also attempt to save the signautre using the function from the previous script
                private_key_found = True
            else:
                private_key_found = False
        except Exception as e:
            private_key_found = False # determine wether the private key is available to the user as an order may be getting placed on a terminal where the private key isn't available

        return (f"\nTotal: £{total_price}", private_key_found) # return the total price of the transaction and wether the private key was found or not to the GUI to display this information accordingly
    
    def get_pizza_price(self, size, toppings): # function to determine the price of a pizza

        # convert the number in the size to a word 
        if size == "7": 
            size_word = "seven"
        elif size == "10":
            size_word = "ten"
        elif size == "12":
            size_word = "twelve"

        cursor.execute(f"""SELECT top_cat_prices.{size_word}_price FROM toppings 
        JOIN top_cat_prices ON toppings.price_cat = top_cat_prices.price_cat 
        WHERE toppings.topping = '{toppings}';""")

        # this SQL query uses a join to determine the price of the pizza by looking at which pizza it has been passed and which pricing category it falls under then it joins to the toppings category table and uses the size to determine how much a pizza is in that price category and for that size

        price = cursor.fetchone()[0] # saves the price to a variable
        price_format = (f"£{price:.2f}") # and formats it
        pizza = (f"{size}\" {toppings} Pizza")
        self.receipt.append((pizza, price)) # it then adds it to the receipt of the current order

        return (f"{pizza} - {price_format}\n") # returns the pizza and it's formatted price to the GUI to be displayed

    def add_non_customisable_food(self, food_item): # function to add a food to the receipt from the non customisable food table           
        
        cursor.execute("SELECT item_price FROM non_customisable_items WHERE item_name = ?", (food_item,))
        price = cursor.fetchone()[0] # get the price of the item from the database and save it to a variable

        self.receipt.append((food_item, price)) # add it to the receipt 
        return f"{food_item} - £{price:.2f}\n" # return the item name and formatted price to the GUI to be displayed
    
    def custom_sauce(self, size, sauce): # function to add a sauce to the order

        if size == "Small Sauce": # as all sauces cost the same amount dependant on size all thats needed is to get the price dependant on the size
            self.receipt.append([f"Small {sauce}" ,"1.10"]) # adds a small sauce
            return f"Small {sauce} - £1.10\n" # returns the price of a small sauce
        elif size == "Large Sauce": 
            self.receipt.append([f"Large {sauce}" ,"1.40"]) # adds a large sauce
            return f"Large {sauce} - £1.40\n" # returns the price of a large sauce
    
def set_order_number(): # a function used to get the order number of the next order as well as increment the next order number value in the database for the next order

    cursor.execute("SELECT order_num FROM order_number_and_date") # gets the order number from the database

    order_num = str(cursor.fetchone()) # saves it to a variable
    order_num = order_num[1:-2]

    next_order_num = int(order_num) + 1 # gets the next order number

    cursor.execute("UPDATE order_number_and_date SET order_num = ?", (next_order_num,)) # updates the database using this value
    conn.commit() # commit the changes

    return order_num # return the order number

def new_order(): # a function to start a new order

    order_num = set_order_number() # get the order number for the new order
    current_order = CurrentOrder(order_num) # create a new object for the current order using the order number it has just obtained

    return current_order # return this object to the GUI so it can be accessed there

def get_toppings(): # a function to add all the possible pizza toppings to a list

    cursor.execute("SELECT topping FROM toppings") # selects them all from the database
    topping_list = [item[0].strip("{}") for item in cursor.fetchall()] # saves them to a list using list comprehension

    return topping_list # return the list to the GUI

def get_order_to_view(order, date): # a function to find a receipt for a specific order to display on the GUI 

    if date == "active" or date == "void_active": # if the date parameter is equal to active or void_active it will search for the order in the folder of receipts from today
        file_path = (f"{today_folder}/{order}") # order will be the order number the user is fetching
    else:
        file_path = (f"{data}/Receipts/{date}/{order}") # otherwise an actual date will be passed to the function and the order will be displayed from the folder of the date matching the date that was passed to the function

    with open(file_path, "r") as oc:

        order_lines = [line.strip() for line in oc] # the lines of the receipt will be added to a list
    
    return order_lines # and then returned to the GUI to be displayed in the GUI line by line

def clear_selected_order(order): # a function to clear an active order and mark it as complete

    number = order[order.index(" ") + 1:order.index('.')] # obtain the order number from the parameter passed to the function
    cursor.execute("DELETE FROM active_orders WHERE order_num = ?", (number,)) # this SQL deletes the order number from the active order table
    conn.commit() # save the changes to the database thus ensuring that the order that has been cleared doesn't appear in the active order window

def void_order(order): # a function to void an order and make sure it isn't included in any analysis or history

    file_path = f"{today_folder}/{order}" # order will be the order's receipt's file name that we are voiding (order 5.txt for example)
    order_signature_file_path = f"{today_folder}/signatures/{order}.signature" # the file path to the signature if it exists
    
    os.remove(file_path) # deletes the receipt

    if os.path.exists(order_signature_file_path): # if the signature exists
        os.remove(order_signature_file_path) # delete the signature als

def get_todays_takings(): # a function to calculate the total cash takings for the day

    total_price = 0.0 # set the total price variable

    file_list = os.listdir(today_folder) # list all the receipts in today's receipt folder

    for filename in file_list:

        if filename != "daily report.txt": # don't include the daily report if it has been created
            
            filePath = os.path.join(today_folder, filename) 

            if os.path.isfile(filePath): # if the file of this run definitely exists

                with open(filePath, 'r') as file:
                    lines = file.readlines()
            
                    last_line = lines[-1].strip() # get the last line where the total price of the transaction will be
                    price = last_line.split('£')[1] 
                    price = float(price) # get the total price of the transaction as a float

                    total_price += price # add it to the total price variable
    
    total_price = (f"£{total_price:.2f}") # format the final total price to look like a monetary value
 
    return total_price # return it to the gui

def get_current_date():

    year, month, day= str(current_date).split("-")  
    return year, month, day # return today's date as 3 variables

def get_admin_password(): 

    cursor.execute("SELECT hashed_password FROM passwords") # from the password table in the database this SQL query obtains the password
    
    password = cursor.fetchone()

    return password # and returns it to the GUI

def create_report(date): # a function to create a report for the items sold on a particular day including quantity of specific items and total takings per item

    report_file_path = (f"{data}/Receipts/{date}") # the file path to the receipts folder for the date that is being analysed 
    
    files = os.listdir(report_file_path) # add all the file names to a list

    if "daily report.txt" in files: # ignore the daily report
        files.remove("daily report.txt")
    if "signatures" in files: # ignore the signatures directory
        files.remove("signatures")

    report = {} # initalise a dictionary for the report

    for receipt in files:
        
        sig_path = (f"{report_file_path}/signatures/{receipt}.signature") # the path for the signature of the order that is currently being analysed
        integrity = fsig.verify_file(public_key_path, (f"{report_file_path}/{receipt}"), sig_path) # confirm the integrity of the signature

        if not integrity: # if the integrity can not be confirmed skip this order 
            continue
        else: # otherwise
            with open((f"{report_file_path}/{receipt}"), "r") as receipt:

                file_lines = receipt.readlines()

                lines = [line.strip() for line in file_lines if "£" in line and "Total Price" not in line] # save all the lines where there is a price but not the total price as this is not a qunatifiable item

                for item in lines:
                    
                    item_name = item.split(":")[0].strip() # obtain the item name
                    item_price = (item.split("£")[1].strip()) # obtain the corresponding price 
            
                    if item_name in report: # if this isn't a new item in terms of this report and the item name already appears in the dictionary
                        
                        quantity, price = report[item_name] # the values in this dictionary are stored as a 2 part tuple (quantity, price)                 
                        quantity += 1 # increase the quantity of this item in the dictionary by 1 

                        price = float(price) + float(item_price) # increase the price by the price of one of the items
                        price = round(price, 2) # round the price to 2 decimal places as money would be represented 
                        price = f"{price:.2f}" # format it 

                        report[item_name] = (quantity, price) # update the dictionary with the new values 
                    else:
                        report[item_name] = (1, item_price) # otherwise if it is being added to the dictionary for the first time set the quantity to 1 and the price to 1 of the item

    try: # the following is used to arrnage the report so the most lucrative item is on the top and the least lucrative in this report is on the bottom
        cursor.execute("""CREATE TABLE IF NOT EXISTS report (
            item_name TEXT PRIMARY KEY,
            quantity INTEGER,
            price REAL)""") # create a table to store all the information from the dictionary

        for item_name, (quantity, price) in report.items(): # add each item into the table
            cursor.execute("""
            INSERT INTO report (item_name, quantity, price)
            VALUES (?,?,?)""", (item_name, quantity, price))

        conn.commit() # commit the changes
    except:
        print("Error accessing database") # if this fails alert the user 

    cursor.execute("""SELECT item_name, quantity, price 
    FROM report ORDER BY price DESC""") # use this SQL query to return the full table in order of price descending

    rows = cursor.fetchall() # add all to a list

    report = {} # re initialise the dictionary

    for row in rows:
        item_name, quantity, price = row 
        price = f"{price:.2f}"
        report[item_name] = (quantity, price) # add each item to the dictionary in order with it's formatted price
    
    cursor.execute("DROP TABLE IF EXISTS report") # delete the table
    conn.commit() # save the changes

    file_name = "daily report.txt" 

    file_path = os.path.join(report_file_path, file_name) # the file path for where the report for the day will be stored

    total_takings = 0.00 # initalise the total price

    with open(file_path, "w") as daily: # if the daily report file already exists open it
        pass # this will wipe it so we can start fresh, this would be useful if a daily report was created for today and then more orders are placed then we can wipe the old one and create a new one with the most recent data
    with open(file_path, "w") as daily:
        
        current_time = datetime.datetime.now().time()
        formatted_time = current_time.strftime("%H:%M:%S")

        daily.write(f"Report for {current_date} as of {formatted_time}\n\n") # mark the report with the time it was created 

        for key, (quantity, price) in report.items(): # for each item in the fictionary
            total_takings = total_takings + float(price) # the total takings + the total taking of the item that is being added to the report
            daily.write(f"{key}: Quantity = {quantity} Total Takings = £{price}\n") # write this information into the report
        total_takings = f"{total_takings:.2f}" # format the final takings 
        daily.write(f"\nTotal Takings: £{total_takings}") # write this at the end of the report

    return report, total_takings # return this information to the GUI to be displayed

def return_legacy_orders(date): # a function to return a list of orders from a previous date

    legacy_path = f"{data}/Receipts/{date}" # date will be the date the user wants a list of orders from 

    all_files = os.listdir(legacy_path) # list all the dates from the above file path

    files = [file for file in all_files if file.startswith("order")] # only keep the orders and not the daily report or signatures folder
    
    def get_order_number_from_file(file): # sub function to return the order number

        return int(file.split("order")[1].split(".")[0]) # gets just the number out of the tect file 

    files = sorted(files, key=get_order_number_from_file) # sort the orders 

    return files # return the list of files 

def update_active_orders(): # a function to update the active orders according to the system so it is synchronised with the database

    cursor.execute("SELECT * FROM active_orders ORDER BY order_num ASC") # this SQL query returns all the order numbers in ascending order to display the oldest and most urgent orders first
    order_numbers = cursor.fetchall() # save them to a variable
    active_orders = [f"order {str(number[0])}.txt" for number in order_numbers] # add them all to a list as their file names (the number 5 might be obtained from the table and it will be added to the list as "order 5.txt")

    return active_orders # return the list of active orders to the GUI

def active_order_count(): # a function to count the number of active orders, this is used to warn the user if too many orders are active and ongoing simultaneously
        
    active_orders = update_active_orders() # update the active orders so we have the most recent list of active orders
    return len(active_orders) # return the length of the list 

def toggle_elevated_privellege(): # A function toggle admin mode for the GUI

    config = configparser.ConfigParser()
    config.read('config.ini') # read the config file

    current_value = config.getboolean('Settings', 'elevated_privellege', fallback=True) # in the settings section check the value for elevated_privelleges
    new_value = not current_value # set it to the opposite 
    # if it can't find a value it will default to True and then switch to False as a safety measure

    config.set('Settings', 'elevated_privellege', str(new_value)) # update the config file with the new value

    with open('config.ini', 'w') as config_file:
        config.write(config_file) # save the changes to the file
        
    return new_value # return the new value for wether the system is in admin mode or not to the GUI

def return_elevated_privellege():

    return elevated_privellege # return the current value for elevated_privellege without changing it

def bridge_regenerate_keys(): # allow the GUIs regenerate key's option to work

    try:
        fsig.regenerate_keys(private_key_path, public_key_path, f"{data}/Receipts") # regenerate the keys by running the function in the file signatures script
        # they key paths will be taken from the config file and are defined earlier in the script

        return ("Keys regenerated") # return this message if it is successful
    except Exception as e:
        return e # otherwise alert the user of the error that was encountered

def verify_order_for_today_bridge(order): # allows the GUI to verify an order

    file_path = f"{today_folder}/{order}" # the file path of the order that is being verified
    signature_file_path = f"{today_folder}/signatures/{order}.signature" # the signature path should it exist for the order

    integrity = fsig.verify_file(public_key_path, file_path, signature_file_path) # use the verify function from the file signatures script to determine the file's integrity

    return integrity # return the value for integrity (True/False)

def sign_order_for_today_bridge(order): # Allows the GUI to sign an order

    file_path=f"{today_folder}/{order}" # the file path for the order that is being signed

    signature = fsig.sign_file(private_key_path, file_path) # create a signature for this file

    success = fsig.save_signature(signature, signature_file_path=f"{today_folder}/signatures/{order}.signature") # attempt to save that signature

    return success # return wether the signature creation was successful or not to the GUI

def sign_order_for_date_bridge(order, date): # Allows the GUI to sign a legacy order 

    file_path = f"{data}/Receipts/{date}/{order}" # date will be the date the order is from and order will be the receipt file name 
    signature = fsig.sign_file(private_key_path, file_path) # attempt to sign it and return the signature

    success = fsig.save_signature(signature, signature_file_path=f"{data}/Receipts/{date}/signatures/{order}.signature") # attempt to save that signature

    return success # return wether it was successful in doing so or not to the GUI

def get_unsigned_orders(): # list all the unsigned legacy orders

    order_list = [] # initialise the list

    for root, dirs, files in os.walk(os.path.join(data, "Receipts")): # recursively browse the receipts folder
        for file in files:
            if file.lower().startswith("order") and file.lower().endswith(".txt"): # if it is an order file 
                order_file_path = os.path.join(root, file) # get its path
                signature_file_path = os.path.join(root, "signatures", file + ".signature") # the corresponding signature path if it exists
                parent_folder_date = os.path.basename(os.path.dirname(order_file_path)) # the date for this order

                append_to_list = True

                if os.path.exists(signature_file_path): # if the signature path exists
                    integrity = fsig.verify_file(public_key_path, order_file_path, signature_file_path) # verify it's signature
                    append_to_list = not integrity # if the signature is fine it will not add it to the list of unsigned orders 

                if append_to_list:
                    match = re.search(r'order (\d+)', order_file_path, re.IGNORECASE) # if it is being added to the list it will obtain the path to the order, date of order and order number
                    order_number = match.group(0) if match else None
                    order_list.append([order_file_path, parent_folder_date, order_number]) # all of these values will be used by the GUI, if two order 5's integrity can not be confirmed it is important to note specifically which date each order 5 is from so they are not confused for eachother

    return order_list # return the list of unsigned orders to the GUI

                