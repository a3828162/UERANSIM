#!/usr/bin/env python3
import csv, math, random, sys
from pathlib import Path

def generate_single_trace(seed, lam, watch_s_mean=240, duration_s=15*60, out_dir='traces', filename=None):
    """
    生成符合 M/M/1 的軌跡檔案
    - 到達時間: Poisson process (指數分布間隔時間，參數 lam)
    - 服務時間 (watch_s): 指數分布 (參數 mu = 1/watch_s_mean)
    """
    rng = random.Random(seed)
    t = 0.0
    events = []
    ue_cnt = 0
    mu = 1.0 / watch_s_mean  # 服務率
    
    while True:
        if lam <= 0:
            break
        # 生成到達時間間隔 (指數分布)
        u = rng.random()
        dt = -math.log(1.0 - u) / lam
        t += dt
        if t > duration_s:
            break
        
        # 生成服務時間 (指數分布)
        u_service = rng.random()
        watch_s = -math.log(1.0 - u_service) / mu
        
        ue_cnt += 1
        events.append({
            "t_arrive": round(t, 3),
            "watch_s": int(watch_s),  # 轉成整數秒
            "ue_id": f"ue{ue_cnt}"
        })
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if filename is None:
        filename = f"trace_seed{seed}.csv"
    path = Path(out_dir) / filename
    with open(path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['t_arrive', 'watch_s', 'ue_id'])
        writer.writeheader()
        for ev in events:
            writer.writerow(ev)
    return str(path), events


if __name__ == "__main__":
    # 讀取命令列參數
    if len(sys.argv) < 2:
        print("Usage: python3 createPoisson.py <seed>")
        sys.exit(1)

    seed = int(sys.argv[1])

    out_path, events = generate_single_trace(
        seed=seed,
        lam=0.045,          # 到達率 (arrivals per second)
        watch_s_mean=240,   # 平均服務時間 (seconds)
        duration_s=600,
        filename=f"trace_seed{seed}.csv"
    )

    print(f"Wrote {len(events)} events to {out_path}\n")
    print("Sample lines:")
    with open(out_path, 'r') as f:
        for _ in range(10):
            line = f.readline().strip()
            if not line:
                break
            print(line)