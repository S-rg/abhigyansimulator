import blocking
import meds
import meters
from utils import load_data, save_data, now_str, get_score, today_key, yes_no


def get_task_scores(label):
    effort = get_score(f"  {label}: tried (0-100): ")
    completed = get_score(f"  {label}: completed (0-100): ")
    return {"effort": effort, "completed": completed}


def get_todo_list():
    todo_list = []
    i = 0

    while True:
        ans = input(f"Enter todo {i + 1} (blank or 'done' to finish): ").strip()

        if ans.lower() in ("done", ""):
            if len(todo_list) < 3:
                print("Bro put at least 3 things")
                continue
            return todo_list

        todo_list.append({"id": "T" + str(i + 1), "title": ans})
        i += 1


def log():
    data = load_data()
    entry = {"timestamp": now_str()}
    permanents = data.get("permanents", [])

    if permanents:
        print("\n=== Permanent tasks ===")
        for permanent in permanents:
            print(f"{permanent['id']} - {permanent['title']}")
            entry[permanent["id"]] = get_task_scores(permanent["title"])

    logs = data.setdefault("logs", [])
    if logs and logs[-1].get("todo"):
        print("\n=== Yesterday's todos ===")
        for todo in logs[-1]["todo"]:
            print(f"{todo['id']} - {todo['title']}")
            entry[todo["id"]] = get_task_scores(todo["title"])

    print("\n=== Mood & anxiety ===")
    energy, happiness = meters.prompt_mood()
    anxiety = meters.prompt_anxiety()
    entry["mood"] = {"energy": energy, "happiness": happiness}
    entry["anxiety"] = anxiety

    settings = data.get("settings", {})
    if settings.get("medicine_enabled"):
        print("\n=== Medicine ===")
        meds_data = data.get("meds", {})
        if meds_data.get("taken") and meds_data.get("date") == today_key():
            print("Meds already marked as taken today.")
            entry["meds"] = True
        else:
            meds_taken = yes_no("Have you taken your meds today? (y/n): ")
            if meds_taken:
                meds_state = data.setdefault("meds", {})
                meds_state["date"] = today_key()
                meds_state["taken"] = True
                meds_state["snooze_until"] = None
                print("Meds marked as taken for today. Nice.")
            entry["meds"] = meds_taken

    print("\n=== Tomorrow's todos ===")
    entry["todo"] = get_todo_list()

    logs.append(entry)
    data.setdefault("mood_entries", []).append(
        {"timestamp": entry["timestamp"], "energy": energy, "happiness": happiness}
    )
    data.setdefault("anxiety_entries", []).append(
        {"timestamp": entry["timestamp"], "anxiety": anxiety}
    )
    data["last_updated"] = now_str()
    save_data(data)
    blocking.unblock("daily_log")
    if entry.get("meds"):
        blocking.unblock("meds")

    print("\nLogged. Nice work.")
    return 0
