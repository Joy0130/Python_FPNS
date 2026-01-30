from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests
import os
import json
from datetime import datetime, timezone, timedelta

# 台灣時區 UTC+8
TAIWAN_TZ = timezone(timedelta(hours=8))

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

def save_history_record(notification_type, filename, total, success, failed, responses, is_scheduled=False, scheduled_time=None, schedule_id=None):
    """保存推播歷史記錄"""
    ensure_data_directory()
    
    # 載入現有記錄
    history = load_history()
    
    # 創建新記錄
    record = {
        'id': len(history) + 1,
        'timestamp': datetime.now(TAIWAN_TZ).isoformat(),
        'notification_type': notification_type,
        'filename': filename,
        'is_scheduled': is_scheduled,
        'summary': {
            'total': total,
            'success': success,
            'failed': failed
        },
        'details': responses
    }
    
    # 如果是排程推播，加入排程時間資訊
    if is_scheduled and scheduled_time:
        record['scheduled_time'] = scheduled_time
        record['status'] = 'completed'  # 執行完成的排程
    
    # 加入排程ID（如果有）
    if schedule_id:
        record['schedule_id'] = schedule_id
    
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
