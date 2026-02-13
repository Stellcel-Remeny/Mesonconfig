#
# Regular Command-line interface for Mesonconfig
# 2026, Remeny
#

# TODO: If .mesonconfig.ini exist, use that for settings (eg. BKGD color, verbose, Default file to use instead of KConfig)
# TODO: Add functionality for --build-meson-options flag

# ---[ Libraries ]--- #
from mesonconfig.tui import app as tui
from mesonconfig.tui import config as tui_config
from mesonconfig import kconfig
from mesonconfig import core
from pathlib import Path
import shutil, argparse

# ---[ Functions ]--- #
### Debug ###
def _debug_display_menu_mockup(menu, kc, depth=0):
    indent = "  " * depth

    for entry in kc.get_visible_entries(menu.entries):
        if isinstance(entry, kconfig.KMenu):
            print(f"{indent}[+] {entry.title}")
            _debug_display_menu_mockup(entry, kc, depth + 1)

        elif isinstance(entry, kconfig.KChoice):
            print(f"{indent}( ) choice")
            for opt in entry.entries:
                state = "*" if opt.value else " "
                print(f"{indent}  ({state}) {opt.prompt}")

        elif isinstance(entry, kconfig.KOption):
            if entry.opt_type == "bool":
                state = "[X]" if entry.value else "[ ]"
                print(f"{indent}{state} {entry.prompt}")
            else:
                print(f"{indent}{entry.prompt}: {entry.value}")

        elif isinstance(entry, kconfig.KComment):
            print(f"{indent}# {entry.text}")

def kconfig_demo_funct(kconfig_file: str) -> None:
    kc = kconfig.KConfig(kconfig_file)
    kc.dump()
    print("===========")
    print("Extra stuff")
    print("Main menu:", kc.mainmenu)
    print("Example stuff (bool_show_cmd)")
    opt = kc.find_option("bool_show_cmd")
    print("Name:", opt.name)
    print("Type:", opt.opt_type)
    print("Default:", opt.default)
    print("Value:", opt.value)
    print("Help:\n", opt.help)
    
    print("===========")
    print("Now producing an edited file (.tmp.kconfig.dbg)")
    print("Result should be bool_show_cmd=y SRC=\"mysource\" and val_grub-boot_timeout=10")
    kc.set_option("bool_show_cmd", "y")
    kc.set_option("SRC", "\"mysource\"")
    kc.set_option("val_grub-boot_timeout", "10")
    kc.set_option("hide_this_funct", "n")
    kc.save_config(".tmp.kconfig.dbg")
    
    print("+++++++++")
    print("That's that. Now opening menu.")
    _debug_display_menu_mockup(kc, kc)
    
    print("\n++++\nDependency visibility:\n")
    opt = kc.find_option("sys_dir_newroot_etc")
    print("Sys_dir_newroot_etc depends on (own):", opt.depends_on)
    parent_dep = kc.get_option_parents("sys_dir_newroot_etc")
    print("Sys_dir_newroot_etc effective parent depends:", parent_dep)

    opt_bool = kc.find_option("bool_move_root")
    print("bool_move_root visible (own depends only):", kc.is_visible(opt_bool))

    print("sys_dir_newroot_etc visible:", kc.is_visible(opt))
    
    print("\n++++\nNew Organized Checks\n")

    def dump_visibility(opt_name):
        opt = kc.find_option(opt_name)
        parent = kc.get_option_parents(opt_name)
        print(f"Option: {opt_name}")
        print("  value:", opt.value)
        print("  own depends:", opt.depends_on)
        print("  parent depends:", parent)
        print("  visible:", kc.is_visible(opt))

    # Core tests
    dump_visibility("hide_this_funct")
    dump_visibility("bool_move_root")
    dump_visibility("sys_dir_newroot_etc")
    dump_visibility("sys_dir_apps")
    dump_visibility("bool_show_cmd_out_err")

#  --[ Custom help messages ]--  #
def custom_help(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.verbose:
        print("\nVerbosity makes the following changes:\n\n"
                "   - Enables secondary status bar (dbg() function messages)\n"
                "   - Use Q to quit TUI app\n"
             )
    else:
        parser.print_help()
        print(f"\n For more information on a flag, use --help with that flag. (not available for every flag)")

# ---[ Entry point ]--- #
def main():
    # Argument checking.
    parser = argparse.ArgumentParser(
        prog="mesonconfig",
        description="Configuration Utility for Meson projects",
        add_help=False
    )

    # --- I/O options ---
    io = parser.add_argument_group("Configuration")
    io.add_argument(
        "--build-meson-options", action="store_true", default=False,
        help="Generate a meson_options.txt file from the provided KConfig file."
    )
    io.add_argument(
        "--kconfig-file", metavar="<file>", default="KConfig",
        help="Path to the KConfig file to load."
    )
    io.add_argument(
        "--output-file", metavar="<file>", default="local.conf",
        help="Path to the output file to generate Local configuration."
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
    
    # --- Debug --- #
    debug = parser.add_argument_group("Debug")
    debug.add_argument(
        "--demo-kconfig", action="store_true", default=False,
        help="KConfig demo test (MarkedRain KConfig needed)."
    )
    debug.add_argument(
        "--verbose", action="store_true", default=False,
        help="Display verbose status messages."
    )

    # --- Other ---
    meta = parser.add_argument_group("Other")
    meta.add_argument(
        "--version", action="store_true", default=False,
        help="Display version information."
    )
    meta.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help message and exit."
    )

    # --- Positional ---
    parser.add_argument(
        "kconfig_positional",
        nargs="?",
        help="same as --kconfig-file"
    )

    args = parser.parse_args()

    # --- Version flag check --- #
    if args.version:
        if args.verbose and args.help:
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

    # --- Custom help messages --- #
    if args.help:
        custom_help(parser, args)
        return

    # --- Conditions before TUI --- #
    # If positional was provided and --kconfig-file was not explicitly used
    if args.kconfig_positional and args.kconfig_file == "KConfig":
        args.kconfig_file = args.kconfig_positional
    
    if not Path(args.kconfig_file).is_file():
        print(f"\nThe file '{args.kconfig_file}' does not exist.\n"
              f"Please create '{args.kconfig_file}', or supply correct path to\n"
              f"the KConfig file by using --kconfig-file\n"
             )
        return 1
    elif args.build_meson_options:
        # TODO: Add functionality...
        print(f"\nBuilding file 'meson_options.txt' using configuration from file '{args.kconfig_file}'...\n")
        print("!! Functionality not implemented yet as of this version !!\n")
        return 1
    

    # --- Other immediate argument checks --- #
    # Check if kconfig demo is enabled
    if args.demo_kconfig:
        kconfig_demo_funct(args.kconfig_file)
        return
    
    # Check if the terminal size is too small
    screen_size = shutil.get_terminal_size(fallback=(0, 0))
    if (screen_size.columns < core.min_cols or screen_size.lines < core.min_rows) and not args.override_minimum_size:
        print(f"\nYour display is too small to run Mesonconfig!\n"
            f"It must be at least {core.min_rows} lines by {core.min_cols} columns.\n"
            f"Current size: {screen_size.columns}x{screen_size.lines}\n"
            f"(use --override-minimum-size to bypass)\n"
        )
        return 1

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

    # Run tui here.
    try:        
        tui.MCfgApp(config=config).run()
     
    except Exception as e:
        import traceback
        print("Oops; An UNexpected error! :(")
        traceback.print_exc()
        print(" ) Figure out the error.")

if __name__ == "__main__":
    main()