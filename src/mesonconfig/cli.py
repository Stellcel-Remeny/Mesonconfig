#
# Regular Command-line interface for Mesonconfig
# 2026, Remeny
#

# TODO: If .mesonconfig.ini exist, use that for settings (eg. BKGD color, verbose, Default file to use instead of KConfig)

# ---[ Libraries ]--- #
from mesonconfig.tui import app as tui
from mesonconfig.tui import config as tui_config
from mesonconfig import core
import shutil, argparse

# ---[ Entry point ]--- #
def main():
    # Argument checking.
    parser = argparse.ArgumentParser(
        prog="mesonconfig",
        description="Configuration Utility for Meson projects"
    )

    # --- I/O options ---
    io = parser.add_argument_group("Configuration")
    io.add_argument(
        "--kconfig-file", metavar="<file>", default="KConfig",
        help="Path to the KConfig file to load."
    )
    io.add_argument(
        "--output-file", metavar="<file>", default="local.conf",
        help="Path to the output file to generate."
    )

    # --- Appearance options --- #
    ui = parser.add_argument_group("Appearance")
    ui.add_argument(
        "--background", metavar="<color>", default="#0037DA",
        help="Background color for the screen."
    )
    ui.add_argument(
        "--window-border", metavar="<style>", default="solid",
        help="Border style for the windows (solid, dashed, etc.)"
    )
    ui.add_argument(
        "--window-color", metavar="<color>", default="black",
        help="Foreground color for the windows."
    )
    ui.add_argument(
        "--window-background", metavar="<color>", default="#CCCCCC",
        help="Background color for the windows."
    )

    # --- Behavior / runtime options ---
    runtime = parser.add_argument_group("Advanced")
    runtime.add_argument(
        "--override-minimum-size", action="store_true", default=False,
        help="Disables the terminal minimum size check."
    )
    runtime.add_argument(
        "--verbose", action="store_true", default=False,
        help="Display verbose status messages."
    )

    # --- Other ---
    meta = parser.add_argument_group("Other")
    meta.add_argument(
        "--version", action="store_true", default=False,
        help="Display version information."
    )

    args = parser.parse_args()

    # Build config object for the app.
    config = tui_config.AppConfig(
        background=args.background.lower(),
        window_border=args.window_border.lower(),
        window_color=args.window_color.lower(),
        window_background=args.window_background.lower(),
        
        disable_minimum_size_check=args.override_minimum_size,
        verbose=args.verbose,
        
        kconfig_file=args.kconfig_file,
        output_file=args.output_file
    )

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
        
        tui.MCfgApp(config=config).run()
    
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