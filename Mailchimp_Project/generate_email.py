import csv
from loguru import logger
from pathlib import Path
import os
from send_email import send_email

current_dir = os.getcwd()


def generate_email(received_contents):  # receeiving a dictionary
    default = '-'

    expected_content = dict.fromkeys(
        ['customer_name', 'product', 'mssg', 'amount'], default)

    for content in expected_content:
        if content in received_contents:
            expected_content[content] = received_contents[content]
        else:
            logger.warning(
                f"The value for {content} was not passed to write failure email. Default value {default} will be used")

        email_template_path = Path(current_dir + "/templates/email_template.html")

        logger.info(f'email template path is {email_template_path}')

        if email_template_path.exists() and email_template_path.is_file():
            with open(str(email_template_path), 'r') as message:
                html = message.read().format(**expected_content)
        else:
            logger.critical(
                "EMAIL_TEMPLATE_PATH does not exist so dumping expected content as string into email ")
            html = f"ERROR: EMAIL_TEMPLATE_PATH was not set or does not exist so dumping email content as string:<br/>{expected_content}"

    return html


def search_customer_lists():
    customer_dir = current_dir + '/CSV_material_generator/customer_carts'
    inventory_file = current_dir + '/CSV_material_generator/inventory_items.csv'

    low_stock = {}
    no_stock = {}

    inventory_file = open(inventory_file, 'r')
    inventory_reader = csv.reader(inventory_file, delimiter=',')
    for row in inventory_reader:
        if 'Amount' in row[1]:  # if header
            continue
        elif int(row[1]) == 0:
            no_stock[row[0]] = row[1]
        elif int(row[1]) <= 15:  # less than 15 items
            low_stock[row[0]] = row[1]

    filenames = os.listdir(customer_dir)
    for file_name in filenames:
        if file_name.endswith('.csv'):
            file = open(os.path.join(customer_dir, file_name), 'r')
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                print(row)
                if row[0] in no_stock:  # if item in no_stack, send email
                    send_no_stock_email('Andy', row[0], no_stock[row[0]])
                elif row[0] in low_stock:
                    send_low_stock_email('Andy', row[0], low_stock[row[0]])


def send_low_stock_email(cust_name, product, amount):
    mssg = "If you would still like to purchase this item, please proceed to your shopping cart and continue with your purchase."
    email_contents = {
        "customer_name": cust_name,
        "product": product,
        "mssg": mssg,
        "amount": amount
    }

    body = generate_email(email_contents)
    send_email(
        body=body, subject="Warning! Low stock for item in your cart", files=[])


def send_no_stock_email(cust_name, product, amount):
    mssg = "The item has been removed from your cart as it is no longer available and out of stock"
    email_contents = {
        "customer_name": cust_name,
        "product": product,
        "mssg": mssg,
        "amount": amount
    }

    body = generate_email(email_contents)
    send_email(body=body, subject="Warning! No stock for item in your cart", files=[])


if __name__ == '__main__':
    search_customer_lists()