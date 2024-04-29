# Alpha Store Management System
import sqlite3
import os
import secrets
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import sha256_crypt
from checkout import Checkout
from inventory_management import InventoryManagement
from product_management import ProductManagement
from report_generator import ReportGenerator
from user_management import UserManagement

# Global variables
db_name = 'alpha_store.sqlite3'
sql_file = 'static/Create_tables.sql'


def configure_routes(app):
    # Variables
    user_management_system = UserManagement(db_name)
    product_management_system = ProductManagement(db_name)
    inventory_management_system = InventoryManagement(db_name)
    checkout_system = Checkout(db_name)
    report_generation_system = ReportGenerator(db_name)

    # General Section
    # Index (Login) page
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if session.get("Username") is not None:
            return redirect(url_for("home"))

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

    #######################################################################
    # Checkout Section
    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        if ((session.get('Position') != 'Cashier') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Checkout'
        products_list = product_management_system.list_products()  # Use a different variable name

        return render_template('checkout.html', username=session.get('Username'), title=title,
                               products=products_list)

    @app.route('/finalize_checkout', methods=['POST'])
    def finalize_checkout():
        title = 'Finalize Checkout'
        data = request.json
        cart_list = data.get('orderData')
        total = data.get('salesTotal')
        email = data.get('email')

        if request.method == 'POST':
            checkout_system.checkout(cart_list, total, email, session.get('EmployeeID'))
            code = (f'<h1>Finalize Checkout</h1><br>'
                    f'<h3>Order has been Completed and the receipt sent to customer.</h3><br>'
                    f'<a href="{url_for("checkout")}">'
                    f'<input class="selection_button" type="button" value="OK">'
                    f'</a>')

            return render_template('form_template.html',
                                   username=session.get('Username'), title=title, code=code)

    #######################################################################
    # Inventory Management Section
    @app.route('/inventory_management/', methods=['GET', 'POST'])
    def inventory_management():
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Inventory Management'
        field = 'ProductID'
        products = inventory_management_system.list_shelf_products()

        if request.method == 'POST':
            field = request.form.get('search_by')
            param = request.form.get('search')
            if (param is not None) and (len(param) <= 60):
                products = inventory_management_system.search_shelf_products(field, param)
            else:
                products = inventory_management_system.list_shelf_products()

        return render_template('inventory_management_template.html',
                               username=session.get('Username'), title=title, products=products, field=field)

    @app.route('/inventory_management/shelf_view', methods=['GET', 'POST'])
    def inventory_management_shelf_view():
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Inventory Management'
        shelves = inventory_management_system.list_shelves()
        field = 'ShelfID'

        if request.method == 'POST':
            param = request.form.get('search')
            if (param is not None) and (len(param) <= 60):
                shelves = inventory_management_system.search_shelves(param)
            else:
                shelves = inventory_management_system.list_shelves()

        return render_template('inventory_management_template_shelf_view.html',
                               username=session.get('Username'), title=title, shelves=shelves,
                               field=field)

    @app.route('/inventory_management/shelf/<shelf_id>', methods=['GET', 'POST'])
    def inventory_management_shelf(shelf_id):
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Inventory Management'
        field = 'ShelfID'
        products = inventory_management_system.search_shelf_products(field, shelf_id)

        if request.method == 'POST':
            field = request.form.get('search_by')
            param = request.form.get('search')
            if (param is not None) and (len(param) <= 60):
                products = inventory_management_system.search_shelf_products_by_shelf(field, param, shelf_id)
            else:
                products = inventory_management_system.list_shelf_products()

        return render_template('inventory_management_shelf_template.html',
                               username=session.get('Username'), title=title, shelf_id=shelf_id, products=products)

    @app.route('/add_shelf', methods=['GET', 'POST'])
    def add_shelf():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add Shelf'
        data = {}
        message = ''
        data["Message"] = message
        code = get_inventory_management_form('add_shelf', data)

        if request.method == 'POST':
            shelf_data = [request.form.get('shelf_id')]

            error = inventory_management_system.add_shelf(shelf_data)

            if error == 1:
                message = f'<h4>A shelf with the shelf_id {shelf_data[0]} already exists!</h4>'
                data = {"Message": message}
                code = get_inventory_management_form('add_shelf', data)
            elif error == 3:
                message = f'<h4>The length of the ShelfID must equal 7!</h4>'
                data = {"Message": message}
                code = get_inventory_management_form('add_shelf', data)
            elif error == 4:
                message = f'<h4>ShelfID must be begin with "WH" or "SF"!</h4>'
                data = {"Message": message}
                code = get_inventory_management_form('add_shelf', data)
            else:
                code = (f'<h1>Add Product</h1><br>'
                        f'<h3>Shelf was added successfully.</h3><br>'
                        f'<a href="{url_for('inventory_management_shelf_view')}">'
                        f'<input class="selection_button" type="submit" value="OK">'
                        f'</a>')
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/delete_shelf/<shelf_id>', methods=['GET', 'POST'])
    def delete_shelf(shelf_id):
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Delete Shelf'
        message = ''
        data = inventory_management_system.search_shelves(shelf_id)[0]
        data["Message"] = message
        code = get_inventory_management_form('delete_shelf', data)

        if request.method == 'POST':

            error = inventory_management_system.delete_shelf(data.get("ShelfID"))

            if error == 1:
                message = f'<h4>The shelf with the ShelfID {shelf_id} does not exist!</h4>'
                data["Message"] = message
                code = get_inventory_management_form('delete_shelf', data)

            elif error == 2:
                message = (f'<h4>The shelf must be emptied before it can be deleted!</h4>'
                           f'<h4>Please move the remaining products to another shelf '
                           f'or remove the product record from the shelf if the quantity of the product is 0!</h4>')
                data["Message"] = message
                code = get_inventory_management_form('delete_shelf', data)

            else:
                code = (f'<h1>Delete Shelf {data.get("ShelfID")}</h1>'
                        f'<h3>This Shelf has been successfully deleted!</h3><br>'
                        f'<a href="{url_for('inventory_management_shelf_view')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/add_product_to_shelf', methods=['GET', 'POST'])
    def add_product_to_shelf():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add Product'
        data = {}
        message = ''
        data["Message"] = message
        code = get_inventory_management_form('add_product_to_shelf', data)

        if request.method == 'POST':
            shelf_product_data = [request.form.get('shelf_id'), request.form.get('product_id')]

            error = inventory_management_system.add_product_to_shelf(shelf_product_data)

            if error == 1:
                message = f'<h4>The shelf with Shelf ID {shelf_product_data[0]} does not exist!</h4>'
                data = {"Message": message}
                code = get_inventory_management_form('add_product_to_shelf', data)
            elif error == 2:
                message = f'<h4>The product with the product ID {shelf_product_data[1]} does not exist!</h4>'
                data = {"Message": message}
                code = get_inventory_management_form('add_product_to_shelf', data)
            elif error == 3:
                message = f'<h4>The this product already has a record a warehouse shelf!</h4>'
                data = {"Message": message}
                code = get_inventory_management_form('add_product_to_shelf', data)
            elif error == 4:
                message = f'<h4>The this product already has a record a sales floor shelf!</h4>'
                data = {"Message": message}
                code = get_inventory_management_form('add_product_to_shelf', data)
            else:
                code = (f'<h1>Add Product</h1><br>'
                        f'<h3>The Product was added successfully.</h3><br>'
                        f'<a href="{url_for('inventory_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/delete_product_from_shelf/<product_id>&<shelf_id>', methods=['GET', 'POST'])
    def delete_product_from_shelf(product_id, shelf_id):
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Delete Product From Shelf'
        message = ''
        data = inventory_management_system.search_shelf_products_by_shelf('ProductID', product_id, shelf_id)[0]
        data["Message"] = message
        code = get_inventory_management_form('delete_product_from_shelf', data)

        if request.method == 'POST':

            error = inventory_management_system.delete_product_from_shelf(data.get('ProductID'), data.get('ShelfID'))

            if error == 1:
                message = f'<h4>The quantity of the Shelf_Product record must be 0!</h4>'
                data["Message"] = message
                code = get_inventory_management_form('delete_product_from_shelf', data)
            else:
                code = (f'<h1>Delete Product {data.get("ProductID")} From Shelf {data.get("ShelfID")}</h1>'
                        f'<h3>This Product has been successfully deleted from the shelf!</h3><br>'
                        f'<a href="{url_for('inventory_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/receive_order', methods=['GET', 'POST'])
    def receive_order():
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Receive Order'
        products_list = product_management_system.list_products()  # Use a different variable name

        # if request.method == 'POST':
        #
        #     code = (f'<h1>Receive Order</h1><br>'
        #             f'<h3>The order was received successfully.</h3><br>'
        #             f'<a href="{url_for("inventory_management")}">'
        #             f'<input class="selection_button" type="button" value="OK">'
        #             f'</a>')
        #
        #     return render_template('form_template.html',
        #                            username=session.get('Username'), title=title, code=code)

        return render_template('receive_order.html', username=session.get('Username'), title=title,
                               products=products_list)

    @app.route('/submit_received_order', methods=['POST'])
    def submit_order():
        title = 'Receive Order'
        order_data = request.json

        # Pass the order data to the receive_order function
        inventory_management_system.receive_order(order_data)

        if request.method == 'POST':

            code = (f'<h1>Receive Order</h1><br>'
                    f'<h3>The order was received successfully.</h3><br>'
                    f'<a href="{url_for("inventory_management")}">'
                    f'<input class="selection_button" type="button" value="OK">'
                    f'</a>')

            return render_template('form_template.html',
                                   username=session.get('Username'), title=title, code=code)

    @app.route('/move_product/<product_id>&<shelf_id>', methods=['GET', 'POST'])
    def move_product(product_id, shelf_id):
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Move Product'
        data = {}
        message = ''
        data['Message'] = message
        data['ProductID'] = product_id
        data['ShelfID'] = shelf_id
        code = get_inventory_management_form('move_product', data)

        if request.method == 'POST':
            shelf_product_info = [product_id, shelf_id, request.form.get('to_shelf_id')]

            error = inventory_management_system.move_product(shelf_product_info)

            if error == 1:
                message = f"<h4>The product with the product ID {shelf_product_info[0]} was not found!</h4>"
                data['Message'] = message
                code = get_inventory_management_form('move_product', data)
            elif error == 2:
                message = f"<h4>The shelf with the shelf ID {shelf_product_info[1]} was not found!</h4>"
                data['Message'] = message
                code = get_inventory_management_form('move_product', data)
            elif error == 3:
                message = f"<h4>The shelf with the shelf ID {shelf_product_info[2]} was not found!</h4>"
                data['Message'] = message
                code = get_inventory_management_form('move_product', data)
            elif error == 4:
                message = f"<h4>A product from a warehouse shelf can only be moved to another warehouse shelf!</h4>"
                data['Message'] = message
                code = get_inventory_management_form('move_product', data)
            elif error == 5:
                message = f"<h4>A product from a sales floor shelf can only be moved to another sales floor shelf!</h4>"
                data['Message'] = message
                code = get_inventory_management_form('move_product', data)
            else:
                code = (f'<h1>Move Product</h1><br>'
                        f'<h3>The Product was moved successfully.</h3><br>'
                        f'<a href="{url_for('inventory_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/stock_product/<product_id>', methods=['GET', 'POST'])
    def stock_product(product_id):
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Stock Product'
        data = {}
        message = ''
        data['Message'] = message
        data['ProductID'] = product_id
        code = get_inventory_management_form('stock_product', data)

        if request.method == 'POST':
            product = [product_id, request.form.get('quantity')]

            inventory_management_system.stock_product(product)

            code = (f'<h1>Stock Product</h1><br>'
                    f'<h3>The product was stocked successfully.</h3><br>'
                    f'<a href="{url_for('inventory_management')}">'
                    f'<input class="selection_button" type="button" value="OK">'
                    f'</a>')

        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/report_waste/<product_id>&<shelf_id>', methods=['GET', 'POST'])
    def report_waste(product_id, shelf_id):
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Report Waste'
        data = {}
        message = ''
        data['Message'] = message
        data['ProductID'] = product_id
        data['ShelfID'] = shelf_id
        code = get_inventory_management_form('report_waste', data)

        if request.method == 'POST':
            now = datetime.now()
            formatted_datetime = now.strftime('%Y-%m-%d')
            report = [product_id, shelf_id, request.form.get('quantity'), request.form.get('reason'),
                      request.form.get('description'), session.get('EmployeeID'), formatted_datetime]

            inventory_management_system.report_waste(report)

            code = (f'<h1>Report Waste</h1><br>'
                    f'<h3>The report was submitted successfully.</h3><br>'
                    f'<a href="{url_for('inventory_management')}">'
                    f'<input class="selection_button" type="button" value="OK">'
                    f'</a>')
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    #######################################################################
    # Product Management Section
    @app.route('/product_management', methods=['GET', 'POST'])
    def product_management():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Product Management'
        products = product_management_system.list_products()
        field = 'ProductID'

        if request.method == 'POST':
            field = request.form.get('search_by')
            param = request.form.get('search')
            if (param is not None) and (len(param) <= 60):
                products = product_management_system.search_products(field, param)
            else:
                products = product_management_system.list_products()

        return render_template('product_management_template.html',
                               username=session.get('Username'), title=title, products=products, field=field)

    @app.route('/add_product', methods=['GET', 'POST'])
    def add_product():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add Product'
        data = {}
        message = ''
        data["Message"] = message
        code = get_product_management_form('add_product', data)

        if request.method == 'POST':
            product_data = [request.form.get('product_id'), request.form.get('product_name'), request.form.get('price')]

            error = product_management_system.add_product(product_data)

            if error == 1:
                message = f'<h4>A product with the product_id {product_data[0]} already exists!</h4>'
                data = {"Message": message}
                code = get_product_management_form('add_product', data)
            elif error == 2:
                message = f'<h4>A product with the product name {product_data[1]} already exists!</h4>'
                data = {"Message": message}
                code = get_product_management_form('add_product', data)
            elif error == 3:
                message = f'<h4>The ProductID is too long!</h6>'
                data = {"Message": message}
                code = get_product_management_form('add_product', data)
            elif error == 4:
                message = f'<h4>Product name is too long!</h4>'
                data = {"Message": message}
                code = get_product_management_form('add_product', data)
            elif error == 5:
                message = f'<h4>The price must be a number!</h4>'
                data = {"Message": message}
                code = get_product_management_form('add_product', data)

            else:
                code = (f'<h1>Add Product</h1><br>'
                        f'<h3>The Product was added successfully.</h3><br>'
                        f'<a href="{url_for('product_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/modify_product/<product_id>', methods=['GET', 'POST'])
    def modify_product(product_id):
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Modify Product'
        message = ''
        data = product_management_system.get_product_data(product_id)
        data["Message"] = message
        data['ProductID'] = product_id
        code = get_product_management_form('modify_product', data)

        if request.method == 'POST':
            product_data = [product_id, request.form.get('product_name'), request.form.get('price')]

            error = product_management_system.modify_product(product_data)

            if error == 2:
                message = f'<h4>Product name already exists!</h4>'
                data["Message"] = message
                code = get_product_management_form('modify_product', data)
            elif error == 4:
                message = f'<h4>Product Name is too long!</h4>'
                data["Message"] = message
                code = get_product_management_form('modify_product', data)
            elif error == 5:
                message = f'<h4>Price must be a number!</h4>'
                data["Message"] = message
                code = get_product_management_form('modify_product', data)

            else:
                code = (f'<h1>Modify Product {product_data[0]} ({product_data[1]})</h1>'
                        f'<h3>This product has been successfully updated!</h3><br>'
                        f'<a href="{url_for('product_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/delete_product/<product_id>', methods=['GET', 'POST'])
    def delete_product(product_id):
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Delete Product'
        message = ''
        data = product_management_system.get_product_data(product_id)
        data["Message"] = message
        code = get_product_management_form('delete_product', data)

        if request.method == 'POST':

            error = product_management_system.delete_product(data.get("ProductID"))

            if error == 1:
                message = f'<h4>The product {product_id} does not exist!</h4>'
                data["Message"] = message
                code = get_product_management_form('modify_product', data)
            elif error == 2:
                message = (f'<h4>The product {product_id} has shelf records! '
                           f'These records must first be deleted using the inventory management system!</h4>')
                data["Message"] = message
                code = get_product_management_form('modify_product', data)
            else:
                code = (f'<h1>Delete Product {data.get("ProductID")} ({data.get("Product_Name")})</h1>'
                        f'<h3>This Product has been successfully deleted!</h3><br>'
                        f'<a href="{url_for('product_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    #######################################################################
    # User Management Section
    @app.route('/user_management', methods=['GET', 'POST'])
    def user_management():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))

        title = 'User Management'
        users = user_management_system.list_users()
        field = 'EmployeeID'

        if request.method == 'POST':
            field = request.form.get('search_by')
            param = request.form.get('search')
            if (param is not None) and (len(param) <= 60):
                users = user_management_system.search_users(field, param)
            else:
                users = user_management_system.list_users()

        return render_template('user_management_template.html',
                               username=session.get('Username'), title=title, users=users, field=field)

    @app.route('/add_user', methods=['GET', 'POST'])
    def add_user():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add User'
        data = {}
        message = ''
        data["Message"] = message
        code = get_user_management_form('add_user', data)

        if request.method == 'POST':
            user_data = [request.form.get('employee_id'), request.form.get('username'), request.form.get('first_name'),
                         request.form.get('last_name'), request.form.get('dob'), request.form.get('phone'),
                         request.form.get('role')]

            password = user_management_system.add_user(user_data)

            if password == 1:
                message = f'<h4>A user with the employee ID {user_data[2]} already exists!</h4>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
            elif password == 2:
                message = f'<h4>A user with the username {user_data[1]} already exists!</h4>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
            elif password == 3:
                message = f'<h4>The EmployeeID must be a number!</h6>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
            elif password == 4:
                message = f'<h4>Username is too long!</h4>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
            elif password == 5:
                message = f'<h4>First Name is too long!</h4>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
            elif password == 6:
                message = f'<h4>Last Name is too long!</h4>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
            elif password == 7:
                message = f'<h4>Invalid phone number!</h4>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
            elif password == 8:
                message = f'<h4>Invalid role!</h4>'
                data = {"Message": message}
                code = get_user_management_form('add_user', data)
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
        data['EmployeeID'] = employee_id
        code = get_user_management_form('modify_user', data)

        if request.method == 'POST':
            user_data = [employee_id, request.form.get('username'), request.form.get('first_name'),
                         request.form.get('last_name'), request.form.get('phone'), request.form.get('role')]

            error = user_management_system.modify_user(user_data)

            if error == 4:
                message = f'<h4>Username is too long!</h4>'
                data["Message"] = message
                code = get_user_management_form('modify_user', data)
            elif error == 5:
                message = f'<h4>First Name is too long!</h4>'
                data["Message"] = message
                code = get_user_management_form('modify_user', data)
            elif error == 6:
                message = f'<h4>Last Name is too long!</h4>'
                data["Message"] = message
                code = get_user_management_form('modify_user', data)
            elif error == 7:
                message = f'<h4>Invalid phone number!</h4>'
                data["Message"] = message
                code = get_user_management_form('modify_user', data)
            else:
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
        title = 'Delete User'
        message = ''
        data = user_management_system.get_user_data(employee_id)
        data["Message"] = message
        code = get_user_management_form('delete_user', data)

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
        code = get_user_management_form('reset_user', data)

        if request.method == 'POST':
            password = user_management_system.reset_user_password(data.get("EmployeeID"))

            code = (f'<h1>One-Time Password</h1><br>'
                    f'<h3>The account has been reset.<br>Provide the user with the one-time password.</h3><br>'
                    f'<p>{password}</p><br><br>'
                    f'<a href="{url_for('modify_user', employee_id=data.get("EmployeeID"))}">'
                    f'<input class="selection_button" type="button" value="OK">'
                    f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    #######################################################################
    # Report Generation Section
    @app.route('/report_generation')
    def report_generation():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Report Generation'
        data = {}
        message = ''
        data["Message"] = message
        code = get_report_generator_form('report_main', data)
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/report_generation/inventory_report')
    def inventory_report():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Inventory Report'
        data = []
        code = get_report_generator_form('inventory_report', data)
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/report_generation/inventory_report/total_inventory')
    def total_inventory_report():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))

        report_info = {'Report_Type': 'Inventory', 'EmployeeID': session.get('EmployeeID'), 'Scope': 'Total_Inventory'}

        report_generation_system.inventory_report(report_info)

        return redirect(url_for('report_generation'))

    @app.route('/report_generation/inventory_report/shelf_inventory')
    def shelf_inventory_report():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))

        report_info = {'Report_Type': 'Inventory', 'EmployeeID': session.get('EmployeeID'), 'Scope': 'Shelf_Inventory'}

        report_generation_system.generate_report(report_info)

        return redirect(url_for('report_generation'))

    @app.route('/report_generation/sales_report', methods=['GET', 'POST'])
    def sales_report():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Sales Report'
        report_info = {}
        data = {}
        message = ''
        data["Message"] = message
        code = get_report_generator_form('sales_report', data)

        if request.method == 'POST':
            report_info['Report_Type'] = 'Sales'
            report_info['EmployeeID'] = session.get('EmployeeID')
            report_info['Scope'] = request.form.get('scope')
            report_info['ProductID'] = request.form.get('product_id')
            report_info['Metric'] = request.form.get('metric')
            report_info['Period'] = request.form.get('period')
            report_info['From_Date'] = request.form.get('from_date')
            report_info['To_Date'] = request.form.get('to_date')

            error = report_generation_system.generate_report(report_info)

            if error == 0:
                return redirect(url_for('report_generation'))
            elif error == 2:
                message = f'<h4>Invalid Report Type!</h4>'
                data["Message"] = message
            elif error == 3:
                message = f'<h4>The product with the ProductID {request.form.get('product_id')} does not exist!</h4>'
                data["Message"] = message

        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/report_generation/waste_report', methods=['GET', 'POST'])
    def waste_report():
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Waste Report'
        report_info = {}
        data = {}
        message = ''
        data["Message"] = message
        code = get_report_generator_form('waste_report', data)

        if request.method == 'POST':
            report_info['Report_Type'] = 'Waste'
            report_info['EmployeeID'] = session.get('EmployeeID')
            report_info['Scope'] = request.form.get('scope')
            report_info['ProductID'] = request.form.get('product_id')
            report_info['Metric'] = request.form.get('metric')
            report_info['ReasonCode'] = request.form.get('reason')
            report_info['Period'] = request.form.get('period')
            report_info['From_Date'] = request.form.get('from_date')
            report_info['To_Date'] = request.form.get('to_date')

            error = report_generation_system.generate_report(report_info)

            if error == 0:
                return redirect(url_for('report_generation'))
            elif error == 2:
                message = f'<h4>Invalid Report Type!</h4>'
                data["Message"] = message
            elif error == 3:
                message = f'<h4>The product with the ProductID {request.form.get('product_id')} does not exist!</h4>'
                data["Message"] = message

        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)


# Set up the Flask app
def create_app():
    flask_app = Flask(__name__)
    flask_app.secret_key = secrets.token_hex(24)
    flask_app.static_folder = 'static'

    # Configure database creation
    create_database()

    # Other configurations
    configure_routes(flask_app)

    return flask_app


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
            if num_tries <= 3:
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
    if len(password1) < 8:
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


def get_inventory_management_form(form_type, data):
    if form_type == 'add_shelf':
        add_shelf = (f'<h1>Add Shelf</h1>'
                     f'{data.get("Message")}'
                     f'<form action="{url_for('add_shelf')}" id="add_shelf" method="post">'
                     f'<label for="shelf_id">ShelfID: </label>'
                     f'<input type="text" id="shelf_id" name="shelf_id" size="25" autocomplete="off" required>'
                     f'<br>'
                     f'<br>'
                     f'<br>'
                     f'<div>'
                     f'<input class="selection_button" type="submit" value="OK">'
                     f'<a href="{url_for('inventory_management_shelf_view')}">'
                     f'<input class="selection_button" type="button" value="Cancel">'
                     )
        return add_shelf

    if form_type == 'delete_shelf':
        delete_shelf = (f'<h1>Delete Shelf {data.get("ShelfID")}</h1>'
                        f'{data.get("Message")}'
                        f'<form action="{url_for('delete_shelf', shelf_id=data.get("ShelfID"))}" '
                        f'id="delete_shelf" method="post">'
                        f'<h3>Are you sure you want to delete this shelf?</h3>'
                        f'<br>'
                        f'<div>'
                        f'<input class="selection_button" type="submit" value="OK">'
                        f'<a href="{url_for("inventory_management_shelf_view")}">'
                        f'<input class="selection_button" type="button" value="Cancel">'
                        f'</a>'
                        f'</div>'
                        f'</form>'
                        )
        return delete_shelf

    if form_type == 'add_product_to_shelf':
        add_product_to_shelf = (f'<h1>Add Product To Shelf</h1>'
                                f'{data.get("Message")}'
                                f'<form action="{url_for('add_product_to_shelf')}" '
                                f'id="add_product_to_shelf" method="post">'
                                f'<label for="product_id">ProductID: </label>'
                                f'<input type="text" id="product_id" name="product_id" '
                                f'size="25" autocomplete="off" required>'
                                f'<br>'
                                f'<br>'
                                f'<label for="shelf_id">ShelfID: </label>'
                                f'<input type="text" id="shelf_id" name="shelf_id" '
                                f'size="25" autocomplete="off" required>'
                                f'<br>'
                                f'<br>'
                                f'<br>'
                                f'<div>'
                                f'<input class="selection_button" type="submit" value="OK">'
                                f'<a href="{url_for('inventory_management')}">'
                                f'<input class="selection_button" type="button" value="Cancel">'
                                )
        return add_product_to_shelf

    if form_type == 'delete_product_from_shelf':
        delete_product_from_shelf = (f'<h1>Delete Product {data.get("ProductID")} From Shelf {data.get("ShelfID")}</h1>'
                                     f''
                                     f'{data.get("Message")}'
                                     f'<form action="{url_for('delete_product_from_shelf', 
                                                              product_id=data.get("ProductID"), 
                                                              shelf_id=data.get("ShelfID"))}" '
                                     f'id="delete_product_from_shelf" method="post">'
                                     f'<h3>Are you sure you want to delete this Product_Shelf record?</h3>'
                                     f'<br>'
                                     f'<div>'
                                     f'<input class="selection_button" type="submit" value="OK">'
                                     f'<a href="{url_for("inventory_management")}">'
                                     f'<input class="selection_button" type="button" value="Cancel">'
                                     f'</a>'
                                     f'</div>'
                                     f'</form>'
                                     )
        return delete_product_from_shelf

    if form_type == 'move_product':
        move_product = (f'<h1>Move Product {data.get('ProductID')} From Shelf {data.get('ShelfID')} To:</h1>'
                        f'{data.get("Message")}'
                        f'<form action="{url_for('move_product', 
                                                 product_id=data.get('ProductID'), 
                                                 shelf_id=data.get('ShelfID'))}" '
                        f'id="move_product" method="post">'
                        f'<label for="to_shelf_id">ShelfID: </label>'
                        f'<input type="text" id="to_shelf_id" name="to_shelf_id" size="25" autocomplete="off" required>'
                        f'<br>'
                        f'<br>'
                        f'<br>'
                        f'<div>'
                        f'<input class="selection_button" type="submit" value="OK">'
                        f'<a href="{url_for('inventory_management_shelf_view')}">'
                        f'<input class="selection_button" type="button" value="Cancel">'
                        )

        return move_product

    if form_type == 'stock_product':
        stock_product = (f'<h1>Stock Product {data.get('ProductID')}</h1>'
                         f'{data.get("Message")}'
                         f'<form action="{url_for('stock_product', product_id=data.get('ProductID'))}" '
                         f'id="move_product" method="post">'
                         f'<label for="quantity">Quantity: </label>'
                         f'<input type="text" id="quantity" name="quantity" size="25" autocomplete="off" required>'
                         f'<br>'
                         f'<br>'
                         f'<br>'
                         f'<div>'
                         f'<input class="selection_button" type="submit" value="OK">'
                         f'<a href="{url_for('inventory_management_shelf_view')}">'
                         f'<input class="selection_button" type="button" value="Cancel">'
                         )

        return stock_product

    if form_type == 'report_waste':
        report_waste = (f'<h1>Report Waste for Product {data.get('ProductID')} From Shelf {data.get("ShelfID")}</h1>'
                        f'{data.get("Message")}'
                        f'<form action="{url_for('report_waste', 
                                                 product_id=data.get('ProductID'), 
                                                 shelf_id=data.get("ShelfID"))}" '
                        f'id="report_waste" method="post">'
                        f'<label for="quantity">Quantity: </label>'
                        f'<input type="text" id="quantity" name="quantity" size="25" autocomplete="off" required>'
                        f'<br>'
                        f'<br>'
                        f'<label for="reason">Reason: </label>'
                        f'<select id="reason" name="reason" required>'
                        f'<option disabled selected>-- Make Selection --</option>'
                        f'<option value = "Expired">Expired</option>'
                        f'<option value = "Damaged">Damaged</option>'
                        f'<option value = "Stolen">Stolen</option>'
                        f'</select>'
                        f'<br>'
                        f'<br>'
                        f'<label for="description">Description: </label>'
                        f'<textarea id="description" name="description" rows="4" cols="50" '
                        f'autocomplete="off" required></textarea>'
                        f'<br>'
                        f'<br>'
                        f'<div>'
                        f'<input class="selection_button" type="submit" value="OK">'
                        f'<a href="{url_for('inventory_management_shelf_view')}">'
                        f'<input class="selection_button" type="button" value="Cancel">'
                        f'</form>'
                        )

        return report_waste


