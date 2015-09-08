#!/usr/bin/env python

import requests, json, sys
from library.neutron import create_port
from library.keystone import get_token
from prettytable import PrettyTable
from pprint import pprint
from library.ltm import LTM

requests.packages.urllib3.disable_warnings()

ltm = LTM(hostname='192.0.2.13', username='user', password='pass', partition='test')


def listPools():
    poollist = ltm.get_pools()
    table = PrettyTable(["Pool Name", "State", "Description", "Load Balancing Mode", "Monitor", "Status", "Partition"])
    table.align["Pool Name"] = "l" # Left align pool name
    table.align["Description"] = "l" # Left align description


    # Test to see if there are any pools. If so, list them.
    if poollist.has_key('items'):
        for pool in poollist['items']:
            # Check pool stats
            status_code, poolstats = ltm.get_pool_stats(pool['name'])
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

def createVirtualServer(os_token, network_id):
    vip_addr = create_port(network_id)

    vs_name = "PROXY_VS_" + vip_addr
    vs_address = vip_addr
    vs_port = "80"

    status_code, json = ltm.create_virtual(os_token, vs_name,vs_address,vs_port)

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
        print "Error: %s. %s" % (status_code, json['message'])

def deletePool(name):
    status_code = ltm.delete_pool(name)

    if (status_code == 200):
        print "Deleted Pool: " + name
    else:
        print status_code

def addPoolMember(pool_name, member_ip, member_port):
    status_code, response = ltm.add_pool_member(pool_name, member_ip, member_port)

    if (status_code == 200):
        print "\nAdded Pool Member."
        table = PrettyTable(["Field", "Value"])
        table.align["Field"] = "r"
        table.align["Value"] = "l"
        table.add_row(["Pool:",pool_name])
        table.add_row(["Name:",member_ip+':'+member_port])
        table.add_row(["Address:",member_ip])
        table.add_row(["Port:",member_port])
        print table
    else:
        print "Error: %s. %s" % (status_code, response['message'])

def delPoolMember(pool_name, member_ip, member_port):
    status_code, response = ltm.del_pool_member(pool_name, member_ip, member_port)

    if (status_code == 200):
        print "\nOperation Successful: Removed pool member from %s" % pool_name
    else:
        print "Error: %s. %s" % (status_code,response['message'])

def attachPoolToVirtual(vs_name,pool_name):
    status_code, response = ltm.attach_pool_to_virtual(vs_name,pool_name)

    if (status_code ==200):
        print "\rAttached pool %s to virtual server %s" % (pool_name, vs_name)
    else:
        print "Error: %s. %s" % (status_code,response['message'])

def showPoolStats(name):
    status_code, poolstats = ltm.get_pool_stats(name)

    if (status_code == 200):
        state = poolstats['entries']['status.enabledState']['description']
        status = poolstats['entries']['status.availabilityState']['description']
        activeMemberCnt = poolstats['entries']['activeMemberCnt']['value']
        bitsIn = poolstats['entries']['serverside.bitsIn']['value']
        bitsOut = poolstats['entries']['serverside.bitsOut']['value']
        curConns = poolstats['entries']['serverside.curConns']['value']
        maxConns = poolstats['entries']['serverside.maxConns']['value']
        pktsIn = poolstats['entries']['serverside.pktsIn']['value']
        pktsOut = poolstats['entries']['serverside.pktsOut']['value']
        totConns = poolstats['entries']['serverside.totConns']['value']

        table = PrettyTable(["Pool Name", "State", "Status", "Active Members", "Bits In", "Bits Out", "Packets In", "Packets Out", "Current Conns", "Max Conns", "Total Conns"])
        table.align["Pool Name"] = "l" # Left align pool name
        table.add_row([name,state,status,activeMemberCnt,bitsIn,bitsOut,pktsIn,pktsOut,curConns,maxConns,totConns])

        print table
    else:
        print "Error: %s. %s" % (status_code, poolstats['message'])

def main():
    os_token = get_token()
    #print os_token

    if len(sys.argv) > 1:
        if (sys.argv[1] == "pool-list"):
            listPools()
        if (sys.argv[1] == "virtual-server-list"):
            listVirtualServers()
        if (sys.argv[1] == "pool-member-list"):
            listPoolMembers(sys.argv[2])
        if (sys.argv[1] == "virtual-server-create"):
            if (sys.argv[2] == "--auto"):
                createVirtualServer(os_token, sys.argv[3])
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
        if (sys.argv[1] == "pool-stats"):
            if len(sys.argv) < 3:
                print "Syntax: pool-stats <pool_name>"
            else:
                showPoolStats(sys.argv[2])
        if (sys.argv[1] == "pool-member-add"):
            if len(sys.argv) < 5:
                print "Syntax: pool-member-add <pool_name> <ip_address> <port>"
            else:
                addPoolMember(sys.argv[2], sys.argv[3], sys.argv[4])
        if (sys.argv[1] == "pool-member-remove"):
            if len(sys.argv) < 5:
                print "Syntax: pool-member-remove <pool_name> <ip_address> <port>"
            else:
                delPoolMember(sys.argv[2], sys.argv[3], sys.argv[4])
        if (sys.argv[1] == "pool-attach"):
            if len(sys.argv) < 4:
                print "Syntax: pool-attach <virtual_server_name> <pool_name>"
            else:
                attachPoolToVirtual(sys.argv[2], sys.argv[3])
    else:
        print "No command specified. Available commands include:"
        print ""
        print "Virtual Servers:"
        print "virtual-server-list"
        print "virtual-server-create --auto NETWORK_UUID"
        print "pool-attach VS_NAME POOL_NAME"  
        print ""
        print "Pools:"
        print "pool-list"
        print "pool-create POOL_NAME LB_METHOD MONITOR"
        print "pool-delete POOL_NAME"
        print "pool-stats POOL_NAME"
        print "pool-member-list POOL_NAME"
        print "pool-member-add POOL_NAME IP_ADDRESS PORT"
        print "pool-member-remove POOL_NAME IP_ADDRESS PORT"
        print ""  

if __name__ == "__main__":
        main()
