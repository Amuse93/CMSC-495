import secrets
import string
from passlib.handlers.sha2_crypt import sha256_crypt
from database_portal import DatabasePortal


def generate_random_password():
    """generate_random_password

    Description:
    Generates a random password with at least one lowercase letter, one uppercase letter, one digit,
    and one punctuation character. The default length of the password is 8 characters.

    Parameters:
    None

    Output:
    string: A secure password
    """
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
    def __init__(self):
        self.db_portal = DatabasePortal()

    def add_user(self, user_information):
        """add_user

        Description:
        Adds a User object into the database

        Parameters:
        array: user_information

        Output:
        int: error code
        string: password
        """
        user_exists = self.check_if_exists("EmployeeID", user_information[0])

        if user_exists != 0:
            return 1

        username_exists = self.check_if_exists("Username", user_information[1])

        if username_exists != 0:
            return 2

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

        password = generate_random_password()
        hashed_password = sha256_crypt.hash(password)

        script = "INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        param = (user_information[0], user_information[1], hashed_password,
                 user_information[2], user_information[3], user_information[4],
                 user_information[5], user_information[6], 1, 0)
        self.db_portal.push_data(script, param)
        return password

    def delete_user(self, employee_id):
        """delete_user

        Description:
        Deletes a selected User object from the database.

        Parameters:
        string: employee_id

        Output:
        int: error code
        """
        script = "DELETE FROM Users WHERE EmployeeID = ?;"
        param = (employee_id,)
        self.db_portal.push_data(script, param)
        return 0

    def get_user_data(self, employee_id):
        """get_user_data

        Description:
        Provides a selected User's information from the database.

        Parameters:
        string: employee_id

        Output:
        dictionary: user_information
        """
        # Query to select all columns from the Product table, sorted by ProductID
        query = (f"SELECT EmployeeID, Username, First_Name, Last_Name, Phone_Number, Position "
                 f"FROM Users WHERE EmployeeID = ?;")
        param = (employee_id,)
        rows = self.db_portal.pull_data(query, param)

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
        """modify_user

        Description:
        Updates a selected User's information in the database.

        Parameters:
        array: user_information

        Output:
        int: error code
        """
        username_exists = self.check_if_exists("Username", user_information[1])

        if (username_exists != 0) and (username_exists != 1):
            return 2

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

        script = ("UPDATE Users SET Username = ?, First_Name = ?, Last_Name = ?, "
                  "Phone_Number = ?, Position = ? WHERE EmployeeID = ?;")
        param = (user_information[1], user_information[2], user_information[3],
                 user_information[4], user_information[5], user_information[0])
        self.db_portal.push_data(script, param)
        return 0

    def reset_user_password(self, employee_id):
        """reset_user_password

        Description:
        Replaces a selected User's password with a generated one and resets the 'FirstTime' tick and the
         'Number of Tries'

        Parameters:
        string: employee_id

        Output:
        string: password
         """
        password = generate_random_password()
        hashed_password = sha256_crypt.hash(password)
        script = "UPDATE Users SET Password = ?, First_Time = 1, Number_Of_Tries = 0 WHERE EmployeeID = ?;"
        param = (hashed_password, employee_id)
        self.db_portal.push_data(script, param)
        return password

    def list_users(self):
        """list_users

        Description:
        Provides a list of all Users and associated data.

        Parameters:
        None

        Output:
        array: users
        """
        # Query to select all columns from the Product table, sorted by ProductID
        query = (f"SELECT EmployeeID, Username, First_Name, Last_Name, DOB, Phone_Number, Position "
                 f"FROM Users ORDER BY EmployeeID;")
        rows = self.db_portal.pull_data(query)

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
        """search_users

        Description:
        Provides a list of all Users and associated data filtered by search criteria.

        Parameters:
        string: field
        string: param

        Output:
        array: users
        """
        query = (f"SELECT EmployeeID, Username, First_Name, Last_Name, DOB, Phone_Number, Position "
                 f"FROM Users WHERE {field} LIKE ? ORDER BY EmployeeID;")
        param = (param + '%',)
        rows = self.db_portal.pull_data(query, param)

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
        query = f"SELECT COUNT(*) FROM Users WHERE {field} = ?"
        param = (param,)
        user_exists = self.db_portal.pull_data(query, param)[0][0]
        return user_exists
