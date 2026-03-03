import os
import time
import cv2
import argparse
import datetime
import platform
import json
import tempfile

# =========================
# Load configuration
# =========================
PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_FOLDER, "config.json")
EXAMPLE_CONFIG_PATH = os.path.join(PROJECT_FOLDER, "config.example.json")

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
elif os.path.exists(EXAMPLE_CONFIG_PATH):
    print("⚠️ config.json not found, using config.example.json")
    with open(EXAMPLE_CONFIG_PATH, "r") as f:
        config = json.load(f)
else:
    print("❌ No config.json or config.example.json found")
    exit()

STATION_NAME = config.get("station_name", platform.node())
LOCAL_SAVE_FOLDER = config.get("local_save_folder", os.path.join(PROJECT_FOLDER, "captures"))

os.makedirs(LOCAL_SAVE_FOLDER, exist_ok=True)

# =========================
# Parse filename/event info from API server
# =========================
parser = argparse.ArgumentParser()
parser.add_argument("--filename", required=True)
args = parser.parse_args()
initial_filename = args.filename
event_abbr = initial_filename.split("_")[0]

# =========================
# Project reference image
# =========================
REFERENCE_IMAGE_PATH = os.path.join(PROJECT_FOLDER, "scoreboard_reference.jpg")
reference_img = cv2.imread(REFERENCE_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if reference_img is None:
    print("❌ Missing scoreboard_reference.jpg at:", REFERENCE_IMAGE_PATH)
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
    print("❌ No capture device found")
    return None

# =========================
# Video capture setup
# =========================
capture = get_capture_device()
if capture is None:
    exit()

capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print(f"🚀 Detection running on {STATION_NAME}")
last_check = time.time()

# =========================
# Main loop
# =========================
while True:
    ret, frame = capture.read()
    if not ret:
        print("❌ No frame")
        break

    frame_resized = cv2.resize(frame, (1280, 720))
    screen_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    if time.time() - last_check >= 3:  # check every 3 seconds
        resized_ref = resize_reference(reference_img, 1280, 720)
        match = find_reference_location(screen_gray, resized_ref)

        if match:
            x, y = match
            cropped = screen_gray[y:y+720, x:x+1280]

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{STATION_NAME}_{event_abbr}_{timestamp}.png"
            local_path = os.path.join(LOCAL_SAVE_FOLDER, filename)

            cv2.imwrite(local_path, cropped)
            print(f"💾 Saved locally: {filename}")
        else:
            print("❌ Reference not found")

        last_check = time.time()

capture.release()
print("🛑 Stopped.")