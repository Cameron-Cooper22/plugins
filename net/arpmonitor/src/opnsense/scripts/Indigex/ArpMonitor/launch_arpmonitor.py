#!/usr/bin/python3 
from os import chdir, mkdir
import sqlite3
import ifaddr
import nmap
import netifaces

CREATE_STATEMENT = [
        """
        CREATE TABLE IF NOT EXISTS device(
        ip_addr INTEGER PRIMARY KEY,
        mac_addr TEXT NOT NULL,
        interface TEXT NOT NULL,
        old_mac_addr TEXT,
        os TEXT

        )
        """
        ]


mkdir("/var/lib/arpmonitor")
chdir("/var/lib/arpmonitor")
conn = sqlite3.connect("arpmonitor.db")
cursor = conn.cursor()


adapters = ifaddr.get_adapters()
nm = nmap.PortScannerAsync()

for a in adapters:
    print(a.nice_name)
