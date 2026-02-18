#
# String editing widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, Button
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input

# ---[ StringEditScreen ]--- #
class StringEditScreen(ModalScreen):
    """Popup screen to edit string/int options."""

    def __init__(self, option):
        super().__init__()
        self.option = option

    def compose(self):
        yield Container(
            Vertical(
                Label(f"Edit value for: {self.option.prompt}"),
                Input(value=str(self.option.value or ""), id="value_input"),
                Horizontal(
                    Button("OK", id="ok"),
                    Button("Cancel", id="cancel"),
                ),
            ),
            id="string_edit_window",
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok":
            value = self.query_one("#value_input", Input).value
            self.dismiss(value)
        else:
            self.dismiss(None)
