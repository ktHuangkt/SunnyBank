import pandas as pd
import requests
import certifi
from bs4 import BeautifulSoup

def fetch_and_parse_tables(url):
    """
    下載網頁內容，解析 HTML，更新 input 標籤，並讀取 HTML 表格
    """
    # 下載網頁內容
    response = requests.get(url, verify=certifi.where())
    html_content = response.text

    # 使用 BeautifulSoup 解析 HTML 內容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找包含 name="sFundBuy" 的 input 標籤，並將其值設為1
    for td in soup.find_all('td'):
        input_tags = td.find_all('input', {'name': 'sFundBuy'})
        if input_tags:
            for input_tag in input_tags:
                if input_tag.get('value'):
                    input_tag.clear()
                    input_tag.append('1')

    # 使用 pandas 讀取 HTML 表格
    tables = pd.read_html(str(soup))
    
    return tables

def print_tables(tables):
    """
    印出提取的所有表格
    """
    for idx, table in enumerate(tables):
        print(f"表格 {idx}:\n", table)

def save_tables_to_excel(tables, filename):
    """
    將所有表格保存到一個 Excel 文件中
    """
    with pd.ExcelWriter(filename) as writer:
        for idx, table in enumerate(tables):
            table.to_excel(writer, sheet_name=f"表格 {idx}", index=False)

def main():
    url = "https://fund.sunnybank.com.tw/w/wt/wt01List.djhtm?a=0&b=0&c=0~0&d=0~0&e=0~0&f=0~0&g=0~0&h=0~0&i=0&j=0~0&k=0&L=D&M=1"
    
    # 下載、解析 HTML 內容並讀取表格
    tables = fetch_and_parse_tables(url)

    # 印出提取的所有表格
    print_tables(tables)

    # 保存表格到 Excel 文件
    save_tables_to_excel(tables, "fundTable.xlsx")

    print("表格已保存到 fundTable.xlsx")

if __name__ == "__main__":
    main()
