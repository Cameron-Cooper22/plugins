#!/usr/bin/python3 
from os import mkdir, chdir
import sqlite3
from typing import Required
import ifaddr
import mongoengine
from mongoengine.fields import ReferenceField


mongoengine.connect(host="mongodb://127.0.0.1:27017/arpmonitor")

ARPWATCH_DATABASE="/var/lib/arpwatch"

def int2ip(ip: int) -> str:
    d1 = ip >> 24 # true
    d2 = (ip >> 16) | (0xff << 8) ^ (0xff << 8)
    d3 = (ip >> 8) | (0xffff << 16) ^ (0xffff << 16)
    d4 = ip | (0xffffff << 24) ^ (0xffffff << 24)
    return f"{d1}.{d2}.{d3}.{d4}"

def ip2int(ip: str) -> int:
    s = ip.split('.')
    return int(s[0]) * 256 ** 3 + int(s[1]) * 256 ** 2 + int(s[2]) * 256 + int(s[3])

MAX_IPV4 = ip2int('255.255.255.255')

class OpenPort(mongoengine.EmbeddedDocument):
    port = mongoengine.IntField(max_value=0xffff)
    service = mongoengine.StringField()

class NetworkDevice(mongoengine.Document):
    interface = mongoengine.StringField(Required=True)
    ip_addr = mongoengine.IntField(Required=True, max_value=MAX_IPV4)
    mac_addr = mongoengine.StringField(Required=True)
    old_mac_addr = mongoengine.StringField()
    hostname = mongoengine.StringField()
    vendor = mongoengine.StringField()
    timestamp = mongoengine.DateTimeField(Required=True)
    os = mongoengine.StringField()
    open_ports = mongoengine.EmbeddedDocumentListField(OpenPort)

    meta = {'collection': 'network_data'}


mongoengine.disconnect()

