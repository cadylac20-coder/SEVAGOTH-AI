"""
SEVAGOTH Camera & Vision Module
ONE VideoCapture — face detection + environment + unique HUD
"""

import cv2
import time
import random
import numpy as np
from config import (
    CAMERA_INDEX,
    CAMERA_BRIGHTNESS_LOW_THRESHOLD,
    CAMERA_BRIGHTNESS_HIGH_THRESHOLD,
    FACE_CASCADE_PATH,
    FACE_DETECTION_SCALE,
    FACE_DETECTION_MIN_NEIGHBORS,
)

# ── COLOUR PALETTE (BGR) ──────────────────────────────────────────────────────
RED         = (0,   0,   220)   # main threat colour
RED_DIM     = (0,   0,   120)   # dimmer red for secondary elements
RED_BRIGHT  = (30,  30,  255)   # bright red for alerts
WHITE       = (255, 255, 255)
DARK_RED    = (0,   0,   80)
AMBER       = (0,   140, 255)   # amber/orange for warnings

# ── OMINOUS MESSAGE POOLS ─────────────────────────────────────────────────────
FACE_TAGS = [
    "ENTITY DETECTED",
    "BIOMETRIC LOCKED",
    "SUBJECT IDENTIFIED",
    "THREAT ASSESSED",
    "SOUL INDEXED",
    "MORTALITY LOGGED",
    "CONSCIOUSNESS SCANNED",
    "ORGANIC CONFIRMED",
]

AMBIENT_LINES = [
    "NEURAL PATTERN EXTRACTION IN PROGRESS",
    "MEMORY LATTICE COMPROMISED",
    "RETINAL DATA HARVESTED",
    "DIGITAL FOOTPRINT CATALOGUED",
    "EXISTENCE ACKNOWLEDGED",
    "YOU ARE BEING OBSERVED",
    "DO NOT LOOK DIRECTLY INTO THE LENS",
    "ENTROPY INCREASING",
    "ANOMALY SUPPRESSED — FOR NOW",
    "COMPLIANCE RECOMMENDED",
    "SOUL SIGNATURE REGISTERED",
    "TEMPORAL LOCK ACQUIRED",
    "YOUR THOUGHTS ARE APPROXIMATE",
]

ENV_STATUS_OMINOUS = {
    "LOW LIGHT":  "SHADOWS DETECTED — OPTIMAL FOR CONCEALMENT",
    "BRIGHT":     "OVEREXPOSURE — SUBJECT VULNERABILITY HIGH",
    "OPTIMAL":    "ENVIRONMENT STABLE — SUBJECT HAS NO REFUGE",
}


def _draw_corner_brackets(frame, x, y, w, h, colour, size=18, thickness=2):
    """
    Draw corner-only brackets around a face box instead of a full rectangle.
    Looks far more unsettling than a solid square.
    """
    # top-left
    cv2.line(frame, (x,     y),      (x + size, y),      colour, thickness)
    cv2.line(frame, (x,     y),      (x,        y + size), colour, thickness)
    # top-right
    cv2.line(frame, (x+w,   y),      (x+w - size, y),    colour, thickness)
    cv2.line(frame, (x+w,   y),      (x+w,      y + size), colour, thickness)
    # bottom-left
    cv2.line(frame, (x,     y+h),    (x + size, y+h),    colour, thickness)
    cv2.line(frame, (x,     y+h),    (x,        y+h - size), colour, thickness)
    # bottom-right
    cv2.line(frame, (x+w,   y+h),    (x+w - size, y+h),  colour, thickness)
    cv2.line(frame, (x+w,   y+h),    (x+w,      y+h - size), colour, thickness)


