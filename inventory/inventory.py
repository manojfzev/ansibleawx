#!/usr/bin/env python

import os
import json

# Define the IP range
ip_range = range(2, 5)  # IP addresses 10.138.0.2 to 10.138.0.4

# Fetch the value of the OS-level environment variable
environment_variable = os.environ.get('webservers', 'false')

# Define hosts based on the IP range and environment variable
inventory = {
    "_meta": {
        "hostvars": {}
    },
    "webservers": {
        "hosts": [
            f"10.138.0.{ip}" for ip in ip_range if environment_variable == 'true'
        ]
    }
}

print(json.dumps(inventory))
