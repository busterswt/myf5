#!/usr/bin/env python
import os, sys

def get_credentials():
    d = {}
    try:
        d['username'] = os.environ['OS_USERNAME']
        d['password'] = os.environ['OS_PASSWORD']
        d['auth_url'] = os.environ['OS_AUTH_URL']
        d['tenant_name'] = os.environ['OS_TENANT_NAME']
        return d
    except KeyError, e:
        print ("Openstack environment variable %s is not set!") % e
        sys.exit(1)

def get_nova_credentials():
    d = {}
    try:
        d['username'] = os.environ['OS_USERNAME']
        d['api_key'] = os.environ['OS_PASSWORD']
        d['auth_url'] = os.environ['OS_AUTH_URL']
        d['project_id'] = os.environ['OS_TENANT_NAME']
        return d
    except KeyError, e:
        print ("OpenStack environment variable %s is not set!") % e
        sys.exit(1)

def get_f5_credentials():
    d = {}
    try:
        d['f5_username'] = os.environ['F5_USERNAME']
        d['f5_password'] = os.environ['F5_PASSWORD']
        d['f5_endpoint'] = os.environ['F5_ENDPOINT']
        d['f5_partition'] = os.environ['F5_PARTITION']
        return d
    except KeyError, e:
        print ("F5 environment variable %s is not set!") % e
        sys.exit(1)
