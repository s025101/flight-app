import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# FlightRadarAPI の安全なインポート
try:
    from FlightRadar24 import FlightRadar24API
    fr_api = FlightRadar24API()
    has_fr24 = True
except ImportError:
    fr_api = None
    has_fr24 = False

# 空港コード(IATA) と 日本語表示名の対応表
AIRPORT_NAME_MAP = {
    "HND": "東京/羽田", "NRT": "東京/成田", "ITM": "大阪/伊丹", "KIX": "大阪/関西",
    "FUK": "福岡", "CTS": "新千歳", "NGO": "中部", "OKA": "沖縄/那覇",
    "HIJ": "広島", "KCZ": "高知", "MMJ": "松本", "KMJ": "熊本", "KOJ": "鹿児島",
    "SDJ": "仙台", "AOJ": "青森", "AKJ": "旭川", "HKD": "函館", "MYJ": "松山"
}

# 案内板に表示しているデータ（初期値）
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
    """到着地の天気を取得（簡易レスポンス）"""
    return jsonify({
        "icon": "☀️",
        "temp": "22°C"
    })

@app.route("/api/fetch-live-flight", methods=["POST"])
def fetch_live_flight():
    """FlightRadar24 APIを利用した本物のリアルタイム便情報取得"""
    global current_flight_data
    req_data = request.json or {}
    
    airport_code = req_data.get("airport_code") or req_data.get("airport") or "HND"
    target_gate = str(req_data.get("gate_number") or req_data.get("gate") or "5").strip()

    if not has_fr24:
        return jsonify({
            "status": "error",
            "message": "FlightRadarAPI がサーバーにインストールされていません。"
        }), 500

    try:
        # FlightRadar24から空港の運行スケジュールを取得
        details = fr_api.get_airport_details(airport_code)
        plugin_data = details.get("pluginData", {})
        schedule = plugin_data.get("schedule", {})
        departures = schedule.get("departures", {}).get("data", [])

        matched_flight = None

        # 指定されたゲート番号の便を探す
        for item in departures:
            flight_info = item.get("flight", {})
            gate = flight_info.get("status", {}).get("generic", {}).get("status", {}).get("gate") or \
                   flight_info.get("origin", {}).get("info", {}).get("gate")
            
            if gate and str(gate).strip().upper() == target_gate.upper():
                matched_flight = flight_info
                break

        # ゲート指定で見つからない場合、出発予定の先頭便を取得
        if not matched_flight and departures:
            matched_flight = departures[0].get("flight", {})

        if matched_flight:
            # 1. 航空会社 & 便名
            airline_code = matched_flight.get("airline", {}).get("code", {}).get("iata") or "ANA"
            flight_number = matched_flight.get("identification", {}).get("number", {}).get("default") or f"{airline_code}100"
            
            # 2. 到着地
            dest_iata = matched_flight.get("destination", {}).get("code", {}).get("iata") or "ITM"
            dest_name_en = matched_flight.get("destination", {}).get("name") or "OSAKA"
            dest_name_ja = AIRPORT_NAME_MAP.get(dest_iata, dest_name_en)

            # 3. 出発時刻（STD）
            std_timestamp = matched_flight.get("time", {}).get("scheduled", {}).get("departure")
            dep_time = "07:10"
            if std_timestamp:
                dep_time = datetime.fromtimestamp(std_timestamp).strftime("%H:%M")

            # 4. ステータス判定
            status_text = matched_flight.get("status", {}).get("text") or "Scheduled"
            title_ja = "搭乗ご案内"
            title_en = "BOARDING INFORMATION"

            if "Boarding" in status_text:
                title_ja = "ご搭乗中"
                title_en = "NOW BOARDING"
            elif "Delayed" in status_text:
