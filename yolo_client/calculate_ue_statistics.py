#!/usr/bin/env python3
"""
統計 random_seed44 目錄下所有 UE 的性能指標。

計算每個 UE 和全部 UE 的平均值：
- Bitrate (kbps)
- RTT (ms)
- Packet Lost

Usage:
    python3 calculate_ue_statistics.py [directory]
    
Example:
    python3 calculate_ue_statistics.py random_seed44
"""

import csv
import sys
from pathlib import Path


def calculate_statistics(csv_file):
    """計算單個 CSV 檔案的統計數據"""
    stats = {
        'bitrate': [],
        'rtt': [],
        'packetlost': [],
        'server': None
    }
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats['bitrate'].append(float(row['bitrate']))
            stats['rtt'].append(float(row['rtt']))
            stats['packetlost'].append(float(row['packetlost']))
            # 記錄 server (edge)，假設所有行的 server 都相同
            if stats['server'] is None and 'server' in row:
                stats['server'] = row['server']
    
    # 計算平均值
    averages = {
        'bitrate': sum(stats['bitrate']) / len(stats['bitrate']) if stats['bitrate'] else 0,
        'rtt': sum(stats['rtt']) / len(stats['rtt']) if stats['rtt'] else 0,
        'packetlost': sum(stats['packetlost']) / len(stats['packetlost']) if stats['packetlost'] else 0,
        'samples': len(stats['bitrate']),
        'server': stats['server'] if stats['server'] else 'N/A'
    }
    
    return averages, stats


def main():
    # 確定目錄
    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        directory = Path('random_seed44_6ue')
    
    if not directory.exists():
        print(f"錯誤: 目錄 {directory} 不存在")
        sys.exit(1)
    
    # 找到所有 performance_ue*.csv 檔案
    csv_files = sorted(directory.glob('performance_ue*.csv'))
    
    if not csv_files:
        print(f"錯誤: 在 {directory} 中找不到 performance_ue*.csv 檔案")
        sys.exit(1)
    
    print("=" * 80)
    print(f"統計目錄: {directory}")
    print(f"找到 {len(csv_files)} 個 UE 檔案")
    print("=" * 80)
    print()
    
    # 儲存每個 UE 的統計數據
    ue_stats = {}
    all_data = {
        'bitrate': [],
        'rtt': [],
        'packetlost': []
    }
    
    # 計算每個 UE 的統計
    print("正在計算各 UE 統計數據...")
    for csv_file in csv_files:
        ue_id = csv_file.stem.replace('performance_ue', '')
        averages, raw_stats = calculate_statistics(csv_file)
        ue_stats[ue_id] = averages
        
        # 累積所有數據
        all_data['bitrate'].extend(raw_stats['bitrate'])
        all_data['rtt'].extend(raw_stats['rtt'])
        all_data['packetlost'].extend(raw_stats['packetlost'])
    
    print()
    
    # 顯示每個 UE 的統計
    print("📊 每個 UE 的平均統計：")
    print("-" * 95)
    print(f"{'UE ID':<8} {'Edge':<12} {'Bitrate (kbps)':>15} {'RTT (ms)':>12} {'Packet Lost':>12} {'Samples':>10}")
    print("-" * 95)
    
    for ue_id in sorted(ue_stats.keys(), key=lambda x: int(x)):
        stats = ue_stats[ue_id]
        print(f"UE {ue_id:<5} {stats['server']:<12} {stats['bitrate']:>15.2f} {stats['rtt']:>12.2f} {stats['packetlost']:>12.2f} {stats['samples']:>10}")
    
    print("-" * 95)
    
    # 計算全部 UE 的平均（簡單平均：每個 UE 等權重）
    overall_avg = {
        'bitrate': sum(stats['bitrate'] for stats in ue_stats.values()) / len(ue_stats) if ue_stats else 0,
        'rtt': sum(stats['rtt'] for stats in ue_stats.values()) / len(ue_stats) if ue_stats else 0,
        'packetlost': sum(stats['packetlost'] for stats in ue_stats.values()) / len(ue_stats) if ue_stats else 0,
        'total_samples': len(all_data['bitrate'])
    }
    
    print()
    print("🎯 全部 UE 的總體平均：")
    print("-" * 80)
    print(f"{'Metric':<20} {'Average':>15} {'Total Samples':>15}")
    print("-" * 80)
    print(f"{'Bitrate (kbps)':<20} {overall_avg['bitrate']:>15.2f} {overall_avg['total_samples']:>15}")
    print(f"{'RTT (ms)':<20} {overall_avg['rtt']:>15.2f} {overall_avg['total_samples']:>15}")
    print(f"{'Packet Lost':<20} {overall_avg['packetlost']:>15.2f} {overall_avg['total_samples']:>15}")
    print("-" * 80)
    print()
    
    # 輸出到 CSV 檔案
    output_file = directory / 'ue_statistics_summary.csv'
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow(['UE_ID', 'Edge', 'Avg_Bitrate_kbps', 'Avg_RTT_ms', 'Avg_PacketLost', 'Samples'])
        
        for ue_id in sorted(ue_stats.keys(), key=lambda x: int(x)):
            stats = ue_stats[ue_id]
            row = [
                f'UE{ue_id}',
                stats['server'],
                f"{stats['bitrate']:.2f}",
                f"{stats['rtt']:.2f}",
                f"{stats['packetlost']:.2f}",
                stats['samples']
            ]
            writer.writerow(row)
        
        # 添加總平均 (OVERALL 不需要 Edge 欄位)
        overall_row = [
            'OVERALL',
            '',  # Edge 欄位留空
            f"{overall_avg['bitrate']:.2f}",
            f"{overall_avg['rtt']:.2f}",
            f"{overall_avg['packetlost']:.2f}",
            overall_avg['total_samples']
        ]
        writer.writerow(overall_row)
    
    print(f"✅ 統計結果已儲存至: {output_file}")
    print()
    
    # 額外統計資訊
    print("📈 額外統計資訊：")
    print("-" * 80)
    print(f"總 UE 數量: {len(ue_stats)}")
    print(f"總樣本數: {overall_avg['total_samples']}")
    print(f"平均每 UE 樣本數: {overall_avg['total_samples'] / len(ue_stats):.0f}")
    print()
    
    # 計算最大/最小值
    print("📊 各指標範圍 (所有 UE)：")
    print("-" * 80)
    print(f"Bitrate:     Min={min(all_data['bitrate']):.2f}, Max={max(all_data['bitrate']):.2f} kbps")
    print(f"RTT:         Min={min(all_data['rtt']):.2f}, Max={max(all_data['rtt']):.2f} ms")
    print(f"Packet Lost: Min={min(all_data['packetlost']):.2f}, Max={max(all_data['packetlost']):.2f}")
    print("-" * 80)


if __name__ == '__main__':
    main()
