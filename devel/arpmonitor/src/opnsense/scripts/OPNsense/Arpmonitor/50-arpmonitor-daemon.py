#!/usr/local/bin/python3
from io import TextIOWrapper
import os
import json
import socket
from configparser import ConfigParser
import time
import re
import daemonize
import signal
from operator import attrgetter
# import psutil

# TODO: move list[msg] to full json string and see how well it sends through ports
#       see if json.dumps() is effectively the same but if it isnt then it should go
#       fuck itself


arpwatch_config = "/usr/local/etc/arpwatch/arpwatch.conf"
arpwatch_log = "/var/log/arpwatch.log"
arp_dat = "/usr/local/arpwatch/arp.dat"
result = {}

pid_loc = "/tmp/arpwatch-plugin.pid"

import os


'''
Need to handle most of the hard work inside this class. This is due
to the entirety of the conf file reloading each time this script is called.
If I want to enable multithreading, I would have to have a thread running a 
server, probably UDP, on a socket in order to truly allow the script thread
to communicate with the daemonized process.
'''

class ConfFile:
    def __init__(self) -> None:
        self.cnf = ConfigParser()
        self.cnf_str = self.cnf.read(arpwatch_config)
        
        
    def __eq__(self, other) -> bool:
        return self.cnf_str == other.cnf_str

def is_daemon() -> bool:
    return os.path.exists(pid_loc)   

class Cmd:
    RELOAD_CONF = "RELOAD_CONF"
    GET_ARPWATCH_LOG = "GET_ARPWATCH_LOG"
    GET_ARPWATCH_DAT = "GET_ARPWATCH_DAT"
    GET_ARPWATCH_STATUS = "GET_ARPWATCH_STATUS" #basically obtaining arpwatches config
    KILL_ARPWATCH = "KILL_ARPWATCH"
    GET_STATISTICS = "GET_STATISTICS"
    SAVE_ADDRS = "SAVE_ADDRS"

class ReloadConf():
    def run(self) -> ConfFile:
        return ConfFile()


class GetArpwatchLog(Cmd):
    def run(self) -> list[str]:
        f = open(arpwatch_log)
        ls = []
        for line in f:
            ls.append(line)

        return ls
        
class ErrMsg:
    def __init__(self, code: int, timestamp: str, err: str, msg: str) -> None:
        self.code = code
        self.ts = timestamp
        self.err = err
        self.msg = msg


current_conf = ConfFile()

# TODO: Implement this. It is currently not implemented so there should be 0 calls involving this in main()
class SmtpController:
    def __init__(self) -> None:
        pass



class ArpwatchController:
    def __init__(self) -> None:
        pass

    def kill(self) -> bool:
        if os.system("killall arpwatch") == 0:
            return True
        else:
            return False
    def restart(self) -> bool:
        if self.kill():
            if current_conf.cnf.has_section('general'):
                # GENERAL NICS

                nics = current_conf.cnf.get('general', 'Nics')
                nics = nics.split(' ')

                # GENERAL EMAILS
                email_addr = current_conf.cnf.get('general', 'Email')
                if email_addr == "":
                    email_addr = "root"

                # TODO: Maybe add network options?? This would help with not getting about a million
                #       bogon alerts. God there is so many, it hurts to look at the log.
                if nics != "":
                    for nic in nics:
                        os.system(f"arpwatch -i {nic} -e {email_addr}")
                else:
                    os.system(f"arpwatch -e {email_addr}")


            os.system(f"arpwatch")
            return True
        return False

    def get_log(self) -> list[str]:
        sl: list[str] = []
        with open(arpwatch_log) as file:
            for line in file:
                if "arpwatch" in line:
                    sl.append(line)

        return sl


    def get_arp_dat(self) -> list[str]:
        sl: list[str] = []
        with open(arp_dat) as file:
            for line in file:
                sl.append(line)

        return sl








def main():
    IP = "127.0.0.1"
    current_conf = ConfFile()
    PORT = 3529
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    sock.listen(2)
    MAX_SIZE = 500



    dne_line = "This line doesn't exist"

    last_lines: list[bytes] = []

    while True:
        s, addr = sock.accept() # 1024 buf size, will see how well this works and if there is data loss.
                                         # may have to figure out how to compress new parts of msg, but fine for now
        data = s.recv(1024)
        
        match data:
            case Cmd.RELOAD_CONF:
                current_conf = ReloadConf().run()

                current_conf.cnf.read(arpwatch_config)

                ArpwatchController().restart()

                res = {}
                res['status'] = 'success'
                s.send(json.dumps(res).encode())

            # I think client side should handle the splitting of log
            case Cmd.GET_ARPWATCH_LOG:
                res = {}
                log = ArpwatchController().get_log()
                st: str = ""
                for i in log:
                    st += i

                res['message'] = s

            
            # Ignoring this for now, need to figure out where arp.dat is
            case Cmd.GET_ARPWATCH_DAT:
                res = {}

                res['message'] = 'Not available currently'
                s.send(json.dumps(res).encode())

            case Cmd.GET_ARPWATCH_STATUS:
                s.send(json.dumps(current_conf.cnf.items(section='general')).encode())


            case Cmd.KILL_ARPWATCH:
                res = {}
                if ArpwatchController().kill():
                    res['status'] = 'success'
                    s.send(json.dumps(res).encode())
                else:
                    res['status'] = 'failure'
                    s.send(json.dumps(res).encode())


            case 

        

        s.close()

        time.sleep(0.1)

if not is_daemon():
    daemon = daemonize.Daemonize(app="arpmonitor-daemon", pid=pid_loc, action=main)
    daemon.start()
else:
    pass   



