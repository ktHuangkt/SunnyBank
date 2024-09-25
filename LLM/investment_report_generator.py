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
    你是一位資深的金融分析師，根據以下金融市場分析報告，撰寫一份專業且易於理解的投資分析報告：
    {market_report}
    {role_prompt}

    請嚴格遵守以下原則：
    1. 使用精確的專業術語，並引用具體的市場數據或重大事件來支撐分析和建議，內容須盡量詳細。
    2. 每項投資建議需清晰且詳細說明其背後的邏輯和原因。
    3. 提供針對保守型、穩健型和激進型投資者的具體投資組合建議，並根據不同市場情況，解釋如何調整這些配置。

    ----------------------------------------------------------------------------------------------------
    投資分析報告格式如下(請嚴格遵守報告格式):

    摘要
    "摘要請特別指出本期報告的重點以及一些濃縮的內容"

    1. 投資環境概述:
    "- 根據市場報告中的數據，詳細分析當前全球及本地市場的狀況。
    - 特別關注具體的市場事件（如貨幣政策變動、大型經濟事件等），並說明其對投資環境的影響。"

    2. 投資組合建議:
    "- 針對保守型、穩健型和激進型投資者，提供具體且量化的投資組合建議。
    - 資產配置比例說明：詳細解釋為何選擇這些比例，並基於市場數據或事件（例如央行政策變動、經濟指標走勢等）支持這些選擇。
    例如：因應近期市場波動，對保守型投資者增加債券持倉，以降低波動風險，因此建議債券占比提高至60%。請解釋該配置的背景和預期效果。
    - 市場情境下的調整建議：考慮到不同市場情境，針對每種投資組合提供潛在的動態調整策略。"

    3. 風險管理策略:
    "- 提供具體且針對性的風險管理策略，並解釋其背後的邏輯。
    - 詳細原因：根據市場報告中的數據和事件，解釋這些策略為何有效。"

    4. 市場展望:
    "- 根據技術分析和基本面提供市場未來的趨勢預測。
    - 引用具體事件和數據支持預測，並詳細解釋這些趨勢的原因和潛在影響。"

    5. 投資總結:
    "- 概括總結主要的投資建議和市場前景。
    - 說明如何根據分析結果動態調整投資組合，以應對未來市場變化。"

"""


def extract_key_points_and_tips(investment_report):
    return f"""
    {role_prompt}
    請將投資組合建議依照每種類型的投資者（保守型、穩健型、激進型）進行排列，格式如下：

    1. 保守型投資者
       - 資產配置比例："列出資產配置比例。"
       - 配比緣由："解釋每個資產配置的緣由。"

    2. 穩健型投資者
       - 資產配置比例："列出資產配置比例。"
       - 配比緣由："解釋每個資產配置的緣由。"

    3. 激進型投資者
       - 資產配置比例："列出資產配置比例。"
       - 配比緣由："解釋每個資產配置的緣由。"

    投資組合建議如下：
    {investment_report}

    如果有必要，請補充動態調整建議和其他可能的市場情境分析。
    
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
        prompt = generate_investment_prompt(role_prompt, market_report)
        investment_report = generate_report(prompt)

        # 保存原始投資報告
        file_name = f"{role_key}_investment_report.txt"
        file_path = os.path.join(today_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(investment_report)
        print(f"Investment report saved to: {file_path}")

        # 整理成重點節錄和tips格式
        prompt_for_summary = extract_key_points_and_tips(investment_report)
        summarized_report = generate_report(prompt_for_summary)

        # 保存整理後的報告
        summarized_file_name = f"{role_key}_investment_summary.txt"
        summarized_file_path = os.path.join(today_dir, summarized_file_name)
        with open(summarized_file_path, "w", encoding="utf-8") as file:
            file.write(summarized_report)
        print(f"Summarized report saved to: {summarized_file_path}")

# # 計算 tokens
# encoding = tiktoken.get_encoding("cl100k_base")
# tokens = encoding.encode(prompt)
# num_tokens = len(tokens)
# print(f"Prompt tokens count: {num_tokens}")

# # 顯示回應
# print(investment_report)
