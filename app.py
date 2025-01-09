from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import pandas as pd
import requests
import os

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

# .env 文件的路徑
dotenv_path = os.path.join(os.getcwd(), '.env')

# 載入 .env 文件
load_dotenv(dotenv_path=dotenv_path)
print("Loaded .env file :", os.path.abspath(dotenv_path))

# 讀取環境變數
# API_URL = os.getenv("PUSH_API_URL")
API_URL = os.getenv("PUSH_API_URL")
API_KEY = os.getenv("PUSH_API_KEY")
print("API_URL:", os.getenv("PUSH_API_URL"))

# 驗證環境變數是否存在
if not API_URL or not API_KEY:
    raise ValueError("沒有設定環境變數")

# 設置HEADERS
HEADERS = {
    "push-api-key": API_KEY,
    "Content-Type": "application/json"
}

@app.route("/")
@app.route('/index')
def index():
    return render_template('index.html')  #讀取html檔案

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
            # 指讀取上傳的excel檔案 不儲存
            excel_data = pd.read_excel(file, sheet_name=None)
            responses = []  #儲存API資訊

            # 擷取檔名
            file_title = os.path.splitext(file.filename)[0]

            # 抓取excel中的工作表中的員工編號及合計補助金額欄位
            for sheet_name, df in excel_data.items():
                if '員工編號' in df.columns and '合計補助金額' in df.columns:
                    df['員工編號'] = df['員工編號'].astype(str).str.zfill(6)
                elif '員工編號' in df.columns and '合計福利金額' in df.columns:
                    df['員工編號'] = df['員工編號'].astype(str).str.zfill(6)
                else:
                    df['員工編號'] = df['員工編號'].apply(lambda x: str(int(x)).zfill(6) if pd.notna(x) and str(x).strip() else '')# 去掉小數點補 0 至 6 碼
                
                # 判斷是否有對應的金額欄位
                    if '合計補助金額' in df.columns:
                        message_type = 'etext'
                        amount_column = '合計補助金額'
                        body_text = "教育補助費已入帳，您的教育補助費總金額為"
                    elif '合計福利金額' in df.columns:
                        message_type = 'btext'
                        amount_column = '合計福利金額'
                        body_text = "福利金已發放，您的福利金總金額為"
                    elif '禮金' in df.columns:
                        message_type = 'ftext'
                        amount_column = '禮金'
                        body_text = "福委會春節禮金已發放，請至薪資帳戶查看，總金額為"
                    else:
                        continue  # 無符合條件的金額欄位，跳過此工作表

                    # 依列進行推播
                    for _, row in df.iterrows():
                        employee_id = row['員工編號']

                        # 如果員工編號為空，停止處理
                        if not employee_id.strip():  # 判斷是否為空字串
                            print(f"遇到空白員工編號，停止處理工作表: {sheet_name}")
                            break  # 停止處理當前工作表 

                        amount = row.get(amount_column, 0)   
                        # 驗證推播類型
                        if notification_type != message_type:
                            continue

                        # 組建推播資料
                        data = {
                            "title": file_title,
                            "body": f"{body_text} {amount} 元。",
                            "type": "text",
                            "projects": ["Portal-APP"],
                            "platforms": ["iOS", "Android"],
                            "inbox": "user",
                            "recipients": [employee_id],  # 傳送推播使用者 ID
                        }

                        # 送出 API 推播
                        try:
                            response = requests.post(API_URL, json=data, headers=HEADERS)
                            responses.append({
                                "employee_id": employee_id,
                                "status_code": response.status_code,
                                "response": response.json(),
                                "message": response.json().get("message"),
                            })
                            print("Payload being sent:", data)
                            print("Response status code:", response.status_code)
                        except requests.exceptions.RequestException as e:
                            responses.append({
                                "employee_id": employee_id,
                                "error": str(e),
                            })

            return jsonify({"message": "成功送出", "response": responses}), 200
            
        except Exception as e:
            print("Error during file processing:", e) 
            return jsonify({"error": "伺服器錯誤，請稍後再試"}), 500
    
    return jsonify({"error": "檔案必須為excel檔"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)