#!/bin/bash
python3 -m venv venv
. venv/bin/activate
pip3 install flask
pip3 install pandas
pip3 install requests
pip3 install virtualenv
pip3 install openpyxl
pip3 install load-dotenv
pip3 install pdm-dotenv
# 使用 source 加載 .env 文件中的變數
if [ -f .env ]; then
  source .env
fi
python3 app.py
