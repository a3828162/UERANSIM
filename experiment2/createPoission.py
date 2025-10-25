#!/usr/bin/env python3
import csv, math, random, sys
from pathlib import Path

def generate_single_trace(seed, lam, watch_s_fixed=240, duration_s=15*60, out_dir='traces', filename=None):
    rng = random.Random(seed)
    t = 0.0
    events = []
    ue_cnt = 0
    while True:
        if lam <= 0:
            break
        u = rng.random()
        dt = -math.log(1.0 - u) / lam
        t += dt
        if t > duration_s:
            break
        ue_cnt += 1
        events.append({
            "t_arrive": round(t, 3),
            "watch_s": int(watch_s_fixed),
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
        lam=0.025,
        watch_s_fixed=240,
        duration_s=15*60,
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