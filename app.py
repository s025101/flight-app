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

# 主要空港のIATAコードから日本語表示名への変換マップ
AIRPORT_NAME_MAP = {
    "HND": "東京/羽田", "NRT": "東京/成田", "ITM": "大阪/伊丹", "KIX": "大阪/関西",
    "FUK": "福岡", "CTS": "新千歳", "NGO": "中部", "OKA": "沖縄/那覇",
    "HIJ": "広島", "KCZ": "高知", "MMJ": "松本", "KMJ": "熊本", "KOJ": "鹿児島",
    "SDJ": "仙台", "AOJ": "青森", "AKJ": "旭川", "HKD": "函館", "MYJ": "松山"
}

# デフォルトの画面表示データ
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
    """空港コードとゲート番号をキーにしてリアルタイム情報を検索"""
    global current_flight_data
    req_data = request.json or {}
    
    # リクエストから空港名（IATA）とゲート番号を取得
    airport_code = str(req_data.get("airport_code") or req_data.get("airport") or "HND").strip().upper()
    target_gate = str(req_data.get("gate_number") or req_data.get("gate") or "5").strip().upper()

    if not has_fr24:
        return jsonify({"status": "error", "message": "FlightRadarAPIがサーバーにありません"}), 500

    try:
        # 指定空港の運行スケジュールを取得
        details = fr_api.get_airport_details(airport_code)
        plugin_data = details.get("pluginData", {})
        schedule = plugin_data.get("schedule", {})
        departures = schedule.get("departures", {}).get("data", [])

        matched_flight = None

        # 出発予定一覧の中から、指定されたゲート番号と一致するフライトを探索
        for item in departures:
            flight_info = item.get("flight", {})
            
            # FR24のレスポンス構造からゲート情報を柔軟に取得
            gate_in_status = flight_info.get("status", {}).get("generic", {}).get("status", {}).get("gate")
            gate_in_origin = flight_info.get("origin", {}).get("info", {}).get("gate")
            current_gate = str(gate_in_status or gate_in_origin or "").strip().upper()

            if current_gate == target_gate:
                matched_flight = flight_info
                break

        # 該当するゲートの便が見つかった場合
        if matched_flight:
            # 1. 航空会社コード & 便名
            airline_code = matched_flight.get("airline", {}).get("code", {}).get("iata") or "ANA"
            flight_number = matched_flight.get("identification", {}).get("number", {}).get("default") or f"{airline_code}100"
            
            # 2. 到着地
            dest_iata = matched_flight.get("destination", {}).get("code", {}).get("iata") or "ITM"
            dest_name_en = matched_flight.get("destination", {}).get("name") or "OSAKA"
            dest_name_ja = AIRPORT_NAME_MAP.get(dest_iata, dest_name_en)

            # 3. 出発予定時刻（STD）
            std_timestamp = matched_flight.get("time", {}).get("scheduled", {}).get("departure")
            dep_time = "07:10"
            if std_timestamp:
                dep_time = datetime.fromtimestamp(std_timestamp).strftime("%H:%M")

            # 4. 案内ステータス
            status_text = str(matched_flight.get("status", {}).get("text") or "")
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

            # 画面表示用のデータを一括更新
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
            # 指定ゲートにフライト情報が割り当てられていない場合
            return jsonify({
                "status": "error", 
                "message": f"空港 [{airport_code}] の {target_gate} 番ゲートには現在出発予定の便情報がありません。"
            }), 404

    except Exception as e:
        return jsonify({"status": "error", "message": f"データ取得エラー: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
