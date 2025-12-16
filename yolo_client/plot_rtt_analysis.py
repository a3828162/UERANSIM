#!/usr/bin/env python3
"""
RTT 分析腳本 - 分析 delay 和 nodelay 場景
比較不同調度方法 (Random, RoundRobin, LLM, ShortestPath, LowestDelay) 的 RTT 表現
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

class RTTAnalyzer:
    def __init__(self, base_dir="/home/ubuntu/UERANSIM/yolo_client", condition="nodelay", exclude_methods=None):
        self.base_dir = Path(base_dir)
        self.condition = condition  # 'delay' or 'nodelay'
        self.condition_dir = self.base_dir / condition
        self.exclude_methods = exclude_methods or []  # 要排除的方法列表
        
        # 創建輸出資料夾
        self.output_dir = self.base_dir / "plots_rtt" / condition
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 儲存兩種場景的資料
        self.data_satisfy = {}    # Resource-Satisfied
        self.data_overload = {}   # Resource-Overloaded
        
    def load_data(self):
        """載入指定 condition 的所有 CSV 資料"""
        print(f"📂 載入 {self.condition.upper()} 資料...")
        
        if not self.condition_dir.exists():
            print(f"  ❌ 錯誤: {self.condition_dir} 不存在")
            return
        
        # 資料夾結構: delay/resource_satisfy/ 和 delay/resource_overload/
        satisfy_dir = self.condition_dir / "resource_satisfy"
        overload_dir = self.condition_dir / "resource_overload"
        
        # 載入 Resource-Satisfied 資料
        if satisfy_dir.exists():
            for method_dir in satisfy_dir.iterdir():
                if method_dir.is_dir():
                    csv_file = method_dir / "ue_statistics_summary.csv"
                    if csv_file.exists():
                        method = self._extract_method_name(method_dir.name)
                        if method is None:
                            continue
                        
                        # 檢查是否要排除此方法
                        if method in self.exclude_methods:
                            print(f"  ⊝ Resource-Satisfied - {method}: 已排除")
                            continue
                        
                        df = pd.read_csv(csv_file)
                        self.data_satisfy[method] = df
                        print(f"  ✓ Resource-Satisfied - {method}: {len(df)} rows")
        
        # 載入 Resource-Overloaded 資料
        if overload_dir.exists():
            for method_dir in overload_dir.iterdir():
                if method_dir.is_dir():
                    csv_file = method_dir / "ue_statistics_summary.csv"
                    if csv_file.exists():
                        method = self._extract_method_name(method_dir.name)
                        if method is None:
                            continue
                        
                        # 檢查是否要排除此方法
                        if method in self.exclude_methods:
                            print(f"  ⊝ Resource-Overloaded - {method}: 已排除")
                            continue
                        
                        df = pd.read_csv(csv_file)
                        self.data_overload[method] = df
                        print(f"  ✓ Resource-Overloaded - {method}: {len(df)} rows")
        
        print(f"\n✅ 載入完成:")
        print(f"   Resource-Satisfied: {len(self.data_satisfy)} 種方法")
        print(f"   Resource-Overloaded: {len(self.data_overload)} 種方法\n")
    
    def _extract_method_name(self, dirname):
        """從資料夾名稱提取方法名稱"""
        dirname_lower = dirname.lower()
        
        # 精確匹配縮寫（避免誤判）
        if dirname_lower.startswith('ld_') or dirname_lower.startswith('lowestdelay') or dirname_lower.startswith('smallestdelay'):
            return 'SmallestDelay'
        elif dirname_lower.startswith('llm_') or 'llm' in dirname_lower:
            return 'LLM'
        elif dirname_lower.startswith('rd_') or dirname_lower.startswith('random'):
            return 'Random'
        elif dirname_lower.startswith('rr_') or 'roundrobin' in dirname_lower:
            return 'RoundRobin'
        elif dirname_lower.startswith('sp_') or 'shortestpath' in dirname_lower:
            return 'ShortestPath'
        else:
            return None
    
    def plot_rtt_comparison(self):
        """RTT 方法比較 - 柱狀圖 (分開繪製兩個scenario)"""
        print(f"📊 繪製 RTT 方法比較圖...")
        
        for data, scenario, filename in [
            (self.data_satisfy, 'Resource-Satisfied', 'rtt_comparison_satisfy.png'),
            (self.data_overload, 'Resource-Overloaded', 'rtt_comparison_overload.png')
        ]:
            if not data:
                print(f"  ⊝ {scenario}: 無資料，跳過")
                continue
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            methods = sorted(data.keys())
            rtt_values = []
            
            for method in methods:
                df = data[method]
                overall_row = df[df['UE_ID'] == 'OVERALL'].iloc[0]
                rtt_values.append(overall_row['Avg_RTT_ms'])
            
            x = np.arange(len(methods))
            bars = ax.bar(x, rtt_values, color=[METHOD_COLORS.get(m, '#999') for m in methods], alpha=0.8, width=0.6)
            
            # 數值標籤
            for bar, val in zip(bars, rtt_values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.2f} ms',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_xlabel('Method', fontsize=11, fontweight='bold')
            ax.set_ylabel('Average RTT (ms)', fontsize=11, fontweight='bold')
            ax.set_title(f'{self.condition.upper()} - {scenario}\nAverage RTT Comparison', 
                        fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(methods, fontsize=10)
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            output_file = self.output_dir / filename
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"  ✓ {scenario}: {output_file}")
            plt.close()
    
    def plot_rtt_boxplot(self):
        """RTT 分布 - 箱型圖 (分開繪製兩個scenario)"""
        print(f"📊 繪製 RTT 分布箱型圖...")
        
        for data, scenario, filename in [
            (self.data_satisfy, 'Resource-Satisfied', 'rtt_boxplot_satisfy.png'),
            (self.data_overload, 'Resource-Overloaded', 'rtt_boxplot_overload.png')
        ]:
            if not data:
                print(f"  ⊝ {scenario}: 無資料，跳過")
                continue
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 準備資料 (排除 OVERALL)
            plot_data = []
            for method, df in data.items():
                ue_data = df[df['UE_ID'] != 'OVERALL']
                for _, row in ue_data.iterrows():
                    plot_data.append({
                        'Method': method,
                        'RTT': row['Avg_RTT_ms']
                    })
            
            df_plot = pd.DataFrame(plot_data)
            methods = sorted(data.keys())
            
            # 箱型圖
            bp = ax.boxplot([df_plot[df_plot['Method'] == m]['RTT'].values 
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
                method_data = df_plot[df_plot['Method'] == method]['RTT'].values
                x = np.random.normal(i, 0.04, size=len(method_data))
                ax.scatter(x, method_data, alpha=0.5, s=50, color=METHOD_COLORS.get(method, '#999'))
            
            ax.set_ylabel('RTT (ms)', fontsize=11, fontweight='bold')
            ax.set_title(f'{self.condition.upper()} - {scenario}\nRTT Distribution', 
                        fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            output_file = self.output_dir / filename
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"  ✓ {scenario}: {output_file}")
            plt.close()
    
    def plot_rtt_heatmap(self):
        """個別 UE 的 RTT - 熱力圖 (分開繪製兩個scenario)"""
        print(f"📊 繪製 RTT 熱力圖...")
        
        for data, scenario, filename in [
            (self.data_satisfy, 'Resource-Satisfied', 'rtt_heatmap_satisfy.png'),
            (self.data_overload, 'Resource-Overloaded', 'rtt_heatmap_overload.png')
        ]:
            if not data:
                print(f"  ⊝ {scenario}: 無資料，跳過")
                continue
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            methods = sorted(data.keys())
            
            # 找出最大 UE 數量
            max_ue_count = 0
            for method, df in data.items():
                ue_count = len(df[df['UE_ID'] != 'OVERALL'])
                max_ue_count = max(max_ue_count, ue_count)
            
            ue_ids = [f'UE{i}' for i in range(1, max_ue_count + 1)]
            
            # 準備資料矩陣
            rtt_matrix = []
            for method in methods:
                df = data[method]
                ue_rtt = []
                for ue_id in ue_ids:
                    rtt = df[df['UE_ID'] == ue_id]['Avg_RTT_ms'].values
                    ue_rtt.append(rtt[0] if len(rtt) > 0 else np.nan)
                rtt_matrix.append(ue_rtt)
            
            rtt_matrix = np.array(rtt_matrix)
            
            # 繪製熱力圖
            im = ax.imshow(rtt_matrix, cmap='RdYlGn_r', aspect='auto')
            
            # 設定標籤
            ax.set_xticks(np.arange(len(ue_ids)))
            ax.set_yticks(np.arange(len(methods)))
            ax.set_xticklabels(ue_ids)
            ax.set_yticklabels(methods)
            
            # 顯示數值
            for i in range(len(methods)):
                for j in range(len(ue_ids)):
                    if not np.isnan(rtt_matrix[i, j]):
                        text = ax.text(j, i, f'{rtt_matrix[i, j]:.1f}',
                                     ha="center", va="center", color="black", 
                                     fontsize=9, fontweight='bold')
            
            ax.set_title(f'{self.condition.upper()} - {scenario}\nRTT Heatmap by UE', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('UE ID', fontsize=11, fontweight='bold')
            ax.set_ylabel('Method', fontsize=11, fontweight='bold')
            
            # 顏色條
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('RTT (ms)', rotation=270, labelpad=20, fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            output_file = self.output_dir / filename
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"  ✓ {scenario}: {output_file}")
            plt.close()
    
    def plot_rtt_scalability(self):
        """RTT 擴展性分析 - 折線圖 (比較兩個scenario)"""
        print(f"📊 繪製 RTT 擴展性分析...")
        
        scenarios = ['Resource-Satisfied', 'Resource-Overloaded']
        methods = sorted(set(list(self.data_satisfy.keys()) + list(self.data_overload.keys())))
        
        if not methods:
            print("  ⚠️  沒有資料可繪製")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for method in methods:
            values = []
            for data in [self.data_satisfy, self.data_overload]:
                if method in data:
                    overall = data[method][data[method]['UE_ID'] == 'OVERALL'].iloc[0]
                    values.append(overall['Avg_RTT_ms'])
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
        
        ax.set_xlabel('Scenario', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average RTT (ms)', fontsize=12, fontweight='bold')
        ax.set_title(f'{self.condition.upper()} - RTT Performance Across Scenarios', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "rtt_scalability.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def plot_rtt_delta(self):
        """RTT 變化分析 - 柱狀圖 (Overloaded - Satisfied)"""
        print(f"📊 繪製 RTT 變化分析...")
        
        methods = sorted(set(list(self.data_satisfy.keys()) + list(self.data_overload.keys())))
        
        if not methods:
            print("  ⚠️  沒有資料可繪製")
            return
        
        # 計算差異
        deltas = {}
        
        for method in methods:
            if method in self.data_satisfy and method in self.data_overload:
                overall_satisfy = self.data_satisfy[method][self.data_satisfy[method]['UE_ID'] == 'OVERALL'].iloc[0]
                overall_overload = self.data_overload[method][self.data_overload[method]['UE_ID'] == 'OVERALL'].iloc[0]
                
                deltas[method] = overall_overload['Avg_RTT_ms'] - overall_satisfy['Avg_RTT_ms']
        
        if not deltas:
            print("  ⚠️  沒有足夠資料可比較")
            return
        
        # 繪製
        fig, ax = plt.subplots(figsize=(10, 6))
        
        methods_with_data = list(deltas.keys())
        values = list(deltas.values())
        x = np.arange(len(methods_with_data))
        
        bars = ax.bar(x, values, color=[METHOD_COLORS.get(m, '#999') for m in methods_with_data], alpha=0.7)
        
        # 數值標籤
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:+.2f} ms',
                   ha='center', va='bottom' if val > 0 else 'top', 
                   fontsize=10, fontweight='bold')
        
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(methods_with_data)
        ax.set_ylabel('Δ RTT (ms)', fontsize=12, fontweight='bold')
        ax.set_title(f'{self.condition.upper()} - RTT Change: Overloaded - Satisfied (Δ)', 
                    fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "rtt_delta.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ 儲存至: {output_file}")
        plt.close()
    
    def generate_all_plots(self):
        """生成所有 RTT 圖表"""
        print("\n" + "="*70)
        print(f"🎨 開始生成 {self.condition.upper()} 的 RTT 視覺化圖表")
        print("="*70 + "\n")
        
        self.plot_rtt_comparison()
        self.plot_rtt_boxplot()
        self.plot_rtt_heatmap()
        self.plot_rtt_scalability()
        self.plot_rtt_delta()
        
        print("\n" + "="*70)
        print(f"✅ {self.condition.upper()} 的所有 RTT 圖表生成完成！")
        print("="*70)
        print(f"\n📂 輸出位置: {self.output_dir}")
        print("\n生成的圖表:")
        print("  Resource-Satisfied:")
        print("    ├── rtt_comparison_satisfy.png")
        print("    ├── rtt_boxplot_satisfy.png")
        print("    └── rtt_heatmap_satisfy.png")
        print("  Resource-Overloaded:")
        print("    ├── rtt_comparison_overload.png")
        print("    ├── rtt_boxplot_overload.png")
        print("    └── rtt_heatmap_overload.png")
        print("  Cross-Scenario:")
        print("    ├── rtt_scalability.png")
        print("    └── rtt_delta.png")
        print()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='RTT 分析工具 - 分析 delay 和 nodelay 場景的 RTT 表現',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  # 分析所有方法
  python3 plot_rtt_analysis.py
  
  # 排除 ShortestPath 方法
  python3 plot_rtt_analysis.py --exclude ShortestPath
  
  # 排除多個方法
  python3 plot_rtt_analysis.py --exclude ShortestPath Random
  
  # 只分析 delay 場景
  python3 plot_rtt_analysis.py --condition delay --exclude ShortestPath
        '''
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
        nargs='+',
        choices=['delay', 'nodelay'],
        default=['delay', 'nodelay'],
        help='要分析的場景 (預設: delay 和 nodelay)'
    )
    
    args = parser.parse_args()
    
    # 顯示排除的方法
    if args.exclude:
        print("\n" + "="*70)
        print(f"⚠️  已排除的方法: {', '.join(args.exclude)}")
        print("="*70 + "\n")
    
    # 分別處理指定的 condition
    for condition in args.condition:
        analyzer = RTTAnalyzer(condition=condition, exclude_methods=args.exclude)
        analyzer.load_data()
        
        if analyzer.data_satisfy or analyzer.data_overload:
            analyzer.generate_all_plots()
        else:
            print(f"⚠️  {condition.upper()} 沒有資料可分析\n")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
