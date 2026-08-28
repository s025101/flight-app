import os
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

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
    """メイン画面（FIDS表示：main.html をレンダリング）"""
    return render_template("main.html")

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
    """到着地の天気を取得"""
    return jsonify({
        "icon": "☀️",
        "temp": "25°C"
    })

@app.route("/api/fetch-live-flight", methods=["POST"])
def fetch_live_flight():
    """リアルタイム便情報のダミー取得・反映"""
    req_data = request.json or {}
    gate_number = req_data.get("gate_number", "5")
    
    global current_flight_data
    current_flight_data.update({
        "gate": str(gate_number),
        "title_ja": "ご搭乗中",
        "title_en": "NOW BOARDING",
        "airline_code": "ANA",
        "flight_no": "ANA420",
        "departure_time": "07:10",
        "boarding_time": "06:50"
    })
    return jsonify({"status": "success", "data": current_flight_data})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
