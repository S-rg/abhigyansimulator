import os
import sys
from datetime import datetime, timedelta

# Ensure consistent path regardless of scope
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import DATETIME_FORMAT, DEFAULT_BLOCK_HOUR
from utils import load_data 
import blocking  

REASON = "daily_log"

def main():
    data = load_data()
    last_updated_str = data.get("last_updated")

    if not last_updated_str:
        return

    last_updated = datetime.strptime(last_updated_str, DATETIME_FORMAT)
    block_hour = data.get("settings", {}).get("block_hour", DEFAULT_BLOCK_HOUR)

    deadline = (last_updated + timedelta(days=1)).replace(
        hour=block_hour, minute=0, second=0, microsecond=0
    )

    is_late = datetime.now() > deadline

    if is_late:
        blocking.block(REASON)
    else:
        blocking.unblock(REASON)


if __name__ == "__main__":
    main()