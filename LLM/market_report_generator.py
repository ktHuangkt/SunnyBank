#1.產生市場分析報告
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

# Google Sheets的GID
gid = "0"

anue_sheet_id="1IOifGkDYhug5YskqwSoFNi70hkZnppy76uNor52-_HE"
anue_df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{anue_sheet_id}/export?format=csv&gid={gid}")

MoneyDJ_sheet_id="1q-V1YhCWHiyRsizwr_Wlw8fvWESmOsG6C5sd4Yj6jKM"
MoneyDJ_df=pd.read_csv(f"https://docs.google.com/spreadsheets/d/{MoneyDJ_sheet_id}/export?format=csv&gid={gid}")

Franklin_sheet_id="1K-z5v8V_R7zhDpcEHMxUIk9P-J_hNnLT6MxTP_M4XAg"
Franklin_df=pd.read_csv(f"https://docs.google.com/spreadsheets/d/{Franklin_sheet_id}/export?format=csv&gid={gid}")


# 提取当天数据的 title 和 content
data = ""
anue_data=""
MoneyDJ_data=""
Franklin_data=""

for index, row in anue_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    anue_data += f"新聞標題: {title}  內容: {content}\n\n"

for index, row in MoneyDJ_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    MoneyDJ_data += f"新聞標題: {title}  內容: {content}\n\n"

for index, row in Franklin_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    Franklin_data += f"\n國際股債市焦點:\n標題: {title}  內容: {content}\n\n"

data = anue_data + MoneyDJ_data + Franklin_data

# 不同角色 prompt
role_prompts = {
    "beginner": "報告對象為投資新手(投資經驗在5年以內)，故報告內請儘量不要包含專業術語，而是以相對容易理解、簡潔的方式，描述並解釋各種市場現象。",
    "intermediate": "報告對象為投資老手(投資經驗在5年至15年)，他對於財報中各項指標的意義和市場走向有基本的了解。",
    "advanced": "報告對象為投資高手(投資經驗在15年以上)，他對於金融市場非常了解。報告內可含有一些公司營運相關數據、指標，如果有報導中有列出實際數字的話(例如: 營收突破3億)請在報告中列出實際數字。"
}

def generate_market_prompt(role_prompt, data):
    return f"""
你是一個資深的金融業者兼理專，根據以下幾篇新聞生成一份完整專業且易於閱讀的金融市場分析報告：
{data}
{role_prompt}


### 請根據以下原則生成報告

### 請確保文章內容具體，避免模糊的表述。提供具體的數據、指標、趨勢分析。例如，替代 "我們見證了一系列的高潮與低谷" 這種抽象語句，應該更具體描述實際的市場波動，如 "美股在過去三個月內出現了5%的下跌幅度，其中科技股跌幅最大，尤其是XX公司下降了8%"。

### 用詞請盡量專業豐富，文章的評論需要具體且有深度分析，並且提供具體市場事件和數據支持。


### 請根據上述新聞內容以及原則，生成一份如下格式的金融市場分析報告：
    金融市場分析報告
    摘要
### 摘要請特別指出本期報告的重點以及一些濃縮的內容

    目錄
      1.經濟概況
      2.股票市場分析
      3.債券市場分析
      4.外匯市場分析
      5.大宗商品市場分析
      6.投資建議
    目錄
      1.經濟概況
      2.股票市場分析
      3.債券市場分析
      4.外匯市場分析
      5.大宗商品市場分析
      6.投資建議

      
### 請引用具體的數據來支撐每個市場的分析，特別是股票市場、債券市場和大宗商品市場，並且提供具體的價格變化和趨勢。結論部分請根據數據給出有深度的見解。
### 請特別注意每一段的結構應該是(引用事件)->(加入事件相對的數據)->導致甚麼樣的結果

經濟概況：
"請詳細描述由於XXX原因，所以造成市場經濟概況的YYY影響"，例如:"如果要描述由於通脹率上升和能源價格波動，市場經濟概況的顯著變化。就會是，美國的通脹率從4.2%上升到5.1%，而能源成本增加了12%，這給消費者支出帶來了壓力。"

股票市場分析：
"請提供具體數據和趨勢，例如：
標普500指數(或是任何指數)下跌了X%，其背後原因為Y和Z。"
例如：納斯達克指數下跌了X%，其背後原因為Y和Z。
例如：納斯達克指數在上個季度下跌了4.5%，其中科技股的跌幅最大，尤其是半導體行業的銷售疲軟導致跌幅達到6%。"

債券市場分析：
"提供具體收益率和走勢分析，
例如：美國國債收益率上升了X個基點，主要因為Y。"

外匯市場分析：
"具體描述不同貨幣對的動態，
例如：美元兌日元升值X%，原因是Y和Z。
例如：美元兌英鎊匯率下降了1.8%，這是因為英國央行加息的預期增強，吸引了更多資金流入英國市場。"

大宗商品市場分析
"分析內容：提供具體價格趨勢和供需分析，
例如：原油價格上漲了X%，原因是Y和Z。
例如：黃金價格在過去一個月內上漲了3%，由於投資者尋求避險資產來應對全球市場的波動。"

投資建議：
建議投資者關注XXX，因為Y和Z。"

    結論：
"請根據以上提到的資訊給出實際結論，請不要講得太籠統或是只給一個太大的方向"

###請嚴格遵照1~7的格式排版，謝謝!

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

if __name__ == "__main__":
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
        prompt = generate_market_prompt(role_prompt, data)

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
