from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

# 初期データの保持
flight_data = {
    "gate": "5",
    "title_ja": "搭乗ご案内",
    "title_en": "BOARDING INFORMATION",
    "destination_ja": "伊丹",
    "destination_en": "OSAKA/ITAMI",
    "airline_code": "ANA",
    "flight_no": "ANA420",
    "departure_time": "07:10",
    "boarding_time": "06:50",
    "weather_icon": "☀️☁️",
    "weather_temp": "21°C",
    "weather_date": "8月25日"
}

@app.route('/')
def index():
    # templates/main.html を読み込んで表示する
    return render_template('main.html')

@app.route('/api/flight-data', methods=['GET'])
def get_flight_data():
    return jsonify(flight_data)

@app.route('/api/update-flight-data', methods=['POST'])
def update_flight_data():
    global flight_data
    req_data = request.get_json()
    if req_data:
        flight_data.update(req_data)
    return jsonify(flight_data)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    dest = request.args.get('destination', '伊丹')
    # 簡易天気データ（必要に応じて外部API連携可能）
    return jsonify({"icon": "☀️☁️", "temp": "21°C"})

@app.route('/api/fetch-live-flight', methods=['POST'])
def fetch_live_flight():
    # リアルタイム取得処理のプレースホルダー
    return jsonify({"status": "error", "message": "リアルタイム取得機能は準備中です"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
