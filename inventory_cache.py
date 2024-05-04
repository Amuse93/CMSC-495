import time
from threading import Lock

from database_portal import DatabasePortal


class InventoryCache:
    def __init__(self):
        """InventoryCache

        Description:
        Creates lists of shelves and shelf/product records from the database. It helps to prevent multiple calls to
        the database requesting information. The lists update every 5 minutes or when a change is made to the database
        that involves this information."""
        self.cache_expiry = 3000  # Cache expiry time in seconds (5 min)
        self.last_cache_update_time = None
        self.cached_shelf_data = None
        self.cached_inventory_data = None
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
        with self.lock:
            self.cached_inventory_data = self.fetch_sorted_inventory()
            self.cached_shelf_data = self.fetch_sorted_shelves()
            self.last_cache_update_time = time.time()

    def get_shelf_data(self):
        """get_shelf_data()

        Description:
        Provides the shelf data list from the cache storage

        Output:
        array[dictionary]: cached_shelf_data"""
        current_time = time.time()
        if self.last_cache_update_time is None or current_time - self.last_cache_update_time > self.cache_expiry:
            with self.lock:
                if ((self.last_cache_update_time is None)
                        or (current_time - self.last_cache_update_time > self.cache_expiry)):
                    self.cached_inventory_data = self.fetch_sorted_inventory()
                    self.cached_shelf_data = self.fetch_sorted_shelves()
                    self.last_cache_update_time = current_time
        return self.cached_shelf_data

    def fetch_sorted_shelves(self):
        """fetch_sorted_shelves()

        Description:
        Retrieves the sorted shelf data from the database and
        provides it as an array of shelf information dictionaries.

        Output:
        array/dictionaries[]{}:  shelves"""
        query = "SELECT * FROM Shelf ORDER BY ShelfID"
        rows = self.db_portal.pull_data(query)
        shelves = [{"ShelfID": row[0]} for row in rows]
        return shelves

    def get_inventory_data(self):
        """get_inventory_data()

        Description:
        Provides the shelf/product data list from the cache storage

        Output:
        array[dictionary]: cached_inventory_data"""
        current_time = time.time()
        if self.last_cache_update_time is None or current_time - self.last_cache_update_time > self.cache_expiry:
            with self.lock:
                if ((self.last_cache_update_time is None)
                        or (current_time - self.last_cache_update_time > self.cache_expiry)):
                    self.cached_inventory_data = self.fetch_sorted_inventory()
                    self.cached_shelf_data = self.fetch_sorted_shelves()
                    self.last_cache_update_time = current_time
        return self.cached_inventory_data

    def fetch_sorted_inventory(self):
        """fetch_sorted_shelves()

        Description:
        Retrieves the sorted shelf/product data from the database and
        provides it as an array of shelf/product information dictionaries.

        Output:
        array/dictionaries[]{}: inventory"""
        query = """
            SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID
            FROM Shelf_Product
            JOIN Product ON Shelf_Product.ProductID = Product.ProductID
            ORDER BY Shelf_Product.ShelfID
        """

        rows = self.db_portal.pull_data(query)
        inventory = [{"ProductID": row[0], "Product_Name": row[1], "Quantity": row[2],
                      "ShelfID": row[3]} for row in rows]
        return inventory
