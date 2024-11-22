from io import TextIOWrapper
import os
import json
import socket
from configparser import ConfigParser
import time
import daemonize
import signal
from operator import attrgetter
import psutil

# TODO: move list[msg] to full json string and see how well it sends through ports
#       see if json.dumps() is effectively the same but if it isnt then it should go
#       fuck itself


arpwatch_config = "/usr/local/etc/arpwatch/arpwatch.conf"
arpwatch_log = "/var/log/arpwatch.log"

result = {}

pid_loc = "/tmp/arpwatch-plugin.pid"

# parser = argparse.ArgumentParser()
# parser.add_argument('reload_conf')
#
# args = parser.parse_args()
#


import os

def read_last_n_lines(file_name, n):
    with open(file_name, "rb") as f:
        try:
            f.seek(-2, os.SEEK_END) 
            while n > 0:
                f.seek(-2, os.SEEK_CUR) 
                if f.read(1) == b"\n":
                    n -= 1
        except OSError:
            f.seek(0) 
        return f.readlines()[-n:]



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
                if nics != "":
                    for nic in nics:
                        os.system(f"arpwatch -i {nic} -e {email_addr}")
                else:
                    os.system(f"arpwatch -e {email_addr}")


            os.system(f"arpwatch")
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

    last_lines: list[bytes] = []

    while True:
        s, addr = sock.accept() # 1024 buf size, will see how well this works and if there is data loss.
                                         # may have to figure out how to compress new parts of msg, but fine for now
        data = s.recv(512)

        
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
            #[
            #   {
            #       // NewStationMsg
            #   },
            #   {
            #       //Changed StationMsg
            #   },
            #    etc you get it
            #
            #]
                pl = parse_arpwatch_log(sl)
                pl.sort(key=attrgetter('type'))
                s.send(json.dumps(pl, default=LogMsgDict).encode())
            
            # Ignoring this for now, need to figure out where arp.dat is
            case Cmd.GET_ARPWATCH_DAT:
                pass

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

        s.close()
        i = 1
        while True:
            temp = read_last_n_lines(arpwatch_log, 5 + i * 2)
            diff = [item for item in temp if item  not in last_lines]
            if len(diff) != 5 + i * 2:
                last_lines = temp
                temp_sl = [byte.decode() for byte in diff]
                for x in temp_sl:
                    sl.append(x)
                break

            i += 1

if not is_daemon():
    daemon = daemonize.Daemonize(app="arpwatch-plugin", pid=pid_loc, action=main)
    daemon.start()
else:
    pass   

result = {}
result['message'] = "Daemon started"


