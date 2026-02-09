#
# Core mesonconfig functions file
# 2026, Remeny
#

# ---[ Libraries ]--- #
import logging
from importlib.metadata import version as pkg_version

# ---[ Variables]--- #
# Minimum screen resolution
min_cols: int = 80
min_rows: int = 20

# ---[ Classes ]--- #

# ---[ Logging ]--- #
def setup_logging(debug: bool = False, logfile = None) -> None:
    handlers = []

    handlers.append(logging.StreamHandler())

    if logfile:
        handlers.append(logging.FileHandler(logfile, encoding="utf-8"))

    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )

log = logging.getLogger("mesonconfig")

# ---[ Version ]--- #
def get_version() -> str:
    return pkg_version("mesonconfig")

# ---[ Other stuff ]--- #
def get_options():
    return [
        ("enable_tests", True),
        ("use_system_lib", False),
        ("optimization", "O2"),
    ]


def set_option(name: str, value: str) -> None:
    print(f"Setting {name} = {value}")
