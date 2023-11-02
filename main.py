# Version 0.7 for Linux #

import datetime
import os
import fnmatch
from datetime import timedelta
import sqlite3
import operator

currentDate = datetime.date.today()

try:
    with open("config.ini", "r") as conf:
        lines = conf.readlines()
        config = {}

    for line in lines:
        parts = line.strip().split(':')

        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            config[key] = value

    programFolder = config.get('programFolder', 'DefaultProgramFolderValue')
    data = config.get('data', 'DefaultDataPathValue')

except FileNotFoundError:
    print("config.ini not found.")

conn = sqlite3.connect(f"{data}/database.db")
cursor = conn.cursor()

orderPath = f"{data}/orderNumber.txt"

with open(orderPath, "r") as file:
    
    for line in file:
        if line[0:10] != str(currentDate):
            cursor.execute("DELETE FROM active_orders")
            conn.commit()

folderName = currentDate.strftime("%Y-%m-%d") #in this format so folders can sort by earliest created when sorted by name
folderPath = os.path.join(f"{data}/Receipts", folderName)

try:
    os.makedirs(folderPath)
except:
    pass

customDirectory = (f"{data}/Receipts/{folderName}")

def getOrderNumber():

    with open(orderPath, "r") as oF:
        lastDateStr, orderNumberStr = oF.readline().split(',')
        lastDate = datetime.date.fromisoformat(lastDateStr)
        orderNumber = int(orderNumberStr)       

    if currentDate > lastDate:
        orderNumber = 1

    with open(orderPath, "w") as oF:
        oF.write(f"{currentDate.isoformat()},{orderNumber + 1}")

    return orderNumber

def updateActiveOrders():
    
    cursor.execute("SELECT * FROM active_orders ORDER BY order_num DESC")

    global activeOrders

    activeOrders = []
    orderNumbers = cursor.fetchall()

    for number in orderNumbers:
        number = str(number)[1:-2]
        activeOrders.append(f"order {number}.txt")

def newOrder():

    updateActiveOrders()

    global orderNumber
    orderNumber = getOrderNumber()

    global receipt
    receipt = []

def doReceipt(name):
    
    totalPrice = 0.0

    for i in range (len(receipt)):
        totalPrice = float(totalPrice) + float(receipt[i][1])
    
    totalPrice = f"{totalPrice:.2f}"   

    fileName = f"order {orderNumber}.txt"
    filePath = os.path.join(customDirectory, fileName)

    cursor.execute("INSERT INTO active_orders (order_num) VALUES (?)", (orderNumber,))
    conn.commit()

    currentTime = datetime.datetime.now().time()
    formattedTime = currentTime.strftime("%H:%M:%S")

    with open(filePath, "w") as r:

        r.write(f"{currentDate} {formattedTime}\n\n")

        r.write(f"Order: {orderNumber}\n\n")

        if len(name) == 0:
            pass
        else:
            r.write(f"Customer Name: {name}\n\n") 

        for item in receipt:
            itemName = item[0]
            itemPrice = f"{float(item[1]):.2f}"
            formattedItem = f"{itemName}: £{itemPrice}"
            r.write(formattedItem + "\n")

        r.write(f"\nTotal Price: £{totalPrice}")

    return (f"\nTotal: £{totalPrice}")

def addFood(foodItem):           
    
    cursor.execute("SELECT item_price FROM non_customisable_items WHERE item_name = ?", (foodItem,))
    price = cursor.fetchone()[0]
    receipt.append((foodItem, price))

def getPizzaPrice(size, toppings, sizeWord):

    cursor.execute(f"""SELECT top_cat_prices.{sizeWord}_price FROM toppings 
    JOIN top_cat_prices AS top_cat_prices ON toppings.price_cat = top_cat_prices.price_cat 
    WHERE toppings.topping = '{toppings}';""")

    price = cursor.fetchone()[0]
    priceFormat = (f"£{price:.2f}")
    pizza = (f"{size}\" {toppings} Pizza")
    receipt.append((pizza, price))

    return (f"{pizza} - {priceFormat}\n")

def getActiveOrders():

    updateActiveOrders()
    return activeOrders

def activeOrderCount():

    activeOrders = getActiveOrders()
    return len(activeOrders)

def getOrderToView(order):

    orderLines = []

    filePath = (f"{customDirectory}/{order}")

    with open(filePath, "r") as oc:
        for line in oc:
            orderLines.append(line.strip())
    
    return orderLines

