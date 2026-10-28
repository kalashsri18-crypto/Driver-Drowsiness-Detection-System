"""Tracks how long the eyes have stayed closed and decides when to raise an alert."""
import time


class DrowsinessMonitor:
    def __init__(self, ear_threshold=0.21, closed_seconds=1.5):
        self.ear_threshold = ear_threshold
        self.closed_seconds = closed_seconds
        self._closed_since = None

    def update(self, ear, now=None):
        """Feed the latest EAR. Returns (is_drowsy, seconds_closed)."""
        now = time.monotonic() if now is None else now
        if ear < self.ear_threshold:
            if self._closed_since is None:
                self._closed_since = now
            elapsed = now - self._closed_since
        else:
            self._closed_since = None
            elapsed = 0.0
        return elapsed >= self.closed_seconds, elapsed

    def reset(self):
        self._closed_since = None
