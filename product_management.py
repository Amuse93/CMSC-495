import sqlite3
from product_cache import ProductCache


class ProductManagement:
    # The UserManagement constructor
    def __init__(self, db_name):
        self.db_name = db_name
        self.product_cache = ProductCache(db_name)

    def add_product(self, product_information):
        """ Adds a Product object into the database """
        product_exists = self.check_if_exists("ProductID", product_information[0])

        if product_exists != 0:
            return 1

        product_name_exists = self.check_if_exists("Product_Name", product_information[1])

        if product_name_exists != 0:
            return 2

        if len(product_information[0]) > 15:
            return 3

        if len(product_information[1]) > 50:
            return 4

        price_check = product_information[2].split(".")
        if price_check[0].isnumeric() is False or price_check[1].isnumeric() is False:
            return 5

        script = (
            f"INSERT INTO Product VALUES ("
            f"'{product_information[0]}', "
            f"'{product_information[1]}', "
            f"{product_information[2]}, "
            f"0"
            ");"
        )
        self.access_db(script)

        self.product_cache.update_cache()

        return 0

    def delete_product(self, product_id):
        """ Deletes a selected Product object from the database. """
        product_exists = self.check_if_exists("ProductID", product_id)

        if product_exists == 0:
            return 1

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        query = f"SELECT COUNT(*) FROM Shelf_Product WHERE ProductID = '{product_id}';"
        c.execute(query)  # Assuming shelf is a tuple or list with at least one element
        product_record_exists = c.fetchone()[0]
        conn.close()

        if product_record_exists != 0:
            return 2

        script = f"DELETE FROM Product WHERE ProductID = '{product_id}';"
        self.access_db(script)

        self.product_cache.update_cache()

        return 0

    def get_product_data(self, product_id):
        """ Provides a selected Product's information from the database. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = f"SELECT * FROM Product WHERE ProductID = '{product_id}';"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()
        product_info = {}

        for row in rows:
            product_info = {
                "ProductID": row[0],
                "Product_Name": row[1],
                "Price": row[2],
                "Total_In_Stock": row[3]
            }

        return product_info

    def modify_product(self, product_information):
        """ Updates a selected Product's information in the database. """
        product_name_exists = self.check_if_exists("Product_Name", product_information[1])

        if (product_name_exists != 0) and (product_name_exists != 1):
            return 2

        if len(product_information[1]) > 50:
            return 4

        price_check = product_information[2].split(".")
        if price_check[0].isnumeric() is False or price_check[1].isnumeric() is False:
            return 5

        script = (f"UPDATE Product SET Product_Name = '{product_information[1]}', "
                   f"Price = {product_information[2]}, "
                   f"Total_In_Stock = 0 "
                   f"WHERE ProductID = '{product_information[0]}';")
        self.access_db(script)

        self.product_cache.update_cache()

        return 0

    def list_products(self):
        """ Provides a list of all Users and associated data. """
        product_data = self.product_cache.get_product_data()

        return product_data

    def search_products(self, field, param):
        """ Provides a list of all Users and associated data filtered by search criteria. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = (f"SELECT ProductID, Product_Name, Price, Total_In_Stock "
                 f"FROM Product WHERE {field} LIKE '{param}%' ORDER BY ProductID;")

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        products = []
        for row in rows:
            product = {
                "ProductID": row[0],
                "Product_Name": row[1],
                "Price": row[2],
                "Total_In_Stock": row[3]
            }
            products.append(product)

        return products

    def check_if_exists(self, field, param):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = f"SELECT COUNT(*) FROM Product WHERE {field} = ?"

        # Check if the username exists
        cursor.execute(query, (param,))
        product_exists = cursor.fetchone()[0]

        # Close the connection
        conn.close()

        return product_exists

    def access_db(self, script):
        """ Allows scripts to be executed for updating the database """
        # Connect to the database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(script)

        conn.commit()

        # Close the connection
        conn.close()

