import csv
from datetime import datetime, timedelta

from config import DATETIME_FORMAT
from utils import load_data, save_data, score_color, bold, dim

SPARK = "▁▂▃▄▅▆▇█"


def _score_val(v):
    if isinstance(v, dict):
        return v
    return {"effort": v, "completed": v}


def streak(data=None):
    data = data if data is not None else load_data()
    logs = data.get("logs", [])
    if not logs:
        return 0

    dates = set()
    for l in logs:
        try:
            dates.add(datetime.strptime(l["timestamp"], DATETIME_FORMAT).date())
        except (KeyError, ValueError):
            continue
    if not dates:
        return 0

    today = datetime.now().date()
    cursor = today if today in dates else today - timedelta(days=1)
    if cursor not in dates:
        return 0

    count = 0
    while cursor in dates:
        count += 1
        cursor -= timedelta(days=1)
    return count


def permanent_averages(days=14, data=None):
    data = data if data is not None else load_data()
    logs = data.get("logs", [])[-days:]
    perms = {p["id"]: p["title"] for p in data.get("permanents", [])}

    results = {}
    for pid, title in perms.items():
        efforts, completes = [], []
        for l in logs:
            if pid in l:
                v = _score_val(l[pid])
                if v.get("effort") is not None:
                    efforts.append(v["effort"])
                if v.get("completed") is not None:
                    completes.append(v["completed"])
        if efforts or completes:
            results[pid] = {
                "title": title,
                "avg_effort": round(sum(efforts) / len(efforts), 1) if efforts else None,
                "avg_completed": round(sum(completes) / len(completes), 1) if completes else None,
                "n": max(len(efforts), len(completes)),
            }
    return results


def sparkline(values):
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    return "".join(SPARK[int((v - lo) / span * (len(SPARK) - 1))] for v in values)


def show_stats(days=14):
    data = load_data()
    print(f"{bold('Streak:')} {streak(data)} day(s)")

    print(f"\n{bold(f'Permanent tasks (last {days} logs)')}")
    avgs = permanent_averages(days, data=data)
    if not avgs:
        print(dim("  No data yet."))
    for pid, v in avgs.items():
        print(
            f"  {pid} - {v['title']}: "
            f"effort {score_color(v['avg_effort'])}  "
            f"completed {score_color(v['avg_completed'])}  "
            f"(n={v['n']})"
        )

    mood = data.get("mood_entries", [])[-days:]
    anx = data.get("anxiety_entries", [])[-days:]
    if mood:
        print(f"\n{bold('Energy trend:')}    {sparkline([m['energy'] for m in mood])}")
        print(f"{bold('Happiness trend:')} {sparkline([m['happiness'] for m in mood])}")
    if anx:
        print(f"{bold('Anxiety trend:')}   {sparkline([a['anxiety'] for a in anx])} (higher = worse)")


def show_status():
    data = load_data()
    print(f"{bold('Today:')} {datetime.now().strftime('%d %B, %Y')}")
    print(f"{bold('Streak:')} {streak(data)} day(s)")
    print(f"{bold('Last logged:')} {data.get('last_updated') or 'never'}")

    reasons = data.get("block_reasons", [])
    if reasons:
        print(f"{bold('Internet:')} blocked ({', '.join(reasons)})")
    else:
        print(f"{bold('Internet:')} open")

    settings = data.get("settings", {})
    meds = data.get("meds", {})
    if settings.get("medicine_enabled"):
        taken_today = meds.get("taken") and meds.get("date") == datetime.now().strftime("%Y-%m-%d")
        print(f"{bold('Meds today:')} {'taken' if taken_today else 'not yet'}")
    else:
        print(f"{bold('Meds module:')} off")


def undo_last_log():
    data = load_data()
    logs = data.get("logs", [])
    if not logs:
        print("Nothing to undo.")
        return
    removed = logs.pop()
    data["logs"] = logs
    save_data(data)
    print(f"Removed log from {removed.get('timestamp')}.")


def export_csv(path):
    data = load_data()
    logs = data.get("logs", [])
    perms = {p["id"]: p["title"] for p in data.get("permanents", [])}

    fieldnames = (
        ["timestamp"]
        + [f"{pid}_effort" for pid in perms]
        + [f"{pid}_completed" for pid in perms]
        + ["mood_energy", "mood_happiness", "anxiety", "meds"]
    )

    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for l in logs:
            row = {"timestamp": l.get("timestamp")}
            for pid in perms:
                v = _score_val(l.get(pid, {}))
                row[f"{pid}_effort"] = v.get("effort")
                row[f"{pid}_completed"] = v.get("completed")
            mood = l.get("mood", {})
            row["mood_energy"] = mood.get("energy")
            row["mood_happiness"] = mood.get("happiness")
            row["anxiety"] = l.get("anxiety")
            row["meds"] = l.get("meds", "")
            w.writerow(row)

    print(f"Exported {len(logs)} log(s) to {path}")
