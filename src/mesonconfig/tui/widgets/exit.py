#
# Exit screen confirmation widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, Button
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen

# ---[ MenuDisplay ]--- #
class ConfirmExitScreen(ModalScreen):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def compose(self):
        yield Container(
            Vertical(
                Label(f"Would you like to save to {self.filename}?"),
                Horizontal(
                    Button("Yes", id="yes"),
                    Button("No", id="no"),
                    Button("Cancel", id="cancel"),
                ),
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss("yes")
        elif event.button.id == "no":
            self.dismiss("no")
        else:
            self.dismiss("cancel")