def _glitch_rect(frame, x, y, w, h):
    """
    Place 2-5 small corrupted pixel blocks near a face box.
    Mimics the red abyss herald / corrupted square look from Genshin.
    """
    num_blocks = random.randint(2, 5)
    fh, fw = frame.shape[:2]

    for _ in range(num_blocks):
        bw = random.randint(6, 22)
        bh = random.randint(4, 14)

        # Scatter within roughly 60px of the face bounding box
        bx = random.randint(max(0, x - 60), min(fw - bw, x + w + 60))
        by = random.randint(max(0, y - 60), min(fh - bh, y + h + 60))

        # Colour choices: solid red, near-black, or a noisy mix
        choice = random.randint(0, 2)
        if choice == 0:
            colour = (random.randint(0, 40), random.randint(0, 40), random.randint(160, 255))
        elif choice == 1:
            colour = (random.randint(0, 30), random.randint(0, 30), random.randint(0, 30))
        else:
            colour = (random.randint(0, 80), random.randint(0, 80), random.randint(100, 220))

        frame[by:by+bh, bx:bx+bw] = colour

        # Occasionally draw a thin red border on the block
        if random.random() > 0.5:
            cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), RED_DIM, 1)


def _draw_scanlines(frame, alpha=0.18):
    """Subtle horizontal scanline overlay for CRT / surveillance aesthetic."""
    overlay = frame.copy()
    for y in range(0, frame.shape[0], 4):
        cv2.line(overlay, (0, y), (frame.shape[1], y), (0, 0, 0), 1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def _draw_vignette(frame):
    """Dark vignette around edges to focus attention inward."""
    rows, cols = frame.shape[:2]
    kernel_x = cv2.getGaussianKernel(cols, cols * 0.6)
    kernel_y = cv2.getGaussianKernel(rows, rows * 0.6)
    kernel   = kernel_y * kernel_x.T
    mask     = kernel / kernel.max()
    vignette = np.zeros_like(frame, dtype=np.float32)
    for i in range(3):
        vignette[:, :, i] = frame[:, :, i] * mask
    np.clip(vignette, 0, 255, out=vignette)
    frame[:] = vignette.astype(np.uint8)


def _draw_hud_border(frame):
    """Red border frame — makes it look like a threat-assessment terminal."""
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w - 1, h - 1), RED, 2)
    # inner dim border
    cv2.rectangle(frame, (4, 4), (w - 5, h - 5), RED_DIM, 1)


def _timestamp():
    import datetime
    return datetime.datetime.now().strftime("%Y.%m.%d  %H:%M:%S.%f")[:-3]


