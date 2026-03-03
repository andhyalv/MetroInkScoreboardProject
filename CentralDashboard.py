from flask import Flask, render_template, request, jsonify
import paramiko
import requests
import os
from scp import SCPClient
app = Flask(__name__)

PI_FOLDERS = {
    "Station A": r"C:\Users\andhy\Andhy_Main\Code\Completed_Utilities\MetroStats\ScoreboardScreenshots\station_a",
    "Station B": r"C:\Users\andhy\Andhy_Main\Code\Completed_Utilities\MetroStats\ScoreboardScreenshots\station_b",
    "Station C": r"C:\Users\andhy\Andhy_Main\Code\Completed_Utilities\MetroStats\ScoreboardScreenshots\station_c",
    "Station D": r"C:\Users\andhy\Andhy_Main\Code\Completed_Utilities\MetroStats\ScoreboardScreenshots\station_d",
    "Station E": r"C:\Users\andhy\Andhy_Main\Code\Completed_Utilities\MetroStats\ScoreboardScreenshots\station_e",
    "Mainstage": r"C:\Users\andhy\Andhy_Main\Code\Completed_Utilities\MetroStats\ScoreboardScreenshots\mainstage"
}


for folder in PI_FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

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

# ========== Helper: Pull files from a Pi ==========
def pull_files(station):
    import paramiko
    from scp import SCPClient
    ip = PIS[station]
    dest_folder = PI_FOLDERS[station]

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username="metro")  # your Pi username
        scp = SCPClient(ssh.get_transport())

        remote_folder = "/home/metro/MetroInkScoreboardProject/captures/"
        stdin, stdout, stderr = ssh.exec_command(f"ls {remote_folder}*.png")
        files = stdout.read().decode().splitlines()

        if not files:
            scp.close()
            ssh.close()
            return f"⚠️ No PNG files found in {remote_folder}"

        # Filter out files that already exist locally
        new_files = [f for f in files if not os.path.exists(os.path.join(dest_folder, os.path.basename(f)))]

        if not new_files:
            scp.close()
            ssh.close()
            return f"✅ No new files to pull for {station}"

        for file in new_files:
            scp.get(file, dest_folder)

        scp.close()
        ssh.close()
        return f"✅ Pulled {len(new_files)} new files for {station} into {dest_folder}"

    except Exception as e:
        return f"❌ Failed to pull files for {station}: {e}"
        
# ========== Routes ==========
@app.route("/")
def home():
    statuses = {}
    for name, ip in PIS.items():
        try:
            res = requests.get(f"http://{ip}:5001/status", timeout=3)
            statuses[name] = res.text
        except:
            statuses[name] = "Offline"
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
        print("Control Error:", e)
        return "Failed to connect", 500

@app.route("/pull/<station>", methods=["POST"])
def pull(station):
    if station not in PIS:
        return "Invalid station", 400
    result = pull_files(station)
    return jsonify({"message": result})

if __name__ == "__main__":
    print("Dashboard running on port 5002")
    app.run(host="0.0.0.0", port=5002)