import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# 設置樣式
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 11

# 讀取數據
df = pd.read_csv('dns_statistics_summary.csv')

print("="*70)
print("Generating ALL Separate Evaluation Plots (Including Original 4)")
print("="*70)

# 創建輸出目錄
import os
if not os.path.exists('all_plots'):
    os.makedirs('all_plots')

# ===== 原始圖表 1: Average Latency (從 summary 分離) =====
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#c0392b']
bars = ax.bar(df['Scenario'], df['Avg_Latency_ms'], 
               color=colors, edgecolor='black', linewidth=1.5, alpha=0.85)
ax.set_xlabel('Scenario (Number of UEs)', fontsize=13, fontweight='bold')
ax.set_ylabel('Average Latency (ms)', fontsize=13, fontweight='bold')
ax.set_title('Average DNS Query Latency by Scenario', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, df['Avg_Latency_ms']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{val:.2f} ms',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/01_average_latency_bar.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/01_average_latency_bar.png")

# ===== 原始圖表 2: Latency Range (從 summary 分離) =====
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(df))
width = 0.25

bars1 = ax.bar(x - width, df['Min_Latency_ms'], width, 
               label='Min Latency', color='#2ecc71', alpha=0.8, edgecolor='black')
bars2 = ax.bar(x, df['Avg_Latency_ms'], width, 
               label='Avg Latency', color='#3498db', alpha=0.8, edgecolor='black')
