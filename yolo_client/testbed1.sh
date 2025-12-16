#!/bin/bash

res=$(./nr-binder $2 dig @192.168.56.110 vrstream.com +short +time=10)
# res=192.168.113.50

echo -e "dns query response:\n$res"。
echo "ue:$1"
echo "IP:$2"

./nr-binder $2 /home/ubuntu/UERANSIM/yolo_client/yolo_client.py --continuous --folder ./train2017 --interval 1 --max-requests $3 --host $res --port 8443 --ueid $1 --insecure