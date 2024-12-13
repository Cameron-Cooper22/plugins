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

s = socket.socket()
PORT = 3529

s.connect(('127.0.0.1', PORT))

match args.cmd:
    case "reload_conf":
        s.send(Cmd.RELOAD_CONF.encode())
        print(json.dumps(s.recv(512).decode()))

    case "get_log":
        with open("/var/log/arpwatch/arpwatch.log") as file:
            st: str = ""
            for line in file:
                st = st + line

            print(s)

    case "get_dat":
        with open("/usr/local/arpwatch/arp.dat") as file:
            st: str = ""
            for line in file:
                st = st + line
            
            print(st)

    case "get_arpwatch_status":
        s.send(Cmd.GET_ARPWATCH_STATUS.encode())
        print(json.dumps(s.recv(1024).decode()))

    case "kill_arpwatch":
        s.send(Cmd.KILL_ARPWATCH.encode())
        print(json.dumps(s.recv(512).decode()))


    case "test":
        result = {}
        result['message'] = "This is a test of the functionality of some bs"
        print(json.dumps(result))



print("fuck off")
