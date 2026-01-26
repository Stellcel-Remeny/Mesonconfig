#
# Textual-based TUI interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from . import core
# textual tui libs
from textual.app import App
from textual.events import Key
from textual.widgets import Label
from textual.containers import Container, Vertical

# ---[ Main TUI Interface ]--- #
class MCfgApp(App):
    #  --[ On class create ]--  #
    def __init__(self, verbose: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.verbose: bool = verbose
        self._secondary_visible: bool = False
        self._content_hidden: bool = False
        self._last_status_text: str = ""
    
    #  --[ Widgets ]--  #
    def compose(self):
        # Header (What to display at the Top-left corner)
        self.header_label = Label("", id="header_label")
        # Separator for header
        self.header_separator = Label("", id="header_separator")
    
        # Status bars
        self.primary_status = Label("", id="primary_status")
        self.secondary_status = Label("", id="secondary_status")
        
        # Main stuff - windows...
        self.main_content = Vertical(
            Label("Hide me.."),
            id="main_content",
        )
        
        # Commit widgets
        yield Container(
            Vertical(
                self.header_label,
                self.header_separator,
                self.main_content,
            ),
            self.primary_status,
            self.secondary_status,
        )
    
    #  --[ Style ]--  #
    CSS = """    
    Screen {
        background: blue;
        color: cyan;
    }

    #header_label {
        height: 1;
        padding-left: 1;
        content-align: left middle;
    }

    #header_separator {
        height: 1;
        color: cyan;
        padding-left: 1;
    }

    #primary_status,
    #secondary_status {
        height: 1;
        width: 100%;
        padding-left: 1;
    }

    #primary_status {
        background: lightgray;
        color: black;
    }

    #secondary_status {
        background: black;
        color: lightgreen;
    }

    .hidden {
        display: none;
    }
    
    #main_content.hidden {
        display: none;
    }
    """

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
            self.header_separator.update("─" * (width - 2))
    
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
        
    def status(self, text: str) -> None:
        # Updates the primary status bar
        self._last_status_text = text
        self._show_primary_status()
        self.primary_status.update(text)
        
    def sstatus(self, text: str) -> None:
        # Updates the secondary status bar
        self._show_secondary_status()
        self.secondary_status.update(text)
    
    def dbg(self, text: str) -> None:
        # Only shows if verbose is enabled
        if self.verbose:
            self.sstatus(text)

    #  --[ Program Logic ]--  #
    # Stuff to happen on program resize
    def on_resize(self):
        self.update_header_separator()
        if not self.check_size():
            self.hide_main_content()
            self.sstatus(f"Window too small, resize it: Minimum {core.min_cols}x{core.min_rows}")
            return
        elif self._content_hidden:
            # If the content was previously hidden and only now the user has resized it properly, show all stuff and get old status text
            self.show_main_content()
            if self._secondary_visible:
                self.status(self._last_status_text)
    
    # Stuff to happen on user Key press
    def on_key(self, event: Key) -> None:
        if event.key.upper() == "Q":
            self.exit()  # Quit the app
    
    # Stuff to happen on program commence
    def on_mount(self):
        # Program logic here...
        self.header(f"Mesonconfig {core.get_version()}")
        self.status("Initializing...")
        self.dbg("DEBUFF")