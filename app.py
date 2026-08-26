import os
import json
import urllib.request
import datetime
import re
from flask import Flask, jsonify, request, render_template_string
from FlightRadarAPI import FlightRadar24API

app = Flask(__name__)
fr_api = FlightRadar24API()

AIRPORT_COORDINATES = {
    "新千歳": {"lat": 42.7752, "lon": 141.6923}, "函館": {"lat": 41.7700, "lon": 140.8219},
    "旭川": {"lat": 43.6708, "lon": 142.4475}, "釧路": {"lat": 43.0411, "lon": 144.1933},
    "帯広": {"lat": 42.7333, "lon": 143.2167}, "女満別": {"lat": 43.8806, "lon": 144.1642},
    "稚内": {"lat": 45.4039, "lon": 141.8008}, "根室中標津": {"lat": 43.5775, "lon": 144.9600},
    "紋別": {"lat": 44.3042, "lon": 143.4042}, "利尻": {"lat": 45.2419, "lon": 141.1858},
    "奥尻": {"lat": 42.0719, "lon": 139.4328}, "青森": {"lat": 40.7342, "lon": 140.6906},
    "三沢": {"lat": 40.7033, "lon": 141.3683}, "花巻": {"lat": 39.4308, "lon": 141.1356},
    "仙台": {"lat": 38.1397, "lon": 140.9169}, "秋田": {"lat": 39.6156, "lon": 140.2186},
    "大館能代": {"lat": 40.1919, "lon": 140.3714}, "山形": {"lat": 38.4119, "lon": 140.3714},
    "庄内": {"lat": 38.8122, "lon": 139.7878}, "福島": {"lat": 37.2269, "lon": 140.4319},
    "羽田": {"lat": 35.5494, "lon": 139.7798}, "成田": {"lat": 35.7647, "lon": 140.3864},
    "大島": {"lat": 34.7822, "lon": 139.3603}, "八丈島": {"lat": 33.1147, "lon": 139.7858},
    "三宅島": {"lat": 34.0736, "lon": 139.5603}, "茨城": {"lat": 36.1808, "lon": 140.4142},
    "調布": {"lat": 35.6717, "lon": 139.5281}, "新潟": {"lat": 37.9558, "lon": 139.1208},
    "佐渡": {"lat": 38.0619, "lon": 138.4142}, "松本": {"lat": 36.1667, "lon": 137.9228},
    "富山": {"lat": 36.6483, "lon": 137.1875}, "小松": {"lat": 36.3947, "lon": 136.4075},
    "能登": {"lat": 37.2931, "lon": 136.9603}, "福井": {"lat": 36.1428, "lon": 136.2242},
    "静岡": {"lat": 34.7961, "lon": 138.1894}, "中部": {"lat": 34.8583, "lon": 136.8053},
    "名古屋(小牧)": {"lat": 35.2550, "lon": 136.9244}, "伊丹": {"lat": 34.7855, "lon": 135.4382},
    "関西": {"lat": 34.4347, "lon": 135.2442}, "神戸": {"lat": 34.6328, "lon": 135.2239},
    "南紀白浜": {"lat": 33.6622, "lon": 135.3622}, "但馬": {"lat": 35.5122, "lon": 134.7872},
    "鳥取": {"lat": 35.5300, "lon": 134.1667}, "米子": {"lat": 35.4922, "lon": 133.2364},
    "出雲": {"lat": 35.4136, "lon": 132.8894}, "石見": {"lat": 34.6764, "lon": 131.7900},
    "隠岐": {"lat": 36.1811, "lon": 133.3217}, "岡山": {"lat": 34.7569, "lon": 133.8556},
    "広島": {"lat": 34.4361, "lon": 132.9194}, "岩国": {"lat": 34.1439, "lon": 132.2361},
    "山口宇部": {"lat": 33.9300, "lon": 131.2494}, "徳島": {"lat": 34.1328, "lon": 134.6067},
    "高松": {"lat": 34.2142, "lon": 134.0156}, "松山": {"lat": 33.8272, "lon": 132.6997},
    "高知": {"lat": 33.5461, "lon": 133.6694}, "福岡": {"lat": 33.5859, "lon": 130.4507},
    "北九州": {"lat": 33.8458, "lon": 131.0347}, "佐賀": {"lat": 33.1497, "lon": 130.3022},
    "長崎": {"lat": 32.9169, "lon": 129.9136}, "対馬": {"lat": 34.2867, "lon": 129.3306},
    "壱岐": {"lat": 33.7489, "lon": 129.7850}, "福江(五島)": {"lat": 32.6661, "lon": 128.8328},
    "熊本": {"lat": 32.8372, "lon": 130.8550}, "天草": {"lat": 32.4828, "lon": 130.1589},
    "大分": {"lat": 33.4794, "lon": 131.7375}, "宮崎": {"lat": 31.8772, "lon": 131.4486},
    "鹿児島": {"lat": 31.8033, "lon": 130.7194}, "種子島": {"lat": 30.6097, "lon": 130.9592},
    "屋久島": {"lat": 30.3853, "lon": 130.6592}, "奄美": {"lat": 28.4306, "lon": 129.7125},
    "喜界": {"lat": 28.3192, "lon": 129.9281}, "徳之島": {"lat": 27.8364, "lon": 128.8814},
    "沖永良部": {"lat": 27.4256, "lon": 128.7008}, "与論": {"lat": 27.0439, "lon": 128.4011},
    "那覇": {"lat": 26.1958, "lon": 127.6458}, "新石垣": {"lat": 24.3964, "lon": 124.2447},
    "宮古": {"lat": 24.7828, "lon": 125.2953}, "下地島": {"lat": 24.8267, "lon": 125.1444},
    "久米島": {"lat": 26.3636, "lon": 126.7139}, "慶良間": {"lat": 26.1681, "lon": 127.2936},
    "粟国": {"lat": 26.5925, "lon": 127.2417}, "北大東": {"lat": 25.9469, "lon": 131.3283},
    "南大東": {"lat": 25.8469, "lon": 131.2642}, "多良間": {"lat": 24.6539, "lon": 124.6769},
    "与那国": {"lat": 24.4672, "lon": 122.9778}
}

