#
# Textual-based TUI interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig import core
from mesonconfig.tui.css import app_css
from mesonconfig.tui.layout.main_layout import build_main_layout
from mesonconfig.tui.status.status_mixin import StatusMixin
from mesonconfig.tui.chrome.window_mixin import WindowChromeMixin
from mesonconfig.tui.lifecycle.handlers import LifecycleHandlers
# textual tui libs
from textual.app import App
from textual.events import Key

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
        background: str = "blue",
        verbose: bool = False,
        window_color: str = "black",
        window_background: str = "lightgrey",
        **kwargs
    ):
        super().__init__(**kwargs)
        self._background: str = background
        self._verbose: bool = verbose
        self._window_color: str = window_color
        self._window_background: str = window_background
        
        self._content_hidden: bool = False
        self._secondary_visible: bool = False
        self._last_status_text: str = ""
    
    #  --[ Style ]--  #
    @property
    def CSS(self) -> str:
        return app_css(
            background=self._background,
            window_bg=self._window_background,
            window_fg=self._window_color
        )

    #  --[ Commit widgets ]--  #
    def compose(self):
        yield build_main_layout(self)
