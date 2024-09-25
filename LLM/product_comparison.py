#4.推薦產品
import os
import pandas as pd
from datetime import datetime
from fuzzywuzzy import process
from market_report_generator import generate_report

# 獲取今天的日期並格式化為字符串
today_date = datetime.now().strftime('%Y-%m-%d')

# 定義目錄路徑
base_dir = 'report_data'
today_dir = os.path.join(base_dir, today_date)

# 讀取 product_data.txt
with open(os.path.join(base_dir, "product_data.txt"), "r", encoding="utf-8") as file:
    product_data = file.read()

# 確保當日資料夾存在
if not os.path.exists(today_dir):
    raise FileNotFoundError(f"當日日期資料夾 {today_dir} 不存在")

# 讀取當日資料夾中的 intermediate_investment_report
report_path_investment = os.path.join(today_dir, "advanced_investment_report.txt")
if not os.path.exists(report_path_investment):
    raise FileNotFoundError(f"未找到當日的 intermediate_investment_report 文件在 {today_dir} 中")

with open(report_path_investment, "r", encoding="utf-8") as file:
    investment_report = file.read()

report_path_market = os.path.join(today_dir, "advanced_market_report.txt")
if not os.path.exists(report_path_market):
    raise FileNotFoundError(f"未找到當日的 advanced_market_report 文件在 {today_dir} 中")

with open(report_path_market, "r", encoding="utf-8") as file:
    market_report = file.read()

# print("產品:",product_data)
# print("投資分析告:",investment_report)

prompt=f"""你是一位資深的金融業者兼理專，下面是一份投資分析報告及產品資訊，請你比對市場分析報告、投資分析報告及產品資訊後，根據市場分析報告、投資分析報告推薦出前五名的產品(包括排序及推薦原因):

{market_report}
{investment_report}

產品資訊:
{product_data}

請遵循以下原則：
1.產品須按照排名由一到五排序且不得重複
2.透過闡述市場現況或使用具體數據（如報酬率、費用結構、風險等級）來強化推薦理由。
3.提供對市場狀況的具體觀察和分析，並解釋產品如何利用這些趨勢。
4.如果有必要，可以補充其他可能的投資分析依據、及其推薦產品並說明投資分析的背後因素以及推薦原因。
5.模擬市場上漲或下跌的情況下，基金可能的表現，並解釋這對投資者的好處。
6.避免使用模糊的詞語，具體說明產品如何產生回報或降低風險。

推薦產品需符合下面格式:
產品名稱:"content"
產品簡介:"content"
推薦原因:"content"

"""

top_5_product=generate_report(prompt)

gid = "1602496386"
sheet_id = "1bA6fSVgBbfmqcehUOez8yiWF_1IT_q7_flVPSrzP-So"
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}")

# 提取 Google Sheets 中的基金名称列表
fund_names = df['基金名稱'].tolist()

# 处理推荐产品和Google Sheets数据的比对
product_details = []
for line in top_5_product.splitlines():
    stripped_line = line.strip()  # 去除前后空格
    if "產品名稱:" in stripped_line:  # 使用 'in' 检查是否包含"產品名稱:"
        product_name = stripped_line.split(":")[1].strip().strip('"')
        # print(f"Searching for: {product_name}")
        
        # 使用 fuzzywuzzy 进行相似度匹配
        matches = process.extract(product_name, fund_names, limit=10)
        filtered_matches = [match for match in matches if match[1] >= 60]
        
        if filtered_matches:
            # 先找出得分最高的匹配项
            max_score = max(filtered_matches, key=lambda x: x[1])[1]
            highest_matches = [match for match in filtered_matches if match[1] == max_score]
            
            # 在得分相同的匹配项中，选择第一个出现的
            best_match = highest_matches[0]
            best_match_name, best_match_score = best_match
            
            matching_row = df[df['基金名稱'] == best_match_name].iloc[0]
            
            fund_info = {
                "基金名稱": product_name,
                "計價幣別": matching_row["計價幣別"],
                "風險報酬等級": matching_row["風險報酬等級"],
                "主要投資區域": matching_row["主要投資區域"],
                "三個月報酬率": matching_row["三個月(%)"],
                "六個月報酬率": matching_row["六個月(%)"],
                "一年報酬率": matching_row["一年(%)"],
                "連結": matching_row["基金名稱連結"]
            }
            
            # Debug: 打印基金信息
            # print("Fund Info:")
            # print(fund_info)
            
            product_details.append(fund_info)
        else:
            print(f"No match found for product name: {product_name}")
#输出产品详细信息
# print(product_details)

file_name = "top_5_product.txt"
file_path = os.path.join(today_dir, file_name)
with open(file_path, "w", encoding="utf-8") as file:
     for idx, line in enumerate(top_5_product.splitlines()):
        file.write(line + "\n")
        if "產品名稱:" in line:
            product_name = line.split(":")[1].strip().strip('"')
            for detail in product_details:
                if detail['基金名稱'] == product_name:
                    # 寫入基金詳細資料
                    file.write(f"計價幣別: {detail['計價幣別']}\n")
                    file.write(f"風險報酬等級: {detail['風險報酬等級']}\n")
                    file.write(f"主要投資區域: {detail['主要投資區域']}\n")
                    file.write(f"三個月報酬率: {detail['三個月報酬率']}%\n")
                    file.write(f"六個月報酬率: {detail['六個月報酬率']}%\n")
                    file.write(f"一年報酬率: {detail['一年報酬率']}%\n")
                    file.write(f"連結: {detail['連結']}\n")

print(f"合併結果已寫入 {file_path}")
