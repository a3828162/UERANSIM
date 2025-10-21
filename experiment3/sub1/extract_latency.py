import re
import csv

# File names
files = [
    'withoutEASDF.txt',
    'withEASDFFORWARD.txt',
    'withEASDFBUFFERFIRST.txt',
    'withEASDFBUFFERALL.txt'
]

# Extract latency values from each file
all_latencies = {}

for file in files:
    latencies = []
    with open(file, 'r') as f:
        content = f.read()
        # Find all "Average Latency (s): X.XXXXXX" patterns
        matches = re.findall(r'Average Latency \(s\):\s+(\d+\.\d+)', content)
        latencies = [float(match) for match in matches]
    
    # Use file name as column header (without .txt extension)
    column_name = file.replace('.txt', '')
    all_latencies[column_name] = latencies
    print(f"{column_name}: Found {len(latencies)} latency values")

# Create CSV file
output_file = 'latency_results.csv'

# Get the maximum number of rows (should be 60)
max_rows = max(len(values) for values in all_latencies.values())

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write header
    writer.writerow(list(all_latencies.keys()))
    
    # Write data rows
    for i in range(max_rows):
        row = []  # No row number
        for file in files:
            column_name = file.replace('.txt', '')
            if i < len(all_latencies[column_name]):
                row.append(all_latencies[column_name][i])
            else:
                row.append('')  # Empty if no data
        writer.writerow(row)

print(f"\nCSV file created: {output_file}")
print(f"Total rows: {max_rows}")
