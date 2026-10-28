"""Simple audible alert that works without extra dependencies."""
import sys
import threading


def _beep():
    if sys.platform.startswith("win"):
        import winsound
        winsound.Beep(1800, 400)
    else:
        sys.stdout.write("\a")
        sys.stdout.flush()


def beep():
    """Play the alert in a background thread so the video loop never blocks."""
    threading.Thread(target=_beep, daemon=True).start()
