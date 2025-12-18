#!/usr/bin/env python3
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

# 預設數據路徑
DEFAULT_DATA_DIR = "/home/ubuntu/UERANSIM/yolo_client/delay"
DATA_DIR = DEFAULT_DATA_DIR
EXCLUDE_METHODS = []  # 要排除的方法列表，例如 ['Shortest Path', 'SD']

def extract_method_from_folder(folder_name):
    """從資料夾名稱提取方法名稱（_前面的部分）"""
    parts = folder_name.split('_')
    if len(parts) > 0:
        method_short = parts[0]
        # 返回完整名稱或縮寫
        return METHOD_NAMES.get(method_short, method_short)
    return folder_name

def collect_rtt_data():
    """收集只有RTT的數據（簡單平均：每個UE等權重）"""
    data = {
        'scenario': [],
        'method': [],
        'rtt': []
    }
    
    # 遍歷所有p*資料夾
    for scenario_folder in sorted(os.listdir(DATA_DIR)):
        scenario_path = os.path.join(DATA_DIR, scenario_folder)
        
        if not os.path.isdir(scenario_path):
            continue
        
        # 提取scenario號碼（例如 p60 -> 60）
        try:
            if scenario_folder.startswith('p'):
                scenario_num = scenario_folder.replace('p', '')
                scenario_display = scenario_folder  # 保持 p60 的格式用於顯示
            else:
                scenario_num = scenario_folder
                scenario_display = scenario_folder
        except:
            continue
        
        # 遍歷每個scenario下的方法資料夾
        for method_folder in sorted(os.listdir(scenario_path)):
            method_path = os.path.join(scenario_path, method_folder)
            
            if not os.path.isdir(method_path):
                continue
            
            # 提取方法名稱
            method = extract_method_from_folder(method_folder)
            
            # 優先查找 ue_statistics_summary.csv（使用簡單平均）
            summary_csv = os.path.join(method_path, 'ue_statistics_summary.csv')
            if os.path.exists(summary_csv):
                try:
                    df = pd.read_csv(summary_csv)
                    overall = df[df['UE_ID'] == 'OVERALL']
                    if not overall.empty:
                        avg_rtt = overall['Avg_RTT_ms'].values[0]
                        data['scenario'].append(scenario_display)
                        data['method'].append(method)
                        data['rtt'].append(avg_rtt)
                        print(f"✓ Loaded: scenario={scenario_display}, method={method}, avg_rtt={avg_rtt:.2f}ms (from summary)")
                        continue
                except Exception as e:
                    pass
            
            # 如果沒有 summary CSV，則從 performance_ue*.csv 計算（簡單平均各UE）
            rtt_values_by_ue = []
            
            for filename in os.listdir(method_path):
                if filename.startswith('performance_ue') and filename.endswith('.csv'):
                    csv_file = os.path.join(method_path, filename)
                    
                    try:
                        df = pd.read_csv(csv_file)
                        
                        # 檢查是否有 rtt 列
                        if 'rtt' in df.columns:
                            ue_rtt_values = df['rtt'].dropna().tolist()
                            if ue_rtt_values:
                                ue_avg_rtt = np.mean(ue_rtt_values)
                                rtt_values_by_ue.append(ue_avg_rtt)
                    except Exception as e:
                        pass
            
            # 計算簡單平均（每個UE等權重）
            if rtt_values_by_ue:
                avg_rtt = np.mean(rtt_values_by_ue)
                data['scenario'].append(scenario_display)
                data['method'].append(method)
                data['rtt'].append(avg_rtt)
                print(f"✓ Loaded: scenario={scenario_display}, method={method}, avg_rtt={avg_rtt:.2f}ms (simple avg)")
            else:
                print(f"✗ No RTT data found in {method_folder}")
    
    return pd.DataFrame(data)

