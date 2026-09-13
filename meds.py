from datetime import datetime, timedelta

import blocking
from config import MEDS_SNOOZE_MINUTES
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
    print(f"Medicine reminders: {'ON' if settings['medicine_enabled'] else 'OFF'}")
    if settings["medicine_enabled"]:
        print(f"Taken today: {'yes' if meds['taken'] else 'no'}")
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

    if not data["settings"]["medicine_enabled"]:
        save_data(data)
        return

    if data["meds"]["taken"]:
        save_data(data)
        return

    now = datetime.now()
    snooze_until_raw = data["meds"]["snooze_until"]

    if snooze_until_raw is None:
        save_data(data)
        answer = _ask(meds_only=False)
        if answer is True:
            mark_taken()
        else:
            snooze()
        return

    snooze_until = datetime.fromisoformat(snooze_until_raw)
    if now < snooze_until:
        save_data(data)
        return  

    save_data(data)
    blocking.block(REASON)
    answer = _ask(meds_only=True)
    if answer is True:
        mark_taken()
    else:
        snooze()
