import requests
import certifi
from bs4 import BeautifulSoup
import pygsheets
import logging
import pyautogui
import time
import pyperclip  # 用於訪問剪貼簿內容
import webbrowser

# 設置日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def authorize_google_sheets(service_file):
    """
    授權訪問 Google Sheets
    """
    return pygsheets.authorize(service_file=service_file)

def get_urls_from_sheet(sheet_url, service_file, column_index=2):
    """
    從 Google Sheets 中讀取指定列的所有網址
    """
    gc = authorize_google_sheets(service_file)
    spreadsheet = gc.open_by_url(sheet_url)
    worksheet = spreadsheet.sheet1
    return worksheet.get_col(column_index)[1:1123]  # 只讀取前3個網址，跳過第一行標題

def fetch_webpage(url):
    """
    爬取網頁內容
    """
    try:
        response = requests.get(url, verify=certifi.where())
        response.raise_for_status()  # 如果請求不成功，拋出 HTTPError
        return response.content
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve the webpage: {url}, error: {e}")
        return None

def parse_simple_prospectus_link(content):
    """
    解析網頁內容，提取 "簡式公開說明書" 的連結
    """
    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a', string="簡式公開說明書")
    if links:
        return links[0]['href']
    else:
        logging.info("No '簡式公開說明書' link found.")
    return None

def open_pdf_and_copy_content(pdf_url):
    """
    使用系統瀏覽器打開PDF文件，並用pyautogui複製內容
    """
    try:
        webbrowser.open(pdf_url)
        time.sleep(10)  # 等待PDF加載完成

        pyautogui.hotkey('ctrl', 'a')  # 全選
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'c')  # 複製
        time.sleep(1)

        pyautogui.hotkey('alt', 'f4')  # 關掉視窗
        
        pdf_text = pyperclip.paste()  # 獲取剪貼簿內容
        return pdf_text
    except Exception as e:
        logging.error(f"Failed to open and copy PDF content from {pdf_url}, error: {e}")
        return None

def save_to_google_sheet(data, sheet_url, service_file):
    """
    將數據保存到 Google Sheet 中
    """
    gc = authorize_google_sheets(service_file)
    spreadsheet = gc.open_by_url(sheet_url)
    worksheet = spreadsheet.sheet1
    worksheet.clear()  # 清空表格
    worksheet.update_values('A1', data)  # 更新數據

def main():
    # 讀取網址的 Google Sheets 的 URL 和認證文件
    read_sheet_url = "https://docs.google.com/spreadsheets/d/1bA6fSVgBbfmqcehUOez8yiWF_1IT_q7_flVPSrzP-So/edit?gid=0#gid=0"
    read_service_file = 'web-scraping/cynes-key.json'

    # 保存結果的 Google Sheets 的 URL 和認證文件
    save_sheet_url = "https://docs.google.com/spreadsheets/d/1oHPQJ3A9Cb5CHdgAKcK8YQtAd_ga8X2HqmqZBrdZhAY/edit?gid=0#gid=0"
    save_service_file = 'web-scraping/kinetic-bot-429607-b2-83e041270035.json'

    # 讀取 B 列的前三個網址
    urls = get_urls_from_sheet(read_sheet_url, read_service_file)

    # 爬取每個網址並處理 "簡式公開說明書" 的 PDF
    results = [["URL", "PDF 內容"]]
    for url in urls:
        if url:
            logging.info(f"Processing URL: {url}")
            content = fetch_webpage(url)
            if content:
                simple_prospectus_link = parse_simple_prospectus_link(content)
                if simple_prospectus_link:
                    logging.info(f"簡式公開說明書連結: {simple_prospectus_link}")
                    # 打開PDF網址並複製內容
                    pdf_text = open_pdf_and_copy_content(simple_prospectus_link)
                    if pdf_text:
                        results.append([simple_prospectus_link, pdf_text])
                        # 將結果保存到 Google Sheets
                        save_to_google_sheet(results, save_sheet_url, save_service_file)
                    else:
                        logging.info(f"無法讀取PDF內容: {simple_prospectus_link}")
                else:
                    logging.info(f"簡式公開說明書連結未找到 in {url}")



if __name__ == "__main__":
    main()
