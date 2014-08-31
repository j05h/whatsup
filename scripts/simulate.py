#!.env/bin/python
"""Simulate usage

Seeds the database with dummy data
"""

import random
import subprocess
import requests
import json

sites = ['US-TX', 'US-NC', 'EU-AERO', 'AUS-MEL']
services = ['nova', 'glance', 'neutron', 'cinder', 'swift']
messages = {'nominal': 1, 'reduced capabilities': 0, 'failed': -1}
url = 'http://localhost:5000/api/v1.0/status'
headers = {'content-type': 'application/json'}
auth = ('admin', 'testing')

for site in sites:
    for service in services:
        message = messages.keys()[random.randrange(0, 3)]
        payload = {'site': site, 'service': service, 'message': message,
                   'state': messages[message]}
        r = requests.post(url, data=json.dumps(payload), headers=headers,
                          auth=auth)
        print(r.text)
