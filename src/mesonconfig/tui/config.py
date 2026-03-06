#
# Configuration storage for current session of Mesonconfig
# 2026, Remeny
#

from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    # Stuff in here should not be changed (unless user tells to)
    background: str
    window_border: str
    window_color: str
    window_background: str
    
    disable_minimum_size_check: bool
    
    verbose: bool
    
    kconfig_file: str
    output_file: str
    
    logging: bool = False          # Enable/disable logging
    log_file: str = None           # Path to logfile
    debug_timer: float = 0.5       # Time to display dbg messages

@dataclass
class UIState:
    # Stuff in here can be changed by program
    content_hidden: bool = False
    secondary_visible: bool = False
    other_windows_are_open: bool = False
    last_status_text: str = ""
