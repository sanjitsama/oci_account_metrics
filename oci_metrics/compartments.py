#! /usr/bin/python3
import oci
import json
import os


def get_compartments(*args):
    [identity, config, account] = args
    all_comps = [c.__dict__ for c in list(identity.list_compartments(
        config["tenancy"], compartment_id_in_subtree=True, access_level="ANY").data) if c.__dict__["_lifecycle_state"] != "DELETED"]
    comps = list(map(lambda curr: dict([(k, v) for (k, v) in curr.items(
    ) if (k != "attribute_map" and k != "swagger_types")]), all_comps))
    output_dir = os.path.join(os.getcwd(), "output_files/")
    with open(os.path.join(output_dir, "parent_compartments.json"), 'w') as f:
        f.write(json.dumps(comps, indent=4,
                           sort_keys=True, default=str))
    return comps


def get_compartment_tree(rootcomps, *args):
    [identity, config, account] = args
    next_comps = []
    for comp in rootcomps:
        next_all_comps = [c.__dict__ for c in list(identity.list_compartments(
            comp["_compartment_id"], access_level="ANY").data) if c.__dict__["_lifecycle_state"] != "DELETED"]
        next_comps.extend(list(map(lambda curr: dict([(k, v) for (k, v) in curr.items(
        ) if (k != "attribute_map" and k != "swagger_types")]), next_all_comps)))
    output_dir = os.path.join(os.getcwd(), "output_files/")
    with open(os.path.join(output_dir, "child_compartments.json"), 'w') as f:
        f.write(json.dumps(next_comps, indent=4,
                           sort_keys=True, default=str))
    return next_comps
