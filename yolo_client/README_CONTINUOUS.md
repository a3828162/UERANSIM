# YOLO Client 持續檢測模式

## 功能說明

yolo_client.py 現在支援兩種模式：

### 1. 批量檢測模式（原有功能）
一次性檢測指定的圖片文件

### 2. 持續檢測模式（新功能）
從指定目錄持續讀取圖片，每秒發送一張到 HTTP/3 server 進行物件偵測

## 使用方法

### 持續檢測模式

#### 基本用法（無限循環）
```bash
python3 yolo_client.py --continuous --folder train2017 --host <server-ip> --port 8443 --insecure
```

#### 指定發送間隔（例如每 0.5 秒一張）
```bash
python3 yolo_client.py --continuous --folder train2017 --interval 0.5 --host <server-ip> --port 8443 --insecure
```

#### 限制最大請求數（例如只發送 100 張）
```bash
python3 yolo_client.py --continuous --folder train2017 --max-requests 100 --host <server-ip> --port 8443 --insecure
```

#### 詳細日誌輸出
```bash
python3 yolo_client.py --continuous --folder train2017 --host <server-ip> --port 8443 --insecure -v
```

### 批量檢測模式（原有功能）

```bash
python3 yolo_client.py image1.jpg image2.jpg --host <server-ip> --port 8443 --insecure
```

## 參數說明

### 持續模式專用參數

- `--continuous`: 啟用持續檢測模式
- `--folder <path>`: 圖片目錄路徑（必須與 --continuous 一起使用）
- `--interval <seconds>`: 發送間隔秒數（默認: 1.0）
- `--max-requests <num>`: 最大請求數（默認: 無限循環）

### 通用參數

- `--host <hostname>`: 服務器主機名（默認: localhost）
- `--port <port>`: 服務器端口（默認: 8443）
- `--endpoint <path>`: 檢測端點路徑（默認: /object-detect）
- `--insecure`: 跳過 SSL 證書驗證（測試用）
- `-v, --verbose`: 詳細日誌輸出

## 輸出資訊

持續檢測模式會顯示：

1. **每個請求的詳細資訊**：
   - 圖片名稱和大小
   - 傳輸時間
   - 處理時間
   - 吞吐量
   - RTT（往返時間）
   - 檢測到的物體數量

2. **統計摘要**（按 Ctrl+C 停止後）：
   - 總請求數
   - 使用的圖片數量
   - 總運行時間
   - 實際發送速率
   - 傳輸時間統計（平均/最小/最大）
   - 處理時間統計（平均/最小/最大）
   - 吞吐量統計（平均/最小/最大）

## 停止程序

按 `Ctrl+C` 即可安全停止持續檢測，程序會顯示統計資訊後退出。

## 範例

### 每秒從 train2017 發送圖片到本地 server（無限循環）
```bash
cd /home/ubuntu/UERANSIM/yolo_client
python3 yolo_client.py --continuous --folder train2017 --host localhost --port 8443 --insecure
```

### 每 2 秒發送一張，最多 50 張圖片
```bash
python3 yolo_client.py --continuous --folder train2017 --interval 2.0 --max-requests 50 --host 192.168.1.100 --port 8443 --insecure
```

## 圖片格式支援

程序自動掃描目錄中的以下格式圖片：
- `.jpg`
- `.jpeg`
- `.png`
- `.JPG`
- `.JPEG`
- `.PNG`

## 注意事項

1. 圖片會按文件名排序後循環發送
2. 如果圖片數量少於最大請求數，程序會循環使用圖片
3. 實際發送速率可能因網路狀況或處理時間而低於設定的間隔
4. 使用 `--insecure` 選項僅適用於測試環境，生產環境應配置正確的 SSL 證書
