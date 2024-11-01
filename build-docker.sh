#!/bin/bash
. venv/bin/activate
pip freeze > requirements.txt
pip uninstall -r requirements.txt -y
deactivate
rm -r venv/
sudo docker build -t "nas-tvm.futsu.com.tw:9999/python-fpns:latest" .