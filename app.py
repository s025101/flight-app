import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# FlightRadarAPI の安全なインポート
try:
    from FlightRadar24 import FlightRadar24API
    fr_api = FlightRadar24API()
    has_fr24 = True
except Exception:
    fr_api = None
    has_fr24 = False

AIRPORT_NAME_MAP = {
    "HND": "東京/羽田", "NRT": "東京/成田", "ITM": "大阪/伊丹", "KIX": "大阪/関西",
    "FUK": "福岡", "CTS": "新千歳", "NGO": "中部", "OKA": "沖縄/那覇",
    "HIJ": "広島", "KCZ": "高知", "MMJ": "松本", "KMJ": "熊本", "KOJ": "鹿児島",
    "SDJ": "仙台", "AOJ": "青森", "AKJ": "旭川", "HKD": "函館", "MYJ": "松山"
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
    """空港コードとゲート番号をキーにしてリアルタイム情報を取得（安全設計）"""
    global current_flight_data
    req_data = request.json or {}
    
    airport_code = str(req_data.get("airport_code") or req_data.get("airport") or "HND").strip().upper()
    target_gate = str(req_data.get("gate_number") or req_data.get("gate") or "5").strip().upper()

    if not has_fr24 or not fr_api:
        return jsonify({"status": "error", "message": "FlightRadar24 APIが使用できません。"}), 500

    try:
        # 空港詳細を取得（例外が発生しても落ちないようにケア）
        details = fr_api.get_airport_details(airport_code)
        if not isinstance(details, dict):
            details = {}

        plugin_data = details.get("pluginData") or {}
        schedule = plugin_data.get("schedule") or {}
        departures_data = schedule.get("departures") or {}
        departures = departures_data.get("data") or []

        matched_flight = None

        # 1. ゲート番号が一致するフライトを探す
        for item in departures:
            if not isinstance(item, dict):
                continue
            flight_info = item.get("flight") or {}
            
            # 各種キーからのゲート番号取得（安全アクセスの徹底）
            status_obj = flight_info.get("status") or {}
            generic_obj = status_obj.get("generic") or {}
            gate1 = (generic_obj.get("status") or {}).get("gate")
            
            origin_obj = flight_info.get("origin") or {}
            gate2 = (origin_obj.get("info") or {}).get("gate")

            current_gate = str(gate1 or gate2 or "").strip().upper()

            if current_gate and current_gate == target_gate:
                matched_flight = flight_info
                break

        # 2. もし一致するゲートが見つからない場合、出発予定の先頭便をフォールバック取得
        if not matched_flight and departures:
            first_item = departures[0]
            if isinstance(first_item, dict):
                matched_flight = first_item.get("flight")

        # フライト情報が抽出できた場合
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
            sched_obj = time_obj.get("scheduled") or {}
            std_timestamp = sched_obj.get("departure")

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
                "message": f"[{airport_code}] のデータ取得に成功しましたが、出発予定の便情報が見つかりませんでした。"
            }), 404

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"FlightRadar24通信エラー: {str(e)}"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
