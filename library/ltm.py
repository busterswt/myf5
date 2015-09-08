import requests, json
requests.packages.urllib3.disable_warnings()

class LTM:
    """A basic class for interacting with F5's Local Traffic
    manager."""

    def __init__(self, hostname, username, password, partition):
        self.url_base = 'https://%s/mgmt/tm' % hostname
        self.bigip = requests.session()
        self.bigip.auth = (username, password)
        self.bigip.verify = False
        self.bigip.headers.update({'Content-Type': 'application/json'})
        self.partition = partition

    def get_pools(self):
        resp = self.bigip.get('%s/ltm/pool?$filter=partition eq %s' % (self.url_base, self.partition))
        return json.loads(resp.text)

    def get_pool_stats(self, pool):
        resp = self.bigip.get('%s/ltm/pool/~%s~%s/stats' % (self.url_base, self.partition, pool))
        return resp.status_code, json.loads(resp.text)

    def get_pool_members(self, pool):
        resp = self.bigip.get('%s/ltm/pool/~%s~%s/members' % (self.url_base, self.partition, pool))
        return json.loads(resp.text)

    def get_virtuals(self):
        resp = self.bigip.get('%s/ltm/virtual?$filter=partition eq %s' % (self.url_base, self.partition))
        return json.loads(resp.text)

    def create_virtual(self, os_token, name, address, port):
        headers = {'X-Auth-Token': os_token}

        payload = {}

        # Define virtal server properties
        payload['kind'] = 'tm:ltm:virtual:virtualstate'
        payload['partition'] = self.partition
        payload['name'] = name
        payload['description'] = 'Created by F5 Proxy'
        payload['destination'] = '%s:%s' % (address, port)
        payload['mask'] = '255.255.255.255'
        payload['ipProtocol'] = 'tcp'
        payload['sourceAddressTranslation'] = { 'type' : 'automap' }
        payload['profiles'] = [
            { 'kind' : 'ltm:virtual:profile', 'name' : 'http' },
            { 'kind' : 'ltm:virtual:profile', 'name' : 'tcp' }
        ]

        resp = self.bigip.post('%s/ltm/virtual' % self.url_base, data=json.dumps(payload), headers=headers)
        return resp.status_code, json.loads(resp.text)

    def create_pool(self, name, lb_method, monitor):
        payload = {}

        # Define pool properties
        payload['kind'] = 'tm:ltm:pool:poolstate'
        payload['partition'] = self.partition
        payload['name'] = name
        payload['description'] = 'Created by F5 Proxy'
        payload['loadBalancingMode'] = lb_method
        payload['monitor'] = monitor

        resp = self.bigip.post('%s/ltm/pool' % self.url_base, data=json.dumps(payload))
        return resp.status_code, json.loads(resp.text)

    def add_pool_member(self, pool_name, member_ip, member_port):
        payload = {}

        # Define pool member properties
        payload['partition'] = self.partition
        payload['name'] = member_ip+':'+member_port
        payload['description'] = 'Created by F5 Proxy'
        payload['address'] = member_ip

        resp = self.bigip.post('%s/ltm/pool/~%s~%s/members/' % (self.url_base,self.partition,pool_name), data=json.dumps(payload))
        return resp.status_code, json.loads(resp.text)

    def del_pool_member(self, pool_name, member_ip, member_port):
        resp = self.bigip.delete('%s/ltm/pool/~%s~%s/members/%s:%s' % (self.url_base,self.partition,pool_name,member_ip,member_port))

        # Test to see if the operation was successful. BIGIP does not return JSON on 200 OK
        if not resp.text:
            return resp.status_code, False
        else:
            return resp.status_code, json.loads(resp.text)

    def attach_pool_to_virtual(self, vs_name, pool_name):
        payload = {}

        payload['kind'] = 'tm:ltm:virtual:virtualstate'
        payload['pool'] = pool_name
        payload['partition'] = self.partition

        resp = self.bigip.put('%s/ltm/virtual/~%s~%s/' % (self.url_base,self.partition,vs_name), data=json.dumps(payload))
        return resp.status_code, json.loads(resp.text)

    def delete_pool(self, name):
        resp = self.bigip.delete('%s/ltm/pool/~%s~%s'  % (self.url_base,self.partition,name))
        return resp.status_code

    def get_nodes(self):
        resp = self.bigip.get('%s/ltm/node?$filter=partition eq %s' % (self.url_base, self.partition))
        return resp.json()['items']

    def disable_node(self, node):
        payload = { 'session': 'user-disabled' }
        resp = self.bigip.put('%s/ltm/node/~%s~%s' % (self.url_base, node), self.partition, data=json.dumps(payload))
        resp.raise_for_status()
        return resp.json()

    def enable_node(self, node):
        payload = { 'session': 'user-enabled' }
        resp = self.bigip.put('%s/ltm/node/~%s~%s' % (self.url_base, node), self.partition, data=json.dumps(payload))
        resp.raise_for_status()
        return resp.json()

    def sync_nodes(self, device_group):
        payload = { 'command': 'run', 'utilCmdArgs': 'config-sync to-group %s' % device_group }
        resp = self.bigip.post('%s/cm' % self.url_base, data=json.dumps(payload))
        return resp.status_code, json.loads(resp.text)

    def get_device_stats(self):
        resp = self.bigip.get('%s/cm/traffic-group/stats' % self.url_base)
#        return resp.status_code, json.loads(resp.text)
        return resp.status_code, resp.json()
