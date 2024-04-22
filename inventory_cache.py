import sqlite3
import time
from threading import Lock


class InventoryCache:
    def __init__(self, db_name):
        self.cache_expiry = 3000  # Cache expiry time in seconds (5 min)
        self.last_cache_update_time = None
        self.cached_shelf_data = None
        self.cached_inventory_data = None
        self.db_name = db_name
        self.lock = Lock()  # Lock for thread safety

    def get_last_cache_update_time(self):
        return self.last_cache_update_time

    def update_cache(self):
        """
        Manually updates the cache with the latest data from the database.
        """
        with self.lock:
            self.cached_inventory_data = self.fetch_sorted_inventory()
            self.cached_shelf_data = self.fetch_sorted_shelves()
            self.last_cache_update_time = time.time()

    def get_shelf_data(self):
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
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM Shelf ORDER BY ShelfID"
                cursor.execute(query)
                rows = cursor.fetchall()

            shelves = [{"ShelfID": row[0]} for row in rows]
            return shelves
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return []

    def get_inventory_data(self):
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
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = """
                    SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID
                    FROM Shelf_Product
                    JOIN Product ON Shelf_Product.ProductID = Product.ProductID
                    ORDER BY Shelf_Product.ShelfID
                """
                cursor.execute(query)
                rows = cursor.fetchall()

            inventory = [{"ProductID": row[0], "Product_Name": row[1], "Quantity": row[2], "ShelfID": row[3]} for row in rows]
            return inventory
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return []