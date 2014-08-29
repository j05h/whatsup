#!.env/bin/python
"""Simulate usage

Seeds the database with dummy data
"""

import random
import subprocess

sites = ['US-TX', 'US-NC', 'EU-AERO', 'AUS-MEL']
services = ['nova', 'glance', 'neutron', 'cinder', 'swift']
messages = {'nominal': 1, 'reduced capabilities': 0, 'failed': -1}

for site in sites:
    for service in services:
        message = messages.keys()[random.randrange(0, 3)]

        syscmd = "curl -u admin:testing -H \"Content-Type: application/json\"\
-X POST -d \'{\"site\":\"" + site + "\",\"service\":\"" + service + "\",\
\"message\":\"" + message + "\",\"state\":%d}\'" % messages[message] + " \
localhost:5000/api/v1.0/status"
        print syscmd
        subprocess.Popen(syscmd, stdout=subprocess.PIPE,
                         shell=True).communicate()[0]
