import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 1. 獲取天氣資訊 (包含當前、最高最低、以及詳細預測)
def get_weather_info():
    try:
        fnd_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"
        rhr_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        fnd_data = requests.get(fnd_url, timeout=10).json()
        rhr_data = requests.get(rhr_url, timeout=10).json()
        
        today_f = fnd_data['weatherForecast'][0]
        return {
            "current": rhr_data['temperature']['data'][0]['value'],
            "max": today_f['forecastMaxTemp']['value'],
            "min": today_f['forecastMinTemp']['value'],
            "desc": today_f['forecastForecast'], # 詳細天氣概況
            "humidity": today_f['forecastMaxrh']['value'] # 今日濕度上限
        }
    except:
        return None

# 2. 2026 DSE ICT 倒數
def get_dse_countdown():
    # 設定 2026 ICT 考試大約日期 (2026-04-24)
    target_date = datetime(2026, 4, 24)
    today = datetime.now()
    delta = target_date - today
    if delta.days > 0:
        return f"距離 2026 DSE ICT 考試還有 <strong>{delta.days}</strong> 天"
    else:
        return "2026 DSE ICT 考試已經開始或結束"

# 3. 獲取新聞 (整合 Google News & 政府新聞)
def get_it_edu_news():
    it_keywords = ["科技", "AI", "人工智能", "黑客", "網絡安全", "ChatGPT", "編程"]
    ed_keywords = ["教育", "學校", "DSE", "教育局", "教師", "學生", "STEM"]
    
    # 來源：Google News & 政府新聞
    urls = [
        "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant",
        "https://www.info.gov.hk/gia/rss/general_zh.xml"
    ]
    
    unique_news = []
    seen_titles = set()
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            root = ET.fromstring(response.content)
            for item in root.findall('./channel/item'):
                title = item.find('title').text
                link = item.find('link').text
                if any(kw in title for kw in it_keywords + ed_keywords):
                    if title not in seen_titles:
                        unique_news.append({"title": title, "link": link})
                        seen_titles.add(title)
                if len(unique_news) >= 5: break
        except:
            continue
    return unique_news[:5]

# --- 數據準備 ---
weather = get_weather_info()
dse_text = get_dse_countdown()
news_list = get_it_edu_news()
now_str = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')

# --- HTML 生成 ---
weather_box = ""
weather_desc_card = "無法獲取今日預測"
if weather:
    weather_box = f"""
    <div class="weather-box">
        <div class="temp-main">{weather['current']}°C</div>
        <div class="temp-detail">今日範圍：{weather['min']}°C - {weather['max']}°C</div>
    </div>
    """
    weather_desc_card = f"{weather['desc']} (濕度：{weather['humidity']}%)"

news_html = "".join([f'<div class="card"><h3>{n["title"]}</h3><a href="{n["link"]}" target="_blank">查看全文 →</a></div>' for n in news_list])

html_content = f"""
<html>
<head>
    <title>IT 教育教學看板</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, "PingFang HK", sans-serif; background: #f4f6f9; padding: 15px; max-width: 650px; margin: auto; color: #333; }}
        header {{ background: linear-gradient(135deg, #0d47a1, #1976d2); color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; }}
        .current-time {{ font-size: 0.9em; opacity: 0.8; margin-top: 5px; }}
        
        .info-panel {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .info-card {{ flex: 1; background: #fff; padding: 15px; border-radius: 12px; border-top: 4px solid #1976d2; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        .info-card h4 {{ margin: 0 0 8px 0; color: #1976d2; font-size: 0.85em; }}
        
        .weather-box {{ margin-top: 10px; }}
        .temp-main {{ font-size: 2.5em; font-weight: bold; }}
        .temp-detail {{ font-size: 1em; opacity: 0.9; }}
        
        .card {{ background: white; padding: 18px; margin-bottom: 12px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); transition: transform 0.1s; }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 1.05em; line-height: 1.4; color: #2c3e50; }}
        a {{ color: #1976d2; text-decoration: none; font-weight: 500; font-size: 0.9em; }}
        
        .footer {{ text-align: center; font-size: 0.75em; color: #7f8c8d; margin-top: 30px; line-height: 1.8; }}
    </style>
</head>
<body>
    <header>
        <h1>👨‍🏫 IT 教育情報站</h1>
        <div class="current-time">🕒 更新時間：{now_str}</div>
        {weather_box}
    </header>

    <div class="info-panel">
        <div class="info-card">
            <h4>🗓️ 2026 DSE ICT 倒數</h4>
            <div style="font-size: 1.1em;">{dse_text}</div>
        </div>
        <div class="info-card">
            <h4>🌤️ 今日天氣預測</h4>
            <div style="font-size: 0.95em; line-height: 1.5;">{weather_desc_card}</div>
        </div>
    </div>

    <h2 style="font-size: 1.2em; border-left: 4px solid #0d47a1; padding-left: 10px; margin: 25px 0 15px 0;">📰 最新教育與科技焦點</h2>
    {news_html}

    <div class="footer">
        自動化腳本運行中 | 數據來源：香港天文台、香港政府新聞網、Google News RSS<br>
        本網頁由 IT 教師自動化系統每日更新
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
