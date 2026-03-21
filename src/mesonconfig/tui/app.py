#
# Textual-based TUI interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig import core
from mesonconfig.tui.css import app_css
from mesonconfig.tui.status.status_mixin import StatusMixin
from mesonconfig.tui.chrome.window_mixin import WindowChromeMixin
from mesonconfig.tui.lifecycle.handlers import LifecycleHandlers
from mesonconfig.tui.config import AppConfig, UIState
from mesonconfig.tui.widgets.menu import MenuDisplay
from mesonconfig.tui.widgets.string import StringEditScreen
from mesonconfig.tui.widgets.integer import IntegerEditScreen
from mesonconfig.tui.widgets.help import HelpScreen
from mesonconfig.tui.widgets.exit import ConfirmExitScreen
from mesonconfig.kconfig import KConfig, KMenu, KOption, KComment
# textual tui libs
from textual.app import App
from textual.widgets import Label
from textual.containers import Container, Vertical
# Other libs
from pathlib import Path

# ---[ Main TUI Interface ]--- #
class MCfgApp(
    App,
    StatusMixin,
    WindowChromeMixin,
    LifecycleHandlers
):
    #  --[ Key bindings ]--  #
    BINDINGS = [
        ("up", "cursor_up", ""),
        ("down", "cursor_down", ""),
        ("left", "control_left", ""),
        ("right", "control_right", ""),
        ("space", "activate", ""),
        ("escape", "escape_key", ""),
    ]

    #  --[ On class create ]--  #
    def __init__(
        self,
        config: AppConfig = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        if not isinstance(config, AppConfig):
            raise TypeError(
                f"config must be an AppConfig, got {type(config).__name__}"
            )
        self.config: AppConfig = config
        self.kconfig = KConfig(self.config.kconfig_file)
        
        # navigation stack
        self.menu_stack = []  # holds KMenu objects
        
        self.state = UIState()
        self._esc_timer = None
        self._focus_mode = "list"
        self._control_index = 0
        self._last_escape_time = 0.0  # for double escape detection in Exit window
    
    #  --[ Style ]--  #
    @property
    def CSS(self) -> str:
        return app_css(
            background=self.config.background,
            window_border=self.config.window_border,
            window_bg=self.config.window_background,
            window_fg=self.config.window_color
        )

    #  --[ On class mount ]--  #
    def on_mount(self) -> None:
        super().on_mount()

        # No output_file provided -> stop.
        if not self.config.output_file:
            raise ValueError("No output file provided.")

        # auto-load existing output file unless disabled
        if self.config.disable_autoconfig:
            self.dbg("Autoload config is disabled, skipping loading existing config.")
        else:
            try:
                self.kconfig.load_config(path = self.config.output_file)
                self.dbg(f"Loaded existing config: {self.config.output_file}")
            except FileNotFoundError:
                self.dbg(f"No existing config found at: {self.config.output_file}")
            except Exception as e:
                self.dbg(f"Error loading existing config {self.config.output_file}: {e}")            

        # Schedule render_entries to happen after current event loop
        self.call_later(self.render_entries)
        self.set_timer(0.3, lambda: self.dbg("Debug text will show in this color scheme, right down here."))

    #  --[ Commit widgets ]--  #
    def compose(self):
        # Header (What to display at the Top-left corner)
        self.header_label = Label("", id="header_label")
        # Separator for header
        self.header_separator = Label("", id="header_separator")

        # Status bars
        self.primary_status = Label("", id="primary_status")
        self.secondary_status = Label("", id="secondary_status")
        
        # Main list in the middle
        self.main_list = MenuDisplay(
            title="MCONF PROJECT TITLE PLACEHOLDER",
            description=("Arrow keys navigate the menu.  <Enter> selects submenus ---> (or empty submenus ----)."
                    "  Highlighted letters are hotkeys.  Pressing <Y> includes, <N> excludes, <M> modularizes features."
                    "  Press <Esc><Esc> to exit, <?> for Help, </> for Search."
                    "  Legend: [*] built-in  [ ] excluded  <M> module  < > module capable"),
            items=["Hello", "If you", "see this,", "that means", "something has", "gone wrong..."]
        )
        
        # This wrapper owns the flexible height
        body = Vertical(
            Vertical(
                self.main_list,
                id="main_content",
            ),
            id="body_wrapper",
        )

        # Yield the layout
        yield Container(
            self.header_label,
            self.header_separator,
            body,
            self.primary_status,
            self.secondary_status,
        )

    #  --[ Key methods ]--  #
    def action_cursor_up(self):
        self._focus_mode = "list"
        self.main_list.list_view.focus()
        self.main_list.list_view.action_cursor_up()

    def action_cursor_down(self):
        self._focus_mode = "list"
        self.main_list.list_view.focus()
        self.main_list.list_view.action_cursor_down()

    def action_control_left(self):
        if self._focus_mode == "list":
            self._focus_mode = "controls"
            self._control_index = len(self.main_list.control_bar.children) - 1
            self._focus_control()
        else:
            self._control_index = (self._control_index - 1) % len(self.main_list.control_bar.children)
            self._focus_control()

    def action_control_right(self):
        if self._focus_mode == "list":
            self._focus_mode = "controls"
            self._control_index = 0
            self._focus_control()
        else:
            self._control_index = (self._control_index + 1) % len(self.main_list.control_bar.children)
            self._focus_control()

    def action_activate(self):
        if self._focus_mode == "list":
            index = self.main_list.list_view.index
            self.handle_menu_selection(index)
        elif self._focus_mode == "controls":
            self.main_list.control_bar.children[self._control_index].press()

    def action_space(self):
        if self._focus_mode == "list":
            index = self.main_list.list_view.index
            entry = self.current_entries[index]
            if isinstance(entry, KOption):
                if entry.opt_type == "bool":
                    entry.value = not entry.value
                    self.render_entries()
                    # Keep focus on current item
                    self.main_list.list_view.index = index

    def action_escape_key(self):
        if self._return_to_parent_menu():
            return

        # At root, show exit screen (show only if other windows aren't open)
        if not self.state.other_windows_are_open:
            if self._esc_timer is None:
                self.set_secondary_status("Press ESC again to exit")
                self._esc_timer = self.set_timer(1.0, self._reset_esc)
            else:
                self._esc_timer.stop()
                self._reset_esc()

                # Only show dialog if config changed
                if self.kconfig.has_changes(self.config.output_file):
                    self._show_exit_dialog()
                else:
                    self.exit()

    #  --[ Functions ]--  #
    def _get_status_path(self):
        if not self.menu_stack:
            return self.kconfig.mainmenu
        path = " > ".join([m.title for m in self.menu_stack])
        return f"> {path}"

    def _reset_esc(self):
        self._esc_timer = None
        self._show_primary_status()

    def _reset_other_windows_are_open(self):
        self.state.other_windows_are_open = False

    def _return_to_parent_menu(self) -> bool:
        # Returns True if went to parent menu, False if already at root
        if self.menu_stack:
            self.menu_stack.pop()
            self._focus_mode = "list"
            self._control_index = 0
            self.render_entries()
            self.set_status(self._get_status_path())
            return True
        return False

    def _focus_control(self):
        buttons = self.main_list.control_bar.children
        btn = buttons[self._control_index]
        btn.focus()

    def _show_exit_dialog(self):
        def callback(result):
            if result == "yes":
                self.kconfig.save_config(path=self.config.output_file,
                                        tool_name="Mesonconfig",
                                        tool_version=core.get_version())
                self.exit()
            elif result == "no":
                self.exit()
            elif result == "cancel":
                self.state.other_windows_are_open = True
                self.state.other_windows_are_open = self.set_timer(0.2, self._reset_other_windows_are_open)

        self.open_modal(ConfirmExitScreen(), callback)

    def get_current_entries(self):
        if not self.menu_stack:
            return self.kconfig.get_visible_entries()

        current_menu = self.menu_stack[-1]
        entries = self.kconfig.get_visible_entries(current_menu.entries)
        # fallback to parent if empty (prevents hang)
        if not entries and len(self.menu_stack) > 1:
            current_menu = self.menu_stack[-2]
            entries = self.kconfig.get_visible_entries(current_menu.entries)
        return entries

    def render_entries(self):
        self.current_entries = self.get_current_entries()
        display_items = []
        for e in self.current_entries:
            if isinstance(e, KMenu):
                display_items.append(f"{e.title}  --->")
            elif isinstance(e, KOption):
                if e.opt_type == "bool":
                    val = "[*]" if e.value else "[ ]"
                    display_items.append(f"{val} {e.prompt}")
                elif e.opt_type == "string":
                    display_items.append(f"({e.value or ''}) {e.prompt}")
                elif e.opt_type == "int":
                    display_items.append(f"({e.value or 0}) {e.prompt}")
            elif isinstance(e, KComment):
                display_items.append(f"# {e.text}")

        prev_index = getattr(self.main_list.list_view, "index", 0)
        self.main_list.update_items(display_items)
        if display_items:
            self.main_list.list_view.index = min(prev_index, len(display_items)-1)
            
        # Update title
        title = self.menu_stack[-1].title if self.menu_stack else self.kconfig.mainmenu
        self.main_list.border_title = f"[bold]{title}[/bold]"
        # Update status bar
        self.set_status(self._get_status_path())

    def handle_menu_selection(self, index: int):
        if not self.current_entries:
            return

        if index >= len(self.current_entries):
            return

        entry = self.current_entries[index]

        # Do not trigger selection on comments
        if isinstance(entry, KComment):
            return

        if not self.kconfig.is_visible(entry):
            return

        if isinstance(entry, KMenu):
            self.menu_stack.append(entry)
            self.render_entries()

        elif isinstance(entry, KOption):

            if entry.opt_type == "bool":
                entry.value = not bool(entry.value)
                self.render_entries()

            elif entry.opt_type in ("string", "int"):
                def callback(result):
                    if result is not None:
                        index = self.main_list.list_view.index  # preserve focus

                        if entry.opt_type == "int":
                            try:
                                entry.value = int(result)
                            except ValueError:
                                return  # or show error dialog
                        else:
                            entry.value = result

                        self.render_entries()
                        self.main_list.list_view.index = index

                if entry.opt_type == "int":
                    self.open_modal(IntegerEditScreen(entry), callback)
                else:
                    self.open_modal(StringEditScreen(entry), callback)
                
    def handle_help(self, index: int):
        if not self.current_entries:
            return

        entry = self.current_entries[index]

        if isinstance(entry, KOption):

            help_text = entry.help.strip() or "No help available."

            if entry.opt_type == "bool":
                symbol_val = "y" if entry.value else "n"
            elif entry.opt_type == "string":
                symbol_val = f'"{entry.value}"' if entry.value is not None else '""'
            elif entry.opt_type == "int":
                symbol_val = str(entry.value) if entry.value is not None else "0"
            else:
                symbol_val = str(entry.value)

            filename = getattr(entry, "filename", "unknown")
            lineno = getattr(entry, "lineno", "?")

            location = self.kconfig.get_option_location(entry.name)
            location_str = "\n".join(
                f"{' ' * (5 + i*2)}-> {p}" for i, p in enumerate(location)
            )

            content = f"""
{entry.name}:

{help_text}


 Symbol: {entry.name} [={symbol_val}]
 Type  : {entry.opt_type}
 Defined at {filename}:{lineno}
   Prompt: {entry.prompt}
   Location:
{location_str}
            """

            self.open_modal(
                HelpScreen(
                    title=entry.prompt,
                    content=content.strip(),
                    markdown=False
                )
            )

        elif isinstance(entry, KMenu):
            try:
                help_path = Path(__file__).parent / "README"
                content = help_path.read_text(encoding="utf-8")
            except FileNotFoundError:
                content = "README file not found."
            except Exception as e:
                content = f"Error loading README: {e}"

            self.open_modal(
                HelpScreen(
                    title="README",
                    content=content,
                    markdown=True
                )
            )
    
    def open_modal(self, screen, callback=None):
        self.main_list.display = False

        def wrapped_callback(result):
            self.state.other_windows_are_open = True
            self.main_list.display = True
            self.main_list.focus()

            if callback:
                callback(result)

        self.state.other_windows_are_open = True
        self.push_screen(screen, wrapped_callback)