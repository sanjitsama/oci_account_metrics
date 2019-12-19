#! /usr/bin/python3
import oci
import json
import os
import backoff
from treelib import Node, Tree


config_file = "/home/opc/.oci/config"


""" def backoff_hdlr(details):
    print("Backing off {wait:0.1f} seconds afters {tries} tries "
          "calling function {target} with args {args} and kwargs "
          "{kwargs}".format(**details)) """


def get_availability_domains(identity_client, compartment_id):
    list_availability_domains_response = oci.pagination.list_call_get_all_results(
        identity_client.list_availability_domains,
        compartment_id
    )
    availability_domains = list_availability_domains_response.data
    return availability_domains


class Compartments:
    def __init__(self, tenancy):
        self.config = tenancy.config
        self.identity = tenancy.identity
        self.compute = tenancy.compute
        self.availability_domains = get_availability_domains(
            self.identity, self.config["tenancy"])
        self.compartments = []
        self.compartment_tree = Tree()
        self.instances = []

    def get_all(self, current=None):
        comp_id = self.config["tenancy"] if current is None else current["_id"]
        for ad in self.availability_domains:
            self.get_instances(comp_id, ad)
        children = self.get_compartments(comp_id)
        if len(children) is 0:
            return
        children = list(map(lambda curr: dict([(k, v) for (k, v) in curr.items(
        ) if (k != "attribute_map" and k != "swagger_types")]), children))
        for child in children:
            self.compartments.append(child)
            self.get_all(child)
        return

    @backoff.on_exception(backoff.expo, oci.exceptions.ServiceError)
    def get_compartments(self, comp_id):
        return [c.__dict__ for c in list(self.identity.list_compartments(
            comp_id, access_level="ANY").data) if c.__dict__["_lifecycle_state"] != "DELETED"]

    @backoff.on_exception(backoff.expo, oci.exceptions.ServiceError)
    def get_instances(self, comp_id, ad):
        instances = [c.__dict__ for c in list(self.compute.list_instances(
            comp_id, availability_domain=ad, lifecycle_state="RUNNING").data)]
        instances = list(map(lambda curr: dict([(k, v) for (k, v) in curr.items(
        ) if (k != "metadata" and k != "attribute_map" and k != "swagger_types")]), instances))
        self.instances.extend(instances)

    def get_compartment_tree(self):
        self.compartment_tree.create_node(
            f"{self.config['tenancy_name']} (root)", self.config['tenancy'])
        for compartment in self.compartments:
            self.compartment_tree.create_node(
                compartment["_name"], compartment["_id"], parent=compartment["_compartment_id"])
