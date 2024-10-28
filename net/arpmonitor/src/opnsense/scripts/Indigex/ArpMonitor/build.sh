#!/bin/sh
sudo sysrc mongod_enable="YES"
sudo service mongod start

sudo mkdir -p /var/lib/arpmonitor
sudo mkdir -p /var/log/mongodb
sudo chown -R mongodb:mongodb /var/lib/arpmonitor
sudo service mongod restart

mongod --fork --logpath /var/log/mongodb/mongod.log
