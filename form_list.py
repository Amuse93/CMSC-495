class FormList:

    # Provides HTML for various forms
    def get_inventory_management_form(self, form_type, data):
        if form_type == 'add_shelf':
            add_shelf = (f'<h1>Add Shelf</h1>'
                         f'{data.get("Message")}'
                         f'<form action="{data.get("Action_URL")}" id="add_shelf" method="post">'
                         f'<label for="shelf_id">ShelfID: </label>'
                         f'<input type="text" id="shelf_id" name="shelf_id" size="25" autocomplete="off" required>'
                         f'<br>'
                         f'<br>'
                         f'<br>'
                         f'<div>'
                         f'<input class="selection_button" type="submit" value="OK">'
                         f'<a href="{data.get("Cancel_URL")}">'
                         f'<input class="selection_button" type="button" value="Cancel">'
                         )
            return add_shelf

        if form_type == 'delete_shelf':
            delete_shelf = (f'<h1>Delete Shelf {data.get("ShelfID")}</h1>'
                            f'{data.get("Message")}'
                            f'<form action="{data.get("Action_URL")}" id="delete_shelf" method="post">'
                            f'<h3>Are you sure you want to delete this shelf?</h3>'
                            f'<br>'
                            f'<div>'
                            f'<input class="selection_button" type="submit" value="OK">'
                            f'<a href="{data.get("Cancel_URL")}">'
                            f'<input class="selection_button" type="button" value="Cancel">'
                            f'</a>'
                            f'</div>'
                            f'</form>'
                            )
            return delete_shelf

        if form_type == 'add_product_to_shelf':
            add_product_to_shelf = (f'<h1>Add Product To Shelf</h1>'
                                    f'{data.get("Message")}'
                                    f'<form action="{data.get("Action_URL")}" '
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
                                    f'<a href="{data.get("Cancel_URL")}">'
                                    f'<input class="selection_button" type="button" value="Cancel">'
                                    )
            return add_product_to_shelf

        if form_type == 'delete_product_from_shelf':
            delete_product_from_shelf = (
                f'<h1>Delete Product {data.get("ProductID")} From Shelf {data.get("ShelfID")}</h1>'
                f''
                f'{data.get("Message")}'
                f'<form action="{data.get("Action_URL")}" '
                f'id="delete_product_from_shelf" method="post">'
                f'<h3>Are you sure you want to delete this Product_Shelf record?</h3>'
                f'<br>'
                f'<div>'
                f'<input class="selection_button" type="submit" value="OK">'
                f'<a href="{data.get("Cancel_URL")}">'
                f'<input class="selection_button" type="button" value="Cancel">'
                f'</a>'
                f'</div>'
                f'</form>'
            )
            return delete_product_from_shelf

        if form_type == 'move_product':
            move_product = (f'<h1>Move Product {data.get('ProductID')} From Shelf {data.get('ShelfID')} To:</h1>'
                            f'{data.get("Message")}'
                            f'<form action="{data.get("Action_URL")}" '
                            f'id="move_product" method="post">'
                            f'<label for="to_shelf_id">ShelfID: </label>'
                            f'<input type="text" id="to_shelf_id" name="to_shelf_id" size="25" '
                            f'autocomplete="off" required>'
                            f'<br>'
                            f'<br>'
                            f'<br>'
                            f'<div>'
                            f'<input class="selection_button" type="submit" value="OK">'
                            f'<a href="{data.get("Cancel_URL")}">'
                            f'<input class="selection_button" type="button" value="Cancel">'
                            )

            return move_product

        if form_type == 'stock_product':
            stock_product = (f'<h1>Stock Product {data.get('ProductID')}</h1>'
                             f'{data.get("Message")}'
                             f'<form action="{data.get("Action_URL")}" '
                             f'id="move_product" method="post">'
                             f'<label for="quantity">Quantity: </label>'
                             f'<input type="text" id="quantity" name="quantity" size="25" autocomplete="off" required>'
                             f'<br>'
                             f'<br>'
                             f'<br>'
                             f'<div>'
                             f'<input class="selection_button" type="submit" value="OK">'
                             f'<a href="{data.get("Cancel_URL")}">'
                             f'<input class="selection_button" type="button" value="Cancel">'
                             )

            return stock_product

        if form_type == 'report_waste':
            report_waste = (
                f'<h1>Report Waste for Product {data.get('ProductID')} From Shelf {data.get("ShelfID")}</h1>'
                f'{data.get("Message")}'
                f'<form action="{data.get("Action_URL")}" '
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
                f'<a href="{data.get("Cancel_URL")}">'
                f'<input class="selection_button" type="button" value="Cancel">'
                f'</form>'
            )

            return report_waste

    def get_product_management_form(self, form_type, data):
        if form_type == 'add_product':
            add_product = (f'<h1>Add Product</h1>'
                           f'{data.get("Message")}'
                           f'<form action="{data.get("Action_URL")}" id="add_product" method="post">'
                           f'<label for="product_id">ProductID: </label>'
                           f'<input type="text" id="product_id" name="product_id" size="25" '
                           f'autocomplete="off" required>'
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
                           f'<a href="{data.get("Cancel_URL")}">'
                           f'<input class="selection_button" type="button" value="Cancel">'
                           f'</a>'
                           f'</div>'
                           f'</form>'
                           )
            return add_product

        if form_type == 'modify_product':
            modify_product = (f'<h1>Modify Product {data.get("ProductID")} ({data.get("Product_Name")})</h1>'
                              f'{data.get("Message")}'
                              f'<form action="{data.get("Action_URL")}" '
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
                              f'<a href="{data.get("Cancel_URL")}">'
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
                              f'<a href="{data.get("Delete_Product_URL")}">'
                              f'<input class="selection_button" type="button" value="Delete">'
                              f'</a>'
                              f'</div>'
                              )
            return modify_product

        if form_type == 'delete_product':
            delete_product = (f'<h1>Delete Product {data.get("ProductID")} ({data.get("Product_Name")})</h1>'
                              f'<form action="{data.get("Action_URL")}" '
                              f'id="delete_product" method="post">'
                              f'<h3>Are you sure you want to delete this product?</h3>'
                              f'<br>'
                              f'<div>'
                              f'<input class="selection_button" type="submit" value="OK">'
                              f'<a href="{data.get("Cancel_URL")}">'
                              f'<input class="selection_button" type="button" value="Cancel">'
                              f'</a>'
                              f'</div>'
                              f'</form>'
                              )

            return delete_product

    def get_user_management_form(self, form_type, data):
        if form_type == 'add_user':
            add_user = (f'<h1>Add User</h1>'
                        f'{data.get("Message")}'
                        f'<form action="{data.get("Action_URL")}" id="add_user" method="post">'
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
                        f'<a href="{data.get("Cancel_URL")}">'
                        f'<input class="selection_button" type="button" value="Cancel">'
                        f'</a>'
                        f'</div>'
                        f'</form>'
                        )
            return add_user

        if form_type == 'modify_user':
            modify_user = (f'<h1>Modify User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                           f'{data.get("Message")}'
                           f'<form action="{data.get("Action_URL")}" '
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
                            f'<a href="{data.get("Cancel_URL")}">'
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
                            f'<a href="{data.get("Reset_User_URL")}">'
                            f'<input class="selection_button" type="button" value="Reset Password">'
                            f'</a>'
                            f'<a href="{data.get("Delete_User_URL")}">'
                            f'<input class="selection_button" type="button" value="Delete">'
                            f'</a>'
                            f'</div>'
                            )
            return modify_user

        if form_type == 'delete_user':
            delete_user = (f'<h1>Delete User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                           f'<form action="{data.get("Action_URL")}" '
                           f'id="delete_user" method="post">'
                           f'<h3>Are you sure you want to delete this account?</h3>'
                           f'<br>'
                           f'<div>'
                           f'<input class="selection_button" type="submit" value="OK">'
                           f'<a href="{data.get("Cancel_URL")}">'
                           f'<input class="selection_button" type="button" value="Cancel">'
                           f'</a>'
                           f'</div>'
                           f'</form>'
                           )

            return delete_user

        if form_type == 'reset_user':
            reset_user = (f'<h1>Reset User {data.get("EmployeeID")} ({data.get("Username")})</h1>'
                          f'<form action="{data.get("Action_URL")}" '
                          f'id="reset_user" method="post">'
                          f'<h3>Are you sure you want to reset the password for this account?</h3>'
                          f'<br>'
                          f'<div>'
                          f'<input class="selection_button" type="submit" value="OK">'
                          f'<a href="{data.get("Cancel_URL")}">'
                          f'<input class="selection_button" type="button" value="Cancel">'
                          f'</a>'
                          f'</div>'
                          f'</form>'
                          )

            return reset_user

    def get_report_generator_form(self, form_type, data):
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
                           f'<a href="{data.get("Inventory_Report_URL")}"><button>Inventory</button></a>'
                           f'<a href="{data.get("Sales_Report_URL")}"><button>Sales</button></a>'
                           f'<a href="{data.get("Waste_Report_URL")}"><button>Waste</button></a>'
                           )
            return report_main

        if form_type == 'inventory_report':
            inventory_report = (f'<h1>Select a Scope</h1>'
                                f'<a href="{data.get("Total_Inventory_Report_URL")}">'
                                f'<button>Total Inventory On Hand</button>'
                                f'</a>'
                                f'<a href="{data.get("Shelf_Inventory_Report_URL")}">'
                                f'<button>Shelf Inventory</button>'
                                f'</a>'
                                f'<a href="{data.get("Cancel_URL")}">'
                                f'<button>Cancel</button>'
                                f'</a>'
                                )
            return inventory_report

        if form_type == 'sales_report':
            sales_report = (f'<h1>Sales Report</h1>'
                            f'{data.get("Message")}'
                            f'<form action="{data.get("Action_URL")}" id="sales_report" method="post">'
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
                            f'<a href="{data.get("Cancel_URL")}">'
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
                            f'<form action="{data.get("Action_URL")}" id="waste_report" method="post">'
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
                            f'<a href="{data.get("Cancel_URL")}">'
                            f'<input class="selection_button" type="button" value="Cancel">'
                            f'</a>'
                            f'</div>'
                            f'</form>'
                            f'{script}'
                            )
            return waste_report

        return 0
