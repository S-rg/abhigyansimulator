import sys
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
            res = subprocess.run(["sudo", str(BLOCK_SCRIPT)], check=False)
            if res.returncode != 0:
                print(f"Warning: sudo failed with exit code {res.returncode}", file=sys.stderr)
        except FileNotFoundError:
            print(f"Error: block script not found at {BLOCK_SCRIPT}", file=sys.stderr)
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
            res = subprocess.run(["sudo", str(UNBLOCK_SCRIPT)], check=False)
            if res.returncode != 0:
                print(f"Warning: sudo failed with exit code {res.returncode}", file=sys.stderr)
        except FileNotFoundError:
            print(f"Error: unblock script not found at {UNBLOCK_SCRIPT}", file=sys.stderr)
        print("Internet unblocked.")


def active_reasons():
    return load_data().get("block_reasons", [])
