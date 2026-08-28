import os
from flask import Flask, jsonify, render_template_string
from FlightRadar24 import FlightRadar24API

app = Flask(__name__)
fr_api = FlightRadar24API()

# HTMLテンプレート（簡単な動作確認用UI）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlightRadar24 Monitor</title>
    <style>
        body { font-family: sans-serif; margin: 2rem; background: #f4f4f9; color: #333; }
        h1 { color: #0056b3; }
        .card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        ul { line-height: 1.8; }
    </style>
</head>
<body>
    <div class="card">
        <h1>✈️ 航空会社リスト (FlightRadar24)</h1>
        <p>FlightRadar24 API との連携が正常に動作しています。</p>
        <p><a href="/api/airlines">APIエンドポイント (/api/airlines) を確認する</a></p>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    """トップページ"""
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/airlines")
def get_airlines():
    """航空会社一覧を取得するAPIエンドポイント"""
    try:
        airlines = fr_api.get_airlines()
        # 上位20件のみ返す例
        return jsonify({
            "status": "success",
            "count": len(airlines),
            "data": airlines[:20]
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/api/flights")
def get_flights():
    """現在飛行中のフライト情報を取得する例"""
    try:
        flights = fr_api.get_flights()
        # 最初の10件の簡易情報を抽出
        flight_data = []
        for f in flights[:10]:
            flight_data.append({
                "id": f.id,
                "callsign": f.callsign,
                "latitude": f.latitude,
                "longitude": f.longitude,
                "altitude": f.altitude,
                "ground_speed": f.ground_speed
            })
        return jsonify({
            "status": "success",
            "count": len(flights),
            "sample": flight_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    # ローカル開発用
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
