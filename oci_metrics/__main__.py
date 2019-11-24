#! /usr/bin/python3
import sys
import os
import oci
import datetime
import json
import smtplib
import email
from oci_metrics.compartments import get_compartments, get_compartment_tree
from oci_metrics import report
#from oci_metrics import compartments, report

# from oci_metrics.instances import get_all, get_by_compartment,
# from oci_metrics.
#


def main():
    sessions = os.listdir(os.getcwd()+"/../.oci/sessions")
    configs = []
    for account in sessions:
        config = oci.config.from_file("~/.oci/config", profile_name=account)
        identity = oci.identity.IdentityClient(config)
        configs.append((identity, config, account))
        for args in configs:  # for each account
            print(f"Running OCI Metrics script on Tenancy {account} ...\n")
            print("Step 1: Getting one level compartment structure...")
            comps = get_compartments(*args)
            print("Printing Root Compartments ...\n")
            for c in comps:
                cname = c["_name"]
                print(f"Compartment {cname}: \n{c}\n\n")
            next_comps = get_compartment_tree(comps, *args)
            print("\n\nPrinting Next Level Compartments ...\n")
            for c in next_comps:
                cname = c["_name"]
                print(f"Compartment {cname}: \n{c}\n\n")
            report_dir = os.path.join(os.getcwd(), "output_files/")
            for report_name in os.listdir(report_dir):
                report.send_email(report_name)
                report.send_text(report_name)
        break


if __name__ == '__main__':
    main()
