#!/bin/bash

for i in {1..60}; do
  dnsperf -s 192.168.56.110 -p 53 -Q 1 -d queries.txt -l 1 >> single_buffer2_latency5.txt
done