import csv
import statistics

# Read CSV file
data = {}
with open('latency_results.csv', 'r') as f:
    reader = csv.DictReader(f)
    for column in reader.fieldnames:
        data[column] = []
    
    for row in reader:
        for column in reader.fieldnames:
            if row[column]:
                data[column].append(float(row[column]))

# Print statistics
print("=" * 80)
print("LATENCY ANALYSIS - Statistics Summary")
print("=" * 80)

for method, values in data.items():
    print(f"\n📊 {method}")
    print("-" * 80)
    
    # Convert to milliseconds
    values_ms = [v * 1000 for v in values]
    
    mean = statistics.mean(values_ms)
    median = statistics.median(values_ms)
    stdev = statistics.stdev(values_ms)
    min_val = min(values_ms)
    max_val = max(values_ms)
    
    # Calculate percentiles
    sorted_vals = sorted(values_ms)
    n = len(sorted_vals)
    p50 = sorted_vals[int(n * 0.50)]
    p90 = sorted_vals[int(n * 0.90)]
    p95 = sorted_vals[int(n * 0.95)]
    p99 = sorted_vals[int(n * 0.99)]
    
    print(f"  Sample Size:      {len(values_ms)}")
    print(f"  Mean:             {mean:.4f} ms")
    print(f"  Median (P50):     {median:.4f} ms")
    print(f"  Std Deviation:    {stdev:.4f} ms")
    print(f"  Min:              {min_val:.4f} ms")
    print(f"  Max:              {max_val:.4f} ms")
    print(f"  Range:            {max_val - min_val:.4f} ms")
    print(f"  Coefficient of Variation: {(stdev/mean)*100:.2f}%")
    print(f"\n  Percentiles:")
    print(f"    50th (Median):  {p50:.4f} ms")
    print(f"    90th:           {p90:.4f} ms")
    print(f"    95th:           {p95:.4f} ms")
    print(f"    99th:           {p99:.4f} ms")

# Comparison table
print("\n" + "=" * 80)
print("COMPARISON TABLE (All values in milliseconds)")
print("=" * 80)
print(f"{'Metric':<20}", end="")
for method in data.keys():
    print(f"{method:<25}", end="")
print()
print("-" * 80)

metrics = ['Mean', 'Median', 'Std Dev', 'Min', 'Max', 'P90', 'P95', 'P99']

for metric in metrics:
    print(f"{metric:<20}", end="")
    for method, values in data.items():
        values_ms = [v * 1000 for v in values]
        sorted_vals = sorted(values_ms)
        n = len(sorted_vals)
        
        if metric == 'Mean':
            val = statistics.mean(values_ms)
        elif metric == 'Median':
            val = statistics.median(values_ms)
        elif metric == 'Std Dev':
            val = statistics.stdev(values_ms)
        elif metric == 'Min':
            val = min(values_ms)
        elif metric == 'Max':
            val = max(values_ms)
        elif metric == 'P90':
            val = sorted_vals[int(n * 0.90)]
        elif metric == 'P95':
            val = sorted_vals[int(n * 0.95)]
        elif metric == 'P99':
            val = sorted_vals[int(n * 0.99)]
        
        print(f"{val:<25.4f}", end="")
    print()

print("=" * 80)

# Find best performing method
print("\n🏆 BEST PERFORMING METHOD:")
print("-" * 80)
best_mean = min((statistics.mean([v * 1000 for v in values]), method) 
                for method, values in data.items())
print(f"  Lowest Mean Latency: {best_mean[1]} ({best_mean[0]:.4f} ms)")

best_median = min((statistics.median([v * 1000 for v in values]), method) 
                  for method, values in data.items())
print(f"  Lowest Median Latency: {best_median[1]} ({best_median[0]:.4f} ms)")

best_stdev = min((statistics.stdev([v * 1000 for v in values]), method) 
                 for method, values in data.items())
print(f"  Most Stable (Lowest Std Dev): {best_stdev[1]} ({best_stdev[0]:.4f} ms)")

print("\n" + "=" * 80)
