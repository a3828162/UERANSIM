#!/usr/bin/env python3
"""
檢查 traces 目錄中的 CSV 文件，找出 t_arrive 間隔都大於等於指定閾值的文件
"""

import pandas as pd
from pathlib import Path
import sys

def check_trace_intervals(traces_dir='./traces', min_interval=10):
    """
    檢查所有 trace CSV 文件的 t_arrive 間隔
    
    參數:
        traces_dir: traces 目錄路徑
        min_interval: 最小間隔閾值（秒）
    
    返回:
        符合條件的文件列表
    """
    traces_path = Path(traces_dir)
    
    if not traces_path.exists():
        print(f"❌ 錯誤: 目錄 {traces_dir} 不存在")
        return []
    
    csv_files = sorted(traces_path.glob('trace_seed*.csv'))
    
    if not csv_files:
        print(f"❌ 錯誤: 在 {traces_dir} 中找不到 trace_seed*.csv 文件")
        return []
    
    print(f"檢查所有 trace CSV 文件的 t_arrive 間隔 (閾值: {min_interval}s):\n")
    print("=" * 70)
    
    valid_files = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            if len(df) < 2:
                print(f"⚠️  {csv_file.name:25s} - 數據不足 (僅 {len(df)} 行)")
                continue
            
            # 計算相鄰 t_arrive 的差距
            intervals = df['t_arrive'].diff().dropna()
            
            # 檢查是否所有間隔都 >= min_interval
            min_interval_value = intervals.min()
            max_interval_value = intervals.max()
            avg_interval_value = intervals.mean()
            all_above_threshold = (intervals >= min_interval).all()
            
            if all_above_threshold:
                valid_files.append({
                    'filename': csv_file.name,
                    'path': str(csv_file),
                    'min_interval': min_interval_value,
                    'max_interval': max_interval_value,
                    'avg_interval': avg_interval_value,
                    'num_events': len(df)
                })
                print(f"✅ {csv_file.name:25s} - 最小: {min_interval_value:6.2f}s, "
                      f"平均: {avg_interval_value:6.2f}s, 最大: {max_interval_value:6.2f}s, "
                      f"事件數: {len(df)}")
            else:
                print(f"❌ {csv_file.name:25s} - 最小: {min_interval_value:6.2f}s "
                      f"(不符合 >= {min_interval}s)")
        
        except Exception as e:
            print(f"⚠️  {csv_file.name:25s} - 讀取錯誤: {e}")
    
    print("\n" + "=" * 70)
    print(f"\n符合條件的文件 (共 {len(valid_files)} 個):\n")
    
    if valid_files:
        for idx, file_info in enumerate(valid_files, 1):
            print(f"{idx:2d}. {file_info['filename']:25s} - "
                  f"間隔範圍: [{file_info['min_interval']:.2f}, {file_info['max_interval']:.2f}]s, "
                  f"平均: {file_info['avg_interval']:.2f}s, "
                  f"事件數: {file_info['num_events']}")
    else:
        print("  (無符合條件的文件)")
    
    return valid_files

def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='檢查 trace CSV 文件的 t_arrive 間隔',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 檢查間隔都 >= 10 秒的文件
  python3 check_trace_intervals.py
  
  # 檢查間隔都 >= 20 秒的文件
  python3 check_trace_intervals.py --min-interval 20
  
  # 指定 traces 目錄
  python3 check_trace_intervals.py --traces-dir /path/to/traces
        """
    )
    
    parser.add_argument(
        '--traces-dir',
        default='./traces',
        help='traces 目錄路徑 (預設: ./traces)'
    )
    
    parser.add_argument(
        '--min-interval',
        type=float,
        default=10.0,
        help='最小間隔閾值（秒）(預設: 10.0)'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='將符合條件的文件列表輸出到 valid_traces.txt'
    )
    
    args = parser.parse_args()
    
    # 執行檢查
    valid_files = check_trace_intervals(
        traces_dir=args.traces_dir,
        min_interval=args.min_interval
    )
    
    # 如果需要導出
    if args.export and valid_files:
        output_file = 'valid_traces.txt'
        with open(output_file, 'w') as f:
            for file_info in valid_files:
                f.write(f"{file_info['filename']}\n")
        print(f"\n✅ 已將符合條件的文件列表導出到: {output_file}")
    
    return 0 if valid_files else 1

if __name__ == "__main__":
    sys.exit(main())
