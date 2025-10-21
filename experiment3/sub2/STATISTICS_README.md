# DNS Statistics Summary

## 概述

本分析從5個不同UE數量的scenario（10, 30, 50, 100, 200 UEs）中提取DNS查詢統計數據，每個scenario包含對應數量的UE，每個UE執行60秒的DNS查詢測試。

## 生成的文件

### 1. CSV文件
- **dns_statistics_summary.csv** (647 bytes)
  - 包含5個scenarios的平均統計數據
  - 每個scenario對應該資料夾下所有UE的統計平均值

### 2. 視覺化圖表
- **dns_statistics_summary.png** (325 KB)
  - 4個子圖展示關鍵指標
- **dns_statistics_table.png** (207 KB)
  - 詳細比較表格

### 3. 腳本
- **aggregate_statistics.py** - 數據提取和聚合腳本
- **visualize_summary.py** - 視覺化生成腳本

## CSV欄位說明

| 欄位名稱 | 說明 |
|---------|------|
| Scenario | 測試場景名稱 (10ue, 30ue, 50ue, 100ue, 200ue) |
| UE_Count | UE數量 |
| Total_UEs | 實際處理的UE數量 |
| Queries_Sent_Avg | 平均發送的查詢數 |
| Queries_Completed_Avg | 平均完成的查詢數 |
| Queries_Completed_Pct | 完成查詢的百分比 |
| Queries_Lost_Avg | 平均丟失的查詢數 |
| Queries_Lost_Pct | 丟失查詢的百分比 |
| **Avg_Latency_ms** | **平均延遲（毫秒）** |
| **Min_Latency_ms** | **最小延遲（毫秒）** |
| **Max_Latency_ms** | **最大延遲（毫秒）** |
| **Latency_StdDev_ms** | **延遲標準差（毫秒）** |
| Queries_Per_Second | 每秒查詢數 |

## 統計結果摘要

| Scenario | UE Count | Queries Lost % | Avg Latency (ms) | Min Latency (ms) | Max Latency (ms) | StdDev (ms) |
|----------|----------|----------------|------------------|------------------|------------------|-------------|
| **10ue** | 10 | 0.00% | **3.924** | 1.948 | 7.033 | 1.235 |
| **30ue** | 30 | 0.00% | **6.466** | 2.084 | 14.781 | 2.756 |
| **50ue** | 50 | 0.00% | **6.136** | 1.620 | 82.304 | 11.709 |
| **100ue** | 100 | 0.00% | **21.016** | 1.614 | 156.133 | 23.996 |
| **200ue** | 200 | 0.00% | **53.208** | 1.603 | 198.064 | 41.657 |

## 關鍵發現

### 1. 查詢成功率
✅ **所有scenarios的查詢完成率均為100%**，沒有查詢丟失

### 2. 延遲性能

**相對於基準（10ue）的性能退化：**

| Scenario | Avg Latency | 增加量 | 增加百分比 |
|----------|-------------|--------|-----------|
| 10ue (baseline) | 3.924 ms | - | - |
| 30ue | 6.466 ms | +2.542 ms | +64.8% |
| 50ue | 6.136 ms | +2.212 ms | +56.4% |
| 100ue | 21.016 ms | +17.093 ms | **+435.6%** |
| 200ue | 53.208 ms | +49.284 ms | **+1256.1%** |

**關鍵觀察：**
- ⚠️ 50ue比30ue略低，但最大延遲和變異性顯著增加
- 🚨 100ue開始出現劇烈性能退化（4.4倍增長）
- 🔴 200ue延遲增加超過12倍

### 3. 穩定性評估

使用變異係數（CV = StdDev/Mean × 100%）評估：

| Scenario | CV (%) | 品質評估 |
|----------|--------|----------|
| 10ue | 31.47% | ✅ Good (Stable) |
| 30ue | 42.62% | ✅ Good (Stable) |
| 50ue | 190.83% | ❌ Poor (Highly Variable) |
| 100ue | 114.18% | ❌ Poor (Highly Variable) |
| 200ue | 78.29% | ⚠️ Fair (Variable) |

**結論：**
- CV < 50%：穩定且可預測（10ue, 30ue）
- CV > 100%：高度不穩定（50ue, 100ue）

### 4. 延遲範圍分析

| Scenario | Min (ms) | Max (ms) | Range (ms) | Range/Avg |
|----------|----------|----------|------------|-----------|
| 10ue | 1.948 | 7.033 | 5.085 | 1.30x |
| 30ue | 2.084 | 14.781 | 12.697 | 1.97x |
| 50ue | 1.620 | 82.304 | 80.684 | **13.15x** |
| 100ue | 1.614 | 156.133 | 154.519 | **7.35x** |
| 200ue | 1.603 | 198.064 | 196.461 | **3.69x** |

**觀察：**
- 最小延遲在所有scenarios中保持穩定（~1.6-2.1ms）
- 最大延遲隨UE數量急劇增長
- 50ue的範圍/平均比最高，表示極端不穩定

## 建議

### 🟢 推薦使用範圍：≤ 30 UEs
- 延遲 < 7ms
- 穩定且可預測
- 適合生產環境

### 🟡 可接受範圍：30-50 UEs
- 延遲 6-7ms（平均）
- 但要注意高變異性
- 需要密切監控

### 🔴 不建議：≥ 100 UEs
- 延遲 > 20ms
- 極度不穩定
- 不適合對延遲敏感的應用

## 使用方法

### 重新生成數據
```bash
cd /home/ubuntu/UERANSIM/experiment3/sub2
python3 aggregate_statistics.py
```

### 生成視覺化
```bash
python3 visualize_summary.py
```

### 查看CSV
```bash
cat dns_statistics_summary.csv
# 或使用 column 格式化顯示
cat dns_statistics_summary.csv | column -t -s,
```

## 數據來源

- **位置**: `/home/ubuntu/UERANSIM/experiment3/sub2/{10,30,50,100,200}ue/`
- **文件格式**: `ue_*_latency.log`
- **測試工具**: dnsperf 2.9.0
- **測試時間**: 60秒/UE
- **查詢頻率**: 1查詢/秒
- **總測量數**: 390 UEs × 60 queries = 23,400 measurements

---

*生成日期: 2025-10-21*  
*腳本: aggregate_statistics.py, visualize_summary.py*
