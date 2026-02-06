#
# Configuration storage for current session of Mesonconfig [Immutable]
# ( Appearance of the application )
# 2026, Remeny
#

from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    background: str
    window_border: str
    window_color: str
    window_background: str
    
    disable_minimum_size_check: bool
    
    verbose: bool
    
    kconfig_file: str
    output_file: str