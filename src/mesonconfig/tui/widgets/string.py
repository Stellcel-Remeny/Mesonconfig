#
# String editing widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, Button, Input
from textual.containers import Container, Horizontal, Vertical

# ---[ StringEditScreen ]--- #
class StringEditScreen(Container):
    """Popup screen to edit string/int options."""

    def __init__(self, option):
        super().__init__()
        self.option = option
        self.on_close = None

    def compose(self):
        yield Container(
            Vertical(
                Label("  Please enter a string value. Use the <TAB> key to move."),
                Container(
                    Input(value=str(self.option.value or ""), id="value_input"),
                    id="input_wrapper",
                ),
                Container(
                    Horizontal(
                        Button("<  Ok  >", id="ok"),
                        Button("< Help >", id="help"),
                    ),
                    classes="dialog-buttons"
                ),
            ),
            id="string_dialog",
            classes="dialog-window"
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok":
            value = self.query_one("#value_input", Input).value
            if self.on_close:
                self.on_close(value)

        elif event.button.id == "help":
            if self.on_close:
                self.on_close(None)
