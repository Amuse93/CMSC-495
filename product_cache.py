import time
from threading import Lock
from database_portal import DatabasePortal


class ProductCache:
    def __init__(self):
        """ProductCache

        Description:
        Creates a list of products from the database. It helps to prevent multiple calls to the database
        requesting information. The list update every 5 minutes or when a change is made to the database
        that involves this information."""
        self.cache_expiry = 3000  # Cache expiry time in seconds (5 min)
        self.last_cache_update_time = None  # Initialize to None
        self.cached_product_data = None
        self.db_portal = DatabasePortal()
        self.lock = Lock()  # Lock for thread safety

    def get_last_cache_update_time(self):
        """get_last_cache_update_time()

        Description:
        Provides the time in which the cache was last updated. Used to determine when the cache need to be updated.

        Output:
        time: last_cache_update_time"""
        return self.last_cache_update_time

    def update_cache(self):
        """update_cache()

        Description:
        Manually updates the cache with the latest data from the database.
        """
        current_time = time.time()
        with self.lock:
            self.cached_product_data = self.fetch_sorted_products()
            self.last_cache_update_time = current_time

    def get_product_data(self):
        """get_product_data()

        Description:
        Provides the product data list from the cache storage

        Output:
        array[dictionary]: cached_product_data"""
        current_time = time.time()
        if self.last_cache_update_time is None or current_time - self.last_cache_update_time > self.cache_expiry:
            with (self.lock):
                # Double check in case another thread updated the cache
                if ((self.last_cache_update_time is None)
                        or (current_time - self.last_cache_update_time > self.cache_expiry)):
                    self.cached_product_data = self.fetch_sorted_products()
                    self.last_cache_update_time = current_time
        return self.cached_product_data

    def fetch_sorted_products(self):
        """fetch_sorted_products()

        Description:
        Retrieves the sorted product data from the database and
        provides it as an array of shelf information dictionaries.

        Output:
        array[dictionary]: products"""
        query = "SELECT * FROM Product ORDER BY ProductID"
        products = []
        rows = self.db_portal.pull_data(query)
        for row in rows:
            product = {
                "ProductID": row[0],
                "Product_Name": row[1],
                "Price": row[2],
                "Total_In_Stock": row[3]
            }
            products.append(product)

        return products
