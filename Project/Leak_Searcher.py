import os
import re
from loguru import logger
import smtplib
from smtplib import SMTPException
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

current_dir = os.getcwd()

class Leak_Searcher:
    def __init__(
        self,
        receiver_name,
        sender_email,
        receiver_email,
        # string of ',' delimited emails
        cc_emails,
        my_password,
        current_dir=os.getcwd(),
        max_file_size=2000000
    ):
        self.__receiver_name = receiver_name
        self.__sender_email = sender_email
        self.__receiver_email = receiver_email
        self.__cc_emails = cc_emails
        self.__my_password = my_password
        self.__max_file_size = max_file_size
        self.__current_dir = current_dir

    def scan_dir_files(self, dir):
        customer_dir = os.path.join(self.__current_dir, dir)  # '/Project/test_data/'

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

        #get list of ONLY files, no folders
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
                            self.send_sensitive_data_email(info_type, file_name)

                # if sensitive info was found, the strings will be different
                if file_str != file_redacted:
                    # save the redacted text to a new file
                    with open(f'{file_name}_REDACTED', 'w') as redacted_info_file:
                        # print(f'writing {file_redacted} to new file')
                        redacted_info_file.write(file_redacted)


    def send_email(self, subject, body, files):
        to_emails = self.__receiver_email.split(',') + self.__cc_emails.split(',')

        message = MIMEMultipart()
        message['From'] = self.__sender_email
        message['To'] = self.__receiver_email
        message['Subject'] = subject
        message['CC'] = self.__cc_emails

        message.attach(MIMEText(body, 'html'))

        # loop through filenames to attach files passed through
        for filename in files:
            attach_path = filename
            if attach_path.exists() and os.path.getsize(filename) < self.__max_file_size:
                with open(os.path.join(filename), 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename = {os.path.basename(filename)}'
                    )
                    message.attach(part)
            else:
                logger.warning(
                    f'Failed to attach {attach_path.as_posix()} as the path did not exist or the file was larger than {self.__max_file_size} bytes.')

        text = message.as_string()

        try:
            smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpobj.ehlo()
            smtpobj.starttls()
            smtpobj.ehlo()
            smtpobj.login(self.__sender_email, self.__my_password)
            smtpobj.sendmail(self.__sender_email, to_emails, text)
            smtpobj.close()

        except SMTPException:
            logger.exception(
                f'Unable to send email. Failed to send from {self.__sender_email} to {"".join(to_emails) }.')

    def send_sensitive_data_email(self, leaked_info, sensitive_file):
        mssg = "A copy of your file has been made with redacted sensitive information. Please review the file and remove any remaining sensitive information as soon as possible."
        subject = 'WARNING! Sensitive Info. Leaked'
        email_contents = {
            "customer_name": self.__receiver_name,
            "leaked_info": leaked_info,
            "mssg": mssg,
            "sensitive_file": sensitive_file
        }
        body = self.generate_email(email_contents)

        self.send_email(body=body, subject=subject, files=[])

    def generate_email(self, received_contents):  # receiving a dictionary
        default = '-'

        email_template_path = Path(
            os.path.join(
            current_dir, "Project/templates/email_template.html"
            )
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