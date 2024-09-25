##產品收斂
import pandas as pd
import tiktoken
import re
import os
from market_report_generator import generate_report

sheet_id="1oHPQJ3A9Cb5CHdgAKcK8YQtAd_ga8X2HqmqZBrdZhAY" ##簡式公開說明書
# Google Sheets的GID
gid = "0"
product_df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}")

# # 选择每20笔数据中的一条（20, 40, 60, ...），并获取前10条
# sampled_df = product_df.iloc[19::20].head(10)

# 定义清理文本的函数
def clean_text(text):
    # 去除后面的「1\n」或其他非内容相关部分
    text = re.sub(r'\s*[\d\W]+\s*$', '', text)
    return text.strip()

# 处理每一笔数据并生成报告
product_data = ""

for index, row in product_df.iterrows():
    content = row["PDF 內容"] 
    cleaned_content = clean_text(content)  # 清理文本

    # 创建完整的提示
    prompt = f"""將下面產品整理成以下格式(2. - 4. 皆用一句話總結)(沒有資料的部分寫'文件中未提供相關資料'):

    1. 產品名稱:"content"
    2. 投資特色:"content"
    (投資特色包括基金的投資策略、主要投資標的（如股票、債券、或其他資產）、地區或行業的集中度等。)
    3. 基金風險等級:"content"
    4. 基金績效:"content"
    5. 費用:"content"
    (費用(基金的費用結構包括管理費、銷售費等。))
    
    
    {cleaned_content}
    """
    
    # 调用生成报告函数
    product = generate_report(prompt)
    
    # 将生成的报告添加到 product_data 中
    product_data += f"{product}\n\n"

print(product_data)

# 初始化 tiktoken 的编码器，选择 gpt-4 对应的编码器
tokenizer = tiktoken.get_encoding("cl100k_base")

# 计算 token 数
def count_tokens(text):
    tokens = tokenizer.encode(text)
    return len(tokens)

# 计算 product_data 的 token 数
product_data_token_count = count_tokens(product_data)

print(f"Token 数量: {product_data_token_count}")

# 保存生成的 product_data 到文件中
output_directory = "report_data"

# 如果目录不存在，则创建
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# 定义文件路径
output_file = os.path.join(output_directory, "product_data.txt")

# 将 product_data 写入文件
with open(output_file, "w", encoding="utf-8") as file:
    file.write(product_data)

print(f"生成的 product_data 已保存在 {output_file}")


