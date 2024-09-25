from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os


today_date = datetime.now().strftime('%Y-%m-%d')  # 獲取當天日期
base_dir = 'report_data'
today_dir = os.path.join(base_dir, today_date)

app = Flask(__name__,
            template_folder='C:/Users/User/Downloads/training_syscom/training_syscom',
            static_folder='C:/Users/User/Downloads/training_syscom/training_syscom')##路徑要改成自己的!!!

# 设置一个密钥用于会话管理
app.secret_key = 'QAQ'  # 这里使用一个独特的字符串

@app.route('/index')
def index():
    return render_template('index.html')

def parse_report(report):
    sections = report.split('\n\n')  # 根據段落分割報告
    parsed_report = []
    summary = ''
    
    for section in sections:
        lines = section.split('\n')
        title = lines[0].strip()

        # 判斷該段是否為摘要
        if '摘要' in title : 
            summary = '\n'.join(lines[1:]).strip()  # 將摘要提取出來
        else:
            content = '\n'.join(lines[1:]).strip()
            parsed_report.append({'report-title': title, 'report-content': content})

    return summary, parsed_report

@app.route('/market')
def market():
    user_role = session.get('role', 'beginner')  # 从会话中获取角色，默认值为 'beginner'
    market_report = read_report_from_file('market', user_role)  # 根据角色读取市场报告
    
    # 解析報告內容
    summary, report_sections = parse_report(market_report)  # 將報告分割成摘要與其他部分
    
    return render_template('market.html', 
                           summary=summary,        # 傳遞摘要
                           report=report_sections,  # 傳遞其他報告部分
                           date=today_date)

@app.route('/investment')
def investment():
    user_role = session.get('role', 'beginner')  # 从会话中获取角色，默认值为 'beginner'
    investment_report = read_report_from_file('investment', user_role)  # 根据角色读取投资报告

    summary, report_sections = parse_report(investment_report)  # 將報告分割成摘要與其他部分
    
    return render_template('investment.html', 
                           summary=summary,        # 傳遞摘要
                           report=report_sections,  # 傳遞其他報告部分
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

@app.route('/get_products')
def get_products_route():
    file_path = os.path.join(today_dir, 'top_5_product.txt')

    product_names = []

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # print(f"Line read: {line}")  # 输出读取的每一行
                stripped_line = line.strip()  # 去除前后空格
                if "產品名稱:" in stripped_line:  # 使用 'in' 检查是否包含"產品名稱:"
                    product_name = stripped_line.split(":")[1].strip().strip('"')
                    product_names.append(product_name)
                    
        print(product_names)
    return jsonify(product_names)

@app.route('/fund_details')
def fund_details_route():
    file_path = os.path.join(today_dir, 'top_5_product.txt')
    fund_details = []  # 用於存儲解析後的基金資料
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            current_fund = {}
            for line in file:
                stripped_line = line.strip()
                
                # 如果是新基金的開始，並且 current_fund 不為空，則將其加入列表
                if stripped_line and stripped_line[0].isdigit() and stripped_line[1] == '.':
                    if current_fund:
                        fund_details.append(current_fund)
                    current_fund = {}  # 初始化新的基金資料
                
                # 處理基金資料的具體內容
                if '產品名稱:' in stripped_line:
                    current_fund['產品名稱'] = stripped_line.split(':', 1)[1].strip().strip('"')
                elif '計價幣別:' in stripped_line:
                    current_fund['計價幣別'] = stripped_line.split(':', 1)[1].strip()
                elif '風險報酬等級:' in stripped_line:
                    current_fund['風險報酬等級'] = stripped_line.split(':', 1)[1].strip()
                elif '主要投資區域:' in stripped_line:
                    current_fund['主要投資區域'] = stripped_line.split(':', 1)[1].strip()
                elif '三個月報酬率:' in stripped_line:
                    current_fund['三個月報酬率'] = stripped_line.split(':', 1)[1].strip()
                elif '六個月報酬率:' in stripped_line:
                    current_fund['六個月報酬率'] = stripped_line.split(':', 1)[1].strip()
                elif '一年報酬率:' in stripped_line:
                    current_fund['一年報酬率'] = stripped_line.split(':', 1)[1].strip()
                elif '連結:' in stripped_line:
                    current_fund['連結'] = stripped_line.split(':', 1)[1].strip()
                elif '產品簡介:' in stripped_line:
                    current_fund['產品簡介'] = stripped_line.split(':', 1)[1].strip()
                elif '推薦原因:' in stripped_line:
                    current_fund['推薦原因'] = stripped_line.split(':', 1)[1].strip()

            # 將最後一個基金加入列表
            if current_fund:
                fund_details.append(current_fund)
    
    # print(fund_details)

    # 將解析出的基金資料轉換為 JSON 格式並返回給前端
    return jsonify(fund_details)

if __name__ == '__main__':
    app.run(debug=True)
