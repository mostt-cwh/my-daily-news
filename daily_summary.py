import os
from google import genai

# 1. 設定 AI (使用最新的 google-genai 庫)
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. 模擬抓取新聞
news_list = [
    "新聞 1: 科技業最新發展，AI 算力需求持續攀升。",
    "新聞 2: 全球氣候變化報告顯示，今年夏季氣溫可能創紀錄。",
    "新聞 3: 體育賽事精華：本地足球隊奪得聯賽冠軍。"
]

# 3. 讓 AI 總結
summaries = []
for news in news_list:
    # 使用目前最快且免費的 gemini-1.5-flash 或 gemini-2.0-flash
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=f"請用 50 字以內廣東話/中文總結這則新聞：{news}"
    )
    summaries.append(response.text)

# 4. 產生 HTML 檔案
html_content = f"""
<html>
<head>
    <title>我的每日新聞</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto; background: #f4f4f9; }}
        .card {{ background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>📅 每日 AI 新聞總結</h1>
    <div class="card">{summaries[0]}</div>
    <div class="card">{summaries[1]}</div>
    <div class="card">{summaries[2]}</div>
    <hr>
    <p style="font-size: 0.8em; color: #666;">最後更新時間：{os.popen('date').read()}</p>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
