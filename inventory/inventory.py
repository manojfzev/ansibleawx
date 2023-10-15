#!/usr/bin/env python

import json
import os

# Define the IP range
ip_range = range(2, 9)  # IP addresses 10.138.0.2 to 10.138.0.8

# Fetch the value of the environment variable "webservers"
webservers_env = os.environ.get('webservers', 'false')

# Define the Ansible SSH user and SSH password to be used for all hosts
ansible_ssh_user = "ansible"
ssh_password = "redhat"

# Create an empty dictionary to store host variables
hostvars = {}

# Create the inventory structure
inventory = {
    "_meta": {
        "hostvars": hostvars
    },
    "all": {
        "hosts": [f"10.138.0.{ip}" for ip in ip_range]
    }
}

# Set the Ansible SSH user, SSH password, and any additional variables based on the "webservers" environment variable
for host in inventory["all"]["hosts"]:
    hostvars[host] = {
        "ansible_ssh_user": ansible_ssh_user,
        "ansible_ssh_pass": ssh_password,
        "webservers": webservers_env
    }

print(json.dumps(inventory))
