#
# Core mesonconfig functions file
# 2026, Remeny
#

# ---[ Libraries ]--- #
import logging
from importlib.metadata import version as pkg_version
from datetime import datetime
from pathlib import Path

# ---[ Variables]--- #
# Minimum screen resolution
min_cols: int = 80
min_rows: int = 20

# ---[ Classes ]--- #

# ---[ Logging ]--- #
def log_debug(msg: str, log_file: str) -> None:
    """
    Log a debug message to a file in the format:
    [YYYY-MM-DD HH:MM:SS] <msg>
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"

    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)

# ---[ Version ]--- #
def get_version() -> str:
    return pkg_version("mesonconfig")
