import pygsheets
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def fetch_links(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    links = driver.find_elements(By.CSS_SELECTOR, "li.mediaCard a.mediaCard-mediaContainer")
    hrefs = [link.get_attribute('href') for link in links]
    return hrefs

def fetch_content(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    try:
        title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.heading-2')))
        title = title_element.text

        date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.template-content-insight-date')))
        date = date_element.text

        content_elements = driver.find_elements(By.CSS_SELECTOR, 'div.editor > p')
        content = "\n".join([element.text for element in content_elements])

        return title, content, date
    except Exception as e:
        print(f"Error fetching content for {url}: {e}")
        return "Error", "", ""

def save_to_google_sheets(parsed_data, key, url):
    try:
        gc = pygsheets.authorize(service_file=key)
        sh = gc.open_by_url(url)
        wks = sh.worksheet_by_title("工作表1")
        df = pd.DataFrame(parsed_data, columns=['標題', '內容', '日期', '連結'])
        wks.clear()
        wks.set_dataframe(df, (1, 1))
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")

def main():
    key = "C:\SunnyBank\web-scraping\kinetic-bot-429607-b2-83e041270035.json"
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1nXt0kzBeVODvqmCVn914YdtqmEPNz5b83OITAHVNd7Q/edit?gid=0#gid=0"
    base_url = "https://www.fhtrust.com.tw/insights_list/article_list/views"

    driver = initialize_driver()

    try:
        hrefs = fetch_links(driver, base_url)
        parsed_data = []

        for href in hrefs:
            print(f"Processing link: {href}")
            title, content, date = fetch_content(driver, href)
            parsed_data.append({'標題': title, '內容': content, '日期': date, '連結': href})

    finally:
        driver.quit()

    save_to_google_sheets(parsed_data, key, spreadsheet_url)

if __name__ == "__main__":
    main()
