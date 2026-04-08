import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 1. 獲取香港天氣 (使用天文台 API)
def get_weather():
    try:
        # 天文台「今日天氣報告」API
        url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        temp = data['temperature']['data'][0]['value'] # 取第一個站點溫度
        humidity = data['humidity']['data'][0]['value']
        # 天氣警告或狀態描述
        desc = data.get('tcmessage', '天氣穩定')
        
        return f"🌡️ {temp}°C | 💧 濕度 {humidity}%"
    except:
        return "暫時無法獲取天氣資訊"

# 2. 獲取並過濾新聞 (教育 + IT)
def get_filtered_news():
    rss_url = "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    response = requests.get(rss_url, timeout=10)
    root = ET.fromstring(response.content)
    
    # 你想要的關鍵字
    keywords = ["教育", "學校", "STEM", "科技", "AI", "資訊科技", "編程", "DSE"]
    
    filtered_items = []
    for item in root.findall('./channel/item'):
        title = item.find('title').text
        link = item.find('link').text
        
        # 邏輯：如果標題包含任何一個關鍵字，就收入
        if any(word in title for word in keywords):
            filtered_items.append({"title": title, "link": link})
            if len(filtered_items) >= 3: # 只要 3 單
                break
                
    # 如果過濾完不到 3 單，就拿最新的補齊
    if len(filtered_items) < 3:
        for item in root.findall('./channel/item'):
            title = item.find('title').text
            link = item.find('link').text
            if not any(f['title'] == title for f in filtered_items):
                filtered_items.append({"title": title, "link": link})
            if len(filtered_items) >= 3: break
            
    return filtered_items

# 3. 執行抓取
weather_str = get_weather()
news_list = get_filtered_news()

# 4. 生成 HTML
news_html = ""
for news in news_list:
    news_html += f"""
    <div class="card">
        <h3>{news['title']}</h3>
        <a href="{news['link']}" target="_blank">點擊閱讀原文 →</a>
    </div>
    """

html_content = f"""
<html>
<head>
    <title>IT 老師的每日剪報</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: 'PingFang HK', sans-serif; line-height: 1.6; padding: 20px; max-width: 650px; margin: auto; background: #eef2f3; color: #2c3e50; }}
        header {{ background: #1a73e8; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px; }}
        .weather-box {{ background: #fff; padding: 10px; border-radius: 10px; margin-top: 10px; color: #1a73e8; font-weight: bold; }}
        .card {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        h3 {{ margin-top: 0; font-size: 1.1em; color: #34495e; }}
        a {{ color: #1a73e8; text-decoration: none; font-size: 0.9em; font-weight: bold; }}
        .footer {{ text-align: center; font-size: 0.75em; color: #95a5a6; margin-top: 30px; }}
    </style>
</head>
<body>
    <header>
        <h1>👨‍🏫 IT 教育日誌</h1>
        <div class="weather-box">今日天氣：{weather_str}</div>
    </header>

    {news_html}

    <div class="footer">
        更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (HKT)<br>
        資料來源：Google News & 香港天文台
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
