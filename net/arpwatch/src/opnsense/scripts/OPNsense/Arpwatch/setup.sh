#!/bin/sh

mkdir -p /var/lib/arpwatch
mkdir -p /var/log/arpwatch

if [ $(ls /var/log/arpwatch | grep arpwatch.log) = "arpwatch.log"]
then 
  touch /var/log/arpwatch/arpwatch.log
fi
