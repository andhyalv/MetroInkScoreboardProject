from flask import Flask, jsonify, request
import subprocess, os, random, re

app = Flask(__name__)

# Universal home directory
HOME = os.path.expanduser("~")

# main.py is in the SAME project folder
SCRIPT_PATH = os.path.join(HOME, "MetroInkScoreboardProject", "main.py")

process = None

def sanitize(s):
    return re.sub(r"[^\w\d_-]", "_", s)

@app.route("/status", methods=["GET"])
def status():
    if process and process.poll() is None:
        return "🟢 Running"
    return "⚪ Idle"

@app.route("/start", methods=["POST"])
def start():
    global process  
    if process and process.poll() is None:
        return jsonify({"message": "⚠️ Already Running"}), 400

    data = request.json
    event_abbr = data.get("event_abbr", "EVT")
    event_safe = sanitize(event_abbr)
    rand_num = random.randint(1000, 9999)

    filename = f"{event_safe}_{rand_num}.png"

    cmd = ["python3", SCRIPT_PATH, f"--filename={filename}"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print(f"🚀 Started recording with filename: {filename}")
    return jsonify({"message": f"✅ Started recording {filename}"}), 200

@app.route("/stop", methods=["POST"])
def stop():
    global process
    if process and process.poll() is None:
        process.terminate()
        process = None
        return jsonify({"message": "⛔ Script Stopped"}), 200
    return jsonify({"message": "⚪ Not Running"}), 400

if __name__ == "__main__":
    print("🚀 Pi server running on port 5001")
    app.run(host="0.0.0.0", port=5001)
