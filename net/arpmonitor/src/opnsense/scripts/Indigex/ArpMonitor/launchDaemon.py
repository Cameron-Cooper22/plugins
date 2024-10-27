#!/usr/bin/python3

import os
import sys
import time
import atexit
import signal
from socket import inet_aton
import configparser
import sqlite3

pid_file = '/tmp/mydaemon.pid'

CONFIGFILE = "/usr/local/etc/arpmonitor/arpmonitor.conf"

sql_statements = [
        """CREATE TABLE IF NOT EXISTS devices (
                mac_addr character(17) NOT NULL,
                state varying character(8) NOT NULL,
                "timestamp" timestamp without time zone NOT NULL,
                oldmac character(17) DEFAULT NULL::bpchar,
                arpwatchid bigserial NOT NULL,
                ip_addr bigint NOT NULL,
                CONSTRAINT arpwatch_pkey PRIMARY KEY (arpwatchid)

        )"""
        ]

def normalize_mac(mac: str) -> str:
    s = mac.split(':')
    digits = [ int(x, 16) for x in s]
    s = "%02x:%02x:%02x:%02x:%02x:%02x" % tuple(digits)
    return s

def ip2int(ip) -> int:
    nums = ip.split('.')
    '''
    Similar holding 2 u8 values in a u16, this is effectively holding 4 u8 integers.
    summation(num * num_possiblities ^ (num_u8 - 1) - n)
    Very similar to when ordering binary
    '''
    return int(nums[0])*256**3 + int(nums[1])*256**2 + int(nums[2])*256 + int(nums[3])

def daemonize():
    if os.fork():
        sys.exit()

    os.chdir('/')
    os.setsid()
    if os.fork():
        sys.exit
    
    sys.stdout.flush()
    sys.stderr.flush()
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())
    atexit.register(lambda: os.remove(pid_file))
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid))

def sig_handler(signum, frame):
    print("Exiting...")
    sys.exit()

def main():
    # Database is implicitly created
    daemonize()
    config = configparser.RawConfigParser()
    config.read(CONFIGFILE)

    LOGFILE = config.get("database", "LOGFILE")
    STATEFILE = config.get("database", "STATEFILE")

    lastline = 0
    try:
        # read state file
        statefile = open(STATEFILE, 'r')
        lastline = int(statefile.readline())
        statefile.close()
    except IOError as e:
        if e.errno != 2:
            raise
    try:
        logfile = open(LOGFILE, 'r')
    except IOError as e:
        if e.errno != 2:
            raise
        print(f'Logfile {LOGFILE} not found. Exiting...')
        sys.exit(1)


    logfile.seek(0, 2)
    size = logfile.tell()

    if size < lastline:
        lastline = 0

    db = sqlite3.connect("/var/lib/arpmonitor/arpmonitor.db")
    cur = db.cursor()
    cur.execute("CREATE TABLE(mac_addr, )")
    while True:
        pass
