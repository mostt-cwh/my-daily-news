import os
import requests
import xml.etree.ElementTree as ET
from google import genai

# 1. 初始化 Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. 抓取新聞
def get_real_news():
    rss_url = "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    try:
        response = requests.get(rss_url, timeout=10)
        root = ET.fromstring(response.content)
        return [{"title": i.find('title').text, "link": i.find('link').text} for i in root.findall('./channel/item')[:3]]
    except:
        return []

real_news = get_real_news()

# 3. AI 總結邏輯 (嘗試多個模型版本)
def ask_gemini(prompt):
    # 這裡列出你想嘗試的模型，按優先順序排列
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            return response.text, model_name # 回傳總結內容和使用的模型名
        except Exception:
            continue # 如果失敗，嘗試下一個
    return "所有模型均暫時無法使用", "None"

summaries_html = ""
for news in real_news:
    summary_text, used_model = ask_gemini(f"請用 80 字內廣東話總結這新聞重點並加 Emoji：{news['title']}")
    summaries_html += f"""
    <div class="card">
        <h3>{news['title']}</h3>
        <p>{summary_text}</p>
        <div style="font-size:0.7em; color: #bbb;">Powered by {used_model}</div>
        <a href="{news['link']}" target="_blank">閱讀原文 →</a>
    </div>
    """

# 4. 生成 HTML (其餘樣式保持不變)
html_content = f"""
<html>
<head>
    <title>AI 每日新聞</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto; background: #f4f7f6; }}
        .card {{ background: white; padding: 15px; margin-bottom: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        h1 {{ color: #2c3e50; text-align: center; }}
        a {{ color: #3498db; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>🗞️ AI 每日新聞 (Gemini 驅動)</h1>
    {summaries_html}
    <p style="text-align:center; color:#999; font-size:0.8em;">更新時間：{os.popen('date').read()}</p>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
