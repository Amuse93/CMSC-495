import time
import sqlite3


class InventoryCache:
    # The InventoryCache constructor
    def __init__(self, db_name):
        self.cache_expiry = 3000  # Cache expiry time in seconds (5 min)
        self.last_cache_update_time = None
        self.cached_shelf_data = None
        self.cached_inventory_data = None
        self.db_name = db_name

    # Returns the time last updated
    def get_last_cache_update_time(self):
        return self.last_cache_update_time

    # Returns the shelf data
    def get_shelf_data(self):
        if self.last_cache_update_time is None or time.time() - self.last_cache_update_time > self.cache_expiry:
            # Fetch shelf data from the database
            self.cached_shelf_data = self.fetch_sorted_shelves()
            self.last_cache_update_time = time.time()

        return self.cached_shelf_data

    # Pulls the shelf data from the database sorted by ShelfID
    def fetch_sorted_shelves(self):
        # Connect to the database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = "SELECT * FROM Shelf ORDER BY ShelfID"

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

    # Returns the inventory data sorted by ShelfID
    def get_inventory_data(self):
        if self.last_cache_update_time is None or time.time() - self.last_cache_update_time > self.cache_expiry:
            # Fetch shelf data from the database
            self.cached_inventory_data = self.fetch_sorted_inventory()
            self.last_cache_update_time = time.time()

        return self.cached_inventory_data

    def fetch_sorted_inventory(self):
        # Connect to the database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = "SELECT * FROM Shelf_Product ORDER BY ShelfID"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        inventory = []
        for row in rows:
            record = {
                "ProductID": row[1],
                "Quantity": row[2],
                "ShelfID": row[0]
            }
            inventory.append(record)

        return inventory
