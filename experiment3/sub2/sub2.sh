#!/bin/bash

SERVER_IP=192.168.56.110
PORT=53
QUERY_FILE=queries.txt
UE_COUNT=200

for i in $(seq 1 $UE_COUNT); do
  SRC_IP="10.60.0.$i"
  LOG="./${UE_COUNT}ue/ue_${i}_latency.log"
  echo "Starting UE$i from $SRC_IP"
  dnsperf -s $SERVER_IP -a $SRC_IP -p $PORT -Q 1 -d $QUERY_FILE -l 60 -v & #> $LOG &
done

wait
echo "All ${UE_COUNT} UEs finished."
