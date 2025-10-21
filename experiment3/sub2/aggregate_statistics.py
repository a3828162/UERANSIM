import pandas as pd
import re
from pathlib import Path

def extract_statistics_from_log(log_file):
    """
    從log文件提取Statistics部分的統計數據
    """
    with open(log_file, 'r') as f:
        content = f.read()
    
    stats = {}
    
    # 提取 Queries sent
    match = re.search(r'Queries sent:\s+(\d+)', content)
    if match:
        stats['queries_sent'] = int(match.group(1))
    
    # 提取 Queries completed (number and percentage)
    match = re.search(r'Queries completed:\s+(\d+)\s+\(([\d.]+)%\)', content)
    if match:
        stats['queries_completed'] = int(match.group(1))
        stats['queries_completed_pct'] = float(match.group(2))
    
    # 提取 Queries lost (number and percentage)
    match = re.search(r'Queries lost:\s+(\d+)\s+\(([\d.]+)%\)', content)
    if match:
        stats['queries_lost'] = int(match.group(1))
        stats['queries_lost_pct'] = float(match.group(2))
    
    # 提取 Average Latency (包括 min, max)
    match = re.search(r'Average Latency \(s\):\s+([\d.]+)\s+\(min\s+([\d.]+),\s+max\s+([\d.]+)\)', content)
    if match:
        stats['avg_latency_sec'] = float(match.group(1))
        stats['min_latency_sec'] = float(match.group(2))
        stats['max_latency_sec'] = float(match.group(3))
        # 轉換成毫秒
        stats['avg_latency_ms'] = stats['avg_latency_sec'] * 1000
        stats['min_latency_ms'] = stats['min_latency_sec'] * 1000
        stats['max_latency_ms'] = stats['max_latency_sec'] * 1000
    
    # 提取 Latency StdDev
    match = re.search(r'Latency StdDev \(s\):\s+([\d.]+)', content)
    if match:
        stats['latency_stddev_sec'] = float(match.group(1))
        stats['latency_stddev_ms'] = float(match.group(1)) * 1000
    
    # 提取 Queries per second
    match = re.search(r'Queries per second:\s+([\d.]+)', content)
    if match:
        stats['queries_per_second'] = float(match.group(1))
    
    return stats

def process_scenario(scenario_path, scenario_name, ue_count):
    """處理一個scenario資料夾，計算所有UE的平均統計"""
    print(f"Processing {scenario_name}...")
    
    scenario_dir = Path(scenario_path)
    log_files = sorted(scenario_dir.glob('ue_*_latency.log'))
    
    all_stats = []
    
    for log_file in log_files:
        stats = extract_statistics_from_log(log_file)
        if stats:
            all_stats.append(stats)
        else:
            print(f"  Warning: Could not extract stats from {log_file.name}")
    
    if not all_stats:
        print(f"  Error: No valid statistics found!")
        return None
    
    # 計算平均值
    df = pd.DataFrame(all_stats)
    
    avg_stats = {
        'Scenario': scenario_name,
        'UE_Count': ue_count,
        'Total_UEs': len(all_stats),
        'Queries_Sent_Avg': df['queries_sent'].mean(),
        'Queries_Completed_Avg': df['queries_completed'].mean(),
        'Queries_Completed_Pct': df['queries_completed_pct'].mean(),
        'Queries_Lost_Avg': df['queries_lost'].mean(),
        'Queries_Lost_Pct': df['queries_lost_pct'].mean(),
        'Avg_Latency_ms': df['avg_latency_ms'].mean(),
        'Min_Latency_ms': df['min_latency_ms'].mean(),
        'Max_Latency_ms': df['max_latency_ms'].mean(),
        'Latency_StdDev_ms': df['latency_stddev_ms'].mean(),
        'Queries_Per_Second': df['queries_per_second'].mean()
    }
    
    print(f"  Processed {len(all_stats)} UE files")
    print(f"  Average Latency: {avg_stats['Avg_Latency_ms']:.3f} ms")
    
    return avg_stats

def main():
    print("="*70)
    print("DNS Statistics Aggregation")
    print("="*70)
    
    # 定義scenarios
    base_path = Path('/home/ubuntu/UERANSIM/experiment3/sub2')
    scenarios = [
        ('10ue', 10),
        ('30ue', 30),
        ('50ue', 50),
        ('100ue', 100),
        ('200ue', 200)
    ]
    
    results = []
    
    # 處理每個scenario
    for scenario_name, ue_count in scenarios:
        scenario_path = base_path / scenario_name
        
        if not scenario_path.exists():
            print(f"Warning: {scenario_path} does not exist, skipping...")
            continue
        
        stats = process_scenario(scenario_path, scenario_name, ue_count)
        if stats:
            results.append(stats)
    
    # 創建DataFrame
    df_results = pd.DataFrame(results)
    
    # 保存CSV
    output_file = 'dns_statistics_summary.csv'
    df_results.to_csv(output_file, index=False, float_format='%.4f')
    
    print("\n" + "="*70)
    print("Summary Statistics")
    print("="*70)
    print(df_results.to_string(index=False))
    
    print("\n" + "="*70)
    print(f"✅ CSV file saved: {output_file}")
    print("="*70)
    
    # 顯示關鍵指標比較
    print("\n" + "="*70)
    print("Key Metrics Comparison")
    print("="*70)
    
    comparison = df_results[['Scenario', 'UE_Count', 'Queries_Lost_Pct', 
                             'Avg_Latency_ms', 'Min_Latency_ms', 
                             'Max_Latency_ms', 'Latency_StdDev_ms']].copy()
    print(comparison.to_string(index=False))
    
    return df_results

if __name__ == "__main__":
    df = main()
