import os
import sqlite3
import subprocess
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter


def generate_filename():
    now = datetime.now()
    formatted_datetime = now.strftime('%Y%m%d%H%M%S')
    nanoseconds = now.strftime('%f')
    nanoseconds = int(nanoseconds) * 1000

    result = 'temp/Report-' + formatted_datetime + f"{nanoseconds:09d}" + ".pdf"
    return result


class ReportGenerator:
    # The UserManagement constructor
    def __init__(self, db_name):
        self.db_name = db_name

    def generate_report(self, report_info):
        """ Generate a report. Accepts a dictionary with the following
        parameters: Report_Type, Reason, Scope, Metric, Period, From_Date,
        and To_Date"""
        report_type = report_info.get('Report_Type')
        period = report_info.get('Period')

        # Define the SQL query based on the selected time interval
        if period == "yearly":
            group_by_sql = "strftime('%Y', Date)"
        elif period == "monthly":
            group_by_sql = "strftime('%Y-%m', Date)"
        elif period == "weekly":
            group_by_sql = "strftime('%Y-%W', Date)"
        elif period == "daily":
            group_by_sql = "strftime('%Y-%m-%d', Date)"
        else:
            print("Invalid group_by option")
            return 1

        if report_type == 'Sales':
            return self.sales_report(report_info, group_by_sql)

        elif report_type == 'Inventory':
            return self.inventory_report(report_info)

        elif report_type == 'Waste':
            return self.waste_report(report_info, group_by_sql)

        else:
            return 2

    def sales_report(self, report_info, group_by_sql):
        user_id = report_info.get('UserID')
        report_type = report_info.get('Report_Type')
        start_date = report_info.get('From_Date')
        end_date = report_info.get('To_Date')
        scope = report_info.get("Scope")
        metric = report_info.get("Metric")
        query = ''

        if scope == 'Total':
            if metric == 'Quantity':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                    SELECT {group_by_sql} AS Period,
                        COUNT(*) AS Quantity
                    FROM Sales
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    GROUP BY {group_by_sql}
                    ORDER BY Period
                    """
            elif metric == 'Dollar Amount':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                   SELECT {group_by_sql} AS Period,
                          SUM(Total_Price) AS Total_Price
                   FROM Sales
                   WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                   GROUP BY {group_by_sql}
                   ORDER BY Period
                   """
        elif scope == 'Individual Product':
            product_id = report_info.get('ProductID')

            if not self.check_product_exists(product_id):
                return 3

            product_id = report_info.get('ProductID')
            if metric == 'Quantity':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                    SELECT {group_by_sql} AS Period,
                        SUM(Quantity) AS Quantity
                    FROM Sales_Products
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    AND ProductID = '{product_id}'
                    GROUP BY {group_by_sql}
                    ORDER BY Period
                    """
            elif metric == 'Dollar Amount':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                   SELECT {group_by_sql} AS Period,
                          SUM(Quantity * Unit_Price) AS Total_Price
                   FROM Sales_Products
                   WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                   AND ProductID = '{product_id}'
                   GROUP BY {group_by_sql}
                   ORDER BY Period
                   """

        # Execute the query
        rows = self.get_table_data(query)

        print(rows)

        self.generate_pdf_report(rows, user_id, report_type)

    def inventory_report(self, report_info):
        user_id = report_info.get('UserID')
        report_type = report_info.get('Report_Type')
        query = ''

        if report_info.get('Scope') == 'Total_Inventory':
            query = ('SELECT ProductID, Product_Name, Total_In_Stock '
                     'FROM Products ORDER BY ProductID')
        elif report_info.get('Scope') == 'Shelf_Inventory':
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"ORDER BY Shelf_Product.ShelfID;")

        # Execute the query
        rows = self.get_table_data(query)

        print(rows)

        self.generate_pdf_report(rows, user_id, report_type)

    def waste_report(self, report_info, group_by_sql):
        user_id = report_info.get('UserID')
        report_type = report_info.get('Report_Type')
        start_date = report_info.get('From_Date')
        end_date = report_info.get('To_Date')
        scope = report_info.get('Scope')
        metric = report_info.get('Metric')
        reason_code = report_info.get('ReasonCode')
        reason = ''
        query = ''

        if reason_code != 'All':
            reason = f"AND ReasonCode = '{reason_code}' "

        if scope == 'Total':
            if metric == 'Quantity':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                    SELECT {group_by_sql} AS Period,
                        COUNT(*) AS Quantity
                    FROM Waste_Reports
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    GROUP BY {group_by_sql}
                    ORDER BY Period
                    """
            elif metric == 'Dollar Amount':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                   SELECT {group_by_sql} AS Period,
                          SUM(Quantity * Unit_Price) AS Total_Price
                   FROM Waste_Reports
                   WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                   GROUP BY {group_by_sql}
                   ORDER BY Period
                   """
        elif scope == 'Individual Product':
            product_id = report_info.get('ProductID')

            if not self.check_product_exists(product_id):
                return 3

            if metric == 'Quantity':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                    SELECT {group_by_sql} AS Period,
                        SUM(Quantity) AS Quantity
                    FROM FROM Waste_Reports
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    AND ProductID = '{product_id}'
                    {reason}
                    GROUP BY {group_by_sql}
                    ORDER BY Period
                    """
            elif metric == 'Dollar Amount':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                   SELECT {group_by_sql} AS Period,
                          SUM(Quantity * Unit_Price) AS Total_Price
                   FROM FROM Waste_Reports
                   WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                   AND ProductID = '{product_id}'
                   {reason}
                   GROUP BY {group_by_sql}
                   ORDER BY Period
                   """

        # Execute the query
        rows = self.get_table_data(query)

        print(rows)

        self.generate_pdf_report(rows, user_id, report_type)

    def generate_pdf_report(self, rows, user_id, report_type):
        # Create DataFrame from the query result
        df = pd.DataFrame(rows)
        filename = generate_filename()

        first_name = self.get_table_data(f"SELECT First_Name FROM Users WHERE UserID = '{user_id}';")
        last_name = self.get_table_data(f"SELECT Last_Name FROM Users WHERE UserID = '{user_id}';")

        # Create PDF report
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # Add header to the PDF
        styles = getSampleStyleSheet()
        header_text = f"Alpha Store - {report_type} Report"
        generated_by_text = f"Generated By: {first_name} {last_name}"
        header = Paragraph(header_text, styles['Heading1'])
        generated_by = Paragraph(generated_by_text, styles['Heading1'])
        header_table = Table([[header, generated_by]], colWidths=[400, 200])
        elements.append(header_table)

        # Add table to the PDF
        table_data = [df.columns.tolist()] + df.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                   ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                   ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                   ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                   ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                   ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                   ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)

        # Build PDF report
        doc.build(elements)

        # Open the generated PDF in a subprocess
        subprocess.Popen(['start', '', filename], shell=True)

        # Wait for the subprocess to finish (i.e., PDF viewer is closed)
        p = subprocess.Popen(['start', '', filename], shell=True)
        p.communicate()

        # Delete the PDF file after it has been closed
        os.remove(filename)

        return filename

    def check_product_exists(self, product):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        query = f"SELECT COUNT(*) FROM Product WHERE ProductID = '{product}'"
        c.execute(query)
        product_exists = c.fetchone()[0]
        conn.close()

        if product_exists == 0:
            return False
        return True

    def get_table_data(self, query):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
