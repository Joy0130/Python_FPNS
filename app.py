from flask import Flask, render_template, request, jsonify, session, redirect, url_for,send_file, abort
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import requests
import os
import threading
from datetime import datetime
import json
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import pytz
from history import save_history_record, load_history, get_notification_type_name


# config檔案設定
# with open("config.json") as config_file:
#     config = json.load(config_file)
#     API_URL = config["PUSH_API_URL"]
#     API_KEY = config["push-api-key"]
#     if not API_URL or not API_KEY:
#         raise ValueError("API URL or API Key is missing in config.json")

# PUSH_API_URL = API_URL
# HEADERS = {
#     "push-api-key": API_KEY,
#     "Content-Type": "application/json"
# }

app = Flask(__name__)

# 設置 secret key 用於 session（用於 POST-Redirect-GET 模式）
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-change-this-in-production")

# .env 文件的路徑
dotenv_path = os.path.join(os.getcwd(), '.env')

# 載入 .env 文件
load_dotenv(dotenv_path=dotenv_path)
print("Loaded .env file :", os.path.abspath(dotenv_path))

# 讀取環境變數
API_URL = os.getenv("PUSH_API_URL")
API_KEY = os.getenv("PUSH_API_KEY")

# 驗證環境變數是否存在
if not API_URL or not API_KEY:
    raise ValueError("沒有設定環境變數")

# 設置HEADERS
HEADERS = {
    "push-api-key": API_KEY,
    "Content-Type": "application/json"
}

# 排程推播資料檔案
SCHEDULED_NOTIFICATIONS_FILE = 'data/scheduled_notifications.json'
TAIWAN_TZ = pytz.timezone('Asia/Taipei')

# 初始化背景排程器
scheduler = BackgroundScheduler(timezone=TAIWAN_TZ)
scheduler.start()

