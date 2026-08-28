import os
import datetime
from flask import Flask, request, jsonify, render_template
from FlightRadar24 import FlightRadar24API

app = Flask(__name__, template_folder='.')

fr_api = FlightRadar24API()

@app.route('/')
def index():
    try:
        return render_template('main.html')
    except Exception as e:
        # main.html が読めない場合のフォールバック表示
        return f"HTMLの読み込みに失敗しました: {str(e)}", 500

@app.route('/api/fetch-live-flight', methods=['POST'])
def fetch_live_flight():
    try:
        data = request.get_json() or {}
        
        airport_code = data.get('airport_code') or data.get('airport') or 'HND'
        target_gate = str(data.get('gate_number') or data.get('gate') or '').strip()

        matched_flight = None
        
        # FR24からのデータ取得処理（安全に取得）
        try:
            airport_info = fr_api.get_airport(airport_code)
            
            # オブジェクトか辞書型かを安全に判定してデータ抽出
            if isinstance(airport_info, dict):
                plugin_data = airport_info.get('plugin_data', {})
            else:
                plugin_data = getattr(airport_info, 'plugin_data', {}) or {}

            if isinstance(plugin_data, dict):
                schedule = plugin_data.get('schedule', {}) or {}
                departures = schedule.get('departures', {}).get('data', [])
            else:
                departures = []

            # 対象ゲートの便を探索
            if target_gate and departures:
                for item in departures:
                    if not isinstance(item, dict):
                        continue
                    flight = item.get('flight', {})
                    if not isinstance(flight, dict):
                        continue
                        
                    # ゲート情報の安全な抽出
                    status_gate = flight.get('status', {}).get('generic', {}).get('status', {}).get('gate')
                    origin_gate = flight.get('airport', {}).get('origin', {}).get('info', {}).get('gate')
                    gate = str(status_gate or origin_gate or '').strip()
                    
                    if gate == target_gate:
                        matched_flight = flight
                        break

            # ゲート一致がない場合、最初の1件を採用
            if not matched_flight and departures:
                first_item = departures[0]
                if isinstance(first_item, dict):
                    matched_flight = first_item.get('flight', {})

        except Exception as fr_err:
            print(f"FR24 API Internal Warning: {fr_err}")

        # 万が一FR24から取得できなかった場合のダミー／初期値の安全生成
        if not matched_flight or not isinstance(matched_flight, dict):
            matched_flight = {}

        # 航空会社コードの安全取得
        airline_info = matched_flight.get('airline', {}) if isinstance(matched_flight.get('airline'), dict) else {}
        airline_code_info = airline_info.get('code', {}) if isinstance(airline_info.get('code'), dict) else {}
        airline_code = airline_code_info.get('icao') or airline_code_info.get('iata') or 'ANA'

        # 便名の安全取得
        ident_info = matched_flight.get('identification', {}) if isinstance(matched_flight.get('identification'), dict) else {}
        number_info = ident_info.get('number', {}) if isinstance(ident_info.get('number'), dict) else {}
        flight_number = number_info.get('default') or f"{airline_code}123"

        # 行き先空港の安全取得
        airport_dest = matched_flight.get('airport', {}) if isinstance(matched_flight.get('airport'), dict) else {}
        dest_info = airport_dest.get('destination', {}) if isinstance(airport_dest.get('destination'), dict) else {}
        dest_name = dest_info.get('name', '大阪/伊丹')
        dest_code_info = dest_info.get('code', {}) if isinstance(dest_info.get('code'), dict) else {}
        dest_code = dest_code_info.get('iata', 'ITM')

        # 出発時刻の安全取得
        time_details = matched_flight.get('time', {}) if isinstance(matched_flight.get('time'), dict) else {}
        sched_info = time_details.get('scheduled', {}) if isinstance(time_details.get('scheduled'), dict) else {}
        std_timestamp = sched_info.get('departure')
        
        std_str = "07:10"
        if std_timestamp:
            try:
                std_dt = datetime.datetime.fromtimestamp(std_timestamp)
                std_str = std_dt.strftime('%H:%M')
            except Exception:
                pass

        # 正常レスポンス返却
        response_data = {
            "status": "success",
            "data": {
                "gate": target_gate or "5",
                "title_ja": "搭乗ご案内",
                "title_en": "BOARDING INFORMATION",
                "destination_ja": dest_name,
                "destination_en": dest_code,
                "airline_code": airline_code,
                "flight_no": flight_number,
                "departure_time": std_str,
                "boarding_time": std_str,
                "weather_icon": "☀️",
                "weather_temp": "22°C",
                "weather_date": datetime.date.today().strftime('%m月%d日')
            }
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"Server Error: {e}")
        # サーバー側でエラーが起言しても 500 にせずメッセージを綺麗に返却
        return jsonify({
            "status": "error",
            "message": f"処理中にエラーが発生しました: {str(e)}"
        }), 200

@app.route('/api/update-flight-data', methods=['POST'])
def update_flight_data():
    data = request.get_json() or {}
    return jsonify(data)

@app.route('/api/flight-data', methods=['GET'])
def get_flight_data():
    return jsonify({
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
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
