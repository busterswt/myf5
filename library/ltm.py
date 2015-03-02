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
        resp = self.bigip.get('%s/ltm/pool' % self.url_base)
        return json.loads(resp.text)

    def get_pool_members(self, pool):
        resp = self.bigip.get('%s/ltm/pool/%s/members' % (self.url_base, pool))
        return json.loads(resp.text)

    def get_virtuals(self):
        resp = self.bigip.get('%s/ltm/virtual' % self.url_base)
        return json.loads(resp.text)

    def create_virtual(self, name, address, port):
        payload = {}

        # Define virtal server properties
        payload['kind'] = 'tm:ltm:virtual:virtualstate'
        payload['partition'] = self.partition
        payload['name'] = name
        payload['description'] = 'Sample Virtual Server'
        payload['destination'] = '%s:%s' % (address, port)
        payload['mask'] = '255.255.255.255'
        payload['ipProtocol'] = 'tcp'
        payload['sourceAddressTranslation'] = { 'type' : 'automap' }
        payload['profiles'] = [
            { 'kind' : 'ltm:virtual:profile', 'name' : 'http' },
            { 'kind' : 'ltm:virtual:profile', 'name' : 'tcp' }
        ]

        resp = self.bigip.post('%s/ltm/virtual' % self.url_base, data=json.dumps(payload))
        return resp.status_code, json.loads(resp.text)

    def get_nodes(self):
        resp = self.bigip.get('%s/ltm/node' % self.url_base)
        return resp.json()['items']

    def disable_node(self, node):
        payload = { 'session': 'user-disabled' }
        resp = self.bigip.put('%s/ltm/node/%s' % (self.url_base, node), data=json.dumps(payload))
        resp.raise_for_status()
        return resp.json()

    def enable_node(self, node):
        payload = { 'session': 'user-enabled' }
        resp = self.bigip.put('%s/ltm/node/%s' % (self.url_base, node), data=json.dumps(payload))
        resp.raise_for_status()
        return resp.json()

    def sync_nodes(self, device_group):
        payload = { 'command': 'run', 'utilCmdArgs': 'confg-sync to-group %s' % device_group }
        resp = self.bigip.post('%s/cm', data=json.dumps(payload))
        resp.raise_for_status()
        return resp.json()
