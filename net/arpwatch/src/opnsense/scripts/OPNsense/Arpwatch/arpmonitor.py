import os
import socket
import json
from configparser import ConfigParser

arpwatch_config = "/usr/local/etc/arpwatch/arpwatch.conf"

result = {}

if os.path.exists(arpwatch_config):
    cnf = ConfigParser()
    cnf.read(arpwatch_config)
    if cnf.has_section('general'):
        try:

