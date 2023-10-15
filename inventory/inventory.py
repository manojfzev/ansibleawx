import os
import subprocess

def get_dynamic_inventory():
  """Returns a dynamic inventory based on the following conditions:
    * IP range 10.138.0.2 - 10.138.0.4
    * OS environment variable "webservers"
    * Login credentials
  """

  # Get the IP range
  ip_range = range(10138002, 10138008)

  # Get the webservers environment variable
  webservers = os.environ.get("webservers")

  # Get the login credentials
  username = "ansible"
  password = "redhat"

  # Create a list of hosts
  hosts = []
  for ip in ip_range:
    if webservers is not None and ip in webservers:
      # SSH to the host to get the environment variables
      cmd = f"sshpass -p {password} ssh {username}@{ip} \"env\""
      proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
      output, err = proc.communicate()
      proc.wait()

      # Parse the environment variables from the output
      env_vars = dict(line.split("=") for line in output.decode("utf-8").split("\n"))

      # Add the host to the list, with the environment variables
      hosts.append({
        "hostname": ip,
        "ansible_user": username,
        "ansible_ssh_pass": password,
        "env_vars": env_vars
      })

  # Return the inventory
  return {
    "all": {
      "hosts": hosts,
    },
  }

# Print the inventory
print(get_dynamic_inventory())
