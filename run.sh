#!/bin/bash

# 使用 uv 同步依賴（會自動創建虛擬環境）
uv sync --no-install-project

# 使用 source 加載 .env 文件中的變數
if [ -f .env ]; then
  source .env
fi

# 使用 uv run 執行應用
uv run python app.py