def clearSelectedOrder(order):

    number = order[order.index(" ") + 1:order.index('.')]
    cursor.execute("DELETE FROM active_orders WHERE order_num = ?", (number,))
    conn.commit()

def voidOrder(order):

    order = (f"order {order}.txt")
    filePath = f"{customDirectory}/{order}"
    try:
        os.remove(filePath)
    except:
        pass
        # Order not found handling?

def removeLastItem():
    receipt.pop()

def getDate():
    return folderName

def customSauce(size, sauce):

    if size == "small":
        receipt.append([f"Small {sauce}" ,"1.10"])
        return f"Small {sauce} - £1.10\n"
    elif size == "large":
        receipt.append([f"Large {sauce}" ,"1.40"])
        return f"Large {sauce} - £1.40\n"

def giveOrderNumber():
    return orderNumber

def getTodaysTakings():

    totalPrice = 0.0 

    fileList = os.listdir(customDirectory)

    for filename in fileList:

        if filename != "daily report.txt":
        
            filePath = os.path.join(customDirectory, filename)

            if os.path.isfile(filePath):
                
                with open(filePath, 'r') as file:
                    lines = file.readlines()
            
                    lastLine = lines[-1].strip()
                    price = lastLine.split('£')[1]
                    price = float(price)

                    totalPrice += price
    
    totalPrice = (f"£{totalPrice:.2f}")

    return totalPrice

def getCurrentDate():

    year, month, day= str(currentDate).split("-")  
    return year, month, day

def getAdminPassword():

    cursor.execute("SELECT hashed_password FROM passwords")
    results = cursor.fetchall()

    passwords = []

    for i in range(len(results)):
        passwords.append(results[i][0])

    return passwords
            
def createReport(date):

    global reportFilePath
    reportFilePath = (f"{data}/Receipts/{date}")
    
    files = os.listdir(reportFilePath)
    
    if "daily report.txt" in files:
        files.remove("daily report.txt")

    report = {}    

    for receipt in files:

        with open((f"{reportFilePath}/{receipt}"), "r") as receipt:

            lines = []
            saveLines = False

            fileLines = receipt.readlines()

            for line in fileLines:

                if "£" in line:
                    saveLines = True
                if saveLines and "Total Price" not in line and line != "\n":
                    lines.append(line.strip())

            for item in lines:
                
                itemName = item.split(":")[0].strip()
                itemPrice = (item.split("£")[1].strip())
        
                if itemName in report:
                    
                    quantity, price = report[itemName]                    
                    quantity += 1

                    price = float(price) + float(itemPrice)
                    price = round(price, 2)
                    price = f"{price:.2f}"

                    report[itemName] = (quantity, price)
                else:
                    report[itemName] = (1, itemPrice)

    try: 
        cursor.execute("""CREATE TABLE IF NOT EXISTS report (
            item_name TEXT PRIMARY KEY,
            quantity INTEGER,
            price REAL
        )""")

        for itemName, (quantity, price) in report.items():
            cursor.execute("""
            INSERT INTO report (item_name, quantity, price)
            VALUES (?,?,?)""", (itemName, quantity, price))

        conn.commit()
    except:
        pass

    cursor.execute("""SELECT item_name, quantity, price 
    FROM report ORDER BY price DESC""")

    rows = cursor.fetchall()

    report = {}

    for row in rows:
        itemName, quantity, price = row
        price = f"{price:.2f}"
        report[itemName] = (quantity, price)
    
    cursor.execute("DROP TABLE IF EXISTS report")
    conn.commit()

    fileName = "daily report.txt"

    filePath = os.path.join(reportFilePath, fileName)

    totalPrice = 0.00

    with open(filePath, "w") as daily:
        pass
    with open(filePath, "w") as daily:
        
        currentTime = datetime.datetime.now().time()
        formattedTime = currentTime.strftime("%H:%M:%S")

        daily.write(f"Report for {currentDate} as of {formattedTime}\n\n")

        for key, (quantity, price) in report.items():
                totalPrice = totalPrice + float(price)
                daily.write(f"{key}: Quantity = {quantity} Total Price = £{price}\n")
        totalPrice = f"{totalPrice:.2f}"
        daily.write(f"\nTotal Takings: £{totalPrice}")

    return report, totalPrice