def get_product_management_form(form_type, data):
    if form_type == 'add_product':
        add_product = (f'<h1>Add Product</h1>'
                       f'{data.get("Message")}'
                       f'<form action="{url_for('add_product')}" id="add_product" method="post">'
                       f'<label for="product_id">ProductID: </label>'
                       f'<input type="text" id="product_id" name="product_id" size="25" autocomplete="off" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="product_name">Product_Name: </label>'
                       f'<input type="text" id="product_name" name="product_name" size="25" '
                       f'autocomplete="off" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="price">Price: </label>'
                       f'<input type="text" id="price" name="price" size="25" autocomplete="off" required>'
                       f'<br>'
                       f'<br>'
                       f'<input class="selection_button" type="submit" value="OK">'
                       f'<a href="{url_for('product_management')}">'
                       f'<input class="selection_button" type="button" value="Cancel">'
                       f'</a>'
                       f'</div>'
                       f'</form>'
                       )
        return add_product

    if form_type == 'modify_product':
        modify_product = (f'<h1>Modify Product {data.get("ProductID")} ({data.get("Product_Name")})</h1>'
                          f'{data.get("Message")}'
                          f'<form action="{url_for('modify_product', product_id=data.get("ProductID"))}" '
                          f'id="modify_product" method="post">'
                          f'<label for="product_name">Product_Name: </label>'
                          f'<input type="text" id="product_name" name="product_name" size="25" autocomplete="off" '
                          f'value="{data.get("Product_Name")}" required>'
                          f'<br>'
                          f'<br>'
                          f'<label for="price">Price: </label>'
                          f'<input type="text" id="price" name="price" size="25" autocomplete="off" '
                          f'value="{data.get("Price")}" required>'
                          f'<br>'
                          f'<br>'
                          f'<input class="selection_button" type="submit" value="OK">'
                          f'<a href="{url_for("product_management")}">'
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
                          f'<a href="{url_for("delete_product", product_id=data.get("ProductID"))}">'
                          f'<input class="selection_button" type="button" value="Delete">'
                          f'</a>'
                          f'</div>'
                          )
        return modify_product

    if form_type == 'delete_product':
        delete_product = (f'<h1>Delete Product {data.get("ProductID")} ({data.get("Product_Name")})</h1>'
                          f'<form action="{url_for('delete_product', product_id=data.get("ProductID"))}" '
                          f'id="delete_product" method="post">'
                          f'<h3>Are you sure you want to delete this product?</h3>'
                          f'<br>'
                          f'<div>'
                          f'<input class="selection_button" type="submit" value="OK">'
                          f'<a href="{url_for("modify_product", product_id=data.get("ProductID"))}">'
                          f'<input class="selection_button" type="button" value="Cancel">'
                          f'</a>'
                          f'</div>'
                          f'</form>'
                          )

        return delete_product


