import os
import time
import cv2
import random
import paramiko
from scp import SCPClient
import argparse
import datetime

# =========================
# SSH SETTINGS
# =========================
WINDOWS_USER = "andhy"
WINDOWS_IP = "192.168.8.131"
DEST_FOLDER = "C:/Users/andhy/Andhy_Main/Code/Completed_Utilities/MetroStats/ScoreboardScreenshots/station_a"

# =========================
# Parse filename from Pi server (used only for event abbreviation)
# =========================
parser = argparse.ArgumentParser()
parser.add_argument("--filename", required=True)
args = parser.parse_args()
initial_filename = args.filename

# Extract event abbreviation from initial filename
event_abbr = initial_filename.split("_")[0]

# =========================
# SCP client
# =========================
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(WINDOWS_IP, username=WINDOWS_USER)
scp_client = SCPClient(ssh_client.get_transport())

# =========================
# Reference image
# =========================
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
REFERENCE_IMAGE_PATH = os.path.join(BASE_PATH, "scoreboard_reference.jpg")
reference_img = cv2.imread(REFERENCE_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if reference_img is None:
    print("❌ Reference image missing:", REFERENCE_IMAGE_PATH)
    exit()

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
    print("❌ No capture device found.")
    return None

def upload_to_windows(file_path):
    try:
        scp_client.put(file_path, DEST_FOLDER)
        print(f"📤 Uploaded {os.path.basename(file_path)} to Station A")
    except Exception as e:
        print("❌ Upload failed:", e)

# =========================
# Capture init
# =========================
capture = get_capture_device()
if capture is None:
    exit()
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

last_check = time.time()
STATION_NAME = "Station A"
print(f"🚀 {STATION_NAME} detection script running headlessly...")

# =========================
# Main loop
# =========================
while True:
    ret, frame = capture.read()
    if not ret:
        print("❌ Frame grab failed.")
        break

    frame_resized = cv2.resize(frame, (1280, 720))
    screen_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    if time.time() - last_check >= 3:
        resized_ref = resize_reference(reference_img, 1280, 720)
        match = find_reference_location(screen_gray, resized_ref)

        if match:
            x, y = match
            cropped = screen_gray[y:y+720, x:x+1280]  # adjust if needed

            # Generate new filename for each capture
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # up to microseconds
            filename = f"{event_abbr}_{timestamp}.png"

            # Save locally and upload
            local_path = os.path.join("/tmp", filename)
            cv2.imwrite(local_path, cropped)
            upload_to_windows(local_path)
            os.remove(local_path)

        else:
            print("❌ Reference not found.")

        last_check = time.time()

capture.release()
scp_client.close()
ssh_client.close()
print("🛑 Capture stopped.")
