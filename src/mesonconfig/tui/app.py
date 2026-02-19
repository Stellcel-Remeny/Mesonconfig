#
# Textual-based TUI interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig.tui.css import app_css
from mesonconfig.tui.status.status_mixin import StatusMixin
from mesonconfig.tui.chrome.window_mixin import WindowChromeMixin
from mesonconfig.tui.lifecycle.handlers import LifecycleHandlers
from mesonconfig.tui.config import AppConfig, UIState
from mesonconfig.tui.widgets.menu import MenuDisplay
from mesonconfig.tui.widgets.string import StringEditScreen
from mesonconfig.tui.widgets.help import HelpScreen
from mesonconfig.tui.widgets.exit import ConfirmExitScreen
from mesonconfig.kconfig import KConfig, KMenu, KOption, KComment
# textual tui libs
from textual.app import App
from textual.widgets import Label
from textual.containers import Container, Vertical

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
        self.render_entries()

    #  --[ On class resume ]--  #
    def on_screen_resume(self) -> None:
        # Called when modal closes
        self.main_list.display = True
        self.main_list.focus()

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

        self.main_content = Vertical(
            self.main_list,
            id="main_content",
        )

        self.overlay_layer = Container(
            id="overlay_layer",
            classes="hidden",
        )
        
        self.windows = Vertical(
            self.main_content,
            self.overlay_layer,
            id="windows",
        )
        
        # Yield the layout
        yield Container(
            self.header_label,
            self.header_separator,
            Vertical(
                self.windows,
            ),
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
        if not self.overlay_layer.has_class("hidden"):
            self.close_dialog()
            return
        
        if self.menu_stack:
            self.menu_stack.pop()
            self._focus_mode = "list"
            self._control_index = 0
            self.render_entries()
            self.set_status(self._get_status_path())
            if self._esc_timer:
                self._esc_timer.stop()
                self._esc_timer = None
            return

        # At root
        if self._esc_timer is None:
            self.set_secondary_status("Press ESC / < Exit > again to exit")
            self._esc_timer = self.set_timer(1.0, self._reset_esc)
        else:
            def callback(result):
                if result == "yes":
                    self.kconfig.save_config(self.config.output_file)
                    self.exit()
                elif result == "no":
                    self.exit()
                # cancel → do nothing

            self.main_list.display = False
            self.show_dialog(
                ConfirmExitScreen(),
                callback
            )

    #  --[ Functions ]--  #
    def _get_status_path(self):
        if not self.menu_stack:
            return self.kconfig.mainmenu
        path = " > ".join([m.title for m in self.menu_stack])
        return f"> {path}"

    def _reset_esc(self):
        self._esc_timer = None
        self._show_primary_status()

    def _focus_control(self):
        buttons = self.main_list.control_bar.children
        btn = buttons[self._control_index]
        btn.focus()

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
                        if entry.opt_type == "int":
                            entry.value = int(result)
                        else:
                            entry.value = result
                        self.render_entries()

                self.main_list.display = False
                self.show_dialog(StringEditScreen(entry), callback)
                
    def handle_help(self, index: int):
        if not self.current_entries:
            return

        entry = self.current_entries[index]

        if isinstance(entry, KOption):
            content = f"Type: {entry.opt_type}\n\n{entry.help or 'No help available.'}"
            self.main_list.display = False
            self.show_dialog(HelpScreen(entry.prompt, content))

        elif isinstance(entry, KMenu):
            self.main_list.display = False
            self.show_dialog(
                HelpScreen(
                    entry.title,
                    "General submenu help placeholder."
                )
            )
        
    def show_dialog(self, widget, callback=None):
        self.overlay_layer.remove_class("hidden")
        self.overlay_layer.mount(widget)

        if callback:
            widget.on_close = lambda result=None: (
                callback(result),
                self.close_dialog()
            )
        else:
            widget.on_close = lambda result=None: self.close_dialog()

        widget.focus()

    def close_dialog(self):
        # Remove all dialog widgets completely
        for child in list(self.overlay_layer.children):
            child.remove()

        self.overlay_layer.add_class("hidden")

        self.main_list.display = True
        self.main_list.list_view.focus()
