#!/bin/sh

# 確保data目錄有正確權限
chmod -R 755 /app/data

# 檢查模板檔案是否存在
if [ ! -f "/app/data/推播標準格式.xlsx" ]; then
    echo "警告: 模板檔案不存在於 /app/data/推播標準格式.xlsx"
    ls -la /app/data/
else
    echo "模板檔案存在: $(ls -la /app/data/推播標準格式.xlsx)"
fi

# 啟動Flask應用程式
echo "啟動FPNS應用程式..."
exec uv run python app.py