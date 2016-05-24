#!/usr/bin/python
#
# Collection script to retrieve device metrics, and post to InfluxDB at regular intervals
#
# By:       barnesry@juniper.net
# Date :    18-May-2016
# Updated:  ---

from jnpr.junos import Device
from jnpr.junos.op.ethport import EthPortTable
from time import sleep
from influxdb import InfluxDBClient
import time
import logging

#############
# Constants #
#############
device_ip = "192.168.56.107"
user_name = "root"
password = "junos123"
sleep_time = 600        # interval between polls
logging_level = "DEBUG"

#############
# Functions #
#############
def get_current_time():
    localtime = time.localtime(time.time())
    logging.debug("Local current time :", localtime)
    return localtime


def get_rpm_history(device, db, sleep_time):
    # retrieve RPM results in XML table
    rpm_history = device.rpc.get_history_results()

    # find our test results in the returned XML
    probe_single_results = rpm_history.findall('.//probe-single-results')

    data_point = {}

    for results in probe_single_results:
        #time = get_current_time()

        # build our InfluxDB JSON
        for tag in ('owner', 'test-name', 'probe-time', 'probe-status', 'rtt'):
            elem = results.find(tag)

            if elem is not None:
                data_point[tag] = elem.text
            else:
                logging.warning("Element {} not returned".format(tag))
                data_point[tag] = 0     # we'll assume anything not found is zero for now

        point = [
            {
                'measurement': 'rpm_history',
                'tags': {
                    'device': device.facts[ 'fqdn' ],
                    'owner': data_point['owner'],
                    'test-name': data_point['test-name']
                },
                'time': data_point['probe-time'],
                'fields': {
                    'value': int(data_point['rtt'])
                }
            }
        ]

        #
        logging.debug(point)
        db.write_points(point)
    logging.info("Sleeping for {} seconds".format(sleep_time))
    sleep(sleep_time)


def get_port_stats(device, db, sleep_time):

    ports = ports_table.get()
    for port in ports:
        if port.name.startswith("ge"):
            point = [
                {
                    'measurement': 'port_counters',
                    'tags': {
                        'device': switch_name,
                        'port': port['name']
                    },
                    'fields': {
                        'rx_packets': int(port['rx_packets']),
                        'rx_bytes': int(port['rx_bytes']),
                        'tx_packets': int(port['tx_packets']),
                        'tx_bytes': int(port['tx_bytes'])
                    }
                }
            ]
            logging.debug(point)
            db.write_points(point)
    logging.info("Sleeping for {} seconds...".format(sleep_time))
    sleep(sleep_time)


##############
# MAIN BLOCK #
##############
def main():
    device = Device(host=device_ip, port=22, user=user_name, passwd=password)
    device.open()
    switch_name = device.facts[ 'fqdn' ]
    logging.info('Connected to', switch_name, '(', device.facts[ 'model' ], 'running', device.facts[ 'version' ])
    ports_table = EthPortTable(device)

    db = InfluxDBClient('localhost', 8086, 'root', 'root', 'network')
    logging.info('Connected to InfluxDB')

    logging.info('Staring metrics collection...')

    while True:
        # get_port_stats(device, db, sleep_time)
        get_rpm_history(device, db, sleep_time)


# executes only if not called as a module
if __name__ == "__main__":

   logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

   main()
