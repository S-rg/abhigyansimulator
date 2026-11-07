import os
from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent


def _resolve_path(env_var: str, default: Path) -> Path:
    val = os.environ.get(env_var)
    if not val:
        return default
    p = Path(val)
    if p.exists():
        return p
    if default.exists():
        return default
    return p


FNAME: Path = _resolve_path("ABHIGYANSIM_DATA_FILE", BASE_DIR / "data.json")

DATETIME_FORMAT: str = "%d %B, %Y %I:%M %p"

BLOCK_SCRIPT: Path = _resolve_path(
    "ABHIGYANSIM_BLOCK_SCRIPT", BASE_DIR / "blocker" / "blockinternet"
)
UNBLOCK_SCRIPT: Path = _resolve_path(
    "ABHIGYANSIM_UNBLOCK_SCRIPT", BASE_DIR / "blocker" / "unblockinternet"
)

MEDS_SNOOZE_MINUTES: int = int(os.environ.get("ABHIGYANSIM_MEDS_SNOOZE_MIN", "10"))

DEFAULT_BLOCK_HOUR: int = 23

DEFAULT_MEDS_BLOCK_HOUR: int = int(os.environ.get("ABHIGYANSIM_MEDS_BLOCK_HOUR", str(DEFAULT_BLOCK_HOUR)))