bars3 = ax.bar(x + width, df['Max_Latency_ms'], width, 
               label='Max Latency', color='#e74c3c', alpha=0.8, edgecolor='black')

ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Latency (ms)', fontsize=13, fontweight='bold')
ax.set_title('Latency Range Comparison (Min/Avg/Max)', fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(df['Scenario'])
ax.legend(fontsize=11, loc='upper left')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('all_plots/02_latency_range_grouped.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/02_latency_range_grouped.png")

# ===== 原始圖表 3: Standard Deviation (從 summary 分離) =====
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(df['Scenario'], df['Latency_StdDev_ms'],
               color='#9b59b6', edgecolor='black', linewidth=1.5, alpha=0.85)
ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Standard Deviation (ms)', fontsize=13, fontweight='bold')
ax.set_title('Latency Variability (Standard Deviation)', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, df['Latency_StdDev_ms']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{val:.2f} ms',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/03_standard_deviation_bar.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/03_standard_deviation_bar.png")

# ===== 原始圖表 4: Success Rate (從 summary 分離) =====
fig, ax = plt.subplots(figsize=(10, 6))
completed_pct = df['Queries_Completed_Pct'].values
lost_pct = df['Queries_Lost_Pct'].values

x = np.arange(len(df))
width = 0.6

bars1 = ax.bar(x, completed_pct, width, label='Completed', 
               color='#2ecc71', edgecolor='black', alpha=0.85)
bars2 = ax.bar(x, lost_pct, width, bottom=completed_pct, 
               label='Lost', color='#e74c3c', edgecolor='black', alpha=0.85)

ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Percentage (%)', fontsize=13, fontweight='bold')
ax.set_title('Query Success Rate', fontsize=15, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(df['Scenario'])
ax.set_ylim([0, 105])
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

# 添加百分比標籤
for i, (comp, lost) in enumerate(zip(completed_pct, lost_pct)):
    ax.text(i, 50, f'{comp:.1f}%', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='white')

plt.tight_layout()
plt.savefig('all_plots/04_success_rate_stacked.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/04_success_rate_stacked.png")

# ===== 圖表 5: Coefficient of Variation (CV) =====
fig, ax = plt.subplots(figsize=(10, 6))
cv = (df['Latency_StdDev_ms'] / df['Avg_Latency_ms']) * 100
colors_cv = ['#2ecc71' if x < 50 else '#f39c12' if x < 100 else '#e74c3c' for x in cv]
bars = ax.bar(df['Scenario'], cv, color=colors_cv, edgecolor='black', linewidth=1.5, alpha=0.85)

ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Coefficient of Variation (%)', fontsize=13, fontweight='bold')
ax.set_title('Latency Consistency (Coefficient of Variation)', fontsize=15, fontweight='bold', pad=20)
ax.axhline(y=50, color='orange', linestyle='--', linewidth=2, label='Acceptable Threshold (50%)')
ax.axhline(y=100, color='red', linestyle='--', linewidth=2, label='Poor Threshold (100%)')
ax.grid(True, alpha=0.3, axis='y')
ax.legend(fontsize=10)

for bar, val in zip(bars, cv):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 3,
             f'{val:.1f}%',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/05_coefficient_variation.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/05_coefficient_variation.png")

# ===== 圖表 6: Performance Degradation =====
fig, ax = plt.subplots(figsize=(10, 6))
baseline = df[df['Scenario'] == '10ue'].iloc[0]['Avg_Latency_ms']
degradation = ((df['Avg_Latency_ms'] - baseline) / baseline) * 100
colors_deg = ['green' if x < 100 else 'orange' if x < 300 else 'red' for x in degradation]

bars = ax.bar(df['Scenario'], degradation, color=colors_deg, 
               edgecolor='black', linewidth=1.5, alpha=0.85)
ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Performance Degradation (%)', fontsize=13, fontweight='bold')
ax.set_title('Performance Degradation Relative to Baseline (10ue)', 
             fontsize=15, fontweight='bold', pad=20)
ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, degradation):
    height = bar.get_height()
    y_pos = height + 20 if height > 0 else height - 20
    ax.text(bar.get_x() + bar.get_width()/2., y_pos,
             f'+{val:.1f}%' if val > 0 else f'{val:.1f}%',
             ha='center', va='bottom' if height > 0 else 'top', 
             fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/06_performance_degradation.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/06_performance_degradation.png")

# ===== 圖表 7: Scalability Curve =====
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df['UE_Count'], df['Avg_Latency_ms'], 
        marker='o', markersize=12, linewidth=3, color='#3498db', label='Average Latency')
ax.fill_between(df['UE_Count'], 
                df['Avg_Latency_ms'] - df['Latency_StdDev_ms'],
                df['Avg_Latency_ms'] + df['Latency_StdDev_ms'],
                alpha=0.3, color='#3498db', label='±1 StdDev')

ax.set_xlabel('Number of UEs', fontsize=13, fontweight='bold')
ax.set_ylabel('Average Latency (ms)', fontsize=13, fontweight='bold')
ax.set_title('Scalability: Latency vs Number of UEs', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)

for ue, lat in zip(df['UE_Count'], df['Avg_Latency_ms']):
    ax.annotate(f'{lat:.1f}ms', xy=(ue, lat), xytext=(0, 10),
                textcoords='offset points', ha='center', fontsize=10,
                fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/07_scalability_curve.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/07_scalability_curve.png")

# ===== 圖表 8: Max Latency =====
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(df['Scenario'], df['Max_Latency_ms'],
               color='#e74c3c', edgecolor='black', linewidth=1.5, alpha=0.85)
ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Maximum Latency (ms)', fontsize=13, fontweight='bold')
ax.set_title('Worst-Case Latency by Scenario', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, df['Max_Latency_ms']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{val:.1f} ms',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/08_max_latency.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/08_max_latency.png")

# ===== 圖表 9: Min Latency =====
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(df['Scenario'], df['Min_Latency_ms'],
               color='#2ecc71', edgecolor='black', linewidth=1.5, alpha=0.85)
ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Minimum Latency (ms)', fontsize=13, fontweight='bold')
ax.set_title('Best-Case Latency by Scenario', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, df['Min_Latency_ms']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
             f'{val:.2f} ms',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/09_min_latency.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/09_min_latency.png")

# ===== 圖表 10: Latency Spread =====
fig, ax = plt.subplots(figsize=(10, 6))
latency_spread = df['Max_Latency_ms'] - df['Min_Latency_ms']
bars = ax.bar(df['Scenario'], latency_spread,
               color='#e67e22', edgecolor='black', linewidth=1.5, alpha=0.85)
ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Latency Spread (ms)', fontsize=13, fontweight='bold')
ax.set_title('Latency Range (Max - Min)', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, latency_spread):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{val:.1f} ms',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/10_latency_spread.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/10_latency_spread.png")

# ===== 圖表 11: Normalized Latency =====
fig, ax = plt.subplots(figsize=(10, 6))
baseline = df[df['Scenario'] == '10ue'].iloc[0]['Avg_Latency_ms']
normalized = df['Avg_Latency_ms'] / baseline

bars = ax.bar(df['Scenario'], normalized, color='#1abc9c', 
               edgecolor='black', linewidth=1.5, alpha=0.85)
ax.axhline(y=1, color='red', linestyle='--', linewidth=2, label='Baseline (10ue)')
ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Normalized Latency (relative to 10ue)', fontsize=13, fontweight='bold')
ax.set_title('Latency Normalized to Baseline', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')
ax.legend(fontsize=11)

for bar, val in zip(bars, normalized):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.3,
             f'{val:.2f}x',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/11_normalized_latency.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/11_normalized_latency.png")

# ===== 圖表 12: Quality Score =====
fig, ax = plt.subplots(figsize=(10, 6))
cv_values = (df['Latency_StdDev_ms'] / df['Avg_Latency_ms']) * 100
norm_lat = df['Avg_Latency_ms'] / baseline
quality_score = 100 - (norm_lat * 30) - (cv_values * 0.3)
quality_score = quality_score.clip(lower=0)

colors_quality = ['#2ecc71' if x > 70 else '#f39c12' if x > 40 else '#e74c3c' 
                  for x in quality_score]
bars = ax.bar(df['Scenario'], quality_score, color=colors_quality,
               edgecolor='black', linewidth=1.5, alpha=0.85)

ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Quality Score', fontsize=13, fontweight='bold')
ax.set_title('Overall Quality Score (Higher is Better)', fontsize=15, fontweight='bold', pad=20)
ax.set_ylim([0, 105])
ax.axhline(y=70, color='green', linestyle='--', linewidth=1.5, alpha=0.5, label='Good (>70)')
ax.axhline(y=40, color='orange', linestyle='--', linewidth=1.5, alpha=0.5, label='Fair (>40)')
ax.grid(True, alpha=0.3, axis='y')
ax.legend(fontsize=10)

for bar, val in zip(bars, quality_score):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{val:.1f}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/12_quality_score.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/12_quality_score.png")

# ===== 圖表 13: Latency per UE =====
fig, ax = plt.subplots(figsize=(10, 6))
latency_per_ue = df['Avg_Latency_ms'] / df['UE_Count']
bars = ax.bar(df['Scenario'], latency_per_ue, color='#34495e',
               edgecolor='black', linewidth=1.5, alpha=0.85)

ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Latency per UE (ms)', fontsize=13, fontweight='bold')
ax.set_title('Average Latency Contribution per UE', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, latency_per_ue):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{val:.3f}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/13_latency_per_ue.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/13_latency_per_ue.png")

# ===== 圖表 14: Queries Per Second =====
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(df['Scenario'], df['Queries_Per_Second'],
               color='#16a085', edgecolor='black', linewidth=1.5, alpha=0.85)

ax.set_xlabel('Scenario', fontsize=13, fontweight='bold')
ax.set_ylabel('Queries Per Second', fontsize=13, fontweight='bold')
ax.set_title('DNS Query Throughput', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

for bar, val in zip(bars, df['Queries_Per_Second']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 5,
             f'{val:.1f} QPS',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('all_plots/14_queries_per_second.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/14_queries_per_second.png")

# ===== 圖表 15: Radar Chart =====
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

categories = ['Low Latency\n(inverted)', 'Stability\n(low CV)', 
              'Success Rate', 'Low Max Latency\n(inverted)', 'Predictability']
N = len(categories)

scores_data = []
for _, row in df.iterrows():
    lat_score = max(0, 100 - (row['Avg_Latency_ms'] / baseline) * 50)
    cv_val = (row['Latency_StdDev_ms'] / row['Avg_Latency_ms']) * 100
    stab_score = max(0, 100 - cv_val)
    success_score = row['Queries_Completed_Pct']
    max_lat_score = max(0, 100 - (row['Max_Latency_ms'] / 200) * 100)
    predict_score = max(0, 100 - (row['Latency_StdDev_ms'] / 50) * 100)
    
    scores_data.append([lat_score, stab_score, success_score, max_lat_score, predict_score])

angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

colors_radar = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#c0392b']
for idx, (scenario, scores) in enumerate(zip(df['Scenario'], scores_data)):
    scores += scores[:1]
    ax.plot(angles, scores, 'o-', linewidth=2, label=scenario, color=colors_radar[idx])
    ax.fill(angles, scores, alpha=0.15, color=colors_radar[idx])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, size=11)
ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20', '40', '60', '80', '100'], size=9)
ax.grid(True)
ax.set_title('Multi-Dimensional Performance Evaluation', 
             fontsize=15, fontweight='bold', pad=30)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

plt.tight_layout()
plt.savefig('all_plots/15_radar_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/15_radar_chart.png")

# ===== 圖表 16: Comparison Table (as image) =====
fig, ax = plt.subplots(figsize=(14, 6))
ax.axis('tight')
ax.axis('off')

table_data = []
table_data.append(['Scenario', 'Avg (ms)', 'Min (ms)', 'Max (ms)', 
                   'StdDev (ms)', 'CV (%)', 'Lost (%)', 'QPS'])

for _, row in df.iterrows():
    cv_val = (row['Latency_StdDev_ms'] / row['Avg_Latency_ms']) * 100
    table_data.append([
        row['Scenario'],
        f"{row['Avg_Latency_ms']:.2f}",
        f"{row['Min_Latency_ms']:.2f}",
        f"{row['Max_Latency_ms']:.2f}",
        f"{row['Latency_StdDev_ms']:.2f}",
        f"{cv_val:.1f}",
        f"{row['Queries_Lost_Pct']:.2f}",
        f"{row['Queries_Per_Second']:.1f}"
    ])

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                 colWidths=[0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12])
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# 設置標題行樣式
for i in range(8):
    cell = table[(0, i)]
    cell.set_facecolor('#3498db')
    cell.set_text_props(weight='bold', color='white')

# 設置數據行顏色
colors_table = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#c0392b']
for i in range(1, 6):
    for j in range(8):
        cell = table[(i, j)]
        cell.set_facecolor(colors_table[i-1])
        cell.set_alpha(0.2)

plt.title('DNS Performance Statistics Summary', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('all_plots/16_summary_table.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: all_plots/16_summary_table.png")

print("\n" + "="*70)
print("✅ All 16 separate plots generated successfully!")
print("="*70)
print(f"\nPlots saved in: {os.path.abspath('all_plots')}/")
print("\nPlots 1-4: Original summary plots (now separated)")
print("Plots 5-16: Additional evaluation plots")
