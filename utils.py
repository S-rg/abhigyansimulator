import json
import shutil
import subprocess
import sys
from copy import deepcopy
from datetime import datetime

from config import FNAME, DATETIME_FORMAT, DEFAULT_BLOCK_HOUR

DEFAULT_DATA = {
    "permanents": [],
    "logs": [],
    "mood_entries": [],
    "anxiety_entries": [],
    "meds": {"date": None, "taken": False, "snooze_until": None},
    "settings": {
        "medicine_enabled": False,
        "block_hour": DEFAULT_BLOCK_HOUR,
        "meds_block_hour": DEFAULT_BLOCK_HOUR,
    },
    "block_reasons": [],
    "blocked": False,
    "last_updated": None,
}


def load_data():
    if not FNAME.exists():
        data = deepcopy(DEFAULT_DATA)
        save_data(data)
        return data

    with open(FNAME, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            backup = FNAME.with_suffix(".json.bak")
            if backup.exists():
                print(f"data.json was corrupted - restoring from {backup.name}")
                with open(backup, "r") as bf:
                    data = json.load(bf)
            else:
                raise

    changed = False
    for key, default in DEFAULT_DATA.items():
        if key not in data:
            data[key] = deepcopy(default)
            changed = True
    if changed:
        save_data(data)
    return data


def save_data(data):
    FNAME.parent.mkdir(parents=True, exist_ok=True)
    if FNAME.exists():
        try:
            shutil.copy(FNAME, FNAME.with_suffix(".json.bak"))
        except OSError:
            pass
    tmp = FNAME.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    tmp.replace(FNAME)


def now_str():
    return datetime.now().strftime(DATETIME_FORMAT)


def today_key():
    return datetime.now().strftime("%Y-%m-%d")


def is_interactive():
    return sys.stdin.isatty()


def notify(title, message):
    if not shutil.which("notify-send"):
        return
    try:
        subprocess.run(
            ["notify-send", title, message],
            check=False,
            timeout=5,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def _c(code, text):
    if not sys.stdout.isatty():
        return str(text)
    return f"\033[{code}m{text}\033[0m"


def green(t):
    return _c("32", t)


def yellow(t):
    return _c("33", t)


def red(t):
    return _c("31", t)


def bold(t):
    return _c("1", t)


def dim(t):
    return _c("2", t)


def score_color(value):
    if value is None:
        return dim("-")
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    if v >= 80:
        return green(value)
    if v >= 50:
        return yellow(value)
    return red(value)


def get_score(prompt):
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print("Give me a number bro, don't make life hard.")
            continue
        try:
            val = float(raw)
        except ValueError:
            print("Numbers only, e.g. 75")
            continue
        if 0 < val <= 1:
            val *= 100
        if val < 0:
            print("Has to be more than 0.")
            continue
        val = min(100, val)
        return int(val) if val == int(val) else round(val, 1)


def yes_no(prompt):
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Just y or n please.")
