from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__, static_folder='web', static_url_path='/web')

# 日本全国の主要・地方空港マッピング（天気取得用）
AIRPORT_COORDS = {
    # 北海道
    "新千歳": {"lat": 42.7752, "lon": 141.6923},
    "函館": {"lat": 41.7700, "lon": 140.8219},
    "旭川": {"lat": 43.6708, "lon": 142.4475},
    "釧路": {"lat": 43.0411, "lon": 144.1931},
    "帯広": {"lat": 42.7333, "lon": 143.2172},
    "女満別": {"lat": 43.8806, "lon": 144.1642},
    "稚内": {"lat": 45.4039, "lon": 141.8006},
    "中標津": {"lat": 43.5775, "lon": 144.9603},
    "紋別": {"lat": 44.3042, "lon": 143.4042},
    "奥尻": {"lat": 42.0719, "lon": 139.4328},
    "利尻": {"lat": 45.2422, "lon": 141.1858},
    "札幌丘珠": {"lat": 43.1161, "lon": 141.3800},

    # 東北
    "青森": {"lat": 40.7347, "lon": 140.6906},
    "三沢": {"lat": 40.7033, "lon": 141.3683},
    "花巻": {"lat": 39.4308, "lon": 141.1356},
    "仙台": {"lat": 38.1397, "lon": 140.9169},
    "秋田": {"lat": 39.6156, "lon": 140.2186},
    "大館能代": {"lat": 40.1919, "lon": 140.3708},
    "山形": {"lat": 38.4119, "lon": 140.3711},
    "庄内": {"lat": 38.8122, "lon": 139.7878},
    "福島": {"lat": 37.2272, "lon": 140.4319},

    # 関東・甲信越
    "羽田": {"lat": 35.5494, "lon": 139.7798},
    "成田": {"lat": 35.7647, "lon": 140.3863},
    "茨城": {"lat": 36.1808, "lon": 140.4144},
    "大島": {"lat": 34.7822, "lon": 139.3603},
    "八丈島": {"lat": 33.1147, "lon": 139.7858},
    "三宅島": {"lat": 34.0736, "lon": 139.5603},
    "調布": {"lat": 35.6717, "lon": 139.5281},
    "新潟": {"lat": 37.9558, "lon": 139.1214},
    "松本": {"lat": 36.1667, "lon": 137.9228},

    # 中部・北陸
    "中部": {"lat": 34.8583, "lon": 136.8053},
    "小牧": {"lat": 35.2550, "lon": 136.9244},
    "富士山静岡": {"lat": 34.7961, "lon": 138.1894},
    "富山": {"lat": 36.6483, "lon": 137.1875},
    "小松": {"lat": 36.3947, "lon": 136.4075},
    "能登": {"lat": 37.2931, "lon": 136.9603},
    "福井": {"lat": 36.1417, "lon": 136.2242},

    # 近畿
    "伊丹": {"lat": 34.7855, "lon": 135.4382},
    "関西": {"lat": 34.4320, "lon": 135.2304},
    "神戸": {"lat": 34.6328, "lon": 135.2239},
    "南紀白浜": {"lat": 33.6622, "lon": 135.3622},
    "但馬": {"lat": 35.5136, "lon": 134.7869},

    # 中国・四国
    "鳥取": {"lat": 35.5300, "lon": 134.1664},
    "米子": {"lat": 35.4922, "lon": 133.2364},
    "出雲": {"lat": 35.4136, "lon": 132.8894},
    "石見": {"lat": 34.6764, "lon": 131.7900},
    "隠岐": {"lat": 36.1811, "lon": 133.3333},
    "岡山": {"lat": 34.7569, "lon": 133.8553},
    "広島": {"lat": 34.4361, "lon": 132.9194},
    "岩国": {"lat": 34.1439, "lon": 132.2361},
    "山口宇部": {"lat": 33.9300, "lon": 131.2489},
    "徳島": {"lat": 34.1328, "lon": 134.6067},
    "高松": {"lat": 34.2142, "lon": 134.0156},
    "松山": {"lat": 33.8272, "lon": 132.7000},
    "高知": {"lat": 33.5461, "lon": 133.6694},

    # 九州・沖縄
    "福岡": {"lat": 33.5859, "lon": 130.4507},
    "北九州": {"lat": 33.8456, "lon": 131.0347},
    "佐賀": {"lat": 33.1497, "lon": 130.3022},
    "長崎": {"lat": 32.9169, "lon": 129.9136},
    "壱岐": {"lat": 33.7489, "lon": 129.7850},
    "対馬": {"lat": 34.2881, "lon": 129.3308},
    "五島福江": {"lat": 32.6664, "lon": 128.8328},
    "熊本": {"lat": 32.8372, "lon": 130.8553},
    "天草": {"lat": 32.4819, "lon": 130.1586},
    "大分": {"lat": 33.4794, "lon": 131.7372},
    "宮崎": {"lat": 31.8772, "lon": 131.4486},
    "鹿児島": {"lat": 31.8033, "lon": 130.7194},
    "奄美": {"lat": 28.4306, "lon": 129.7125},
    "屋久島": {"lat": 30.3853, "lon": 130.6592},
    "種子島": {"lat": 30.6094, "lon": 130.9583},
    "喜界": {"lat": 28.3211, "lon": 129.9281},
    "徳之島": {"lat": 27.8364, "lon": 128.8814},
    "沖永良部": {"lat": 27.4256, "lon": 128.7008},
    "与論": {"lat": 27.0439, "lon": 128.4011},
    "那覇": {"lat": 26.1958, "lon": 127.6458},
    "宮古": {"lat": 24.7828, "lon": 125.2950},
    "下地島": {"lat": 24.8267, "lon": 125.1447},
    "新石垣": {"lat": 24.3964, "lon": 124.2450},
    "久米島": {"lat": 26.3636, "lon": 126.7136},
    "与那国": {"lat": 24.4672, "lon": 122.9772},
    "多良間": {"lat": 24.6539, "lon": 124.6775},
    "南大東": {"lat": 25.8467, "lon": 131.2636},
    "北大東": {"lat": 25.9464, "lon": 131.3286},
    "慶良間": {"lat": 26.1683, "lon": 127.2931},
    "粟国": {"lat": 26.5928, "lon": 127.2386}
}

