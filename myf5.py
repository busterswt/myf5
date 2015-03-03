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
    table = PrettyTable(["Pool Name", "State", "Description", "Load Balancing Mode", "Monitor", "Status", "Partition"])
    table.align["Pool Name"] = "l" # Left align pool name
    table.align["Description"] = "l" # Left align description


    # Test to see if there are any pools. If so, list them.
    if poollist.has_key('items'):
        for pool in poollist['items']:
            # Check pool stats
            poolstats = ltm.get_pool_stats(pool['name'])
            pool_state = poolstats['entries']['status.enabledState']['description']
            pool_status = poolstats['entries']['status.availabilityState']['description']

            # Check for the existence of particular keys
            if not pool.has_key('description'):
                pool['description'] = "None"
            if not pool.has_key('monitor'):
                pool['monitor'] = "None"
            table.add_row([pool['name'],pool_state,pool['description'],pool['loadBalancingMode'],pool['monitor'],pool_status,pool['partition']])
    else:
        table.add_row(["There are no pools.","","","","","",""])

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

def createPool(name, lb_method, monitor):
    status_code, json = ltm.create_pool(name, lb_method, monitor)

    if (status_code == 200):
        print "\nCreated Pool: " + name
        table = PrettyTable(["Field", "Value"])
        table.align["Field"] = "r"
        table.align["Value"] = "l"
        table.add_row(["Name:",name])
        table.add_row(["Load Balancing Method:",lb_method])
        table.add_row(["Monitor",monitor])
        print table
    else:
        print status_code

def deletePool(name):
    status_code = ltm.delete_pool(name)

    if (status_code == 200):
        print "Deleted Pool: " + name
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
        if (sys.argv[1] == "pool-create"):
            if len(sys.argv) < 5:
                print "Syntax: pool-create <pool_name> <lb_method> <monitor>"
            else:
                createPool(sys.argv[2], sys.argv[3], sys.argv[4])
        if (sys.argv[1] == "pool-delete"):
            if len(sys.argv) < 3:
                print "Syntax: pool-delete <pool_name>"
            else:
                deletePool(sys.argv[2])
    else:
        print "No command specified"


if __name__ == "__main__":
        main()
