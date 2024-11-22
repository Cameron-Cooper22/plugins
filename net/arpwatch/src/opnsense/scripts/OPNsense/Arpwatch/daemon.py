from io import TextIOWrapper
import os
import json
import socket
from configparser import ConfigParser
import argparse
import time
import daemonize
import signal
from operator import attrgetter
import psutil

# TODO: move list[msg] to full json string and see how well it sends through ports
#       see if json.dumps() is effectively the same but if it isnt then it should go
#       fuck itself


arpwatch_config = "/usr/local/etc/arpwatch/arpwatch.conf"
arpwatch_log = "/var/log/arpwatch/arpwatch.log"

result = {}

pid_loc = "/tmp/arpwatch-plugin.pid"

# parser = argparse.ArgumentParser()
# parser.add_argument('reload_conf')
#
# args = parser.parse_args()
#
def tail(f: TextIOWrapper, sleep=1.0):
    f.seek(0, 2) # 2 sets pointer to end of file

    while True:
        line = f.readline()

        if not line:
            time.sleep(sleep)
            continue

        yield line



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
    RELOAD_CONF = 0x01
    GET_ARPWATCH_LOG = 0x02
    GET_ARPWATCH_DAT = 0x03
    GET_ARPWATCH_STATUS = 0x04
    KILL_ARPWATCH = 0x05


class ReloadConf():
    def run(self) -> ConfFile:
        return ConfFile()

class LogMsg:
    def __init__(self) -> None:
        self.type = ""
        
def LogMsgDict(obj: LogMsg):
    return obj.__dict__

# Probably most common message
class NewStationMsg(LogMsg):
    def __init__(self, ipAddr: str, macAddr:str, timestamp: str) -> None:
        super().__init__()
        self.ipAddr = ipAddr
        self.macAddr = macAddr
        self.timestamp = timestamp
        self.type = "NewStationMsg"

    # def to_json(self) -> str:
    #     return f"""
    #     {{
    #         "timeStamp": "{self.ts}",
    #         "ipAddr": "{self.ip_addr}",
    #         "macAddr": "{self.mac_addr}"
    #     }}
    #     """

class ChangedEthernetMsg(LogMsg):
    def __init__(self, ipAddr: str, macAddr: str, oldMacAddr: str, timestamp: str) -> None:
        super().__init__()
        self.ip_addr = ipAddr
        self.mac_addr = macAddr
        self.old_mac_addr = oldMacAddr
        self.ts = timestamp
        self.type = "ChangedStationMsg"

    def to_json(self) -> str:
            return f"""
        {{
            "timestamp": "{self.ts}",
            "ipAddr": "{self.ip_addr}",
            "macAddr": "{self.mac_addr}",
            "oldMacAddr": "{self.old_mac_addr}"
        }}
        """

class NewActivityMsg(LogMsg):
    def __init__(self, ipAddr: str, macAddr:str, timestamp: str) -> None:
        super().__init__()
        self.ip_addr = ipAddr
        self.mac_addr = macAddr
        self.ts = timestamp
        self.type = "NewStationMsg"

    def to_json(self) -> str:
        return f"""
        {{
            "timeStamp": "{self.ts}",
            "ipAddr": "{self.ip_addr}",
            "macAddr": "{self.mac_addr}"
        }}
        """

# main in the middle attack possibility
class FlipFlopMsg(LogMsg):
    def __init__(self, ipAddr: str, macAddr: str, oldMacAddr: str, timestamp: str) -> None:
        super().__init__()
        self.ip_addr = ipAddr
        self.mac_addr = macAddr
        self.old_mac_addr = oldMacAddr
        self.ts = timestamp
        self.type = "FlipFlop"

    def to_json(self) -> str:
        return f"""
        {{
            "timeStamp": "{self.ts}",
            "ipAddr": "{self.ip_addr}",
            "macAddr": "{self.mac_addr}"
        }}
        """

# TODO: Add  support for eth broadcast, ip broadcast, bogon (maybe remove), diff ethernet broadcast
# eth mismatch, reused old ethernet address, suppressed DECnet flip flop
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
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == "arpwatch":
                    os.kill(proc.pid, signal.SIGTERM)
                    return True

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        return False

    def restart(self) -> bool:
        if self.kill():
            if current_conf.cnf.has_section('general'):
                # GENERAL NICS
                nics = current_conf.cnf.get('general', 'nics')
                nics = nics.split(' ')

                # GENERAL EMAILS
                email_addr = current_conf.cnf.get('general', 'email')
                if email_addr == "":
                    email_addr = "root"

                # TODO: Maybe add network options?? This would help with not getting about a million
                #       bogon alerts. God there is so many, it hurts to look at the log.
                for nic in nics:
                    os.system(f"arpwatch -i {nic} -e {email_addr}")


            os.system(f"arpwatch ")
            return True
        
        return False



def parse_arpwatch_log(ls: list[str]) -> list[LogMsg]:
    msg_list = []
    for x in ls:
        sl = x.split(' ')
        ts = sl[1]
        if sl[3] != "arpwatch":
            continue

        pid = sl[4]
        match (sl[8]):
            case "changed":
                if (sl[9], sl[10]) != ("ethernet", "address"):
                    continue
                msg_list.append(ChangedEthernetMsg(sl[11], sl[12], sl[13].strip("()"), ts))
            case "new":
                match sl[9]:
                    case "station":
                        msg_list.append(NewStationMsg(sl[10], sl[11], ts))
                    case "activity":
                        msg_list.append(NewActivityMsg(sl[10], sl[11], ts))
                    case _:
                        continue
            case "flip":
                if sl[9] == "flop":
                    msg_list.append(FlipFlopMsg(sl[10], sl[11], sl[12].strip("()"), ts))
                else:
                    continue


    return msg_list


def main():
    IP = "127.0.0.1"
    current_conf = ConfFile()
    PORT = 3529
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    sock.listen(2)
    sl: list[str] = []
    ll: list[LogMsg] = []
    MAX_SIZE = 500

    dne_line = "This line doesn't exist"

    while True:
        s, addr = sock.accept() # 1024 buf size, will see how well this works and if there is data loss.
                                         # may have to figure out how to compress new parts of msg, but fine for now
        s.recv(1024)

        
        match int(data):
            case Cmd.RELOAD_CONF:
                current_conf = ReloadConf().run()

                current_conf.cnf.read(arpwatch_config)
                if current_conf.cnf.has_section('general'):
                    # TODO: Further implementation
                    pass

            case Cmd.GET_ARPWATCH_LOG:

#[
#   {
#       // NewStationMsg
#   },
#   {
#       //Changed StationMsg
#   },
#
#
#
#
#
#
#
#
#
#]
                pl = parse_arpwatch_log(sl)
                pl.sort(key=attrgetter('type'))
                s.send(json.dumps(pl, default=LogMsgDict).encode())



            case Cmd.GET_ARPWATCH_DAT:
                pass

        for line in tail(open(arpwatch_log), sleep=0.5):
            if line == dne_line:
                break
            else:
                sl.append(line)
                while len(sl) > MAX_SIZE:
                    sl.pop(0)
                

if not is_daemon():
    daemon = daemonize.Daemonize(app="arpwatch-plugin", pid=pid_loc, action=main)
    daemon.start()
else:
    pass   



