#!/usr/bin/env python3
"""
實驗 3.3: 多 UE 併發測試
測試不同數量的 UE 併發運行 YOLO 推理請求
"""

import subprocess
import time
import threading
import psutil
import re
import shutil
import os
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

def run_yolo_client(ue_id, ue_ip):
    """運行單個 UE 的 YOLO 客戶端"""
    print(f"[UE {ue_id}] Starting with IP {ue_ip}")
    
    command = f"./nr-binder {ue_ip} /home/ubuntu/UERANSIM/yolo_client/yolo_client.py --continuous --folder ./train2017 --interval 1 --max-requests 60 --host 192.168.113.50 --port 8443 --ueid ue{ue_id} --insecure"
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[UE {ue_id}] ✓ Completed successfully")
        else:
            print(f"[UE {ue_id}] ✗ Failed with error: {result.stderr}")
    except Exception as e:
        print(f"[UE {ue_id}] ✗ Exception: {e}")

def run_experiment_with_ue_count(ue_count, uesimtun_ips):
    """運行指定數量 UE 的實驗"""
    print("\n" + "=" * 80)
    print(f"📊 Running experiment with {ue_count} UE(s)")
    print("=" * 80)
    
    # 啟動所有 UE 的執行緒
    threads = []
    for ue_id in range(1, ue_count + 1):
        ue_ip = uesimtun_ips[(ue_id - 1) % len(uesimtun_ips)]
        t = threading.Thread(target=run_yolo_client, args=(ue_id, ue_ip))
        threads.append(t)
        t.start()
    
    # 等待所有 UE 完成
    for t in threads:
        t.join()
    
    print(f"[MAIN] All {ue_count} UE(s) completed")
    
    # 等待 90 秒
    # print(f"[MAIN] Waiting 90 seconds before statistics calculation...")
    # time.sleep(90)
    
    # 計算統計
    print(f"[MAIN] Calculating UE statistics...")
    try:
        result = subprocess.run("python3 calculate_ue_statistics.py dataset", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[MAIN] ✓ Statistics calculated successfully")
        else:
            print(f"[MAIN] ✗ Statistics calculation failed: {result.stderr}")
    except Exception as e:
        print(f"[MAIN] ✗ Exception during statistics: {e}")
    
    # 移動資料集目錄
    output_dir = f"ue_{ue_count}_exp3_3"
    if os.path.exists("dataset"):
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        shutil.move("dataset", output_dir)
        print(f"[MAIN] ✓ Dataset saved to {output_dir}")
    else:
        print(f"[MAIN] ⚠ Dataset directory not found")

def main():
    print("=" * 80)
    print("🚀 Experiment 3.3: Multi-UE Concurrent YOLO Inference Test")
    print("=" * 80)
    
    # UE 數量配置
    max_ue_list = [3,4]
    
    # 取得 uesimtun IP
    uesimtun_ips = get_uesimtun_ips()
    print(f"\n✓ Detected {len(uesimtun_ips)} uesimtun interface(s):")
    for i, ip in enumerate(uesimtun_ips):
        print(f"  - uesimtun{i}: {ip}")
    
    if not uesimtun_ips:
        print("✗ Error: No uesimtun interfaces found!")
        sys.exit(1)
    
    # 運行各個 UE 數量的實驗
    for ue_count in max_ue_list:
        try:
            run_experiment_with_ue_count(ue_count, uesimtun_ips)
        except Exception as e:
            print(f"\n✗ Error in experiment with {ue_count} UE(s): {e}")
            continue
    
    print("\n" + "=" * 80)
    print("✅ All experiments completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()
