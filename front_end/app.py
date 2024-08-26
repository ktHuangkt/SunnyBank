from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os


today_date = datetime.now().strftime('%Y-%m-%d')  # 獲取當天日期
base_dir = 'report_data'
today_dir = os.path.join(base_dir, today_date)

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

@app.route('/get_news')
def get_news_route():
    file_path = os.path.join(today_dir, 'top_5_news.txt')

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            news_content = file.read()

        # 解析文本内容到 JSON 格式
        news_items = []
        items = news_content.strip().split('\n\n')
        for item in items:
            lines = item.split('\n')
            if len(lines) >= 2:
                title_line = lines[0].strip()
                link_line = lines[1].strip()
                title = title_line.replace('標題: ', '')
                link = link_line.replace('連結: ', '')
                news_items.append({
                    'title': title,
                    'link': link
                })

        return jsonify(news_items)
    else:
        return jsonify({'error': 'News file not found'}), 404

@app.route('/get_views')
def get_views():
    user_role = session.get('role', 'beginner')
    print(f"Fetching views for role from session: {user_role}")
    file_path = os.path.join(today_dir, f"{user_role}_views.txt")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            views = file.read()
        return jsonify({"views": views})
    else:
        return jsonify({"error": "File not found"}), 404

def read_report_from_file(report_type, role_key):
    file_name = f"{role_key}_{report_type}_report.txt"
    file_path = os.path.join(today_dir, file_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return "報告未找到"

if __name__ == '__main__':
    app.run(debug=True)
