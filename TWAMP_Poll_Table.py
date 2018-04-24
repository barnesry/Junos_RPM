from jnpr.junos import Device
from jnpr.junos.factory.factory_loader import FactoryLoader
import yaml
import json
from time import sleep
from influxdb import InfluxDBClient
import time ,sys
import logging
import argparse

myYAML = """
---
twampHistoryResults:
  rpc: twamp-get-history-results
  args:
    extensive: False
  key: test-name
  item: history-test-results/probe-single-results
  view: probeSingleResults

probeSingleResults:
  fields:
    owner: owner
    test_name: test-name
    rtt: rtt
    probe_sent_time: probe-sent-time
    probe_time: probe-time
    egress_jitter: egress-jitter
    ingress_jitter: ingress-jitter
    round_trip_jitter: round-trip-jitter
"""

def get_rpm_history(device, db, sleep_time):


    users = twampHistoryResults(device)
    device.timeout = 120
    users.get()
    data_point = {}

    #db = InfluxDBClient('10.0.0.2', 8086, 'influx', 'influx', 'rpm_history')

    for value_list in users.values():
        for value_tuple in value_list:
            if value_tuple[1] is None:
                data_point[value_tuple[0]] = 0
            else:
                data_point[value_tuple[0]] = value_tuple[1]
        point = [
            {
                'measurement': 'rpm_history',
                'tags': {
                'device': device.facts[ 'fqdn' ],
                'owner': data_point['owner'],
                'test-name': data_point['test_name']
            },
                'time': data_point['probe_time'],
                'fields': {
                'rtt': int(data_point['rtt']),
                'e_jitter': int(data_point['egress_jitter']),
                'i_jitter': int(data_point['ingress_jitter']),
                'rt_jitter': int(data_point['round_trip_jitter'])
                }
            }
        ]

        result = db.write_points(point)
    logging.info("Sleeping for {} seconds".format(sleep_time))
    n = sleep_time
    for i in range(n):
        n, dots = n%4+1, list(' ...')
        dots[n-1]=' '
        sys.stdout.write('\rSleeping'+ ''.join(dots))
        sys.stdout.flush()
        time.sleep(0.5)

def parse_args():
    parser = argparse.ArgumentParser(
    description='Arguments for RPM Polling')
    parser.add_argument('--target', type=str, required=False, default='10.0.01',
                        help='default IP to log into Juniper SRX')
    parser.add_argument('--username', type=str, required=False, default='test',
                        help='default username to log into Juniper SRX')
    parser.add_argument('--password', type=str, required=False, default='test',
                        help='default password to log into Juniper SRX')
    parser.add_argument('--influx', type=str, required=False, default='10.0.0.2',
                        help='InfluxDB server IP to log into')
    parser.add_argument('--dbuser', type=str, required=False, default='influx',
                        help='default username to log into InfluxDB')
    parser.add_argument('--dbpass', type=str, required=False, default='influx',
                        help='default password to log into InfluxDB')
    return parser.parse_args()


def main(target,username,password):
    device = Device(host=target, port=22, user=username, passwd=password)
    device.open()
    device_name = device.facts[ 'fqdn' ]
    globals().update(FactoryLoader().load(yaml.load(myYAML)))
    logging.info('Connected to {}, {} running {}'.format(device_name,
                                                         device.facts['model'],
                                                        device.facts[ 'version' ]))

    db = InfluxDBClient(args.influx, 8086, args.dbuser, args.dbpass, 'rpm_history')
    logging.info('Connected to InfluxDB')

    logging.info('Staring metrics collection...')

    while True:
        print "Data Collection Started"
        get_rpm_history(device, db, sleep_time)


if __name__ == "__main__":
    print "Starting TWAMP RPM History Collection"
    sleep_time = 300                # interval between polls
    logging_level = logging.CRITICAL

    #Level 	Numeric value
    #CRITICAL 	50
    #ERROR 	40
    #WARNING 	30
    #INFO 	20
    #DEBUG 	10
    #NOTSET 	0

    args = parse_args()
    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

    main(target=args.target, username=args.username, password=args.password)
