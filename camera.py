# 21/03/2026

import cv2
import threading
import time
from ultralytics import YOLO
import numpy as np

nano_model = YOLO("yolo26n.pt")
pose_model = YOLO("yolo26n-pose.pt")

_running = False
latest_result = {"present": False, "confidence": 0.0, "pose_safe": None}

MOTION_THRESHOLD = 500     # minimum pixel difference to count as movement
STILLNESS_SECONDS = 10     # seconds of no movement before flagging

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

def _camera_loop():
    global latest_result
    cam = cv2.VideoCapture(0)

    while _running:
        ret, frame = cam.read()
        if not ret:
            continue

        # person detection
        nano_results = nano_model(frame, verbose=False)
        persons = [b for b in nano_results[0].boxes if int(b.cls) == 0]
        present = len(persons) > 0
        confidence = float(persons[0].conf) if present else 0.0

        pose_safe = None
        moving = None

        if present:
            # pose check
            pose_results = pose_model(frame, verbose=False)
            if pose_results[0].keypoints is not None:
                kps = pose_results[0].keypoints.xy
                if len(kps) > 0:
                    pose_safe = _is_pose_safe(kps[0])

            # motion check
            moving = _is_moving(frame)

        latest_result = {
            "present": present,
            "confidence": confidence,
            "pose_safe": pose_safe,
            "moving": moving
        }

        annotated_frame = pose_results[0].plot() if present else nano_results[0].plot()

        # overlay motion and stillness status
        seconds_still = round(time.time() - _last_motion_time)
        status = "Moving" if moving else f"Still for {seconds_still}s"
        color = (0, 255, 0) if moving else (0, 165, 255) if seconds_still < STILLNESS_SECONDS else (0, 0, 255)
        cv2.putText(annotated_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("YOLO Camera", annotated_frame)
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

if __name__ == "__main__":
    start_camera()
    for _ in range(30):
        time.sleep(0.5)
        r = latest_result
        print(f"Present: {r['present']} — Pose safe: {r['pose_safe']} — Moving: {r['moving']}")
    stop_camera()
    print("Done.")