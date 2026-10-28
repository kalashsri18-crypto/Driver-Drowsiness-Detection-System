# Driver Drowsiness Detection

A webcam-based student prototype that watches a driver's eyes and raises an alert when they stay closed for too long.

## How it works
1. OpenCV captures webcam frames.
2. MediaPipe Face Landmarker finds the eye landmarks (the ~4 MB model file is downloaded automatically on first run; needs internet once).
3. The **Eye Aspect Ratio (EAR)** is computed for both eyes. EAR stays roughly constant when the eye is open and falls close to 0 when it closes.
4. If EAR stays below a threshold for a set time (default 1.5 s), the app shows a red **DROWSY** warning and beeps. A normal blink does not trigger it.

## Setup
```bash
pip install -r requirements.txt
python main.py
```
Press `q` to quit.

### Options
| Flag | Default | Meaning |
|---|---|---|
| `--camera` | 0 | Webcam index |
| `--threshold` | 0.21 | EAR below this = eyes closed |
| `--seconds` | 1.5 | Closed time before alert |
| `--no-sound` | off | Disable beep |

If it triggers too easily or not at all, adjust `--threshold` (try 0.18 to 0.25) for your face and camera.

## Tests
```bash
python test_logic.py
```
Covers the EAR calculation and the alert timing logic (no camera needed).

## Project files
- `main.py` - webcam loop and on-screen display
- `ear.py` - EAR calculation and landmark indices
- `drowsiness.py` - eye-closure timer / alert decision
- `alert.py` - beep

## Limitations
- Prototype tested on a webcam, not in a real vehicle. It is **not** a certified safety device.
- Accuracy is not formally validated. Lighting, glasses, camera angle and head pose affect results.
- Detects prolonged eye closure only; it does not detect yawning or head nodding.
