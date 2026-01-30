FROM python:3.12.3-alpine

# 安裝 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 設置工作目錄
WORKDIR /app

# 複製專案配置文件
COPY pyproject.toml uv.lock ./

# 複製應用程式碼和模板
COPY app.py ./
COPY history.py ./
COPY templates ./templates
COPY static ./static

# 設置環境變數
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 創建data目錄用於存放數據文件
RUN mkdir -p /app/data

# 同步依賴（會自動創建虛擬環境）
RUN uv sync --no-install-project --frozen

# 開放 Flask 預設埠 5002
EXPOSE 5002

# 啟動 Flask 應用
CMD ["uv", "run", "python", "app.py"]