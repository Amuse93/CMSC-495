# Alpha Store Management System
import secrets
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import sha256_crypt
from checkout import Checkout
from database_portal import DatabasePortal
from inventory_management import InventoryManagement
from product_management import ProductManagement
from report_generator import ReportGenerator
from user_management import UserManagement
from form_list import FormList

# Global variables
db_portal = DatabasePortal()
db_name = 'alpha_store.sqlite3'


def configure_routes(app):
    """configure_routes

    Description:
    Configure all endpoints for the website

    parameter:
    Flask object

    Output:
    Flask application object.
    """
    # Variables
    user_management_system = UserManagement()
    product_management_system = ProductManagement()
    inventory_management_system = InventoryManagement()
    checkout_system = Checkout()
    report_generation_system = ReportGenerator()
    form_list = FormList()

    # General Section
    # Index (Login) page
    @app.route('/', methods=['GET', 'POST'])
    def index():
        """index

        Description:
        Directs user to home if request is GET
        and Username is not None. If request is
        Post and username and password are correct,
        function directs user to home. Otherwise,
        function directs user to  login page.

        Parameter:
        none

        Output:
        string: error
        url_for("home")
        login.html
        """
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
        """create_password

        Description:
        Function is called when user login
        into the system for the first time.
        When called, function directs user
        to "create new password page".
        If password meets required criteria,
        function directs user to home page.

        Parameter:
        none

        Output:
        url_for('index').
        url_for('home')
        create_password.html
        """
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
        """logout

        Description:
        Function is called when user logs out
        of the system. When called, function
        clears user's session and directs
        user to the login page.

        Parameter:
        none

        Output:
        url_for('index').
        """
        logoff()
        return redirect(url_for('index'))

    @app.route('/home')
    def home():
        """home

        Description:
        When called, functions directs user
        to the home screen if Username is
        not None. Otherwise, function directs
        user to login page.

        Parameter:
        none

        output:
        url_for('index').
        home.html.
        """
        if session.get('Username') is None:
            return redirect(url_for('index'))
        return render_template('home.html', username=session.get('Username'), role=session.get('Position'))

    # Checkout Section
    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        """checkout

        Description:
        When called, function directs user
        to the checkout-page if user's
        role-attribute meet the acceptable
        requirements. Otherwise, user is
        redirected to the home-page.

        Parameter:
        none

        Output:
        checkout.html
        url_for('home').
        """
        if ((session.get('Position') != 'Cashier') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Checkout'
        products_list = product_management_system.list_products()  # Use a different variable name

        return render_template('checkout.html', username=session.get('Username'), title=title,
                               products=products_list)

    @app.route('/finalize_checkout', methods=['POST'])
    def finalize_checkout():
        """finalize_checkout

        Description:
        When called, function retrieve sales data
        from user input, and uses that data to
        update the database, and email a copy of
        the receipt to the customer. The function
        also renders a form-template that displays the
        sales receipt allows the user to select "ok"
        Selecting "ok" will prompt the function to
        redirect user to url_for('checkout')

        Parameters:
        none

        Output:
        form_template.html
        url_for('checkout')
        """
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
        """inventory_management

        Description:
        When called, function directs user
        to inventory_management page if user's
        role-attribute meets acceptable requirements.
        Otherwise, user is redirected to the home page

        Parameters:
        none

        Output:
        inventory_management.html
        url_for('home')
        """
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
        """inventory_management_shelf_view

        Description:
        When called, function displays all shelves
        and their content to user. Function also allow
        user to filter which shelf to display.

        Parameter:
        none

        Output:
        dictionary: shelves
        inventory_management_template_shelf_view.html
        """
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
        """inventory_management_shelf

        Description:
        When called, function uses the
        shelf_id provided by user to search
        and display the content of the shelf
        with the provided shelf_id.

        Parameters:
        shelf_id

        Output:
        dictionary: shelf
        inventory_management_shelf_template.html
        """
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

        """add_shelf

        Description:
        When called, function checks session
        role-attribute for accessibility. If role
        is allowed access, function renders
        the form_template to allow for user to add
        shelves to the database.

        Parameter:
        none

        output:
        form_template.html."""

        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add Shelf'
        data = {}
        message = ''
        data["Message"] = message
        data["Action_URL"] = url_for('add_shelf')
        data["Cancel_URL"] = url_for('inventory_management_shelf_view')
        code = form_list.get_inventory_management_form('add_shelf', data)

        if request.method == 'POST':
            shelf_data = [request.form.get('shelf_id')]

            error = inventory_management_system.add_shelf(shelf_data)

            if error == 1:
                message = f'<h4>A shelf with the shelf_id {shelf_data[0]} already exists!</h4>'
                data = {"Message": message}
                code = form_list.get_inventory_management_form('add_shelf', data)
            elif error == 3:
                message = f'<h4>The length of the ShelfID must equal 7!</h4>'
                data = {"Message": message}
                code = form_list.get_inventory_management_form('add_shelf', data)
            elif error == 4:
                message = f'<h4>ShelfID must be begin with "WH" or "SF"!</h4>'
                data = {"Message": message}
                code = form_list.get_inventory_management_form('add_shelf', data)
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
        """delete_shelf

        Description:
        When called, function checks session
        role-attribute for accessibility. If role
        is allowed access, function renders
        the form_template to allow for user to
        delete shelves from database.

        Parameter:
        shelf_id

        output:
        form_template.html."""

        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Delete Shelf'
        message = ''
        data = inventory_management_system.search_shelves(shelf_id)[0]
        data["Message"] = message
        data["Action_URL"] = url_for('delete_shelf', shelf_id=data.get("ShelfID"))
        data["Cancel_URL"] = url_for('inventory_management_shelf_view')
        code = form_list.get_inventory_management_form('delete_shelf', data)

        if request.method == 'POST':

            error = inventory_management_system.delete_shelf(data.get("ShelfID"))

            if error == 1:
                message = f'<h4>The shelf with the ShelfID {shelf_id} does not exist!</h4>'
                data["Message"] = message
                code = form_list.get_inventory_management_form('delete_shelf', data)

            elif error == 2:
                message = (f'<h4>The shelf must be emptied before it can be deleted!</h4>'
                           f'<h4>Please move the remaining products to another shelf '
                           f'or remove the product record from the shelf if the quantity of the product is 0!</h4>')
                data["Message"] = message
                code = form_list.get_inventory_management_form('delete_shelf', data)

            else:
                code = (f'<h1>Delete Shelf {data.get("ShelfID")}</h1>'
                        f'<h3>This Shelf has been successfully deleted!</h3><br>'
                        f'<a href="{url_for('inventory_management_shelf_view')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/add_product_to_shelf', methods=['GET', 'POST'])
    def add_product_to_shelf():
        """add_product_to_shelf

        Description:
        When called, function checks session
        role-attribute for accessibility. If role
        is allowed access, function renders
        the form_template to allow for user to add
        product to shelves in the database.

        Parameter:
        none

        output:
        form_template.html."""

        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add Product'
        data = {}
        message = ''
        data["Message"] = message
        data["Action_URL"] = url_for('add_product_to_shelf')
        data["Cancel_URL"] = url_for('inventory_management')
        code = form_list.get_inventory_management_form('add_product_to_shelf', data)

        if request.method == 'POST':
            shelf_product_data = [request.form.get('shelf_id'), request.form.get('product_id')]

            error = inventory_management_system.add_product_to_shelf(shelf_product_data)

            if error == 1:
                message = f'<h4>The shelf with Shelf ID {shelf_product_data[0]} does not exist!</h4>'
                data = {"Message": message}
                code = form_list.get_inventory_management_form('add_product_to_shelf', data)
            elif error == 2:
                message = f'<h4>The product with the product ID {shelf_product_data[1]} does not exist!</h4>'
                data = {"Message": message}
                code = form_list.get_inventory_management_form('add_product_to_shelf', data)
            elif error == 3:
                message = f'<h4>The this product already has a record a warehouse shelf!</h4>'
                data = {"Message": message}
                code = form_list.get_inventory_management_form('add_product_to_shelf', data)
            elif error == 4:
                message = f'<h4>The this product already has a record a sales floor shelf!</h4>'
                data = {"Message": message}
                code = form_list.get_inventory_management_form('add_product_to_shelf', data)
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
        """delete_product_from_shelf

        Description:
        When called, function checks session
        role-attribute for accessibility. If role
        is allowed access, function renders
        the form_template to allow for user to
        delete product from shelves in the database.

        Parameter:
        product_id
        shelf_id

        output:
        form_template.html."""

        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Delete Product From Shelf'
        message = ''
        data = inventory_management_system.search_shelf_products_by_shelf('ProductID', product_id, shelf_id)[0]
        data["Message"] = message
        data["Action_URL"] = url_for('delete_product_from_shelf',
                                     product_id=data.get("ProductID"),
                                     shelf_id=data.get("ShelfID"))
        data["Cancel_URL"] = url_for("inventory_management")
        code = form_list.get_inventory_management_form('delete_product_from_shelf', data)

        if request.method == 'POST':

            error = inventory_management_system.delete_product_from_shelf(data.get('ProductID'), data.get('ShelfID'))

            if error == 1:
                message = f'<h4>The quantity of the Shelf_Product record must be 0!</h4>'
                data["Message"] = message
                code = form_list.get_inventory_management_form('delete_product_from_shelf', data)
            else:
                code = (f'<h1>Delete Product {data.get("ProductID")} From Shelf {data.get("ShelfID")}</h1>'
                        f'<h3>This Product has been successfully deleted from the shelf!</h3><br>'
                        f'<a href="{url_for('inventory_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/receive_order', methods=['GET', 'POST'])
    def receive_order():
        """receive_order

        Description:
        When called, function checks
        user role-attribute for accessibility.
        If user is allowed access, function
        directs user to the receive_order
        page. Otherwise, user is directed
        to the home page

        Parameter:
        none

        Output:
        receive_order.html
        url_for('home')
        """
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Receive Order'
        products_list = product_management_system.list_products()  # Use a different variable name

        return render_template('receive_order.html', username=session.get('Username'), title=title,
                               products=products_list)

    @app.route('/submit_received_order', methods=['POST'])
    def submit_order():
        """submit_order

        Description:
        When called, function parses received
        order from the front-end to the back-end,
        and renders the form_template to display
        the outcome of the transfer process.

        Parameter:
        none

        Output:
        form_template.html
        """
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
        """move_product

        Description:
        When called, function render the form
        template to allow user to move products
        between shelves in a warehouse or between
        shelves on the sales floor.

        Parameter:
        product_id
        shelf_id

        Output:
        int: error
        form_template.html
        """
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Move Product'
        data = {}
        message = ''
        data['Message'] = message
        data['ProductID'] = product_id
        data['ShelfID'] = shelf_id
        data["Action_URL"] = url_for('move_product',
                                     product_id=data.get('ProductID'),
                                     shelf_id=data.get('ShelfID'))
        data["Cancel_URL"] = url_for('inventory_management_shelf_view')
        code = form_list.get_inventory_management_form('move_product', data)

        if request.method == 'POST':
            shelf_product_info = [product_id, shelf_id, request.form.get('to_shelf_id')]

            error = inventory_management_system.move_product(shelf_product_info)

            if error == 1:
                message = f"<h4>The product with the product ID {shelf_product_info[0]} was not found!</h4>"
                data['Message'] = message
                code = form_list.get_inventory_management_form('move_product', data)
            elif error == 2:
                message = f"<h4>The shelf with the shelf ID {shelf_product_info[1]} was not found!</h4>"
                data['Message'] = message
                code = form_list.get_inventory_management_form('move_product', data)
            elif error == 3:
                message = f"<h4>The shelf with the shelf ID {shelf_product_info[2]} was not found!</h4>"
                data['Message'] = message
                code = form_list.get_inventory_management_form('move_product', data)
            elif error == 4:
                message = f"<h4>A product from a warehouse shelf can only be moved to another warehouse shelf!</h4>"
                data['Message'] = message
                code = form_list.get_inventory_management_form('move_product', data)
            elif error == 5:
                message = f"<h4>A product from a sales floor shelf can only be moved to another sales floor shelf!</h4>"
                data['Message'] = message
                code = form_list.get_inventory_management_form('move_product', data)
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
        """stock_product

        Description:
        When called, function renders form template
        to allow user to add received products
        to inventory.

        Parameter:
        product_id

        Output:
        form_template
        """
        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Stock Product'
        data = {}
        message = ''
        data['Message'] = message
        data['ProductID'] = product_id
        data["Action_URL"] = url_for('stock_product', product_id=data.get('ProductID'))
        data["Cancel_URL"] = url_for('inventory_management_shelf_view')
        code = form_list.get_inventory_management_form('stock_product', data)

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
        """report_waste

        Description:
        When called, function renders
        the form_template to allow
        user to report damage products.

        Parameter:
        product_id
        shelf_id

        Output:
        form_template."""

        if ((session.get('Position') != 'Warehouseman') and (session.get('Position') != 'Cashier/Warehouseman')
                and (session.get('Position') != 'Manager')):
            return redirect(url_for('home'))
        title = 'Report Waste'
        data = {}
        message = ''
        data['Message'] = message
        data['ProductID'] = product_id
        data['ShelfID'] = shelf_id
        data["Action_URL"] = url_for('report_waste',
                                     product_id=data.get('ProductID'),
                                     shelf_id=data.get("ShelfID"))
        data["Cancel_URL"] = url_for('inventory_management_shelf_view')
        code = form_list.get_inventory_management_form('report_waste', data)

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
        """product_management

        Description:
        When called, if user role-attribute
        is not manager, function redirects
        user to the home page. If user role
        is manager, function directs user to
        the product_management page.

        Parameter:
        none

        Output:
        product_management_template.html
        """
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
        """add_product

        Description:
        When called, function renders the form_template
        to allow user to add a new product to inventory.

        Parameters:
        none

        Output:
        form_template.html.
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add Product'
        data = {}
        message = ''
        data["Message"] = message
        data["Action_URL"] = url_for('add_product')
        data["Cancel_URL"] = url_for('product_management')
        code = form_list.get_product_management_form('add_product', data)

        if request.method == 'POST':
            product_data = [request.form.get('product_id'), request.form.get('product_name'), request.form.get('price')]

            error = product_management_system.add_product(product_data)

            if error == 1:
                message = f'<h4>A product with the product_id {product_data[0]} already exists!</h4>'
                data = {"Message": message}
                code = form_list.get_product_management_form('add_product', data)
            elif error == 2:
                message = f'<h4>A product with the product name {product_data[1]} already exists!</h4>'
                data = {"Message": message}
                code = form_list.get_product_management_form('add_product', data)
            elif error == 3:
                message = f'<h4>The ProductID is too long!</h6>'
                data = {"Message": message}
                code = form_list.get_product_management_form('add_product', data)
            elif error == 4:
                message = f'<h4>Product name is too long!</h4>'
                data = {"Message": message}
                code = form_list.get_product_management_form('add_product', data)
            elif error == 5:
                message = f'<h4>The price must be a number!</h4>'
                data = {"Message": message}
                code = form_list.get_product_management_form('add_product', data)

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
        """modify_product

        Description:
        When called, function renders the form_template
        to allow user to modify any attribute of an
        existing product.

        Parameter:
        product_id

        Output:
        form_template.
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Modify Product'
        message = ''
        data = product_management_system.get_product_data(product_id)
        data["Message"] = message
        data['ProductID'] = product_id
        data["Action_URL"] = url_for('modify_product', product_id=data.get("ProductID"))
        data["Cancel_URL"] = url_for("product_management")
        data["Delete_Product_URL"] = url_for("delete_product", product_id=data.get("ProductID"))
        code = form_list.get_product_management_form('modify_product', data)

        if request.method == 'POST':
            product_data = [product_id, request.form.get('product_name'), request.form.get('price')]

            error = product_management_system.modify_product(product_data)

            if error == 2:
                message = f'<h4>Product name already exists!</h4>'
                data["Message"] = message
                code = form_list.get_product_management_form('modify_product', data)
            elif error == 4:
                message = f'<h4>Product Name is too long!</h4>'
                data["Message"] = message
                code = form_list.get_product_management_form('modify_product', data)
            elif error == 5:
                message = f'<h4>Price must be a number!</h4>'
                data["Message"] = message
                code = form_list.get_product_management_form('modify_product', data)

            else:
                code = (f'<h1>Modify Product {product_data[0]} ({product_data[1]})</h1>'
                        f'<h3>This product has been successfully updated!</h3><br>'
                        f'<a href="{url_for('product_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/delete_product/<product_id>', methods=['GET', 'POST'])
    def delete_product(product_id):
        """delete_product

        Description:
        When called, function renders the form_template
        to allow user to delete product from inventory.

        Parameter:
        none

        Output:
        form_template.html
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Delete Product'
        message = ''
        data = product_management_system.get_product_data(product_id)
        data["Message"] = message
        data["Action_URL"] = url_for('delete_product', product_id=data.get("ProductID"))
        data["Cancel_URL"] = url_for("modify_product", product_id=data.get("ProductID"))
        code = form_list.get_product_management_form('delete_product', data)

        if request.method == 'POST':

            error = product_management_system.delete_product(data.get("ProductID"))

            if error == 1:
                message = f'<h4>The product {product_id} does not exist!</h4>'
                data["Message"] = message
                code = form_list.get_product_management_form('modify_product', data)
            elif error == 2:
                message = (f'<h4>The product {product_id} has shelf records! '
                           f'These records must first be deleted using the inventory management system!</h4>')
                data["Message"] = message
                code = form_list.get_product_management_form('modify_product', data)
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
        """user_management

        Description:
        When called, if user role is not manager,
        user is redirected to url_for('home').
        Otherwise, user is directed to the
        user_management page.

        Parameter:
        none

        Output:
        url_for('home')
        user_management_template.html.
        """
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
        """add_user

        Description:
        When called, if user is not manager, user is
        redirected to url_for('home'). Otherwise, function
        renders the form_template to allow user to
        add new users to the database.

        Parameter:
        none

        Output:
        url_for('home')
        form_template.
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Add User'
        data = {}
        message = ''
        data["Message"] = message
        data["Action_URL"] = url_for('add_user')
        data["Cancel_URL"] = url_for('user_management')
        code = form_list.get_user_management_form('add_user', data)

        if request.method == 'POST':
            user_data = [request.form.get('employee_id'), request.form.get('username'), request.form.get('first_name'),
                         request.form.get('last_name'), request.form.get('dob'), request.form.get('phone'),
                         request.form.get('role')]

            password = user_management_system.add_user(user_data)

            if password == 1:
                message = f'<h4>A user with the employee ID {user_data[2]} already exists!</h4>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
            elif password == 2:
                message = f'<h4>A user with the username {user_data[1]} already exists!</h4>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
            elif password == 3:
                message = f'<h4>The EmployeeID must be a number!</h6>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
            elif password == 4:
                message = f'<h4>Username is too long!</h4>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
            elif password == 5:
                message = f'<h4>First Name is too long!</h4>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
            elif password == 6:
                message = f'<h4>Last Name is too long!</h4>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
            elif password == 7:
                message = f'<h4>Invalid phone number!</h4>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
            elif password == 8:
                message = f'<h4>Invalid role!</h4>'
                data = {"Message": message}
                code = form_list.get_user_management_form('add_user', data)
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
        """modify_user

        Description:
        When called, if user is not manager, user
        is redirected to url_for('home'). Otherwise,
        function renders the form_template to allow
        user to modify existing user attributes.

        Parameters:
        employee_id

        Output:
        url_for('home')
        form_template
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Modify User'
        message = ''
        data = user_management_system.get_user_data(employee_id)
        data["Message"] = message
        data['EmployeeID'] = employee_id
        data["Action_URL"] = url_for('modify_user', employee_id=data.get("EmployeeID"))
        data["Cancel_URL"] = url_for("user_management")
        data["Reset_User_URL"] = url_for("reset_user", employee_id=data.get("EmployeeID"))
        data["Delete_User_URL"] = url_for("delete_user", employee_id=data.get("EmployeeID"))
        code = form_list.get_user_management_form('modify_user', data)

        if request.method == 'POST':
            user_data = [employee_id, request.form.get('username'), request.form.get('first_name'),
                         request.form.get('last_name'), request.form.get('phone'), request.form.get('role')]

            error = user_management_system.modify_user(user_data)

            if error == 4:
                message = f'<h4>Username is too long!</h4>'
                data["Message"] = message
                code = form_list.get_user_management_form('modify_user', data)
            elif error == 5:
                message = f'<h4>First Name is too long!</h4>'
                data["Message"] = message
                code = form_list.get_user_management_form('modify_user', data)
            elif error == 6:
                message = f'<h4>Last Name is too long!</h4>'
                data["Message"] = message
                code = form_list.get_user_management_form('modify_user', data)
            elif error == 7:
                message = f'<h4>Invalid phone number!</h4>'
                data["Message"] = message
                code = form_list.get_user_management_form('modify_user', data)
            elif error == 0:
                code = (f'<h1>Modify User {user_data[0]} ({user_data[1]})</h1>'
                        f'<h3>This user account has been successfully updated!</h3><br>'
                        f'<a href="{url_for('user_management')}">'
                        f'<input class="selection_button" type="button" value="OK">'
                        f'</a>')

        return render_template('form_template.html', username=session.get('Username'), title=title, code=code)

    @app.route('/delete_user/<int:employee_id>', methods=['GET', 'POST'])
    def delete_user(employee_id):
        """delete_user

        Description:
        When called, if user is not manager, user
        is redirected to url_for('home'). Otherwise,
        function renders the form_template to allow
        user to delete existing user from database.

        Parameters:
        employee_id

        Output:
        url_for('home')
        form_template
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Delete User'
        message = ''
        data = user_management_system.get_user_data(employee_id)
        data["Message"] = message
        data["Action_URL"] = url_for('delete_user', employee_id=data.get("EmployeeID"))
        data["Cancel_URL"] = url_for("modify_user", employee_id=data.get("EmployeeID"))
        code = form_list.get_user_management_form('delete_user', data)

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
        """reset_user

        Description:
        When called, if user is not manager,
        user is redirected to url_for('home').
        Otherwise, function renders the form_template
        to allow for user to reset user's account( in
        case of a lock out)

        Parameters:
        employee_id

        Output:
        url_for('home')
        form_template.html
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Reset User Password'
        message = ''
        data = user_management_system.get_user_data(employee_id)
        data["Message"] = message
        data["Action_URL"] = url_for('reset_user', employee_id=data.get("EmployeeID"))
        data["Cancel_URL"] = url_for("modify_user", employee_id=data.get("EmployeeID"))
        code = form_list.get_user_management_form('reset_user', data)

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
        """report_generation

        Description:
        When called, if user is not manager,
        user is redirected to url_for('home').
        Otherwise, function renders the form_template
        to allow for user to generate different
        types of data reports.

        Parameters:
        none

        Output:
        url_for('home')
        form_template.html
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Report Generation'
        data = {}
        message = ''
        data["Message"] = message
        data["Inventory_Report_URL"] = url_for('inventory_report')
        data["Sales_Report_URL"] = url_for('sales_report')
        data["Waste_Report_URL"] = url_for('waste_report')
        code = form_list.get_report_generator_form('report_main', data)
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/report_generation/inventory_report')
    def inventory_report():
        """inventory_report

        Description:
        When called, if user is not manager,
        user is redirected to url_for('home').
        Otherwise, function renders the form_template
        to allow for user to generate inventory
        related reports.

        Parameters:
        none

        Output:
        url_for('home')
        form_template.html
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Inventory Report'
        data = {"Total_Inventory_Report_URL": url_for('total_inventory_report'),
                "Shelf_Inventory_Report_URL": url_for('shelf_inventory_report'),
                "Cancel_URL": url_for('report_generation')}
        code = form_list.get_report_generator_form('inventory_report', data)
        return render_template('form_template.html',
                               username=session.get('Username'), title=title, code=code)

    @app.route('/report_generation/inventory_report/total_inventory')
    def total_inventory_report():
        """total_inventory_report

        Description:
        When called, if user is not manager,
        user is redirected to url_for('home').
        Otherwise, function generates and
        display a report of all products and their
         total quantity in the database
        in a pdf file.

        Parameters:
        none

        Output:
        url_for('home')
        url_for('report_generation')
        File: pdf
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))

        report_info = {'Report_Type': 'Inventory', 'EmployeeID': session.get('EmployeeID'), 'Scope': 'Total_Inventory'}

        report_generation_system.inventory_report(report_info)

        return redirect(url_for('report_generation'))

    @app.route('/report_generation/inventory_report/shelf_inventory')
    def shelf_inventory_report():
        """shelf_inventory_report

        Description:
        When called, if user is not manager,
        user is redirected to url_for('home').
        Otherwise, function generates and
        display a report of all products
        in each shelf in the database
        in a pdf file.

        Parameters:
        none

        Output:
        url_for('home')
        url_for('report_generation')
        File: pdf
        """

        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))

        report_info = {'Report_Type': 'Inventory', 'EmployeeID': session.get('EmployeeID'), 'Scope': 'Shelf_Inventory'}

        report_generation_system.generate_report(report_info)

        return redirect(url_for('report_generation'))

    @app.route('/report_generation/sales_report', methods=['GET', 'POST'])
    def sales_report():
        """sales_report

        Description:
        When called, if user is not manager,
        user is redirected to url_for('home').
        Otherwise, function renders the form
        template to allow user to enter the values
        needed for the generation of a sales report.

        Parameters:
        none

        Output:
        url_for('home')
        form_template.html
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Sales Report'
        report_info = {}
        data = {}
        message = ''
        data["Message"] = message
        data["Action_URL"] = url_for('sales_report')
        data["Cancel_URL"] = url_for('report_generation')
        code = form_list.get_report_generator_form('sales_report', data)

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
        """sales_report

        Description:
        When called, if user is not manager,
        user is redirected to url_for('home').
        Otherwise, function renders the form
        template to allow user to enter the values
        needed for the generation of a waste report.

        Parameters:
        none

        Output:
        url_for('home')
        form_template.html
        """
        if session.get('Position') != 'Manager':
            return redirect(url_for('home'))
        title = 'Waste Report'
        report_info = {}
        data = {}
        message = ''
        data["Message"] = message
        data["Action_URL"] = url_for('waste_report')
        data["Cancel_URL"] = url_for('report_generation')
        code = form_list.get_report_generator_form('waste_report', data)

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
    """create_app

    Description:
    When called, function sets up and configure
    the Flask application instance.

    Parameters:
    none

    Output:
    object: flask app.
    """
    flask_app = Flask(__name__)
    flask_app.secret_key = secrets.token_hex(24)
    flask_app.static_folder = 'static'

    # Configure database creation
    db_portal.create_database()

    # Other configurations
    configure_routes(flask_app)

    return flask_app


# Allows the user to login
def login(username, password):
    """login

    Description:
    Function is used to verify user
    credentials during login. If user number
    of login trials are within an acceptable
    value and  user credentials are validated,
    user session object is created and number
    of login trials is adjusted to zero.
    Otherwise, function return an
    error code, and increment the
    number of login trials.

    Parameter:
    username
    password

    Output:
    int: error code
    """
    # Constant
    param = (username,)

    # Check if the username exists
    query = "SELECT COUNT(*) FROM Users WHERE Username = ?"
    user_exists = db_portal.pull_data(query, param)[0][0]

    if user_exists == 1:
        # Get the number of tries for the user
        query = "SELECT Number_Of_Tries FROM Users WHERE Username = ?"
        num_tries = db_portal.pull_data(query, param)[0][0]

        if num_tries <= 3:
            # Get the stored password for the user
            query = "SELECT Password FROM Users WHERE Username = ?"
            stored_password = db_portal.pull_data(query, param)[0][0]

            # Hash the provided password (assuming it's SHA256 hashed in the database)
            hash_pass = sha256_crypt.verify(password, stored_password)

            # Check if the provided password matches the stored password
            if hash_pass is True:
                query = "SELECT EmployeeID, Position, First_Name, Last_Name, First_Time FROM Users WHERE Username = ?"
                user_info = db_portal.pull_data(query, param)[0]
                session['EmployeeID'] = user_info[0]
                session['Username'] = username
                session['Position'] = user_info[1]
                session['First_Name'] = user_info[2]
                session['Last_Name'] = user_info[3]
                session['First_Time'] = user_info[4]

                # Reset the number of tries
                db_portal.push_data("UPDATE Users SET Number_Of_Tries = 0 WHERE Username = ?", param)

                return 0
            else:
                # Password does not match, increment the number of tries
                db_portal.push_data("UPDATE Users SET Number_Of_Tries = Number_Of_Tries + 1 "
                                    "WHERE Username = ?", param)

                return 1
        else:
            # User has exceeded the maximum number of tries
            return 2

    else:
        # Username does not exist
        return 1


# Change password
def create_password_function(employee_id, password1, password2):
    """create_password_function

    Description:
    Function is called when user create
    a new password and click submit. Function
    verifies if password meets complexity,
    minimum length, and ensures that both passwords
    match. If new password meets all criteria, user
    password is updated in the database, and user
    number of trials is set to zero.

    Parameter:
    employee_id
    password1(current password)
    password2(new password)

    Output:
    int: error code
    user password update
    """
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

    script_one = f"UPDATE Users SET Password = ? WHERE EmployeeID = ?;"
    param_one = (hashed_password, employee_id)
    db_portal.push_data(script_one, param_one)

    script_two = f"UPDATE Users SET First_Time = 0 WHERE EmployeeID = ?;"
    param_two = (employee_id,)
    db_portal.push_data(script_two, param_two)

    return 0


# Logs off the user by clearing the session data
def logoff():
    """logoff

    Description:
    Clears user session

    Parameter:
    none

    Output:
    clears user session"""
    session.clear()


if __name__ == '__main__':
    app = create_app()
    app.run()
