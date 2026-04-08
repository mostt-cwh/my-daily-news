import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# 1. 獲取天氣 (包含最高最低溫)
def get_detailed_weather():
    try:
        fnd_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"
        rhr_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
        fnd_data = requests.get(fnd_url, timeout=10).json()
        rhr_data = requests.get(rhr_url, timeout=10).json()
        
        today_forecast = fnd_data['weatherForecast'][0]
        return {
            "current": rhr_data['temperature']['data'][0]['value'],
            "max": today_forecast['forecastMaxTemp']['value'],
            "min": today_forecast['forecastMinTemp']['value'],
            "desc": today_forecast['forecastForecast']
        }
    except:
        return None

# 2. 獲取重要日子倒數 (例如：DSE ICT 考試)
def get_countdown():
    # 這裡可以修改為你學校的考試日期或重要活動
    target_date = datetime(2027, 4, 15) # 假設 2027 年 DSE ICT 考試日
    today = datetime.now()
    delta = target_date - today
    if delta.days > 0:
        return f"距離 2027 DSE ICT 考試還有 <strong>{delta.days}</strong> 天"
    else:
        return "DSE 已經開始或結束！"

# 3. 每日 IT 金句 / 冷知識 (根據日期自動輪換)
def get_daily_quote():
    quotes = [
        "「每個人都應該學習編程，因為它教你如何思考。」— Steve Jobs",
        "💡 IT 冷知識：世界上第一個滑鼠是木頭做的，發明於 1964 年。",
        "「Talk is cheap. Show me the code.」— Linus Torvalds (Linux 創始人)",
        "💡 IT 冷知識：第一隻電腦 Bug 真的是一隻飛蛾，被夾在電腦繼電器中。",
        "「電腦就像比基尼，省去了人們許多猜想。」— Sam Ewing",
        "💡 IT 冷知識：Ctrl+Alt+Del 最初是設計給開發人員快速重啟電腦的隱藏快捷鍵。"
    ]
    # 根據一年中的第幾天來決定顯示哪一句，每天不一樣
    day_of_year = datetime.now().timetuple().tm_yday
    return quotes[day_of_year % len(quotes)]

# 4. 抓取新聞 (加入政府新聞網 RSS)
def fetch_news_from_rss(rss_url, keywords, limit=3):
    items = []
    try:
        response = requests.get(rss_url, timeout=10)
        root = ET.fromstring(response.content)
        for item in root.findall('./channel/item'):
            title = item.find('title').text
            link = item.find('link').text
            if any(word in title for word in keywords):
                items.append({"title": title, "link": link})
            if len(items) >= limit: break
    except:
        pass
    return items

def get_all_news():
    it_keywords = ["科技", "AI", "資訊科技", "編程", "人工智能", "黑客", "網絡安全"]
    ed_keywords = ["教育", "學校", "DSE", "考評局", "教師", "學生"]
    
    # 來源 A: Google News (主攻 IT)
    google_url = "https://news.google.com/rss?hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    # 來源 B: 香港政府新聞網 (教育局相關)
    gov_url = "https://www.info.gov.hk/gia/rss/general_zh.xml"
    
    news_all = []
    news_all.extend(fetch_news_from_rss(google_url, it_keywords, limit=3))
    news_all.extend(fetch_news_from_rss(gov_url, ed_keywords, limit=2))
    
    # 去重
    seen, unique_news = set(), []
    for n in news_all:
        if n['title'] not in seen:
            unique_news.append(n)
            seen.add(n['title'])
    return unique_news[:5]

# --- 執行程序 ---
weather = get_detailed_weather()
countdown_text = get_countdown()
quote_text = get_daily_quote()
news_items = get_all_news()

# --- 生成 HTML ---
weather_html = ""
if weather:
    weather_html = f"""
    <div class="weather-box">
        <div class="temp-main">{weather['current']}°C</div>
        <div class="temp-detail">今日：{weather['min']}°C - {weather['max']}°C</div>
        <div class="weather-desc">{weather['desc']}</div>
    </div>
    """

news_html = "".join([f'<div class="card"><h3>{n["title"]}</h3><a href="{n["link"]}" target="_blank">查看全文 →</a></div>' for n in news_items])

html_content = f"""
<html>
<head>
    <title>IT 老師教學儀表板</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, "PingFang HK", sans-serif; background: #f0f2f5; padding: 20px; max-width: 650px; margin: auto; color: #333; }}
        header {{ background: linear-gradient(135deg, #1a73e8, #2c3e50); color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ margin: 0; font-size: 1.8em; }}
        .weather-box {{ background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; margin-top: 15px; }}
        .temp-main {{ font-size: 2.2em; font-weight: bold; margin-bottom: 5px; }}
        
        .info-panel {{ display: flex; gap: 15px; margin-bottom: 20px; }}
        .info-card {{ flex: 1; background: #fff; padding: 15px; border-radius: 10px; border-left: 5px solid #1a73e8; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .info-card h4 {{ margin: 0 0 8px 0; color: #666; font-size: 0.9em; text-transform: uppercase; }}
        
        .card {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: transform 0.2s; }}
        .card:hover {{ transform: translateX(5px); border-left: 3px solid #1a73e8; }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 1.1em; line-height: 1.4; }}
        a {{ color: #1a73e8; text-decoration: none; font-weight: 500; font-size: 0.9em; }}
        .footer {{ text-align: center; font-size: 0.8em; color: #888; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <header>
        <h1>👨‍🏫 IT 老師教學儀表板</h1>
        {weather_html}
    </header>

    <div class="info-panel">
        <div class="info-card">
            <h4>⏱️ 重要倒數</h4>
            <div>{countdown_text}</div>
        </div>
        <div class="info-card" style="border-left-color: #f39c12;">
            <h4>💬 每日金句 / 冷知識</h4>
            <div>{quote_text}</div>
        </div>
    </div>

    <h2 style="font-size: 1.2em; color: #2c3e50; border-bottom: 2px solid #1a73e8; padding-bottom: 5px; display: inline-block;">📰 焦點新聞 (教育與科技)</h2>
    {news_html}

    <div class="footer">
        自動更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (HKT)<br>
        數據來源：香港天文台、香港政府新聞網、Google News
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
