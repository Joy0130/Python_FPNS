from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests
import os
import json
from datetime import datetime

# 歷史記錄文件路徑
HISTORY_FILE = 'data/history.json'

def ensure_data_directory():
    """確保 data 目錄存在"""
    os.makedirs('data', exist_ok=True)

def load_history():
    """載入歷史記錄"""
    ensure_data_directory()
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入歷史記錄失敗: {e}")
        return []

def save_history_record(notification_type, filename, total, success, failed, responses):
    """保存推播歷史記錄"""
    ensure_data_directory()
    
    # 載入現有記錄
    history = load_history()
    
    # 創建新記錄
    record = {
        'id': len(history) + 1,
        'timestamp': datetime.now().isoformat(),
        'notification_type': notification_type,
        'filename': filename,
        'summary': {
            'total': total,
            'success': success,
            'failed': failed
        },
        'details': responses
    }
    
    # 添加到歷史記錄
    history.append(record)
    
    # 保存到文件
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"歷史記錄已保存: ID {record['id']}")
    except Exception as e:
        print(f"保存歷史記錄失敗: {e}")

def get_notification_type_name(notification_type):
    """獲取推播類型的中文名稱"""
    type_mapping = {
        'btext': '福利金',
        'etext': '教育補助',
        'ftext': '春節禮金'
    }
    return type_mapping.get(notification_type, notification_type)
