#!/bin/bash
python3 -m venv venv
. venv/bin/activate
pip3 install flask
pip3 install pandas
pip3 install requests
pip3 install virtualenv
pip3 install openpyxl
python3 app.py
