from utils import load_data, save_data


def add_permanent(text: str):
    text = text.strip()
    if not text:
        print("Can't add an empty permanent task.")
        return

    data = load_data()
    data.setdefault("permanents", [])
    new_id = "P" + str(len(data["permanents"]) + 1)
    data["permanents"].append({"id": new_id, "title": text})
    save_data(data)
    print(f"Added {new_id} - {text}")


def list_permanents():
    data = load_data()
    perms = data.get("permanents", [])
    if not perms:
        print("No permanent tasks yet. Add with: add permanent <title>")
        return
    for p in perms:
        print(f"{p['id']} - {p['title']}")


def remove_permanent(pid: str):
    data = load_data()
    perms = data.get("permanents", [])
    match = next((p for p in perms if p["id"] == pid), None)
    if not match:
        print(f"No permanent task with id {pid}")
        return
    perms.remove(match)
    data["permanents"] = perms
    save_data(data)
    print(f"Removed {pid} - {match['title']}")


def rename_permanent(pid: str, new_title: str):
    new_title = new_title.strip()
    data = load_data()
    for p in data.get("permanents", []):
        if p["id"] == pid:
            old = p["title"]
            p["title"] = new_title
            save_data(data)
            print(f"Renamed {pid}: '{old}' -> '{new_title}'")
            return
    print(f"No permanent task with id {pid}")
