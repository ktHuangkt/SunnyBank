import datetime as dt
import requests
import json
import csv
from bs4 import BeautifulSoup
import pygsheets
import time
import html
import re

# Google sheets authorization
gc = pygsheets.authorize(service_file='web-scraping/cynes-key.json')
sheet_url = "https://docs.google.com/spreadsheets/d/1IOifGkDYhug5YskqwSoFNi70hkZnppy76uNor52-_HE/edit?gid=0#gid=0"
sheet = gc.open_by_url(sheet_url)

worksheet = sheet.sheet1
header = ['Title', 'Content', 'Link', 'PublishAt']
worksheet.update_row(1, header)

cnyes_api = "https://api.cnyes.com/media/api/v1/newslist/category/tw_stock"
params = {
  "startAt": int((dt.datetime.today()-dt.timedelta(days=1)).timestamp()), 
  "endAt": int(dt.datetime.today().timestamp()),
  "limit": 30
}

response = requests.get(url=cnyes_api, params=params)
data_dict = response.json()

news_data = []
if data_dict.get('items') and data_dict['items'].get('data'):
    for item in data_dict['items']['data']:
        title = item.get('title', 'No title')
        
        content = item.get('content', 'No content') # News content
        _text = html.unescape(content)
        pattern = "<.*?>|\n|&[a-z0-9]+;|http+"
        clean_content = re.sub(pattern, "", _text)

        newsId = item.get('newsId', 'No link')
        
        keyword = item.get('keyword', 'No keyword')

        publishAt = item.get('publishAt', 'No publish time')
        
        news_data.append({
            'title': title,
            'content': clean_content,
            'link': "https://news.cnyes.com/news/id/" + str(newsId),
            'keyword': keyword,
            'publishAt': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(publishAt))
        })

'''
# Save to json file
with open("anue.json", "w", encoding="utf8") as file:
    json.dump(news_data, file, indent=2, sort_keys=True, ensure_ascii=False)

# Save to csv file
csv_file = "anue.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['title', 'content', 'link', 'keyword', 'publishAt'])
    writer.writeheader()
    for news_item in news_data:
        writer.writerow(news_item)
'''
# Save to gsheet
rows = [[item['title'], item['content'], item['link'], item['publishAt']] for item in news_data]
worksheet.update_row(index=2, values=rows)

# print("Success!")