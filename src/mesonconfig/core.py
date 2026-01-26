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
class TerminalTooSmall(Exception):
    """Raised when the terminal size is below the minimum required."""
    pass

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

def meatball():
    import sys,time,zlib,base64
    from . import pukcell as _
    w=sys.stdout.write;s=time.sleep
    d=zlib.decompress(base64.b64decode(_.DATA))
    t=int(d.split(b"\n\n",1)[0].split()[2])/1e3
    for _ in d.split(b"\x1f")[1:]:w("\033[H\033[J"+_.decode());s(t)
