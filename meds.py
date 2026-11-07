from datetime import datetime, timedelta

import blocking
from config import MEDS_SNOOZE_MINUTES, DEFAULT_MEDS_BLOCK_HOUR
from utils import load_data, save_data, today_key, is_interactive, notify, yes_no

REASON = "meds"


def _ensure_state(data):
    settings = data.setdefault("settings", {})
    settings.setdefault("medicine_enabled", False)

    meds = data.setdefault("meds", {})
    if meds.get("date") != today_key():
        meds["date"] = today_key()
        meds["taken"] = False
        meds["snooze_until"] = None
    meds.setdefault("taken", False)
    meds.setdefault("snooze_until", None)
    return data


def enable():
    data = _ensure_state(load_data())
    data["settings"]["medicine_enabled"] = True
    save_data(data)
    print("Medicine reminders turned ON.")


def disable():
    data = _ensure_state(load_data())
    data["settings"]["medicine_enabled"] = False
    save_data(data)
    blocking.unblock(REASON) 
    print("Medicine reminders turned OFF.")


def mark_taken():
    data = _ensure_state(load_data())
    data["meds"]["taken"] = True
    data["meds"]["snooze_until"] = None
    save_data(data)
    blocking.unblock(REASON)
    print("Meds marked as taken for today. Nice.")


def snooze():
    data = _ensure_state(load_data())
    data["meds"]["snooze_until"] = (
        datetime.now() + timedelta(minutes=MEDS_SNOOZE_MINUTES)
    ).isoformat()
    save_data(data)
    print(f"Ok, I'll check again in {MEDS_SNOOZE_MINUTES} minutes.")


def status():
    data = _ensure_state(load_data())
    settings = data["settings"]
    meds = data["meds"]
    block_hour = settings.get(
        "meds_block_hour",
        settings.get("block_hour", DEFAULT_MEDS_BLOCK_HOUR),
    )
    print(f"Medicine reminders: {'ON' if settings['medicine_enabled'] else 'OFF'}")
    if settings["medicine_enabled"]:
        print(f"Taken today: {'yes' if meds['taken'] else 'no'}")
        print(f"Block deadline: {block_hour:02d}:00")
        if meds["snooze_until"] and not meds["taken"]:
            print(f"Next check: {meds['snooze_until']}")


def _ask(meds_only):
    if not meds_only:
        print("\nHave you taken your meds today?")

    if is_interactive():
        return yes_no("Taken? (y/n): ")

    notify(
        "Meds check-in",
        "Have you taken your meds today? Run: abhigyansimulator meds yes",
    )
    return None 


def check():
    data = _ensure_state(load_data())
    save_data(data)

    if not data["settings"]["medicine_enabled"]:
        blocking.unblock(REASON)
        return

    if data["meds"]["taken"]:
        blocking.unblock(REASON)
        return

    now = datetime.now()
    block_hour = data.get("settings", {}).get(
        "meds_block_hour",
        data.get("settings", {}).get("block_hour", DEFAULT_MEDS_BLOCK_HOUR),
    )

    deadline = now.replace(hour=block_hour, minute=0, second=0, microsecond=0)
    is_late = now >= deadline

    snooze_until_raw = data["meds"]["snooze_until"]
    if snooze_until_raw is not None:
        snooze_until = datetime.fromisoformat(snooze_until_raw)
        if now < snooze_until:
            return

    if not is_late:
        blocking.unblock(REASON)
        return

    blocking.block(REASON)
    answer = _ask(meds_only=True)
    if answer is True:
        mark_taken()
    else:
        snooze()
