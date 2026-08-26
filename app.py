from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

# 空港ごとの緯度・経度マッピング
AIRPORT_COORDS = {
    "羽田": {"lat": 35.5494, "lon": 139.7798},
    "成田": {"lat": 35.7647, "lon": 140.3863},
    "伊丹": {"lat": 34.7855, "lon": 135.4382},
    "関西": {"lat": 34.4320, "lon": 135.2304},
    "福岡": {"lat": 33.5859, "lon": 130.4507},
    "新千歳": {"lat": 42.7752, "lon": 141.6923},
    "那覇": {"lat": 26.1958, "lon": 127.6458},
    "中部": {"lat": 34.8584, "lon": 136.8053}
}

# WMO天気コードを絵文字に変換する辞書
WEATHER_ICONS = {
    0: "☀️",
    1: "🌤️",
    2: "⛅",
    3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌧️", 53: "🌧️", 55: "🌧️",
    61: "☔", 63: "☔", 65: "☔",
    71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌦️", 81: "🌦️", 82: "🌦️",
    95: "⚡", 96: "⚡", 99: "⚡"
}

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
    "weather_date": "8月25日"
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
    
    # デフォルトの座標（伊丹）
    target_coords = AIRPORT_COORDS["伊丹"]
    
    # 部分一致で空港を検索
    for key, coords in AIRPORT_COORDS.items():
        if key in dest:
            target_coords = coords
            break
            
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={target_coords['lat']}&longitude={target_coords['lon']}&current_weather=true"
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
