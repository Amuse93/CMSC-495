import os
import io
import subprocess
import time
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
plt.switch_backend('agg')


def generate_filename():
    now = datetime.now()
    formatted_datetime = now.strftime('%Y%m%d%H%M%S')
    nanoseconds = now.strftime('%f')
    nanoseconds = int(nanoseconds) * 1000

    result = "Report-" + formatted_datetime + f"{nanoseconds:09d}" + ".pdf"
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

        if report_type == 'Sales':
            return self.sales_report(report_info)

        elif report_type == 'Inventory':
            return self.inventory_report(report_info)

        elif report_type == 'Waste':
            return self.waste_report(report_info)

        else:
            return 2

    def sales_report(self, report_info):

        period = report_info.get('Period')

        # Define the SQL query based on the selected time interval
        if period == "Yearly":
            group_by_sql = "strftime('%Y', Date)"
        elif period == "Monthly":
            group_by_sql = "strftime('%Y-%m', Date)"
        elif period == "Weekly":
            group_by_sql = "strftime('%Y-%W', Date)"
        elif period == "Daily":
            group_by_sql = "strftime('%Y-%m-%d', Date)"
        else:
            return 1

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
                        SUM(Sales_Products.Product_Quantity) AS Quantity
                    FROM Sales
                    JOIN Sales_Products ON Sales.SaleID = Sales_Products.SaleID
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    GROUP BY {group_by_sql}
                    ORDER BY Period
                    """
            elif metric == 'Dollar_Amount':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                   SELECT {group_by_sql} AS Period,
                          SUM(Total_Price) AS Total_Price
                   FROM Sales
                   WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                   GROUP BY {group_by_sql}
                   ORDER BY Period
                   """
        elif scope == 'Individual_Product':
            product_id = report_info.get('ProductID')

            if not self.check_product_exists(product_id):
                return 3

            product_id = report_info.get('ProductID')
            if metric == 'Quantity':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                    SELECT {group_by_sql} AS Period,
                        SUM(Sales_Products.Product_Quantity) AS Quantity
                    FROM Sales
                    JOIN Sales_Products ON Sales.SaleID = Sales_Products.SaleID
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    AND ProductID = '{product_id}'
                    GROUP BY {group_by_sql}
                    ORDER BY Period
                    """
            elif metric == 'Dollar_Amount':
                # Construct the SQL query to retrieve total price grouped by time interval
                query = f"""
                    SELECT {group_by_sql} AS Period,
                        SUM(Sales_Products.Product_Quantity * Sales_Products.Unit_Price) AS Total_Price
                    FROM Sales
                    JOIN Sales_Products ON Sales.SaleID = Sales_Products.SaleID
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    AND ProductID = '{product_id}'
                    GROUP BY {group_by_sql}
                    ORDER BY Period
                    """

        # Execute the query
        rows = self.get_table_data(query)
        periods = []
        amounts = []

        for row in rows:
            periods.append(row[0])
            amounts.append(row[1])

        data = {
            'Period': periods,
            'Amount': amounts
        }

        self.generate_pdf_report(data, report_info)

        return 0

    def inventory_report(self, report_info):
        data = {}

        if report_info.get('Scope') == 'Total_Inventory':
            query = ('SELECT ProductID, Product_Name, Total_In_Stock '
                     'FROM Product ORDER BY ProductID')

            # Execute the query
            rows = self.get_table_data(query)
            product_ids = []
            product_names = []
            total_in_stock = []

            for row in rows:
                product_ids.append(row[0])
                product_names.append(row[1])
                total_in_stock.append(row[2])

            data = {
                'ProductID': product_ids,
                'Product Name': product_names,
                'Total In Stock': total_in_stock
            }

        elif report_info.get('Scope') == 'Shelf_Inventory':
            query = (
                f"SELECT Shelf_Product.ProductID, Product.Product_Name, Shelf_Product.Quantity, Shelf_Product.ShelfID "
                f"FROM Shelf_Product "
                f"JOIN Product ON Shelf_Product.ProductID = Product.ProductID "
                f"ORDER BY Shelf_Product.ShelfID;")

            # Execute the query
            rows = self.get_table_data(query)
            product_ids = []
            product_names = []
            quantities = []
            shelf_ids = []

            for row in rows:
                product_ids.append(row[0])
                product_names.append(row[1])
                quantities.append(row[2])
                shelf_ids.append(row[3])

            data = {
                'ProductID': product_ids,
                'Product Name': product_names,
                'Quantity': quantities,
                'ShelfID': shelf_ids
            }

        self.generate_pdf_report(data, report_info)

        return 0

    def waste_report(self, report_info):

        period = report_info.get('Period')

        # Define the SQL query based on the selected time interval
        if period == "Yearly":
            group_by_sql = "strftime('%Y', Date)"
        elif period == "Monthly":
            group_by_sql = "strftime('%Y-%m', Date)"
        elif period == "Weekly":
            group_by_sql = "strftime('%Y-%W', Date)"
        elif period == "Daily":
            group_by_sql = "strftime('%Y-%m-%d', Date)"
        else:
            return 1

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
                        SUM(Quantity) AS Quantity
                    FROM Waste_Reports
                    WHERE Date BETWEEN '{start_date}' AND '{end_date}'
                    {reason}
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
                   {reason}
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
        periods = []
        amounts = []

        for row in rows:
            periods.append(row[0])
            amounts.append(row[1])

        data = {
            'Period': periods,
            'Amount': amounts
        }

        self.generate_pdf_report(data, report_info)

        return 0

    def generate_pdf_report(self, rows, report_info):
        report_title_text = ''
        report_title_text2 = ''

        employee_id = report_info.get('EmployeeID')
        report_type = report_info.get('Report_Type')
        scope = report_info.get('Scope')
        product_id = ''
        start_date = ''
        metric = ''
        end_date = ''
        reason_code = ''
        if report_type != 'Inventory':
            start_date = report_info.get('From_Date')
            end_date = report_info.get('To_Date')
            metric = report_info.get('Metric')
            reason_code = report_info.get('ReasonCode')
            if scope == "Individual_Product":
                product_id = report_info.get('ProductID')

        # Constants
        padding = Spacer(1, 24)

        # Get current datetime
        current_datetime = datetime.now()

        # Format datetime into the desired format
        formatted_datetime = current_datetime.strftime("%B %d, %Y at %I:%M %p")
        datetime_text = f"Generated on {formatted_datetime}"

        # Create DataFrame from the query result
        df = pd.DataFrame(rows)
        directory = 'temp'
        filename = generate_filename()  # You need to define this function
        full_path = os.path.join(directory, filename)
        temp_path = os.path.join(directory, 'test.pdf')

        # Fetch employee's first and last name from the database
        query = f"SELECT First_Name, Last_Name FROM Users WHERE EmployeeID = '{employee_id}';"
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                first_name, last_name = result
            else:
                first_name, last_name = "Unknown", "Unknown"

        # Create PDF report
        doc = SimpleDocTemplate(full_path, pagesize=letter,
                                topMargin=inch / 2,
                                bottomMargin=inch / 2,
                                leftMargin=inch / 2,
                                rightMargin=inch / 2)
        elements = []

        # Add Report Title
        if report_type == 'Inventory':
            if scope == 'Total_Inventory':
                report_title_text = f"Alpha Store - {report_type} Report"
                report_title_text2 = f"Total Inventory"
            elif scope == 'Shelf_Inventory':
                report_title_text = f"Alpha Store - {report_type} Report"
                report_title_text2 = f"Shelf Inventory"

        elif report_type == 'Sales':
            if scope == 'Total':
                report_title_text = f"Alpha Store - {report_type} Report"
                report_title_text2 = f"Total {report_type} From {start_date} To {end_date}"
            elif scope == 'Individual_Product':
                report_title_text = f"Alpha Store - {report_type} Report"
                report_title_text2 = f"{product_id} Sales From {start_date} To {end_date}"

        elif report_type == 'Waste':
            if scope == 'Total':
                report_title_text = f"Alpha Store - {reason_code} {report_type} Report"
                report_title_text2 = f"Total {report_type} From {start_date} To {end_date}"
            elif scope == 'Individual_Product':
                report_title_text = f"Alpha Store - {reason_code} {report_type} Report"
                report_title_text2 = f"{product_id} Sales From {start_date} To {end_date}"

        # Define a paragraph style
        title_style = ParagraphStyle(
            name='TableLabel',
            fontName='Helvetica-Bold',
            fontSize=24,
            alignment=TA_CENTER,
        )

        # Create paragraphs for each part of the title text
        report_title_part1 = Paragraph(report_title_text, title_style)
        report_title_part2 = Paragraph(report_title_text2, title_style)

        datetime_generated = Paragraph(datetime_text + f" by {first_name} {last_name}", ParagraphStyle(
            name='datetime_generated', alignment=TA_CENTER))
        elements.extend([report_title_part1, padding, report_title_part2, padding])
        elements.extend([datetime_generated, padding])

        # Add text labels
        table_label = Paragraph(f"Table 1: {report_type} Data", ParagraphStyle(name='TableLabel'))

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
        table.hAlign = 'LEFT'

        elements.extend([table_label, padding, table, padding])

        if report_type == 'Sales' or report_type == 'Waste':
            # Add plot to the PDF
            figure_label = Paragraph(f"Figure 1: {report_type} Graph", ParagraphStyle(name='FigureLabel'))

            # Generate a plot
            plt.figure(figsize=(8, 6))  # Define figure size if needed
            plt.bar(df['Period'], df['Amount'])
            plt.xlabel('Period')
            if metric == 'Dollar_Amount':
                plt.ylabel('($)Amount')
            else:
                plt.ylabel('Amount')
            plt.title('Report')

            # Save plot to a buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)

            # Create Image object from buffer
            plot_img = Image(buffer)

            # Calculate available width for the image
            available_width = doc.width

            # Calculate aspect ratio of the image
            img_width, img_height = plot_img.wrap(doc.width, doc.height)
            aspect_ratio = img_width / img_height

            # Calculate new width and height based on available width and aspect ratio
            new_img_width = available_width
            new_img_height = new_img_width / aspect_ratio

            # Set new width and height for the image
            plot_img.drawWidth = new_img_width
            plot_img.drawHeight = new_img_height

            # Add plot to the PDF
            elements.extend([figure_label, padding, plot_img])

            # Build PDF report
            doc.build(elements)

            # Close the buffer
            buffer.close()

            plt.close()

        else:
            # Build PDF report
            doc.build(elements)

        # Open the PDF file
        try:
            viewer = 'start' if os.name == 'nt' else 'xdg-open'  # Windows or Linux
            subprocess.Popen([viewer, full_path], shell=True)
        except Exception as e:
            print(f"Error opening PDF file: {e}")

        while True:
            try:
                time.sleep(1)
                os.rename(full_path, temp_path)
                os.rename(temp_path, full_path)
                break
            except OSError:
                continue

        os.remove(full_path)

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
