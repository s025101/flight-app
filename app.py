import re

@app.route('/api/fetch-live-flight', methods=['POST'])
def fetch_live_flight():
    global flight_data
    req_data = request.get_json() or {}
    airport_code = req_data.get('airport_code', 'HND').upper()
    target_gate_raw = str(req_data.get('gate_number', '')).strip()
    
    # 入力された数字部分だけを抽出（例: "Gate 54" や "54A" から "54" を取り出す）
    target_gate_num = re.sub(r'\D', '', target_gate_raw)

    try:
        url = f"https://api.flightradar24.com/common/v1/airport.json?code={airport_code}&plugin[]=&plugin-setting[schedule][mode]=departures&plugin-setting[schedule][timestamp]={int(datetime.now().timestamp())}&page=1&limit=100"
        
        resp = impersonate_requests.get(url, impersonate="chrome110", timeout=10)
        
        if resp.status_code != 200:
            return jsonify({"status": "error", "message": f"HTTP {resp.status_code} エラーが発生しました"})

        data = resp.json()
        plugin_data = data.get("result", {}).get("response", {}).get("airport", {}).get("pluginData", {})
        departures = plugin_data.get("schedule", {}).get("departures", {}).get("data", [])

        if not departures:
            return jsonify({"status": "error", "message": f"空港コード ({airport_code}) の出発データが見つかりませんでした"})

        matched_flight = None
        found_gates_log = []

        for item in departures:
            flight = item.get("flight", {})
            gate = flight.get("status", {}).get("generic", {}).get("gate", {})
            
            # APIからゲート文字列を取得
            raw_gate_str = ""
            if isinstance(gate, dict):
                raw_gate_str = str(gate.get("number", "") or gate.get("name", "")).strip()
            elif isinstance(gate, str):
                raw_gate_str = gate.strip()

            if raw_gate_str:
                found_gates_log.append(raw_gate_str)

            # --- 柔軟なゲート一致判定 ---
            # 1. 完全一致
            # 2. API側のゲート文字列内に指定数字が含まれる（例: "Gate 54" に "54" が含まれる）
            # 3. 数字のみ抽出して比較
            api_gate_num = re.sub(r'\D', '', raw_gate_str)
            
            if target_gate_raw and (
                target_gate_raw.upper() == raw_gate_str.upper() or
                (target_gate_num and target_gate_num == api_gate_num) or
                (target_gate_raw in raw_gate_str)
            ):
                matched_flight = flight
                break

        if matched_flight:
            airline_code = matched_flight.get("airline", {}).get("code", {}).get("icao", "ANA")
            flight_no = matched_flight.get("identification", {}).get("number", {}).get("default", "ANA000")
            dest_name = matched_flight.get("airport", {}).get("destination", {}).get("name", "TOKYO")
            
            std_timestamp = matched_flight.get("time", {}).get("scheduled", {}).get("departure")
            dep_time = datetime.fromtimestamp(std_timestamp).strftime("%H:%M") if std_timestamp else "00:00"

            flight_data.update({
                "gate": target_gate_raw,
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
            # 見つからなかった場合、現在API上で確認できた実際のゲート文字一覧を表示する
            gates_preview = ", ".join(list(set(found_gates_log))[:10]) if found_gates_log else "（なし）"
            return jsonify({
                "status": "error", 
                "message": f"ゲート「{target_gate_raw}」の便が見つかりませんでした。\n\n【現在APIから取得できている実際のゲート表記例】\n[{gates_preview}]"
            })

    except Exception as e:
        print("取得例外:", e)
        return jsonify({"status": "error", "message": f"通信例外: {str(e)}"})
