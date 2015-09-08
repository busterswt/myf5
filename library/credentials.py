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
        print ("Environment variable %s is not set!") % e
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
        print ("Environment variable %s is not set!") % e
        sys.exit(1)
