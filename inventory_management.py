import sqlite3
from inventory_cache import InventoryCache


class InventoryManagement:

    def __init__(self, db_name):
        self.db_name = db_name
        self.inventory_cache = InventoryCache(self.db_name)

    def add_shelf(self, shelf):
        """Function will add a new shelf to the inventory"""

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        queryOne = 'SELECT COUNT(*) FROM Shelf WHERE ShelfID = ?'

        c.execute(queryOne, (shelf[0],))  # Assuming shelf is a tuple or list with at least one element
        shelf_exists = c.fetchone()[0]
        conn.close()

        # Check if the shelf already exists
        if shelf_exists == 1:
            return 1

        # Check if new shelf ID is greater than 15 characters
        if len(shelf[0]) > 15:
            return 3

        # Insert new shelf into Shelf table
        queryTwo = "INSERT INTO Shelf (ShelfID) VALUES (?)"
        self.access_db(queryTwo, shelf)

        return 0

    def delete_shelf(self, shelf):
        """This function will delete a shelf from the inventory"""

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        queryOne = "SELECT COUNT(*) FROM Shelf WHERE ShelfID = ?"
        c.execute(queryOne, shelf)
        shelf_exists = c.fetchone()[0]
        conn.close()

        # Check if the shelf exists. If it does not, it can't be deleted
        if shelf_exists == 0:
            return 1

        # Delete the selected shelf from inventory
        queryTwo = "DELETE FROM Shelf WHERE ShelfID = ?"
        param = shelf
        self.access_db(queryTwo, param)

        return 0

    def add_product_to_shelf(self, shelf_product_info):

        """This function will add a new product to a shelf"""

        if not self.check_shelf_exists(shelf_product_info[1]):
            return 1

        if not self.check_product_exists(shelf_product_info[0]):
            return 3

        queryThree = "INSERT INTO Shelf_Product VALUES (?,?,?)"
        params = [shelf_product_info[0], shelf_product_info[1], 0]
        self.access_db(queryThree, params)

        return 0

    def delete_product_from_shelf(self, shelf_product_info):
        """This function will add a new product to a shelf"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        queryOne = "SELECT Quantity FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?"
        params = [shelf_product_info[0], shelf_product_info[1]]
        c.execute(queryOne, params)

        shelf_product = c.fetchone()
        quantity = shelf_product[0]
        conn.close()

        if quantity != 0:
            return 1

        # Delete the entry in the database
        queryTwo = "DELETE FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?"
        self.access_db(queryTwo, params)

        return 0

    def move_product(self, shelf_product_info):
        """This function moves a product from one shelf to another"""

        # Ensure product exists
        if not self.check_product_exists(shelf_product_info[0]):
            return 1

        # Ensure source shelf exists
        if not self.check_shelf_exists(shelf_product_info[1]):
            return 2

        # Ensure destination shelf exists
        if not self.check_shelf_exists(shelf_product_info[2]):
            return 3

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Run this query to get the quantity of the product on the old shelf. This will
        # be used to fill in the quantity in the new shelf.
        queryOne = "SELECT Quantity FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?"
        params = [shelf_product_info[0], shelf_product_info[1]]
        c.execute(queryOne, params)

        shelf_product = c.fetchone()
        quantity = shelf_product[0]
        conn.close()

        # Delete the old entry in the database
        queryTwo = "DELETE FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?"
        self.access_db(queryTwo, params)

        # Add new entry into database
        queryThree = "INSERT INTO Shelf_Product VALUES (?, ?, ?)"
        paramsTwo = [shelf_product_info[0], shelf_product_info[2], quantity]
        self.access_db(queryThree, paramsTwo)

        return 0

    def receive_order(self, order_info):
        """This function will manage the inventory when a sale is made.
        When a sale is made, the quantity in the warehouse will reduce to simulate the
        automatic movement of product from the warehouse to the shelf after every transaction.
        A dictionary containing ProductID:quantity as the key/value pair will be passed to the function"""

        # Loop through the dictionary and subtract the quantity from each product in the warehouse
        for key, item in order_info.items():
            # First, query the product get the stock quantity prior to the sale.
            param = key

            # Update the quantity by adding the received quantity to the existing quantity
            query = (f"UPDATE Shelf_Product SET Quantity = Quantity + {item} "
                     f"WHERE ProductID = ? and ShelfID LIKE 'WH%'")
            self.access_db(query, param)

            # Update the total amount of the product that is in stock by adding the received quantity to the total
            queryTwo = (f"UPDATE Product SET Total_In_Stock = Total_In_Stock + {item} "
                        f"WHERE ProductID = ?")
            self.access_db(queryTwo, param)

        return 0

    def stock_product(self, stock_info):
        """This function adds more items to the inventory of a particular product"""
        if not self.check_product_exists(stock_info[0]):
            return 1

        quantity = stock_info[1]

        # Remove from warehouse shelf
        query = (f"UPDATE Shelf_Product SET Quantity = Quantity - {quantity} "
                 f"WHERE ProductID = ? and ShelfID LIKE 'WH%'")
        param = (stock_info[1],)
        self.access_db(query, param)

        # Add to sales floor shelf
        query = (f"UPDATE Shelf_Product SET Quantity = Quantity + {quantity} "
                 f"WHERE ProductID = ? and ShelfID LIKE 'SF%'")
        param = (stock_info[1],)
        self.access_db(query, param)

        return 0

    def report_waste(self, waste_info):
        """ Produces a waste report and updates inventory and product information """
        report_number = waste_info[0]
        shelf_id = waste_info[1]
        product_id = waste_info[2]
        quantity = waste_info[3]
        reason_code = waste_info[4]
        date = waste_info[5]
        description = waste_info[6]
        employee_id = waste_info[7]

        if not self.check_product_exists(product_id):
            return 1

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Ensure employee exists
        queryOne = "SELECT COUNT(*) FROM Users WHERE EmployeeID = ?"
        param = (employee_id,)
        c.execute(queryOne, param)
        employee_exists = c.fetchone()
        conn.close()

        if employee_exists == 0:
            return 2

        # Create waste report
        queryTwo = "INSERT INTO Waste_Reports VALUES (?,?,?,?,?,?,?)"
        paramTwo = (report_number, product_id, quantity, reason_code, date, description, employee_id)
        self.access_db(queryTwo, paramTwo)

        # Update inventory information
        queryThree = (f"UPDATE Shelf_Product SET Quantity = Quantity - {quantity} "
                 f"WHERE ProductID = ? AND ShelfID = ?")
        paramThree = (product_id, shelf_id)
        self.access_db(queryThree, paramThree)

        # Update product information
        queryThree = (f"UPDATE Product SET Total_In_Stock = Total_In_Stock - {quantity} "
                      f"WHERE ProductID = ?")
        paramThree = (product_id, shelf_id)
        self.access_db(queryThree, paramThree)

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

    def search_shelf_product(self, field, param):
        """ Provides a list of products along with their quantity and shelf locations filtered by search criteria. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = f"SELECT * FROM Shelf_Product WHERE {field} LIKE '{param}%' ORDER BY ShelfID;"

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
                "ProductID": row[1],
                "Quantity": row[2],
                "ShelfID": row[0]
            }
            shelf_products.append(shelf_product)

        return shelf_products

    def check_shelf_exists(self, shelf):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        query = "SELECT COUNT(*) FROM Shelf WHERE ShelfID = ?"
        param = shelf[0]
        c.execute(query, param)
        shelf_exists = c.fetchone()
        conn.close()
        if shelf_exists == 0:
            return False
        return True

    def check_product_exists(self, product):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        query = "SELECT COUNT(*) FROM Product WHERE ProductID = ?"
        param = product[0]
        c.execute(query, param)
        product_exists = c.fetchone()
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
