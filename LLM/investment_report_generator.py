#2.產生投資分析報告(先執行市場分析報告)
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
    
def generate_investment_prompt(role_prompt, market_report):
    return f"""
    你是一個資深的金融業者兼理專，請根據下面的金融市場分析報告做出完整專業且易於閱讀的一份投資分析報告:
    {market_report}
    {role_prompt}

    請遵守以下原則：
    1. 使用專業術語，並引用具體的數據或事件來支撐分析。
    2. 對每個投資建議進行具體說明，並解釋這些建議背後的邏輯。
    3. 提供每個結論的原因，並分析市場事件的影響。

    ----------------------------------------------------------------------------------------------------
    投資分析報告格式如下:
    投資分析報告
    投資摘要
    
    目錄
     1.投資環境概述
     2.投資組合建議
     3.風險管理策略
     4.市場展望(請詳細說明理由)
     5.投資總結
    
    1. 投資環境概述
        - 根據市場報告中的數據，詳細分析當前全球及本地市場的狀況。
        - 請特別關注具體的市場事件（例如貨幣政策變動、大型經濟事件等），並說明其對投資環境的影響。
  
        
    2. 投資組合建議
        - 提供針對保守型、穩健型和激進型投資者的具體投資組合建議。
        - **每個投資組合的資產配置比例**：請詳細說明為什麼選擇這樣的比重，並根據市場數據和事件來支撐這些選擇。
         例如：根據最近的市場波動，增加債券持倉可以有效對沖風險，因此保守型組合中債券占比提高至 60%，然後再詳細解釋由於Y所以XX配置Z%，以此類推。
  
    3. 風險管理策略
        - 提供具體的風險管理策略，並解釋每個策略背後的邏輯。
        - **詳細理由**：根據市場報告中的具體數據和事件，解釋這些策略為何能有效管理當前的市場風險。
        例如：考慮到近期央行政策可能引發市場波動，建議增加避險工具的使用，如選擇權。

    4. 市場展望
        - 根據技術面和基本面提供市場未來的趨勢預測。
        - 請引用具體事件和數據支持這些預測，並詳細解釋這些趨勢的原因和潛在影響。
        例如：由於 XXX 事件導致的供應鏈中斷，預期某行業會受到影響，這會導致短期內的價格波動。

    5. 投資總結
        - 概括總結主要的投資建議和市場前景。
        - 說明根據這些分析，如何對投資組合進行動態調整，以應對未來市場變化。
"""
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
    for role_key, role_prompt in role_prompts.items():
        market_report = read_market_report(role_key)
        prompt=generate_investment_prompt(role_prompt,market_report)
        investment_report = generate_report(prompt)
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
