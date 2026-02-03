#
# Textual widgets for Mesonconfig
# 2026, Remeny
#

# TODO: Make MenuDisplay and other windows 3D (fake borders, shadow)

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, ListView, ListItem, Static

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
