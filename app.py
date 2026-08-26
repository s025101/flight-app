import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# シンプルな画面（HTML）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>フライトインフォメーション</title>
    <style>
        body { font-family: sans-serif; background: #111; color: #fff; text-align: center; padding: 20px; }
        .card { border: 2px solid #444; border-radius: 12px; padding: 20px; background: #222; display: inline-block; width: 80%; max-width: 400px; }
        .gate { font-size: 3rem; color: #ffcc00; font-weight: bold; }
        .info { font-size: 1.2rem; margin: 10px 0; }
        .status { background: #0088cc; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <div>GATE</div>
        <div class="gate">5</div>
        <hr>
        <div class="info">便名: <b>ANA420</b></div>
        <div class="info">行先: <b>大阪 / 伊丹</b></div>
        <div class="info">出発: <b>07:10</b> (搭乗 06:50)</div>
        <div class="info">天気: <b>21°C ☀️</b></div>
        <div style="margin-top: 15px;"><span class="status">ON TIME</span></div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Renderで動かすためのポート設定
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)