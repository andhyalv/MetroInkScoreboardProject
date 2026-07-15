import os
import time
import cv2
import argparse
import datetime
import platform
import json
import glob

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
# Project reference images (now supports MULTIPLE templates)
# =========================
# Put all your sample screenshots of the scoreboard in a folder called
# "reference_images/" next to this script (e.g. different scores, lighting,
# mid-animation, etc). Every one of them is tried on every check.
REFERENCE_DIR = os.path.join(PROJECT_FOLDER, "reference_images")
reference_paths = sorted(glob.glob(os.path.join(REFERENCE_DIR, "*.jpg")) +
                          glob.glob(os.path.join(REFERENCE_DIR, "*.png")))

# Backward compatibility: fall back to the single old reference file if the
# folder doesn't exist yet.
if not reference_paths:
    legacy_path = os.path.join(PROJECT_FOLDER, "scoreboard_reference.jpg")
    if os.path.exists(legacy_path):
        reference_paths = [legacy_path]

if not reference_paths:
    print("❌ No reference images found in reference_images/ (or scoreboard_reference.jpg)")
    exit()

reference_imgs = []
for p in reference_paths:
    img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
    if img is not None:
        reference_imgs.append((os.path.basename(p), img))
    else:
        print(f"⚠️ Could not load reference image: {p}")

print(f"📸 Loaded {len(reference_imgs)} reference template(s): {[n for n, _ in reference_imgs]}")

# =========================
# Helper functions
# =========================
def resize_reference(reference_img, screen_w, screen_h):
    ref_h, ref_w = reference_img.shape[:2]
    if ref_w > screen_w or ref_h > screen_h:
        scale = min(screen_w / ref_w, screen_h / ref_h)
        return cv2.resize(reference_img, (int(ref_w * scale), int(ref_h * scale)))
    return reference_img

def find_best_match(screen_img, reference_imgs, screen_w, screen_h, threshold=0.3):
    """
    Try every reference template against the current frame.
    Returns (name, max_val, max_loc) for the BEST scoring template,
    plus a boolean for whether it cleared the threshold.
    This lets us log how close near-misses were, not just pass/fail.
    """
    best_name, best_val, best_loc = None, -1.0, None
    for name, ref in reference_imgs:
        resized_ref = resize_reference(ref, screen_w, screen_h)
        result = cv2.matchTemplate(screen_img, resized_ref, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > best_val:
            best_name, best_val, best_loc = name, max_val, max_loc
    return best_name, best_val, best_loc, (best_val >= threshold)

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
last_capture_time = 0
CAPTURE_COOLDOWN = 30
CHECK_INTERVAL = 1.0     # was 3s — tighter so short-lived boards aren't missed
MATCH_THRESHOLD = 0.3

# Optional: log every check's best score to a CSV so you can tune threshold
# and see near-misses after the event, instead of just "not found".
LOG_PATH = os.path.join(LOCAL_SAVE_FOLDER, "match_log.csv")
log_file = open(LOG_PATH, "a")
if os.path.getsize(LOG_PATH) == 0:
    log_file.write("timestamp,best_template,best_score,matched,saved\n")

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

    if time.time() - last_check >= CHECK_INTERVAL:
        name, score, loc, matched = find_best_match(
            screen_gray, reference_imgs, 1280, 720, threshold=MATCH_THRESHOLD
        )

        saved = False
        if matched:
            now = time.time()
            if now - last_capture_time >= CAPTURE_COOLDOWN:
                x, y = loc
                cropped = screen_gray[y:y+720, x:x+1280]
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"{STATION_NAME}_{event_abbr}_{timestamp}.png"
                local_path = os.path.join(LOCAL_SAVE_FOLDER, filename)
                cv2.imwrite(local_path, cropped)
                print(f"💾 Saved locally: {filename} (matched '{name}', score={score:.3f})")
                last_capture_time = now
                saved = True
            else:
                remaining = int(CAPTURE_COOLDOWN - (now - last_capture_time))
                print(f"⏳ Cooldown — skipping ({remaining}s remaining, would've matched '{name}', score={score:.3f})")
        else:
            print(f"❌ Reference not found (best='{name}', score={score:.3f})")

        log_file.write(f"{datetime.datetime.now().isoformat()},{name},{score:.4f},{matched},{saved}\n")
        log_file.flush()

        last_check = time.time()

log_file.close()
capture.release()
print("🛑 Stopped.")
