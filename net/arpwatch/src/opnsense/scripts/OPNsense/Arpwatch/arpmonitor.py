import os
import socket
import json
from configparser import ConfigParser
import sys
import daemonize
import argparse
import socket
from enum import Enum

arpwatch_config = "/usr/local/etc/arpwatch/arpwatch.conf"
arpwatch_log = "/var/log/arpwatch/arpwatch.log"

result = {}

pid_loc = "/tmp/arpwatch-plugin.pid"

parser = argparse.ArgumentParser()
parser.add_argument('reload_conf')

args = parser.parse_args()

class Cmd(Enum):
    RELOAD_CONF = 0x01
    GET_ARPWATCH_LOG = 0x02
    GET_ARPWATCH_DAT = 0x03
    KILL_ARPWATCH = 0x04

"""
Need to handle most of the hard work inside this class. This is due
to the entirety of the conf file reloading each time this script is called.
If I want to enable multithreading, I would have to have a thread running a 
server, probably UDP, on a socket in order to truly allow the script thread
to communicate with the daemonized process.
"""
class ConfFile:
    def __init__(self) -> None:
        self.cnf = ConfigParser()
        if os.path.exists(arpwatch_config):
            self.cnf_str = self.cnf.read(arpwatch_config)
        
        else:
            self.cnf_str = ""
            sys.exit(1)        
        
    def __eq__(self, other) -> bool:
        return self.cnf_str == other.cnf_str

def is_daemon() -> bool:
    return os.path.exists(pid_loc)   

def get_arp_log() -> bytes:
    f = open(arpwatch_log, "r")
    string = bytes(f.read().encode())
    f.close()
    return string

'''
Daemon Server
'''
def main():
    IP = "127.0.0.1"
    PORT = 3529
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    cf = ConfFile()
    while True:
        data, addr = sock.recvfrom(1024) # 1024 buf size, will see how well this works and if there is data loss.
                                         # may have to figure out how to compress new parts of msg, but fine for now
        
        """
            json will return:
                {
                    "err": 200,
                    "numBufs": int,
                    "bufs": [
                        ...,
                        ...,
                        ...,
                    ].
                }
            json must return numBufs as it will be easier to parse, handle, and debug.
        """

        match int(data):
            case Cmd.RELOAD_CONF:
                cf = ConfFile()

            case Cmd.GET_ARPWATCH_LOG:
                f = get_arp_log()
                

if not is_daemon():
    daemon = daemonize.Daemonize(app="arpwatch-plugin", pid=pid_loc, action=main)
    daemon.start()
else:
    pass   
