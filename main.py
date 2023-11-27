# Version 0.8 for Linux #

import datetime
import os
import sqlite3

current_date = datetime.date.today() 

try:
    with open("config.ini", "r") as conf:
        lines = conf.readlines()
        config = {}

    for line in lines:
        parts = line.strip().split(':')
        key = parts[0].strip()
        value = parts[1].strip()
        config[key] = value

    program_folder = config.get('programFolder', 'DefaultProgramFolderValue') # setup script will have assigned paths for the program folder
    data = config.get('data', 'DefaultDataPathValue')                       # and the data folder that are used throughout

except FileNotFoundError:
    print("config.ini not found.")
except:
    print("Please ensure your config.ini file is formatted correctly")

try:
    conn = sqlite3.connect(f"{data}/database.db")
    cursor = conn.cursor()
except:
    print("database.db file not found")

try:
    cursor.execute("SELECT date FROM order_number_and_date")
    
    last_recorded_date = cursor.fetchone()
    last_recorded_date = str((last_recorded_date[0])).strip()
    
    if last_recorded_date != str(current_date).strip():
        cursor.execute("DELETE FROM active_orders")
        cursor.execute("UPDATE order_number_and_date SET date = ?", (str(current_date),))
        cursor.execute("UPDATE order_number_and_date SET order_num = 1")
        conn.commit()

except:
    print("Error! Ensure database.db is formatted correctly")

folder_name = current_date.strftime("%Y-%m-%d") #in this format so folders can sort by earliest created when sorted by name
folder_path = os.path.join(f"{data}/Receipts", folder_name)

try:
    os.makedirs(folder_path)
except FileExistsError:
    pass
except:
    print("Receipts folder not found")

today_folder = (f"{data}/Receipts/{folder_name}")

def get_order_number():

    cursor.execute("SELECT order_num FROM order_number_and_date")
    order_num = str(cursor.fetchone())
    order_num = order_num[1:-2]

    next_order_num = int(order_num) + 1

    cursor.execute("UPDATE order_number_and_date SET order_num = ?", (next_order_num,))
    conn.commit()

    return order_num

def update_active_orders():
    
    cursor.execute("SELECT * FROM active_orders ORDER BY order_num ASC")

    global active_orders

    active_orders = []
    order_numbers = cursor.fetchall()

    for number in order_numbers:
        number = str(number[0])
        
        active_orders.append(f"order {number}.txt")

def new_order():

    update_active_orders()

    global order_num
    order_num = get_order_number()

    global receipt
    receipt = []

def do_receipt(name):
    
    total_price = 0.0

    for i in range (len(receipt)):
        total_price = float(total_price) + float(receipt[i][1])
    
    total_price = f"{total_price:.2f}"   

    file_name = f"order {order_num}.txt"
    file_path = os.path.join(today_folder, file_name)

    cursor.execute("INSERT INTO active_orders (order_num) VALUES (?)", (order_num,))
    conn.commit()

    current_time = datetime.datetime.now().time()
    formatted_time = current_time.strftime("%H:%M:%S")

    with open(file_path, "w") as r:

        r.write(f"{current_date} {formatted_time}\n\n")

        r.write(f"Order: {order_num}\n\n")

        if len(name) == 0:
            pass
        else:
            r.write(f"Customer Name: {name}\n\n") 

        for item in receipt:
            item_name = item[0]
            item_price = f"{float(item[1]):.2f}"
            formatted_item = f"{item_name}: £{item_price}"
            r.write(formatted_item + "\n")

        r.write(f"\nTotal Price: £{total_price}")

    return (f"\nTotal: £{total_price}")

def add_food(food_item):           
    
    cursor.execute("SELECT item_price FROM non_customisable_items WHERE item_name = ?", (food_item,))
    price = cursor.fetchone()[0]
    receipt.append((food_item, price))

def get_pizza_price(size, toppings):

    if size == "7":
        size_word = "seven"
    elif size == "10":
        size_word = "ten"
    elif size == "12":
        size_word = "twelve"

    cursor.execute(f"""SELECT top_cat_prices.{size_word}_price FROM toppings 
    JOIN top_cat_prices AS top_cat_prices ON toppings.price_cat = top_cat_prices.price_cat 
    WHERE toppings.topping = '{toppings}';""")

    price = cursor.fetchone()[0]
    price_format = (f"£{price:.2f}")
    pizza = (f"{size}\" {toppings} Pizza")
    receipt.append((pizza, price))

    return (f"{pizza} - {price_format}\n")

def get_active_orders():

    update_active_orders()
    return active_orders

def active_order_count():

    activeOrders = get_active_orders()
    return len(activeOrders)

