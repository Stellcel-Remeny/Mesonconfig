#
# Textual-based TUI interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig.tui.css import app_css
from mesonconfig.tui.status.status_mixin import StatusMixin
from mesonconfig.tui.chrome.window_mixin import WindowChromeMixin
from mesonconfig.tui.lifecycle.handlers import LifecycleHandlers
from mesonconfig.tui.state import UIState
from mesonconfig.tui.config import AppConfig
from mesonconfig.tui.widgets.menu import MenuDisplay
# textual tui libs
from textual.app import App
from textual.widgets import Label, Button
from textual.containers import Container, Vertical, Horizontal

# ---[ Main TUI Interface ]--- #
class MCfgApp(
    App,
    StatusMixin,
    WindowChromeMixin,
    LifecycleHandlers
):
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
        self.state = UIState()
    
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
        self.main_list.update_items(['Hi', 'John', 'Appleseed', 'Bananaseed'])

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
            items=["tempo", "cheetah", "ah", "yolo", "yt"]
        )

        self.main_content = Vertical(
            self.main_list,
            id="main_content",
        )

        # Yield the layout
        yield Container(
            Vertical(
                self.header_label,
                self.header_separator,
                self.main_content,
            ),
            self.primary_status,
            self.secondary_status,
        )
