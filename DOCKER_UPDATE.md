# Docker 部署更新說明

## 🎯 新功能

本次更新添加了以下功能：

- ✅ 推播歷史記錄（JSON 檔案存儲）
- ✅ POST-Redirect-GET 模式（防止重複提交）
- ✅ Flask session 加密

## 📋 部署命令（已更新）

### 在 Ubuntu 伺服器上執行

```bash
# 1. 停止並刪除舊容器
docker stop python-fpns-container
docker rm python-fpns-container

# 2. 拉取最新映像
docker pull ghcr.io/joy0130/python_fpns:latest

# 3. 創建資料目錄（用於存儲歷史記錄）
sudo mkdir -p /var/lib/python-fpns

# 4. 運行新容器
sudo docker run -d \
  -p 5001:5001 \
  --name python-fpns-container \
  -e PUSH_API_URL="你的推播API網址" \
  -e PUSH_API_KEY="你的API金鑰" \
  -e FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -v /var/lib/python-fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/joy0130/python_fpns:latest
```

## ⚠️ 重要變更

### 1. 新增環境變數

- **FLASK_SECRET_KEY**: 用於加密 Flask session
  - 首次部署：使用命令生成隨機密鑰
  - 更新部署：請使用相同的密鑰，否則現有 session 會失效

### 2. 資料目錄掛載

- **Volume 掛載**: `-v /var/lib/python-fpns:/app/data`
- **用途**: 存儲推播歷史記錄（`history.json`）
- **重要性**: 不掛載會導致重啟後歷史記錄遺失

## 🔍 驗證部署

```bash
# 查看容器狀態
docker ps | grep python-fpns

# 查看日誌
docker logs python-fpns-container

# 訪問應用
curl http://localhost:5001
```

## 📊 新功能驗證

1. **推播管理** - http://joylinux.futsu.com.tw:5001
2. **歷史記錄** - http://joylinux.futsu.com.tw:5001/history
3. 發送推播後重新整理結果頁面不會重複提交

## 💾 資料備份

歷史記錄檔案位置：`/var/lib/python-fpns/history.json`

備份命令：

```bash
sudo cp /var/lib/python-fpns/history.json /path/to/backup/
```
