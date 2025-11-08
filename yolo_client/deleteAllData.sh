#!/bin/bash

# 刪除 dataset 目錄下所有子資料夾中的檔案，但保留資料夾本身

DATASET_DIR="/home/ubuntu/UERANSIM/yolo_client/dataset"

# 檢查 dataset 目錄是否存在
if [ ! -d "$DATASET_DIR" ]; then
    echo "錯誤: 目錄 $DATASET_DIR 不存在"
    exit 1
fi

echo "開始清理 $DATASET_DIR 下的所有檔案..."

# 遍歷 dataset 下的所有子資料夾
for dir in "$DATASET_DIR"/*/ ; do
    if [ -d "$dir" ]; then
        folder_name=$(basename "$dir")
        echo "清理資料夾: $folder_name"
        
        # 刪除該資料夾下的所有檔案（不包含子資料夾）
        rm -f "$dir"/*
        
        # 計算剩餘檔案數
        remaining=$(find "$dir" -type f | wc -l)
        echo "  - 已清理，剩餘檔案數: $remaining"
    fi
done

echo "清理完成！"
echo ""
echo "資料夾結構："
ls -l "$DATASET_DIR"