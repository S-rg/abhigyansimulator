from utils import load_data, save_data, now_str, get_score, score_color


def prompt_mood():
    print("Mood check-in")
    energy = get_score("  Energy (0-100): ")
    happiness = get_score("  Happiness (0-100): ")
    return energy, happiness


def prompt_anxiety():
    print("Anxiety check-in")
    return get_score("  Anxiety, higher = worse (0-100): ")


def log_mood():
    energy, happiness = prompt_mood()
    data = load_data()
    data.setdefault("mood_entries", []).append(
        {"timestamp": now_str(), "energy": energy, "happiness": happiness}
    )
    save_data(data)
    print(f"Logged - energy {score_color(energy)}, happiness {score_color(happiness)}")
    return energy, happiness


def log_anxiety():
    level = prompt_anxiety()
    data = load_data()
    data.setdefault("anxiety_entries", []).append(
        {"timestamp": now_str(), "anxiety": level}
    )
    save_data(data)
    print(f"Logged - anxiety {score_color(level)}")
    return level


def _print_history(entries, n, fields):
    if not entries:
        print("No entries yet.")
        return
    for e in entries[-n:]:
        parts = ", ".join(f"{f}={e[f]}" for f in fields if f in e)
        print(f"{e['timestamp']}  {parts}")


def mood_history(n=10):
    data = load_data()
    _print_history(data.get("mood_entries", []), n, ["energy", "happiness"])


def anxiety_history(n=10):
    data = load_data()
    _print_history(data.get("anxiety_entries", []), n, ["anxiety"])
