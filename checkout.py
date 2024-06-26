import os
import tempfile
from datetime import datetime
import ssl
from email.message import EmailMessage
import smtplib
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from database_portal import DatabasePortal


def generate_receipt_number():
    """generate_receipt_number()

    Description:
    Creates a receipt number based on the time the transaction took place.
    """
    now = datetime.now()
    formatted_datetime = now.strftime('%Y%m%d%H%M%S')
    nanoseconds = now.strftime('%f')
    nanoseconds = int(nanoseconds) * 1000

    result = '' + formatted_datetime + f"{nanoseconds:09d}"
    return result


def send_email(email, body, filename):
    """send_email()

    Description:
    Sends the sales' record via email to the customer with a PDF version attached.

    Parameters:
    String: email
    String: body
    String: filename
    """

    password = "iqsykkuktypwwclx"
    email_sender = "alpha.store.email123@gmail.com"
    email_receiver = email

    subject = "Alpha Store Receipt"
    message_body = body

    em = EmailMessage()
    em['From'] = email_sender
    em["To"] = email_receiver
    em['Subject'] = subject
    em.set_content(message_body)

    # Attach the file
    with open(filename, "rb") as attachment:
        attachment_data = attachment.read()
        em.add_attachment(attachment_data, maintype="application", subtype="octet-stream", filename=filename)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def delete_pdf(sale_id):
    """ delete_pdf()

    Description:
    Deletes the PDF from the temp directory to prevent the disk from filling up.

    Parameters:
    String: sale_id
    """

    try:
        os.remove(f"temp/Receipt-{sale_id}.pdf")

    except OSError:
        return 1

    return 0


def generate_pdf_receipt(receipt_number, sales_date, cart_list, total):
    """generate_pdf_receipt()

    Description:
    Generates a PDF version of the customer's sale receipt.

    Parameters:
    String: receipt_number
    Data: sales_date
    array/dictionary[]{}: cart_list
    float: total

    Output:
    String: filename
    """

    temp_dir = tempfile.gettempdir()
    file_name = f"Receipt-{receipt_number}.pdf"
    file_path = os.path.join(temp_dir, file_name)

    # Create a PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    header_text = f"Alpha Store Receipt\nReceipt Number: {receipt_number}\nDate: {sales_date}"
    elements.append(Paragraph(header_text, styles['Heading1']))

    # Table of items
    data = [["Product", "Quantity", "Unit_Price"]]
    for product in cart_list:
        product_name = product.get('Product_Name')
        quantity = product.get('Quantity')
        unit_price = product.get('Unit_Price')
        total_price = float(quantity) * unit_price
        data.append([product_name, str(quantity), f"${total_price:.2f}"])

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), 'lightgrey'),
                               ('TEXTCOLOR', (0, 0), (-1, 0), 'black'),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), 'white'),
                               ('GRID', (0, 0), (-1, -1), 1, 'black')]))

    elements.append(table)

    # Total
    total_text = f"Total: ${total:.2f}"
    elements.append(Paragraph(total_text, styles['Normal']))

    # Build PDF
    doc.build(elements)

    return file_path


class Checkout:

    def __init__(self):
        """Checkout

        Description:
        Updates the system inventory to account for the products sold, creates PDF and email versions of the
        sales record or receipt, and emails the receipts to the customer.
        """
        self.db_portal = DatabasePortal()

    def checkout(self, cart_list, total, email, employee_id):
        """checkout()

        Description:
        Updates the database subtracting the quantity sold from the quantity of the product on the sales floor shelf
        and total quantity on hand, and creates a sales record to be stored in the database.
        """

        receipt_number = generate_receipt_number()
        sales_date = datetime.now()
        formatted_date = sales_date.strftime("%Y-%m-%d")
        formatted_date_email = sales_date.strftime("%Y/%m/%d %I:%M %p")

        script = "INSERT INTO Sales VALUES (?, ?, ?, ?)"
        param = (receipt_number, employee_id, total, formatted_date)
        self.db_portal.push_data(script, param)

        for product in cart_list:
            product_id = product.get('ProductID')
            quantity = product.get('Quantity')
            unit_price = product.get('Unit_Price')

            script = "INSERT INTO Sales_Products VALUES (?, ?, ?, ?)"
            param = (receipt_number, product_id, quantity, unit_price)
            self.db_portal.push_data(script, param)

            script = (f"UPDATE Shelf_Product SET Quantity = Quantity - ? "
                      f"WHERE ProductID = ? AND ShelfID LIKE 'SF%';")
            param = (quantity, product_id)
            self.db_portal.push_data(script, param)

            # Update the total amount of the product that is in stock by adding the received quantity to the total
            script = (f"UPDATE Product SET Total_In_Stock = Total_In_Stock - ? "
                      f"WHERE ProductID = ?;")
            param = (quantity, product_id)
            self.db_portal.push_data(script, param)

        # Generate PDF receipt and get file path
        pdf_file_path = generate_pdf_receipt(receipt_number, formatted_date_email, cart_list, total)

        # Construct the email body resembling a retail store receipt
        email_body = f"Receipt Number: {receipt_number}\n"
        email_body += f"Date: {formatted_date_email}\n"
        email_body += "----------------------------------------\n"
        email_body += "Product                 Quantity   Price\n"
        email_body += "----------------------------------------\n"

        for product in cart_list:
            product_name = product.get('Product_Name')
            quantity = product.get('Quantity')
            unit_price = product.get('Unit_Price')
            total_price = float(quantity) * unit_price

            # Adjust spacing to align columns
            email_body += f"{product_name.ljust(24)}{str(quantity).ljust(11)}${total_price:.2f}\n"

        email_body += "----------------------------------------\n"
        email_body += f"Total: ${total:.2f}\n\n"
        email_body += "Thank you for shopping with us!\n"

        # Send the email
        send_email(email, email_body, pdf_file_path)

        # Delete the PDF
        delete_pdf(receipt_number)

        return 0
