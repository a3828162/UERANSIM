#!/bin/bash
# === 使用 rsync 同步 edge1/2/3 資料並清空遠端內容 ===

# 定義 Edge 主機與對應目錄
declare -A EDGES=(
  ["edge1"]="140.113.208.89"
  ["edge2"]="140.113.208.91"
  ["edge3"]="140.113.208.76"
)

REMOTE_USER=jameswu
REMOTE_BASE=/home/jameswu/xuan/udp_sender/dataset
LOCAL_BASE=./data

# 確保本地端目錄存在
mkdir -p "${LOCAL_BASE}"

for edge in "${!EDGES[@]}"; do
  host=${EDGES[$edge]}
  echo "=============================="
  echo "🚀 Syncing from $edge ($host)"
  echo "=============================="

  mkdir -p "${LOCAL_BASE}"

  # 1️⃣ 用 rsync 同步遠端 → 本地（會覆蓋同名檔案）
  rsync -avz --progress ${REMOTE_USER}@${host}:${REMOTE_BASE}/${edge}/ ${LOCAL_BASE}/

  # 2️⃣ 清空遠端內容（但保留 edge 資料夾本身）
  ssh ${REMOTE_USER}@${host} "find ${REMOTE_BASE}/${edge} -mindepth 1 -delete"

  echo "✅ ${edge} done."
  echo ""
done

echo "🎯 All edges synced successfully!"
