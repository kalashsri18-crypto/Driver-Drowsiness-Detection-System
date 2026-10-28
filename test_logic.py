"""Tests for the pure-Python logic (no camera or MediaPipe needed).  Run: python test_logic.py"""
from drowsiness import DrowsinessMonitor
from ear import eye_aspect_ratio

OPEN = [(0, 0), (1, -1), (2, -1), (3, 0), (2, 1), (1, 1)]
CLOSED = [(0, 0), (1, -0.1), (2, -0.1), (3, 0), (2, 0.1), (1, 0.1)]


def test_ear_open_vs_closed():
    assert eye_aspect_ratio(OPEN) > 0.5
    assert eye_aspect_ratio(CLOSED) < 0.1


def test_alert_after_long_closure():
    m = DrowsinessMonitor(0.21, 1.5)
    assert m.update(0.1, now=0.0) == (False, 0.0)
    assert m.update(0.1, now=1.0)[0] is False
    assert m.update(0.1, now=1.6)[0] is True


def test_blink_does_not_alert_and_resets():
    m = DrowsinessMonitor(0.21, 1.5)
    m.update(0.1, now=0.0)
    m.update(0.3, now=0.2)           # eyes reopen
    assert m.update(0.1, now=1.0)[0] is False   # timer restarted
    assert m.update(0.1, now=2.4)[0] is False
    assert m.update(0.1, now=2.6)[0] is True


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
