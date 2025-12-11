#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 設置中文字體支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 數據路徑
DATA_DIR = "/home/ubuntu/UERANSIM/experiment2/delay_new1"

def extract_method_from_folder(folder_name):
    """從資料夾名稱提取方法名稱（_前面的部分）"""
    parts = folder_name.split('_')
    if len(parts) > 0:
        return parts[0]
    return folder_name

def collect_data():
    """收集所有數據"""
    data = {
        'scenario': [],
        'method': [],
        'fps': [],
        'bitrate': [],
        'rtt': [],
        'mos': []
    }
    
    # 遍歷所有p*資料夾
    for scenario_folder in sorted(os.listdir(DATA_DIR)):
        scenario_path = os.path.join(DATA_DIR, scenario_folder)
        
        if not os.path.isdir(scenario_path):
            continue
        
        # 提取scenario號碼（例如 p60 -> 60）
        try:
            scenario_num = scenario_folder.replace('p', '')
        except:
            continue
        
        # 遍歷每個scenario下的方法資料夾
        for method_folder in sorted(os.listdir(scenario_path)):
            method_path = os.path.join(scenario_path, method_folder)
            
            if not os.path.isdir(method_path):
                continue
            
            # 提取方法名稱
            method = extract_method_from_folder(method_folder)
            
            # 查找ue_statistics_summary.csv
            csv_file = os.path.join(method_path, "ue_statistics_summary.csv")
            
            if os.path.exists(csv_file):
                try:
                    df = pd.read_csv(csv_file)
                    
                    # 取OVERALL行的數據
                    overall_row = df[df['UE_ID'] == 'OVERALL']
                    
                    if not overall_row.empty:
                        data['scenario'].append(scenario_num)
                        data['method'].append(method)
                        data['fps'].append(overall_row['Avg_FPS'].values[0])
                        data['bitrate'].append(overall_row['Avg_Bitrate_kbps'].values[0])
                        data['rtt'].append(overall_row['Avg_RTT_ms'].values[0])
                        data['mos'].append(overall_row['MOS'].values[0])
                        
                        print(f"✓ Loaded: scenario={scenario_num}, method={method}")
                    else:
                        print(f"✗ No OVERALL row in {csv_file}")
                except Exception as e:
                    print(f"✗ Error reading {csv_file}: {e}")
            else:
                print(f"✗ File not found: {csv_file}")
    
    return pd.DataFrame(data)

def plot_metrics(df):
    """繪製4張柱狀圖：FPS、Bitrate、RTT、MOS"""
    
    if df.empty:
        print("No data to plot!")
        return
    
    # 確保plot資料夾存在
    plot_dir = "/home/ubuntu/UERANSIM/experiment2/plot"
    os.makedirs(plot_dir, exist_ok=True)
    
    # 設置顏色和樣式
    methods = sorted(df['method'].unique())
    scenarios = sorted(df['scenario'].unique(), key=lambda x: int(x))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(methods)))
    method_colors = {method: colors[i] for i, method in enumerate(methods)}
    
    # 為每個指標生成柱狀圖
    metrics = [
        ('fps', 'FPS', 'FPS'),
        ('bitrate', 'Bitrate (kbps)', 'Bitrate'),
        ('rtt', 'RTT (ms)', 'RTT'),
        ('mos', 'MOS', 'MOS')
    ]
    
    for metric_col, metric_label, metric_title in metrics:
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
                    values.append(data[metric_col].values[0])
                else:
                    values.append(0)
            
            offset = (i - len(methods)/2 + 0.5) * bar_width
            ax.bar(x_positions + offset, values, bar_width, 
                   label=method, color=method_colors[method], edgecolor='black', linewidth=0.7)
        
        # 設置x軸標籤
        ax.set_xlabel('Scenario', fontsize=12, fontweight='bold')
        ax.set_ylabel(metric_label, fontsize=12, fontweight='bold')
        ax.set_title(f'Average {metric_title} by Scenario and Method', fontsize=14, fontweight='bold')
        ax.set_xticks(x_positions)
        ax.set_xticklabels([f'p{s}' for s in scenarios], fontsize=11)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # 保存圖表
        output_path = os.path.join(plot_dir, f'{metric_title.lower()}_comparison.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved to: {output_path}")
        plt.close()

def main():
    print("=" * 60)
    print("Loading data from delay_new1...")
    print("=" * 60)
    
    # 收集數據
    df = collect_data()
    
    print("\n" + "=" * 60)
    print(f"Total records loaded: {len(df)}")
    print("=" * 60)
    print("\nData Summary:")
    print(df.to_string(index=False))
    
    # 繪製圖表
    print("\n" + "=" * 60)
    print("Generating plots...")
    print("=" * 60)
    plot_metrics(df)

if __name__ == "__main__":
    main()
