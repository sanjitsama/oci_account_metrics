#! /usr/bin/python3
import sys
import os
import oci
import datetime
import json
from oci_metrics.compartments import get_compartments, get_compartment_tree
# from
# from .funcmodule import my_function


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
        break


if __name__ == '__main__':
    main()
