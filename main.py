import sys
import json
import argparse

import create
import log as log_mod
import meds
import meters
import stats
from utils import load_data, save_data


def build_parser():
    p = argparse.ArgumentParser(
        prog="abhigyansimulator", description="Personal daily accountability tracker."
    )
    sub = p.add_subparsers(dest="command")

    sub.add_parser("log", help="Do today's daily log")

    add_p = sub.add_parser("add", help="Add something")
    add_sub = add_p.add_subparsers(dest="add_what")
    perm_add = add_sub.add_parser("permanent", help="Add a permanent task")
    perm_add.add_argument("title", nargs="+")

    perm_p = sub.add_parser("permanents", help="List / manage permanent tasks")
    perm_sub = perm_p.add_subparsers(dest="perm_action")
    perm_sub.add_parser("list", help="List permanent tasks")
    perm_rm = perm_sub.add_parser("remove", help="Remove a permanent task")
    perm_rm.add_argument("id")
    perm_rn = perm_sub.add_parser("rename", help="Rename a permanent task")
    perm_rn.add_argument("id")
    perm_rn.add_argument("title", nargs="+")

    meds_p = sub.add_parser("meds", help="Medicine reminder module")
    meds_sub = meds_p.add_subparsers(dest="meds_action")
    meds_sub.add_parser("on", help="Turn medicine reminders on")
    meds_sub.add_parser("off", help="Turn medicine reminders off")
    meds_sub.add_parser("yes", help="Mark meds as taken today")
    meds_sub.add_parser("no", help="Snooze the meds reminder")
    meds_sub.add_parser("status", help="Show meds status")
    meds_sub.add_parser("check", help="Run the meds check (cron-safe, use this in crontab)")

    mood_p = sub.add_parser("mood", help="Mood meter (energy + happiness)")
    mood_sub = mood_p.add_subparsers(dest="mood_action")
    mood_sub.add_parser("log", help="Log your current mood")
    mhist = mood_sub.add_parser("history", help="Show recent mood entries")
    mhist.add_argument("n", nargs="?", type=int, default=10)

    anx_p = sub.add_parser("anxiety", help="Anxiety meter")
    anx_sub = anx_p.add_subparsers(dest="anx_action")
    anx_sub.add_parser("log", help="Log your current anxiety level")
    ahist = anx_sub.add_parser("history", help="Show recent anxiety entries")
    ahist.add_argument("n", nargs="?", type=int, default=10)

    sub.add_parser("status", help="Today's dashboard")

    stats_p = sub.add_parser("stats", help="Streaks, averages, trends")
    stats_p.add_argument("--days", type=int, default=14)

    sub.add_parser("undo", help="Remove the most recent daily log entry")

    export_p = sub.add_parser("export", help="Export data")
    export_sub = export_p.add_subparsers(dest="export_what")
    csv_p = export_sub.add_parser("csv")
    csv_p.add_argument("path")

    cfg_p = sub.add_parser("config", help="View/change settings")
    cfg_sub = cfg_p.add_subparsers(dest="cfg_action")
    cfg_sub.add_parser("show")
    cfg_set = cfg_sub.add_parser("set")
    cfg_set.add_argument("key")
    cfg_set.add_argument("value")

    blocker_p = sub.add_parser("blocker", help="Daily-log lateness blocker (cron-safe)")
    blocker_sub = blocker_p.add_subparsers(dest="blocker_action")
    blocker_sub.add_parser("check")

    return p


def config_show():
    data = load_data()
    print(json.dumps(data.get("settings", {}), indent=2))


def config_set(key, value):
    data = load_data()
    settings = data.setdefault("settings", {})

    if key in ("block_hour", "meds_block_hour"):
        try:
            value = int(value)
        except ValueError:
            print(f"{key} must be an integer 0-23")
            return
        if not (0 <= value <= 23):
            print(f"{key} must be 0-23")
            return
    elif key == "medicine_enabled":
        value = value.strip().lower() in ("1", "true", "yes", "on")
    else:
        print(f"Unknown setting: {key}")
        return

    settings[key] = value
    save_data(data)
    print(f"Set {key} = {value}")


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    try:
        if args.command == "log":
            log_mod.log()

        elif args.command == "add":
            if args.add_what == "permanent":
                create.add_permanent(" ".join(args.title))
            else:
                parser.parse_args(["add", "--help"])

        elif args.command == "permanents":
            action = args.perm_action or "list"
            if action == "list":
                create.list_permanents()
            elif action == "remove":
                create.remove_permanent(args.id)
            elif action == "rename":
                create.rename_permanent(args.id, " ".join(args.title))

        elif args.command == "meds":
            action = args.meds_action or "status"
            {
                "on": meds.enable,
                "off": meds.disable,
                "yes": meds.mark_taken,
                "no": meds.snooze,
                "status": meds.status,
                "check": meds.check,
            }[action]()

        elif args.command == "mood":
            action = args.mood_action or "log"
            if action == "log":
                meters.log_mood()
            elif action == "history":
                meters.mood_history(args.n)

        elif args.command == "anxiety":
            action = args.anx_action or "log"
            if action == "log":
                meters.log_anxiety()
            elif action == "history":
                meters.anxiety_history(args.n)

        elif args.command == "status":
            stats.show_status()

        elif args.command == "stats":
            stats.show_stats(args.days)

        elif args.command == "undo":
            stats.undo_last_log()

        elif args.command == "export":
            if args.export_what == "csv":
                stats.export_csv(args.path)

        elif args.command == "config":
            action = args.cfg_action or "show"
            if action == "show":
                config_show()
            elif action == "set":
                config_set(args.key, args.value)

        elif args.command == "blocker":
            if args.blocker_action == "check":
                from blocker import blocker as blocker_mod

                blocker_mod.main()

    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)


if __name__ == "__main__":
    main()
