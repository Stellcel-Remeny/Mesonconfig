#
# Regular Command-line interface for Mesonconfig
# 2026, Remeny
#

# TODO: If .mesonconfig.ini exist, use that for settings (eg. BKGD color, verbose, Default file to use instead of KConfig)

# ---[ Libraries ]--- #
from mesonconfig.tui import app as tui
from mesonconfig import core
import shutil, argparse

# ---[ Entry point ]--- #
def main():
    # Argument checking.
    parser = argparse.ArgumentParser()
    parser.add_argument("--background", metavar="<color>", default="#0037DA",
                        help="Background color for the screen.")
    
    parser.add_argument("--window_color", metavar="<color>", default="black",
                        help="Foreground color for the windows.")
    parser.add_argument("--window_background", metavar="<color>", default="#CCCCCC",
                        help="Background color for the windows.")
    
    parser.add_argument("--override-minimum-size", action="store_true", default=False,
                        help="Disables the terminal minimum size check.")
    
    parser.add_argument("--verbose", action="store_true", default=False,
                        help="Display verbose status messages.")
    parser.add_argument("--version", action="store_true", default=False,
                        help="Display version information.")
    args = parser.parse_args()

    if args.version:
        if args.verbose:
            import sys,time,zlib,base64
            from . import pukcell as _
            w=sys.stdout.write;s=time.sleep
            d=zlib.decompress(base64.b64decode(_.DATA))
            t=int(d.split(b"\n\n",1)[0].split()[2])/1e3
            for _ in d.split(b"\x1f")[1:]:w("\033[H\033[J"+_.decode());s(t)
            return
        print("")
        print("Mesonconfig")
        print(core.get_version())
        print("Repository: github.com/stellcel-remeny/mesonconfig")
        print("")
        return

    # Run tui here.
    try:
        # Check if the terminal size is greater than or equal to minimum
        screen_size = shutil.get_terminal_size(fallback=(0, 0))
        if (screen_size.columns < core.min_cols or screen_size.lines < core.min_rows) and not args.override_minimum_size:
            raise core.TerminalTooSmall
        
        tui.MCfgApp(background=args.background.lower(),
                    window_color=args.window_color.lower(),
                    window_background=args.window_background.lower(),
                    disable_minimum_size_check=args.override_minimum_size,
                    verbose=args.verbose).run()
    
    except core.TerminalTooSmall:
        # Screen size is too small.
        screen_size = shutil.get_terminal_size(fallback=(0, 0))
        print(f"\nYour display is too small to run Mesonconfig!\n"
              f"It must be at least {core.min_rows} lines by {core.min_cols} columns.\n"
              f"Current size: {screen_size.columns}x{screen_size.lines}\n"
              f"(use --override-minimum-size to bypass)\n"
        )
    
    except Exception as e:
        import traceback
        print("Oops; An UNexpected error! :(")
        traceback.print_exc()
        print(" ) Figure out the error.")

if __name__ == "__main__":
    main()