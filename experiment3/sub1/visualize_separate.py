import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
sns.set_style("whitegrid")

# Read the CSV file
df = pd.read_csv('latency_results.csv')
df_ms = df * 1000  # Convert to milliseconds

print("Generating individual plots...")
print("="*70)

# 1. Time Series Plot
fig, ax = plt.subplots(figsize=(12, 6))
for column in df.columns:
    ax.plot(range(1, len(df) + 1), df_ms[column], label=column, alpha=0.7, linewidth=2)
ax.set_xlabel('Measurement Number', fontsize=12)
ax.set_ylabel('Latency (ms)', fontsize=12)
ax.set_title('Latency Over Time for Each Method', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('1_time_series.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 1_time_series.png")

# 2. Box Plot
fig, ax = plt.subplots(figsize=(10, 6))
df_ms.boxplot(ax=ax)
ax.set_ylabel('Latency (ms)', fontsize=12)
ax.set_title('Latency Distribution Comparison (Box Plot)', fontsize=14, fontweight='bold')
ax.set_xticklabels(df.columns, rotation=15, ha='right')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('2_box_plot.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 2_box_plot.png")

# 3. Violin Plot
fig, ax = plt.subplots(figsize=(10, 6))
df_melted = pd.melt(df_ms, var_name='Method', value_name='Latency')
sns.violinplot(data=df_melted, x='Method', y='Latency', ax=ax)
ax.set_ylabel('Latency (ms)', fontsize=12)
ax.set_title('Latency Distribution (Violin Plot)', fontsize=14, fontweight='bold')
ax.set_xticklabels(df.columns, rotation=15, ha='right')
plt.tight_layout()
plt.savefig('3_violin_plot.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 3_violin_plot.png")

# 4. Histogram with KDE
fig, ax = plt.subplots(figsize=(12, 6))
for column in df.columns:
    df_ms[column].plot(kind='hist', alpha=0.5, bins=20, label=column, ax=ax, density=True)
    df_ms[column].plot(kind='kde', ax=ax, linewidth=2)
ax.set_xlabel('Latency (ms)', fontsize=12)
ax.set_ylabel('Density', fontsize=12)
ax.set_title('Latency Distribution with KDE', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('4_histogram_kde.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 4_histogram_kde.png")

# 5. CDF (Cumulative Distribution Function)
fig, ax = plt.subplots(figsize=(12, 6))
for column in df.columns:
    sorted_data = np.sort(df_ms[column])
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    ax.plot(sorted_data, cdf * 100, label=column, linewidth=2.5)
ax.set_xlabel('Latency (ms)', fontsize=12)
ax.set_ylabel('Cumulative Probability (%)', fontsize=12)
ax.set_title('Cumulative Distribution Function (CDF)', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('5_cdf.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 5_cdf.png")

# 6. Moving Average
fig, ax = plt.subplots(figsize=(12, 6))
window_size = 5
for column in df.columns:
    moving_avg = df_ms[column].rolling(window=window_size).mean()
    ax.plot(range(1, len(df) + 1), moving_avg, label=column, linewidth=2.5)
ax.set_xlabel('Measurement Number', fontsize=12)
ax.set_ylabel('Latency (ms)', fontsize=12)
ax.set_title(f'Moving Average (window={window_size})', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('6_moving_average.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 6_moving_average.png")

# 7. Scatter plot with trend lines
fig, ax = plt.subplots(figsize=(12, 6))
colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']
for idx, column in enumerate(df.columns):
    ax.scatter(range(1, len(df) + 1), df_ms[column], alpha=0.5, label=column, 
                color=colors[idx % len(colors)], s=40)
    # Add trend line
    z = np.polyfit(range(1, len(df) + 1), df_ms[column], 1)
    p = np.poly1d(z)
    ax.plot(range(1, len(df) + 1), p(range(1, len(df) + 1)), 
             linestyle='--', color=colors[idx % len(colors)], alpha=0.7, linewidth=2)
ax.set_xlabel('Measurement Number', fontsize=12)
ax.set_ylabel('Latency (ms)', fontsize=12)
ax.set_title('Scatter Plot with Trend Lines', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('7_scatter_trend.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 7_scatter_trend.png")

# 8. Bar chart of statistics
fig, ax = plt.subplots(figsize=(12, 6))
stats_df = pd.DataFrame({
    'Mean': [df_ms[col].mean() for col in df.columns],
    'Median': [df_ms[col].median() for col in df.columns],
    '95th %ile': [df_ms[col].quantile(0.95) for col in df.columns]
}, index=df.columns)
stats_df.plot(kind='bar', ax=ax, width=0.8)
ax.set_ylabel('Latency (ms)', fontsize=12)
ax.set_title('Statistical Comparison', fontsize=14, fontweight='bold')
ax.set_xticklabels(df.columns, rotation=15, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('8_statistics_bar.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 8_statistics_bar.png")

# 9. Correlation Heatmap
fig, ax = plt.subplots(figsize=(8, 6))
correlation = df.corr()
sns.heatmap(correlation, annot=True, fmt='.3f', cmap='coolwarm', 
            center=0, ax=ax, cbar_kws={'label': 'Correlation'}, 
            square=True, linewidths=1)
ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('9_correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 9_correlation_heatmap.png")

# 10. Mean with error bars
fig, ax = plt.subplots(figsize=(10, 6))
means = [df_ms[col].mean() for col in df.columns]
stds = [df_ms[col].std() for col in df.columns]
x_pos = np.arange(len(means))
bars = ax.bar(x_pos, means, yerr=stds, capsize=10, alpha=0.7, 
              color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
ax.set_xticks(x_pos)
ax.set_xticklabels(df.columns, rotation=15, ha='right')
ax.set_ylabel('Latency (ms)', fontsize=12)
ax.set_title('Mean Latency ± Standard Deviation', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for i, (mean, std) in enumerate(zip(means, stds)):
    ax.text(i, mean + std + 0.1, f'{mean:.3f}±{std:.3f}', 
             ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('10_mean_error_bars.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 10_mean_error_bars.png")

# 11. Histogram overlay
fig, ax = plt.subplots(figsize=(12, 6))
for column in df.columns:
    ax.hist(df_ms[column], bins=20, alpha=0.6, label=column, edgecolor='black')
ax.set_xlabel('Latency (ms)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Latency Distribution Histogram', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('11_histogram_overlay.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: 11_histogram_overlay.png")

# Print summary statistics
print("\n" + "="*70)
print("LATENCY ANALYSIS SUMMARY")
print("="*70)
print(f"\nTotal measurements per method: {len(df)}")
print("\nStatistics (in milliseconds):")
print("-" * 70)

summary_df = pd.DataFrame({
    'Mean (ms)': [df_ms[col].mean() for col in df.columns],
    'Median (ms)': [df_ms[col].median() for col in df.columns],
    'Std Dev (ms)': [df_ms[col].std() for col in df.columns],
    'Min (ms)': [df_ms[col].min() for col in df.columns],
    'Max (ms)': [df_ms[col].max() for col in df.columns],
    '95th %ile (ms)': [df_ms[col].quantile(0.95) for col in df.columns],
    '99th %ile (ms)': [df_ms[col].quantile(0.99) for col in df.columns]
}, index=df.columns)

print(summary_df.to_string())
print("\n" + "="*70)

# Determine the best method
best_method_mean = summary_df['Mean (ms)'].idxmin()
best_method_median = summary_df['Median (ms)'].idxmin()
best_method_std = summary_df['Std Dev (ms)'].idxmin()

print(f"\n🏆 Best Method (Lowest Mean Latency): {best_method_mean}")
print(f"   Mean: {summary_df.loc[best_method_mean, 'Mean (ms)']:.4f} ms")
print(f"\n🏆 Best Method (Lowest Median Latency): {best_method_median}")
print(f"   Median: {summary_df.loc[best_method_median, 'Median (ms)']:.4f} ms")
print(f"\n🏆 Most Stable Method (Lowest Std Dev): {best_method_std}")
print(f"   Std Dev: {summary_df.loc[best_method_std, 'Std Dev (ms)']:.4f} ms")
print("\n" + "="*70)
print("\n✅ All 11 individual visualizations completed!")
