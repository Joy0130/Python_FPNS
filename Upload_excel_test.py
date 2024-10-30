from flask import Flask, render_template,request,redirect,url_for
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/path/to/upload'  # Define the upload folder path
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
@app.route('/index')
def index():
    return render_template('index.html')  # 透過 render_template 函數載入 HTML

@app.route("/upload", methods=['POST'])
def upload_file():

    file = request.files['file']  

    if 'file' not in request.files:
        return "無此檔案"
    
    file = request.files['file']
    if file.filename == '':
        return "沒有選擇檔案"
    
    #儲存上傳的excel 到 sheets.html中

    if file:
        filename = file.filename
        secure_name = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
        file.save(file_path)

        # 讀取excel檔
        excel_data = pd.read_excel(file_path, sheet_name=None)

         # 工作表
        for sheet_name, df in excel_data.items():
            # 在員工編號欄位未滿6位前面自動補0
            df['員工編號'] = df['員工編號'].astype(str).str.zfill(6)
        
        sheets = {sheet_name: df.to_html() for sheet_name, df in excel_data.items()}

        return render_template('sheets.html',filename=filename,sheets=sheets)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)