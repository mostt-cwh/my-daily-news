import os
import requests
import xml.etree.ElementTree as ET
from google import genai

# 1. 設定 AI - 移除 api_version 強制設定，讓 SDK 自己選最適合的
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. 真正抓取 Google 新聞
def get_real_news():
    rss_url = "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    try:
        response = requests.get(rss_url, timeout=10)
        root = ET.fromstring(response.content)
        news_items = []
        for item in root.findall('./channel/item')[:3]:
            title = item.find('title').text
            link = item.find('link').text
            news_items.append({"title": title, "link": link})
        return news_items
    except Exception as e:
        return [{"title": f"抓取新聞失敗: {str(e)}", "link": "#"}]

real_news = get_real_news()

# 3. 讓 AI 總結 - 切換到 2.0 版本，這是目前 2026 年最主流的模型
summaries_html = ""
for news in real_news:
    try:
        # 如果 gemini-2.0-flash 還是不行，這段 try-except 會捕捉它
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=f"請用 80 字以內廣東話/中文總結這則新聞重點：{news['title']}"
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
        summaries_html += f"<div class='card'>總結失敗，錯誤碼：{str(e)}</div>"

# 4. 產生 HTML 檔案
html_content = f"""
<html>
<head>
    <title>AI 每日新聞精選</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; padding: 20px; max-width: 700px; margin: auto; background: #f5f7fa; color: #333; }}
        h1 {{ text-align: center; color: #1a73e8; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .card h3 {{ margin-top: 0; font-size: 1.1em; }}
        .footer {{ text-align: center; font-size: 0.8em; color: #999; margin-top: 30px; }}
    </style>
</head>
<body>
    <h1>🤖 AI 每日新聞總結</h1>
    {summaries_html}
    <div class="footer">更新時間：{os.popen('date').read()}</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
