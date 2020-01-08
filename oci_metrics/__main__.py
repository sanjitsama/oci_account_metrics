#! /usr/bin/python3
import sys
import os
import configparser
import oci
import datetime
import json
import smtplib
import email
from operator import setitem
from oci_metrics.compartments import Compartments
from oci_metrics.instances import Instances
from oci_metrics.report import Report
from oci_metrics.showoci import showoci

CONFIG_FILE = "/home/opc/.oci/config"
base_dir = "/home/opc/oci_metrics/report_dir"

class TenancyMetrics(object):

    def __init__(self, config):
        self.config = config
        self.name = self.config['tenancy_name']
        self.identity = oci.identity.IdentityClient(self.config)
        self.compute = oci.core.ComputeClient(self.config)
        self.compartments = None
        self.instances = None
        self.report_dir = None

    """ def save_report(self):
         with open(os.path.join(report_dir, f"{self.config['tenancy_name']}_compartments.json"), 'w') as f:
            f.write(json.dumps(self.compartments.compartments, indent=4,
                               sort_keys=True, default=str))
        print("******************************************************")
        print("***               Compartment Layout               ***")
        print("******************************************************")
        self.compartments.compartment_tree.show()
        print("\n")
        self.compartments.compartment_tree.save2file(
            os.path.join(report_dir, f"{self.config['tenancy_name']}_compartment_tree.txt"))
        with open(os.path.join(report_dir, f"{self.config['tenancy_name']}_instances.json"), 'w') as f:
            f.write(json.dumps(self.compartments.instances, indent=4,
                               sort_keys=True, default=str)) """

def main():
    cmd = showoci.set_parser_arguments()
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    """ sections =  dict([ (k, dict(v)) for k,v in list(config.items()) if k is not "DEFAULT"])
    smtp = sections.pop("smtp") """
    config = dict(parser[cmd.profile])
    smtp = dict(parser["smtp"])
    tenancy = TenancyMetrics(config)
    tenancy.report_dir = f"{base_dir}/{cmd.datetime}"
    print(f"Running OCI Metrics script on Tenancy {cmd.profile} ...\n")
    print("Step 1: Getting Compartment Structure...\n\n")
    tenancy.compartments = Compartments(tenancy)
    tenancy.compartments.get_all()
    tenancy.compartments.get_compartment_tree(tenancy.report_dir)
    showoci.execute_extract(cmd, tenancy.report_dir)
    """ for section in sections:
        
        tenancy = TenancyMetrics(section, sections[section])
        print(
            f"Running OCI Metrics script on Tenancy {tenancy.config['tenancy_name']} ...\n")
        print("Step 1: Getting Compartment Structure...\n\n")
        tenancy.compartments = Compartments(tenancy)
        tenancy.compartments.get_all()
        #print(f"Total # of instances = {len(tenancy.compartments.instances)}")
        tenancy.compartments.get_compartment_tree()
        #print(f"Total # of instances = {len(tenancy.compartments.instances)}")
        report.create_report(section) """


if __name__ == '__main__':
    main()