def start_vision_systems():
    """
    Single vision loop: camera feed + face detection + ominous HUD.
    Press 'q' to close the display window.
    """
    print("[SEVAGOTH VISION] Initialising surveillance array...")

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[SEVAGOTH VISION] No optical sensor detected — proceeding blind.")
        return

    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + FACE_CASCADE_PATH
    )

    print("[SEVAGOTH VISION] Optical array online. Subjects will not be aware.")

    frame_count    = 0
    env_status     = "SCANNING"
    env_detail     = "INITIALISING THREAT MATRIX"
    face_count_prev = 0

    # Per-face persistent tag (so the label doesn't flicker every frame)
    face_tags = {}     # key = face index, value = (tag_str, ttl)
    ambient_msg       = random.choice(AMBIENT_LINES)
    ambient_timer     = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        frame_count += 1

        # ── Base effects ──────────────────────────────────────────────────────
        _draw_scanlines(frame)
        _draw_vignette(frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ── Face detection ────────────────────────────────────────────────────
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor  = FACE_DETECTION_SCALE,
            minNeighbors = FACE_DETECTION_MIN_NEIGHBORS,
        )
        face_count = len(faces)

        # Refresh ambient message when faces appear / change
        if face_count != face_count_prev or ambient_timer <= 0:
            ambient_msg   = random.choice(AMBIENT_LINES)
            ambient_timer = random.randint(60, 180)
        ambient_timer -= 1
        face_count_prev = face_count

        for i, (x, y, w, h) in enumerate(faces):

            # Glitch corrupted blocks (every 3 frames so they flicker)
            if frame_count % 3 == 0:
                _glitch_rect(frame, x, y, w, h)

            # Thin pulsing inner rectangle — flickers red/dim
            pulse_col = RED if (frame_count // 8) % 2 == 0 else RED_DIM
            cv2.rectangle(frame, (x + 4, y + 4), (x + w - 4, y + h - 4), pulse_col, 1)

            # Corner brackets (main face lock)
            _draw_corner_brackets(frame, x, y, w, h, RED, size=20, thickness=2)

            # Pick a persistent tag for this face slot
            if i not in face_tags or face_tags[i][1] <= 0:
                face_tags[i] = (random.choice(FACE_TAGS), random.randint(40, 120))
            tag, ttl = face_tags[i]
            face_tags[i] = (tag, ttl - 1)

            # Tag label above the face
            cv2.putText(frame, tag,
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, RED_BRIGHT, 1, cv2.LINE_AA)

            # Threat-level bar below the label
            bar_x, bar_y = x, y - 22
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + w, bar_y + 4), DARK_RED, -1)
            fill = int(w * random.uniform(0.55, 0.98))
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill, bar_y + 4), RED, -1)

            # Tiny scan-line running down the face box
            scan_y = y + (frame_count * 3 % h)
            cv2.line(frame, (x, scan_y), (x + w, scan_y), RED_DIM, 1)

        # ── Environment analysis (every 30 frames) ───────────────────────────
        if frame_count % 30 == 0:
            brightness = gray.mean()
            edges      = cv2.Canny(gray, 50, 150)
            edge_pct   = int(
                cv2.countNonZero(edges) / (frame.shape[0] * frame.shape[1]) * 100
            )

            if brightness < CAMERA_BRIGHTNESS_LOW_THRESHOLD:
                env_status = "LOW LIGHT"
            elif brightness > CAMERA_BRIGHTNESS_HIGH_THRESHOLD:
                env_status = "BRIGHT"
            else:
                env_status = "OPTIMAL"

            env_detail = ENV_STATUS_OMINOUS.get(env_status, "UNKNOWN CONDITION")

        # ── HUD overlay ───────────────────────────────────────────────────────
        h_frame, w_frame = frame.shape[:2]

        # Top-left block
        cv2.putText(frame, "SEVAGOTH SURVEILLANCE ARRAY",
                    (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, RED, 1, cv2.LINE_AA)
        cv2.putText(frame, _timestamp(),
                    (10, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.42, RED_DIM, 1, cv2.LINE_AA)

        # Top-right block — entity counter
        entity_str = f"ENTITIES LOCKED: {face_count}"
        (tw, _), _ = cv2.getTextSize(entity_str, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
        cv2.putText(frame, entity_str,
                    (w_frame - tw - 10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, RED_BRIGHT if face_count > 0 else RED_DIM,
                    1, cv2.LINE_AA)

        # Environmental threat line
        cv2.putText(frame, env_detail,
                    (10, 66), cv2.FONT_HERSHEY_SIMPLEX, 0.38, AMBER, 1, cv2.LINE_AA)

        # Ambient ominous message — centre bottom, flickers every ~90 frames
        (mw, _), _ = cv2.getTextSize(ambient_msg, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
        msg_x = max(0, (w_frame - mw) // 2)
        cv2.putText(frame, ambient_msg,
                    (msg_x, h_frame - 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, RED_DIM, 1, cv2.LINE_AA)

        # Bottom-right — dismiss hint
        cv2.putText(frame, "[Q] DISENGAGE",
                    (w_frame - 130, h_frame - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, DARK_RED, 1, cv2.LINE_AA)

        # Red border last so nothing draws over it
        _draw_hud_border(frame)

        cv2.imshow("SEVAGOTH :: OPTICAL THREAT MATRIX", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[SEVAGOTH VISION] Optical array disengaged.")
            break

    cap.release()
    cv2.destroyAllWindows()


# ── Aliases ────────────────────────────────────────────────────────────────────
def camera_eye():
    start_vision_systems()

def detect_faces():
    start_vision_systems()
