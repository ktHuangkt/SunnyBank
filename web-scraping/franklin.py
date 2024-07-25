import pygsheets
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd



def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def fetch_page(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None
    return BeautifulSoup(driver.page_source, 'html.parser')

def extract_all_text(soup):
    texts = soup.stripped_strings
    return list(texts)

def parse_text_to_title_content(text_list):
    sections = ['美國股市', '美國債市', '歐洲', '亞洲', '中港台', '拉美', '黃金']
    parsed_data = []
    current_title = None
    current_content = []

    for text in text_list:
        if text in sections:
            if current_title and current_content:
                parsed_data.append((current_title, ' '.join(current_content)))
            current_title = text
            current_content = []
        else:
            current_content.append(text)
    
    if current_title and current_content:
        parsed_data.append((current_title, ' '.join(current_content)))
    
    return parsed_data

def save_to_google_sheets(parsed_data, key, url):
    try:
        gc = pygsheets.authorize(service_file=key)
        sh = gc.open_by_url(url)
        wks = sh.worksheet_by_title("工作表1")
        df = pd.DataFrame(parsed_data, columns=['Title', 'Content'])
        wks.clear()
        wks.set_dataframe(df, (1, 1))
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")

def main():
    url = "https://www.franklin.com.tw/dailynews/Daily_A.html"
    key = "web-scraping/kinetic-bot-429607-b2-83e041270035.json"
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1K-z5v8V_R7zhDpcEHMxUIk9P-J_hNnLT6MxTP_M4XAg/edit?gid=0#gid=0"
    
    driver = initialize_driver()
    try:
        soup = fetch_page(driver, url)
        if soup:
            all_texts = extract_all_text(soup)
            parsed_data = parse_text_to_title_content(all_texts)
            save_to_google_sheets(parsed_data, key, spreadsheet_url)
            print(parsed_data)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
