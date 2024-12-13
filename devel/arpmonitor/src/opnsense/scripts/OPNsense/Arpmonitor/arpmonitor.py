#!/usr/local/bin/python3

import os
import socket
import json
from configparser import ConfigParser
import sys
import argparse
import socket
from enum import Enum
import re
import signal



#TODO: Need to send the information from the daemon back to the front end in a more reasonable manner
#   Currently it is not the worst, but for the most part it will be displaying the log as a data grid
#   Also need to show success


parser = argparse.ArgumentParser(prog="Arpwatch Plugin", description="Controls access to arpwatch plugins daemon")
parser.add_argument("cmd", help="command to run for the connection to arpwatch plugin daemon.")

args = parser.parse_args()


# sending codes doesnt work. weird
class Cmd:
    RELOAD_CONF = "RELOAD_CONF"
    GET_ARPWATCH_LOG = "GET_ARPWATCH_LOG"
    GET_ARPWATCH_DAT = "GET_ARPWATCH_DAT"
    GET_ARPWATCH_STATUS = "GET_ARPWATCH_STATUS" #basically obtaining arpwatches config
    KILL_ARPWATCH = "KILL_ARPWATCH"
    GET_STATISTICS = "GET_STATISTICS"


conf_loc = "/usr/etc/arpmonitor/arpmonitor.conf"

cnf = ConfigParser()
cnf.read(conf_loc)

match args.cmd:
    case "reload_conf":
        PROCNAME = "arpwatch"
        pid = os.system("pgrep -lS arpwatch | awk '{print $1}'")
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print(f"Process with PID {pid} not found.")
        except PermissionError:
            print(f"Insufficient permissions to kill process with PID {pid}.")

        email = "root@localhost"
        if cnf.has_section('general'):
            if cnf.has_option('general', 'email'):
                email = cnf.get('general', 'email')
            os.system("arpwatch -e {email}")

    case "get_log":
        st: str = ""
        # HACK: this will have to change, log file isn't rotated so in prod this may
        # point to the actual syslog. ALSO WTH apparently it decided to not use it anymore
        with open("/var/log/system/system_20241122.log") as file:
            for line in file:
                if "arpwatch" in line:
                    st = st + line
        print(st)

    case "get_dat":
        st: str = ""
        with open("/usr/local/arpwatch/arp.dat") as file:
            for line in file:
                st = st + line
            
        print(st)

    case "get_arpwatch_status":
        PROCNAME = "arpwatch"
        pid = os.system("pgrep -lS arpwatch | awk '{print $1}'")

    case "kill_arpwatch":
        PROCNAME = "arpwatch"

        pid = os.system("pgrep -lS arpwatch | awk '{print $1}'")
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print(f"Process with PID {pid} not found.")
        except PermissionError:
            print(f"Insufficient permissions.")


    case "test":
        result = {}
        result['message'] = "This is a test of the functionality of some bs"
        print(json.dumps(result))



