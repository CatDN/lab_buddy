# 21/03/2026

import cv2
import threading
import time
from ultralytics import YOLO
import numpy as np


nano_model = YOLO("yolo26n.pt")
pose_model = YOLO("yolo26n-pose.pt")

_running = False
_latest_frame = None

latest_result = {
    "present": False,
    "confidence": 0.0,
    "pose_safe": None,
    "moving": None,
    "seconds_still": 0,
    "description": "No data yet"
}

MOTION_THRESHOLD  = 500
STILLNESS_SECONDS = 10

_prev_frame_gray = None
_last_motion_time = time.time()

def _is_pose_safe(keypoints):
    try:
        head_y     = keypoints[0][1]
        shoulder_y = (keypoints[5][1] + keypoints[6][1]) / 2
        return float(head_y) < float(shoulder_y)
    except:
        return None

def _is_moving(frame):
    global _prev_frame_gray, _last_motion_time

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if _prev_frame_gray is None:
        _prev_frame_gray = gray
        return True

    diff = cv2.absdiff(_prev_frame_gray, gray)
    _prev_frame_gray = gray

    changed_pixels = np.sum(diff > 25)

    if changed_pixels > MOTION_THRESHOLD:
        _last_motion_time = time.time()
        return True

    seconds_still = time.time() - _last_motion_time
    return seconds_still < STILLNESS_SECONDS

def _build_description(present, confidence, pose_safe, moving, seconds_still):
    if not present:
        return "No person detected."

    desc = f"Person detected ({confidence:.0%} confidence). "

    if pose_safe is True:
        desc += "Pose appears safe — head is above shoulders. "
    elif pose_safe is False:
        desc += "Pose appears unsafe — head is below shoulders, person may be slumped. "
    else:
        desc += "Pose unclear — keypoints not visible. "

    if moving:
        desc += "Person is moving."
    else:
        desc += f"Person has been still for {seconds_still}s."

    return desc

def _camera_loop():
    global latest_result, _latest_frame
    cam = cv2.VideoCapture(0)

    while _running:
        ret, frame = cam.read()
        if not ret:
            continue

        _latest_frame = frame.copy()

        # person detection
        nano_results = nano_model(frame, verbose=False)
        persons = [b for b in nano_results[0].boxes if int(b.cls) == 0]
        present    = len(persons) > 0
        confidence = float(persons[0].conf) if present else 0.0

        pose_safe = None
        moving    = None
        seconds_still = round(time.time() - _last_motion_time)

        if present:
            # pose check
            pose_results = pose_model(frame, verbose=False)
            if pose_results[0].keypoints is not None:
                kps = pose_results[0].keypoints.xy
                if len(kps) > 0:
                    pose_safe = _is_pose_safe(kps[0])

            # motion check
            moving = _is_moving(frame)
            seconds_still = round(time.time() - _last_motion_time)

        latest_result = {
            "present":      present,
            "confidence":   confidence,
            "pose_safe":    pose_safe,
            "moving":       moving,
            "seconds_still": seconds_still,
            "description":  _build_description(present, confidence, pose_safe, moving, seconds_still)
        }

        annotated_frame = pose_results[0].plot() if present else nano_results[0].plot()

        status = "Moving" if moving else f"Still for {seconds_still}s"
        color  = (0, 255, 0) if moving else (0, 165, 255) if seconds_still < STILLNESS_SECONDS else (0, 0, 255)
        cv2.putText(annotated_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        screen_w = 1219
        screen_h = 820
        half_w = screen_w // 2

        # resize frame to fill left half of screen
        resized = cv2.resize(annotated_frame, (half_w, screen_h))

        cv2.namedWindow("YOLO Camera", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("YOLO Camera", half_w, screen_h)
        cv2.moveWindow("YOLO Camera", 0, 0)  # top left corner
        cv2.imshow("YOLO Camera", resized)
        cv2.setWindowProperty("YOLO Camera", cv2.WND_PROP_TOPMOST, 1)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

def start_camera():
    global _running
    _running = True
    threading.Thread(target=_camera_loop, daemon=True).start()
    time.sleep(5)

def stop_camera():
    global _running
    _running = False

def check_camera() -> dict:
    """Returns the latest camera analysis result."""
    return latest_result

def get_latest_frame():
    """Returns the latest raw frame for sending to Gemini or email."""
    return _latest_frame

if __name__ == "__main__":
    start_camera()
    for _ in range(30):
        time.sleep(0.5)
        r = latest_result
        print(f"Present: {r['present']} — Pose safe: {r['pose_safe']} — Moving: {r['moving']} — {r['description']}")
    stop_camera()
    print("Done.")