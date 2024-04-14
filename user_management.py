import secrets
import sqlite3
import string
from passlib.handlers.sha2_crypt import sha256_crypt


def generate_random_password():
    """ Generates a random password with at least one lowercase letter, one uppercase letter, one digit,
    and one punctuation character. The default length of the password is 8 characters. """
    alphabet = ""
    alphabet += string.ascii_lowercase
    alphabet += string.ascii_uppercase
    alphabet += string.digits
    alphabet += string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(8))
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
        """ Adds a User object into the database """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        print(user_information[6])

        if user_information[0].isnumeric() is False:
            return 3
        if len(user_information[1]) > 60:
            return 4
        if len(user_information[2]) > 60:
            return 5
        if len(user_information[3]) > 60:
            return 6
        if (user_information[5].isnumeric() is False) or (len(user_information[5]) != 10):
            return 7
        if user_information[6] is None:
            return 8

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
        """ Deletes a selected User object from the database. """
        script = [f'DELETE FROM Users WHERE EmployeeID = {employee_id};']
        self.access_db(script)
        return 0

    def get_user_data(self, employee_id):
        """ Provides a selected User's information from the database. """
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
        """ Updates a selected User's information in the database. """

        if len(user_information[1]) > 60:
            return 4
        if len(user_information[2]) > 60:
            return 5
        if len(user_information[3]) > 60:
            return 6
        if (user_information[4].isnumeric() is False) or (len(user_information[4]) != 10):
            return 7
        if user_information[5] == '-- Make Selection --':
            return 8

        script = [(f"UPDATE Users SET Username = '{user_information[1]}', "
                   f"First_Name = '{user_information[2]}', "
                   f"Last_Name = '{user_information[3]}', "
                   f"Phone_Number = '{user_information[4]}', "
                   f"Position = '{user_information[5]}' "
                   f"WHERE EmployeeID = {user_information[0]};")]
        self.access_db(script)

    def reset_user_password(self, employee_id):
        """ Replaces a selected User's password with a generated one and resets the 'FirstTime' tick and the
         'Number of Tries' """
        password = generate_random_password()
        hashed_password = sha256_crypt.hash(password)
        script = [(f"UPDATE Users SET Password = '{hashed_password}', "
                   f"First_Time = 1, "
                   f"Number_Of_Tries = 0 "
                   f"WHERE EmployeeID = {employee_id};")]
        self.access_db(script)
        return password

    def list_users(self):
        """ Provides a list of all Users and associated data. """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Query to select all columns from the Product table, sorted by ProductID
        query = (f"SELECT EmployeeID, Username, First_Name, Last_Name, DOB, Phone_Number, Position "
                 f"FROM Users ORDER BY EmployeeID;")

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
        """ Provides a list of all Users and associated data filtered by search criteria. """
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
