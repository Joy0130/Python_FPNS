#!/bin/bash

# 確保 uv.lock 是最新的
uv sync --no-install-project

# 設置映像名稱正式機
# IMAGE_NAME="ghcr.io/joy0130/python_fpns:FPNS"

# 設置映像名稱測試機
IMAGE_NAME="ghcr.io/joy0130/python_fpns:dev"

# 構建 Docker 映像
echo " 構建 Docker 映像..."
docker build -t "$IMAGE_NAME" .

echo "✅ Docker 映像構建完成！"
echo "映像標籤: $IMAGE_NAME"
echo ""
echo "💡 下一步："
echo "  推送到 GHCR: docker push $IMAGE_NAME"