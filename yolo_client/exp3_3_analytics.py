#!/usr/bin/env python3
"""
實驗 3.3 數據分析：分析多 UE 場景下的 RTT 變化
讀取 ex3-3data 資料夾中各個 UE 配置的統計數據，繪製 RTT vs UE 數量的折線圖
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

# 設置中文字體支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def collect_rtt_data():
    """收集各個 UE 配置下的 RTT 數據"""
    data_dir = "./ex3-3data"
    
    if not os.path.exists(data_dir):
        print(f"✗ Error: Directory {data_dir} not found")
        return None
    
    rtt_data = {
        'ue_count': [],
        'avg_rtt': []
    }
    
    # 遍歷 ue_1_exp3_3 到 ue_8_exp3_3 資料夾
    for ue_count in range(1, 9):
        folder_name = f"ue_{ue_count}_exp3_3"
        folder_path = os.path.join(data_dir, folder_name)
        csv_file = os.path.join(folder_path, "ue_statistics_summary.csv")
        
        if not os.path.exists(csv_file):
            print(f"✗ File not found: {csv_file}")
            continue
        
        try:
            df = pd.read_csv(csv_file)
            
            # 取 OVERALL 行的數據
            overall_row = df[df['UE_ID'] == 'OVERALL']
            
            if not overall_row.empty:
                avg_rtt = overall_row['Avg_RTT_ms'].values[0]
                rtt_data['ue_count'].append(ue_count)
                rtt_data['avg_rtt'].append(avg_rtt)
                print(f"✓ UE {ue_count}: RTT = {avg_rtt:.2f} ms")
            else:
                print(f"✗ No OVERALL row in {csv_file}")
        except Exception as e:
            print(f"✗ Error reading {csv_file}: {e}")
    
    if not rtt_data['ue_count']:
        print("\n✗ No data collected!")
        return None
    
    return pd.DataFrame(rtt_data)

def plot_rtt_analysis(df):
    """繪製 RTT vs UE 數量的折線圖"""
    
    if df is None or df.empty:
        print("✗ No data to plot!")
        return
    
    # 確保 plot 資料夾存在
    plot_dir = "./plot"
    os.makedirs(plot_dir, exist_ok=True)
    
    # 創建圖表
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 使用美觀的配色
    line_color = '#2E86AB'
    marker_color = '#A23B72'
    
    # 繪製折線圖
    ax.plot(df['ue_count'], df['avg_rtt'], 
            marker='o', markersize=10, linewidth=2.5,
            color=line_color, markerfacecolor=marker_color, 
            markeredgecolor=line_color, markeredgewidth=2,
            label='Average RTT')
    
    # 設置標籤和標題
    ax.set_xlabel('Number of Concurrent UEs', fontsize=13, fontweight='bold', color='#333333')
    ax.set_ylabel('Average RTT (ms)', fontsize=13, fontweight='bold', color='#333333')
    ax.set_title('RTT Performance vs Concurrent UE Count (Experiment 3.3)', 
                 fontsize=15, fontweight='bold', color='#333333', pad=20)
    
    # 設置 X 軸為整數
    ax.set_xticks(df['ue_count'])
    ax.set_xticklabels([int(x) for x in df['ue_count']])
    
    # 改進網格和樣式
    ax.grid(True, alpha=0.25, axis='y', linestyle='--', linewidth=0.8, color='#CCCCCC')
    ax.set_axisbelow(True)
    
    # 設置背景色和邊框
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    
    # 添加圖例
    ax.legend(loc='best', fontsize=11, framealpha=0.98, edgecolor='#CCCCCC', fancybox=True, shadow=True)
    
    plt.tight_layout()
    
    # 保存圖表
    output_path = os.path.join(plot_dir, 'exp3_3_rtt_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"\n✓ Figure saved to: {output_path}")
    
    plt.show()

def print_statistics(df):
    """打印統計信息"""
    print("\n" + "=" * 70)
    print("📊 Experiment 3.3 RTT Analysis Summary")
    print("=" * 70)
    print("\nData Summary:")
    print(df.to_string(index=False))
    
    print("\n" + "-" * 70)
    print("📈 Statistics:")
    print("-" * 70)
    print(f"Min RTT:     {df['avg_rtt'].min():.2f} ms (at {df.loc[df['avg_rtt'].idxmin(), 'ue_count']:.0f} UE(s))")
    print(f"Max RTT:     {df['avg_rtt'].max():.2f} ms (at {df.loc[df['avg_rtt'].idxmax(), 'ue_count']:.0f} UE(s))")
    print(f"Mean RTT:    {df['avg_rtt'].mean():.2f} ms")
    print(f"RTT Growth:  {df['avg_rtt'].iloc[-1] - df['avg_rtt'].iloc[0]:.2f} ms ({((df['avg_rtt'].iloc[-1] / df['avg_rtt'].iloc[0]) - 1) * 100:.1f}%)")
    print("-" * 70)

def main():
    print("=" * 70)
    print("🚀 Experiment 3.3 Analytics: Multi-UE RTT Analysis")
    print("=" * 70)
    print()
    
    # 收集數據
    print("📂 Loading data from ex3-3data folder...")
    print()
    df = collect_rtt_data()
    
    if df is None or df.empty:
        print("\n✗ Failed to load data. Exiting.")
        return
    
    # 打印統計信息
    print_statistics(df)
    
    # 繪製圖表
    print("\n📈 Generating plots...")
    plot_rtt_analysis(df)
    
    print("\n" + "=" * 70)
    print("✅ Analysis completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
