import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from curl_cffi import requests as impersonate_requests

app = Flask(__name__)

flight_data = {
    "gate": "5",
    "title_ja": "ご搭乗中",
    "title_en": "NOW BOARDING",
    "destination_ja": "伊丹",
    "destination_en": "OSAKA/ITAMI",
    "airline_code": "ANA",
    "flight_no": "ANA420",
    "departure_time": "21:00",
    "boarding_time": "20:45",
    "weather_date": "08月26日"
}

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/api/flight')
def get_flight():
    return jsonify(flight_data)

@app.route('/api/fetch-live-flight', methods=['POST'])
def fetch_live_flight():
    global flight_data
    try:
        req_data = request.get_json() or {}
        airport_code = req_data.get('airport_code', 'HND').upper()
        target_gate_raw = str(req_data.get('gate_number', '')).strip()
        
        # 入力文字列から数字のみを抽出（例: "Gate 54" -> "54"）
        target_gate_num = re.sub(r'\D', '', target_gate_raw)

        url = f"https://api.flightradar24.com/common/v1/airport.json?code={airport_code}&plugin[]=&plugin-setting[schedule][mode]=departures&plugin-setting[schedule][timestamp]={int(datetime.now().timestamp())}&page=1&limit=100"
        
        resp = impersonate_requests.get(url, impersonate="chrome110", timeout=10)
        
        if resp.status_code != 200:
            return jsonify({"status": "error", "message": f"API取得失敗: HTTP {resp.status_code}"})

        data = resp.json()
        plugin_data = data.get("result", {}).get("response", {}).get("airport", {}).get("pluginData", {})
        departures = plugin_data.get("schedule", {}).get("departures", {}).get("data", [])

        if not departures:
            return jsonify({"status": "error", "message": f"空港（{airport_code}）の出発データが見つかりません"})

        matched_flight = None
        found_gates_log = []

        for item in departures:
            flight = item.get("flight", {})
            gate = flight.get("status", {}).get("generic", {}).get("gate", {})
            flight_no = flight.get("identification", {}).get("number", {}).get("default", "")
            
            raw_gate_str = ""
            if isinstance(gate, dict):
                raw_gate_str = str(gate.get("number", "") or gate.get("name", "")).strip()
            elif isinstance(gate, str):
                raw_gate_str = gate.strip()

            if raw_gate_str:
                found_gates_log.append(raw_gate_str)

            api_gate_num = re.sub(r'\D', '', raw_gate_str)
            
            # 【判定条件】
            # 1. ゲート番号（完全一致 / 数字一致 / 部分一致）
            # 2. 便名（例: "ANA420" や "420" を入力した場合にもヒットさせる）
            if target_gate_raw and (
                target_gate_raw.upper() == raw_gate_str.upper() or
                (target_gate_num and target_gate_num == api_gate_num) or
                (target_gate_raw in raw_gate_str) or
                (target_gate_raw.upper() in flight_no.upper())
            ):
                matched_flight = flight
                break

        # 判定に合格したフライトのみを反映（自動フォールバックは削除）
        if matched_flight:
            airline_code = matched_flight.get("airline", {}).get("code", {}).get("icao", "ANA")
            flight_no = matched_flight.get("identification", {}).get("number", {}).get("default", "ANA000")
            dest_name = matched_flight.get("airport", {}).get("destination", {}).get("name", "TOKYO")
            
            std_timestamp = matched_flight.get("time", {}).get("scheduled", {}).get("departure")
            dep_time = datetime.fromtimestamp(std_timestamp).strftime("%H:%M") if std_timestamp else "00:00"

            flight_data.update({
                "gate": target_gate_raw if target_gate_raw else "5",
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
            # マッチしなかった場合はエラーを返し、現在APIから取れている実際のゲート情報例を表示する
            gates_preview = ", ".join(list(set(found_gates_log))[:10]) if found_gates_log else "ゲート情報なし"
            return jsonify({
                "status": "error", 
                "message": f"「{target_gate_raw}」に一致する便・ゲートが見つかりませんでした。\n\n【現在APIで確認できる主なゲート一覧】\n[{gates_preview}]"
            })

    except Exception as e:
        print("例外エラー:", str(e))
        return jsonify({"status": "error", "message": f"処理エラー: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
