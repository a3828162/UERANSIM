#!/usr/bin/env python3
"""
Experiment 2-3 數據分析和繪圖
讀取 exp2-3 資料夾下的所有 ue_statistics_summary.csv，繪製性能對比圖表
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 設置中文字體支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 方法名稱對應
METHOD_NAMES = {
    'rd': 'Random',
    'rr': 'RoundRobin',
    'sl': 'Smallest Latency',
    'sp': 'Shortest Path',
    'llm': 'LLM',
    'ra': 'RA',
    'sd': 'SD'
}

def extract_method_from_folder(folder_name):
    """從資料夾名稱提取方法名稱（_前面的部分）"""
    parts = folder_name.split('_')
    if len(parts) > 0:
        method_short = parts[0]
        # 返回完整名稱或縮寫
        return METHOD_NAMES.get(method_short, method_short)
    return folder_name

def collect_data(data_dir="./exp2-3", period=None):
    """收集 exp2-3 資料夾下的所有數據"""
    
    if not os.path.isdir(data_dir):
        print(f"✗ Error: Directory {data_dir} not found")
        return None
    
    data = {
        'scenario': [],
        'period': [],
        'fps': [],
        'bitrate': [],
        'rtt': [],
        'mos': []
    }
    
    # 遍歷 period 資料夾 (period5, period10)
    for period_folder in sorted(os.listdir(data_dir)):
        period_path = os.path.join(data_dir, period_folder)
        
        if not os.path.isdir(period_path):
            continue
        
        # 如果指定了 period，則只加載該 period
        if period and period_folder != f"period{period}":
            continue
        
        period_name = period_folder.replace("period", "")
        
        # 遍歷 scenario 資料夾 (p60, p80, p100, p120)
        for scenario_folder in sorted(os.listdir(period_path)):
            scenario_path = os.path.join(period_path, scenario_folder)
            
            if not os.path.isdir(scenario_path):
                continue
            
            # 查找ue_statistics_summary.csv
            csv_file = os.path.join(scenario_path, "ue_statistics_summary.csv")
            
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    
                    # 取OVERALL行的數據
                    overall_row = df[df['UE_ID'] == 'OVERALL']
                    
                    if not overall_row.empty:
                        data['scenario'].append(scenario_folder)
                        data['period'].append(f"period{period_name}")
                        data['fps'].append(overall_row['Avg_FPS'].values[0])
                        data['bitrate'].append(overall_row['Avg_Bitrate_kbps'].values[0])
                        data['rtt'].append(overall_row['Avg_RTT_ms'].values[0])
                        data['mos'].append(overall_row['MOS'].values[0])
                        
                        print(f"✓ Loaded: period={period_name}, scenario={scenario_folder}")
                    else:
                        print(f"✗ No OVERALL row in {csv_file}")
                except Exception as e:
                    print(f"✗ Error reading {csv_file}: {e}")
            else:
                print(f"✗ File not found: {csv_file}")
    
    if not data['scenario']:
        print("\n✗ No data collected!")
        return None
    
    return pd.DataFrame(data)

def plot_metrics(df, data_dir="./exp2-3"):
    """繪製4張柱狀圖合併為一張 2x2 的圖"""
    
    if df is None or df.empty:
        print("No data to plot!")
        return
    
    # 確保plot資料夾存在
    plot_dir = os.path.join(data_dir, "plot")
    os.makedirs(plot_dir, exist_ok=True)
    
    # 設置顏色和樣式
    scenarios = sorted(df['scenario'].unique(), key=lambda x: int(x.replace('p', '')))
    periods = sorted(df['period'].unique())
    
    # 使用美觀的配色方案
    academic_colors = [
        '#2E86AB',  # 深藍
        '#A23B72',  # 深紫紅
    ]
    period_colors = {period: academic_colors[i % len(academic_colors)] for i, period in enumerate(periods)}
    
    # 為每個指標生成柱狀圖
    metrics = [
        ('fps', 'FPS', 'FPS'),
        ('bitrate', 'Bitrate (kbps)', 'Bitrate'),
        ('rtt', 'RTT (ms)', 'RTT'),
        ('mos', 'MOS', 'MOS')
    ]
    
    # 創建 2x2 的 subplot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    for idx, (metric_col, metric_label, metric_title) in enumerate(metrics):
        ax = axes[idx]
        
        # 準備數據
        x_positions = np.arange(len(scenarios))
        bar_width = 0.35
        
        # 為每個 period 繪製柱狀圖
        for i, period in enumerate(periods):
            values = []
            for scenario in scenarios:
                data_subset = df[(df['scenario'] == scenario) & (df['period'] == period)]
                if not data_subset.empty:
                    values.append(data_subset[metric_col].values[0])
                else:
                    values.append(0)
            
            offset = (i - len(periods)/2 + 0.5) * bar_width
            ax.bar(x_positions + offset, values, bar_width,
                   label=period, color=period_colors[period], edgecolor='#333333', linewidth=1.2, alpha=0.85)
        
        # 設置標籤
        ax.set_xlabel('Scenario', fontsize=12, fontweight='bold', color='#333333')
        ax.set_ylabel(metric_label, fontsize=12, fontweight='bold', color='#333333')
        ax.set_title(f'{metric_title} Comparison', fontsize=13, fontweight='bold', color='#333333', pad=15)
        ax.set_xticks(x_positions)
        ax.set_xticklabels([s for s in scenarios], fontsize=11)
        
        # 改进图例和网格 - 将Method标记放在上方，不遮挡任何数据
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), fontsize=10, framealpha=0.92, 
                          edgecolor='#999999', fancybox=False, shadow=False, frameon=True, ncol=4)
        legend.get_frame().set_facecolor('white')
        legend.get_frame().set_linewidth(1.5)
        ax.grid(True, alpha=0.25, axis='y', linestyle='--', linewidth=0.8, color='#CCCCCC')
        ax.set_axisbelow(True)
        
        # 設置背景色和邊框
        ax.set_facecolor('#FAFAFA')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#CCCCCC')
        ax.spines['bottom'].set_color('#CCCCCC')
    
    fig.patch.set_facecolor('white')
    fig.suptitle('Experiment 2-3: Performance Metrics Comparison', fontsize=18, fontweight='bold', color='#333333', y=0.995)
    plt.tight_layout()
    
    # 保存圖表
    output_path = os.path.join(plot_dir, 'all_metrics_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Combined figure saved to: {output_path}")
    plt.close()

def print_statistics(df):
    """打印數據摘要"""
    print("\n" + "=" * 70)
    print("📊 Experiment 2-3 Data Summary")
    print("=" * 70)
    print(df.to_string(index=False))
    print("=" * 70)

def main():
    print("=" * 70)
    print("🚀 Experiment 2-3: Performance Analysis")
    print("=" * 70)
    print()
    
    # 設定數據目錄
    data_dir = "./exp2-3"
    
    print(f"📂 Loading data from {data_dir}...")
    print()
    
    # 收集數據 (可選：period=5 只加載 period5，或 period=10)
    df = collect_data(data_dir, period=None)
    
    if df is None or df.empty:
        print("\n✗ Failed to load data. Exiting.")
        return
    
    # 打印統計信息
    print_statistics(df)
    
    # 繪製圖表
    print("\n📈 Generating plots...")
    plot_metrics(df, data_dir)
    
    print("\n" + "=" * 70)
    print("✅ Analysis completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
