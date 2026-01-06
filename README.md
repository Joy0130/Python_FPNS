# Python FPNS - Flask Push Notification System

Flask 推播通知系統，支援批量發送 HTML 格式的推播訊息。

## 🚀 快速開始

### 前置需求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv) - 快速的 Python 套件管理工具

### 安裝 uv（如果尚未安裝）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 設置專案

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
