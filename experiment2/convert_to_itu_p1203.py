#!/usr/bin/env python3
"""
Convert performance CSV files to ITU-P1203 Mode 0 JSON format.

Usage:
    python3 convert_to_itu_p1203.py <input_csv> [output_json]
    
Example:
    python3 convert_to_itu_p1203.py data/edge2/performance_ue1.csv output_ue1.json
"""

import csv
import json
import sys
from pathlib import Path


def convert_csv_to_itu_p1203(csv_path, output_path=None):
    """
    Convert performance CSV to ITU-P1203 Mode 0 JSON format.
    
    Parameters from requirements:
    - I11: audio (not considered, same as mode0_without_audio.json)
    - IGen: device=pc, displaySize=2048x1080, viewingDistance=0
    - Stalling: one entry [0,8] for initial stalling
    - streamId: 42 (uniform)
    - I13 segments: each segment duration=1 (one per second)
    - resolution: 2048x1080 (uniform)
    - start: begins at 0, increments by 1
    - codec: h264
    """
    
    # Read CSV data
    segments = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        start_time = 0
        
        for row in reader:
            # Each row represents 1 second of data
            segment = {
                "bitrate": float(row['bitrate']),  # kbps from CSV
                "codec": "h264",
                "duration": 1,  # 1 second per segment
                "fps": int(float(row['framespersecond'])),
                "resolution": "2048x1080",
                "start": start_time
            }
            segments.append(segment)
            start_time += 1
    
    # Build the ITU-P1203 JSON structure
    itu_json = {
        "IGen": {
            "device": "pc",
            "displaySize": "2048x1080",
            "viewingDistance": 0
        },
        "I11": {
            "segments": []
        },
        "I13": {
            "streamId": 42,
            "segments": segments
        },
        "I23": {
            "stalling": [[0, 8]],
            "streamId": 42
        }
    }
    
    # Determine output path
    if output_path is None:
        csv_name = Path(csv_path).stem
        output_path = Path(csv_path).parent / f"{csv_name}_itu_p1203.json"
    
    # Write JSON output
    with open(output_path, 'w') as f:
        json.dump(itu_json, f, indent=2)
    
    print(f"✓ Converted {csv_path}")
    print(f"  → {output_path}")
    print(f"  Segments: {len(segments)}")
    print(f"  Duration: {start_time} seconds")
    
    return output_path


def batch_convert(data_dir):
    """Convert all performance_ue*.csv files in a directory."""
    data_path = Path(data_dir)
    csv_files = sorted(data_path.glob('performance_ue*.csv'))
    
    if not csv_files:
        print(f"No performance_ue*.csv files found in {data_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV file(s) to convert:")
    print()
    
    for csv_file in csv_files:
        convert_csv_to_itu_p1203(csv_file)
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nBatch convert mode:")
        print("  python3 convert_to_itu_p1203.py --batch <directory>")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("Error: --batch requires a directory path")
            sys.exit(1)
        batch_convert(sys.argv[2])
    else:
        input_csv = sys.argv[1]
        output_json = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not Path(input_csv).exists():
            print(f"Error: File not found: {input_csv}")
            sys.exit(1)
        
        convert_csv_to_itu_p1203(input_csv, output_json)


if __name__ == '__main__':
    main()