AIRPORT_NAME_JA = {
    "HND": "羽田", "Haneda": "羽田", "Tokyo": "東京/羽田",
    "NRT": "成田", "Narita": "成田",
    "ITM": "伊丹", "Itami": "大阪/伊丹", "Osaka": "大阪/伊丹",
    "KIX": "関空", "Kansai": "大阪/関空",
    "UKB": "神戸", "Kobe": "神戸",
    "NGO": "中部", "Chubu": "名古屋/中部", "Nagoya": "名古屋",
    "FUK": "福岡", "Fukuoka": "福岡",
    "CTS": "新千歳", "New Chitose": "札幌/新千歳", "Sapporo": "札幌/新千歳",
    "OKA": "那覇", "Naha": "沖縄/那覇", "Okinawa": "沖縄/那覇",
    "KOJ": "鹿児島", "Kagoshima": "鹿児島", "KMJ": "熊本", "Kumamoto": "熊本",
    "MYJ": "松山", "Matsuyama": "松山", "HIJ": "広島", "Hiroshima": "広島",
    "SDJ": "仙台", "Sendai": "仙台", "AOJ": "青森", "Aomori": "青森",
    "ISG": "石垣", "Ishigaki": "石垣", "MMY": "宮古", "Miyako": "宮古"
}

WEATHER_CODES = {
    0: "☀️", 1: "☀️☁️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️", 51: "🌧️", 61: "☔",
    71: "❄️", 80: "🌦️", 95: "🌩️"
}

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
    "revised_dep_time": "",
    "revised_board_time": "",
    "weather_icon": "☀️☁️",
    "weather_temp": "21°C",
    "weather_date": "8月25日",
    "status": "ON TIME"
}

