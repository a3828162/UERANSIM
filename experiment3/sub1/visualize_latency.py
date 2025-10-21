import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

# Read the CSV file
df = pd.read_csv('latency_results.csv')

# Create a figure with multiple subplots
fig = plt.figure(figsize=(16, 12))

# 1. Time Series Plot
ax1 = plt.subplot(3, 2, 1)
for column in df.columns:
    plt.plot(range(1, len(df) + 1), df[column] * 1000, label=column, alpha=0.7, linewidth=1.5)
plt.xlabel('Measurement Number', fontsize=12)
plt.ylabel('Latency (ms)', fontsize=12)
plt.title('Latency Over Time for Each Method', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 2. Box Plot
ax2 = plt.subplot(3, 2, 2)
df_ms = df * 1000  # Convert to milliseconds
df_ms.boxplot(ax=ax2)
plt.ylabel('Latency (ms)', fontsize=12)
plt.title('Latency Distribution Comparison', fontsize=14, fontweight='bold')
plt.xticks(rotation=15, ha='right')
plt.grid(True, alpha=0.3)

# 3. Violin Plot
ax3 = plt.subplot(3, 2, 3)
df_melted = pd.melt(df_ms, var_name='Method', value_name='Latency')
sns.violinplot(data=df_melted, x='Method', y='Latency', ax=ax3)
plt.ylabel('Latency (ms)', fontsize=12)
plt.title('Latency Distribution (Violin Plot)', fontsize=14, fontweight='bold')
plt.xticks(rotation=15, ha='right')

# 4. Histogram with KDE
ax4 = plt.subplot(3, 2, 4)
for column in df.columns:
    df_ms[column].plot(kind='hist', alpha=0.5, bins=20, label=column, ax=ax4, density=True)
    df_ms[column].plot(kind='kde', ax=ax4, linewidth=2)
plt.xlabel('Latency (ms)', fontsize=12)
plt.ylabel('Density', fontsize=12)
plt.title('Latency Distribution with KDE', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 5. CDF (Cumulative Distribution Function)
ax5 = plt.subplot(3, 2, 5)
for column in df.columns:
    sorted_data = np.sort(df_ms[column])
    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    plt.plot(sorted_data, cdf * 100, label=column, linewidth=2)
plt.xlabel('Latency (ms)', fontsize=12)
plt.ylabel('Cumulative Probability (%)', fontsize=12)
plt.title('Cumulative Distribution Function (CDF)', fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)

# 6. Statistical Summary (as text)
ax6 = plt.subplot(3, 2, 6)
ax6.axis('off')

# Calculate statistics
stats_text = "Statistical Summary (in ms)\n" + "="*50 + "\n\n"
for column in df.columns:
    stats_text += f"{column}:\n"
    stats_text += f"  Mean:        {df_ms[column].mean():.4f} ms\n"
    stats_text += f"  Median:      {df_ms[column].median():.4f} ms\n"
    stats_text += f"  Std Dev:     {df_ms[column].std():.4f} ms\n"
    stats_text += f"  Min:         {df_ms[column].min():.4f} ms\n"
    stats_text += f"  Max:         {df_ms[column].max():.4f} ms\n"
    stats_text += f"  95th %ile:   {df_ms[column].quantile(0.95):.4f} ms\n"
    stats_text += f"  99th %ile:   {df_ms[column].quantile(0.99):.4f} ms\n"
    stats_text += "\n"

ax6.text(0.1, 0.9, stats_text, fontsize=10, family='monospace', 
         verticalalignment='top', transform=ax6.transAxes)

plt.tight_layout()
plt.savefig('latency_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: latency_analysis.png")

# Create a separate detailed comparison figure
fig2, axes = plt.subplots(2, 2, figsize=(14, 10))

# Moving average plot
ax1 = axes[0, 0]
window_size = 5
for column in df.columns:
    moving_avg = df_ms[column].rolling(window=window_size).mean()
    ax1.plot(range(1, len(df) + 1), moving_avg, label=column, linewidth=2)
ax1.set_xlabel('Measurement Number', fontsize=11)
ax1.set_ylabel('Latency (ms)', fontsize=11)
ax1.set_title(f'Moving Average (window={window_size})', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Scatter plot with trend
ax2 = axes[0, 1]
colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown']  # Added more colors
for idx, column in enumerate(df.columns):
    ax2.scatter(range(1, len(df) + 1), df_ms[column], alpha=0.5, label=column, 
                color=colors[idx % len(colors)], s=30)
    # Add trend line
    z = np.polyfit(range(1, len(df) + 1), df_ms[column], 1)
    p = np.poly1d(z)
    ax2.plot(range(1, len(df) + 1), p(range(1, len(df) + 1)), 
             linestyle='--', color=colors[idx % len(colors)], alpha=0.7, linewidth=2)
ax2.set_xlabel('Measurement Number', fontsize=11)
ax2.set_ylabel('Latency (ms)', fontsize=11)
ax2.set_title('Scatter Plot with Trend Lines', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Bar chart of statistics
ax3 = axes[1, 0]
stats_df = pd.DataFrame({
    'Mean': [df_ms[col].mean() for col in df.columns],
    'Median': [df_ms[col].median() for col in df.columns],
    '95th %ile': [df_ms[col].quantile(0.95) for col in df.columns]
}, index=df.columns)
stats_df.plot(kind='bar', ax=ax3)
ax3.set_ylabel('Latency (ms)', fontsize=11)
ax3.set_title('Statistical Comparison', fontsize=12, fontweight='bold')
ax3.set_xticklabels(df.columns, rotation=15, ha='right')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y')

# Heatmap of correlation
ax4 = axes[1, 1]
correlation = df.corr()
sns.heatmap(correlation, annot=True, fmt='.3f', cmap='coolwarm', 
            center=0, ax=ax4, cbar_kws={'label': 'Correlation'})
ax4.set_title('Correlation Matrix', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('latency_detailed_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: latency_detailed_analysis.png")

# Print summary statistics to console
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
print("\n✓ All visualizations completed!")

# plt.show()  # Commented out for non-interactive execution
