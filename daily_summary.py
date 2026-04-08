import os
import requests
import xml.etree.ElementTree as ET
from google import genai

# 1. 設定 AI
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options={'api_version': 'v1'}
)

# 2. 真正抓取 Google 新聞 (香港繁體中文)
def get_real_news():
    rss_url = "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    
    news_items = []
    # 只取前 3 條新聞
    for item in root.findall('./channel/item')[:3]:
        title = item.find('title').text
        link = item.find('link').text
        news_items.append({"title": title, "link": link})
    return news_items

# 執行抓取
real_news = get_real_news()

# 3. 讓 AI 總結
summaries_html = ""
for news in real_news:
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=f"請用 80 字以內廣東話/中文總結這則新聞的重點，並加入適當的 Emoji：{news['title']}"
        )
        summary_text = response.text
        summaries_html += f"""
        <div class="card">
            <h3>{news['title']}</h3>
            <p>{summary_text}</p>
            <a href="{news['link']}" target="_blank">閱讀原文 →</a>
        </div>
        """
    except Exception as e:
        summaries_html += f"<div class='card'>總結失敗: {str(e)}</div>"

# 4. 產生 HTML 檔案
html_content = f"""
<html>
<head>
    <title>AI 每日新聞精選</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; padding: 20px; max-width: 700px; margin: auto; background: #f0f2f5; color: #1c1e21; }}
        h1 {{ text-align: center; color: #007bff; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); transition: transform 0.2s; }}
        .card:hover {{ transform: translateY(-5px); }}
        .card h3 {{ margin-top: 0; font-size: 1.2em; color: #333; }}
        .card p {{ color: #444; font-size: 1em; }}
        .card a {{ color: #007bff; text-decoration: none; font-weight: bold; font-size: 0.9em; }}
        .footer {{ text-align: center; font-size: 0.8em; color: #888; margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>🤖 AI 每日新聞總結</h1>
    {summaries_html}
    <div class="footer">最後更新時間 (UTC)：{os.popen('date').read()}</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
