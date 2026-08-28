import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# FlightRadarAPI の安全なインポート
try:
    from FlightRadar24 import FlightRadar24API
    fr_api = FlightRadar24API()
    has_fr24 = True
except Exception as e:
    print(f"FR24 Init Error: {e}")
    fr_api = None
    has_fr24 = False

AIRPORT_NAME_MAP = {
    "HND": "東京/羽田", "NRT": "東京/成田", "ITM": "大阪/伊丹", "KIX": "大阪/関西",
    "FUK": "福岡", "CTS": "新千歳", "NGO": "中部", "OKA": "沖縄/那覇",
    "HIJ": "広島", "KCZ": "高知", "MMJ": "松本", "KMJ": "熊本", "KOJ": "鹿児島",
    "SDJ": "仙台", "AOJ": "青森", "AKJ": "旭川", "HKD": "函館", "MYJ": "松山", "NTQ": "能登"
}

current_flight_data = {
    "gate": "5",
    "title_ja": "搭乗ご案内",
    "title_en": "BOARDING INFORMATION",
    "destination_ja": "大阪/伊丹",
    "destination_en": "OSAKA/ITAMI",
    "airline_code": "ANA",
    "flight_no": "ANA420",
    "departure_time": "07:10",
    "boarding_time": "06:50",
    "weather_icon": "☀️☁️",
    "weather_temp": "21°C",
    "weather_date": "8月25日"
}

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/api/flight-data", methods=["GET"])
def get_flight_data():
    return jsonify(current_flight_data)

@app.route("/api/update-flight-data", methods=["POST"])
def update_flight_data():
    global current_flight_data
    data = request.json
    if data:
        current_flight_data.update(data)
    return jsonify(current_flight_data)

@app.route("/api/weather", methods=["GET"])
def get_weather():
    return jsonify({"icon": "☀️", "temp": "22°C"})

@app.route("/api/fetch-live-flight", methods=["POST"])
def fetch_live_flight():
    """空港コードとゲート番号をキーにしてリアルタイム情報を取得"""
    global current_flight_data
    req_data = request.json or {}
    
    airport_code = str(req_data.get("airport_code") or req_data.get("airport") or "HND").strip().upper()
    target_gate = str(req_data.get("gate_number") or req_data.get("gate") or "5").strip().upper()

    if not has_fr24 or fr_api is None:
        return jsonify({
            "status": "error",
            "message": "FlightRadar24ライブラリが利用できません。"
        }), 200

    try:
        details = fr_api.get_airport_details(airport_code)
        
        if not details or not isinstance(details, dict):
            return jsonify({
                "status": "error",
                "message": "FlightRadar24からの応答データが空でした。"
            }), 200

        plugin_data = details.get("pluginData") or {}
        schedule = plugin_data.get("schedule") or {}
        departures_data = schedule.get("departures") or {}
        departures = departures_data.get("data") or []

        matched_flight = None

        # 1. 指定ゲートの便を探す
        for item in departures:
            if not isinstance(item, dict):
                continue
            flight_info = item.get("flight") or {}
            
            gate1 = ((flight_info.get("status") or {}).get("generic") or {}).get("status", {}).get("gate")
            gate2 = ((flight_info.get("origin") or {}).get("info") or {}).get("gate")
            current_gate = str(gate1 or gate2 or "").strip().upper()

            if current_gate and current_gate == target_gate:
                matched_flight = flight_info
                break

        # 2. 見つからない場合は出発予定の先頭便をフォールバック
        if not matched_flight and departures:
            first_item = departures[0]
            if isinstance(first_item, dict):
                matched_flight = first_item.get("flight")

        if matched_flight and isinstance(matched_flight, dict):
            airline_obj = matched_flight.get("airline") or {}
            airline_code = (airline_obj.get("code") or {}).get("iata") or "ANA"

            ident_obj = matched_flight.get("identification") or {}
            flight_number = (ident_obj.get("number") or {}).get("default") or f"{airline_code}100"

            dest_obj = matched_flight.get("destination") or {}
            dest_iata = (dest_obj.get("code") or {}).get("iata") or "ITM"
            dest_name_en = dest_obj.get("name") or "OSAKA"
            dest_name_ja = AIRPORT_NAME_MAP.get(dest_iata, dest_name_en)

            time_obj = matched_flight.get("time") or {}
            std_timestamp = (time_obj.get("scheduled") or {}).get("departure")

            dep_time = "07:10"
            if std_timestamp:
                try:
                    dep_time = datetime.fromtimestamp(std_timestamp).strftime("%H:%M")
                except Exception:
                    pass

            status_text = str((matched_flight.get("status") or {}).get("text") or "")
            title_ja = "搭乗ご案内"
            title_en = "BOARDING INFORMATION"

            if "Boarding" in status_text:
                title_ja = "ご搭乗中"
                title_en = "NOW BOARDING"
            elif "Delayed" in status_text:
                title_ja = "出発遅延"
                title_en = "DELAYED"
            elif "Canceled" in status_text or "Cancelled" in status_text:
                title_ja = "欠航"
                title_en = "CANCELLED"

            current_flight_data.update({
                "gate": target_gate,
                "title_ja": title_ja,
                "title_en": title_en,
                "destination_ja": dest_name_ja,
                "destination_en": str(dest_name_en).upper(),
                "airline_code": airline_code,
                "flight_no": flight_number,
                "departure_time": dep_time,
                "boarding_time": dep_time
            })

            return jsonify({"status": "success", "data": current_flight_data})

        else:
            return jsonify({
                "status": "error",
                "message": f"[{airport_code}] の {target_gate}番ゲートに該当する便が見つかりませんでした。"
            }), 200

    except Exception as e:
        print(f"FR24 Fetch Error: {e}")
        return jsonify({
            "status": "error",
            "message": f"リアルタイム情報の取得に失敗しました: {str(e)}"
        }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
