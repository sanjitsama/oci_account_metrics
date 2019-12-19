#! /usr/bin/python3
import oci
import json
import os
from treelib import Node, Tree


config_file = "/home/opc/.oci/config"


def get_availability_domains(identity_client, compartment_id):
    list_availability_domains_response = oci.pagination.list_call_get_all_results(
        identity_client.list_availability_domains,
        compartment_id
    )
    availability_domains = list_availability_domains_response.data
    return availability_domains


class Instances:
    def __init__(self, tenancy):
        self.config = tenancy.config
        self.identity = tenancy.identity
        self.compute = tenancy.compute
        self.compartments = tenancy.compartments.compartments
        self.availability_domains = get_availability_domains(
            self.identity, self.config["tenancy"])
        self.instances = []

    def get_ad_instances(self, comp_id):
        for ad in self.availability_domains:
            instances = [c.__dict__ for c in list(self.compute.list_instances(
                comp_id, availability_domain=ad, lifecycle_state="RUNNING").data)]
            instances = list(map(lambda curr: dict([(k, v) for (k, v) in curr.items(
            ) if (k != "metadata")]), instances))
            self.instances.extend(instances)

    def get_instances(self):
        self.get_ad_instances(self.config["tenancy"])
        for comp in self.compartments:
            comp_id = comp["_id"]
            self.get_ad_instances(comp_id)
        print(len(self.instances))
