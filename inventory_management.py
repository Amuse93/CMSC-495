from datetime import datetime
from database_portal import DatabasePortal
from inventory_cache import InventoryCache


def get_report_number():
    now = datetime.now()
    formatted_datetime = now.strftime('%Y%m%d%H%M%S')
    nanoseconds = now.strftime('%f')
    nanoseconds = int(nanoseconds) * 1000

    result = 'WR-' + formatted_datetime + f"{nanoseconds:09d}"
    return result


class InventoryManagement:

    def __init__(self):
        self.inventory_cache = InventoryCache()
        self.db_portal = DatabasePortal()

    def add_shelf(self, shelf_info):
        """add_shelf

        Description:
        Adds a new shelf to the inventory

        Parameters:
        array: shelf_info

        Output:
        int: error_code
        """

        shelf_exists = self.check_if_exists('Shelf', 'ShelfID', shelf_info[0])

        # Check if the shelf already exists
        if shelf_exists != 0:
            return 1

        # Check if new shelf ID is greater than 15 characters
        if len(shelf_info[0]) != 7:
            return 3

        if shelf_info[0][:2] != 'WH' and shelf_info[0][:2] != 'SF':
            return 4

        # Insert new shelf into Shelf table
        script = "INSERT INTO Shelf (ShelfID) VALUES (?)"
        self.db_portal.push_data(script, shelf_info)

        self.inventory_cache.update_cache()

        return 0

    def delete_shelf(self, shelf_id):
        """This function will delete a shelf from the inventory"""

        shelf_exists = self.check_if_exists('Shelf', 'ShelfID', shelf_id)

        # Check if the shelf exists. If it does not, it can't be deleted
        if shelf_exists == 0:
            return 1

        # Get the number of products associated with the shelf.
        query = f"SELECT COUNT(*) FROM Shelf_Product WHERE ShelfID = ?;"
        param = (shelf_id,)
        number_of_items = self.db_portal.pull_data(query, param)[0][0]

        # Ensure there are no products associated with the shelf.
        if number_of_items != 0:
            return 2

        # Delete the selected shelf from inventory
        script = f"DELETE FROM Shelf WHERE ShelfID = '{shelf_id}';"
        param = (shelf_id,)
        self.db_portal.push_data(script, param)

        self.inventory_cache.update_cache()

        return 0

    def add_product_to_shelf(self, shelf_product_info):

        """This function will add a new product to a shelf"""
        shelf_id = shelf_product_info[0]
        product_id = shelf_product_info[1]

        if not self.check_if_exists('Shelf', 'ShelfID', shelf_id):
            return 1

        if not self.check_if_exists('Product', 'ProductID', product_id):
            return 2

        if shelf_id[:2] == 'WH':
            query = f"SELECT COUNT(*) FROM Shelf_Product WHERE ProductID = ? AND ShelfID LIKE 'WH%';"
            param = (product_id,)
            product_record_exists = self.db_portal.pull_data(query, param)

            if product_record_exists != 0:
                return 3

        if shelf_id[:2] == 'SF':
            query = f"SELECT COUNT(*) FROM Shelf_Product WHERE ProductID = ? AND ShelfID LIKE 'SF%';"
            param = (product_id,)
            product_record_exists = self.db_portal.pull_data(query, param)

            if product_record_exists != 0:
                return 4

        script = "INSERT INTO Shelf_Product VALUES (?,?,?)"
        param = [shelf_id, product_id, 0]
        self.db_portal.push_data(script, param)

        self.inventory_cache.update_cache()

        return 0

    def delete_product_from_shelf(self, product_id, shelf_id):
        """This function will add a new product to a shelf"""
        param = (product_id, shelf_id)

        query = f"SELECT Quantity FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?;"
        quantity = self.db_portal.pull_data(query, param)[0][0]

        if quantity != 0:
            return 1

        # Delete the entry in the database
        script = f"DELETE FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?;"
        self.db_portal.push_data(script, param)

        self.inventory_cache.update_cache()

        return 0

    def move_product(self, shelf_product_info):
        """This function moves a product from one shelf to another"""
        product_id = shelf_product_info[0]
        from_shelf = shelf_product_info[1]
        to_shelf = shelf_product_info[2]

        # Ensure product exists
        if not self.check_if_exists('Product', 'ProductID', product_id):
            return 1

        # Ensure source shelf exists
        if not self.check_if_exists('Shelf', 'ShelfID', from_shelf):
            return 2

        # Ensure destination shelf exists
        if not self.check_if_exists('Shelf', 'ShelfID', to_shelf):
            return 3

        if from_shelf[:2] == 'WH' and to_shelf[:2] != "WH":
            return 4

        if from_shelf[:2] == 'SF' and to_shelf[:2] != "SF":
            return 5

        query = f"SELECT Quantity FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?;"
        param = (product_id, from_shelf)
        quantity = self.db_portal.pull_data(query, param)[0][0]

        # Delete the old entry in the database
        script = f"DELETE FROM Shelf_Product WHERE ProductID = ? AND ShelfID = ?;"
        param = (product_id, from_shelf)
        self.db_portal.push_data(script, param)

        # Add new entry into database
        script = f"INSERT INTO Shelf_Product VALUES (?, ?, ?);"
        param = (to_shelf, product_id, quantity)
        self.db_portal.push_data(script, param)

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
            script = "UPDATE Shelf_Product SET Quantity = Quantity + ? WHERE ProductID = ? AND ShelfID LIKE 'WH%';"
            param = (quantity, product_id)
            self.db_portal.push_data(script, param)

            # Update the total amount of the product that is in stock by adding the received quantity to the total
            script = "UPDATE Product SET Total_In_Stock = Total_In_Stock + ? WHERE ProductID = ?;"
            param = (quantity, product_id)
            self.db_portal.push_data(script, param)

        self.inventory_cache.update_cache()

        return 0

    def stock_product(self, stock_info):
        """This function adds more items to the inventory of a particular product"""
        product_id = stock_info[0]
        quantity = stock_info[1]

        if not self.check_if_exists('Product', 'ProductID', product_id):
            return 1

        # Remove from warehouse shelf
        script = "UPDATE Shelf_Product SET Quantity = Quantity - ? WHERE ProductID = ? and ShelfID LIKE 'WH%';"
        param = (quantity, product_id)
        self.db_portal.push_data(script, param)

        # Add to sales floor shelf
        script = "UPDATE Shelf_Product SET Quantity = Quantity + ? WHERE ProductID = ? and ShelfID LIKE 'SF%';"
        param = (quantity, product_id)
        self.db_portal.push_data(script, param)

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

        # Ensure employee exists
        query = f"SELECT Price FROM Product WHERE ProductID = ?;"
        param = (product_id,)
        unit_price = self.db_portal.pull_data(query, param)[0][0]

        if not self.check_if_exists('Product', 'ProductID', product_id):
            return 1

        # Ensure employee exists
        employee_exists = self.check_if_exists('Users', 'EmployeeID', employee_id)

        if employee_exists == 0:
            return 2

        # Create waste report
        script = "INSERT INTO Waste_Reports VALUES (?,?,?,?,?,?,?,?);"
        param = (report_number, product_id, quantity, unit_price, reason_code, date, description, employee_id)
        self.db_portal.push_data(script, param)

        # Update inventory information
        script = "UPDATE Shelf_Product SET Quantity = Quantity - ? WHERE ProductID = ? AND ShelfID = ?;"
        param = (quantity, product_id, shelf_id)
        self.db_portal.push_data(script, param)

        # Update product information
        script = "UPDATE Product SET Total_In_Stock = Total_In_Stock - ? WHERE ProductID = ?;"
        param = (quantity, product_id, shelf_id)
        self.db_portal.push_data(script, param)

        self.inventory_cache.update_cache()

        return 0

    def list_shelves(self):
        """ Provides a list of available shelving units """
        # Pull shelf list from inventory cache
        shelves = self.inventory_cache.get_shelf_data()
        return shelves

    def search_shelves(self, param):
        """ Provides a list of shelves filtered by search criteria. """
        # Query to select all columns from the Product table, sorted by ProductID
        query = "SELECT * FROM Shelf WHERE ShelfID LIKE ? ORDER BY ShelfID;"
        param = (param + '%',)
        rows = self.db_portal.pull_data(query, param)

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

        # Query to select ProductID, Product_Name, Quantity, and ShelfID from Shelf_Product table
        # Joined with Product table to get the Product_Name
        if field == 'Product_Name':
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Product.{field} LIKE ? "
                f"ORDER BY Shelf_Product.ShelfID;")
        else:
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Shelf_Product.{field} LIKE ? "
                f"ORDER BY Shelf_Product.ShelfID;")
        param = (param + '%',)
        rows = self.db_portal.pull_data(query, param)

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
        # Query to select ProductID, Product_Name, Quantity, and ShelfID from Shelf_Product table
        # Joined with Product table to get the Product_Name
        if field == 'Product_Name':
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Product.{field} LIKE ? "
                f"AND Shelf_Product.ShelfID = ? "
                f"ORDER BY Shelf_Product.ShelfID;")
        else:
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"WHERE Shelf_Product.{field} LIKE ? "
                f"AND Shelf_Product.ShelfID = ? "
                f"ORDER BY Shelf_Product.ShelfID;")
        param = (param + '%', shelf_id)
        rows = self.db_portal.pull_data(query, param)

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
        # Query to select ProductID, Product_Name, Quantity, and ShelfID from Shelf_Product table
        # Joined with Product table to get the Product_Name
        query = (
            f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
            f"FROM Shelf_Product "
            f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
            f"WHERE Shelf_Product.ProductID = ?;")
        param = (product_id,)
        rows = self.db_portal.pull_data(query, param)

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

    def check_if_exists(self, table, field, param):
        query = f"SELECT COUNT(*) FROM {table} WHERE {field} = ?;"
        param = (param,)
        shelf_exists = self.db_portal.pull_data(query, param)
        if shelf_exists == 0:
            return False
        return True
