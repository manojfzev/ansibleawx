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

# Define the IP range with a /29 subnet mask (covers 10.138.0.2 - 10.138.0.8)
ip_range = IPv4Network('10.138.0.0/24')

# Define the environment variable to check
desired_environment_variable = "webservers"

# Define SSH credentials
ssh_username = "ansible"
ssh_private_key_secret = "ssh-key-secret"  # Name of the Kubernetes Secret
ssh_timeout = 5  # Set the SSH timeout in seconds
ssh_private_key_secret_namespace = "awx"

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
        # Configure the Kubernetes client using an in-cluster config
        config.load_incluster_config()
        
        # Create a Kubernetes API client
        v1 = client.CoreV1Api()

        # Retrieve the SSH private key from the Kubernetes Secret
        secret = v1.read_namespaced_secret(name=ssh_private_key_secret, namespace=ssh_private_key_secret_namespace)
        ssh_private_key_base64 = secret.data["ssh-privatekey"]
        ssh_private_key = base64.b64decode(ssh_private_key_base64).decode()
        

        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the SSH private key from the Secret
        private_key = io.StringIO(ssh_private_key)
        private_key = paramiko.RSAKey(file_obj=private_key)
        ssh.connect(host, username=ssh_username, pkey=private_key, timeout=ssh_timeout)

        # Run a command on the remote host to check the environment variable
        stdin, stdout, stderr = ssh.exec_command("echo $" + desired_environment_variable)
        result = stdout.read().decode().strip().lower()

        # Close the SSH connection
        ssh.close()

        return result
    except (paramiko.ssh_exception.SSHException, client.rest.ApiException):
        return False
    except paramiko.ssh_exception.AuthenticationException:
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