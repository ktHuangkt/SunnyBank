import pandas as pd
import requests
import certifi
from bs4 import BeautifulSoup
import pygsheets

# 配置 Google Sheets API token
gc = pygsheets.authorize(service_account_file='web-scraping/cynes-key.json')

# 打開要寫入的 Google Sheet
#spreadsheet = gc.open('')
sheet_url = "https://docs.google.com/spreadsheets/d/1IOifGkDYhug5YskqwSoFNi70hkZnppy76uNor52-_HE/edit?gid=0#gid=0"
spreadsheet = gc.open_by_url(sheet_url)
worksheet = spreadsheet[1]  # 或者使用 spreadsheet[0] 選擇第一張表


# 下載網頁内容
url = "https://fund.sunnybank.com.tw/w/wt/wt01List.djhtm?a=0&b=0&c=0~0&d=0~0&e=0~0&f=0~0&g=0~0&h=0~0&i=0&j=0~0&k=0&L=D&M=1"
response = requests.get(url, verify=certifi.where())
html_content = response.text

# 使用 BeautifulSoup 解析 HTML 内容
soup = BeautifulSoup(html_content, 'html.parser')

# 查找包含 name="sFundBuy" 的 input 標籤，並值設為1
for td in soup.find_all('td'):
    input_tags = td.find_all('input', {'name': 'sFundBuy'})
    if input_tags:
        for input_tag in input_tags:
            if input_tag.get('value'):
                input_tag.clear()
                input_tag.append('1')
        '''
        print(input_tags)
        input_tags.clear()  # 清除 td 中的所有内容
        input_tags.append('1')  # 添加新的内容
        '''

# 使用 pandas 讀取 HTML 表格
tables = pd.read_html(str(soup))

# 印出提取的所有表格
for idx, table in enumerate(tables):
    print(f"Table {idx}:\n", table)

'''
# 遍歷所有表格
for idx, table in enumerate(tables):
    # 写入到 Google Sheet，逐行写入
    for i, row in table.iterrows():
        worksheet.append_table(row.tolist())

print("Tables have been saved to Google Sheet")

'''

# 將所有表格保存到一個 Excel 文件中
with pd.ExcelWriter("fundTable.xlsx") as writer:
    for idx, table in enumerate(tables):
        table.to_excel(writer, sheet_name=f"Table {idx}", index=False)

print("Tables have been saved to fundTable.xlsx")
