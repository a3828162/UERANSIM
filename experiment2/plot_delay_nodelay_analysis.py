#!/usr/bin/env python3
"""
視覺化分析腳本 - 分別分析 delay 和 nodelay 場景
Resource-Satisfied (6UE) vs Resource-Overloaded (7UE)
比較 Random, RoundRobin, LLM, ShortestPath 方法
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 設定字體和樣式
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

# 方法顏色和標記定義
METHOD_COLORS = {
    'Random': '#FF6B6B', 
    'RoundRobin': '#4ECDC4', 
    'LLM': '#95E1D3', 
    'ShortestPath': '#FFD93D',
    'SmallestDelay': '#A8E6CF'
}

METHOD_MARKERS = {
    'Random': 'o', 
    'RoundRobin': 's', 
    'LLM': '^', 
    'ShortestPath': 'D',
    'SmallestDelay': 'v'
}

class ConditionAnalyzer:
    def __init__(self, base_dir="/home/ubuntu/UERANSIM/experiment2", condition="nodelay", exclude_methods=None):
        self.base_dir = Path(base_dir)
        self.condition = condition  # 'delay' or 'nodelay'
        self.condition_dir = self.base_dir / condition
        self.exclude_methods = exclude_methods or []  # 要排除的方法列表
        
        # 創建輸出資料夾
        self.output_dir = Path("/home/ubuntu/UERANSIM/experiment2/plots") / condition
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 創建子資料夾
        (self.output_dir / "resource_satisfied").mkdir(exist_ok=True)
        (self.output_dir / "resource_overloaded").mkdir(exist_ok=True)
        (self.output_dir / "cross_scenario").mkdir(exist_ok=True)
        (self.output_dir / "fairness_analysis").mkdir(exist_ok=True)
        
        # 儲存兩種場景的資料
        self.data_6ue = {}  # Resource-Satisfied
        self.data_7ue = {}  # Resource-Overloaded
        
    def load_data(self):
        """載入指定 condition 的所有 CSV 資料"""
        print(f"📂 載入 {self.condition.upper()} 資料...")
        
        if not self.condition_dir.exists():
            print(f"  ❌ 錯誤: {self.condition_dir} 不存在")
            return
        
        # 嘗試兩種資料夾結構
        # 結構 1: nodelay/6ue/ 和 nodelay/7ue/
        # 結構 2: delay/resource_satisfy/ 和 delay/resource_overload/
        
        # 6UE 資料 (Resource-Satisfied)
        ue6_dirs = [
            self.condition_dir / "6ue",
            self.condition_dir / "resource_satisfy"
        ]
        
        for ue6_dir in ue6_dirs:
            if ue6_dir.exists():
                for method_dir in ue6_dir.iterdir():
                    if method_dir.is_dir():
                        csv_file = method_dir / "ue_statistics_summary.csv"
                        if csv_file.exists():
                            method = self._extract_method_name(method_dir.name)
                            if method is None:
                                continue
                            
                            # 檢查是否要排除此方法
                            if method in self.exclude_methods:
                                print(f"  ⊝ Resource-Satisfied (6UE) - {method}: 已排除")
                                continue
                            
                            df = pd.read_csv(csv_file)
                            self.data_6ue[method] = df
                            print(f"  ✓ Resource-Satisfied (6UE) - {method}: {len(df)} rows")
                break  # 找到資料後跳出
        
        # 7UE 資料 (Resource-Overloaded)
        ue7_dirs = [
            self.condition_dir / "7ue",
            self.condition_dir / "resource_overload"
        ]
        
        for ue7_dir in ue7_dirs:
            if ue7_dir.exists():
                for method_dir in ue7_dir.iterdir():
                    if method_dir.is_dir():
                        csv_file = method_dir / "ue_statistics_summary.csv"
                        if csv_file.exists():
                            method = self._extract_method_name(method_dir.name)
                            if method is None:
                                continue
                            
                            # 檢查是否要排除此方法
                            if method in self.exclude_methods:
                                print(f"  ⊝ Resource-Overloaded (7UE) - {method}: 已排除")
                                continue
                            
                            df = pd.read_csv(csv_file)
                            self.data_7ue[method] = df
                            print(f"  ✓ Resource-Overloaded (7UE) - {method}: {len(df)} rows")
                break  # 找到資料後跳出
        
        print(f"\n✅ 載入完成:")
        print(f"   Resource-Satisfied (6UE): {len(self.data_6ue)} 種方法")
        print(f"   Resource-Overloaded (7UE): {len(self.data_7ue)} 種方法\n")
    
    def _extract_method_name(self, dirname):
        """從資料夾名稱提取方法名稱"""
        dirname_lower = dirname.lower()
        # 支援簡短前綴 (ld_, llm_, rd_, rr_, sp_)
        if dirname_lower.startswith('ld_'):
            return 'SmallestDelay'
        elif dirname_lower.startswith('llm_'):
            return 'LLM'
        elif dirname_lower.startswith('rd_'):
            return 'Random'
        elif dirname_lower.startswith('rr_'):
            return 'RoundRobin'
        elif dirname_lower.startswith('sp_'):
            return 'ShortestPath'
        # 支援完整方法名稱 (lowestdelay, smallestdelay, random, roundrobin, shortestpath)
        elif 'lowestdelay' in dirname_lower or 'smallestdelay' in dirname_lower:
            return 'SmallestDelay'
        elif 'random' in dirname_lower:
            return 'Random'
        elif 'roundrobin' in dirname_lower:
            return 'RoundRobin'
        elif 'shortestpath' in dirname_lower:
            return 'ShortestPath'
        else:
            return None
    
    def plot_method_comparison(self, scenario='6ue'):
        """方法比較 - 群組柱狀圖"""
        data = self.data_6ue if scenario == '6ue' else self.data_7ue
        scenario_name = 'Resource-Satisfied' if scenario == '6ue' else 'Resource-Overloaded'
        num_ues = 6 if scenario == '6ue' else 7
        
        print(f"📊 繪製 {scenario_name} ({num_ues}UE) 方法比較圖...")
        
        # 準備 OVERALL 資料
        metrics = ['MOS', 'Avg_FPS', 'Avg_Bitrate_kbps', 'Avg_RTT_ms']
        metric_labels = ['MOS', 'FPS', 'Bitrate (kbps)', 'RTT (ms)']
        
        overall_data = {}
        for method, df in data.items():
            overall_row = df[df['UE_ID'] == 'OVERALL'].iloc[0]
            overall_data[method] = overall_row
        
        # 創建 2x2 子圖
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{scenario_name} - {self.condition.upper()} - Method Comparison', 
                    fontsize=16, fontweight='bold')
        
        methods = sorted(overall_data.keys())
        x = np.arange(len(methods))
        width = 0.6
        
        for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ax = axes[idx // 2, idx % 2]
            
            values = [overall_data[method][metric] for method in methods]
            bars = ax.bar(x, values, width, color=[METHOD_COLORS.get(m, '#999') for m in methods])
            
            # 數值標籤
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.2f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_xlabel('Method', fontsize=11, fontweight='bold')
            ax.set_ylabel(label, fontsize=11, fontweight='bold')
            ax.set_title(f'{label} Comparison', fontsize=12, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(methods, fontsize=10)
            ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        folder_name = "resource_satisfied" if scenario == '6ue' else "resource_overloaded"
        output_file = self.output_dir / folder_name / f"{scenario}_method_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def plot_fairness_boxplot(self, scenario='6ue'):
        """公平性分析 - 箱型圖"""
        data = self.data_6ue if scenario == '6ue' else self.data_7ue
        scenario_name = 'Resource-Satisfied' if scenario == '6ue' else 'Resource-Overloaded'
        num_ues = 6 if scenario == '6ue' else 7
        
        print(f"📊 繪製 {scenario_name} ({num_ues}UE) 公平性箱型圖...")
        
        # 準備資料 (排除 OVERALL)
        plot_data = []
        for method, df in data.items():
            ue_data = df[df['UE_ID'] != 'OVERALL']
            for _, row in ue_data.iterrows():
                plot_data.append({
                    'Method': method,
                    'MOS': row['MOS'],
                    'FPS': row['Avg_FPS'],
                    'RTT': row['Avg_RTT_ms']
                })
        
        df_plot = pd.DataFrame(plot_data)
        
        # 創建 1x3 子圖
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle(f'{scenario_name} - {self.condition.upper()} - Fairness Analysis', 
                    fontsize=16, fontweight='bold')
        
        methods = sorted(data.keys())
        metrics = ['MOS', 'FPS', 'RTT']
        titles = ['MOS Distribution', 'FPS Distribution', 'RTT Distribution (ms)']
        
        for idx, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[idx]
            
            # 箱型圖
            bp = ax.boxplot([df_plot[df_plot['Method'] == m][metric].values 
                             for m in methods],
                            labels=methods,
                            patch_artist=True,
                            showmeans=True,
                            meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
            
            # 上色
            for patch, method in zip(bp['boxes'], methods):
                patch.set_facecolor(METHOD_COLORS.get(method, '#999'))
                patch.set_alpha(0.6)
            
            # 疊加散點圖
            for i, method in enumerate(methods, 1):
                method_data = df_plot[df_plot['Method'] == method][metric].values
                x = np.random.normal(i, 0.04, size=len(method_data))
                ax.scatter(x, method_data, alpha=0.5, s=50, color=METHOD_COLORS.get(method, '#999'))
            
            ax.set_ylabel(metric, fontsize=11, fontweight='bold')
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        folder_name = "resource_satisfied" if scenario == '6ue' else "resource_overloaded"
        output_file = self.output_dir / folder_name / f"{scenario}_fairness_boxplot.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def plot_radar_chart(self, scenario='6ue'):
        """雷達圖 - 綜合能力"""
        data = self.data_6ue if scenario == '6ue' else self.data_7ue
        scenario_name = 'Resource-Satisfied' if scenario == '6ue' else 'Resource-Overloaded'
        num_ues = 6 if scenario == '6ue' else 7
        
        print(f"📊 繪製 {scenario_name} ({num_ues}UE) 雷達圖...")
        
        # 準備資料
        metrics = ['MOS', 'Avg_FPS', 'Avg_Bitrate_kbps', 'Avg_RTT_ms', 'Avg_PacketLost']
        labels = ['MOS', 'FPS', 'Bitrate', 'Low RTT', 'Low PacketLoss']
        
        overall_data = {}
        for method, df in data.items():
            overall_row = df[df['UE_ID'] == 'OVERALL'].iloc[0]
            overall_data[method] = overall_row
        
        # 正規化 (0-100)
        normalized = {}
        for method in overall_data.keys():
            row = overall_data[method]
            normalized[method] = [
                row['MOS'] / 5 * 100,  # MOS (0-5 -> 0-100)
                row['Avg_FPS'] / 60 * 100,  # FPS (0-60 -> 0-100)
                row['Avg_Bitrate_kbps'] / 5000 * 100,  # Bitrate (0-5000 -> 0-100)
                (50 - row['Avg_RTT_ms']) / 50 * 100 if row['Avg_RTT_ms'] < 50 else 0,  # RTT 越低越好
                (1 - row['Avg_PacketLost']) * 100  # PacketLost 越低越好
            ]
        
        # 繪製雷達圖
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        for method, values in normalized.items():
            values += values[:1]
            ax.plot(angles, values, 'o-', linewidth=2, label=method, 
                   color=METHOD_COLORS.get(method, '#999'))
            ax.fill(angles, values, alpha=0.15, color=METHOD_COLORS.get(method, '#999'))
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.grid(True)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
        ax.set_title(f'{scenario_name} - {self.condition.upper()}\nComprehensive Performance', 
                    fontsize=14, fontweight='bold', pad=20)
        
        folder_name = "resource_satisfied" if scenario == '6ue' else "resource_overloaded"
        output_file = self.output_dir / folder_name / f"{scenario}_radar_chart.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def plot_ue_heatmap(self, scenario='6ue'):
        """個別 UE 表現 - 熱力圖"""
        data = self.data_6ue if scenario == '6ue' else self.data_7ue
        scenario_name = 'Resource-Satisfied' if scenario == '6ue' else 'Resource-Overloaded'
        num_ues = 6 if scenario == '6ue' else 7
        
        print(f"📊 繪製 {scenario_name} ({num_ues}UE) UE 熱力圖...")
        
        # 準備資料矩陣
        methods = sorted(data.keys())
        ue_ids = [f'UE{i}' for i in range(1, num_ues + 1)]
        
        mos_matrix = []
        for method in methods:
            df = data[method]
            ue_mos = []
            for ue_id in ue_ids:
                mos = df[df['UE_ID'] == ue_id]['MOS'].values
                ue_mos.append(mos[0] if len(mos) > 0 else 0)
            mos_matrix.append(ue_mos)
        
        mos_matrix = np.array(mos_matrix)
        
        # 繪製熱力圖
        fig, ax = plt.subplots(figsize=(10, 6))
        
        im = ax.imshow(mos_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=5)
        
        # 設定標籤
        ax.set_xticks(np.arange(len(ue_ids)))
        ax.set_yticks(np.arange(len(methods)))
        ax.set_xticklabels(ue_ids)
        ax.set_yticklabels(methods)
        
        # 旋轉標籤
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
        
        # 顯示數值
        for i in range(len(methods)):
            for j in range(len(ue_ids)):
                text = ax.text(j, i, f'{mos_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=11, fontweight='bold')
        
        ax.set_title(f'{scenario_name} - {self.condition.upper()}\nMOS Heatmap', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('UE ID', fontsize=12, fontweight='bold')
        ax.set_ylabel('Method', fontsize=12, fontweight='bold')
        
        # 顏色條
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('MOS', rotation=270, labelpad=20, fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        folder_name = "resource_satisfied" if scenario == '6ue' else "resource_overloaded"
        output_file = self.output_dir / folder_name / f"{scenario}_ue_heatmap.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def plot_scalability_analysis(self):
        """擴展性分析 - 折線圖"""
        print(f"📊 繪製跨場景擴展性分析...")
        
        scenarios = ['Resource-Satisfied\n(6 UE)', 'Resource-Overloaded\n(7 UE)']
        methods = sorted(set(list(self.data_6ue.keys()) + list(self.data_7ue.keys())))
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle(f'{self.condition.upper()} - Scalability Analysis', 
                    fontsize=16, fontweight='bold')
        
        metrics = ['MOS', 'Avg_FPS', 'Avg_Bitrate_kbps']
        titles = ['MOS Scalability', 'FPS Scalability', 'Bitrate Scalability']
        ylabels = ['MOS', 'FPS', 'Bitrate (kbps)']
        
        for idx, (metric, title, ylabel) in enumerate(zip(metrics, titles, ylabels)):
            ax = axes[idx]
            
            for method in methods:
                values = []
                for data in [self.data_6ue, self.data_7ue]:
                    if method in data:
                        overall = data[method][data[method]['UE_ID'] == 'OVERALL'].iloc[0]
                        values.append(overall[metric])
                    else:
                        values.append(None)
                
                if None not in values:
                    ax.plot(scenarios, values, marker=METHOD_MARKERS.get(method, 'o'), 
                           linewidth=2.5, markersize=10, label=method,
                           color=METHOD_COLORS.get(method, '#999'))
                    
                    # 顯示數值
                    for x, y in zip(scenarios, values):
                        ax.text(x, y, f'{y:.1f}', ha='center', va='bottom', 
                               fontsize=9, fontweight='bold')
            
            ax.set_xlabel('Scenario', fontsize=11, fontweight='bold')
            ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "cross_scenario" / "scalability_lineplot.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def plot_performance_delta(self):
        """性能變化分析 - 柱狀圖"""
        print(f"📊 繪製性能變化分析...")
        
        methods = sorted(set(list(self.data_6ue.keys()) + list(self.data_7ue.keys())))
        
        # 計算差異
        deltas = {'MOS': {}, 'FPS': {}, 'Bitrate': {}}
        
        for method in methods:
            if method in self.data_6ue and method in self.data_7ue:
                overall_6 = self.data_6ue[method][self.data_6ue[method]['UE_ID'] == 'OVERALL'].iloc[0]
                overall_7 = self.data_7ue[method][self.data_7ue[method]['UE_ID'] == 'OVERALL'].iloc[0]
                
                deltas['MOS'][method] = overall_7['MOS'] - overall_6['MOS']
                deltas['FPS'][method] = overall_7['Avg_FPS'] - overall_6['Avg_FPS']
                deltas['Bitrate'][method] = overall_7['Avg_Bitrate_kbps'] - overall_6['Avg_Bitrate_kbps']
        
        # 繪製
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle(f'{self.condition.upper()} - Performance Change: Overloaded - Satisfied (Δ)', 
                    fontsize=16, fontweight='bold')
        
        for idx, (metric, title) in enumerate([('MOS', 'Δ MOS'), 
                                               ('FPS', 'Δ FPS'), 
                                               ('Bitrate', 'Δ Bitrate (kbps)')]):
            ax = axes[idx]
            
            methods_with_data = list(deltas[metric].keys())
            values = list(deltas[metric].values())
            x = np.arange(len(methods_with_data))
            
            bars = ax.bar(x, values, color=[METHOD_COLORS.get(m, '#999') for m in methods_with_data], alpha=0.7)
            
            # 數值標籤
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:+.2f}',
                       ha='center', va='bottom' if val > 0 else 'top', 
                       fontsize=10, fontweight='bold')
            
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
            ax.set_xticks(x)
            ax.set_xticklabels(methods_with_data)
            ax.set_ylabel(title, fontsize=11, fontweight='bold')
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "cross_scenario" / "performance_delta.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def plot_fairness_cv(self):
        """公平性 - 變異係數"""
        print(f"📊 繪製公平性變異係數分析...")
        
        # 計算 CV
        cv_data = []
        gap_data = []
        
        for scenario, data, name in [('6UE', self.data_6ue, 'Resource-Satisfied'), 
                                     ('7UE', self.data_7ue, 'Resource-Overloaded')]:
            for method, df in data.items():
                ue_data = df[df['UE_ID'] != 'OVERALL']
                mos_values = ue_data['MOS'].values
                
                mean_mos = np.mean(mos_values)
                std_mos = np.std(mos_values)
                cv = (std_mos / mean_mos) * 100  # 百分比
                gap = np.max(mos_values) - np.min(mos_values)
                
                cv_data.append({
                    'Scenario': name,
                    'Method': method,
                    'CV': cv
                })
                
                gap_data.append({
                    'Scenario': name,
                    'Method': method,
                    'Gap': gap
                })
        
        df_cv = pd.DataFrame(cv_data)
        df_gap = pd.DataFrame(gap_data)
        
        # 繪製
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'{self.condition.upper()} - Fairness Analysis (CV & MOS Gap)', 
                    fontsize=16, fontweight='bold')
        
        methods = sorted(df_cv['Method'].unique())
        scenarios = df_cv['Scenario'].unique()
        x = np.arange(len(methods))
        width = 0.35
        
        # 左圖: CV 比較
        ax = axes[0]
        for i, scenario in enumerate(scenarios):
            scenario_data = df_cv[df_cv['Scenario'] == scenario]
            values = [scenario_data[scenario_data['Method'] == m]['CV'].values[0] 
                     if len(scenario_data[scenario_data['Method'] == m]) > 0 else 0
                     for m in methods]
            
            bars = ax.bar(x + i*width, values, width, label=scenario, alpha=0.8)
            
            # 數值標籤
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.1f}%',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Method', fontsize=11, fontweight='bold')
        ax.set_ylabel('CV (%)', fontsize=11, fontweight='bold')
        ax.set_title('Coefficient of Variation\n(Lower is Better)', fontsize=12, fontweight='bold')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(methods)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # 右圖: Max-Min Gap
        ax = axes[1]
        for i, scenario in enumerate(scenarios):
            scenario_data = df_gap[df_gap['Scenario'] == scenario]
            values = [scenario_data[scenario_data['Method'] == m]['Gap'].values[0]
                     if len(scenario_data[scenario_data['Method'] == m]) > 0 else 0
                     for m in methods]
            
            bars = ax.bar(x + i*width, values, width, label=scenario, alpha=0.8)
            
            # 數值標籤
            for bar, val in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.2f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Method', fontsize=11, fontweight='bold')
        ax.set_ylabel('MOS Gap', fontsize=11, fontweight='bold')
        ax.set_title('Max-Min MOS Gap\n(Lower is Better)', fontsize=12, fontweight='bold')
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels(methods)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "fairness_analysis" / "coefficient_of_variation.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def generate_all_plots(self):
        """生成所有圖表"""
        print("\n" + "="*70)
        print(f"🎨 開始生成 {self.condition.upper()} 的所有視覺化圖表")
        print("="*70 + "\n")
        
        # Resource-Satisfied Scenario (6UE)
        print("📁 Resource-Satisfied Scenario:")
        self.plot_method_comparison('6ue')
        self.plot_fairness_boxplot('6ue')
        self.plot_radar_chart('6ue')
        self.plot_ue_heatmap('6ue')
        
        print()
        
        # Resource-Overloaded Scenario (7UE)
        print("📁 Resource-Overloaded Scenario:")
        self.plot_method_comparison('7ue')
        self.plot_fairness_boxplot('7ue')
        self.plot_radar_chart('7ue')
        self.plot_ue_heatmap('7ue')
        
        print()
        
        # Cross Scenario
        print("📁 Cross Scenario Analysis:")
        self.plot_scalability_analysis()
        self.plot_performance_delta()
        
        print()
        
        # Fairness Analysis
        print("📁 Fairness Analysis:")
        self.plot_fairness_cv()
        
        print("\n" + "="*70)
        print(f"✅ {self.condition.upper()} 的所有圖表生成完成！")
        print("="*70)
        print(f"\n📂 輸出位置: {self.output_dir}")
        print("\n生成的圖表:")
        print("  resource_satisfied/")
        print("    ├── 6ue_method_comparison.png")
        print("    ├── 6ue_fairness_boxplot.png")
        print("    ├── 6ue_radar_chart.png")
        print("    └── 6ue_ue_heatmap.png")
        print("  resource_overloaded/")
        print("    ├── 7ue_method_comparison.png")
        print("    ├── 7ue_fairness_boxplot.png")
        print("    ├── 7ue_radar_chart.png")
        print("    └── 7ue_ue_heatmap.png")
        print("  cross_scenario/")
        print("    ├── scalability_lineplot.png")
        print("    └── performance_delta.png")
        print("  fairness_analysis/")
        print("    └── coefficient_of_variation.png")
        print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='分析 experiment2 的 delay/nodelay 實驗數據並生成視覺化圖表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 分析所有方法 (delay 和 nodelay)
  python3 plot_delay_nodelay_analysis.py
  
  # 只分析 delay 數據
  python3 plot_delay_nodelay_analysis.py --condition delay
  
  # 排除 ShortestPath 方法
  python3 plot_delay_nodelay_analysis.py --exclude ShortestPath
  
  # 排除多個方法
  python3 plot_delay_nodelay_analysis.py --exclude ShortestPath Random --condition nodelay
        """
    )
    
    parser.add_argument(
        '--exclude',
        nargs='+',
        choices=['Random', 'RoundRobin', 'LLM', 'ShortestPath', 'SmallestDelay'],
        default=[],
        help='要排除的方法 (可指定多個)'
    )
    
    parser.add_argument(
        '--condition',
        choices=['delay', 'nodelay', 'both'],
        default='both',
        help='要分析的條件: delay, nodelay, 或 both (預設: both)'
    )
    
    args = parser.parse_args()
    
    # 決定要處理的條件
    if args.condition == 'both':
        conditions = ['delay', 'nodelay']
    else:
        conditions = [args.condition]
    
    # 顯示排除的方法
    if args.exclude:
        print(f"\n⚠️  將排除以下方法: {', '.join(args.exclude)}\n")
    
    # 分別處理每個條件
    for condition in conditions:
        analyzer = ConditionAnalyzer(condition=condition, exclude_methods=args.exclude)
        analyzer.load_data()
        analyzer.generate_all_plots()
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
