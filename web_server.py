from flask import Flask, json
import time

app = Flask(__name__)

def shutdown_flask():
    try:
        requests.get("http://127.0.0.1:5000/shutdown")
    except:
        pass

def update_pressure_history(pressure_value):
    history_path = "/tmp/pressure_history.json"
    max_length = 500

    try:
        with open(history_path, "r") as f:
            history = json.load(f)
    except:
        history = []

    timestamp = int(time.time())
    history.append({"time": timestamp, "pressure": pressure_value})
    history = history[-max_length:]

    try:
        with open(history_path, "w") as f:
            json.dump(history, f)
    except Exception as e:
        print(f"❌ Failed to save pressure history: {e}")

def get_json_pressure_log(retries=3):
    for _ in range(retries):
        try:
            with open("/tmp/pressure_log.json", "r") as f:
                data = json.load(f)

            pressure_val = data.get("pressure", 0.0)
            update_pressure_history(pressure_val)

            return {
                "pressure": pressure_val,
                "program": data.get("program", "N/A"),
                "stage": data.get("stage", 0),
                "cycle": data.get("cycle", 0),
                "action": data.get("action", "Idle")
            }
        except Exception as e:
            print(f"❌ Error reading status file: {e}")
            return {
                "pressure": 0.0,
                "program": "N/A",
                "stage": 0,
                "cycle": 0,
                "action": "Idle"
            }

@app.route('/pressure-data')
def pressure_data():
    try:
        with open("/tmp/pressure_history.json", "r") as f:
            return json.dumps(json.load(f))
    except:
        return json.dumps([])

@app.route('/status')
def get_status():
    return json.dumps(get_json_pressure_log())

@app.route('/')
def index():
    status = get_json_pressure_log()
    return f"""
    <html>
        <head>
            <title>Wine Press</title>
            <link rel="icon" href="/static/wine-press.ico" type="image/x-icon">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: sans-serif;
                    max-width: 700px;
                    margin: 20px auto;
                    padding: 10px;
                    background-color: #f7f7f7;
                }}
                h1 {{
                    font-size: 1.5em;
                    margin-bottom: 10px;
                }}
                p {{
                    margin: 6px 0;
                    font-size: 1em;
                }}
                .status-label {{
                    font-weight: bold;
                }}
                .status-value {{
                    transition: background-color 0.3s ease;
                    padding: 2px 4px;
                    border-radius: 4px;
                }}
                .flash {{
                    background-color: #d2eaf1;
                }}
                #chart-container {{
                    height: 300px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>🍷 Wine Press Status</h1>
            <p><span class="status-label">Current Pressure:</span> <span id="pressure" class="status-value">{status['pressure']:.2f}</span> BAR</p>
            <p><span class="status-label">Program:</span> <span id="program" class="status-value">{status['program']}</span></p>
            <p><span class="status-label">Stage:</span> <span id="stage" class="status-value">{status['stage']}</span></p>
            <p><span class="status-label">Cycle:</span> <span id="cycle" class="status-value">{status['cycle']}</span></p>
            <p><span class="status-label">Action:</span> <span id="action" class="status-value">{status['action']}</span></p>

            <div id="chart-container">
                <canvas id="pressureChart"></canvas>
            </div>

            <script>
                async function fetchData() {{
                    const res = await fetch('/pressure-data');
                    const data = await res.json();
                    return {{
                        labels: data.map(pt => new Date(pt.time * 1000).toLocaleTimeString()),
                        datasets: [{{
                            label: 'Pressure (BAR)',
                            data: data.map(pt => pt.pressure),
                            fill: false,
                            borderColor: 'blue',
                            tension: 0.3
                        }}]
                    }};
                }}

                async function renderChart() {{
                    const ctx = document.getElementById('pressureChart').getContext('2d');
                    const chartData = await fetchData();
                    window.chart = new Chart(ctx, {{
                        type: 'line',
                        data: chartData,
                        options: {{
                            animation: false,
                            responsive: true,
                            scales: {{
                                y: {{
                                    min: 0,
                                    max: 2,
                                    ticks: {{
                                        stepSize: 0.2
                                    }}
                                }}
                            }},
                            plugins: {{
                                legend: {{
                                    display: false
                                }}
                            }}
                        }}
                    }});
                }}

                async function updateStatus() {{
                    try {{
                        const res = await fetch('/status');
                        const data = await res.json();

                        updateField("pressure", data.pressure.toFixed(2));
                        updateField("program", data.program);
                        updateField("stage", data.stage);
                        updateField("cycle", data.cycle);
                        updateField("action", data.action);
                    }} catch (err) {{
                        console.error("❌ Failed to update status:", err);
                    }}
                }}

                function updateField(id, newValue) {{
                    const el = document.getElementById(id);
                    if (el.textContent !== newValue) {{
                        el.textContent = newValue;
                        el.classList.add("flash");
                        setTimeout(() => el.classList.remove("flash"), 300);
                    }}
                }}

                renderChart();
                setInterval(() => {{
                    updateStatus();
                    fetchData().then(chartData => {{
                        window.chart.data = chartData;
                        window.chart.update();
                    }});
                }}, 2000);
            </script>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
