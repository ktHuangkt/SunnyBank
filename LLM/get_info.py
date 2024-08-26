#產生首頁資訊(前五條新聞、觀點摘要)
import pandas as pd
import re
import os
from market_report_generator import generate_report, anue_df, MoneyDJ_df, Franklin_df, role_prompts
from datetime import datetime


today_date = datetime.now().strftime('%Y-%m-%d')

link_data=""

for index, row in anue_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    link=row["Link"]
    link_data += f"新聞標題: {title}  內容: {content}  連結: {link}\n\n"

for index, row in MoneyDJ_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    link=row["Link"]
    link_data += f"新聞標題: {title}  內容: {content}  連結: {link}\n\n"

data=""

for index, row in anue_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    data += f"新聞標題: {title}  內容: {content}\n\n"

for index, row in MoneyDJ_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    data += f"新聞標題: {title}  內容: {content}\n\n"

for index, row in Franklin_df.iterrows():
    title = row["Title"]
    content = row["Content"]
    data += f"\n國際股債市焦點:\n標題: {title}  內容: {content}\n\n"


#新聞排名前五
def get_news():

    prompt=f"""你是一個資深的金融業者兼理專,從下列新聞中列出對金融市場及投資來說最重要的五篇新聞(內容不重複)，
    請符合下面格式"標題: ,連結: ":
    {link_data}
    """
    news=generate_report(prompt)
    # print("Returned news data:", news)  # 添加这行代码以调试
    news_items = []
    pattern = r"標題: (.+?)\s*, 連結: (https://[^\s]+)"
    matches = re.findall(pattern, news)

    for title, link in matches:
        news_items.append({
            'title': title,
            'link': link
        })

    return news_items

def save_news(news_items, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in news_items:
            f.write(f"標題: {item['title']}\n")
            f.write(f"連結: {item['link']}\n\n")


#多方觀點摘要
def view_prompt(role_prompt, data):
    return f"""你是一個資深的金融業者兼理專,根據以下幾篇新聞及各類資產表現從多個角度進行分析和摘要，
    {role_prompt}
    {data}

    以下是一些可以考慮的觀點：
    1.市場趨勢
    2.個股表現與行業動態
    3.風險管理
    4.投資機會
    5.市場情緒
    6.宏觀經濟影響

    摘要請符合下面格式:

    市場趨勢 : 內容

    個股表現與行業動態 : 內容
    
    風險管理 : 內容
    
    投資機會 : 內容
    
    市場情緒 : 內容
    
    宏觀經濟影響 : 內容

    """

def save_views():
    for role_key, role_prompt in role_prompts.items():
        prompt=view_prompt(role_prompt,data)
        views=generate_report(prompt)
        file_name = f"{role_key}_views.txt"
        views_file_path = os.path.join(today_dir, file_name)
        with open(views_file_path, "w", encoding="utf-8") as file:
            file.write(views)
        print(f"Investment report saved to: {views_file_path}")


#國際股債市焦點

if __name__ == "__main__":
    # 定義報告目錄和當天的資料夾路徑
    base_dir = 'report_data'
    today_dir = os.path.join(base_dir, today_date)

    # 如果資料夾不存在，則創建它
    if not os.path.exists(today_dir):
        os.makedirs(today_dir)
        print(f"Created directory: {today_dir}")
    else:
        print(f"Directory already exists: {today_dir}")

    news_items = get_news()
    news_file_path = os.path.join(today_dir, 'top_5_news.txt')
    save_news(news_items, news_file_path)
    print(f"Saved top 5 news to: {news_file_path}")

    save_views()