# WMO天気コードを絵文字に変換する辞書
WEATHER_ICONS = {
    0: "☀️",          # 快晴
    1: "🌤️",          # ほぼ晴れ
    2: "⛅",          # 一部曇り
    3: "☁️",          # 曇り
    45: "🌫️", 48: "🌫️", # 霧
    51: "🌧️", 53: "🌧️", 55: "🌧️", # しとしと雨
    61: "☔", 63: "☔", 65: "☔", # 雨
    71: "❄️", 73: "❄️", 75: "❄️", # 雪
    80: "🌦️", 81: "🌦️", 82: "🌦️", # 俄か雨
    95: "⚡", 96: "⚡", 99: "⚡"  # 雷雨
}

# 初期データの保持
flight_data = {
    "gate": "5",
    "title_ja": "搭乗ご案内",
    "title_en": "BOARDING INFORMATION",
    "destination_ja": "伊丹",
    "destination_en": "OSAKA/ITAMI",
    "airline_code": "ANA",
    "flight_no": "ANA420",
    "departure_time": "07:10",
    "boarding_time": "06:50",
    "weather_icon": "☀️",
    "weather_temp": "21°C",
    "weather_date": datetime.now().strftime("%m月%d日")
}

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/api/flight-data', methods=['GET'])
def get_flight_data():
    return jsonify(flight_data)

@app.route('/api/update-flight-data', methods=['POST'])
def update_flight_data():
    global flight_data
    req_data = request.get_json()
    if req_data:
        flight_data.update(req_data)
    return jsonify(flight_data)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    dest = request.args.get('destination', '伊丹')
    coords = AIRPORT_COORDS.get(dest, AIRPORT_COORDS["伊丹"])
    
    try:
        # Open-Meteo APIからリアルタイム天気を取得
        url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if "current_weather" in data:
            current = data["current_weather"]
            temp = f"{round(current['temperature'])}°C"
            weather_code = current.get("weathercode", 0)
            icon = WEATHER_ICONS.get(weather_code, "☀️")
            return jsonify({"icon": icon, "temp": temp})
    except Exception as e:
        print("天気API取得エラー:", e)
        
    return jsonify({"icon": "☀️", "temp": "--°C"})

@app.route('/api/fetch-live-flight', methods=['POST'])
def fetch_live_flight():
    return jsonify({"status": "error", "message": "リアルタイム取得機能は準備中です"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
