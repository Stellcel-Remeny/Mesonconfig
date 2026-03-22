#
# Configuration storage for current session of Mesonconfig
# 2026, Remeny
#

from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    # Stuff in here should not be changed (unless user tells to)
    kconfig_file: str = "KConfig"                   # Path to KConfig file to load
    output_file: str = "local.conf"                 # File to write config to on save (and load from on start)

    background: str = "blue"                        # Background of the whole application
    window_border: str = "solid"                    # Border style of Windows
    window_color: str = "black"                     # Foreground color of Windows
    window_background: str = "lightgrey"            # Background color of Windows
    
    disable_autoconfig: bool = False                # If true, the app will not load settings set in the output_file, using only defaults from KConfig file.
    disable_minimum_size_check: bool = False        # If true, the app will not check for minimum terminal size and will not hide content if the terminal is too small.
    
    verbose: bool = False                           # Enable/disable verbose mode
    logging: bool = False                           # Enable/disable logging
    log_file: str = None                            # Path to logfile
    debug_timer: float = 0.5                        # Time to display dbg messages

@dataclass
class UIState:
    # Stuff in here can be changed by program
    content_hidden: bool = False
    secondary_visible: bool = False
    other_windows_are_open: bool = False
    last_status_text: str = ""
