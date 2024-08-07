import tiktoken
from openai import AzureOpenAI
from training_config import *
import pandas as pd
import json
import os
from datetime import datetime
from market_report_generator import generate_report, role_prompts

client = AzureOpenAI(
  azure_endpoint = azure_endpoint, 
  api_key=api_key,  
  api_version=api_version
)

# 獲取今天的日期並格式化為字符串
today_date = datetime.now().strftime('%Y-%m-%d')

def read_market_report(role_key):
    file_path = os.path.join(today_dir, f"{role_key}_market_report.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
    
def generate_investment_report(market_report):
    prompt = f"""
    你是一個資深的金融業者兼理專，請根據下面的金融市場分析報告做出完整專業且易於閱讀的一份投資分析報告:
    
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
    2.投資組合建議
     "內容(條列式)(ex:保守型、穩健型、激進型，各類型投資組合占比)"
    3.風險管理策略
     "內容(條列式)"
    4.市場展望
     "內容(條列式)"
    5.投資總結
     "內容"
    """
    
    return generate_report(prompt)

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

    # 生成并保存不同角色的投資報告
    for role_key in role_prompts.keys():
        market_report = read_market_report(role_key)
        investment_report = generate_investment_report(market_report)
        file_name = f"{role_key}_investment_report.txt"
        file_path = os.path.join(today_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(investment_report)
        print(f"Investment report saved to: {file_path}")

# # 計算 tokens
# encoding = tiktoken.get_encoding("cl100k_base")
# tokens = encoding.encode(prompt)
# num_tokens = len(tokens)
# print(f"Prompt tokens count: {num_tokens}")

# # 顯示回應
# print(investment_report)
