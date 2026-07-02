# Python FPNS 部署指南

本文檔說明如何將 Python FPNS 部署到 Ubuntu 伺服器。

## 🚀 部署方式

### 方式一：使用 GitHub Container Registry（推薦）

#### 1. **自動構建（GitHub Actions）**

當您推送程式碼到 GitHub 的 `main` 分支時，GitHub Actions 會自動：

- 構建 Docker 映像
- 推送到 GitHub Container Registry (GHCR)
- 映像路徑：`ghcr.io/futsumis/fpns:latest`

#### 2. **設置映像為公開（首次需要）**

1. 前往 GitHub 個人主頁
2. 點擊 "Packages" 標籤
3. 找到 `fpns` 套件
4. 點擊 "Package settings"
5. 在 "Danger Zone" 將 visibility 改為 Public（如果需要公開存取）

#### 3. **在 Ubuntu 伺服器上部署**

SSH 連接到您的 Ubuntu 伺服器（tk8s-ubuntu-master.futsu.com.tw），然後執行：

```bash
# 拉取最新映像（如果是公開的則不需要登入）
docker pull ghcr.io/futsumis/fpns:latest

# 停止並移除舊容器（如果存在）
docker stop python-fpns-container 2>/dev/null || true
docker rm python-fpns-container 2>/dev/null || true

# 運行新容器
sudo docker run -d \
  -p 5001:5001 \
  --name fpns-container \
  -e PUSH_API_URL="你的推播API網址" \
  -e PUSH_API_KEY="你的API金鑰" \
  -e FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -v /var/lib/fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/futsumis/fpns:latest
```

> **重要說明：**
>
> - `-e FLASK_SECRET_KEY=...` 用於加密 session，**請保存生成的密鑰**
> - `-v /var/lib/fpns:/app/data` 掛載資料目錄，存儲歷史記錄
> - 更新部署時請使用**相同的 FLASK_SECRET_KEY**

#### 4. **檢查容器狀態**

```bash
# 查看容器運行狀態
docker ps | grep fpns

# 查看容器日誌
docker logs fpns-container

# 即時追蹤日誌
docker logs -f fpns-container
```

---

### 方式二：本地構建並推送

如果您想從本地構建並推送：

```bash
# 登入 GHCR（需要 Personal Access Token）
echo $GITHUB_TOKEN | docker login ghcr.io -u futsumis --password-stdin

# 構建並推送到 GHCR
./build-docker.sh ghcr

# 或者構建並推送到 NAS Registry
./build-docker.sh nas

# 或者同時構建兩個標籤
./build-docker.sh both
```

---

### 方式三：使用 NAS Registry

```bash
# 在伺服器上
docker pull nas-tvm.futsu.com.tw:9999/fpns:latest

sudo docker run -d \
  -p 5001:5001 \
  --name fpns-container \
  -e PUSH_API_URL="你的推播API網址" \
  -e PUSH_API_KEY="你的API金鑰" \
  --restart unless-stopped \
  nas-tvm.futsu.com.tw:9999/fpns:latest
```

---

## 🔄 更新部署

當您需要更新應用時：

### 使用 GitHub Actions（自動）

1. 修改程式碼
2. 提交並推送到 `main` 分支
3. GitHub Actions 自動構建新映像
4. 在伺服器上更新容器：

```bash
# 拉取最新映像
docker pull ghcr.io/futsumis/fpns:latest

# 重新啟動容器
docker stop fpns-container
docker rm fpns-container
sudo docker run -d \
  -p 5001:5001 \
  --name fpns-container \
  -e PUSH_API_URL="你的推播API網址" \
  -e PUSH_API_KEY="你的API金鑰" \
  -e FLASK_SECRET_KEY="你儲存的密鑰" \
  -v /var/lib/fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/futsumis/fpns:dev
```

> **提醒**: 更新時請使用首次部署時保存的 FLASK_SECRET_KEY

---

## 🔐 環境變數配置

應用需要以下環境變數：

- `PUSH_API_URL`: 推播 API 的完整網址
- `PUSH_API_KEY`: API 金鑰
- `FLASK_SECRET_KEY`: Flask session 加密密鑰（建議使用隨機生成）

您可以透過以下方式設置：

1. **Docker run 命令**（如上所示）
2. **環境變數檔案**：創建 `.env` 檔案並使用 `--env-file .env`
3. **Docker Compose**：在 `docker-compose.yml` 中配置

### 生成 FLASK_SECRET_KEY

```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

---

## 📊 監控與維護

### 查看應用狀態

```bash
# 檢查容器是否運行
docker ps | grep fpns

# 查看資源使用情況
docker stats fpns-container
```

### 查看日誌

```bash
# 查看最後 100 行日誌
docker logs --tail 100 fpns-container

# 即時追蹤日誌
docker logs -f fpns-container
```

### 重啟容器

```bash
docker restart fpns-container
```

---

## 🛠️ 疑難排解

### 容器無法啟動

1. 檢查日誌：`docker logs fpns-container`
2. 確認環境變數是否正確設置
3. 確認端口 5001 沒有被其他服務佔用

### 映像拉取失敗

1. 檢查網絡連接
2. 如果是私有映像，確保已登入 GHCR：
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u futsumis --password-stdin
   ```

### 應用程式錯誤

1. 檢查應用日誌
2. 確認 API 端點可訪問
3. 驗證 API 金鑰有效

---

## 📱 訪問應用

部署成功後，可以透過以下方式訪問：

- **本地訪問**：`http://localhost:5002`
- **遠程訪問**：`http://tk8s-ubuntu-master.futsu.com.tw:5002`

---
