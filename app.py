import os
from flask import Flask, render_template, jsonify, request
from FlightRadar24 import FlightRadar24API
import requests

app = Flask(__name__)

# Flightradar24 API インスタンス
fr_api = FlightRadar24API()

# 空港名・日本語マッピング用テーブル
AIRPORT_NAME_MAP = {
    "HND": "東京/羽田", "NRT": "東京/成田", "ITM": "大阪/伊丹", "KIX": "大阪/関西",
    "FUK": "福岡", "CTS": "新千歳", "NGO": "中部", "OKA": "沖縄/那覇",
    "HIJ": "広島", "KCZ": "高知", "MYJ": "松本", "KMJ": "熊本", "KOJ": "鹿児島"
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
    "weather_icon": "☀️",
    "weather_temp": "21°C",
    "weather_date": "8月25日"
}

@app.route("/")
def index():
    """メイン画面"""
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
    """オープン天気API等を利用した簡易天気取得（ダミー/拡張用）"""
    dest = request.args.get("destination", "")
    # 必要に応じてOpenWeatherMap等のAPIキーをセットして拡張可能です
    return jsonify({
        "icon": "☀️",
        "temp": "22°C"
    })

@app.route("/api/fetch-live-flight", methods=["POST"])
def fetch_live_flight():
    """Flightradar24からリアルタイム便情報を取得して反映"""
    global current_flight_data
    req_data = request.json or {}
    
    airport_code = req_data.get("airport_code") or req_data.get("airport") or "HND"
    target_gate = str(req_data.get("gate_number") or req_data.get("gate") or "5").strip()

    try:
        # Flightradar24から該当空港の運行スケジュール情報を取得
        details = fr_api.get_airport_details(airport_code)
        plugin_data = details.get("pluginData", {})
        schedule = plugin_data.get("schedule", {})
        departures = schedule.get("departures", {}).get("data", [])

        matched_flight = None

        # 該当するゲート番号の便を探索
        for item in departures:
            flight_info = item.get("flight", {})
            gate = flight_info.get("status", {}).get("generic", {}).get("status", {}).get("gate") or \
                   flight_info.get("origin", {}).get("info", {}).get("gate")
            
            # ゲート番号の一致確認（文字列比較）
            if gate and str(gate).strip().upper() == target_gate.upper():
                matched_flight = flight_info
                break

        if not matched_flight:
            # ゲート指定で見つからない場合、出発予定の最新便をフォールバック取得
            if departures:
                matched_flight = departures[0].get("flight", {})

        if matched_flight:
            # 航空会社コード・便名
            airline_code = matched_flight.get("airline", {}).get("code", {}).get("iata") or "ANA"
            flight_number = matched_flight.get("identification", {}).get("number", {}).get("default") or f"{airline_code}100"
            
            # 到着地
            dest_iata = matched_flight.get("destination", {}).get("code", {}).get("iata") or "ITM"
            dest_name_en = matched_flight.get("destination", {}).get("name") or "OSAKA"
            dest_name_ja = AIRPORT_NAME_MAP.get(dest_iata, dest_name_en)

            # 定刻（STD）
            std_timestamp = matched_flight.get("time", {}).get("scheduled", {}).get("departure")
            dep_time = "00:00"
            if std_timestamp:
                from datetime import datetime
                dep_time = datetime.fromtimestamp(std_timestamp).strftime("%H:%M")

            # ステータス判定
            status_text = matched_flight.get("status", {}).get("text") or "Scheduled"
            title_ja = "搭乗ご案内"
            title_en = "BOARDING INFORMATION"

            if "Boarding" in status_text:
                title_ja = "ご搭乗中"
                title_en = "NOW BOARDING"
            elif "Delayed" in status_text:
                title_ja = "出発遅延"
                title_en = "DELAYED"
            elif "Canceled" in status_text:
                title_ja = "欠航"
                title_en = "CANCELLED"

            # データを更新
            current_flight_data.update({
                "gate": target_gate,
                "title_ja": title_ja,
                "title_en": title_en,
                "destination_ja": dest_name_ja,
                "destination_en": dest_name_en.upper(),
                "airline_code": airline_code,
                "flight_no": flight_number,
                "departure_time": dep_time,
                "boarding_time": dep_time # 簡易的に定刻をセット
            })

            return jsonify({
                "status": "success",
                "data": current_flight_data
            })
        else:
            return jsonify({"status": "error", "message": "指定されたゲートの便が見つかりませんでした"}), 444

    except Exception as e:
        print(f"FR24 Fetch Error: {e}")
        return jsonify({"status": "error", "message": f"Flightradar24からの取得に失敗しました: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
