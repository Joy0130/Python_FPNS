# Python FPNS - Flask Push Notification System

Flask 推播通知系統，支援批量發送 HTML 格式的推播訊息。

## 🚀 快速開始

### 方式一：Docker 部署（推薦）

使用 Docker 是最快速且一致的部署方式，無需在伺服器上安裝 Python 或相關依賴。

#### 前置需求

- Docker 環境

#### 部署步驟

```bash
# 拉取最新映像
docker pull ghcr.io/joy0130/python_fpns:latest

# 運行容器
docker run -d \
  -p 5001:5001 \
  --name python-fpns-container \
  -e PUSH_API_URL="你的推播API網址" \
  -e PUSH_API_KEY="你的API金鑰" \
  -e FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -v /var/lib/python-fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/joy0130/python_fpns:latest
```

詳細的 Docker 部署說明請參考 [DEPLOYMENT.md](./DEPLOYMENT.md)。

---

### 方式二：本地開發

適合開發環境或需要修改程式碼的情況。

#### 前置需求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) - 快速的 Python 套件管理工具

#### 安裝 uv（如果尚未安裝）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 設置專案

1. **克隆或進入專案目錄**

   ```bash
   cd Python_FPNS
   ```

2. **安裝依賴**

   ```bash
   uv sync --no-install-project
   ```

   這會自動創建虛擬環境並安裝所有依賴套件。

3. **配置環境變數**

   創建或編輯 `.env` 文件：

   ```bash
   PUSH_API_URL=你的推播API網址
   PUSH_API_KEY=你的API金鑰
   FLASK_SECRET_KEY=你的Session加密金鑰
   ```

4. **運行應用**

   使用腳本運行（推薦）：

   ```bash
   ./run.sh
   ```

   或直接使用 uv 運行：

   ```bash
   uv run python app.py
   ```

5. **訪問應用**

   瀏覽器打開：`http://localhost:5001`

## 📦 依賴套件

- **Flask** - Web 框架
- **Pandas** - Excel 數據處理
- **Requests** - HTTP 請求
- **OpenPyXL** - Excel 文件讀取
- **Python-dotenv** - 環境變數管理

## 🔧 常用命令

### 添加新的依賴

```bash
uv add package-name
```

### 更新依賴

```bash
uv sync --no-install-project
```

### 移除依賴

```bash
uv remove package-name
```

### 查看已安裝的套件

```bash
uv pip list
```

### 運行 Python 腳本

```bash
uv run python script.py
```

## 🎯 功能特點

- ✅ 批量發送推播通知（支援數百則訊息）
- ✅ 多線程並發處理（最多同時 10 個請求）
- ✅ 自動去重避免重複推播
- ✅ HTML 格式推播內容（響應式設計）
- ✅ Excel 文件批量處理
- ✅ 詳細的發送統計和錯誤處理
- ✅ 推播歷史記錄（JSON 檔案存儲）
- ✅ POST-Redirect-GET 模式（防止重複提交）
- ✅ Docker 容器化部署

## 📊 推播格式

推播訊息採用完整 HTML 格式，包含：

- DOCTYPE 聲明
- 響應式 viewport 設定
- 自適應樣式（手機、平板、桌面）
- 專業的卡片式設計

## ⚡ 性能

- **並發處理**：同時發送 10 個請求
- **速度提升**：相比串行發送快約 10 倍
- **預估時間**：300 則訊息約 1-2 分鐘

## 🐳 Docker 部署

### 自動構建（GitHub Actions）

當推送程式碼到 GitHub 的 `main` 分支時，GitHub Actions 會自動：

- 構建 Docker 映像
- 推送到 GitHub Container Registry (GHCR)
- 映像路徑：`ghcr.io/joy0130/python_fpns:latest`

### 更新部署

```bash
# 拉取最新映像
docker pull ghcr.io/joy0130/python_fpns:latest

# 停止並移除舊容器
docker stop python-fpns-container
docker rm python-fpns-container

# 運行新容器（使用相同的 FLASK_SECRET_KEY）
docker run -d \
  -p 5001:5001 \
  --name python-fpns-container \
  -e PUSH_API_URL="你的推播API網址" \
  -e PUSH_API_KEY="你的API金鑰" \
  -e FLASK_SECRET_KEY="你儲存的密鑰" \
  -v /var/lib/python-fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/joy0130/python_fpns:latest
```

### 環境變數說明

- `PUSH_API_URL`: 推播 API 的完整網址
- `PUSH_API_KEY`: API 金鑰
- `FLASK_SECRET_KEY`: Flask session 加密密鑰（**請保存，更新時需使用相同密鑰**）

### 資料持久化

- **掛載目錄**: `/var/lib/python-fpns:/app/data`
- **用途**: 存儲推播歷史記錄（`history.json`）
- **重要性**: 不掛載會導致重啟後歷史記錄遺失

### 監控與維護

```bash
# 查看容器狀態
docker ps | grep python-fpns

# 查看日誌
docker logs python-fpns-container

# 即時追蹤日誌
docker logs -f python-fpns-container

# 重啟容器
docker restart python-fpns-container
```

完整的 Docker 部署說明請參考 [DEPLOYMENT.md](./DEPLOYMENT.md) 和 [DOCKER_UPDATE.md](./DOCKER_UPDATE.md)。

## 🛠️ 開發

使用 uv 的優勢：

- 🚀 更快的依賴安裝速度
- 🔒 自動生成 `uv.lock` 鎖定依賴版本
- 📦 統一的 `pyproject.toml` 配置
- 🎯 簡化的命令行工具

## 📝 注意事項

1. 首次運行會自動創建 `.venv` 虛擬環境
2. `uv.lock` 文件會自動生成，建議加入版本控制
3. 可根據 API 伺服器容量調整 `max_workers` 參數
4. 推播 API 如有速率限制，需相應調整並發數
5. **Docker 部署時請妥善保存 `FLASK_SECRET_KEY`，更新時需使用相同密鑰**

## 🔗 相關鏈接

- **GitHub Repository**: https://github.com/Joy0130/Python_FPNS
- **GitHub Container Registry**: https://github.com/Joy0130/Python_FPNS/pkgs/container/python_fpns
- **UV Package Manager**: https://github.com/astral-sh/uv
