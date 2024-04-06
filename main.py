# Alpha Store Management System

import sqlite3
import os
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import sha256_crypt
from product_cache import ProductCache


def configure_routes(app, database_name):
    # Variables
    product_cache = ProductCache(database_name)

    # Index (Login) page
    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/product_management')
    def product_management():
        products = product_cache.get_product_data()
        return render_template('product_list.html', products)


# Set up the Flask app
def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(24)
    app.static_folder = 'static'

    # Configure database creation
    database_name = 'alpha_store.sqlite3'
    sql_script_file = 'static/Create_tables.sql'
    create_database(database_name, sql_script_file)



    # Other configurations
    configure_routes(app, database_name)

    return app


# Check if there exists a database. If not, create one.
def create_database(db_name, sql_file):
    # Check if the database file exists
    if not os.path.exists(db_name):
        # If the database file doesn't exist, create a new one
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Read SQL commands from the SQL file and execute them
        with open(sql_file, 'r') as sql_file:
            sql_commands = sql_file.read()
            cursor.executescript(sql_commands)

        # Commit changes and close the connection
        conn.commit()
        conn.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = create_app()
    app.run()
