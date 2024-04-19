import sqlite3
from product_cache import ProductCache


class ProductManagement:
    # The UserManagement constructor
    def __init__(self, db_name):
        self.db_name = db_name

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
        if product_information[2].isnumeric() is False:
            return 5

        script = [(
            f"INSERT INTO Product VALUES ("
            f"{product_information[0]},"
            f"'{product_information[1]}',"
            f"{product_information[2]},"
            f"0"
            ");"
        )]
        self.access_db(script)
        return 0

    def delete_product(self, product_id):
        """ Deletes a selected Product object from the database. """
        product_exists = self.check_if_exists("ProductID", product_id)

        if product_exists == 0:
            return 1

        script = [f'DELETE FROM Product WHERE ProductID = {product_id};']
        self.access_db(script)
        return 0

    def get_product_data(self, product_id):
        """ Provides a selected Product's information from the database. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = f"SELECT * FROM Product WHERE ProductID = {product_id};"

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

        if (product_name_exists != 0) or (product_name_exists != 1):
            return 2

        if len(product_information[1]) > 50:
            return 4
        if product_information[2].isnumeric() is False:
            return 5

        script = [(f"UPDATE Product SET Product_Name = '{product_information[1]}', "
                   f"Price = {product_information[2]}, "
                   f"Total_In_Stock = {product_information[3]} "
                   f"WHERE ProductID = {product_information[0]};")]
        self.access_db(script)

    def list_products(self):
        """ Provides a list of all Users and associated data. """
        product_data = ProductCache.get_product_data(self.db_name)

        # Convert the fetched rows to a list of dictionaries
        products = []
        for row in product_data:
            product = {
                "ProductID": row[0],
                "Product_Name": row[1],
                "Price": row[2],
                "Total_In_Stock": row[3]
            }
            products.append(product)

        return products

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

        for item in script:
            # Query to select all columns from the Product table, sorted by ProductID
            query = item

            # Execute the query
            cursor.execute(query)

        conn.commit()

        # Close the connection
        conn.close()

