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

                    # 抓取對應員工編號與補助金額
                    for _, row in df.iterrows():
                        employee_id = row['員工編號']
                        amount = row['合計補助金額']
                        etext = "教育補助費已入帳，您的教育補助費總金額為"
                        btext = "福利金已發放，您的福利金總金額為"

                        #根據推播類型來設定推播內文
                        if notification_type == "btext":
                            body_text = btext
                        elif notification_type == "etext":
                            body_text = etext
                        else:
                            return jsonify({"error": "無效的推播類型"}), 400  # 檢查無效值

                        # 推播訊息
                        data = { 
                            "title": file_title,
                            "body": f"{body_text} {amount} 元。",
                            "type": "text",
                            "projects": ["Portal-APP"],
                            "platforms": ["iOS", "Android"],
                            "inbox": "user",
                            "recipients": [employee_id]  # 傳送推播使用者ID
                        }
                        
                        # 送出API推播
                        response = requests.post(API_URL, json=data, headers=HEADERS)
                        responses.append({
                            "employee_id": employee_id,
                            "status_code": response.status_code, 
                            # "response": response.json(),
                            "message": response.json().get("message")
                        })
                        
                        print("Payload being sent:", data)
                        print("Response status code:", response.status_code)
                        #print("Response content:", response.content)

                return jsonify({"message": "成功送出", "response": responses}), 200
            
        except Exception as e:
            print("Error during file processing:", e) 
            return jsonify({"error": "伺服器錯誤，請稍後再試"}), 500
    
    return jsonify({"error": "檔案必須為excel檔"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)