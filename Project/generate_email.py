import csv
from loguru import logger
from pathlib import Path
import os
from send_email import send_email
import re

current_dir = os.getcwd()


def generate_email(received_contents):  # receiving a dictionary
    default = '-'

    expected_content = dict.fromkeys(
        ['customer_name', 'leaked_info', 'mssg', 'sensitive_file'], default)

    for content in expected_content:
        if content in received_contents:
            expected_content[content] = received_contents[content]
        else:
            logger.warning(
                f"The value for {content} was not passed to write failure email. Default value {default} will be used")

        email_template_path = Path(
            current_dir + "/Project/templates/email_template.html")

        logger.info(f'email template path is {email_template_path}')

        if email_template_path.exists() and email_template_path.is_file():
            with open(str(email_template_path), 'r') as message:
                html = message.read().format(**expected_content)
        else:
            logger.critical(
                "EMAIL_TEMPLATE_PATH does not exist so dumping expected content as string into email ")
            html = f"ERROR: EMAIL_TEMPLATE_PATH was not set or does not exist so dumping email content as string:<br/>{expected_content}"

    return html

def search_customer_files():
    customer_dir = current_dir + '/Project/test_data/'

    # dictionary of sensitive info types mapped to a list containing regex matches for that type
    # multiple regex matches are provided in some cases for higher accuracy
    regex_matches = {
        'ssn': [r'(?!000|.+0{4})(?:\d{9}|\d{3}-\d{2}-\d{4})'],
        'email': [
            r'([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})',
            r'[\w\.=-]+@[\w\.-]+\.[\w]{2,3}'
        ],
        'phone': [r'\d{3}-\d{3}-\d{4}'],
        'credit_card': [
            # mastercard
            r'(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}',
            # visa
            r'\b([4]\d{3}[\s]\d{4}[\s]\d{4}[\s]\d{4}|[4]\d{3}[-]\d{4}[-]\d{4}[-]\d{4}|[4]\d{3}[.]\d{4}[.]\d{4}[.]\d{4}|[4]\d{3}\d{4}\d{4}\d{4})\b',
            # amex
            r'^3[47][0-9]{13}$',
            # discover
            r'(6(?:011|5[0-9]{2})[0-9]{12})',
        ],
        'ipv6_address': [r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}'],
    }

    filenames = os.listdir(customer_dir)
    # iterating over files in customer_dir
    for file_name in filenames:
        # if file is .csv
        if file_name.endswith('.csv'):
            continue  # todo
        # handle as text file
        else:
            with open(os.path.join(customer_dir, file_name), 'r') as file:
                file_str = file.read()

                # iterate through all keys in regex_matches dictionary
                for info_type in regex_matches:
                    # iterate through all regex_matches for the info_type in the dictionary
                    for info_type_match in regex_matches[info_type]:
                        matches = re.findall(info_type_match, file_str) # todo replace with find or match; don't need to find all matches, just know if it exists

                        # if there are any matches
                        if len(matches) > 0:

                            # print the type of info_match along with all the matches
                            print(
                                info_type,
                                re.findall(info_type_match, file_str),
                                sep=' '
                            )

                            # send_sensitive_data_email('bob', info_type, file_name)

                            break

# sends an email to customer telling what type of sensitive data was found and what file it was found in
def send_sensitive_data_email(cust_name, leaked_info, sensitive_file):
    mssg = "Please remove your sensitive info from the file as soon as possible."
    subject = 'WARNING! Sensitive Info. Leaked'
    email_contents = {
        "customer_name": cust_name,
        "leaked_info": leaked_info,
        "mssg": mssg,
        "sensitive_file": sensitive_file
    }
    body = generate_email(email_contents)

    print(body)
    # send_email(body=body, subject=subject, files=[])

if __name__ == '__main__':
    search_customer_files()