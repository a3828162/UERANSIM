#!/bin/bash
# 批量生成 Poisson/Exponential trace 文件
# 用法: ./batch_generate_traces.sh <start_seed> <end_seed>

if [ $# -lt 2 ]; then
    echo "Usage: $0 <start_seed> <end_seed>"
    echo "Example: $0 1 10  # 生成 seed 1 到 10 的 trace 文件"
    exit 1
fi

START_SEED=$1
END_SEED=$2

if [ $START_SEED -gt $END_SEED ]; then
    echo "Error: start_seed ($START_SEED) must be less than or equal to end_seed ($END_SEED)"
    exit 1
fi

echo "=========================================="
echo "批量生成 Trace 文件"
echo "範圍: seed $START_SEED 到 $END_SEED"
echo "=========================================="
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for seed in $(seq $START_SEED $END_SEED); do
    echo "[$seed/$END_SEED] 正在生成 trace_seed${seed}.csv..."
    
    if python3 createPoissionExponential.py $seed; then
        ((SUCCESS_COUNT++))
        echo "  ✓ trace_seed${seed}.csv 生成成功"
    else
        ((FAIL_COUNT++))
        echo "  ✗ trace_seed${seed}.csv 生成失敗"
    fi
    echo ""
done

echo "=========================================="
echo "完成！"
echo "成功: $SUCCESS_COUNT 個文件"
echo "失敗: $FAIL_COUNT 個文件"
echo "=========================================="
