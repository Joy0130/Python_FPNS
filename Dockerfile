FROM python:3.12.3-alpine

# 安裝 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 設定工作目錄
WORKDIR /app

# 環境變數（uv 建議先設）
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 複製依賴定義檔
COPY pyproject.toml uv.lock ./

# 先安裝依賴（避免程式碼變動導致 cache 失效）
RUN uv sync --no-install-project --frozen

# 複製應用程式碼與資源
COPY app.py history.py ./
COPY templates ./templates
COPY static ./static
RUN mkdir -p /app/data

# 驗證 data 目錄與 Excel 檔案
RUN chmod 755 /app/data && \
    ls -la /app/data && \
    test -f "/app/static/推播標準格式.xlsx" && \
    test "$(wc -c < /app/static/推播標準格式.xlsx)" -gt 0

# 開放 Flask port（與你 app.py 一致）
EXPOSE 5002

# 啟動 Flask
CMD ["uv", "run", "python", "app.py"]
