import subprocess

from config import BLOCK_SCRIPT, UNBLOCK_SCRIPT
from utils import load_data, save_data


def block(reason):
    data = load_data()
    reasons = set(data.get("block_reasons", []))
    was_blocked = bool(reasons)

    if reason in reasons:
        return

    reasons.add(reason)
    data["block_reasons"] = sorted(reasons)
    data["blocked"] = True
    save_data(data)

    if not was_blocked:
        try:
            subprocess.run(["sudo", str(BLOCK_SCRIPT)], check=False)
        except FileNotFoundError:
            pass
        print(f"Internet blocked ({reason}).")


def unblock(reason):
    data = load_data()
    reasons = set(data.get("block_reasons", []))

    if reason not in reasons:
        return

    reasons.discard(reason)
    data["block_reasons"] = sorted(reasons)
    data["blocked"] = bool(reasons)
    save_data(data)

    if not reasons:
        try:
            subprocess.run(["sudo", str(UNBLOCK_SCRIPT)], check=False)
        except FileNotFoundError:
            pass
        print("Internet unblocked.")


def active_reasons():
    return load_data().get("block_reasons", [])
