# Abhigyan Simulator

A personal daily-accountability CLI inspired by a good friend, with ... incentives.

## Setup

Needs Python 3.9+, nothing else (no pip installs required).
Set an environment variable before running (e.g. in `~/.bashrc`):

```bash
export ABHIGYANSIM_DATA_FILE="$HOME/abhigyansimulator/data.json"
export ABHIGYANSIM_BLOCK_SCRIPT="$HOME/abhigyansimulator/blocker/blockinternet"
export ABHIGYANSIM_UNBLOCK_SCRIPT="$HOME/abhigyansimulator/blocker/unblockinternet"
```

**Sudo:** `blockinternet` / `unblockinternet` use `iptables` and need root. Add a NOPASSWD rule these via `sudo visudo`:

```bash
yourusername ALL=(ALL) NOPASSWD: /path/to/abhigyansimulator/blocker/blockinternet, /path/toabhigyansimulator/blocker/unblockinternet
```

## Commands

```bash
abhigyansimulator log                          # do today's full log
abhigyansimulator add permanent "Exercise"      # add a permanent task
abhigyansimulator permanents                    # list permanent tasks
abhigyansimulator permanents remove P1
abhigyansimulator permanents rename P1 "New title"

abhigyansimulator meds on / off                 # toggle the meds module
abhigyansimulator meds yes                      # mark meds taken today
abhigyansimulator meds no                       # snooze the reminder
abhigyansimulator meds status
abhigyansimulator meds check                    # cron-safe, see below

abhigyansimulator mood log                      # quick energy/happiness check-in
abhigyansimulator mood history [n]
abhigyansimulator anxiety log                   # quick anxiety check-in
abhigyansimulator anxiety history [n]

abhigyansimulator status                        # today's dashboard
abhigyansimulator stats [--days N]              # streaks, averages, trends
abhigyansimulator undo                          # remove the last daily log
abhigyansimulator export csv out.csv

abhigyansimulator config show
abhigyansimulator config set block_hour 22
abhigyansimulator config set medicine_enabled true

abhigyansimulator blocker check                 
```

Two wrapper scripts, `run_blocker.sh` and `run_meds.sh`, are included - they `cd` into the project, run the right check, and append output to `logfile.log` so you can see what cron's been doing. Crontab:

```
*/2 * * * * /path/to/abhigyansimulator/run_meds.sh
*/5 * * * * /path/to/abhigyansimulator/run_blocker.sh
```