def normalize_gate(gate_str):
    if not gate_str:
        return ""
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', str(gate_str)).lower()
    return re.sub(r'^0+', '', cleaned)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>フライトインフォメーション</title>
    <style>
        body { font-family: sans-serif; background: #111; color: #fff; text-align: center; padding: 20px; }
        .card { border: 2px solid #444; border-radius: 12px; padding: 20px; background: #222; display: inline-block; width: 85%; max-width: 450px; }
        .gate { font-size: 3.5rem; color: #ffcc00; font-weight: bold; }
        .info { font-size: 1.2rem; margin: 12px 0; }
        .status { background: #0088cc; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 1.3rem; }
    </style>
</head>
<body>
    <div class="card">
        <div>GATE</div>
        <div class="gate" id="gate">{{ data.gate }}</div>
        <hr>
        <div class="info">便名: <b id="flight_no">{{ data.flight_no }}</b></div>
        <div class="info">行先: <b id="dest_ja">{{ data.destination_ja }}</b> (<span id="dest_en">{{ data.destination_en }}</span>)</div>
        <div class="info">出発: <b id="dep_time">{{ data.departure_time }}</b> (搭乗 <span id="board_time">{{ data.boarding_time }}</span>)</div>
        <div class="info">天気: <b id="weather">{{ data.weather_temp }} {{ data.weather_icon }}</b></div>
        <div style="margin-top: 20px;"><span class="status" id="status">{{ data.status }}</span></div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, data=flight_data)

@app.route('/api/flight_data', methods=['GET'])
def get_flight_data():
    return jsonify(flight_data)

@app.route('/api/fetch_weather', methods=['GET'])
def fetch_weather():
    destination = request.args.get('destination', '伊丹')
    if destination not in AIRPORT_COORDINATES:
        return jsonify({"temp": "--°C", "icon": "☀️"})
    
    coords = AIRPORT_COORDINATES[destination]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            current = data.get("current_weather", {})
            temp = f"{round(current.get('temperature'))}°C"
            code = current.get("weathercode", 0)
            icon = WEATHER_CODES.get(code, "☀️")
            return jsonify({"temp": temp, "icon": icon})
    except Exception as e:
        print(f"天気取得エラー: {e}")
        return jsonify({"temp": "--°C", "icon": "☀️"})

@app.route('/api/fetch_live', methods=['GET'])
def fetch_live_flight():
    airport_code = request.args.get('airport', 'HND')
    gate_number = request.args.get('gate', '5')
    
    try:
        airport_details = fr_api.get_airport_details(airport_code)
        airport_obj = airport_details.get('airport', {}) if isinstance(airport_details, dict) else {}
        plugin_data = airport_obj.get('pluginData', {})
        schedule = plugin_data.get('schedule', {})
        departures = schedule.get('departures', {}).get('data', [])

        if not departures:
            return jsonify({"status": "not_found", "message": f"{airport_code} の出発便データが見つかりませんでした"})

        matched_item = None
        target_gate_norm = normalize_gate(gate_number)

        if target_gate_norm:
            for item in departures:
                f_data = item.get('flight') or {}
                my_airport = f_data.get('airport', {}).get('origin') or {}
                raw_gate = my_airport.get('info', {}).get('gate')
                if raw_gate and normalize_gate(raw_gate) == target_gate_norm:
                    matched_item = item
                    break

        if target_gate_norm and not matched_item:
            return jsonify({
                "status": "not_found", 
                "message": f"{airport_code} の ゲート {gate_number} に割り当てられている出発便が見つかりませんでした"
            })

        if not matched_item:
            matched_item = departures[0]

        flight = matched_item.get('flight') or {}

        time_info = flight.get('time') or {}
        scheduled_info = time_info.get('scheduled') or {}
        schedule_time = scheduled_info.get('departure')
        
        estimated_info = time_info.get('estimated') or {}
        estimated_time = estimated_info.get('departure')

        dep_time_str = "07:10"
        boarding_time_str = "06:50"
        revised_dep_str = ""
        revised_board_str = ""

        if schedule_time:
            dt_sched = datetime.datetime.fromtimestamp(schedule_time)
            dep_time_str = dt_sched.strftime("%H:%M")
            dt_board = dt_sched - datetime.timedelta(minutes=20)
            boarding_time_str = dt_board.strftime("%H:%M")

        is_delayed = False
        if estimated_time and schedule_time and estimated_time > (schedule_time + 300):
            is_delayed = True
            dt_est = datetime.datetime.fromtimestamp(estimated_time)
            revised_dep_str = dt_est.strftime("%H:%M")
            dt_est_board = dt_est - datetime.timedelta(minutes=20)
            revised_board_str = dt_est_board.strftime("%H:%M")

        dest_airport = flight.get('airport', {}).get('destination') or {}
        dest_code = dest_airport.get('code', {}).get('iata', '')
        raw_city = dest_airport.get('position', {}).get('region', {}).get('city', '')
        raw_name = dest_airport.get('name', '')

        dest_ja = (
            AIRPORT_NAME_JA.get(dest_code) or 
            AIRPORT_NAME_JA.get(raw_city) or 
            AIRPORT_NAME_JA.get(raw_name) or 
            raw_city or 
            raw_name or 
            "伊丹"
        )
        dest_en = dest_code if dest_code else "ITM"

        airline = flight.get('airline') or {}
        airline_code = airline.get('code', {}).get('iata', 'ANA')

        identification = flight.get('identification') or {}
        number_info = identification.get('number') or {}
        flight_num = number_info.get('default', 'ANA420')

        my_airport_info = flight.get('airport', {}).get('origin') or {}
        info_data = my_airport_info.get('info', {}) if 'info' in my_airport_info else {}
        retrieved_gate = info_data.get('gate')
        display_gate = str(retrieved_gate) if retrieved_gate else (str(gate_number) if gate_number else "5")

        status_text = "DELAYED" if is_delayed else "ON TIME"
        status_info = flight.get('status') or {}
        fr_status = status_info.get('text') or ''
        if "Boarding" in fr_status:
            status_text = "BOARDING"
        elif "Departed" in fr_status:
            status_text = "DEPARTED"
        elif "Canceled" in fr_status:
            status_text = "CANCELED"

        global flight_data
        flight_data.update({
            "gate": display_gate,
            "airline_code": airline_code,
            "flight_no": flight_num,
            "destination_ja": dest_ja,
            "destination_en": dest_en,
            "departure_time": dep_time_str,
            "boarding_time": boarding_time_str,
            "revised_dep_time": revised_dep_str,
            "revised_board_time": revised_board_str,
            "status": status_text
        })
        
        return jsonify({"status": "success", "data": flight_data})

    except Exception as e:
        print(f"リアルタイム取得エラー: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
