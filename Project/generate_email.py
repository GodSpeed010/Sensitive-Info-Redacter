import csv
from loguru import logger
from pathlib import Path
import os
from send_email import send_email
import re
import sys

current_dir = os.getcwd()
project_abs_path = os.path.dirname(__file__)

CUSTOMER_NAME = 'Bob'


def generate_email(received_contents):  # receiving a dictionary
    default = '-'

    email_template_path = Path(
        os.path.join(project_abs_path, "templates/email_template.html")
    )

    logger.info(f'email template path is {email_template_path}')

    expected_content = dict.fromkeys(
        ['customer_name', 'leaked_info', 'mssg', 'sensitive_file'], default)

    for content in expected_content:
        if content in received_contents:
            expected_content[content] = received_contents[content]
        else:
            logger.warning(
                f"The value for {content} was not passed to write failure email. Default value {default} will be used")

        if email_template_path.exists() and email_template_path.is_file():
            with open(str(email_template_path), 'r') as message:
                html = message.read().format(**expected_content)
        else:
            logger.critical(
                "EMAIL_TEMPLATE_PATH does not exist so dumping expected content as string into email ")
            html = f"ERROR: EMAIL_TEMPLATE_PATH was not set or does not exist so dumping email content as string:<br/>{expected_content}"

    return html


def search_customer_files(customer_dir=os.getcwd()):

    # dictionary of sensitive info types mapped to a list containing regex matches for that type
    # multiple regex matches are provided in some cases for higher accuracy
    regex_matches = {
        'ssn': [
            r'(?!000|.+0{4})(?:\d{9}|\d{3}-\d{2}-\d{4})',
            r'[0-9]{3}-[0-9]{2}-[0-9]{4}'
        ],
        'email': [
            r'([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6})',
            r'[\w\.=-]+@[\w\.-]+\.[\w]{2,3}'
        ],
        'phone_number': [r'\d{3}-\d{3}-\d{4}'],
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

    # get list of ONLY files, no folders
    filenames = list(filter(
        lambda file_or_folder: os.path.isfile(
            os.path.join(customer_dir, file_or_folder)
        ),
        os.listdir(customer_dir)
    ))

    # iterating over files in customer_dir
    for file_name in filenames:
        with open(os.path.join(customer_dir, file_name), 'r') as file:
            file_str = file.read()
            file_redacted = file_str[:]  # copy the file string

            # iterate through all keys in regex_matches dictionary ('ssn', 'email', etc..)
            for info_type in regex_matches:
                # iterate through all regex_matches for the info_type in the dictionary
                for info_type_match in regex_matches[info_type]:
                    # tries replacing sensitive info using regex
                    replacement_operation = re.subn(
                        info_type_match, 'REDACTED', file_redacted
                    )
                    # the file string after having sensitive info replaced
                    file_redacted = replacement_operation[0]
                    replacements_made = replacement_operation[1]

                    if replacements_made:
                        send_sensitive_data_email(info_type, file_name)

            # if sensitive info was found, the strings will be different
            if file_str != file_redacted:
                # save the redacted text to a new file
                with open(f'{file_name}_REDACTED', 'w') as redacted_info_file:
                    # print(f'writing {file_redacted} to new file')
                    redacted_info_file.write(file_redacted)

# sends an email to customer telling what type of sensitive data was found and what file it was found in
def send_sensitive_data_email(leaked_info, sensitive_file):
    mssg = "A copy of your file has been made with redacted sensitive information. Please review the file and remove any remaining sensitive information as soon as possible."
    subject = 'WARNING! Sensitive Info. Leaked'
    email_contents = {
        "customer_name": CUSTOMER_NAME,
        "leaked_info": leaked_info,
        "mssg": mssg,
        "sensitive_file": sensitive_file
    }
    body = generate_email(email_contents)

    send_email(body=body, subject=subject, files=[])


if __name__ == '__main__':
    # if arguments were passed via terminal
    if len(sys.argv) > 1:
        # relative path to directory to search that user passed as argument
        relative_search_dir = sys.argv[1]

        # absolute path for the above relative path
        abs_search_dir = os.path.join(os.getcwd(), relative_search_dir)

        search_customer_files(customer_dir=abs_search_dir)

    else:
        search_customer_files()

    print('Done')