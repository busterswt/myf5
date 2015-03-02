import requests, json, sys
from neutronclient.v2_0 import client
from credentials import get_credentials

def create_port(network_id):
    credentials = get_credentials()
    neutron = client.Client(**credentials)

    body_value = {
        "port": {
            "admin_state_up": True,
            "name": "VIP",
            "network_id": network_id
         }
    }

    response = neutron.create_port(body=body_value)
    #print json.dumps(response, sort_keys=True, indent=4) // Debug Example
    return response["port"]["fixed_ips"][0]["ip_address"]
    #return json.dumps(response["port"]["fixed_ips"][0]["ip_address"])