# 載入排程推播資料
def load_scheduled_notifications():
    """載入排程推播資料"""
    if not os.path.exists(SCHEDULED_NOTIFICATIONS_FILE):
        return {"schedules": []}
    try:
        with open(SCHEDULED_NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入排程資料錯誤: {e}")
        return {"schedules": []}

# 保存排程推播資料
def save_scheduled_notifications(data):
    """保存排程推播資料"""
    try:
        with open(SCHEDULED_NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存排程資料錯誤: {e}")

# 新增排程推播
def add_scheduled_notification(schedule_id, notification_type, filename, schedule_datetime, notification_tasks):
    """新增排程推播"""
    data = load_scheduled_notifications()
    data['schedules'].append({
        'id': schedule_id,
        'notification_type': notification_type,
        'filename': filename,
        'schedule_datetime': schedule_datetime.isoformat(),
        'notification_tasks': notification_tasks,
        'created_at': datetime.now(TAIWAN_TZ).isoformat(),
        'status': 'pending'
    })
    save_scheduled_notifications(data)

# 移除排程推播
def remove_scheduled_notification(schedule_id):
    """移除已執行的排程"""
    data = load_scheduled_notifications()
    data['schedules'] = [s for s in data['schedules'] if s['id'] != schedule_id]
    save_scheduled_notifications(data)

# 執行排程的推播任務
def execute_scheduled_notification(schedule_id):
    """執行排程的推播任務"""
    print(f"\n========== 開始執行排程推播 ==========")
    print(f"排程ID: {schedule_id}")
    print(f"執行時間: {datetime.now(TAIWAN_TZ)}")
    
    # 載入排程資料
    data = load_scheduled_notifications()
    schedule = next((s for s in data['schedules'] if s['id'] == schedule_id), None)
    
    if not schedule:
        print(f"找不到排程 {schedule_id}")
        return
    
    notification_tasks = schedule['notification_tasks']
    notification_type = schedule['notification_type']
    filename = schedule['filename']
    
    print(f"準備發送 {len(notification_tasks)} 則排程推播...")
    
    # 使用現有的多線程發送邏輯
    responses = []
    max_workers = 10
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(
                send_notification,
                task['employee_id'],
                task['amount'],
                task['body_text'],
                task['file_title']
            ): task for task in notification_tasks
        }
        
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                responses.append(result)
                print(f"已發送排程推播給員工 {result['employee_id']}: 狀態碼 {result.get('status_code', 'N/A')}")
            except Exception as e:
                responses.append({
                    "employee_id": task['employee_id'],
                    "status_code": 500,
                    "error": f"執行錯誤: {str(e)}",
                    "success": False
                })
    
    # 統計結果
    success_count = sum(1 for r in responses if r.get('success', False))
    fail_count = len(responses) - success_count
    
    print(f"排程推播完成: 成功 {success_count} 則, 失敗 {fail_count} 則")
    
    # 更新歷史記錄（將待發送改為已發送）
    history = load_history()
    # 找到對應的排程記錄並更新
    for record in history:
        if record.get('schedule_id') == schedule_id:
            record['status'] = 'completed'
            record['executed_at'] = datetime.now(TAIWAN_TZ).isoformat()
            record['summary'] = {
                'total': len(responses),
                'success': success_count,
                'failed': fail_count
            }
            record['details'] = responses
            break
    
    # 如果沒找到記錄，創建新的
    if not any(r.get('schedule_id') == schedule_id for r in history):
        save_history_record(
            notification_type=notification_type,
            filename=filename,
            total=len(responses),
            success=success_count,
            failed=fail_count,
            responses=responses,
            is_scheduled=True,
            scheduled_time=schedule['schedule_datetime'],
            schedule_id=schedule_id
        )
    else:
        # 保存更新後的歷史記錄
        try:
            with open('data/history.json', 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"更新歷史記錄失敗: {e}")
    
    # 移除已執行的排程
    remove_scheduled_notification(schedule_id)
    print(f"已移除排程 {schedule_id}")

# 恢復應用重啟前的排程任務
def restore_scheduled_jobs():
    """從檔案恢復排程任務（應用重啟時）"""
    data = load_scheduled_notifications()
    now = datetime.now(TAIWAN_TZ)
    
    for schedule in data['schedules']:
        schedule_id = schedule['id']
        schedule_datetime_str = schedule['schedule_datetime']
        schedule_datetime = datetime.fromisoformat(schedule_datetime_str)
        
        # 如果排程時間還沒到，重新註冊任務
        if schedule_datetime > now:
            scheduler.add_job(
                execute_scheduled_notification,
                trigger=DateTrigger(run_date=schedule_datetime),
                args=[schedule_id],
                id=schedule_id,
                replace_existing=True
            )
            print(f"已恢復排程: {schedule_id}, 預計執行時間: {schedule_datetime}")
        else:
            # 過期的排程，標記為已過期但不刪除（讓使用者知道）
            print(f"排程 {schedule_id} 已過期，跳過")

# 應用啟動時恢復排程
restore_scheduled_jobs()

# @app.route("/fpns")
# @app.route("/fpns/")
# @app.route('/fpns/index')
@app.route('/')
def index():
    return render_template('index.html')  #讀取html檔案

# 下載推播範本
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/download_template")
def download_template():
    file_path = os.path.join(BASE_DIR, "data", "推播標準格式.xlsx")

    print("DOWNLOAD FILE PATH =", file_path)
    print("EXISTS =", os.path.exists(file_path))

    return send_file(
        file_path,
        as_attachment=True,
        download_name="推播標準格式.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# @app.route("/download_template")
# def download_template():
#     try:
#         # 統一使用專案內 data 目錄
#         file_path = os.path.join(BASE_DIR, "data", "推播標準格式.xlsx")

#         print(f"嘗試下載檔案: {file_path}")

#         # 檔案不存在
#         if not os.path.exists(file_path):
#             print("檔案不存在")
#             abort(404, "範本檔案不存在")

#         # 檔案大小檢查
#         file_size = os.path.getsize(file_path)
#         print(f"檔案大小: {file_size} bytes")

#         if file_size == 0:
#             abort(500, "範本檔案為空")

#         # 正確下載 xlsx
#         return send_file(
#             file_path,
#             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             as_attachment=True,
#             download_name="推播標準格式.xlsx"
#         )

#     except Exception as e:
#         print(f"下載錯誤: {e}")
#         abort(500, "下載失敗")


@app.route('/history')
def history():
    """顯示歷史記錄列表"""
    records = load_history()
    # 按時間倒序排列（最新的在前）
    records.reverse()
    
    # 添加類型中文名稱
    for record in records:
        record['type_name'] = get_notification_type_name(record.get('notification_type', ''))
    
    return render_template('history.html', records=records)

@app.route('/result')
def push_result():
    """顯示推播結果（POST-Redirect-GET 模式）"""
    result_data = session.pop('push_result', None)
    
    if not result_data:
        # 如果沒有結果數據，重定向到首頁
        return redirect(url_for('index'))
    
    # 排序 responses：失敗的在前，成功的在後
    responses = result_data.get('responses', [])
    sorted_responses = sorted(responses, key=lambda x: (x.get('success', True), x.get('employee_id', '')))
    
    return render_template('result.html',
        message=result_data.get('message'),
        summary=result_data.get('summary'),
        responses=sorted_responses
    )

@app.route('/history/<int:record_id>')
def history_detail(record_id):
    """顯示單一記錄的詳細資訊"""
    records = load_history()
    record = next((r for r in records if r['id'] == record_id), None)
    
    if not record:
        return "記錄不存在", 404
    
    record['type_name'] = get_notification_type_name(record.get('notification_type', ''))
    # 排序 details：失敗的在前，成功的在後
    if 'details' in record:
        record['details'] = sorted(record['details'], key=lambda x: (x.get('success', True), x.get('employee_id', '')))
    
    return render_template('history_detail.html', record=record)

@app.route('/cancel_schedule/<schedule_id>', methods=['POST'])
def cancel_schedule(schedule_id):
    """取消排程推播"""
    try:
        # 從scheduler中移除任務
        try:
            scheduler.remove_job(schedule_id)
            print(f"已從scheduler移除任務: {schedule_id}")
        except Exception as e:
            print(f"移除scheduler任務時出錯（可能已不存在）: {e}")
        
        # 從排程文件中移除
        remove_scheduled_notification(schedule_id)
        
        # 更新歷史記錄狀態為已取消
        history = load_history()
        for record in history:
            if record.get('schedule_id') == schedule_id:
                record['status'] = 'cancelled'
                record['cancelled_at'] = datetime.now(TAIWAN_TZ).isoformat()
                break
        
        # 保存更新后的歷史記錄
        try:
            with open('data/history.json', 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            print(f"已更新歷史記錄狀態: {schedule_id}")
        except Exception as e:
            print(f"更新歷史記錄失敗: {e}")
            return jsonify({"success": False, "error": "更新歷史記錄失敗"}), 500
        
        return jsonify({"success": True, "message": "排程已取消"})
    
    except Exception as e:
        print(f"取消排程時發生錯誤: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# 發送單一推播通知的函數
def send_notification(employee_id, amount, body_text, file_title):
    """
    發送單一推播通知
    
    Args:
        employee_id: 員工編號
        amount: 金額
        body_text: 推播內文文字
        file_title: 檔案標題為推播標題
    """
    try:
        # 構建 HTML 格式的推播內文
        html_body = f'''<!DOCTYPE html><html lang="zh-TW"><head><meta charset="UTF-8"><title>{file_title}</title><meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes"><style>body {{margin: 0;font-family: Arial, sans-serif;background-color: #f9f9f9;line-height: 1.6;color: #333;}}.content-wrap {{background-color: white;max-width: 800px;margin: 0 auto;padding: 16px;box-shadow: 0 2px 6px rgba(0,0,0,0.1);border-radius: 8px;}}.amount {{color: #008a00;font-weight: bold;}}a {{color:#0066cc;text-decoration:none;}}a:hover {{text-decoration:underline;}}@media (max-width: 600px) {{.content-wrap {{ padding: 12px; }}}}@media (min-width:601px) and (max-width:1024px) {{.content-wrap {{ padding: 20px; }}}}@media (min-width:1025px) {{.content-wrap {{ padding: 32px; }}}}</style></head><body><div class="content-wrap"> {body_text} <strong><span class="amount">{amount} 元</span>。</strong></div></body></html>'''
        
        # 推播訊息
        data = { 
            "title": file_title,
            "body": html_body,
            "type": "text",
            "bodyType": "html",
            "projects": ["Portal-APP"],
            "platforms": ["iOS", "Android"],
            "inbox": "user",
            "recipients": [employee_id]
        }
        
        # 增加 timeout 到 30 秒以應對大量推播時的延遲
        response = requests.post(API_URL, json=data, headers=HEADERS, timeout=30)
        
        # 檢查 HTTP 狀態碼
        if response.status_code >= 200 and response.status_code < 300:
            return {
                "employee_id": employee_id,
                "status_code": response.status_code,
           # "response": response.json(),
           # "message": response.json().get("message"),
                "success": True
            }
        else:
            # HTTP 錯誤狀態碼（4xx, 5xx）
            try:
                error_detail = response.json()
                error_message = error_detail.get('message', response.text)
            except:
                error_message = response.text
            
            return {
                "employee_id": employee_id,
                "status_code": response.status_code,
                "error": f"API 錯誤 {response.status_code}: {error_message}",
                "success": False
            }
    except requests.exceptions.Timeout:
        return {
            "employee_id": employee_id,
            "status_code": 408,
            "error": "請求超時（超過 30 秒）",
            "success": False
        }
    except requests.exceptions.RequestException as e:
        # 處理其他 requests 相關錯誤
        return {
            "employee_id": employee_id,
            "status_code": 500,
            "error": f"網路請求錯誤: {str(e)}",
            "success": False
        }
    except Exception as e:
        return {
            "employee_id": employee_id,
            "status_code": 500,
            "error": f"未預期的錯誤: {str(e)}",
            "success": False
        }

# 上傳excel檔案
@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.form)
    if 'file' not in request.files:
        return jsonify({"error": "無此檔案"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "沒有選擇檔案"}), 400

    # 檢查是否選擇了推播類型
    notification_type = request.form.get("notification_type")
    if not notification_type:  # 如果推播類型為空
        return jsonify({"error": "請選擇推播類型"}), 400

    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            # 讀取上傳的excel檔案 不儲存
            excel_data = pd.read_excel(file, sheet_name=None)
            
            # 擷取檔名
            file_title = os.path.splitext(file.filename)[0]
            
            # 定義推播內文文字
            text_mapping = {
                #"btext": "福利金已發放，您的福利金總金額為",
                "etext": "教育補助費已入帳，您的教育補助費總金額為",
                "ftext": "農曆春節禮金已發放，請至薪資帳戶查看，您的春節禮金總金額為"
            }
            
            # 驗證推播類型
            if notification_type not in text_mapping:
                return jsonify({"error": "無效的推播類型，請檢查excel格式"}), 400
            
            body_text = text_mapping[notification_type]
            
            # 使用 set 追蹤已處理的員工編號，避免重複推播
            processed_employees = set()
            
            # 收集所有需要發送的推播任務
            notification_tasks = []
            
            # 驗證 Excel 格式
            has_valid_sheet = False
            invalid_sheets = []
            
            # 抓取 Excel 中的員工編號及合計補助金額欄位
            for sheet_name, df in excel_data.items():
                # 檢查是否有員工編號欄位
                if '員工編號' not in df.columns:
                    invalid_sheets.append(f"工作表 '{sheet_name}': 缺少「員工編號」欄位")
                    continue
                
                # 檢查是否有金額欄位
                has_amount_column = False
                amount_column_name = None
                
                # 先統一處理員工編號格式（補0到6位數）
                df['員工編號'] = df['員工編號'].astype(str).str.strip().str.zfill(6)
                
                if '合計補助金額' in df.columns:
                    has_amount_column = True
                    amount_column_name = '合計補助金額'
                elif '禮金' in df.columns:
                    has_amount_column = True
                    amount_column_name = '禮金'
                
                if not has_amount_column:
                    invalid_sheets.append(f"工作表 '{sheet_name}': 缺少金額欄位（需要「合計補助金額」或「禮金」）")
                    continue
                
                # 標記為有效工作表
                has_valid_sheet = True

                # 抓取對應員工編號與補助金額
                for _, row in df.iterrows():
                    employee_id = row['員工編號']
                    amount = row.get('合計補助金額', row.get('禮金', None))

                    # 跳過無效資料
                    if not employee_id or pd.isna(amount):
                        continue
                    
                    # 檢查是否已經處理過此員工編號（避免重複）
                    if employee_id in processed_employees:
                        print(f"跳過重複的員工編號: {employee_id}")
                        continue
                    
                    # 標記為已處理
                    processed_employees.add(employee_id)
                    
                    # 添加到任務列表
                    notification_tasks.append({
                        'employee_id': employee_id,
                        'amount': amount,
                        'body_text': body_text,
                        'file_title': file_title
                    })
            
            # 檢查是否有有效的 Excel 格式
            if not has_valid_sheet:
                error_msg = "Excel 格式不正確！\n\n"
                error_msg += "必要欄位：\n"
                error_msg += "1. 員工編號\n"
                error_msg += "2. 金額欄位（合計補助金額 或 禮金）\n\n"
                
                if invalid_sheets:
                    error_msg += "問題詳情：\n" + "\n".join(invalid_sheets)
                else:
                    error_msg += "無法找到包含必要欄位的工作表。"
                
                return jsonify({"error": error_msg}), 400
            
            if not notification_tasks:
                return jsonify({"error": "Excel 中沒有有效的資料（所有員工編號或金額欄位都是空的）"}), 400
            
            print(f"準備發送 {len(notification_tasks)} 則推播通知...")
            
            # 檢查是否為排程推播
            is_scheduled = request.form.get("is_scheduled") == "true"
            schedule_date = request.form.get("schedule_date")
            schedule_time = request.form.get("schedule_time")
            
            if is_scheduled and schedule_date and schedule_time:
                # 排程推播邏輯
                try:
                    # 解析排程時間
                    schedule_datetime_str = f"{schedule_date}T{schedule_time}:00"
                    schedule_datetime = datetime.fromisoformat(schedule_datetime_str)
                    # 加上台灣時區
                    schedule_datetime = TAIWAN_TZ.localize(schedule_datetime)
                    
                    # 檢查排程時間是否在未來
                    now = datetime.now(TAIWAN_TZ)
                    if schedule_datetime <= now:
                        return jsonify({"error": "排程時間必須是未來的時間"}), 400
                    
                    # 生成唯一的排程 ID
                    schedule_id = f"schedule_{int(datetime.now().timestamp() * 1000)}"
                    
                    # 保存排程資料
                    add_scheduled_notification(
                        schedule_id=schedule_id,
                        notification_type=notification_type,
                        filename=file.filename,
                        schedule_datetime=schedule_datetime,
                        notification_tasks=notification_tasks
                    )
                    
                    # 註冊排程任務
                    scheduler.add_job(
                        execute_scheduled_notification,
                        trigger=DateTrigger(run_date=schedule_datetime),
                        args=[schedule_id],
                        id=schedule_id,
                        replace_existing=True
                    )
                    
                    print(f"\n========== 排程推播已建立 ==========")
                    print(f"排程ID: {schedule_id}")
                    print(f"預計執行時間: {schedule_datetime}")
                    print(f"排程任務數: {len(notification_tasks)}")
                    
                    # 立即創建歷史記錄（狀態為待發送）
                    from history import ensure_data_directory
                    ensure_data_directory()
                    history = load_history()
                    record = {
                        'id': len(history) + 1,
                        'schedule_id': schedule_id,
                        'timestamp': datetime.now(TAIWAN_TZ).isoformat(),
                        'notification_type': notification_type,
                        'filename': file.filename,
                        'is_scheduled': True,
                        'scheduled_time': schedule_datetime.isoformat(),
                        'status': 'pending',
                        'summary': {
                            'total': len(notification_tasks),
                            'success': 0,
                            'failed': 0
                        },
                        'details': []
                    }
                    history.append(record)
                    try:
                        with open('data/history.json', 'w', encoding='utf-8') as f:
                            json.dump(history, f, ensure_ascii=False, indent=2)
                        print(f"已創建歷史記錄: ID {record['id']}")
                    except Exception as e:
                        print(f"保存歷史記錄失敗: {e}")
                    
                    # 返回排程確認訊息
                    session['push_result'] = {
                        "message": f"推播已排程",
                        "summary": {
                            "scheduled": True,
                            "schedule_time": schedule_datetime.strftime("%Y-%m-%d %H:%M"),
                            "total": len(notification_tasks)
                        },
                        "responses": []
                    }
                    
                    return redirect(url_for('push_result'))
                    
                except Exception as e:
                    print(f"建立排程推播錯誤: {e}")
                    return jsonify({"error": f"排程推播錯誤: {str(e)}"}), 500
            else:
                # 即時推播邏輯（原有邏輯）
                responses = []
                max_workers = 10  # 可以根據 API 伺服器容量調整
                # 使用 ThreadPoolExecutor 進行並發發送
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # 提交所有任務
                    future_to_task = {
                        executor.submit(
                            send_notification,
                            task['employee_id'],
                            task['amount'],
                            task['body_text'],
                            task['file_title']
                        ): task for task in notification_tasks
                    }
                    
                    # 收集結果，將結果加到responses列表中
                    for future in as_completed(future_to_task):
                        task = future_to_task[future]
                        try:
                            result = future.result()
                            responses.append(result)
                            print(f"已發送推播給員工 {result['employee_id']}: 狀態碼 {result.get('status_code', 'N/A')}")
                        except Exception as e:
                            responses.append({
                                "employee_id": task['employee_id'],
                                "status_code": 500,
                                "error": f"執行錯誤: {str(e)}",
                                "success": False
                            })

                # 統計成功和失敗的數量
                success_count = sum(1 for r in responses if r.get('success', False))
                fail_count = len(responses) - success_count
                
                print(f"推播完成: 成功 {success_count} 則, 失敗 {fail_count} 則")
                
                # 保存歷史記錄
                save_history_record(
                    notification_type=notification_type,
                    filename=file.filename,
                    total=len(responses),
                    success=success_count,
                    failed=fail_count,
                    responses=responses
                )
                
                # 使用 session 保存推播結果，然後重定向（POST-Redirect-GET 模式）
                session['push_result'] = {
                    "message": "推播處理完成",
                    "summary": {
                        "total": len(responses),
                        "success": success_count,
                        "failed": fail_count
                    },
                    "responses": responses
                }
                
                # 重定向到結果頁面（避免重新整理重複提交）
                return redirect(url_for('push_result'))
            
        except Exception as e:
            print("Error during file processing:", e)
            return jsonify({"error": f"伺服器錯誤: {str(e)}"}), 500
    
    return jsonify({"error": "檔案必須為excel檔"}), 400
#測試機
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5002)