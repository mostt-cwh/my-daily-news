import os
import requests
import xml.etree.ElementTree as ET
from google import genai

# 1. 初始化 Client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 2. 自動偵測可用的模型 (不再盲猜名稱)
def get_available_model():
    try:
        # 列出所有你可以使用的模型
        for model in client.models.list():
            # 優先找 flash 等級的模型，速度快且免費
            if "generateContent" in model.supported_methods:
                if "flash" in model.name:
                    return model.name
        return "models/gemini-1.5-flash" # 保底
    except Exception as e:
        print(f"無法列出模型: {e}")
        return "models/gemini-1.5-flash"

selected_model = get_available_model()
print(f"系統自動選擇模型: {selected_model}")

# 3. 抓取新聞
def get_real_news():
    rss_url = "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    try:
        response = requests.get(rss_url, timeout=10)
        root = ET.fromstring(response.content)
        return [{"title": i.find('title').text, "link": i.find('link').text} for i in root.findall('./channel/item')[:3]]
    except:
        return []

real_news = get_real_news()

# 4. 總結邏輯
summaries_html = ""
for news in real_news:
    try:
        response = client.models.generate_content(
            model=selected_model, 
            contents=f"請用 80 字內廣東話總結這新聞重點並加 Emoji：{news['title']}"
        )
        summary_text = response.text
    except Exception as e:
        summary_text = f"總結失敗。錯誤原因：{str(e)}"

    summaries_html += f"""
    <div class="card">
        <h3>{news['title']}</h3>
        <p>{summary_text}</p>
        <div style="font-size:0.7em; color: #bbb;">模型：{selected_model}</div>
        <a href="{news['link']}" target="_blank">閱讀原文 →</a>
    </div>
    """

# 5. 生成 HTML (樣式優化)
html_content = f"""
<html>
<head>
    <title>AI 每日新聞</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, system-ui, sans-serif; line-height: 1.6; padding: 20px; max-width: 600px; margin: auto; background: #f0f2f5; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
        h1 {{ color: #1a73e8; text-align: center; }}
        a {{ color: #1a73e8; text-decoration: none; font-weight: bold; }}
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
