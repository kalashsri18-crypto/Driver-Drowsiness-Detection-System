"""Eye Aspect Ratio (EAR) helpers.

EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
It stays roughly constant while the eye is open and drops towards 0 when it closes.
"""
import math

# MediaPipe Face Mesh landmark indices, ordered p1..p6 for each eye.
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def eye_aspect_ratio(points):
    """points: six (x, y) tuples ordered p1..p6. Returns the EAR as a float."""
    if len(points) != 6:
        raise ValueError("EAR needs exactly 6 eye landmark points")
    p1, p2, p3, p4, p5, p6 = points
    horizontal = _dist(p1, p4)
    if horizontal == 0:
        return 0.0
    return (_dist(p2, p6) + _dist(p3, p5)) / (2.0 * horizontal)
