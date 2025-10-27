#!/usr/bin/env python3
"""
統計 random_seed44 目錄下所有 UE 的性能指標。

計算每個 UE 和全部 UE 的平均值：
- FPS (framespersecond)
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
import subprocess
from pathlib import Path
from collections import defaultdict


def calculate_mos(csv_file, mos_binary_path):
    """使用 calculateMOS binary 計算 MOS 分數"""
    try:
        # 執行 calculateMOS binary
        result = subprocess.run(
            [str(mos_binary_path), str(csv_file)],
            capture_output=True,
            text=True,
            cwd=csv_file.parent.parent  # experiment2 目錄
        )
        
        if result.returncode == 0:
            # 解析輸出的 MOS 分數
            mos_score = float(result.stdout.strip())
            return mos_score
        else:
            print(f"  警告: 無法計算 {csv_file.name} 的 MOS: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"  警告: MOS 計算失敗 ({csv_file.name}): {e}")
        return None


def calculate_statistics(csv_file):
    """計算單個 CSV 檔案的統計數據"""
    stats = {
        'fps': [],
        'bitrate': [],
        'rtt': [],
        'packetlost': []
    }
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats['fps'].append(float(row['framespersecond']))
            stats['bitrate'].append(float(row['bitrate']))
            stats['rtt'].append(float(row['rtt']))
            stats['packetlost'].append(float(row['packetlost']))
    
    # 計算平均值
    averages = {
        'fps': sum(stats['fps']) / len(stats['fps']) if stats['fps'] else 0,
        'bitrate': sum(stats['bitrate']) / len(stats['bitrate']) if stats['bitrate'] else 0,
        'rtt': sum(stats['rtt']) / len(stats['rtt']) if stats['rtt'] else 0,
        'packetlost': sum(stats['packetlost']) / len(stats['packetlost']) if stats['packetlost'] else 0,
        'samples': len(stats['fps'])
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
    
    # 找到 calculateMOS binary
    mos_binary = Path(__file__).parent.parent / 'calculateMOS' / 'calculateMOS'
    if not mos_binary.exists():
        print(f"警告: 找不到 MOS 計算程式 {mos_binary}")
        print("將跳過 MOS 計算")
        mos_binary = None
    
    # 找到所有 performance_ue*.csv 檔案
    csv_files = sorted(directory.glob('performance_ue*.csv'))
    
    if not csv_files:
        print(f"錯誤: 在 {directory} 中找不到 performance_ue*.csv 檔案")
        sys.exit(1)
    
    print("=" * 80)
    print(f"統計目錄: {directory}")
    print(f"找到 {len(csv_files)} 個 UE 檔案")
    if mos_binary:
        print(f"MOS 計算程式: {mos_binary}")
    print("=" * 80)
    print()
    
    # 儲存每個 UE 的統計數據
    ue_stats = {}
    all_data = {
        'fps': [],
        'bitrate': [],
        'rtt': [],
        'packetlost': []
    }
    ue_mos_scores = {}
    
    # 計算每個 UE 的統計
    print("正在計算各 UE 統計數據...")
    for csv_file in csv_files:
        ue_id = csv_file.stem.replace('performance_ue', '')
        averages, raw_stats = calculate_statistics(csv_file)
        ue_stats[ue_id] = averages
        
        # 計算 MOS
        if mos_binary:
            print(f"  計算 UE{ue_id} MOS...", end=' ')
            mos_score = calculate_mos(csv_file, mos_binary)
            ue_mos_scores[ue_id] = mos_score
            if mos_score is not None:
                print(f"MOS = {mos_score:.2f}")
            else:
                print("失敗")
        
        # 累積所有數據
        all_data['fps'].extend(raw_stats['fps'])
        all_data['bitrate'].extend(raw_stats['bitrate'])
        all_data['rtt'].extend(raw_stats['rtt'])
        all_data['packetlost'].extend(raw_stats['packetlost'])
    
    print()
    
    # 顯示每個 UE 的統計
    print("📊 每個 UE 的平均統計：")
    print("-" * 90)
    if mos_binary and ue_mos_scores:
        print(f"{'UE ID':<8} {'FPS':>10} {'Bitrate (kbps)':>15} {'RTT (ms)':>12} {'Packet Lost':>12} {'MOS':>8} {'Samples':>10}")
    else:
        print(f"{'UE ID':<8} {'FPS':>10} {'Bitrate (kbps)':>15} {'RTT (ms)':>12} {'Packet Lost':>12} {'Samples':>10}")
    print("-" * 90)
    
    for ue_id in sorted(ue_stats.keys(), key=lambda x: int(x)):
        stats = ue_stats[ue_id]
        mos_str = f"{ue_mos_scores.get(ue_id, 0):.2f}" if ue_mos_scores.get(ue_id) is not None else "N/A"
        
        if mos_binary and ue_mos_scores:
            print(f"UE {ue_id:<5} {stats['fps']:>10.2f} {stats['bitrate']:>15.2f} {stats['rtt']:>12.2f} {stats['packetlost']:>12.2f} {mos_str:>8} {stats['samples']:>10}")
        else:
            print(f"UE {ue_id:<5} {stats['fps']:>10.2f} {stats['bitrate']:>15.2f} {stats['rtt']:>12.2f} {stats['packetlost']:>12.2f} {stats['samples']:>10}")
    
    print("-" * 90)
    
    # 計算全部 UE 的平均
    overall_avg = {
        'fps': sum(all_data['fps']) / len(all_data['fps']) if all_data['fps'] else 0,
        'bitrate': sum(all_data['bitrate']) / len(all_data['bitrate']) if all_data['bitrate'] else 0,
        'rtt': sum(all_data['rtt']) / len(all_data['rtt']) if all_data['rtt'] else 0,
        'packetlost': sum(all_data['packetlost']) / len(all_data['packetlost']) if all_data['packetlost'] else 0,
        'total_samples': len(all_data['fps'])
    }
    
    # 計算整體平均 MOS
    valid_mos_scores = [score for score in ue_mos_scores.values() if score is not None]
    overall_mos = sum(valid_mos_scores) / len(valid_mos_scores) if valid_mos_scores else None
    
    print()
    print("🎯 全部 UE 的總體平均：")
    print("-" * 90)
    if mos_binary and overall_mos is not None:
        print(f"{'Metric':<20} {'Average':>15} {'Total Samples':>15}")
    else:
        print(f"{'Metric':<20} {'Average':>15} {'Total Samples':>15}")
    print("-" * 90)
    print(f"{'FPS':<20} {overall_avg['fps']:>15.2f} {overall_avg['total_samples']:>15}")
    print(f"{'Bitrate (kbps)':<20} {overall_avg['bitrate']:>15.2f} {overall_avg['total_samples']:>15}")
    print(f"{'RTT (ms)':<20} {overall_avg['rtt']:>15.2f} {overall_avg['total_samples']:>15}")
    print(f"{'Packet Lost':<20} {overall_avg['packetlost']:>15.2f} {overall_avg['total_samples']:>15}")
    if mos_binary and overall_mos is not None:
        print(f"{'MOS':<20} {overall_mos:>15.2f} {len(valid_mos_scores):>15}")
    print("-" * 90)
    print()
    
    # 輸出到 CSV 檔案
    output_file = directory / 'ue_statistics_summary.csv'
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # 根據是否有 MOS 決定欄位
        if mos_binary and ue_mos_scores:
            writer.writerow(['UE_ID', 'Avg_FPS', 'Avg_Bitrate_kbps', 'Avg_RTT_ms', 'Avg_PacketLost', 'MOS', 'Samples'])
        else:
            writer.writerow(['UE_ID', 'Avg_FPS', 'Avg_Bitrate_kbps', 'Avg_RTT_ms', 'Avg_PacketLost', 'Samples'])
        
        for ue_id in sorted(ue_stats.keys(), key=lambda x: int(x)):
            stats = ue_stats[ue_id]
            row = [
                f'UE{ue_id}',
                f"{stats['fps']:.2f}",
                f"{stats['bitrate']:.2f}",
                f"{stats['rtt']:.2f}",
                f"{stats['packetlost']:.2f}"
            ]
            
            if mos_binary and ue_mos_scores:
                mos_value = ue_mos_scores.get(ue_id)
                row.append(f"{mos_value:.2f}" if mos_value is not None else "N/A")
            
            row.append(stats['samples'])
            writer.writerow(row)
        
        # 添加總平均
        overall_row = [
            'OVERALL',
            f"{overall_avg['fps']:.2f}",
            f"{overall_avg['bitrate']:.2f}",
            f"{overall_avg['rtt']:.2f}",
            f"{overall_avg['packetlost']:.2f}"
        ]
        
        if mos_binary and overall_mos is not None:
            overall_row.append(f"{overall_mos:.2f}")
        
        overall_row.append(overall_avg['total_samples'])
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
    print(f"FPS:         Min={min(all_data['fps']):.2f}, Max={max(all_data['fps']):.2f}")
    print(f"Bitrate:     Min={min(all_data['bitrate']):.2f}, Max={max(all_data['bitrate']):.2f} kbps")
    print(f"RTT:         Min={min(all_data['rtt']):.2f}, Max={max(all_data['rtt']):.2f} ms")
    print(f"Packet Lost: Min={min(all_data['packetlost']):.2f}, Max={max(all_data['packetlost']):.2f}")
    print("-" * 80)


if __name__ == '__main__':
    main()
