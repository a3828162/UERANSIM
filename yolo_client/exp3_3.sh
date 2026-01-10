#!/bin/bash

max_ue=(1 2 3 4 5 6 7 8)

for ue in "${max_ue[@]}"; do
    for ((ue_id=1; ue_id<=ue; ue_id++)); do
        # echo "max_ue=$ue, ue_id=$ue_id"

        ./nr-binder 10.60.0.$ue_id /home/ubuntu/UERANSIM/yolo_client/yolo_client.py --continuous --folder ./train2017 --interval 1 --max-requests 60 --host 192.168.113.50 --port 8443 --ueid $ue_id --insecure &

    done

    sleep 90
    python3 calculate_ue_statistics.py dataset

    mv dataset ue_${ue}_exp3_3

done
