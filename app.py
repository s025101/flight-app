from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime
from FlightRadarAPI import FlightRadar24API

app = Flask(__name__)

# User-Agentを設定してCloudflareなどのブロックを回避
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
fr_api = FlightRadar24API()

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

WEATHER_ICONS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️", 51: "🌧️", 53: "🌧️", 55: "🌧️",
    61: "☔", 63: "☔", 65: "☔", 71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌦️", 81: "🌦️", 82: "🌦️", 95: "⚡", 96: "⚡", 99: "⚡"
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
    global flight_data
    req_data = request.get_json() or {}
    airport_code = req_data.get('airport_code', 'HND').upper()
    target_gate = str(req_data.get('gate_number', '5')).strip()

    try:
        # FlightRadar24のWeb APIエンドポイントへ直接リクエスト（Renderからのブロック対策ヘッダー付き）
        url = f"https://api.flightradar24.com/common/v1/airport.json?code={airport_code}&plugin[]=&plugin-setting[schedule][mode]=departures&plugin-setting[schedule][timestamp]={int(datetime.now().timestamp())}&page=1&limit=100"
        
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code != 200:
            return jsonify({"status": "error", "message": f"FlightRadar24通信エラー (HTTP {resp.status_code})"}).strip()

        data = resp.json()
        
        # ネストされたデータの安全な取得
        plugin_data = data.get("result", {}).get("response", {}).get("airport", {}).get("pluginData", {})
        schedule = plugin_data.get("schedule", {})
        departures = schedule.get("departures", {}).get("data", [])

        if not departures:
            return jsonify({"status": "error", "message": f"空港コード ({airport_code}) のデータ構造が取得できませんでした。"})

        matched_flight = None
        available_gates = []

        for item in departures:
            flight = item.get("flight", {})
            
            # ゲート番号の抽出 (複数パターンに対応)
            gate = flight.get("status", {}).get("generic", {}).get("gate", {})
            gate_number = ""
            if isinstance(gate, dict):
                gate_number = str(gate.get("number", "")).strip()
            elif isinstance(gate, str):
                gate_number = gate.strip()

            if gate_number:
                available_gates.append(gate_number)

            if gate_number == target_gate:
                matched_flight = flight
                break

        if matched_flight:
            airline_code = matched_flight.get("airline", {}).get("code", {}).get("icao", "ANA")
            flight_no = matched_flight.get("identification", {}).get("number", {}).get("default", "ANA000")
            dest_name = matched_flight.get("airport", {}).get("destination", {}).get("name", "OSAKA")
            
            std_timestamp = matched_flight.get("time", {}).get("scheduled", {}).get("departure")
            dep_time = datetime.fromtimestamp(std_timestamp).strftime("%H:%M") if std_timestamp else "00:00"

            flight_data.update({
                "gate": target_gate,
                "title_ja": "ご搭乗中",
                "title_en": "NOW BOARDING",
                "destination_ja": dest_name.split()[0],
                "destination_en": dest_name.upper(),
                "airline_code": airline_code,
                "flight_no": flight_no,
                "departure_time": dep_time,
                "boarding_time": dep_time,
                "weather_date": datetime.now().strftime("%m月%d日")
            })
            return jsonify({"status": "success", "data": flight_data})
        else:
            gates_str = ", ".join(sorted(list(set(available_gates)))) if available_gates else "現在ゲート番号が設定されている便がありません"
            return jsonify({
                "status": "error", 
                "message": f"ゲート {target_gate} の便が見つかりませんでした。\n取得できたゲート一覧: [{gates_str}]"
            })

    except Exception as e:
        print("FlightRadar24取得エラー:", e)
        return jsonify({"status": "error", "message": f"API取得例外: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