def get_order_to_view(order, date):

    order_lines = []

    if date == "active":
        file_path = (f"{today_folder}/{order}")
    else:
        file_path = (f"{data}/Receipts/{date}/{order}")

    with open(file_path, "r") as oc:
        for line in oc:
            order_lines.append(line.strip())
    
    return order_lines

def clear_selected_order(order):

    number = order[order.index(" ") + 1:order.index('.')]
    cursor.execute("DELETE FROM active_orders WHERE order_num = ?", (number,))
    conn.commit()

def void_order(order):

    order = (f"order {order}.txt")
    file_path = f"{today_folder}/{order}"
    try:
        os.remove(file_path)
    except:
        pass
        #! Order not found handling?

def remove_last_item():
    receipt.pop()

def get_date():
    return folder_name

def custom_sauce(size, sauce):

    if size == "small":
        receipt.append([f"Small {sauce}" ,"1.10"])
        return f"Small {sauce} - £1.10\n"
    elif size == "large":
        receipt.append([f"Large {sauce}" ,"1.40"])
        return f"Large {sauce} - £1.40\n"

def give_order_number():
    return order_num

def get_todays_takings():

    total_price = 0.0 

    file_list = os.listdir(today_folder)

    for filename in file_list:

        if filename != "daily report.txt":
        
            filePath = os.path.join(today_folder, filename)

            if os.path.isfile(filePath):
                
                with open(filePath, 'r') as file:
                    lines = file.readlines()
            
                    last_line = lines[-1].strip()
                    price = last_line.split('£')[1]
                    price = float(price)

                    total_price += price
    
    total_price = (f"£{total_price:.2f}")

    return total_price

def get_current_date():

    year, month, day= str(current_date).split("-")  
    return year, month, day

def get_admin_password():

    cursor.execute("SELECT hashed_password FROM passwords")
    results = cursor.fetchall()

    passwords = []

    for i in range(len(results)):
        passwords.append(results[i][0])

    return passwords
            
def create_report(date):

    report_file_path = (f"{data}/Receipts/{date}")
    
    files = os.listdir(report_file_path)
    
    if "daily report.txt" in files:
        files.remove("daily report.txt")

    report = {}    

    for receipt in files:

        with open((f"{report_file_path}/{receipt}"), "r") as receipt:

            lines = []
            save_lines = False

            file_lines = receipt.readlines()

            for line in file_lines:

                if "£" in line:
                    save_lines = True
                if save_lines and "Total Price" not in line and line != "\n":
                    lines.append(line.strip())

            for item in lines:
                
                item_name = item.split(":")[0].strip()
                item_price = (item.split("£")[1].strip())
        
                if item_name in report:
                    
                    quantity, price = report[item_name]                    
                    quantity += 1

                    price = float(price) + float(item_price)
                    price = round(price, 2)
                    price = f"{price:.2f}"

                    report[item_name] = (quantity, price)
                else:
                    report[item_name] = (1, item_price)

    try: 
        cursor.execute("""CREATE TABLE IF NOT EXISTS report (
            item_name TEXT PRIMARY KEY,
            quantity INTEGER,
            price REAL
        )""")

        for item_name, (quantity, price) in report.items():
            cursor.execute("""
            INSERT INTO report (item_name, quantity, price)
            VALUES (?,?,?)""", (item_name, quantity, price))

        conn.commit()
    except:
        pass

    cursor.execute("""SELECT item_name, quantity, price 
    FROM report ORDER BY price DESC""")

    rows = cursor.fetchall()

    report = {}

    for row in rows:
        item_name, quantity, price = row
        price = f"{price:.2f}"
        report[item_name] = (quantity, price)
    
    cursor.execute("DROP TABLE IF EXISTS report")
    conn.commit()

    file_name = "daily report.txt"

    file_path = os.path.join(report_file_path, file_name)

    total_price = 0.00

    with open(file_path, "w") as daily:
        pass
    with open(file_path, "w") as daily:
        
        current_time = datetime.datetime.now().time()
        formatted_time = current_time.strftime("%H:%M:%S")

        daily.write(f"Report for {current_date} as of {formatted_time}\n\n")

        for key, (quantity, price) in report.items():
                total_price = total_price + float(price)
                daily.write(f"{key}: Quantity = {quantity} Total Price = £{price}\n")
        total_price = f"{total_price:.2f}"
        daily.write(f"\nTotal Takings: £{total_price}")

    return report, total_price

def return_legacy_orders(date):

    legacy_path = f"{data}/Receipts/{date}"

    all_files = os.listdir(legacy_path)

    files = [file for file in all_files if file.startswith("order")]
    
    def get_order_number_from_file(file):

        return int(file.split("order")[1].split(".")[0])

    files = sorted(files, key=get_order_number_from_file)

    return files
