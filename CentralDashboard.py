from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Pi IP addresses
PIS = {
    "Station A": "192.168.8.111",
    "Station B": "192.168.8.198",
    "Station C": "192.168.8.200",
    "Station D": "192.168.8.143",
    "Station E": "192.168.8.234",
    "Mainstage": "192.168.8.180"
}

EVENT_INFO = {}  # Holds current event info

@app.route("/")
def home():
    statuses = {}
    for name, ip in PIS.items():
        try:
            res = requests.get(f"http://{ip}:5001/status", timeout=3)
            statuses[name] = res.text
        except:
            statuses[name] = "❌ Offline"
    return render_template("dashboard.html", statuses=statuses, pis=PIS, event=EVENT_INFO)

@app.route("/set_event", methods=["POST"])
def set_event():
    global EVENT_INFO
    data = request.json
    EVENT_INFO = {
        "name": data.get("name"),
        "abbr": data.get("abbr")
    }
    return jsonify(EVENT_INFO)

@app.route("/control", methods=["POST"])
def control():
    data = request.json
    station = data["station"]
    action = data["action"]

    if station not in PIS:
        return "Invalid station", 400

    ip = PIS[station]

    try:
        res = requests.post(f"http://{ip}:5001/{action}", json=data, timeout=3)
        return res.text
    except Exception as e:
        print("❌ Control Error:", e)
        return "Failed to connect", 500

if __name__ == "__main__":
    print("🚀 Dashboard running on port 5002")
    app.run(host="0.0.0.0", port=5002)
