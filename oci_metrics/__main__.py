#! /usr/bin/python3
import sys
import os
import configparser
import oci
import datetime
import json
import smtplib
import email
from oci_metrics.compartments import Compartments
from oci_metrics.instances import Instances
from oci_metrics.report import Report

config_file = "/home/opc/.oci/config"
smtp_file = "/home/opc/.oci/smtp_config"
report_dir = os.path.join(os.getcwd(), "output_files/")
config = configparser.ConfigParser()
config.read(config_file)
sessions = config.sections()
smtp = configparser.ConfigParser()
smtp.read(smtp_file)


class TenancyMetrics:
    def __init__(self, session):
        self.config = oci.config.from_file(config_file, profile_name=session)
        self.identity = oci.identity.IdentityClient(self.config)
        self.compute = oci.core.ComputeClient(self.config)
        self.output_dir = os.path.join(os.getcwd(), "output_files/")
        self.compartments = None
        self.instances = None

    def save_report(self):
        with open(os.path.join(self.output_dir, f"{self.config['tenancy_name']}_compartments.json"), 'w') as f:
            f.write(json.dumps(self.compartments.compartments, indent=4,
                               sort_keys=True, default=str))
        self.compartments.compartment_tree.save2file(
            os.path.join(self.output_dir, f"{self.config['tenancy_name']}_compartment_tree.txt"))
        with open(os.path.join(self.output_dir, f"{self.config['tenancy_name']}_instances.json"), 'w') as f:
            f.write(json.dumps(self.compartments.instances, indent=4,
                               sort_keys=True, default=str))


def main():
    for session in sessions:
        tenancy = TenancyMetrics(session)
        print(
            f"Running OCI Metrics script on Tenancy {tenancy.config['tenancy_name']} ...\n")
        print("Step 1: Getting Compartment Structure...\n\n")
        tenancy.compartments = Compartments(tenancy)
        tenancy.compartments.get_all()
        print(f"Total # of instances = {len(tenancy.compartments.instances)}")
        tenancy.compartments.get_compartment_tree()
        #tenancy.instances = Instances(tenancy)
        # tenancy.instances.get_instances()
        print(f"Total # of instances = {len(tenancy.compartments.instances)}")
        tenancy.save_report()
        # compartments.save_to_report()
    report = Report(smtp)
    report.compose_report()
    report.publish_report()


if __name__ == '__main__':
    main()
