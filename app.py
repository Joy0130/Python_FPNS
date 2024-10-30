from flask import Flask, render_template, request, jsonify,json
import os
import pandas as pd
import requests

app = Flask(__name__)
# config檔案設定
with open("config.json") as config_file:
    config = json.load(config_file)
    API_URL = config["PUSH_API_URL"]
    API_KEY = config["push-api-key"]
    if not API_URL or not API_KEY:
        raise ValueError("API URL or API Key is missing in config.json")

PUSH_API_URL = API_URL
HEADERS = {
    "push-api-key": API_KEY,
    "Content-Type": "application/json"
}


@app.route("/")
@app.route('/index')
def index():
    return render_template('index.html')  # Render HTML file

# 上傳excel檔
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "無此檔案"}), 400

    file = request.files.get('file')
    if file.filename == '':
        return jsonify({"error": "沒有選擇檔案"}), 400

    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            # 讀取excel檔
            excel_data = pd.read_excel(file, sheet_name=None)
            responses = []  # 儲存訊息
            file_title = os.path.splitext(file.filename)[0]  #取標題

            
            for sheet_name, df in excel_data.items():
                if '員工編號' in df.columns and '合計補助金額' in df.columns:
                    df['員工編號'] = df['員工編號'].astype(str).str.zfill(6)

                    
                    for _, row in df.iterrows():
                        employee_id = row['員工編號']
                        amount = row['合計補助金額']

                        # 推播通知
                        data = { 
                            "title": file_title,
                            "body": f"教育補助費已入帳，您的教育補助費合計金額為 {amount} 元。",
                            "type": "text",
                            "projects": ["Portal-APP"],
                            "platforms": ["iOS", "Android"],
                            "inbox": "user",
                            "recipients": [employee_id]
                        }

                        # response = requests.post(PUSH_API_URL, json=data, headers=HEADERS)

                        responses.append({
                            "employee_id": employee_id,
                        })

            
            return jsonify({"message": "成功送出", "response": responses}), 200

        except Exception as e:
            print("Error during file processing:", e) 
            return jsonify({"error": "伺服器錯誤，請稍後再試"}), 500

    return jsonify({"error": "檔案必須為excel檔"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
