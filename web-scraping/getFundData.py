import pandas as pd
import pygsheets
import requests
import certifi
from io import StringIO
from bs4 import BeautifulSoup
import time

# 設置Google Sheets API憑證
credentials_file = 'web-scraping/cynes-key.json'

# 取得pygsheets客戶端
client = pygsheets.authorize(service_file=credentials_file)

# 打開包含網址的Google Sheets
url = 'https://docs.google.com/spreadsheets/d/1bA6fSVgBbfmqcehUOez8yiWF_1IT_q7_flVPSrzP-So/edit?gid=0#gid=0'  # 包含網址的Google Sheets的連結
sheet = client.open_by_url(url)
urls_sheet = sheet[0]
data_sheet = sheet[1]

# 取得B2:B1124範圍的網址
urls = urls_sheet.get_values(start='B2', end='B1124')
urls = [url[0] for url in urls]  # 將多維列表轉換為單維列表

# 用於存儲所有網址的數據
all_data = []
last_row = 1

# 遍歷每個網址
batch_size = 10
for i in range(0, len(urls), batch_size):
    batch_urls = urls[i:i+batch_size]
    batch_data = []
    
    for url in batch_urls:
        # 使用 requests 獲取頁面內容，同時使用 certifi 提供的證書
        response = requests.get(url, verify=certifi.where())
        
        # 確保請求成功
        response.raise_for_status()
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 找到所有 class="wfb5l" 的元素
        elements = soup.find_all(class_="wfb5l")
        
        # 提取元素的文本並添加到列表中
        url_data = [element.get_text(strip=True) for element in elements]
        batch_data.append(url_data)
    
    # 批量寫入 Google Sheets
    data_sheet.insert_rows(last_row, values=batch_data)
    last_row += len(batch_data)
    # print("已寫入第"+str(last_row-batch_data)+"~"+str(last_row)+"行\n")
    
    # 添加延遲以避免 API 限制
    time.sleep(2)