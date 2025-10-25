#!/bin/bash

res=$(dig @192.168.56.110 vrstream.com +short)

echo "dns query response:$res"
echo "ue:$1"

DISPLAY=:0 google-chrome --new-window http://$res:18080/?ue=$1 > /dev/null 2>&1 &
echo "chrome started"