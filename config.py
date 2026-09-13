import os
from pathlib import Path

FNAME: Path = Path(
    os.environ.get("ABHIGYANSIM_DATA_FILE", "")
)

DATETIME_FORMAT: str = "%d %B, %Y %I:%M %p"

BLOCK_SCRIPT: Path = Path(
    os.environ.get("ABHIGYANSIM_BLOCK_SCRIPT", "")
)
UNBLOCK_SCRIPT: Path = Path(
    os.environ.get("ABHIGYANSIM_UNBLOCK_SCRIPT", "")
)

# How long the medicine module waits
MEDS_SNOOZE_MINUTES: int = int(os.environ.get("ABHIGYANSIM_MEDS_SNOOZE_MIN", "10"))

# Hour (24h clock) by which you must have logged, or the blocker kicks in.
DEFAULT_BLOCK_HOUR: int = 23
