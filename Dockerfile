FROM python:3.12.3-alpine
WORKDIR /app
COPY requirements.txt ./
# COPY config*.json ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app