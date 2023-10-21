#!/usr/bin/env python

import os
import json
import socket
import subprocess
import time
from ipaddress import IPv4Network

# Define the IP range with a /29 subnet mask (covers 10.138.0.2 - 10.138.0.8)
ip_range = IPv4Network('10.138.0.0/24')

# Define the environment variable to check
desired_environment_variable = "webservers"

# Define SSH credentials
ssh_username = "ansible"
ssh_private_key = os.environ.get('ansible_private_key_file')
ssh_timeout = 5  # Set the SSH timeout in seconds

# Initialize an empty inventory
inventory = {
    "_meta": {
        "hostvars": {}
    },
    "webservers": {
        "hosts": []
    }
}

# Function to check if the environment variable exists on a host
def environment_variable_exists(host):
    try:
        cmd = ["ssh", "-i", ssh_private_key_file, "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=" + str(ssh_timeout), ssh_username + "@" + host, "echo $" + desired_environment_variable]
        output = subprocess.check_output(cmd, timeout=ssh_timeout)
        return output.decode().strip().lower()
    except subprocess.CalledProcessError:
        return False
    except subprocess.TimeoutExpired:
        return False

# Iterate through the IP range and check for hosts
for ip in ip_range.hosts():
    host = str(ip)
    try:
        socket.gethostbyaddr(host)
        if environment_variable_exists(host):
            inventory["webservers"]["hosts"].append(host)
            inventory["_meta"]["hostvars"][host] = {
                "ansible_ssh_user": ssh_username
            }
    except (socket.herror, TimeoutError):
        pass

# Print the JSON representation of the inventory
print(json.dumps(inventory, indent=2))