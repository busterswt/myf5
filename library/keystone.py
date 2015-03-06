import requests, json, sys
from keystoneclient import session as keystone_session
from keystoneclient.v2_0 import client
from credentials import get_credentials

def get_token():
    credentials = get_credentials()
    keystone = client.Client(**credentials)

    token = keystone.get_raw_token_from_identity_service(**credentials)
    return token["token"]["id"]
