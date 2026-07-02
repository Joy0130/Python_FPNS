import os
import json
import threading
from datetime import datetime, timezone, timedelta

# 台灣時區 UTC+8
TAIWAN_TZ = timezone(timedelta(hours=8))

# 歷史記錄文件路徑
HISTORY_FILE = 'data/history.json'

# 防止並發寫入造成資料損壞
_history_lock = threading.Lock()


def ensure_data_directory():
    """確保 data 目錄存在"""
    os.makedirs('data', exist_ok=True)


def _save_history(history):
    """內部：將 history 寫入檔案（需在 lock 內呼叫）"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存歷史記錄失敗: {e}")
        return False


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


def save_history_record(notification_type, filename, total, success, failed, responses,
                        is_scheduled=False, scheduled_time=None, schedule_id=None,
                        operator_name=None, status=None):
    """保存推播歷史記錄"""
    ensure_data_directory()

    with _history_lock:
        history = load_history()
        # 根據現有記錄自動生成新的 ID
        record = {
            'id': max((r['id'] for r in history), default=0) + 1,
            'timestamp': datetime.now(TAIWAN_TZ).isoformat(),
            'notification_type': notification_type,
            'filename': filename,
            'operator_name': operator_name or '',
            'is_scheduled': is_scheduled,
            'summary': {
                'total': total,
                'success': success,
                'failed': failed
            },
            'details': responses
        }
        # 根據參數決定是否添加 status 和 scheduled_time
        if status:
            record['status'] = status
        elif is_scheduled and scheduled_time:
            record['status'] = 'completed'

        if is_scheduled and scheduled_time:
            record['scheduled_time'] = scheduled_time

        if schedule_id:
            record['schedule_id'] = schedule_id

        history.append(record)
        _save_history(history)
        print(f"歷史記錄已保存: ID {record['id']}")


def update_schedule_record(schedule_id, updates):
    """更新指定排程記錄的欄位"""
    with _history_lock:
        history = load_history()
        for record in history:
            if record.get('schedule_id') == schedule_id:
                record.update(updates)
                if _save_history(history):
                    print(f"已更新歷史記錄: schedule_id={schedule_id}")
                    return True
                return False
    return False


def get_notification_type_name(notification_type):
    """獲取推播類型的中文名稱"""
    type_mapping = {
        'etext': '教育補助',
        'ftext': '春節禮金'
    }
    return type_mapping.get(notification_type, notification_type)
