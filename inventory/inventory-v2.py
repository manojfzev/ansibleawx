#!/usr/bin/env python

import os
import json
import socket
import subprocess
import time
from ipaddress import IPv4Network
import base64
import paramiko
from kubernetes import client, config
import io
import requests  # Import the requests library for making HTTP requests

# Define the IP range with a /29 subnet mask (covers 10.138.0.2 - 10.138.0.8)
ip_range = IPv4Network('10.138.0.0/24')

# Define the environment variable to check
desired_environment_variable = "webservers"

# Define the AWX API URL and your credentials
awx_api_url = "http://104.197.82.158:30707/api/v2/"
awx_api_token = "7lqhH27mTVJF3q1hDCFf9AwofcMCzo"  # Replace with your AWX API token

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
def environment_variable_exists(host, ssh_private_key):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the SSH private key
        private_key = io.StringIO(ssh_private_key)
        private_key = paramiko.RSAKey(file_obj=private_key)
        ssh.connect(host, username="ansible", pkey=private_key, timeout=5)

        # Run a command on the remote host to check the environment variable
        stdin, stdout, stderr = ssh.exec_command(f"echo ${desired_environment_variable}")
        result = stdout.read().decode().strip().lower()

        # Close the SSH connection
        ssh.close()

        return result
    except paramiko.ssh_exception.SSHException:
        return False
    except paramiko.ssh_exception.AuthenticationException:
        return False
    except subprocess.TimeoutExpired:
        return False

# Function to get SSH private key from AWX using its API
def get_ssh_private_key():
    headers = {
        "Authorization": f"Bearer {awx_api_token}",
        "Content-Type": "application/json",
    }
    url = f"{awx_api_url}credentials/10/"  # Replace <CREDENTIAL_ID> with the actual credential ID
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        credential_data = response.json()
        ssh_private_key = base64.b64decode(credential_data["inputs"]["fields"]["ssh_private_key"])
        return ssh_private_key.decode()
    else:
        return None

# Iterate through the IP range and check for hosts
for ip in ip_range.hosts():
    host = str(ip)
    try:
        socket.gethostbyaddr(host)
        
        # Retrieve the SSH private key from AWX
        ssh_private_key = get_ssh_private_key()

        if ssh_private_key and environment_variable_exists(host, ssh_private_key):
            inventory["webservers"]["hosts"].append(host)
            inventory["_meta"]["hostvars"][host] = {
                "ansible_ssh_user": "ansible"
            }
    except (socket.herror, TimeoutError):
        pass

# Print the JSON representation of the inventory
print(json.dumps(inventory, indent=2))