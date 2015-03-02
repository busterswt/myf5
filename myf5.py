#!/usr/bin/env python

import requests, json, sys
from library.neutron import create_port
from prettytable import PrettyTable
from pprint import pprint
from library.ltm import LTM

requests.packages.urllib3.disable_warnings()

ltm = LTM(hostname='10.240.0.248', username='proxyuser', password='proxypass', partition='test')


def listPools():
    poollist = ltm.get_pools()
    table = PrettyTable(["Pool Name", "Description", "Load Balancing Mode", "Partition"])
    table.align["Pool Name"] = "l" # Left align pool name
    table.align["Description"] = "l" # Left align description

    for pool in poollist['items']:
        if not pool.has_key('description'):
            pool['description'] = "None"
        table.add_row([pool['name'],pool['description'],pool['loadBalancingMode'],pool['partition']])

    print table
#        print pool['name']
#    for items,name in poollist.items():
#        print items,name

#print json.dumps(poollist["name"])

def listPoolMembers(pool):
    memberlist = ltm.get_pool_members(pool)
    print "\nPool Name:  " + pool
    table = PrettyTable(["Member Name", "Address", "Monitor", "State", "Partition"])
    table.align["Member Name"] = "l"

    for member in memberlist['items']:
        table.add_row([member['name'],member['address'],member['monitor'],member['state'],member['partition']])
    print table

def listVirtualServers():
    virtualserverlist = ltm.get_virtuals()
    table = PrettyTable(["Virtual Server Name", "Description", "Destination", "Pool", "Partition"])
    table.align["Virtual Server Name"] = "l" # Left align virtual server name

    for virtual in virtualserverlist['items']:
        if not virtual.has_key('description'):
            virtual['description'] = "None"
        if not virtual.has_key('pool'):
            virtual['pool'] = "None"
        table.add_row([virtual['name'],virtual['description'],virtual['destination'],virtual['pool'],virtual['partition']])

    print table

def createVirtualServer(network_id):
    vip_addr = create_port(network_id)

    vs_name = "PROXY_VS_" + vip_addr
    vs_address = vip_addr
    vs_port = "80"

    status_code, json = ltm.create_virtual(vs_name,vs_address,vs_port)

    if (status_code == 200):
        print "\nCreated Virtual Server:  " + vs_name
        table = PrettyTable(["Field", "Value"])
        table.align["Field"] = "r"
        table.align["Value"] = "l"
        table.add_row(["Name:",vs_name])
        table.add_row(["Address:",vs_address])
        table.add_row(["Port:",vs_port])
        print table
    else:
        print status_code

def main():
    if len(sys.argv) > 1:
        if (sys.argv[1] == "pool-list"):
            listPools()
        if (sys.argv[1] == "virtual-server-list"):
            listVirtualServers()
        if (sys.argv[1] == "pool-member-list"):
            listPoolMembers(sys.argv[2])
        if (sys.argv[1] == "virtual-server-create"):
            if (sys.argv[2] == "--auto"):
                createVirtualServer(sys.argv[3])

if __name__ == "__main__":
        main()
