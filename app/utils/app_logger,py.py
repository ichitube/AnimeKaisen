import os
import threading
from datetime import datetime
from collections import deque

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

MAX_LINES = 10_000
_lock = threading.Lock()

# кеш последних строк
_log_buffer = deque(maxlen=MAX_LINES)


def _ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


def _load_existing():
    if not os.path.exists(LOG_FILE):
        return
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f.readlines()[-MAX_LINES:]:
                _log_buffer.append(line.rstrip("\n"))
    except Exception:
        pass


_ensure_log_dir()
_load_existing()


def log(event: str, *, user_id=None, level="INFO", extra=None):
    """
    event  – текст события
    user_id – опционально
    level – INFO | WARN | ERROR | CRIT
    extra – dict или str
    """
    with _lock:
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        line = f"[{ts}] [{level}]"

        if user_id is not None:
            line += f" [uid={user_id}]"

        line += f" {event}"

        if extra:
            line += f" | {extra}"

        _log_buffer.append(line)
        _flush()


def _flush():
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            for line in _log_buffer:
                f.write(line + "\n")
    except Exception:
        pass
