#!/usr/bin/python

device_ip = "192.168.56.101"
user_name = "root"
password = "junos123"

from jnpr.junos import Device
from jnpr.junos.op.ethport import EthPortTable
from time import sleep
from influxdb import InfluxDBClient

device = Device(host=device_ip, port=22, user=user_name, passwd=password)
device.open()
switch_name = device.facts['fqdn']
print 'Connected to', switch_name, '(', device.facts['model'], 'running', device.facts['version'], ')'
ports_table = EthPortTable(device)

db = InfluxDBClient('localhost', 8086, 'root', 'root', 'network')
print 'Connected to InfluxDB'

print 'Collecting metrics...'
columns = ['rx_packets', 'rx_bytes', 'tx_packets', 'tx_bytes']

json_body = [
    {
        "measurement": "cpu_load_short",
        "tags": {
            "host": "server01",
            "region": "us-west"
        },
        "time": "2009-11-10T23:00:00Z",
        "fields": {
            "value": 0.64
        }
    }
]

while True:
    ports = ports_table.get()
    for port in ports:
        if port.name.startswith("ge"):
            point = [
                {
                    'measurement': 'port_counters',
                    'tags': {
                        'device':   switch_name,
                        'port':     port['name']
                    },
                    'fields': {
                            'rx_packets':   int(port['rx_packets']),
                            'rx_bytes':     int(port['rx_bytes']),
                            'tx_packets':   int(port['tx_packets']),
                            'tx_bytes':     int(port['tx_bytes'])
                    }
                }
            ]
            print point
            db.write_points(point)
        sleep(1)