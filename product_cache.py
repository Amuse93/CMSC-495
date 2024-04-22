import sqlite3
import time
from threading import Lock


class ProductCache:
    def __init__(self, db_name):
        self.cache_expiry = 3000  # Cache expiry time in seconds (5 min)
        self.last_cache_update_time = None  # Initialize to None
        self.cached_product_data = None
        self.db_name = db_name
        self.lock = Lock()  # Lock for thread safety

    def update_cache(self):
        """
        Manually updates the cache with the latest product data from the database.
        """
        current_time = time.time()
        with self.lock:
            self.cached_product_data = self.fetch_sorted_products()
            self.last_cache_update_time = current_time

    def get_product_data(self):
        current_time = time.time()
        if self.last_cache_update_time is None or current_time - self.last_cache_update_time > self.cache_expiry:
            with (self.lock):
                # Double check in case another thread updated the cache
                if ((self.last_cache_update_time is None)
                        or (current_time - self.last_cache_update_time > self.cache_expiry)):
                    self.cached_product_data = self.fetch_sorted_products()
                    self.last_cache_update_time = current_time
        return self.cached_product_data

    def get_last_cache_update_time(self):
        return self.last_cache_update_time

    def fetch_sorted_products(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM Product ORDER BY ProductID"
                cursor.execute(query)
                rows = cursor.fetchall()

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
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return []
