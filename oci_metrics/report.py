#! /usr/bin/python3
import oci
import json
import os
import smtplib
from email.message import EmailMessage
# Import the email modules we'll need
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = os.environ.get('TWILIO_SID')
# Your Auth Token from twilio.com/console
auth_token = os.environ.get('TWILIO_TOKEN') 

client = Client(account_sid, auth_token)


def get_report(filepath):
    with open(filepath) as jsonfile:
        data = json.load(jsonfile)
        return data


def send_email(report_name):
    sending_ts = datetime.now()
    sub = "Here's my subject %s" % sending_ts.strftime('%Y-%m-%d %H:%M:%S')
    msg = MIMEMultipart()
    #fromaddr = 'nd.corc@gmail.com'
    fromaddr = 'no-reply@example.com'
    toaddr = 'nolan.corcoran@oracle.com'
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = sub
    body = "This is a sample report email generated from the oci metrics script."
    msg.attach(MIMEText(body, 'plain'))

    report_dir = os.path.join(os.getcwd(), "output_files/")
    report = open(report_dir + report_name, "rb")

    # instance of MIMEBase and named as p
    # To change the payload into encoded form
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((report).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition',
                 "attachment; filename= %s" % report_name)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    #msg['From'] = 'no-reply@example.com'
    slocal = smtplib.SMTP('localhost')
    text = msg.as_string()
    slocal.sendmail(fromaddr, toaddr, text)
    slocal.quit()
    return 0


def send_text(report_name):
    message = client.messages.create(
        to="+18326221587",
        from_="+13462518204",
        body="This is a sample report text generated from the oci metrics script...report name = " + report_name)
    print(message.sid)


""" 
    msg['From'] = 'nd.corc@gmail.com'
    sgmail = smtplib.SMTP('smtp.gmail.com', 587)
    sgmail.starttls()
    sgmail.login("nd.corc@gmail.com", "Snickers123")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    sgmail.sendmail(fromaddr, toaddr, text)
    sgmail.quit() """
