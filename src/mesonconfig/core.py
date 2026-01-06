#
# Functions for use in mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
import logging

# ---[ Logging ]--- #
def setup_logging(debug=False, logfile=None):
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

# ---[ Other stuff ]--- #
def get_options():
    return [
        ("enable_tests", True),
        ("use_system_lib", False),
        ("optimization", "O2"),
    ]


def set_option(name, value):
    print(f"Setting {name} = {value}")
