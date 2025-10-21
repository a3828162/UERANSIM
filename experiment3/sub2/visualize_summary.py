import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 讀取CSV
df = pd.read_csv('dns_statistics_summary.csv')

print("="*70)
print("Visualizing DNS Statistics Summary")
print("="*70)

# 創建圖表
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Average Latency by Scenario
ax1 = axes[0, 0]
bars = ax1.bar(df['Scenario'], df['Avg_Latency_ms'], 
               color=['green', 'lightgreen', 'yellow', 'orange', 'red'],
               edgecolor='black', linewidth=1.5, alpha=0.8)
ax1.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax1.set_ylabel('Average Latency (ms)', fontsize=12, fontweight='bold')
ax1.set_title('Average DNS Query Latency', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# 添加數值標籤
for bar, val in zip(bars, df['Avg_Latency_ms']):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f} ms',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# 2. Latency Range (Min, Avg, Max)
ax2 = axes[0, 1]
x = np.arange(len(df))
width = 0.25

bars1 = ax2.bar(x - width, df['Min_Latency_ms'], width, label='Min', alpha=0.8)
bars2 = ax2.bar(x, df['Avg_Latency_ms'], width, label='Avg', alpha=0.8)
bars3 = ax2.bar(x + width, df['Max_Latency_ms'], width, label='Max', alpha=0.8)

ax2.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax2.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
ax2.set_title('Latency Range (Min/Avg/Max)', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(df['Scenario'])
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# 3. Latency Standard Deviation
ax3 = axes[1, 0]
bars = ax3.bar(df['Scenario'], df['Latency_StdDev_ms'],
               color='purple', edgecolor='black', linewidth=1.5, alpha=0.7)
ax3.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax3.set_ylabel('Standard Deviation (ms)', fontsize=12, fontweight='bold')
ax3.set_title('Latency Variability (StdDev)', fontsize=14, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 添加數值標籤
for bar, val in zip(bars, df['Latency_StdDev_ms']):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:.2f}',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# 4. Query Success Rate
ax4 = axes[1, 1]
completed_pct = df['Queries_Completed_Pct']
lost_pct = df['Queries_Lost_Pct']

bars = ax4.bar(df['Scenario'], completed_pct,
               color='green', edgecolor='black', linewidth=1.5, alpha=0.8,
               label='Completed')
ax4.bar(df['Scenario'], lost_pct, bottom=completed_pct,
        color='red', edgecolor='black', linewidth=1.5, alpha=0.8,
        label='Lost')

ax4.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax4.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax4.set_title('Query Success Rate', fontsize=14, fontweight='bold')
ax4.set_ylim([0, 105])
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

# 添加100%標籤
for i, scenario in enumerate(df['Scenario']):
    ax4.text(i, 102, '100%', ha='center', va='bottom', 
             fontsize=11, fontweight='bold', color='green')

plt.tight_layout()
plt.savefig('dns_statistics_summary.png', dpi=300, bbox_inches='tight')
print("✓ Saved: dns_statistics_summary.png")

# 創建詳細比較表
fig2, ax = plt.subplots(figsize=(14, 8))
ax.axis('tight')
ax.axis('off')

# 準備表格數據
table_data = []
table_data.append(['Scenario', 'UE Count', 'Queries\nLost %', 'Avg Latency\n(ms)', 
                   'Min Latency\n(ms)', 'Max Latency\n(ms)', 'StdDev\n(ms)'])

for _, row in df.iterrows():
    table_data.append([
        row['Scenario'],
        int(row['UE_Count']),
        f"{row['Queries_Lost_Pct']:.2f}%",
        f"{row['Avg_Latency_ms']:.3f}",
        f"{row['Min_Latency_ms']:.3f}",
        f"{row['Max_Latency_ms']:.3f}",
        f"{row['Latency_StdDev_ms']:.3f}"
    ])

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                 colWidths=[0.12, 0.12, 0.12, 0.16, 0.16, 0.16, 0.16])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# 設置標題行樣式
for i in range(len(table_data[0])):
    cell = table[(0, i)]
    cell.set_facecolor('#4472C4')
    cell.set_text_props(weight='bold', color='white')

# 設置數據行顏色
colors = ['#90EE90', '#ADFF2F', '#FFFF99', '#FFB366', '#FF6B6B']
for i in range(1, len(table_data)):
    for j in range(len(table_data[0])):
        cell = table[(i, j)]
        cell.set_facecolor(colors[i-1])
        if j == 0:  # Scenario column
            cell.set_text_props(weight='bold')

plt.title('DNS Statistics Summary - Detailed Comparison', 
          fontsize=16, fontweight='bold', pad=20)
plt.savefig('dns_statistics_table.png', dpi=300, bbox_inches='tight')
print("✓ Saved: dns_statistics_table.png")

# 打印詳細分析
print("\n" + "="*70)
print("PERFORMANCE ANALYSIS")
print("="*70)

baseline = df[df['Scenario'] == '10ue'].iloc[0]['Avg_Latency_ms']
print(f"\nBaseline (10ue): {baseline:.3f} ms")
print("\nPerformance Degradation:")
print("-" * 70)

for _, row in df.iterrows():
    if row['Scenario'] == '10ue':
        continue
    
    increase = row['Avg_Latency_ms'] - baseline
    increase_pct = (increase / baseline) * 100
    
    print(f"{row['Scenario']:8s}: {row['Avg_Latency_ms']:7.3f} ms "
          f"(+{increase:6.3f} ms, +{increase_pct:6.1f}%)")

print("\n" + "="*70)
print("QUALITY METRICS")
print("="*70)

for _, row in df.iterrows():
    cv = (row['Latency_StdDev_ms'] / row['Avg_Latency_ms']) * 100
    print(f"\n{row['Scenario']}:")
    print(f"  Queries Lost: {row['Queries_Lost_Pct']:.2f}%")
    print(f"  Coefficient of Variation: {cv:.2f}%")
    print(f"  Latency Range: {row['Min_Latency_ms']:.3f} - {row['Max_Latency_ms']:.3f} ms")
    
    # 評估
    if cv < 30:
        quality = "Excellent (Predictable)"
    elif cv < 50:
        quality = "Good (Stable)"
    elif cv < 100:
        quality = "Fair (Variable)"
    else:
        quality = "Poor (Highly Variable)"
    print(f"  Quality: {quality}")

print("\n" + "="*70)
print("✅ All visualizations completed!")
print("="*70)