def plot_rtt_metrics(df):
    """繪製RTT柱狀圖"""
    
    if df.empty:
        print("No data to plot!")
        return
    
    # 確保plot資料夾存在
    plot_dir = "/home/ubuntu/UERANSIM/yolo_client/plot"
    os.makedirs(plot_dir, exist_ok=True)
    
    # 設置顏色和樣式
    methods = sorted(df['method'].unique())
    # 對 scenario 進行智能排序
    scenarios_list = df['scenario'].unique()
    # 嘗試按 p 後面的數字排序
    try:
        scenarios = sorted(scenarios_list, key=lambda x: int(x.replace('p', '')) if x.startswith('p') else float('inf'))
    except:
        scenarios = sorted(scenarios_list)
    
    # 使用更美觀的配色方案（現代設計 + 學術專業）
    academic_colors = [
        '#2E86AB',  # 深藍
        '#A23B72',  # 深紫紅
        '#F18F01',  # 金橙
        '#C73E1D',  # 深紅
        '#6A994E',  # 深綠
        '#BC4749',  # 酒紅
        '#8B5A5A'   # 棕色
    ]
    method_colors = {method: academic_colors[i % len(academic_colors)] for i, method in enumerate(methods)}
    
    # 繪製RTT柱狀圖
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # 準備數據
    x_positions = np.arange(len(scenarios))
    bar_width = 0.15  # 每個柱子的寬度
    
    # 為每個方法繪製柱狀圖
    for i, method in enumerate(methods):
        values = []
        for scenario in scenarios:
            data = df[(df['scenario'] == scenario) & (df['method'] == method)]
            if not data.empty:
                values.append(data['rtt'].values[0])
            else:
                values.append(0)
        
        offset = (i - len(methods)/2 + 0.5) * bar_width
        ax.bar(x_positions + offset, values, bar_width, 
               label=method, color=method_colors[method], edgecolor='#333333', linewidth=1.2, alpha=0.85)
    
    # 設置x軸標籤
    ax.set_xlabel('Scenario', fontsize=13, fontweight='bold', color='#333333')
    ax.set_ylabel('RTT (ms)', fontsize=13, fontweight='bold', color='#333333')
    ax.set_title('RTT Performance Comparison', fontsize=15, fontweight='bold', color='#333333', pad=20)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(scenarios, fontsize=12)
    
    # 改進圖例和網格
    ax.legend(loc='best', fontsize=11, framealpha=0.98, edgecolor='#CCCCCC', fancybox=True, shadow=True)
    ax.grid(True, alpha=0.25, axis='y', linestyle='--', linewidth=0.8, color='#CCCCCC')
    ax.set_axisbelow(True)
    
    # 設置背景色和邊框
    ax.set_facecolor('#FAFAFA')
    fig.patch.set_facecolor('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    
    plt.tight_layout()
    
    # 保存圖表
    output_path = os.path.join(plot_dir, 'rtt_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✓ Figure saved to: {output_path}")
    plt.close()

def main():
    global DATA_DIR
    
    # 解析命令行參數
    if len(sys.argv) > 1:
        DATA_DIR = sys.argv[1]
        # 檢查路徑是否存在
        if not os.path.isdir(DATA_DIR):
            print(f"✗ Error: Directory not found: {DATA_DIR}")
            sys.exit(1)
    
    # 解析排除方法參數（--exclude method1,method2）
    exclude_methods_str = None
    if len(sys.argv) > 2 and sys.argv[2].startswith('--exclude'):
        if '=' in sys.argv[2]:
            exclude_methods_str = sys.argv[2].split('=', 1)[1]
        elif len(sys.argv) > 3:
            exclude_methods_str = sys.argv[3]
    
    if exclude_methods_str:
        global EXCLUDE_METHODS
        EXCLUDE_METHODS = [m.strip() for m in exclude_methods_str.split(',')]
        print(f"Excluding methods: {', '.join(EXCLUDE_METHODS)}")
    
    print("=" * 60)
    print(f"Loading RTT data from: {DATA_DIR}")
    print("=" * 60)
    
    # 收集RTT數據
    df = collect_rtt_data()
    
    # 排除指定的方法
    if EXCLUDE_METHODS:
        df = df[~df['method'].isin(EXCLUDE_METHODS)]
        print(f"\n✓ Excluded methods: {', '.join(EXCLUDE_METHODS)}")
    
    print("\n" + "=" * 60)
    print(f"Total records loaded: {len(df)}")
    print("=" * 60)
    print("\nData Summary:")
    print(df.to_string(index=False))
    
    # 繪製圖表
    print("\n" + "=" * 60)
    print("Generating plots...")
    print("=" * 60)
    plot_rtt_metrics(df)

if __name__ == "__main__":
    main()
