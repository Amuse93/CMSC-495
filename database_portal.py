import os
import sqlite3


class DatabasePortal:

    def __init__(self):
        self.db_name = 'alpha_store.sqlite3'
        self.sql_file = 'static/Create_tables.sql'

    # Check if there exists a database. If not, create one.
    def create_database(self):
        # Check if the database file exists
        if not os.path.exists(self.db_name):
            # If the database file doesn't exist, create a new one
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Read SQL commands from the SQL file and execute them
            with open(self.sql_file, 'r') as sql_script_file:
                sql_commands = sql_script_file.read()
                cursor.executescript(sql_commands)

            # Commit changes and close the connection
            conn.commit()
            conn.close()

    def push_data(self, script, args=None):
        """ Allows scripts to be executed for updating the database """

        # Connect to the database
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Execute the query with parameters if provided
        if args:
            cursor.execute(script, args)
        else:
            cursor.execute(script)

        conn.commit()

        # Close the connection
        conn.close()

    def pull_data(self, query, args=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Execute the query with parameters if provided
        if args:
            c.execute(query, args)
        else:
            c.execute(query)
        rows = c.fetchall()
        conn.close()

        return rows
