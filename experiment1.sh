#!/bin/bash

# QPS_List="10 50 100 500 1000 2000 3000 4000"
# QPS_List="25 75 250 750 1500 2500 3500 "
# QPS_List="75 250 750 1500 2500 3500 "
#QPS_List="100 1000 2000 3000 4000 5000 6000 7000 8000 9000 10000 11000 12000 13000 14000 15000 16000 17000 18000 19000 20000 "
QPS_List="10000 11000 12000 "


for QPS in ${QPS_List}; do
    echo "QPS: ${QPS}"

    # 用 bc 做浮點運算並取整數（四捨五入）
    Q=$(printf "%.0f" "$(echo "${QPS} * 1.3" | bc)")

    for i in {1..3}; do
        echo "Run: ${i} (Q=${Q})"
        dnsperf -s 140.113.208.76 -p 53 -Q ${Q} -c ${QPS} -T 4 -d queries.txt -l 30 > ./data/withEASDF/${QPS}_${i}.txt
        # dnsperf -s 192.168.56.50 -p 53 -Q ${Q} -c ${QPS} -T 4 -d queries.txt -l 30 > ./data/withEASDF/${QPS}_${i}.txt
        sleep 10
    done
done
