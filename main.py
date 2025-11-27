import os
import time
import cv2
import random
import paramiko
from scp import SCPClient
import argparse
import datetime
import tempfile
import platform

# =========================
# SSH SETTINGS (EDIT ONLY THESE)
# =========================
WINDOWS_IP = "192.168.8.131"
WINDOWS_USER = "andhy"

# Dynamically build the destination folder on Windows
WINDOWS_DEST_FOLDER = os.path.join(
    os.environ["USERPROFILE"], "MetroInkScoreboardProject", "ScoreboardScreenshots", "station_a"
)

# =========================
# Parse filename sent by API server
# =========================
parser = argparse.ArgumentParser()
parser.add_argument("--filename", required=True)
args = parser.parse_args()
initial_filename = args.filename
event_abbr = initial_filename.split("_")[0]

# =========================
# Universal home directory and project folder
# =========================
HOME = os.path.expanduser("~")
PROJECT_FOLDER = os.path.join(HOME, "MetroInkScoreboardProject")

# =========================
# Reference image
# =========================
REFERENCE_IMAGE_PATH = os.path.join(PROJECT_FOLDER, "scoreboard_reference.jpg")
reference_img = cv2.imread(REFERENCE_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if reference_img is None:
    print("❌ Missing scoreboard_reference.jpg at:", REFERENCE_IMAGE_PATH)
    exit()

# =========================
# SSH + SCP
# =========================
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(WINDOWS_IP, username=WINDOWS_USER)
scp_client = SCPClient(ssh_client.get_transport())

# =========================
# Helper functions
# =========================
def resize_reference(reference_img, screen_w, screen_h):
    ref_h, ref_w = reference_img.shape[:2]
    if ref_w > screen_w or ref_h > screen_h:
        scale = min(screen_w / ref_w, screen_h / ref_h)
        return cv2.resize(reference_img, (int(ref_w * scale), int(ref_h * scale)))
    return reference_img

def find_reference_location(screen_img, reference_img):
    result = cv2.matchTemplate(screen_img, reference_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_loc if max_val >= 0.3 else None

def get_capture_device():
    for i in range(0, 6):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[OK] Found capture device at index {i}")
            return cap
        cap.release()
    print("❌ No capture device found")
    return None

def upload_to_windows(file_path):
    try:
        scp_client.put(file_path, WINDOWS_DEST_FOLDER)
        print(f"📤 Uploaded: {os.path.basename(file_path)}")
    except Exception as e:
        print("❌ Upload failed:", e)

# =========================
# Video capture setup
# =========================
capture = get_capture_device()
if capture is None:
    exit()

capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

STATION_NAME = platform.node()  # auto uses hostname
print(f"🚀 Detection running on {STATION_NAME}")

last_check = time.time()

# =========================
# Main Loop
# =========================
while True:
    ret, frame = capture.read()
    if not ret:
        print("❌ No frame")
        break

    frame_resized = cv2.resize(frame, (1280, 720))
    screen_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    if time.time() - last_check >= 3:
        resized_ref = resize_reference(reference_img, 1280, 720)
        match = find_reference_location(screen_gray, resized_ref)

        if match:
            x, y = match
            cropped = screen_gray[y:y+720, x:x+1280]

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{event_abbr}_{timestamp}.png"

            local_path = os.path.join(tempfile.gettempdir(), filename)
            cv2.imwrite(local_path, cropped)
            upload_to_windows(local_path)
            os.remove(local_path)
        else:
            print("❌ Reference not found")

        last_check = time.time()

capture.release()
scp_client.close()
ssh_client.close()
print("🛑 Stopped.")
