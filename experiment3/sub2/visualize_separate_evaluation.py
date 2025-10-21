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
print("Generating Individual Evaluation Plots")
print("="*70)

# 創建輸出目錄
import os
if not os.path.exists('evaluation_plots'):
    os.makedirs('evaluation_plots')

# ===== 圖表 1: Average Latency Bar Chart =====
fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#c0392b']
bars = ax.bar(df['Scenario'], df['Avg_Latency_ms'], 
               color=colors, edgecolor='black', linewidth=1.5, alpha=0.85)
ax.set_xlabel('Scenario (Number of UEs)', fontsize=13, fontweight='bold')
ax.set_ylabel('Average Latency (ms)', fontsize=13, fontweight='bold')
ax.set_title('Average DNS Query Latency by Scenario', fontsize=15, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

# 添加數值標籤
for bar, val in zip(bars, df['Avg_Latency_ms']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{val:.2f} ms',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('evaluation_plots/1_average_latency.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/1_average_latency.png")

# ===== 圖表 2: Latency Range (Min/Avg/Max) =====
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
plt.savefig('evaluation_plots/2_latency_range.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/2_latency_range.png")

# ===== 圖表 3: Standard Deviation =====
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
plt.savefig('evaluation_plots/3_standard_deviation.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/3_standard_deviation.png")

# ===== 圖表 4: Coefficient of Variation (CV) =====
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
plt.savefig('evaluation_plots/4_coefficient_variation.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/4_coefficient_variation.png")

# ===== 圖表 5: Performance Degradation (相對於baseline) =====
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
plt.savefig('evaluation_plots/5_performance_degradation.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/5_performance_degradation.png")

# ===== 圖表 6: Scalability Curve (Line Plot) =====
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

# 標註數值
for ue, lat in zip(df['UE_Count'], df['Avg_Latency_ms']):
    ax.annotate(f'{lat:.1f}ms', xy=(ue, lat), xytext=(0, 10),
                textcoords='offset points', ha='center', fontsize=10,
                fontweight='bold')

plt.tight_layout()
plt.savefig('evaluation_plots/6_scalability_curve.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/6_scalability_curve.png")

# ===== 圖表 7: Max Latency Comparison =====
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
plt.savefig('evaluation_plots/7_max_latency.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/7_max_latency.png")

# ===== 圖表 8: Latency Spread (Max - Min) =====
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
plt.savefig('evaluation_plots/8_latency_spread.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/8_latency_spread.png")

# ===== 圖表 9: Normalized Latency (相對於10ue) =====
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
plt.savefig('evaluation_plots/9_normalized_latency.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/9_normalized_latency.png")

# ===== 圖表 10: Quality Score (綜合評分) =====
fig, ax = plt.subplots(figsize=(10, 6))
# 計算質量分數：考慮延遲和穩定性
# Score = 100 - (normalized_latency * 40) - (CV * 0.4)
cv_values = (df['Latency_StdDev_ms'] / df['Avg_Latency_ms']) * 100
norm_lat = df['Avg_Latency_ms'] / baseline
quality_score = 100 - (norm_lat * 30) - (cv_values * 0.3)
quality_score = quality_score.clip(lower=0)  # 不低於0

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
plt.savefig('evaluation_plots/10_quality_score.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/10_quality_score.png")

# ===== 圖表 11: Latency per UE (平均每個UE的延遲貢獻) =====
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
plt.savefig('evaluation_plots/11_latency_per_ue.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/11_latency_per_ue.png")

# ===== 圖表 12: Radar Chart (多維評估) =====
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

# 準備數據：5個維度
categories = ['Low Latency\n(inverted)', 'Stability\n(low CV)', 
              'Success Rate', 'Low Max Latency\n(inverted)', 'Predictability']
N = len(categories)

# 計算每個scenario的分數 (0-100)
scores_data = []
for _, row in df.iterrows():
    # 1. Low Latency (反轉，越低越好)
    lat_score = max(0, 100 - (row['Avg_Latency_ms'] / baseline) * 50)
    
    # 2. Stability (CV越低越好)
    cv_val = (row['Latency_StdDev_ms'] / row['Avg_Latency_ms']) * 100
    stab_score = max(0, 100 - cv_val)
    
    # 3. Success Rate
    success_score = row['Queries_Completed_Pct']
    
    # 4. Low Max Latency (反轉)
    max_lat_score = max(0, 100 - (row['Max_Latency_ms'] / 200) * 100)
    
    # 5. Predictability (基於標準差)
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
plt.savefig('evaluation_plots/12_radar_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: evaluation_plots/12_radar_chart.png")

print("\n" + "="*70)
print("✅ All 12 evaluation plots generated successfully!")
print("="*70)
print(f"\nPlots saved in: {os.path.abspath('evaluation_plots')}/")
