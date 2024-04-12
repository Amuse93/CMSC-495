# Alpha Store Management System

import sqlite3
import os
import secrets
import getpass
import hashlib
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from passlib.hash import sha256_crypt
#from product_cache import ProductCache
from user_management import UserManagement

# Global Password for emails
server = None
organizational_email = None
email_password = None
db_name = 'alpha_store.sqlite3'
sql_file = 'static/Create_tables.sql'


def configure_routes(app):
    # Variables
    user_management_system = UserManagement(db_name)

    # Index (Login) page
    @app.route('/', methods=['GET', 'POST'])
    def index():
        message = ''

        if request.method == 'POST':
            username_entered = request.form.get('username')
            password_entered = request.form.get('password')

            error = login(username_entered, password_entered)
            if error == 0:
                if session.get('First_Time') == 0:
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('create_password'))
            elif error == 1:
                message = 'Invalid username or password!'
            elif error == 2:
                message = ('Your account has been locked!<br />'
                           'See a manager to reset your password!')

        return render_template('login.html', message=message)

    @app.route('/create_password', methods=['GET', 'POST'])
    def create_password():
        if session.get('Username') is None:
            return redirect(url_for('index'))
        message = ''

        if request.method == 'POST':
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            error = create_password_function(session.get('EmployeeID'), password1, password2)

            if error == 0:
                return redirect(url_for('home'))
            elif error == 1:
                message = ('Your password must include <br>'
                           '1 uppercase letter, 1 lowercase letter,<br>'
                           '1 number, and 1 special character!<br>'
                           'It must also be at least 8 characters!')
            elif error == 2:
                message = 'The passwords did not match!'

        return render_template('create_password.html', message=message)

    @app.route('/logout')
    def logout():
        logoff()
        return redirect(url_for('index'))

    @app.route('/home')
    def home():
        if session.get('Username') is None:
            return redirect(url_for('index'))
        return render_template('home.html', username=session.get('Username'), role=session.get('Position'))

    @app.route('/checkout')
    def checkout():
        # if ((session.get('Position') != 'Cashier') or (session.get('Position') != 'Cashier/Warehouseman') or (session.get('Position') != 'Manager')):
        #   return redirect(url_for('home'))
        title = 'Checkout'
        code = '<h1>Checkout</h1>'
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/inventory_management')
    def inventory_management():
        # if ((session.get('Position') != 'Warehouseman') or (session.get('Position') != 'Cashier/Warehouseman') or (session.get('Position') != 'Manager')):
        #   return redirect(url_for('home'))
        title = 'Inventory Management'
        code = '<h1>Inventory Management</h1>'
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/product_management')
    def product_management():
        # if session.get('Position') != 'Manager':
        #   return redirect(url_for('home'))
        title = 'Product Management'
        code = '<h1>Product Management</h1>'
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)


    @app.route('/user_management')
    def user_management():
        # if session.get('Position') != 'Manager':
        #   return redirect(url_for('home'))
        title = 'User Management'
        code = '<h1>User Management</h1>'
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/report_generation')
    def report_generation():
        # if session.get('Position') != 'Manager':
        #   return redirect(url_for('home'))
        title = 'Report Generation'
        code = '<h1>Report Generation</h1>'
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/add_user', methods=['GET', 'POST'])
    def add_user():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add User'
        data = {}
        message = ''
        data["Message"] = message
        code = get_form('add_user', data)

        if request.method == 'POST':
            user_data = []

            user_data.append(request.form.get('employee_id'))
            user_data.append(request.form.get('username'))
            user_data.append(request.form.get('first_name'))
            user_data.append(request.form.get('last_name'))
            user_data.append(request.form.get('dob'))
            user_data.append(request.form.get('phone'))
            user_data.append(request.form.get('role'))

            password = user_management_system.add_user(user_data)

            if password == 1:
                message = f'<h6>A user with the employee ID {user_data[2]} already exists!</h6>'
                data = {"Message": message}
                code = get_form('add_user', data)
            elif password == 2:
                message = f'<h6>A user with the username {user_data[1]} already exists!</h6>'
                data = {"Message": message}
                code = get_form('add_user', data)
            else:
                code = (f'<h1>One-Time Password</h1><br>'
                        f'<h3>The account has been created. Provide the user with the one-time password.</h3><br>'
                        f'<p>{password}</p><br><br>'
                        f'<a href="{url_for('user_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/modify_user/<int:employee_id>', methods=['GET', 'POST'])
    def modify_user(employee_id):
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Modify User'
        message = ''
        data = user_management_system.get_user_data(employee_id)
        data["Message"] = message
        code = get_form('modify_user', data)
        message = ''

        if request.method == 'POST':
            user_data = []

            user_data.append(employee_id)
            user_data.append(request.form.get('username'))
            user_data.append(request.form.get('first_name'))
            user_data.append(request.form.get('last_name'))
            user_data.append(request.form.get('phone'))
            user_data.append(request.form.get('role'))

            user_management_system.modify_user(user_data)

            code = (f'<h1>Modify User {user_data[0]} ({user_data[1]})</h1>'
                    f'<h3>This user account has been successfully updated!</h3><br>'
                    f'<a href="{url_for('user_management')}">'
                    f'<input class="selection_button" type="button" value="OK">'
                    f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/delete_user/<int:employee_id>', methods=['GET', 'POST'])
    def delete_user(employee_id):
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Modify User'
        message = ''
        data = user_management_system.get_user_data(employee_id)
        data["Message"] = message
        code = get_form('delete_user', data)

        if request.method == 'POST':

            error = user_management_system.delete_user(data.get("EmployeeID"))

            if error == 0:
                code = (f'<h1>Delete User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                        f'<h3>This user account has been successfully deleted!</h3><br>'
                        f'<a href="{url_for('user_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/reset_user/<int:employee_id>', methods=['GET', 'POST'])
    def reset_user(employee_id):
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Reset User Password'
        message = ''
        data = user_management_system.get_user_data(employee_id)
        data["Message"] = message
        code = get_form('reset_user', data)

        if request.method == 'POST':

            password = user_management_system.reset_user_password(data.get("EmployeeID"))

            code = code = (f'<h1>One-Time Password</h1><br>'
                           f'<h3>The account has been reset.<br>Provide the user with the one-time password.</h3><br>'
                           f'<p>{password}</p><br><br>'
                           f'<input class="selection_button" type="button" value="OK">'
                           f'<h3>The account has been reset.<br>Provide the user with the one-time password.</h3><br>'
                           f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)


# Set up the Flask app
def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(24)
    app.static_folder = 'static'

    # Configure database creation
    create_database()

    # Other configurations
    configure_routes(app)

    return app


# Check if there exists a database. If not, create one.
def create_database():
    # Check if the database file exists
    if not os.path.exists(db_name):
        # If the database file doesn't exist, create a new one
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Read SQL commands from the SQL file and execute them
        with open(sql_file, 'r') as sql_script_file:
            sql_commands = sql_script_file.read()
            cursor.executescript(sql_commands)

        # Commit changes and close the connection
        conn.commit()
        conn.close()


# Allows the user to login
def login(username, password):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    try:
        # Check if the username exists
        cursor.execute("SELECT COUNT(*) FROM Users WHERE Username = ?", (username,))
        user_exists = cursor.fetchone()[0]

        if user_exists == 1:
            # Get the number of tries for the user
            cursor.execute("SELECT Number_Of_Tries FROM Users WHERE Username = ?", (username,))
            num_tries = cursor.fetchone()[0]

            # Check if the user has not exceeded the maximum number of tries (less than 3)
            if num_tries < 3:
                # Get the stored password for the user
                cursor.execute("SELECT Password FROM Users WHERE Username = ?", (username,))
                stored_password = cursor.fetchone()[0]

                # Hash the provided password (assuming it's SHA256 hashed in the database)
                hash_pass = sha256_crypt.verify(password, stored_password)

                # Check if the provided password matches the stored password
                if hash_pass is True:
                    cursor.execute("SELECT EmployeeID FROM Users WHERE Username = ?", (username,))
                    session['EmployeeID'] = cursor.fetchone()[0]
                    session['Username'] = username
                    cursor.execute("SELECT Position FROM Users WHERE Username = ?", (username,))
                    session['Position'] = cursor.fetchone()[0]
                    cursor.execute("SELECT First_Name FROM Users WHERE Username = ?", (username,))
                    session['First_Name'] = cursor.fetchone()[0]
                    cursor.execute("SELECT Last_Name FROM Users WHERE Username = ?", (username,))
                    session['Last_Name'] = cursor.fetchone()[0]
                    cursor.execute("SELECT First_Time FROM Users WHERE Username = ?", (username,))
                    session['First_Time'] = cursor.fetchone()[0]

                    # Reset the number of tries
                    cursor.execute("UPDATE Users SET Number_Of_Tries = 0 WHERE Username = ?",
                                   (username,))

                    # Commit changes to the database
                    conn.commit()

                    return 0
                else:
                    # Password does not match, increment the number of tries
                    cursor.execute("UPDATE Users SET Number_Of_Tries = Number_Of_Tries + 1 WHERE Username = ?",
                                   (username,))

                    # Commit changes to the database
                    conn.commit()

                    return 1
            else:
                # User has exceeded the maximum number of tries
                return 2
        else:
            # Username does not exist
            return 1

    finally:
        # Close the database connection
        conn.close()


# Change password
def create_password_function(employee_id, password1, password2):
    # Check if password1 meets complexity requirements
    flag = 0
    if (len(password1) < 8):
        flag = 1
    elif not re.search("[a-z]", password1):
        flag = 1
    elif not re.search("[A-Z]", password1):
         flag = 1
    elif not re.search("[0-9]", password1):
        flag = 1
    elif not re.search("[!@#$%^&*()_+=:;<>?]", password1):
        flag = 1

    if flag == 1:
        return 1

    # Check if password1 and password2 match
    if password1 != password2:
        return 2

    hashed_password = sha256_crypt.hash(password1)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Change the user's password
    cursor.execute(f"UPDATE Users SET Password = ? WHERE EmployeeID = ?;",
                   (hashed_password, employee_id))

    cursor.execute(f"UPDATE Users SET First_Time = 0 WHERE EmployeeID = ?;",
                   (employee_id,))

    # Commit changes to the database
    conn.commit()

    # Close the database connection
    conn.close()

    return 0


# Logs off the user by clearing the session data
def logoff():
    session.clear()


# Provides HTML for various forms
def get_form(type, data):
    if type == 'add_user':
        add_user = (f'<h1>Add User</h1>'
                    f'{data.get("Message")}'
                    f'<form action="{url_for('add_user')}" id="add_user" method="post">'
                    f'<label for="employee_id">EmployeeID: </label>'
                    f'<input type="text" id="employee_id" name="employee_id" size="25" autocomplete="off" required>'
                    f'<br>'
                    f'<br>'
                    f'<label for="username">Username: </label>'
                    f'<input type="text" id="username" name="username" size="25" autocomplete="off" required>'
                    f'<br>'
                    f'<br>'
                    f'<label for="first_name">First Name: </label>'
                    f'<input type="text" id="first_name" name="first_name" size="25" autocomplete="off" required>'
                    f'<br>'
                    f'<br>'
                    f'<label for="last_name">Last Name: </label>'
                    f'<input type="text" id="last_name" name="last_name" size="25" autocomplete="off" required>'
                    f'<br>'
                    f'<br>'
                    f'<label for="dob">Date of Birth: </label>'
                    f'<input type="date" id="dob" name="dob" size="25" autocomplete="off" required>'
                    f'<br>'
                    f'<br>'
                    f'<label for="phone">Phone Number: </label>'
                    f'<input type="tel" id="phone" name="phone" size="25" autocomplete="off" required>'
                    f'<br>'
                    f'<br>'
                    f'<label for="role">Role(s): </label>'
                    f'<select id="role" name="role" required>'
                    f'<option disabled selected>-- Make Selection --</option>'
                    f'<option value = "Cashier">Cashier</option>'
                    f'<option value = "Warehouseman">Warehouseman</option>'
                    f'<option value = "Cashier/Warehouseman">Cashier/Warehouseman</option>'
                    f'<option value = "Manager">Manager</option>'
                    f'</select>'
                    f'<br>'
                    f'<br>'
                    f'<br>'
                    f'<div>'
                    f'<input class="selection_button" type="submit" value="OK">'
                    f'<a href="{url_for('user_management')}">'
                    f'<input class="selection_button" type="button" value="Cancel">'
                    f'</a>'
                    f'</div>'
                    f'</form>'
                    )
        return add_user



    if type == 'modify_user':
        modify_user = (f'<h1>Modify User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                       f'<form action="{url_for('modify_user', employee_id=data.get("EmployeeID"))}" id="modify_user" method="post">'
                       f'<label for="username">Username: </label>'
                       f'<input type="text" id="username" name="username" size="25" autocomplete="off" value="{data.get("Username")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="first_name">First Name: </label>'
                       f'<input type="text" id="first_name" name="first_name" size="25" autocomplete="off" value="{data.get("First_Name")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="last_name">Last Name: </label>'
                       f'<input type="text" id="last_name" name="last_name" size="25" autocomplete="off" value="{data.get("Last_Name")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="phone">Phone Number: </label>'
                       f'<input type="tel" id="phone" name="phone" size="25" autocomplete="off" value="{data.get("Phone_Number")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="role">Role(s): </label>'
                       f'<select id="role" name="role" required>'
                       f'<option disabled selected>-- Make Selection --</option>'
                       f'<option value = "Cashier">Cashier</option>'
                       f'<option value = "Warehouseman">Warehouseman</option>'
                       f'<option value = "Cashier/Warehouseman">Cashier/Warehouseman</option>'
                       f'<option value = "Manager">Manager</option>'
                       f'</select>'
                       f'<br>'
                       f'<br>'
                       f'<br>'
                       f'<div>'
                       f'<input class="selection_button" type="submit" value="OK">'
                       f'<a href="{url_for("user_management")}">'
                       f'<input class="selection_button" type="button" value="Cancel">'
                       f'</a>'
                       f'</div>'
                       f'</form>'
                       f'<br>'
                       f'<br>'
                       f'<br>'
                       f'<br>'
                       f'<br>'
                       f'<div>'
                       f'<div class="headingsContainer">'
                       f'<h1>Other Options</h1>'
                       f'</div>'
                       f'<a href="{url_for("reset_user", employee_id=data.get("EmployeeID"))}">'
                       f'<input class="selection_button" type="button" value="Reset Password">'
                       f'</a>'
                       f'<a href="{url_for("delete_user", employee_id=data.get("EmployeeID"))}">'
                       f'<input class="selection_button" type="button" value="Delete">'
                       f'</a>'
                       f'</div>'
                       )
        return modify_user


    if type == 'delete_user':
        delete_user = (f'<h1>Delete User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                       f'<form action="{url_for('delete_user', employee_id=data.get("EmployeeID"))}" id="delete_user" method="post">'
                       f'<h3>Are you sure you want to delete this account?</h3>'
                       f'<br>'
                       f'<div>'
                       f'<input class="selection_button" type="submit" value="OK">'
                       f'<a href="{url_for("modify_user", employee_id=data.get("EmployeeID"))}">'
                       f'<input class="selection_button" type="button" value="Cancel">'
                       f'</a>'
                       f'</div>'
                       f'</form>'
                       )

        return delete_user


    if type == 'reset_user':
        reset_user = (f'<h1>Reset User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                      f'<form action="{url_for('reset_user', employee_id=data.get("EmployeeID"))}" id="reset_user" method="post">'
                      f'<h3>Are you sure you want to reset the password for this account?</h3>'
                      f'<br>'
                      f'<div>'
                      f'<input class="selection_button" type="submit" value="OK">'
                      f'<a href="{url_for("modify_user", employee_id=data.get("EmployeeID"))}">'
                      f'<input class="selection_button" type="button" value="Cancel">'
                      f'</a>'
                      f'</div>'
                      f'</form>'
                      )

        return reset_user


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # Prompt System Administrator for the organization's email server, email, and password
    #global server
    #global organizational_email
    #global email_password
    #server = input("Email server: ")
    #organizational_email = input("Email: ")
    #email_password = getpass.getpass("Password: ")

    app = create_app()
    app.run()
