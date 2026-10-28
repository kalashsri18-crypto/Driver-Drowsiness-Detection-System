"""Driver Drowsiness Detection - webcam prototype.

Uses the MediaPipe Face Landmarker to locate the eyes, computes the Eye Aspect Ratio (EAR)
every frame, and raises an alert when the eyes stay closed for too long.

Run:  python main.py            (press q to quit)
"""
import argparse
import os
import time
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from alert import beep
from drowsiness import DrowsinessMonitor
from ear import LEFT_EYE, RIGHT_EYE, eye_aspect_ratio


MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/face_landmarker/"
             "face_landmarker/float16/1/face_landmarker.task")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")


def ensure_model():
    """Download the MediaPipe face landmark model on first run (about 4 MB)."""
    if os.path.exists(MODEL_PATH):
        return
    print("Downloading face landmark model (one time only)...")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    except Exception as exc:
        raise SystemExit(
            f"Could not download the model: {exc}\n"
            f"Download it manually from:\n  {MODEL_URL}\n"
            f"and save it as:\n  {MODEL_PATH}")


def parse_args():
    p = argparse.ArgumentParser(description="Driver drowsiness detection (webcam prototype)")
    p.add_argument("--camera", type=int, default=0, help="webcam index (default 0)")
    p.add_argument("--threshold", type=float, default=0.21,
                   help="EAR below this counts as eyes closed (default 0.21)")
    p.add_argument("--seconds", type=float, default=1.5,
                   help="seconds of continuous eye closure before alert (default 1.5)")
    p.add_argument("--no-sound", action="store_true", help="disable the beep")
    return p.parse_args()


def eye_points(landmarks, indices, w, h):
    return [(landmarks[i].x * w, landmarks[i].y * h) for i in indices]


def main():
    args = parse_args()
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera {args.camera}")

    ensure_model()
    monitor = DrowsinessMonitor(args.threshold, args.seconds)
    options = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1)
    landmarker = vision.FaceLandmarker.create_from_options(options)
    start = time.monotonic()

    last_beep = 0.0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp_ms = int((time.monotonic() - start) * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            status, color = "No face detected", (0, 165, 255)
            if result.face_landmarks:
                lm = result.face_landmarks[0]
                left = eye_points(lm, LEFT_EYE, w, h)
                right = eye_points(lm, RIGHT_EYE, w, h)
                ear = (eye_aspect_ratio(left) + eye_aspect_ratio(right)) / 2.0
                drowsy, closed_for = monitor.update(ear)

                for x, y in left + right:
                    cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 0), -1)
                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, f"Eyes closed: {closed_for:.1f}s", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                if drowsy:
                    status, color = "DROWSY - WAKE UP!", (0, 0, 255)
                    now = time.monotonic()
                    if not args.no_sound and now - last_beep > 1.0:
                        beep()
                        last_beep = now
                else:
                    status, color = "Alert", (0, 200, 0)
            else:
                monitor.reset()

            cv2.putText(frame, status, (10, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
            cv2.imshow("Driver Drowsiness Detection (q to quit)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        landmarker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