# Provides HTML for various forms
def get_user_management_form(form_type, data):
    if form_type == 'add_user':
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

    if form_type == 'modify_user':
        modify_user = (f'<h1>Modify User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                       f'{data.get("Message")}'
                       f'<form action="{url_for('modify_user', employee_id=data.get("EmployeeID"))}" '
                       f'id="modify_user" method="post">'
                       f'<label for="username">Username: </label>'
                       f'<input type="text" id="username" name="username" size="25" autocomplete="off" '
                       f'value="{data.get("Username")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="first_name">First Name: </label>'
                       f'<input type="text" id="first_name" name="first_name" size="25" autocomplete="off" '
                       f'value="{data.get("First_Name")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="last_name">Last Name: </label>'
                       f'<input type="text" id="last_name" name="last_name" size="25" autocomplete="off" '
                       f'value="{data.get("Last_Name")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="phone">Phone Number: </label>'
                       f'<input type="tel" id="phone" name="phone" size="25" autocomplete="off" '
                       f'value="{data.get("Phone_Number")}" required>'
                       f'<br>'
                       f'<br>'
                       f'<label for="role">Role(s): </label>'
                       f'<select id="role" name="role" required>'
                       f'<option disabled>-- Make Selection --</option>')
        if data.get("Position") == "Cashier":
            modify_user += (f'<option value = "Cashier" selected>Cashier</option>'
                            f'<option value = "Warehouseman">Warehouseman</option>'
                            f'<option value = "Cashier/Warehouseman">Cashier/Warehouseman</option>'
                            f'<option value = "Manager">Manager</option>')
        if data.get("Position") == "Warehouseman":
            modify_user += (f'<option value = "Cashier">Cashier</option>'
                            f'<option value = "Warehouseman" selected>Warehouseman</option>'
                            f'<option value = "Cashier/Warehouseman">Cashier/Warehouseman</option>'
                            f'<option value = "Manager">Manager</option>')
        if data.get("Position") == "Cashier/Warehouseman":
            modify_user += (f'<option value = "Cashier">Cashier</option>'
                            f'<option value = "Warehouseman">Warehouseman</option>'
                            f'<option value = "Cashier/Warehouseman" selected>Cashier/Warehouseman</option>'
                            f'<option value = "Manager">Manager</option>')
        if data.get("Position") == "Manager":
            modify_user += (f'<option value = "Cashier">Cashier</option>'
                            f'<option value = "Warehouseman">Warehouseman</option>'
                            f'<option value = "Cashier/Warehouseman">Cashier/Warehouseman</option>'
                            f'<option value = "Manager" selected>Manager</option>')
        modify_user += (f'</select>'
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

    if form_type == 'delete_user':
        delete_user = (f'<h1>Delete User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                       f'<form action="{url_for('delete_user', employee_id=data.get("EmployeeID"))}" '
                       f'id="delete_user" method="post">'
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

    if form_type == 'reset_user':
        reset_user = (f'<h1>Reset User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                      f'<form action="{url_for('reset_user', employee_id=data.get("EmployeeID"))}" '
                      f'id="reset_user" method="post">'
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


def get_report_generator_form(form_type, data):
    script = '''
    <script>
        const scopeSelect = document.getElementById("scope");
        const productIDDiv = document.querySelector('.product_id_input');
        // Function to toggle visibility of ProductID input div based on Scope selection
        function toggleProductIDInput() {
            if (scopeSelect.value === "Individual_Product") {
                productIDDiv.style.display = "block";  // Show ProductID input div
                document.getElementById("product_id").required = true;  // Make input required
            } else {
                productIDDiv.style.display = "none";  // Hide ProductID input div
                document.getElementById("product_id").value = "";  // Clear input value
                document.getElementById("product_id").required = false;  // Make input optional
            }
        }

        // Add event listener to Scope dropdown to trigger visibility toggle
        scopeSelect.addEventListener("change", toggleProductIDInput);

        // Initial call to set initial visibility based on initial Scope value
        toggleProductIDInput();
    </script>
    '''

    if form_type == 'report_main':
        report_main = (f'<h1>Select a Report</h1>'
                       f'<a href="{url_for('inventory_report')}"><button>Inventory</button></a>'
                       f'<a href="{url_for('sales_report')}"><button>Sales</button></a>'
                       f'<a href="{url_for('waste_report')}"><button>Waste</button></a>'
                       )
        return report_main

    if form_type == 'inventory_report':
        inventory_report = (f'<h1>Select a Scope</h1>'
                            f'<a href="{url_for('total_inventory_report')}">'
                            f'<button>Total Inventory On Hand</button>'
                            f'</a>'
                            f'<a href="{url_for('shelf_inventory_report')}">'
                            f'<button>Shelf Inventory</button>'
                            f'</a>'
                            f'<a href="{url_for('report_generation')}">'
                            f'<button>Cancel</button>'
                            f'</a>'
                            )
        return inventory_report

    if form_type == 'sales_report':
        sales_report = (f'<h1>Sales Report</h1>'
                        f'{data.get("Message")}'
                        f'<form action="{url_for('sales_report')}" id="sales_report" method="post">' 
                        f'<label for="scope">Scope: </label>'
                        f'<select id="scope" name="scope" required>'
                        f'<option disabled selected>-- Make Selection --</option>'
                        f'<option value = "Total">Total</option>'
                        f'<option value = "Individual_Product">Individual Product</option>'
                        f'</select>'
                        f'<br><br>'
                        f'<div class="product_id_input" style="display: none;">'
                        f'<label for="product_id">ProductID: </label>'
                        f'<input type="text" id="product_id" name="product_id" size="25" autocomplete="off">'
                        f'<br><br>'
                        f'</div>'
                        f'<label for="metric">Metric: </label>'
                        f'<select id="metric" name="metric" required>'
                        f'<option disabled selected>-- Make Selection --</option>'
                        f'<option value = "Quantity">Quantity</option>'
                        f'<option value = "Dollar_Amount">Dollar Amount</option>'
                        f'</select>'
                        f'<br><br>'
                        f'<label for="period">Period: </label>'
                        f'<select id="period" name="period" required>'
                        f'<option disabled selected>-- Make Selection --</option>'
                        f'<option value = "Yearly">Yearly</option>'
                        f'<option value = "Monthly">Monthly</option>'
                        f'<option value = "Weekly">Weekly</option>'
                        f'<option value = "Daily">Daily</option>'
                        f'</select>'
                        f'<br><br>'
                        f'<label for="from_date">From_Date: </label>'
                        f'<input type="date" id="from_date" name="from_date" size="25" autocomplete="off" required>'
                        f'<br><br>'
                        f'<label for="to_date">To Date: </label>'
                        f'<input type="date" id="to_date" name="to_date" size="25" autocomplete="off" required>'
                        f'<br><br><br>'
                        f'<div>'
                        f'<input class="selection_button" type="submit" value="OK">'
                        f'<a href="{url_for('report_generation')}">'
                        f'<input class="selection_button" type="button" value="Cancel">'
                        f'</a>'
                        f'</div>'
                        f'</form>'
                        f'{script}'
                        )
        return sales_report

    if form_type == 'waste_report':
        waste_report = (f'<h1>Waste Report</h1>'
                        f'{data.get("Message")}'
                        f'<form action="{url_for('waste_report')}" id="waste_report" method="post">' 
                        f'<label for="scope">Scope: </label>'
                        f'<select id="scope" name="scope" required>'
                        f'<option disabled selected>-- Make Selection --</option>'
                        f'<option value = "Total">Total</option>'
                        f'<option value = "Individual_Product">Individual Product</option>'
                        f'</select>'
                        f'<br><br>'
                        f'<div class="product_id_input" style="display:none;">'
                        f'<label for="product_id">ProductID: </label>'
                        f'<input type="text" id="product_id" name="product_id" size="25" autocomplete="off">'
                        f'<br><br>'
                        f'</div>'
                        f'<label for="metric">Metric: </label>'
                        f'<select id="metric" name="metric" required>'
                        f'<option disabled selected>-- Make Selection --</option>'
                        f'<option value = "Quantity">Quantity</option>'
                        f'<option value = "Dollar_Amount">Dollar Amount</option>'
                        f'</select>'
                        f'<br><br>'
                        f'<label for="reason">Reason: </label>'
                        f'<select id="reason" name="reason" required>'
                        f'<option value = "All" selected>All</option>'
                        f'<option value = "Expired">Expired</option>'
                        f'<option value = "Damaged">Damaged</option>'
                        f'<option value = "Stolen">Stolen</option>'
                        f'</select>'
                        f'<br><br>'
                        f'<label for="period">Period: </label>'
                        f'<select id="period" name="period" required>'
                        f'<option disabled selected>-- Make Selection --</option>'
                        f'<option value = "Yearly">Yearly</option>'
                        f'<option value = "Monthly">Monthly</option>'
                        f'<option value = "Weekly">Weekly</option>'
                        f'<option value = "Daily">Daily</option>'
                        f'</select>'
                        f'<br><br>'
                        f'<label for="from_date">From_Date: </label>'
                        f'<input type="date" id="from_date" name="from_date" size="25" autocomplete="off" required>'
                        f'<br><br>'
                        f'<label for="to_date">To Date: </label>'
                        f'<input type="date" id="to_date" name="to_date" size="25" autocomplete="off" required>'
                        f'<br><br><br>'
                        f'<div>'
                        f'<input class="selection_button" type="submit" value="OK">'
                        f'<a href="{url_for('report_generation')}">'
                        f'<input class="selection_button" type="button" value="Cancel">'
                        f'</a>'
                        f'</div>'
                        f'</form>'
                        f'{script}'
                        )
        return waste_report

    return 0


if __name__ == '__main__':
    # Prompt System Administrator for the organization's email server, email, and password
    # global server
    # global organizational_email
    # global email_password
    # server = input("Email server: ")
    # organizational_email = input("Email: ")
    # email_password = getpass.getpass("Password: ")

    app = create_app()
    app.run()
