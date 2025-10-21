#/bin/sh

dnsperf -s 192.168.56.110 -p 53 \
  -Q 5200 \
  -c 4000 \
  -T 4 -d queries.txt \
  -l 60
