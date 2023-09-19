import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
import os
from datetime import timedelta
import logging
import pytz
from datetime import datetime

logger = logging.getLogger("pdnssoccli")

SMTP_ERROR = "The email could not be sent. Check the SMTP configuration. "
PATH_HTML = os.environ.get('PATH_HTML', "/etc/pdnssoc/notification_email.html")
FILENAME_HTML = 'notification_email.html'
TIME_FORMAT_YMD = "%Y-%m-%dT%H:%M:%S.%f" # TODO: format of the alerts timestamp should be new_time = datetime.strptime(time_i[:26], TIME_FORMAT_YMD)

# Define a custom filter to enumerate elements
def enumerate_filter(iterable):
    return enumerate(iterable, 1)  # Start counting from 1

class Email:
    def __init__(self, email_config):
        self.subject = email_config["subject"]
        self.server = email_config["server"]
        self.port = email_config["port"]
        self.from_address = email_config["from"]
        self.to_address = email_config["to"]

    def send_email(self, alerts):
        try:
            # Where to search for the template files
            email_template_loader = jinja2.FileSystemLoader(searchpath = PATH_HTML)
            email_template_env = jinja2.Environment(loader = email_template_loader)
            # To allow the use of the timedelta and pytz inside the Jinja2 templates
            email_template_env.globals.update(timedelta = timedelta)
            email_template_env.globals.update(pytz = pytz)
            # Add the custom filter to the Jinja2 environment
            email_template_env.filters['enumerate'] = enumerate_filter


            # Template to be used
            email_template = email_template_env.get_template(FILENAME_HTML)
            
            # Connecting to the mail server
            smtp = smtplib.SMTP(self.server, self.port)

            # Compose the message to send
            email_body = email_template.render(alerts=alerts)
            print(email_body)
            msg_root = MIMEMultipart('related')
            msg_root['Subject'] = str(self.subject)
            msg_root['From'] = self.from_address
            msg_root['To'] = self.to_address
            msg_root['Reply-To'] = self.to_address
            msg_root.preamble = 'This is a multi-part message in MIME format.'
            msg_alternative = MIMEMultipart('alternative')
            msg_root.attach(msg_alternative)
            msg_text = MIMEText(str(email_body), 'html', 'utf-8')
            msg_alternative.attach(msg_text)


            # Send the email
            smtp.sendmail(self.from_address, self.to_address, msg_root.as_string())
            logging.debug('Sending email notification to {}'.format(self.to_address))
            smtp.quit()

        except Exception as e:
            logging.error(SMTP_ERROR + str(e))
            raise Exception(SMTP_ERROR + str(e))

