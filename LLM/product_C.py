
import tiktoken
from openai import AzureOpenAI
from training_config import *
import pandas as pd
import json
import re
sheet_id="1TnWHPH16OaFkONSYdJeL6BmwdSh4OPeyU4kWjmtX22g"
# Google Sheets的GID
gid = "0"
df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}")


# 定義一個函數來清理每一行的文本
def clean_text(text):
    # 去除後面的「1\n」或其他非內容相關部分
    text = re.sub(r'\s*[\d\W]+\s*$', '', text)
    return text.strip()

data = ""
for index, row in df[0:10].iterrows():
    content = row["PDF 內容"]
    data += f"PDF內容: {content}\n\n"



text="""金融市場分析報告

摘要：
本報告綜合分析了當前全球金融市場的經濟概況、股票市場、債券市場、外匯市場以及大宗商品市場的動態，並提供針對不同市場的投資建議。透過對各項市場指標的深入分析，旨在為投資者提供一個全面的市場視角，幫助投資者做出更明智的投資決策。

目錄：
1. 經濟概況
2. 股票市場分析
3. 債券市場分析
4. 外匯市場分析
5. 大宗商品市場分析
6. 投資建議

1. 經濟概況：
全球經濟面臨多重挑戰，包括通膨壓力、地緣政治緊張、以及可能的經濟衰退風險。美國就業市場顯示經濟衰退的預兆，而中東地區的緊張局勢可能進一步加劇全球經濟的不確定性。

2. 股票市場分析：
- 全球股票市場受到美國經濟數據不佳和地緣政治緊張的影響，呈現下跌趨勢。
- 台股因外資大量賣出，出現斷崖式下跌，但也出現反彈的機會。

3. 債券市場分析：
- 全球債券市場反映出市場對於經濟衰退的擔憂，主要國家的債券收益率呈現下降趨勢。
- 台灣外匯存底減少，反映出外資流出的壓力。

4. 外匯市場分析：
- 美元在全球經濟不確定性中保持強勢。
- 日圓因日本央行政策調整而升值，影響了全球資金流動。

5. 大宗商品市場分析：
- 能源價格受到中東地區緊張局勢的影響，呈現上漲趨勢。
- 黃金作為避險資產，在市場不確定性中價格上漲。

6. 投資建議：
- 股票市場：建議投資者關注具有強勁基本面的公司，並保持靈活的投資策略。
- 債券市場：建議投資者增加對高信用評級債券的配置，以降低風險。
- 外匯市場：建議投資者關注主要貨幣對的動態，並適時調整外匯風險。
- 大宗商品市場：建議投資者可透過黃金等避險資產來分散投資組合的風險。

結論：
面對當前全球金融市場的多重挑戰，投資者應保持謹慎，並根據市場變化調整投資策略。透過深入分析市場動態，投資者可以更好地把握投資機會，並有效管理風險。"
"""

# print(text)


# 不同角色 prompt
role1 = "報告對象為投資新手(投資經驗在1年以內)，故報告內請儘量不要包含專業術語，而是以相對容易理解、簡潔的方式，描述並解釋各種市場現象。"
role2 = "報告對象為投資老手(投資經驗在1年至5年)，他對於財報中各項指標的意義和市場走向有基本的了解。"
role3 = "報告對象為投資高手(投資經驗在5年以上)，他對於金融市場非常了解。報告內可含有一些公司營運相關數據、指標，如果有報導中有列出實際數字的話(例如: 營收突破3億)請在報告中列出實際數字。"


# 定義 prompt
prompt = f"""
你是一位資深的金融業者兼理財顧問。我將提供一份詳細的金融市場分析報告和所有的基金產品信息。請根據這些信息，製作一份完整、專業且易於閱讀的基金產品排名報告。報告內容包括：
1.基金產品的推薦程度評分，0分為最不推薦，100分為最推薦。
2.根據金融市場分析報告中的內容，詳細說明每個基金產品排名的依據。
3.請確保報告內容清晰、結構化，易於客戶理解和使用
4.說明評分的標準，是如何將產品量化成分數:
{role2}
{data}
{text}
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

# 計算 tokens
encoding = tiktoken.get_encoding("cl100k_base")
tokens = encoding.encode(prompt)
num_tokens = len(tokens)
print(f"Prompt tokens count: {num_tokens}")

# 顯示回應
print(market_report)


# f.write(market_report)
# f.close()
  