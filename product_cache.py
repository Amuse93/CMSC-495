import time
import sqlite3


class ProductCache:
    # The ProductCache constructor
    def __init__(self, db_name):
        self.cache_expiry = 3000  # Cache expiry time in seconds (5 min)
        self.last_cache_update_time = None
        self.cached_product_data = None
        self.db_name = db_name

    # Returns the product data
    def get_product_data(self):
        if self.last_cache_update_time is None or time.time() - self.last_cache_update_time > self.cache_expiry:
            # Fetch product data from the database
            self.cached_product_data = self.fetch_sorted_products()
            self.last_cache_update_time = time.time()

        return self.cached_product_data

    # Returns the time last updated
    def get_last_cache_update_time(self):
        return self.last_cache_update_time

    # Pulls the products sorted by ProductID
    def fetch_sorted_products(self):
        # Connect to the database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = "SELECT * FROM Product ORDER BY ProductID"

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
