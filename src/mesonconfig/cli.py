#
# Regular Command-line interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from . import core, tui
import shutil, argparse

# ---[ Variables ]--- #
text_screen_size_less_than_min: str = ("Your display is too small to run Mesonconfig!\n"
                                      f"It must be at least {core.min_rows} lines by {core.min_cols} columns."
                                      )
verbose: bool = False

# ---[ Entry point ]--- #
def main():
    global verbose
    # Argument checking.
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--banana", action="store_true")
    args = parser.parse_args()

    if args.version:
        print("")
        print("Mesonconfig")
        print(core.get_version())
        print("Repository: github.com/stellcel-remeny/mesonconfig")
        print("")
        return
    
    elif args.verbose:
        if args.banana:
            import sys,time,zlib,base64
            from . import pukcell as _
            w=sys.stdout.write;s=time.sleep
            d=zlib.decompress(base64.b64decode(_.DATA))
            t=int(d.split(b"\n\n",1)[0].split()[2])/1e3
            for _ in d.split(b"\x1f")[1:]:w("\033[H\033[J"+_.decode());s(t)
            return
        verbose = True

    try:
        # Check if the terminal size is greater than or equal to minimum
        screen_size = shutil.get_terminal_size(fallback=(0, 0))
        if screen_size.columns < core.min_cols or screen_size.lines < core.min_rows:
            raise core.TerminalTooSmall
        
        tui.MCfgApp(verbose=verbose).run()
    
    except core.TerminalTooSmall:
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