from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
# import market_report_generator
# import investment_report_generator

app = Flask(__name__,
            template_folder='C:/Users/User/Downloads/training_syscom/training_syscom',
            static_folder='C:/Users/User/Downloads/training_syscom/training_syscom')

# 设置一个密钥用于会话管理
app.secret_key = 'QAQ'  # 这里使用一个独特的字符串

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/market')
def market():
    today_date = datetime.now().strftime('%Y/%m/%d')  # 獲取當天日期
    user_role = session.get('role', 'beginner')  # 从会话中获取角色，默认值为 'beginner'
    market_report = read_report_from_file('market', user_role)  # 根据角色读取市场报告
    return render_template('market.html', 
                           report=market_report,
                           date=today_date)

@app.route('/investment')
def investment():
    today_date = datetime.now().strftime('%Y/%m/%d')  # 獲取當天日期
    user_role = session.get('role', 'beginner')  # 从会话中获取角色，默认值为 'beginner'
    investment_report = read_report_from_file('investment', user_role)  # 根据角色读取投资报告
    return render_template('investment.html',
                           report=investment_report,
                           date=today_date)

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/set_role', methods=['POST'])
def set_role():
    data = request.get_json()  # 获取 JSON 数据
    user_role = data.get('role')
    session['role'] = user_role  # 将角色存储到会话中
    print(f"Received role: {user_role}")  # 打印接收到的角色
    return jsonify({'status': 'success', 'role': user_role})

def read_report_from_file(report_type, role_key):
    today_date = datetime.now().strftime('%Y-%m-%d')  # 獲取當天日期
    base_dir = 'report_data'
    today_dir = os.path.join(base_dir, today_date)
    file_name = f"{role_key}_{report_type}_report.txt"
    file_path = os.path.join(today_dir, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return "報告未找到"

if __name__ == '__main__':
    app.run(debug=True)
