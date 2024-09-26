import pygsheets
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

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

    links = driver.find_elements(By.XPATH, "//a[@href]")
    return [link.get_attribute('href') for link in links if "https://www.moneydj.com/funddj/ya/yp050000.djhtm?a=" in link.get_attribute('href')]

def fetch_content(driver, href):
    driver.get(href)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "highlight")))

    title = driver.find_element(By.CSS_SELECTOR, "div.News-Head h1").text
    content = driver.find_element(By.ID, "highlight").text

    date_element = driver.find_element(By.XPATH, "//script[contains(text(), 'dateFunc.format')]")
    date_text = re.search(r"dateFunc.format\('(\d{4}/\d{2}/\d{2} \d{2}:\d{2})", date_element.get_attribute("innerHTML"))
    date = date_text.group(1) if date_text else "未知日期"

    end_markers = ["＊編者按：本文僅供參考之用", "圖片來源"]
    for marker in end_markers:
        content = content.split(marker)[0]

    content = re.sub(r"MoneyDJ新聞.*?報導", "", content, flags=re.DOTALL).strip()

    return title, content, date

def save_to_google_sheets(parsed_data, key, url):
    try:
        gc = pygsheets.authorize(service_file=key)
        sh = gc.open_by_url(url)
        wks = sh.worksheet_by_title("工作表1")
        df = pd.DataFrame(parsed_data, columns=['Title', 'Content', 'Date', 'Link'])
        wks.clear()
        wks.set_dataframe(df, (1, 1))
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")

def main():
    key = "web-scraping/kinetic-bot-429607-b2-61f6937a8283.json"
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1q-V1YhCWHiyRsizwr_Wlw8fvWESmOsG6C5sd4Yj6jKM/edit?usp=sharing"
    base_url = "https://www.moneydj.com/funddj/ya/YP051000.djhtm"

    driver = initialize_driver()

    try:
        hrefs = fetch_links(driver, base_url)
        parsed_data = []

        for href in hrefs:
            print(f"Processing link: {href}")
            title, content, date = fetch_content(driver, href)
            parsed_data.append({'Title': title, 'Content': content, 'Date': date, 'Link': href})

    finally:
        driver.quit()

    save_to_google_sheets(parsed_data, key, spreadsheet_url)

if __name__ == "__main__":
    main()
