import os
import google.generativeai as genai

# 1. 設定 AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# 2. 模擬抓取新聞 (這裡可以進階寫爬蟲，現在先設定示範文字)
news_list = [
    "新聞 1: 科技業最新發展...",
    "新聞 2: 全球氣候變化報告...",
    "新聞 3: 體育賽事精華..."
]

# 3. 讓 AI 總結
summaries = []
for news in news_list:
    response = model.generate_content(f"請用 50 字以內廣東話/中文總結這則新聞：{news}")
    summaries.append(response.text)

# 4. 產生 HTML 檔案
html_content = f"""
<html>
<head><title>我的每日新聞</title><meta charset="utf-8"></head>
<body>
    <h1>📅 每日 AI 新聞總結</h1>
    <ul>
        <li>{summaries[0]}</li>
        <li>{summaries[1]}</li>
        <li>{summaries[2]}</li>
    </ul>
    <p>最後更新時間：{os.popen('date').read()}</p>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
