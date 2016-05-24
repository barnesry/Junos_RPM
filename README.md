# Junos_RPM
Proof of Concept Demonstration for Juniper RPM Collection with InfluxDB and Graphana launched in an Ubuntu instance.

# Get Influxdb and Graphana launched
./vagrant up

This will launch an Ubuntu instance, install InfluxDB and Graphana and configure your local machine to mirror the following services

```
==> default: Forwarding ports...
    default: 3000 (guest) => 3000 (host) (adapter 1)
    default: 8080 (guest) => 8080 (host) (adapter 1)
    default: 8083 (guest) => 8083 (host) (adapter 1)
    default: 8086 (guest) => 8086 (host) (adapter 1)
    default: 22 (guest) => 2222 (host) (adapter 1)
```
## InfluxDB
    http://localhost:8083
    
1. Create a new database called 'network'

## Graphana
The default login here is admin/admin

    http://localhost:3000

Create a new dashboard with a single metric panel using two queries.
    
    SELECT value/1000 FROM "rpm_history" WHERE owner='http-rpm'
    SELECT value/1000 FROM "rpm_history" WHERE owner='dns-rpm'

## vSRX
Relevant RPM configuration configlet. In this instance, each test is 5 minutes long using a probe count of 5 with 60sec in between each probe.
We'll keep a history of 10 only, and we'll poll the device every 10 minutes with the idea of having the oldest data roll out of the buffer
before we gather new data to insert into our history table. There are more elegant ways to do this, but this seemed the easiest for this purpose.

Any successive loss of 2 probes, or a total loss of 3 across all 5 probes (5min) will mean the test failed. And we'll trap on that.
We get both the individual test results AND the test results. For TRAPS, I'm likely only interested in gathering the overall TEST result,
rather than each individual probe, but we'll collect and graph the probe(s).

```
May 19 14:34:43  vSRX-NAT-GW rmopd[1199]: PING_PROBE_FAILED: pingCtlOwnerIndex = http-rpm, pingCtlTestName = http
May 19 14:34:43  vSRX-NAT-GW rmopd[1199]: PING_TEST_FAILED: pingCtlOwnerIndex = http-rpm, pingCtlTestName = http
```

```
barnesry@vSRX-NAT-GW> show services rpm history-results
    Owner, Test                 Probe received              Round trip time
    dns-rpm, ping            Tue May 24 08:34:30 2016            38740 usec
    dns-rpm, ping            Tue May 24 08:35:30 2016            41454 usec
    dns-rpm, ping            Tue May 24 08:36:30 2016            38459 usec
    dns-rpm, ping            Tue May 24 08:37:30 2016            39457 usec
    dns-rpm, ping            Tue May 24 08:38:30 2016            36225 usec
    dns-rpm, ping            Tue May 24 08:39:30 2016            36762 usec
    dns-rpm, ping            Tue May 24 08:40:30 2016            65886 usec
    dns-rpm, ping            Tue May 24 08:41:30 2016            37545 usec
    dns-rpm, ping            Tue May 24 08:42:30 2016            34747 usec
    dns-rpm, ping            Tue May 24 08:43:30 2016            38124 usec
    http-rpm, http         Tue May 24 08:33:21 2016           150059 usec
    http-rpm, http         Tue May 24 08:34:21 2016           165556 usec
    http-rpm, http         Tue May 24 08:35:21 2016           162237 usec
    http-rpm, http         Tue May 24 08:36:21 2016           159409 usec
    http-rpm, http         Tue May 24 08:38:21 2016           159382 usec
    http-rpm, http         Tue May 24 08:39:21 2016           230250 usec
    http-rpm, http         Tue May 24 08:40:21 2016           152138 usec
    http-rpm, http         Tue May 24 08:41:21 2016           165070 usec
    http-rpm, http         Tue May 24 08:42:21 2016           154056 usec
    http-rpm, http         Tue May 24 08:44:21 2016           176014 usec
```


We'll use the following RPC call to gather the historical data using our Python script.
```
barnesry@vSRX-NAT-GW> show services rpm history-results | display xml rpc
<rpc-reply xmlns:junos="http://xml.juniper.net/junos/12.1X47/junos">
    <rpc>
        <get-history-results>
        </get-history-results>
    </rpc>
    <cli>
        <banner></banner>
    </cli>
</rpc-reply>
```

```
barnesry@vSRX-NAT-GW> show configuration services rpm
probe http-rpm {
    test http {
        probe-type http-get;
        target url http://www.google.com;
        probe-count 5;
        probe-interval 60;
        test-interval 60;
        history-size 10;
        thresholds {
            successive-loss 2;
            total-loss 3;
        }
        traps test-failure;
    }
}
probe dns-rpm {
    test ping {
        probe-type icmp-ping;
        target address 8.8.8.8;
        probe-count 5;
        probe-interval 60;
        test-interval 60;
        history-size 10;
        thresholds {
            successive-loss 2;
            total-loss 3;
        }
        traps test-failure;
    }
}
```

# Gather RPM datapoints
Now we need to gather some data to graph. So we'll do this by configuring a few RPM probes on a locally launched vSRX instance. 

./netconf-poll.py

In this instance I configured a vSRX in Virtualbox (not currently configured in Vagrant - next?) The script is hard configured
to poll a specific IP address on my laptop (sorry... lazy) but collects information about the RPM
history from my local vSRX using vboxnet0 and reports this back into the InfluxDB database. My RPM polling is configured to keep a history of (10) and
I've chosen to poll RPM history every 600sec (10min) in order to minimize duplication in the database without getting fancy trying to de-dup
data upon collection.

# Results
## InfluxDB
```
rpm_history
time	device	owner	test-name	value
2016-05-18T11:45:40Z	"vSRX-NAT-GW.thelab.net"	"http-rpm"	"http"	115578
2016-05-18T11:47:40Z	"vSRX-NAT-GW.thelab.net"	"http-rpm"	"http"	110396
2016-05-18T11:48:40Z	"vSRX-NAT-GW.thelab.net"	"http-rpm"	"http"	139676
2016-05-18T11:49:40Z	"vSRX-NAT-GW.thelab.net"	"http-rpm"	"http"	125401
2016-05-18T11:50:40Z	"vSRX-NAT-GW.thelab.net"	"http-rpm"	"http"	125037
2016-05-18T11:51:40Z	"vSRX-NAT-GW.thelab.net"	"http-rpm"	"http"	110834
```
