import secrets
import sqlite3
import string
from passlib.handlers.sha2_crypt import sha256_crypt


def generate_random_password():
    """ Generates a password with the specified attributes """
    alphabet = ""
    alphabet += string.ascii_lowercase
    alphabet += string.ascii_uppercase
    alphabet += string.digits
    alphabet += string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(8))
        bad_symbols = ["/", "\\", "[", "]", "{", "}", "<", ">", "", "'", "\"", "`"]
        if any(c in bad_symbols for c in password):
            continue
        break
    return password


class UserManagement:
    # The UserManagement constructor
    def __init__(self, db_name):
        self.db_name = db_name

    def add_user(self, user_information):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Check if the username exists
        cursor.execute("SELECT COUNT(*) FROM Users WHERE EmployeeID = ?", (user_information[0],))
        user_exists = cursor.fetchone()[0]

        if user_exists == 0:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (user_information[1],))
            user_exists = cursor.fetchone()[0]

            if user_exists == 0:
                password = generate_random_password()
                hashed_password = sha256_crypt.hash(password)
                script = [(
                    "INSERT INTO Users VALUES ("
                    f"{user_information[0]},"
                    f"'{user_information[1]}',"
                    f"'{hashed_password}',"
                    f"'{user_information[2]}',"
                    f"'{user_information[3]}',"
                    f"'{user_information[4]}',"
                    f"'{user_information[5]}',"
                    f"'{user_information[6]}',"
                    "1,"
                    "0"
                    ");"
                )]
                self.access_db(script)
                return password
            else:
                return 2
        else:
            return 1

    def delete_user(self, employee_id):
        script = [(f'DELETE FROM Users WHERE EmployeeID = {employee_id};')]
        self.access_db(script)
        return 0

    def get_user_data(self, employee_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = (f"SELECT EmployeeID, Username, First_Name, Last_Name, Phone_Number, Position "
                 f"FROM Users WHERE EmployeeID = {employee_id};")

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        user_info = {}

        for row in rows:
            user_info = {
                "EmployeeID": row[0],
                "Username": row[1],
                "First_Name": row[2],
                "Last_Name": row[3],
                "Phone_Number": row[4],
                "Position": row[5]
            }

        return user_info

    def modify_user(self, user_information):

        script = [(f"UPDATE Users SET Username = '{user_information[1]}', "
                   f"First_Name = '{user_information[2]}', "
                   f"Last_Name = '{user_information[3]}', "
                   f"Phone_Number = '{user_information[4]}', "
                   f"Position = '{user_information[5]}' "
                   f"WHERE EmployeeID = {user_information[0]};")]
        self.access_db(script)

    def reset_user_password(self, employee_id):
        password = generate_random_password()
        hashed_password = hashed_password = sha256_crypt.hash(password)
        script = [(f"UPDATE Users SET Password = '{hashed_password}' WHERE EmployeeID = {employee_id};"),
                  (f"UPDATE Users SET First_Time = 1 WHERE EmployeeID = {employee_id};"),
                  (f"UPDATE Users SET Number_Of_Tries = 0 WHERE EmployeeID = {employee_id};")]
        self.access_db(script)
        return password

    def list_users(self, field):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = (f"SELECT EmployeeID, Username, First_Name, Last_Name, DOB, Phone_Number, Position "
                 f"FROM Users ORDER BY {field};")

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        users = []
        for row in rows:
            user = {
                "EmployeeID": row[0],
                "Username": row[1],
                "First_Name": row[2],
                "Last_Name": row[3],
                "DOB": row[4],
                "Phone_Number": row[5],
                "Position": row[6]
            }
            users.append(user)

        return users

    def search_users(self, field, param):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = (f"SELECT EmployeeID, Username, First_Name, Last_Name, DOB, Phone_Number, Position "
                 f"FROM Users WHERE {field} LIKE '{param}%' ORDER BY EmployeeID;")

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert the fetched rows to a list of dictionaries
        users = []
        for row in rows:
            user = {
                "EmployeeID": row[0],
                "Username": row[1],
                "First_Name": row[2],
                "Last_Name": row[3],
                "DOB": row[4],
                "Phone_Number": row[5],
                "Position": row[6]
            }
            users.append(user)

        return users

    def access_db(self, script):
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