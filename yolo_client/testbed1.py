import pandas as pd
import threading
import time
import subprocess
import psutil
import re
import sys

def get_uesimtun_ips():
    """取得所有 uesimtun 介面的 IP，依數字排序"""
    addrs = psutil.net_if_addrs()
    tun_ifaces = []
    for name, iface_addrs in addrs.items():
        if name.startswith("uesimtun"):
            for addr in iface_addrs:
                if addr.family.name == 'AF_INET':
                    tun_ifaces.append((name, addr.address))
    tun_ifaces.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))
    return [ip for _, ip in tun_ifaces]

def readCSV(csv_file):
    """讀取 trace CSV"""
    return pd.read_csv(csv_file)

def task(ue_name, arrival_time, watch_duration, ue_ip):
    print(f"[THREAD START] {ue_name} @ {arrival_time}s with IP {ue_ip}, watch_duration={watch_duration}s")
    time.sleep(arrival_time)

    # 啟動 testbed1.sh，傳入 watch_duration 作為參數
    command = f"./testbed1.sh {ue_name} {ue_ip} {watch_duration}"
    print(f"[EXEC] {command}")
    try:
        # subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # print(f"[{ue_name}] launched successfully.")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"[{ue_name}] Run output: {result.stdout.strip()}")
    except Exception as e:
        print(f"[ERROR] {ue_name} failed to launch: {e}")

    # time.sleep(241)

    print(f"[THREAD END] {ue_name}")

if __name__ == "__main__":
    # 檢查是否有 seed 參數
    if len(sys.argv) < 2:
        print("Usage: python3 testbed1.py <seedNum>")
        sys.exit(1)

    seed = sys.argv[1]
    csv_path = f"./traces/trace_seed{seed}.csv"

    print(f"📄 Using CSV file: {csv_path}")
    df = readCSV(csv_path)
    print(df.head(6))

    # 取得 uesimtun IP
    uesimtun_ips = get_uesimtun_ips()
    print(f"Detected uesimtun IPs: {uesimtun_ips}")

    # 啟動最多 20 個 UE
    threads = []
    for i in range(max(0, len(df))):
        row = df.iloc[i]
        ue_name = row['ue_id']
        arrival_time = row['t_arrive']
        watch_duration = row['watch_s']  # 從 CSV 讀取 watch_s
        ue_ip = uesimtun_ips[i % len(uesimtun_ips)]
        t = threading.Thread(target=task, args=(ue_name, arrival_time, watch_duration, ue_ip))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("✅ All UE threads completed.")
