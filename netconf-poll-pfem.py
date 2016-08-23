#!/usr/bin/python
#
# Collection script to retrieve device metrics, and post to InfluxDB at regular intervals
#
# By:       barnesry@juniper.net
# Date :    18-May-2016
#
# DATE          VERSION COMMENTS
# 20-Aug-2016   0.1     added threading to support comma separated IP list as CLI arg
#
# USAGE:
# barnesry-mbp:Junos_RPM barnesry$ ./netconf-poll-pfem.py --target 172.25.45.160,172.25.45.161,172.25.45.162,172.25.45.163,172.25.45.164 --username barnesry --password Whisky:Tango:Foxtrot



from jnpr.junos import Device
from jnpr.junos.op.ethport import EthPortTable
from time import sleep
from influxdb import InfluxDBClient
import time, logging, argparse, re, threading
from datetime import datetime

#############
# Constants #
#############
device_ip = "10.66.1.153"
user_name = "root"
password = 'junos123'
sleep_time = 10        # interval between polls
logging_level = logging.WARN
epoch = datetime.utcfromtimestamp(0)

#############
# Functions #
#############
class Device(Device):
    # extends jnpr.junos.Device
    def get_pfem(self):
        pfem_process = self.get_system_processes('pfem')
        return pfem_process

    def get_system_processes(self, process='pfem'):
        processes = self.cli("show system processes extensive", format='text', warning=False)
        result = re.search('(\d+\.\d\d)% pfem', processes)

        # check if we matched anything
        if result is not None:
            # print our match
            logging.info(result.group(1))
            # dump whole match line
            logging.debug(result.group(0))

            if result.group(1) is not None:
                return result.group(1)
            else:
                # didn't match anything?
                return 0
        else:
            print(result)
            # fail :(
            return 0


def poll_device(stop_event, ip, username, password, sleep_time, db):

    # Connect to device
    try:
        logging.warning("Connecting to {} with username {} and password {}".format(ip,username,password))
        device = Device(host=ip, port=22, user=username, passwd=password)
        device.open()
        switch_name = device.facts[ 'fqdn' ]
        logging.warning('Connected to {}, {} running {}'.format(switch_name,
                                                             device.facts['model'],
                                                            device.facts[ 'version' ]))
    except:
        logging.warning("Can't connect to {}".format(ip))
        sys.exit(1)

    # watch for kill flag while we poll device
    while not stop_event.wait(1):

        pfem_process = device.get_pfem()

        # builds the datapoint and inserts into DB
        build_influx_datapoint(device, db, pfem_process)

        # wait $sleep_time before collecting again
        logging.info("Sleeping for {} seconds".format(sleep_time))
        sleep(sleep_time)

    print("Flag Set. Exiting...")


def get_current_time():
    localtime = time.localtime(time.time())
    logging.debug("Local current time :", localtime)
    return localtime

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

def build_influx_datapoint(device, db, data_point):
    # requires measurement, tag, time,
    #current_time = '{:%Y-%m-%d %H:%M}'.format(datetime.now())

    point = [
        {
            'measurement': 'network_device',
            'tags': {
                'device': device.facts[ 'fqdn' ],
                'test-name': 'pfem_cpu_percent'
            },
            #'time': get_current_time(),
            'fields': {
                'value': float(data_point)
            }
        }
    ]

    #
    logging.warning("{} : {}".format(device.facts['fqdn'], data_point))

    # insert into DB
    result = db.write_points(point, database='network')
    logging.info("Insert into InfluxDB : {}".format(result))
    logging.debug(type(data_point))

def parse_args():
    parser = argparse.ArgumentParser(
    description='Arguments for RPM Polling')
    parser.add_argument('--target', type=str, required=False, default='192.168.56.107',
                        help='default IP to log into Juniper SRX')
    parser.add_argument('--username', type=str, required=False, default='root',
                        help='default username to log into Juniper SRX')
    parser.add_argument('--password', type=str, required=False, default='Juniper',
                        help='default password to log into Juniper SRX')
    return parser.parse_args()


def thread_gen(pill2kill, target_list, username, password, sleep_time, db):
    for ip in target_list:
        t = threading.Thread(target=poll_device, args=(pill2kill, ip, username, password, sleep_time, db))
        yield t

##############
# MAIN BLOCK #
##############
def main(target=['192.168.56.107'], username='root', password='Juniper'):

    # parse args
    if not args.target:
        logging.info("Using default target of {}".format(target))
    if not args.username:
        logging.info("Using default username of {}".format(username))
    if not args.password:
        logging.info("Using default password of {}".format(password))

    # build array of targets (in the event of comma separated hosts)
    target_list = args.target.split(',')

    # Connect to DB
    db = InfluxDBClient('localhost', 8086, 'root', 'root', 'network')
    logging.info('Connected to InfluxDB')

    db.create_database('network', if_not_exists=False)

    # Start of metrics collection
    logging.info('Beginning metrics collection...')

    # flag to kill threads
    pill2kill = threading.Event()

    threads = list(thread_gen(pill2kill, target_list, username, password, sleep_time, db))

    map(threading.Thread.start, threads)
    time.sleep(60)
    pill2kill.set()
    map(threading.Thread.join, threads)


    # for device in device_list:
    #
    #     current = poll_device(device, db, sleep_time)
    #     check_results.append(current)
    #     current.start()

    # for result in check_results:
    #     result.join()
    #     print("Status from {} is {}".format(result.run, result.status))
        # while True:
        #
        #     # returns percentage of CPU from pfem process
        #     pfem_process = get_system_processes(device, 'pfem')
        #     # builds the datapoint and inserts into DB
        #     build_influx_datapoint(device, db, pfem_process)
        #
        #     # wait $sleep_time before collecting again
        #     sleep(sleep_time)
        #

# executes only if not called as a module
if __name__ == "__main__":

    args = parse_args()

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

    main(target=args.target, username=args.username, password=args.password)
