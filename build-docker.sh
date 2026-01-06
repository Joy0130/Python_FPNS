#!/bin/bash

# 確保 uv.lock 是最新的
uv sync --no-install-project

# 構建 Docker 映像
docker build -t "nas-tvm.futsu.com.tw:9999/python-fpns:latest" .

echo "✅ Docker 映像構建完成！"