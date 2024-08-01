import requests
import certifi
from bs4 import BeautifulSoup
import pygsheets

def fetch_fund_data(url):
    """
    爬取網頁資料，並返回包含基金名稱、連結、公司名稱、連結、基金類別、連結的列表。
    """
    response = requests.get(url, verify=certifi.where())
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

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
    
    return data_list

def save_to_google_sheets(data, sheet_url, service_file, worksheet_index):
    """
    將資料保存到 Google Sheets。
    """
    try:
        gc = pygsheets.authorize(service_file=service_file)
        sheet = gc.open_by_url(sheet_url)
        worksheet = sheet[worksheet_index]
        header = ['基金名稱', '基金名稱連結', '基金公司', '基金公司連結', '基金類別', '基金類別連結']
        worksheet.update_row(1, header)
        
        flattened_data = [item for sublist in data for item in sublist]
        rows = [flattened_data[i:i+6] for i in range(0, len(flattened_data), 6)]
        worksheet.update_values('A2', rows)
        print("The data has been saved to Google Sheets.")
    
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")

def main():
    url = "https://fund.sunnybank.com.tw/w/wt/wt01List.djhtm?a=0&b=0&c=0~0&d=0~0&e=0~0&f=0~0&g=0~0&h=0~0&i=0&j=0~0&k=0&L=D&M=1"
    sheet_url = "https://docs.google.com/spreadsheets/d/1bA6fSVgBbfmqcehUOez8yiWF_1IT_q7_flVPSrzP-So/edit?gid=0#gid=0"
    service_file = 'web-scraping/cynes-key.json'
    
    data = fetch_fund_data(url)
    save_to_google_sheets(data, sheet_url, service_file, 0)

if __name__ == "__main__":
    main()
