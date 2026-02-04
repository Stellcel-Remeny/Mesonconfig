#
# Configuration storage for current session of Mesonconfig [Immutable]
# ( Appearance of the application )
# 2026, Remeny
#

from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    background: str = "blue"
    verbose: bool = False
    window_color: str = "black"
    window_background: str = "lightgrey"