#
# Scrollable menu widget for Mesonconfig
# 2026, Remeny
#

# TODO: Make MenuDisplay and other windows 3D (shadow)
# TODO: Add a quit screen on Exit selected
# TODO: Add real functionality on button pressed

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, ListView, ListItem, Static, Button
from textual.containers import Container, Horizontal

# ---[ MenuDisplay ]--- #
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
            *[
                ListItem(Label(item), id=f"item_{i}")
                for i, item in enumerate(self.items)
            ],
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

        #  --[ Control bar ]--  #
        btn_select = Button("<Select>", id="btn_select")
        btn_exit = Button("< Exit >", id="btn_exit")
        btn_help = Button("< Help >", id="btn_help")
        btn_save = Button("< Save >", id="btn_save")
        btn_load = Button("< Load >", id="btn_load")

        self.control_bar = Horizontal(
            btn_select,
            btn_exit,
            btn_help,
            btn_save,
            btn_load,
            id="control_bar",
        )
        
        # Yield control_bar conditionally
        if self.show_controls:
            yield self.control_bar

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = self.list_view.index
        value = self.items[index]
        self.app.dbg(f"Selected: {value} Index: {index}")
        self.app.handle_menu_selection(index)

    def on_mount(self):
        self.border_title = f"[bold]{self.title}[/bold]"
        self.update_items(self.items)
        self.list_view.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "btn_exit":
            self.app.action_escape_key()

        elif button_id == "btn_select":
            self.handle_select()

        elif button_id == "btn_help":
            self.handle_help()

        elif button_id == "btn_save":
            self.handle_save()

        elif button_id == "btn_load":
            self.handle_load()

    def handle_select(self):
        if not self.list_view.children:
            return

        index = self.list_view.index
        self.app.handle_menu_selection(index)

    def handle_help(self):
        if not self.list_view.children:
            return

        index = self.list_view.index
        self.app.handle_help(index)

    def handle_save(self):
        self.app.dbg("Save pressed")

    def handle_load(self):
        self.app.dbg("Load pressed")

    def update_items(self, items: list[str]) -> None:
        self.items = items

        if not self.is_mounted:
            return

        # Clear everything first
        self.list_view.clear()

        # Now rebuild safely
        for i, item in enumerate(items):
            self.list_view.append(
                ListItem(Label(item))
            )
        
    def set_controls_visible(self, visible: bool) -> None:
        self.show_controls = visible
        self.control_bar.display = visible