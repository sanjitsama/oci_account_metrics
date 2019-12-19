# python script for sending SMTP configuration with Oracle Cloud Infrastructure Email Delivery
import os
import smtplib
import json
import inspect
from operator import itemgetter
import email.utils
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, formataddr


report_dir = os.path.join(os.getcwd(), "output_files/")


def tostr(var): return str(
    [k for k, v in inspect.currentframe().f_back.f_locals.items() if v is var][0])


class Report:
    def __init__(self, config):
        self.config = dict(config['DEFAULT'])
        self.subject = "OCI Account Metrics Report"
        self.body_text = ("Email Delivery Test\r\n"
                          "This email was sent through the OCI Email Delivery SMTP "
                          "Interface using the Python smtplib package.\nAttached is the report file."
                          )
        self.body_html = """
            <html>
                <head></head>
                <body>
                <h1>OCI Account Metrics Report</h1>
                <p>This email was sent with Email Delivery using the
                    <a href='https://www.python.org/'>Python</a>
                    <a href='https://docs.python.org/3/library/smtplib.html'>
                    smtplib</a> library.
                </p>
                <p>Attached is the report file.
                </p>
                </body>
            </html>
        """
        self.msg = MIMEMultipart()

    def compose_report(self):
        sender, sendername = itemgetter(
            'sender', 'sendername')(self.config)
        # Create message container - the correct MIME type is multipart/alternative.
        self.msg['From'] = formataddr((sendername, sender))
        self.msg['Date'] = formatdate(localtime=True)
        self.msg['Subject'] = self.subject
        self.msg.attach(MIMEText(self.body_text, 'plain'))
        self.msg.attach(MIMEText(self.body_html, 'html'))
        for report_name in os.listdir(report_dir):
            with open(report_dir + report_name, "rb") as rfile:
                part = MIMEApplication(
                    rfile.read(),
                    Name=report_name
                )
            # After the file is closed
            print(report_name)
            part['Content-Disposition'] = 'attachment; filename="%s"' % report_name
            self.msg.attach(part)

    def publish_report(self):
        username, password, sender, recipients, host, port = itemgetter(
            'username', 'password', 'sender', 'recipients', 'host', 'port')(self.config)
        for recipient in recipients.split(","):
            self.msg['To'] = recipient
            # Try to send the message.
            try:
                server = smtplib.SMTP(host, port)
                server.ehlo()
                server.starttls()
                # smtplib docs recommend calling ehlo() before & after starttls()
                server.ehlo()
                server.login(username, password)
                server.sendmail(sender, recipient, self.msg.as_string())
                server.close()
            # Display an error message if something goes wrong.
            except Exception as e:
                print("Error: ", e)
            else:
                print("Email successfully sent!")


"""
# Try to send the message.
try:
    server = smtplib.SMTP(HOST, PORT)
    server.ehlo()
    server.starttls()
    # smtplib docs recommend calling ehlo() before & after starttls()
    server.ehlo()
    server.login(USERNAME_SMTP, PASSWORD_SMTP)
    server.sendmail(SENDER, RECIPIENT, msg.as_string())
    server.close()
# Display an error message if something goes wrong.
except Exception as e:
    print("Error: ", e)
else:
    print("Email successfully sent!")
 """
