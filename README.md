# Python FPNS - Flask Push Notification System

Flask 推播通知系統，支援批量發送 HTML 格式的推播訊息。

## 🚀 快速開始

### 方式一：Docker 部署（推薦）

使用 Docker 是最快速且一致的部署方式，無需在伺服器上安裝 Python 或相關依賴。

#### 前置需求

- Docker 環境

#### 部署步驟

```bash
# 拉取測試映像
docker pull ghcr.io/futsumis/fpns:dev

# 拉取正式映像
docker pull ghcr.io/futsumis/fpns:main

# 運行測試容器
docker run -d \
  -p 5002:5002 \
  --name fpns-container-dev \
  -e PUSH_API_URL="你的推播API測試機網址" \
  -e PUSH_API_KEY="你的API測試機金鑰" \
  -e FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -v /var/lib/fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/futsumis/fpns:dev
```

```bash
# 運行正式容器
docker run -d \
  -p 5001:5001 \
  --name fpns-container-main \
  -e PUSH_API_URL="你的推播API正式機網址" \
  -e PUSH_API_KEY="你的API正式機金鑰" \
  -e FLASK_SECRET_KEY="你儲存的密鑰" \
  -v /var/lib/fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/futsumis/fpns:main
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
   cd FPNS
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

   瀏覽器打開測試機：`http://localhost:5002`

   瀏覽器打開正式機：`http://localhost:5001`

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

### 正式機 main

### 測試機 dev

### 自動構建（GitHub Actions）

當推送程式碼到 GitHub 的 `main` 或 `dev` 分支時，GitHub Actions 會自動：

- 構建 Docker 映像
- 推送到 GitHub Container Registry (GHCR)
- 映像路徑：`ghcr.io/futsumis/fpns:main` 或 `ghcr.io/futsumis/fpns:dev`

### 設置映像為ython_fpns:main` 或 `ghcr.io/futsumis/fpns:dev`

fpns:dev`

### 更新部署

```bash
# 拉取最新映像測試機
docker pull ghcr.io/futsumis/fpns:dev

# 拉取最新映像正式機
docker pull ghcr.io/futsumis/fpns:main

# 停止並移除舊容器
docker stop fpns-container-dev
docker rm fpns-container-dev

# 拉取最新映像正式機
docker pull ghcr.io/futsumis/config.json
.env

# uv
.venv/
.python-version

# Python
venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

#data
/data/history.json
/data/scheduled_notifications.jsonfpns:main

# 停止並移除舊容器
docker stop fpns-container
docker rm fpns-container

# 運行新容器測試機（使用相同的 FLASK_SECRET_KEY）
docker run -d \
  -p 5002:5002 \
  --name fpns-container-dev \
  -e PUSH_API_URL="你的推播API測試機網址" \
  -e PUSH_API_KEY="你的API測試機金鑰" \
  -e FLASK_SECRET_KEY="你儲存的密鑰" \
  -v /var/lib/fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/futsumis/fpns:dev
```

```bash
# 運行新容器正式機（使用相同的 FLASK_SECRET_KEY）
docker run -d \
  -p 5001:5001 \
  --name fpns-container-main \
  -e PUSH_API_URL="你的推播API正式機網址" \
  -e PUSH_API_KEY="你的API正式機金鑰" \
  -e FLASK_SECRET_KEY="你儲存的密鑰" \
  -v /var/lib/fpns:/app/data \
  --restart unless-stopped \
  ghcr.io/futsumis/fpns:main
```

### 環境變數說明

- `PUSH_API_URL`: 推播 API 的完整網址
- `PUSH_API_KEY`: API 金鑰
- `FLASK_SECRET_KEY`: Flask session 加密密鑰（**請保存，更新時需使用相同密鑰**）

### 資料持久化

- **掛載目錄**: `/var/lib/fpns:/app/data`
- **用途**: 存儲推播歷史記錄（`history.json`）
- **重要性**: 不掛載會導致重啟後歷史記錄遺失

### 監控與維護

```bash
# 查看容器狀態
docker ps | grep fpns

# 查看日誌
docker logs fpns-container-dev
docker logs fpns-container-main

# 即時追蹤日誌
docker logs -f fpns-container-dev
docker logs -f fpns-container-main

# 重啟容器
docker restart fpns-container-dev
docker restart fpns-container-main
```

完整的 Docker 部署說明請參考 [DEPLOYMENT.md](./DEPLOYMENT.md) 和 [DOCKER_UPDATE.md](./DOCKER_UPDATE.md)。

## ☸️ Kubernetes 部署（Helm + Argo CD）

正式環境採用 GitOps 流程部署到 Kubernetes 叢集：先由 GitHub Actions 產生 Docker 映像並推送到 GHCR，接著透過 **Helm** 定義部署資源、由 **Argo CD** 監聽 Git 儲存庫並自動同步至 K8s 叢集，最後由 **Traefik** 作為反向代理綁定 **FQDN**，讓使用者以網址連線登入。

### 部署流程

```
GitHub Actions (build & push image)
  → GHCR (ghcr.io/futsumis/fpns:main / :dev)
  → Helm Chart (定義 Deployment / Service / Traefik IngressRoute)
  → Argo CD (監聽 Git 變更並自動同步至叢集)
  → Kubernetes Containers (Pod 運行中)
  → Traefik + FQDN (透過 Traefik 對外提供網址存取)
```

### 存取網址（FQDN）

部署完成後，可透過下列網址連線登入：

| 環境 | 網址 | 對應映像 |
|------|------|----------|
| 正式機 | http://ewc.futsu.com.tw/login | `ghcr.io/futsumis/fpns:main` |
| 測試機 | https://tewc.futsu.com.tw/login | `ghcr.io/futsumis/fpns:dev` |

### 說明

- **Helm**：以 Chart 管理 Kubernetes 部署資源（Deployment、Service、Traefik IngressRoute 等），並透過 `values.yaml` 區分正式機與測試機的設定與環境變數。
- **Argo CD**：採用 GitOps 模式，持續監聽 Git 儲存庫中的 Helm 設定，一旦有變更即自動同步部署至 K8s 叢集，確保叢集狀態與 Git 一致。
- **Traefik**：作為叢集的反向代理／Ingress Controller，透過 IngressRoute 綁定網域並處理路由與 TLS，使用者可直接以上述 FQDN 存取並登入（Keycloak OAuth2 驗證）。

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