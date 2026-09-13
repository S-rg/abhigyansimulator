import meters
from utils import load_data, save_data, now_str, get_score


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

    print("\nLogged. Nice work.")
    return 0
