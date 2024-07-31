import requests
import certifi
from bs4 import BeautifulSoup
import pygsheets

# Google sheets authorization
gc = pygsheets.authorize(service_file='web-scraping/cynes-key.json')
sheet_url = "https://docs.google.com/spreadsheets/d/1bA6fSVgBbfmqcehUOez8yiWF_1IT_q7_flVPSrzP-So/edit?gid=0#gid=0"
sheet = gc.open_by_url(sheet_url)

worksheet = sheet[0]
header = ['基金名稱', '基金名稱連結', '基金公司', '基金公司連結', '基金類別', '基金類別連結']

worksheet.update_row(1, header)

# 下载网页内容
url = "https://fund.sunnybank.com.tw/w/wt/wt01List.djhtm?a=0&b=0&c=0~0&d=0~0&e=0~0&f=0~0&g=0~0&h=0~0&i=0&j=0~0&k=0&L=D&M=1"
response = requests.get(url, verify=certifi.where())
html_content = response.text

# 使用 BeautifulSoup 解析 HTML 内容
soup = BeautifulSoup(html_content, 'html.parser')

# 查找包含 name="sFundBuy" 的 input 標籤，再從其所在行的前三個包含 a 標籤的 td 元素中提取鏈接和文本內容
data_list = []
for input_tag in soup.find_all('input', {'name': 'sFundBuy'}):
    parent_tr = input_tag.find_parent('tr')
    if parent_tr:
        td_elements = parent_tr.find_all('td')
        row_data = []
        a_count = 0
        for td in td_elements:
            link = td.find('a')
            if link and a_count < 3:
                href = "https://fund.sunnybank.com.tw" + link.get('href', '')
                text = link.text.strip()
                row_data.extend([text, href])
                a_count += 1
            if a_count == 3:
                break
        if row_data:
            data_list.append(row_data)

# 输出数据列表
print(data_list)

'''
# 将数据从A2单元格开始插入到Google Sheets中
worksheet.update_values('A2', data_list)
'''
# 将列表展开为一个平面列表
flattened_data = [item for sublist in data_list for item in sublist]

# 将平面列表重新组织成按行的列表
rows = [flattened_data[i:i+6] for i in range(0, len(flattened_data), 6)]

# 将数据从A2单元格开始插入到Google Sheets中
worksheet.update_values('A2', rows)
