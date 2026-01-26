#
# Regular Command-line interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from .core import *
from .tui import *
import shutil

# ---[ Variables ]--- #
text_screen_size_less_than_min: str = ("Your display is too small to run Mesonconfig!\n"
                                      f"It must be at least {min_rows} lines by {min_cols} columns."
                                      )

# ---[ Entry point ]--- #
def main():
    # Argument checking.
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()

    if args.version:
        print("")
        print("Mesonconfig")
        print(get_version())
        print("Repository: github.com/stellcel-remeny/mesonconfig")
        print("")
        return

    try:
        # Check if the terminal size is greater than or equal to minimum
        screen_size = shutil.get_terminal_size(fallback=(0, 0))
        if screen_size.columns < min_cols or screen_size.lines < min_rows:
            raise TerminalTooSmall
        
        MCfgApp().run()
    
    except TerminalTooSmall:
        # Screen size is too small.
        screen_size = shutil.get_terminal_size(fallback=(0, 0))
        print(text_screen_size_less_than_min)
        print(f"Current size: {screen_size.columns}x{screen_size.lines}")
    
    except Exception as e:
        import traceback
        print("Oops; An UNexpected error! :(")
        traceback.print_exc()
        print(" ) Figure out the error.")

if __name__ == "__main__":
    main()