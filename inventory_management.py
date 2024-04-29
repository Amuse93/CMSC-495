import sqlite3
from datetime import datetime

from inventory_cache import InventoryCache


def get_report_number():
    now = datetime.now()
    formatted_datetime = now.strftime('%Y%m%d%H%M%S')
    nanoseconds = now.strftime('%f')
    nanoseconds = int(nanoseconds) * 1000

    result = 'WR-' + formatted_datetime + f"{nanoseconds:09d}"
    return result


class InventoryManagement:

    def __init__(self, db_name):
        self.db_name = db_name
        self.inventory_cache = InventoryCache(self.db_name)

    def add_shelf(self, shelf):
        """Function will add a new shelf to the inventory"""

        shelf_exists = self.check_shelf_exists(shelf[0])

        # Check if the shelf already exists
        if shelf_exists != 0:
            return 1

        # Check if new shelf ID is greater than 15 characters
        if len(shelf[0]) != 7:
            return 3

        if shelf[0][:2] != 'WH' and shelf[0][:2] != 'SF':
            return 4

        # Insert new shelf into Shelf table
        queryTwo = "INSERT INTO Shelf (ShelfID) VALUES (?)"
        self.access_db(queryTwo, shelf)

        self.inventory_cache.update_cache()

        return 0

    def delete_shelf(self, shelf):
        """This function will delete a shelf from the inventory"""

        shelf_exists = self.check_shelf_exists(shelf)

        # Check if the shelf exists. If it does not, it can't be deleted
        if shelf_exists == 0:
            return 1

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        queryOne = f"SELECT COUNT(*) FROM Shelf_Product WHERE ShelfID = '{shelf}'"

        c.execute(queryOne)  # Assuming shelf is a tuple or list with at least one element
        number_of_items = c.fetchone()[0]
        conn.close()

        if number_of_items != 0:
            return 2

        # Delete the selected shelf from inventory
        queryTwo = f"DELETE FROM Shelf WHERE ShelfID = '{shelf}';"
        self.access_db(queryTwo)

        self.inventory_cache.update_cache()

        return 0

    def add_product_to_shelf(self, shelf_product_info):

        """This function will add a new product to a shelf"""
        shelf_id = shelf_product_info[0]
        product_id = shelf_product_info[1]

        if not self.check_shelf_exists(shelf_id):
            return 1

        if not self.check_product_exists(product_id):
            return 2

        if shelf_id[:2] == 'WH':
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            queryOne = f"SELECT COUNT(*) FROM Shelf_Product WHERE ProductID = '{product_id}' AND ShelfID LIKE 'WH%';"

            c.execute(queryOne)  # Assuming shelf is a tuple or list with at least one element
            product_record_exists = c.fetchone()[0]
            conn.close()

            if product_record_exists != 0:
                return 3

        if shelf_id[:2] == 'SF':
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()

            queryOne = f"SELECT COUNT(*) FROM Shelf_Product WHERE ProductID = '{product_id}' AND ShelfID LIKE 'SF%';"

            c.execute(queryOne)  # Assuming shelf is a tuple or list with at least one element
            product_record_exists = c.fetchone()[0]
            conn.close()

            if product_record_exists != 0:
                return 4

        queryThree = "INSERT INTO Shelf_Product VALUES (?,?,?)"
        params = [shelf_id, product_id, 0]
        self.access_db(queryThree, params)

        self.inventory_cache.update_cache()

        return 0

    def delete_product_from_shelf(self, product_id, shelf_id):
        """This function will add a new product to a shelf"""

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        queryOne = f"SELECT * FROM Shelf_Product WHERE ProductID = '{product_id}' AND ShelfID = '{shelf_id}';"
        c.execute(queryOne)

        quantity = c.fetchone()[2]

        conn.close()

        if quantity != 0:
            return 1

        # Delete the entry in the database
        queryTwo = f"DELETE FROM Shelf_Product WHERE ProductID = '{product_id}' AND ShelfID = '{shelf_id}'"
        self.access_db(queryTwo)

        self.inventory_cache.update_cache()

        return 0

    def move_product(self, shelf_product_info):
        """This function moves a product from one shelf to another"""
        product = shelf_product_info[0]
        from_shelf = shelf_product_info[1]
        to_shelf = shelf_product_info[2]

        # Ensure product exists
        if not self.check_product_exists(product):
            return 1

        # Ensure source shelf exists
        if not self.check_shelf_exists(from_shelf):
            return 2

        # Ensure destination shelf exists
        if not self.check_shelf_exists(to_shelf):
            return 3

        if from_shelf[:2] == 'WH' and to_shelf[:2] != "WH":
            return 4

        if from_shelf[:2] == 'SF' and to_shelf[:2] != "SF":
            return 5

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Run this query to get the quantity of the product on the old shelf. This will
        # be used to fill in the quantity in the new shelf.
        queryOne = f"SELECT Quantity FROM Shelf_Product WHERE ProductID = '{product}' AND ShelfID = '{from_shelf}';"
        c.execute(queryOne)

        shelf_product = c.fetchone()
        quantity = shelf_product[0]
        conn.close()

        # Delete the old entry in the database
        queryTwo = f"DELETE FROM Shelf_Product WHERE ProductID = '{product}' AND ShelfID = '{from_shelf}';"
        self.access_db(queryTwo)

        # Add new entry into database
        queryThree = f"INSERT INTO Shelf_Product VALUES ('{to_shelf}', '{product}', {quantity});"
        self.access_db(queryThree)

        self.inventory_cache.update_cache()

        return 0

    def receive_order(self, order_info):
        """This function will manage the inventory when a sale is made.
        When a sale is made, the quantity in the warehouse will reduce to simulate the
        automatic movement of product from the warehouse to the shelf after every transaction.
        A dictionary containing ProductID:quantity as the key/value pair will be passed to the function"""

        for element in order_info:
            product_id = element.get('ProductID')
            quantity = element.get('Quantity')

            # Update the quantity by adding the received quantity to the existing quantity
            query = (f"UPDATE Shelf_Product SET Quantity = Quantity + {quantity} "
                     f"WHERE ProductID = '{product_id}' AND ShelfID LIKE 'WH%'")
            self.access_db(query)

            # Update the total amount of the product that is in stock by adding the received quantity to the total
            queryTwo = (f"UPDATE Product SET Total_In_Stock = Total_In_Stock + {quantity} "
                        f"WHERE ProductID = '{product_id}'")
            self.access_db(queryTwo)

            self.inventory_cache.update_cache()

        return 0

    def stock_product(self, stock_info):
        """This function adds more items to the inventory of a particular product"""
        product = stock_info[0]
        quantity = stock_info[1]

        if not self.check_product_exists(product):
            return 1

        # Remove from warehouse shelf
        query = (f"UPDATE Shelf_Product SET Quantity = Quantity - {quantity} "
                 f"WHERE ProductID = '{product}' and ShelfID LIKE 'WH%'")
        self.access_db(query)

        # Add to sales floor shelf
        query = (f"UPDATE Shelf_Product SET Quantity = Quantity + {quantity} "
                 f"WHERE ProductID = '{product}' and ShelfID LIKE 'SF%'")
        self.access_db(query)

        self.inventory_cache.update_cache()

        return 0

    def report_waste(self, waste_info):
        """ Produces a waste report and updates inventory and product information """
        report_number = get_report_number()
        product_id = waste_info[0]
        shelf_id = waste_info[1]
        quantity = waste_info[2]
        reason_code = waste_info[3]
        description = waste_info[4]
        employee_id = waste_info[5]
        date = waste_info[6]

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Ensure employee exists
        query = f"SELECT Price FROM Product WHERE ProductID = '{product_id}'"
        c.execute(query)
        unit_price = c.fetchone()[0]
        conn.close()

        if not self.check_product_exists(product_id):
            return 1

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Ensure employee exists
        queryOne = f"SELECT COUNT(*) FROM Users WHERE EmployeeID = '{employee_id}'"
        c.execute(queryOne)
        employee_exists = c.fetchone()
        conn.close()

        if employee_exists == 0:
            return 2

        # Create waste report
        queryTwo = "INSERT INTO Waste_Reports VALUES (?,?,?,?,?,?,?,?)"
        paramTwo = [report_number, product_id, quantity, unit_price, reason_code, date, description, employee_id]
        self.access_db(queryTwo, paramTwo)

        # Update inventory information
        queryThree = (f"UPDATE Shelf_Product SET Quantity = Quantity - {quantity} "
                      f"WHERE ProductID = '{product_id}' AND ShelfID = '{shelf_id}';")
        self.access_db(queryThree)

        # Update product information
        queryThree = (f"UPDATE Product SET Total_In_Stock = Total_In_Stock - {quantity} "
                      f"WHERE ProductID = '{product_id}'")
        self.access_db(queryThree)

        self.inventory_cache.update_cache()

        return 0

    def list_shelves(self):
        """ Provides a list of available shelving units """
        # Pull shelf list from inventory cache
        shelves = self.inventory_cache.get_shelf_data()
        return shelves

    def search_shelves(self, param):
        """ Provides a list of shelves filtered by search criteria. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = f"SELECT * FROM Shelf WHERE ShelfID LIKE '{param}%' ORDER BY ShelfID;"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        shelves = []
        for row in rows:
            shelf = {
                "ShelfID": row[0]
            }
            shelves.append(shelf)

        return shelves

    def list_shelf_products(self):
        """ Provides a list of products along with their quantity and shelf location """
        # Pull inventory list from inventory cache
        shelf_products = self.inventory_cache.get_inventory_data()

        return shelf_products

    def search_shelf_products(self, field, param):
        """ Provides a list of products along with their quantity and shelf locations filtered by search criteria. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select ProductID, Product_Name, Quantity, and ShelfID from Shelf_Product table
        # Joined with Product table to get the Product_Name
        if field == 'Product_Name':
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Product.{field} LIKE '{param}%' "
                f"ORDER BY Shelf_Product.ShelfID;")
        else:
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Shelf_Product.{field} LIKE '{param}%' "
                f"ORDER BY Shelf_Product.ShelfID;")

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        shelf_products = []
        for row in rows:
            shelf_product = {
                "ProductID": row[0],
                "Product_Name": row[1],
                "Quantity": row[2],
                "ShelfID": row[3]
            }
            shelf_products.append(shelf_product)

        return shelf_products

    def search_shelf_products_by_shelf(self, field, param, shelf_id):
        """ Provides a list of products along with their quantity and shelf locations filtered by search criteria. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select ProductID, Product_Name, Quantity, and ShelfID from Shelf_Product table
        # Joined with Product table to get the Product_Name
        if field == 'Product_Name':
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Product.{field} LIKE '{param}%' "
                f"AND Shelf_Product.ShelfID = '{shelf_id}' "
                f"ORDER BY Shelf_Product.ShelfID;")
        else:
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Shelf_Product.{field} LIKE '{param}%' "
                f"AND Shelf_Product.ShelfID = '{shelf_id}' "
                f"ORDER BY Shelf_Product.ShelfID;")

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        shelf_products = []
        for row in rows:
            shelf_product = {
                "ProductID": row[0],
                "Product_Name": row[1],
                "Quantity": row[2],
                "ShelfID": row[3]
            }
            shelf_products.append(shelf_product)

        return shelf_products

    def get_product_data(self, product_id):
        """ Provides a list of products along with their quantity and shelf locations filtered by search criteria. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select ProductID, Product_Name, Quantity, and ShelfID from Shelf_Product table
        # Joined with Product table to get the Product_Name
        query = (
            f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
            f"FROM Shelf_Product "
            f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
            f"WHERE Shelf_Product.ProductID = '{product_id}';")

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        shelf_products = []
        for row in rows:
            shelf_product = {
                "ProductID": row[0],
                "Product_Name": row[1],
                "Quantity": row[2],
                "ShelfID": row[3]
            }
            shelf_products.append(shelf_product)

        return shelf_products

    def check_shelf_exists(self, shelf):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        query = f"SELECT COUNT(*) FROM Shelf WHERE ShelfID = '{shelf}';"
        c.execute(query)
        shelf_exists = c.fetchone()[0]
        conn.close()
        if shelf_exists == 0:
            return False
        return True

    def check_product_exists(self, product):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        query = f"SELECT COUNT(*) FROM Product WHERE ProductID = '{product}'"
        c.execute(query)
        product_exists = c.fetchone()[0]
        conn.close()

        if product_exists == 0:
            return False
        return True

    def access_db(self, script, args=None):
        """ Allows scripts to be executed for updating the database """
        # Connect to the database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Execute the query with parameters if provided
        if args:
            cursor.execute(script, args)
        else:
            cursor.execute(script)

        conn.commit()

        # Close the connection
        conn.close()
