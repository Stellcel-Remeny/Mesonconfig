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

    #  --[ Widgets ]--  #
    def compose(self):
        yield build_main_layout(self)

    #  --[ Functions / Helpers ]--  #
    def check_size(self) -> bool:
        # Checks if current terminal size is minimum or greater
        # Returns:
        #   True = Equal to or more than minimum size
        #   False = Less than minimum size
        width, height = self.size
        return width >= core.min_cols and height >= core.min_rows
    
    def header(self, text: str) -> None:
        # Updates the header label
        self.header_label.update(text)
    
    def update_header_separator(self) -> None:
        # Redraws header separator
        width = self.size.width
        if width > 1:
            self.header_separator.update("─" * (width - 1))
    
    def hide_main_content(self) -> None:
        self.main_content.add_class("hidden")
        self._content_hidden = True
        
    def show_main_content(self) -> None:
        self.main_content.remove_class("hidden")
        self._content_hidden = False
    
    #   -[ Status bar functions ]-   #
    def _show_primary_status(self) -> None:
        # Show primary, hide secondary
        self.secondary_status.add_class("hidden")
        self.primary_status.remove_class("hidden")
        self._secondary_visible = False
        
    def _show_secondary_status(self) -> None:
        # Show secondary, hide primary
        self.primary_status.add_class("hidden")
        self.secondary_status.remove_class("hidden")
        self._secondary_visible = True
        
    def set_status(self, text: str) -> None:
        # Updates the primary status bar
        self._last_status_text = text
        self._show_primary_status()
        self.primary_status.update(text)
        
    def set_secondary_status(self, text: str) -> None:
        # Updates the secondary status bar
        self._show_secondary_status()
        self.secondary_status.update(text)
    
    def dbg(self, text: str) -> None:
        # Only shows if verbose is enabled
        if self._verbose:
            self.set_secondary_status(text)

    #  --[ Program Logic ]--  #
    # Stuff to happen on program resize
    def on_resize(self):
        self.update_header_separator()
        if not self.check_size():
            self.hide_main_content()
            self.set_secondary_status(f"Window too small, resize it: Minimum {core.min_cols}x{core.min_rows}")
            return
        elif self._content_hidden:
            # If the content was previously hidden and only now the user has resized it properly, show all stuff and get old status text
            self.show_main_content()
            if self._secondary_visible:
                self.set_status(self._last_status_text)
    
    # Stuff to happen on user Key press
    def on_key(self, event: Key) -> None:
        if event.key.upper() == "Q":
            self.exit()  # Quit the app
    
    # Stuff to happen on program commence
    def on_mount(self):
        # Program logic here...
        self.header(f"Mesonconfig {core.get_version()}")
        self.set_status("Initializing...")
        self.dbg("Debug text will show in this color scheme, right down here.")
