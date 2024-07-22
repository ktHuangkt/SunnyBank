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


client = AzureOpenAI(
  azure_endpoint = azure_endpoint, 
  api_key=api_key,  
  api_version=api_version
)

# 定義 prompt
prompt = f"""
你是一個資深的金融業者，根據以下幾篇新聞做出完整且專業的市場分析報告:

{data}
"""

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

response_text = response.choices[0].message.content

# 計算 tokens
encoding = tiktoken.get_encoding("cl100k_base")
tokens = encoding.encode(prompt)
num_tokens = len(tokens)

print(f"Prompt tokens count: {num_tokens}")
# 顯示回應
print(response_text)