import tiktoken
from openai import AzureOpenAI
from training_config import *
import pandas as pd
import json
import market_report_generator

market_report=market_report_generator.market_report

prompt=f"""你是一個資深的金融業者兼理專，請根據下面的金融市場分析報告做出完整專業且易於閱讀的一份投資分析報告:

{market_report}

投資分析報告格式如下:
投資分析報告
投資摘要

目錄
 1.投資環境概述
 2.投資組合建議
 3.風險管理策略
 4.市場展望
 5.投資總結

1.投資環境概述
 "內容"
2.投資組合建議(條列式)
 "內容(ex:保守型、穩健型、激進型，各類型投資組合占比)"
3.風險管理策略(條列式)
 "內容"
4.市場展望(條列式)
 "內容"
5.投資總結
 "內容"
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

investment_report = response.choices[0].message.content

# # 計算 tokens
# encoding = tiktoken.get_encoding("cl100k_base")
# tokens = encoding.encode(prompt)
# num_tokens = len(tokens)
# print(f"Prompt tokens count: {num_tokens}")

# # 顯示回應
print(investment_report)
