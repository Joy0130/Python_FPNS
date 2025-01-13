FROM python:3.12.3-alpine
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# 開放 Flask 預設埠 5000
EXPOSE 5000
COPY . /app
# 啟動 Flask 應用
CMD ["python", "app.py"]