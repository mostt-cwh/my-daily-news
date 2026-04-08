import os
import requests
import xml.etree.ElementTree as ET
from google import genai

# 1. 初始化 Client (強制指定 API 版本)
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options={'api_version': 'v1'}
)

# 2. 抓取新聞 (維持原樣，這部分你已經做得很好)
def get_real_news():
    rss_url = "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    try:
        response = requests.get(rss_url, timeout=10)
        root = ET.fromstring(response.content)
        return [{"title": i.find('title').text, "link": i.find('link').text} for i in root.findall('./channel/item')[:3]]
    except:
        return []

real_news = get_real_news()

# 3. 強化版總結邏輯
def summarize_content(text):
    # 嘗試列表，包含 Gemini 和可能的 Gemma API 名稱
    test_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    
    last_err = ""
    for m in test_models:
        try:
            # 加上 config 確保不使用預設的 v1beta
            response = client.models.generate_content(
                model=m, 
                contents=f"請用 80 字內廣東話總結這新聞重點：{text}"
            )
            return response.text, m
        except Exception as e:
            last_err = str(e)
            continue
    return f"暫時無法連線 AI。錯誤：{last_err}", "None"

summaries_html = ""
for news in real_news:
    summary, used_model = summarize_content(news['title'])
    summaries_html += f"""
    <div class="card">
        <h3>{news['title']}</h3>
        <p>{summary}</p>
        <div style="font-size:0.7em; color: #bbb;">AI: {used_model}</div>
        <a href="{news['link']}" target="_blank">閱讀原文 →</a>
    </div>
    """

# 4. 生成 HTML
html_content = f"""
<html>
<head>
    <title>AI 每日新聞</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto; background: #f9f9f9; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 12px; border: 1px solid #eee; }}
        h1 {{ color: #1a73e8; text-align: center; }}
        a {{ color: #1a73e8; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>🗞️ 私人 AI 報紙</h1>
    {summaries_html}
    <p style="text-align:center; color:#999; font-size:0.8em;">最後更新：{os.popen('date').read()}</p>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
