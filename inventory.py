#!/usr/bin/env python
import json

# Define the IP range
ip_range_start = 2
ip_range_end = 4

def generate_inventory():
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": [],
            "children": []
        }
    }

    for i in range(ip_range_start, ip_range_end + 1):
        host = f"10.138.0.{i}"
        inventory["all"]["hosts"].append(host)
        inventory["_meta"]["hostvars"][host] = {
            # You can define host-specific variables here if needed
        }

    print(json.dumps(inventory))

if __name__ == "__main__":
    generate_inventory()
