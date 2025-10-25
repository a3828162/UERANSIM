#!/bin/bash

res=$(./nr-binder $2 dig @192.168.56.110 vrstream.com +short)

echo -e "dns query response:\n$res"
echo "ue:$1"
echo "IP:$2"

DISPLAY=:0 ./nr-binder $2 google-chrome --new-window --user-data-dir="/tmp/chrome_$1" http://$res:18080/?ue=$1

# DISPLAY=:0 google-chrome --new-window http://$res:18080/?ue=$1 > /dev/null 2>&1 &
echo "chrome started"