#
# Textual-based TUI interface for Mesonconfig
# 2026, Remeny
#

# TODO: Make MenuDisplay and other windows 3D (fake borders, shadow)

# ---[ Libraries ]--- #
from . import core
# textual tui libs
from textual.app import App
from textual.events import Key
from textual.widgets import Label, ListView, ListItem, Static
from textual.containers import Container, Vertical, VerticalScroll

# ---[ Windows ]--- #
class MenuDisplay(Static):
    """Displays a scrollable Menu interface."""
    
    def __init__(self, title: str, description: str, items: list[str]):
        super().__init__()
        self.title = title
        self.description = description
        self.items = items

    def compose(self):
        yield Static(self.description, classes="menu-description")
        yield ListView(
            *[ListItem(Label(item), id=item) for item in self.items],
            classes="menu-list",
        )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.app.dbg(f"Selected: {event.item.id}")

    def on_mount(self):
        self.border_title = f"[bold]{self.title}[/bold]"

# ---[ Main TUI Interface ]--- #
class MCfgApp(App):
    #  --[ On class create ]--  #
    def __init__(self, background: str = "blue", verbose: bool = False,
                 window_color: str = "black",
                 window_background: str = "lightgrey",
                 **kwargs):
        super().__init__(**kwargs)
        self._background: str = background
        self._content_hidden: bool = False
        self._last_status_text: str = ""
        self._secondary_visible: bool = False
        self._verbose: bool = verbose
        self._window_color: str = window_color
        self._window_background: str = window_background
    
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
            MenuDisplay(
                title="MCONF PROJECT TITLE PLACEHOLDER",
                description=("Arrow keys navigate the menu.  <Enter> selects submenus ---> (or empty submenus ----)."
                        "  Highlighted letters are hotkeys.  Pressing <Y> includes, <N> excludes, <M> modularizes features."
                        "  Press <Esc><Esc> to exit, <?> for Help, </> for Search."
                        "  Legend: [*] built-in  [ ] excluded  <M> module  < > module capable"),
                items=["tempo", "cheetah", "ah"]
            ),
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
    @property
    def CSS(self) -> str:
        return f"""    
        Screen {{
            background: {self._background};
            color: cyan;
        }}

        #header_label {{
            content-align: left middle;
            height: 1;
            padding-left: 1;
        }}

        #header_separator {{
            color: cyan;
            height: 1;
            padding-left: 1;
        }}

        #primary_status,
        #secondary_status {{
            height: 1;
            width: 100%;
            padding-left: 1;
        }}

        #primary_status {{
            background: lightgray;
            color: black;
        }}

        #secondary_status {{
            background: black;
            color: lightgreen;
        }}

        .hidden {{
            display: none;
        }}
        
        #main_content {{
            height: 1fr;
        }}

        MenuDisplay {{
            height: 1fr;
            width: 100%;
            background: {self._window_background};
            color: {self._window_color};
            border: solid {self._window_color};
            border-title-align: center;
            padding-top: 0;
            padding-left: 2;
            padding-right: 1;
            margin: 0 3 1 2;
        }}
        
        ListView .list-item--highlighted {{
            background: white;
            color: black;
        }}
        
        ListView .list-item--highlighted Label {{
            color: black;
        }}
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
