#
# Layout for Mesonconfig
# 2026, Remeny
#

from textual.widgets import Label
from textual.containers import Container, Vertical
from mesonconfig.tui.widgets.menu import MenuDisplay

def build_main_layout(app):    
    # Header (What to display at the Top-left corner)
    app.header_label = Label("", id="header_label")
    # Separator for header
    app.header_separator = Label("", id="header_separator")

    # Status bars
    app.primary_status = Label("", id="primary_status")
    app.secondary_status = Label("", id="secondary_status")
    
    # Main stuff - windows...
    app.main_content = Vertical(
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
    return Container(
        Vertical(
            app.header_label,
            app.header_separator,
            app.main_content,
        ),
        app.primary_status,
        app.secondary_status,
    )
