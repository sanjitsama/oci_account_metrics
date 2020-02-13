# python script for sending SMTP configuration with Oracle Cloud Infrastructure Email Delivery
import os
import smtplib
import json
import csv
import inspect
from operator import itemgetter
import backoff
import zipfile
import configparser
import argparse
import email.utils
from functools import reduce
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, formataddr
from oci_metrics.showoci import showoci
import cx_Oracle
#from oci_metrics.showoci.showoci import execute_extract

#report_dir = os.path.join(os.getcwd(), "output_files/")
CONFIG_FILE = "/home/opc/.oci/config"
BASE_DIR = "/home/opc/oci_metrics/report_dir"

#def tostr(var): return str([k for k, v in inspect.currentframe().f_back.f_locals.items() if v is var][0])

def set_connection(config):
    db_user, db_pass, admin_user, admin_pass, dsn = itemgetter('db_user', 'db_pass', 'admin_user', 'admin_pass', 'dsn')(config)
    connection = cx_Oracle.connect(db_user, db_pass, dsn, encoding="UTF-8")
    cursor = connection.cursor()
    return connection, cursor
    

class Report:

    def __init__(self, config, datetime):
        self.config = config
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
        self.report_dir = f"{config['report_dir']}/{datetime}"
        self.report_zip = os.path.basename(f"{self.report_dir}.zip")
        self.connection = None

    """ def create_report(self, tenancy=None):
        showoci.execute_extract(tenancy) """


    def compose_email(self):
        sender, sendername = itemgetter(
            'sender', 'sendername')(self.config)
        # Create message container - the correct MIME type is multipart/alternative.
        self.msg['From'] = formataddr((sendername, sender))
        self.msg['Date'] = formatdate(localtime=True)
        self.msg['Subject'] = self.subject
        self.msg.attach(MIMEText(self.body_text, 'plain'))
        self.msg.attach(MIMEText(self.body_html, 'html'))
        report_name = self.report_file
        with open(self.report_file, "rb") as rfile:
            part = MIMEApplication(
                rfile.read(),
                Name=report_name
            )       
        part['Content-Disposition'] = 'attachment; filename="%s"' % report_name
        self.msg.attach(part) 
        """ for report_name in os.listdir(report_dir):
            with open(report_dir + report_name, "rb") as rfile:
                part = MIMEApplication(
                    rfile.read(),
                    Name=report_name
                )
            # After the file is closed
            print(report_name)
            part['Content-Disposition'] = 'attachment; filename="%s"' % report_name
            self.msg.attach(part) """

    def publish_email(self):
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

    def create_table(self, table, csv_file):
        columns = self.get_columns(csv_file)
        sql = f"""create table {table} (
            ID NUMBER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),"""
        for i,c in enumerate(columns):
            if c.lower() == "components":
                chars = 50000
            elif c.lower() == "attributes" or c.lower() == "tags" or c.lower() == "capacities" or c.lower() == "activitylogs":
                chars = 3000 
            else: chars = 500
            sql += f"""
            {c} VARCHAR ({chars}){"," if i < len(columns)-1 else ""}"""
        sql += """ 
        )
        """
        try: 
            self.cursor.execute(sql)    
            while True: 
                row = self.cursor.fetchone()
                if row is None: break
                #print(row)                
        except Exception as e: return False

    def delete_table(self, table):
        print(f"DELETING table = {table.upper()}...\n")
        self.cursor.execute(f"drop table {table}")

    def check_table(self, table):
        sql = f"select * from {table}"
        try: 
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
        except Exception as e: return False
        return True

    def get_columns(self, csv_file):
        columns = []
        try:
            with open(csv_file, "r") as f:
                reader = csv.reader(f)
                i = next(reader)
                columns.extend(i)
                rows = [row for row in reader]
                return columns
        except Exception as e: 
            return columns


    def load_report(self, table, csv_file):
        print(f"LOADING table = {table.upper()}...\n")
        columns = self.get_columns(csv_file)
        sql = f"""insert into {table} ("""
        for i, c in enumerate(columns):
            if i < len(columns)-1: sql += f"""{c}, """
            else: sql += f"""{str(c)}) values ("""
        for i, c in enumerate(columns):
            if i < len(columns)-1: sql += f""":{i+1}, """
            else: sql += f""":{i+1})"""
        try:
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                i = next(reader)
                data = []
                for i, row in enumerate(reader):
                    rowtupe = tuple(row)
                    data.append(rowtupe)
                try: self.cursor.executemany(sql, data)
                except Exception as e: print(f"error: {str(e)}")
        except Exception as oe:
            pass

    def prepare_report(self):
        os.system(f"zip -r -j " + self.report_dir + "{.zip,}")
        csv_dir = self.report_dir + "/csv"
        report_files = []
        for dirname, subdirs, filenames in os.walk(csv_dir):
            report_files.extend(filenames)
            for fname in filenames:
                csv_file = f"{csv_dir}/{fname}"
                print(f"csv_file = {csv_file}")
                table = fname.replace(".csv", "")
                print("\n----------------------------------------------------------------")
                print(f"----------------------------------------------------------------\n\ntable = {table.upper()}\n")
                if not self.check_table(table): self.create_table(table, csv_file)
                self.load_report(table, csv_file)

    def set_connection(self):
        db_user, db_pass, dsn = itemgetter('db_user', 'db_pass', 'dsn')(self.config)
        self.connection = cx_Oracle.connect(db_user, db_pass, dsn, encoding="UTF-8")
        self.cursor = self.connection.cursor()


def main():
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    report_config = dict(parser["report"])
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-date', default="", dest='datetime', help='Print Datetime')
    cmd = argparser.parse_args()
    report = Report(report_config, cmd.datetime)
    report.set_connection()
    report.prepare_report()
    """ report.compose_email()
    report.publish_email() """


if __name__ == '__main__':
    main()


''' def create_table(self, table, csv_file):
    columns = self.get_columns(csv_file)
    sql = f"""create table {table} (
        ID NUMBER GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),"""
    for column in columns:
        sql += f"""{column} VARCHAR (50))"""
    psql(sql)
    try: 
        self.cursor.execute(sql)    
        while True: 
            row = self.cursor.fetchone()
            if row is None: break
            print(row)                
    except Exception as e: 
        print(f"error = {e}")
        return False '''

'''
errCode = es[es.index("ORA"):es.index(":")]
if errCode == "ORA-12899":
    print("max varchar exceeded, increasing column varchar size...")
    col, vals = es.split(" (actual: ")
    col = col.split('."')[-1][:-1]
    vals = vals.split(", maximum: ")
    actual, curr = vals[0], vals[1][:-1]'''