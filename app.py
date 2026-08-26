from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

# 空港ごとの緯度・経度マッピング（天気取得用）
AIRPORT_COORDS = {
    "羽田": {"lat": 35.5494, "lon": 139.7798},
    "成田": {"lat": 35.7647, "lon": 140.3863},
    "伊丹": {"lat": 34.7855, "lon": 135.4382},
    "関西": {"lat": 34.4320, "lon": 135.2304},
    "福岡": {"lat": 33.5859, "lon": 130.4507},
    "新千歳": {"lat": 42.7752, "lon": 141.6923},
    "中部": {"lat": 34.8583, "lon": 136.8053},
    "那覇": {"lat": 26.1958, "lon": 127.6458}
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
    # リアルタイム自動取得ボタンが押された時の処理
    # ここにFlightRadarAPIなどの処理を後から追加できますが、
    # まずは現在のflight_dataをそのまま返すようにしてエラーを防ぎます
    req_data = request.get_json()
    if req_data and 'gate_number' in req_data:
        flight_data['gate'] = req_data['gate_number']
        
    return jsonify({
        "status": "success",
        "message": "データを更新しました",
        "data": flight_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
