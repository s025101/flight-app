import os
from flask import Flask, render_template, jsonify, request
from FlightRadar24 import FlightRadar24API

app = Flask(__name__)
fr_api = FlightRadar24API()

# 現在案内板に表示しているデータ（初期値）
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
    """メイン画面（FIDS表示）"""
    return render_template("index.html")

@app.route("/api/flight-data", methods=["GET"])
def get_flight_data():
    """現在のフライト表示データを取得"""
    return jsonify(current_flight_data)

@app.route("/api/update-flight-data", methods=["POST"])
def update_flight_data():
    """手動設定による更新データを受信"""
    global current_flight_data
    data = request.json
    if data:
        current_flight_data.update(data)
    return jsonify(current_flight_data)

@app.route("/api/weather", methods=["GET"])
def get_weather():
    """到着地の天気を取得（ダミーデータ例）"""
    destination = request.args.get("destination", "")
    return jsonify({
        "icon": "☀️",
        "temp": "25°C"
    })

@app.route("/api/fetch-live-flight", methods=["POST"])
def fetch_live_flight():
    """FlightRadar24からリアルタイム便情報を探索・反映"""
    req_data = request.json or {}
    airport_code = req_data.get("airport_code", "HND")
    gate_number = req_data.get("gate_number", "5")
    
    try:
        flights = fr_api.get_flights()
        found_flight = None

        # 該当空港を出発する便を検索
        for f in flights:
            origin = getattr(f, "origin_airport_iata", "")
            if origin == airport_code:
                found_flight = f
                break

        global current_flight_data
        if found_flight:
            callsign = getattr(found_flight, "callsign", "") or "ANA420"
            airline_code = callsign[:3] if len(callsign) >= 3 else "ANA"
            
            current_flight_data.update({
                "gate": str(gate_number),
                "title_ja": "搭乗ご案内",
                "title_en": "BOARDING INFORMATION",
                "airline_code": airline_code,
                "flight_no": callsign,
                "departure_time": "12:00",
                "boarding_time": "11:40"
            })
            return jsonify({"status": "success", "data": current_flight_data})
        else:
            return jsonify({
                "status": "error", 
                "message": f"{airport_code} 出発のリアルタイム便が見つかりませんでした"
            }), 444

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
