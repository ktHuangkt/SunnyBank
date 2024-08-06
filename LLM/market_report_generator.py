import tiktoken
from openai import AzureOpenAI
from training_config import *
import pandas as pd
import json
import os
from datetime import datetime

# 配置 Azure OpenAI API
client = AzureOpenAI(
  azure_endpoint = azure_endpoint, 
  api_key=api_key,  
  api_version=api_version
)

# 獲取今天的日期並格式化為字符串
today_date = datetime.now().strftime('%Y-%m-%d')

sheet_id="1IOifGkDYhug5YskqwSoFNi70hkZnppy76uNor52-_HE"
# Google Sheets的GID
gid = "0"
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}")

# 筛选出当天的数据
df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')  # 将日期列转换为字符串格式
df_today = df[df['Date'] == today_date]

# 提取当天数据的 title 和 content
data = ""
for index, row in df_today.iterrows():
    title = row["Title"]
    content = row["Content"]
    data += f"新聞標題: {title}  內容: {content}\n\n"


# 不同角色 prompt
role_prompts = {
    "beginner": "報告對象為投資新手(投資經驗在5年以內)，故報告內請儘量不要包含專業術語，而是以相對容易理解、簡潔的方式，描述並解釋各種市場現象。",
    "intermediate": "報告對象為投資老手(投資經驗在5年至15年)，他對於財報中各項指標的意義和市場走向有基本的了解。",
    "advanced": "報告對象為投資高手(投資經驗在15年以上)，他對於金融市場非常了解。報告內可含有一些公司營運相關數據、指標，如果有報導中有列出實際數字的話(例如: 營收突破3億)請在報告中列出實際數字。"
}

def generate_prompt(role_prompt, data):
    return f"""
    你是一個資深的金融業者兼理專，根據以下幾篇新聞做出完整專業且易於閱讀的一份金融市場分析報告並且市場分析報告要利於專員產生投資分析報告(旨在超越市場上的其他報告，並為投資決策提供有價值的參考):
    {role_prompt}
    {data}

    根據上述新聞內容，生成一份如下格式的金融市場分析報告：
    金融市場分析報告
    摘要

    目錄
      1.經濟概況
      2.股票市場分析
      3.債券市場分析
      4.外匯市場分析
      5.大宗商品市場分析
      6.投資建議

    1.經濟概況
     "內容"
    2.股票市場分析(條列式)
     "
     全球股票市場:...
     地區市場分析:...
     "
    3.債券市場分析(條列式)
     "
     全球債券市場：...
     主要債券市場：
     "
    4.外匯市場分析(條列式)
     "內容(ex:美元、歐元、日幣...)"
    5.大宗商品市場分析(條列式)
     "內容(ex:能源、金屬、農產品...)"
    6.投資建議(條列式)
     "內容(ex:股票、債券、外匯...)"

    結論
    """

# 定义生成报告的函数
def generate_report(prompt):

    # 使用Azure ChatGPT產生回應
    message_text = [
        {"role": "system", "content": "你是一個資深的金融業者"},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=message_text,
        temperature=0,
        max_tokens=4096,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    return response.choices[0].message.content

# 定義報告目錄和當天的資料夾路徑
base_dir = 'report_data'
today_dir = os.path.join(base_dir, today_date)

# 如果資料夾不存在，則創建它
if not os.path.exists(today_dir):
    os.makedirs(today_dir)
    print(f"Created directory: {today_dir}")
else:
    print(f"Directory already exists: {today_dir}")

# 生成并保存不同角色的报告
for role_key, role_prompt in role_prompts.items():
    prompt = generate_prompt(role_prompt, data)
    report = generate_report(prompt)
    file_name = f"{role_key}_market_report.txt"
    file_path = os.path.join(today_dir, file_name)
    # 將報告寫入文件
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(report)
    
    print(f"Report saved to: {file_path}")


# # 計算 tokens
# encoding = tiktoken.get_encoding("cl100k_base")
# tokens = encoding.encode(prompt)
# num_tokens = len(tokens)
# print(f"Prompt tokens count: {num_tokens}")

# # 顯示回應
# print(response_text)

 
  