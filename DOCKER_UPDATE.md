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
  -e PUSH_API_URL="env中的PUSH_API_URL推播API網址" \
  -e PUSH_API_KEY="env中的PUSH_API_KEY推播API金鑰" \
  -e FLASK_SECRET_KEY="env中的FLASK_SECRET_KEY" \
  -v /var/lib/python-fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/joy0130/python_fpns:dev
```

## ⚠️ 重要變更

### 1. 新增環境變數

- **FLASK_SECRET_KEY**: 用於加密 Flask session

  **設置方式（二選一）：**

  A. **使用現有 env 中設定的密鑰（推薦）**

  ```bash
  -e FLASK_SECRET_KEY="env中的FLASK_SECRET_KEY"
  ```

  > 直接使用您 `.env` 檔案中的 `FLASK_SECRET_KEY`，保持本地與 Docker 一致

  B. **生成新密鑰（僅首次）**

  ```bash
  # 先生成並記錄密鑰
  python3 -c 'import secrets; print(secrets.token_hex(32))'

  # 然後使用生成的密鑰
  -e FLASK_SECRET_KEY="生成的密鑰"
  ```

  > **重要**：生成後請**保存密鑰**，後續更新需使用相同密鑰

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

# 即時追蹤日誌
docker logs -f python-fpns-container

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
