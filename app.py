from flask import Flask, request, jsonify, render_template
from FlightRadar24 import FlightRadar24API
import requests

app = Flask(__name__)
fr_api = FlightRadar24API()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-live-flight', methods=['POST'])
def fetch_live_flight():
    try:
        data = request.get_json() or {}
        
        # パラメータの取得（front側からのキー表記ゆれに対応）
        airport_code = data.get('airport_code') or data.get('airport') or 'HND'
        target_gate = str(data.get('gate_number') or data.get('gate') or '').strip()

        # 空港の詳細・スケジュールの取得（get_airport_details ではなく get_airport を使用）
        # ※ライブラリ仕様により airport オブジェクトまたは辞書を取得
        try:
            airport_info = fr_api.get_airport(airport_code)
        except Exception as e:
            # 万が一 get_airport が使えない場合のフォールバック（API直叩き等）
            return jsonify({
                "status": "error",
                "message": f"空港情報の取得に失敗しました: {str(e)}"
            }), 400

        # 出発予定便リストの探索
        # ※FlightRadar24APIのレスポンス構造から出発便を取り出します
        plugin_data = getattr(airport_info, 'plugin_data', {}) or {}
        schedule = plugin_data.get('schedule', {}) or {}
        departures = schedule.get('departures', {}).get('data', [])

        matched_flight = None

        # 1. 指定されたゲート番号に一致する便を検索
        if target_gate:
            for item in departures:
                flight = item.get('flight', {})
                # ゲート情報の取得
                gate = str(flight.get('status', {}).get('generic', {}).get('status', {}).get('gate') or 
                           flight.get('airport', {}).get('origin', {}).get('info', {}).get('gate') or '').strip()
                
                if gate == target_gate:
                    matched_flight = flight
                    break

        # 2. ゲート一致が見つからない場合、直近の出発便を1件取得
        if not matched_flight and departures:
            matched_flight = departures[0].get('flight', {})

        if not matched_flight:
            return jsonify({
                "status": "error",
                "message": f"空港 {airport_code} (ゲート: {target_gate}) の対象便が見つかりませんでした。"
            }), 444

        # 取得できた便データの抽出・整頓
        airline_code = matched_flight.get('airline', {}).get('code', {}).get('ica0', 'ANA')
        flight_number = matched_flight.get('identification', {}).get('number', {}).get('default', '')
        
        # 行き先空港の名称
        dest_name = matched_flight.get('airport', {}).get('destination', {}).get('name', '')
        dest_code = matched_flight.get('airport', {}).get('destination', {}).get('code', {}).get('iata', '')
        
        # 時刻情報
        time_details = matched_flight.get('time', {})
        std_timestamp = time_details.get('scheduled', {}).get('departure')
        
        import datetime
        std_str = "07:10"
        if std_timestamp:
            std_dt = datetime.datetime.fromtimestamp(std_timestamp)
            std_str = std_dt.strftime('%H:%M')

        # フロントエンドが期待するフォーマットで返却
        response_data = {
            "status": "success",
            "data": {
                "gate": target_gate or "5",
                "title_ja": "搭乗ご案内",
                "title_en": "BOARDING INFORMATION",
                "destination_ja": dest_name or dest_code or "大阪/伊丹",
                "destination_en": dest_code or "ITM",
                "airline_code": airline_code,
                "flight_no": flight_number or f"{airline_code}123",
                "departure_time": std_str,
                "boarding_time": std_str,
                "weather_icon": "☀️",
                "weather_temp": "22°C",
                "weather_date": datetime.date.today().strftime('%m月%d日')
            }
        }
        return jsonify(response_data)

    except Exception as e:
        print(f"FR24 Fetch Error: {e}")
        return jsonify({
            "status": "error",
            "message": f"リアルタイム情報の取得中にエラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/update-flight-data', methods=['POST'])
def update_flight_data():
    data = request.get_json()
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
