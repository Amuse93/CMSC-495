from database_portal import DatabasePortal
from product_cache import ProductCache


class ProductManagement:
    # The UserManagement constructor
    def __init__(self):
        self.db_portal = DatabasePortal()
        self.product_cache = ProductCache()

    def add_product(self, product_information):
        """add_product

        Description:
        Adds a Product object into the database

        Parameters:
        array: product_information

        Output:
        int: error code
        """
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

        script = f"INSERT INTO Product VALUES (?, ?, ?, ?);"
        param = (product_information[0], product_information[1], product_information[2], 0)
        self.db_portal.push_data(script, param)

        self.product_cache.update_cache()

        return 0

    def delete_product(self, product_id):
        """delete_product

        Description:
        Deletes a selected Product object from the database.

        Parameters:
        string: product_id

        Output:
        int: error code
        """
        param = (product_id,)
        product_exists = self.check_if_exists("ProductID", product_id)

        if product_exists == 0:
            return 1

        query = f"SELECT COUNT(*) FROM Shelf_Product WHERE ProductID = ?;"
        product_record_exists = self.db_portal.pull_data(query, param)[0][0]

        if product_record_exists != 0:
            return 2

        script = f"DELETE FROM Product WHERE ProductID = ?;"
        self.db_portal.push_data(script, param)
        self.product_cache.update_cache()
        return 0

    def get_product_data(self, product_id):
        """get_product_data

        Description:
        Provides a selected Product's information from the database.

        Parameters:
        string: product_id

        Output:
        dict: product_info
        """
        query = f"SELECT * FROM Product WHERE ProductID = ?;"
        param = (product_id,)
        rows = self.db_portal.pull_data(query, param)
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
        """modify_product

        Description:
        Updates a selected Product's information in the database.

        Parameters:
        array: product_information

        Output:
        int: error code
        """
        product_name_exists = self.check_if_exists("Product_Name", product_information[1])

        if (product_name_exists != 0) and (product_name_exists != 1):
            return 2

        if len(product_information[1]) > 50:
            return 4

        price_check = product_information[2].split(".")
        if price_check[0].isnumeric() is False or price_check[1].isnumeric() is False:
            return 5

        script = f"UPDATE Product SET Product_Name = ?, Price = ? WHERE ProductID = ?;"
        param = (product_information[1], product_information[2], product_information[0])
        self.db_portal.push_data(script, param)

        self.product_cache.update_cache()

        return 0

    def list_products(self):
        """list_products

        Description:
        Provides a list of all Users and associated data.

        Parameters:
        None

        Output:
        dict: product_data
        """
        product_data = self.product_cache.get_product_data()

        return product_data

    def search_products(self, field, param):
        """search_products

        Description:
        Provides a list of all Users and associated data filtered by search criteria.

        Parameters:
        string: field
        string: param

        Output:
        array: products
        """
        query = (f"SELECT ProductID, Product_Name, Price, Total_In_Stock "
                 f"FROM Product WHERE {field} LIKE ? ORDER BY ProductID;")
        param = (param + '%',)
        rows = self.db_portal.pull_data(query, param)

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
        """check_if_exists

        Description:
        Checks if the paramter exists in the associated field.

        Parameters:
        string: field
        string: param

        Output:
        boolean: user_exists
        """

        query = f"SELECT COUNT(*) FROM Product WHERE {field} = ?"
        product_exists = self.db_portal.pull_data(query, (param,))[0][0]
        return product_exists
