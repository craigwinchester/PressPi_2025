# web_server.py

from flask import Flask
import json
import time

app = Flask(__name__)

def get_json_pressure_log(retries=3):
    for _ in range(retries):
        try:
            with open("/tmp/pressure_log.json","r") as f:
                data = json.load(f)
            return data.get("pressure", 0.0)
        except (json.JSONDecodeError, FileNotFoundError):
            time.sleep(0.1)    
        return 0.0

@app.route('/')
def index():
    p = get_json_pressure_log()
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="2">
            <title>Wine Press</title>
        </head>
        <body style="font-family:sans-serif;">
            <h1>🍷 Wine Press Status</h1>
            <p style="font-size:1.5em;">Current Pressure: <strong>{p:.2f} BAR</strong></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
