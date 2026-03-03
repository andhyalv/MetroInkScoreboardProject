from flask import Flask, jsonify, request, send_from_directory
import subprocess, os, random, re

app = Flask(__name__)

HOME = os.path.expanduser("~")
PROJECT_FOLDER = os.path.join(HOME, "MetroInkScoreboardProject")
SCRIPT_PATH = os.path.join(PROJECT_FOLDER, "main.py")

# Folder to store captured images
CAPTURE_FOLDER = os.path.join(PROJECT_FOLDER, "captures")
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

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

    # Pass the filename argument to main.py
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

# =========================
# New endpoint to pull files
# =========================
@app.route("/files", methods=["GET"])
def list_files():
    """List all files in the capture folder."""
    files = sorted(os.listdir(CAPTURE_FOLDER))
    return jsonify(files)

@app.route("/files/<filename>", methods=["GET"])
def get_file(filename):
    """Download a specific file."""
    safe_filename = sanitize(filename)
    return send_from_directory(CAPTURE_FOLDER, safe_filename, as_attachment=True)

if __name__ == "__main__":
    print("🚀 Pi server running on port 5001")
    app.run(host="0.0.0.0", port=5001)
