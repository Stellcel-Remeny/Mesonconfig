#
# Textual widgets for Mesonconfig
# 2026, Remeny
#

# TODO: Make MenuDisplay and other windows 3D (shadow)

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, ListView, ListItem, Static, Button
from textual.containers import Container, Horizontal, Vertical

# ---[ Widgets ]--- #
class MenuDisplay(Static):
    """Displays a scrollable Menu interface."""
    
    def __init__(
        self,
        title: str,
        description: str,
        items: list[str],
        show_controls: bool = True
    ):
        super().__init__()
        self.title: str = title
        self.description: str = description
        self.items: list[str] = items
        self.show_controls: bool = show_controls

    def compose(self):
        yield Static(self.description, classes="menu-description")
        
        self.list_view = ListView(
            *[ListItem(Label(item), id=item) for item in self.items],
            id="menu_list",
            classes="menu-list",
        )
        
        yield Container(
            Horizontal(
                self.list_view,
                classes="menu-list-wrapper",
            ),
            classes="menu-frame",
        )

        self.control_bar = Horizontal(
            Button("<Select>", id="btn_select"),
            Button("< Exit >", id="btn_exit"),
            Button("< Help >", id="btn_help"),
            Button("< Save >", id="btn_save"),
            Button("< Load >", id="btn_load"),
            id="control_bar",
        )
        
        # Yield control_bar conditionally
        if self.show_controls:
            yield self.control_bar

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.app.dbg(f"Selected: {event.item.id}")

    def on_mount(self):
        self.border_title = f"[bold]{self.title}[/bold]"
        self.update_items(self.items)

    def update_items(self, items: list[str]) -> None:
        """Replace the items in the ListView."""
        self.items = items
        
        if not self.is_mounted:
            return  # wait until mounted

        self.list_view.clear()
        self.list_view.extend(
            ListItem(Label(item), id=item)
            for item in items
        )
        
    def set_controls_visible(self, visible: bool) -> None:
        self.show_controls = visible
        self.control_bar.display = visible