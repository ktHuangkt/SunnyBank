import tiktoken
from openai import AzureOpenAI
from training_config import *
import pandas as pd
import json

sheet_id="1IOifGkDYhug5YskqwSoFNi70hkZnppy76uNor52-_HE"
# Google Sheets的GID
gid = "0"
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}")
# 提取每一行的 title 和 content
data = ""
for index, row in df.iterrows():
    title = row["Title"]
    content = row["Content"]
    data += f"新聞標題: {title}  內容: {content}\n\n"

# 顯示純文本數據
#print(data)



# 定義 prompt
prompt = f"""
你是一個資深的金融業者兼理專，根據以下幾篇新聞做出完整專業且易於閱讀的一份金融市場分析報告並且市場分析報告要利於專員產生投資分析報告(旨在超越市場上的其他報告，並為投資決策提供有價值的參考):

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


client = AzureOpenAI(
  azure_endpoint = azure_endpoint, 
  api_key=api_key,  
  api_version=api_version
)
message_text =[
        {"role": "system", "content": "你是一個資深的金融業者"},
        {"role": "user", "content": prompt}
    ]

# 使用Azure ChatGPT產生回應
response = client.chat.completions.create(
  model=model_name,
  messages = message_text,
  temperature=0,
  max_tokens=4096,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None
)

market_report = response.choices[0].message.content

# # 計算 tokens
# encoding = tiktoken.get_encoding("cl100k_base")
# tokens = encoding.encode(prompt)
# num_tokens = len(tokens)
# print(f"Prompt tokens count: {num_tokens}")

# # 顯示回應
# print(response_text)

 
  