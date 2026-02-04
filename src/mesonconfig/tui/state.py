#
# UI State file for current session of Mesonconfig
# ( Stuff happening currently )
# 2026, Remeny
#

from dataclasses import dataclass

@dataclass
class UIState:
    # Stuff in here can be changed.
    content_hidden: bool = False
    secondary_visible: bool = False
    last_status_text: str = ""
