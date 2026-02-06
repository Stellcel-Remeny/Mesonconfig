#
# Textual-based TUI interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig.tui.css import app_css
from mesonconfig.tui.layout.main_layout import build_main_layout
from mesonconfig.tui.status.status_mixin import StatusMixin
from mesonconfig.tui.chrome.window_mixin import WindowChromeMixin
from mesonconfig.tui.lifecycle.handlers import LifecycleHandlers
from mesonconfig.tui.state import UIState
from mesonconfig.tui.config import AppConfig
# textual tui libs
from textual.app import App

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
    ):
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

    #  --[ Commit widgets ]--  #
    def compose(self):
        yield build_main_layout(self)
