import json
import requests

NUTANIX_API_URL = "https://nxeqch3prism.sysco.net:9440/api/nutanix/v3/vms/list"
NUTANIX_USERNAME = "svc_nutanix@na.sysco.net"
NUTANIX_PASSWORD = os.environ.get('NUTANIX_PASSWORD')

def get_nutanix_servers():
    auth = (NUTANIX_USERNAME, NUTANIX_PASSWORD)
    headers = {"Content-Type": "application/json"}
    payload = {    
        "kind": "vm",
        "offset": 0,
        "length":5,  
        "sort_order": "ASCENDING",
        "sort_attribute": "string"
    }     
    
    response = requests.post(NUTANIX_API_URL, auth=auth, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch Nutanix server information.")
        return None

def adding_servers(nutanix_servers):
    ansible_inventory = {
        "all": {"hosts": []},
        "_meta": {"hostvars": {}},
        "windows": {"hosts": []},
        "linux": {"hosts": []}
    }

    vms = nutanix_servers.get('entities', [])    
    for vm in vms:
        vm_name = vm.get('status', {}).get('name')
        ngt_check = vm.get('status').get('resources', {}).get("guest_tools")
        if ngt_check == None:
            print("Skipping adding" + " " + vm_name + " " + "guest tool not available")
        else:
            ngt_state = ngt_check.get("nutanix_guest_tools").get("ngt_state")
            if ngt_state == "UNINSTALLED":
                print("Skipping adding" + " " + vm_name + " " + "guest tool has been uninstalled ")
            else:
                os_version = ngt_check.get("nutanix_guest_tools").get('guest_os_version')
                if "windows" in os_version or "linux" in os_version:
                    power_state = vm.get('status').get('resources', {}).get('power_state')
                    
                    # Check for the existence of 'nic_list' and 'ip_endpoint_list'
                    nic_list = vm.get('status', {}).get('resources', {}).get('nic_list', [])
                    if nic_list:
                        ip_list = nic_list[0].get('ip_endpoint_list', [])
                        
                        if ip_list:
                            ip_addr = ip_list[0].get('ip')
                            if ip_addr is not None:
                                ansible_inventory["all"]["hosts"].append(vm_name)
                                ansible_inventory["_meta"]["hostvars"][vm_name] = {"ansible_host": ip_addr}
                                
                                if "windows" in os_version:
                                    ansible_inventory["windows"]["hosts"].append(vm_name)
                                elif "linux" in os_version:
                                    ansible_inventory["linux"]["hosts"].append(vm_name)
                            else:
                                print("Skipping adding" + " " + vm_name + " " + "since IP address is not available")
                        else:
                            print("Skipping adding" + " " + vm_name + " " + "since IP endpoint list is empty")
                    else:
                        print("Skipping adding" + " " + vm_name + " " + "since NIC list is empty")

    return json.dumps(ansible_inventory, indent=2)

if __name__ == "__main__":
    nutanix_servers = get_nutanix_servers()
    ansible_inventory_json = adding_servers(nutanix_servers)
    print(ansible_inventory_json)
