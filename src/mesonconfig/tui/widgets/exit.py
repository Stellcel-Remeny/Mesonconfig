#
# Exit screen confirmation widget for Mesonconfig
# 2026, Remeny
#

from textual.screen import ModalScreen
from textual.widgets import Label, Button
from textual.containers import Container, Horizontal, Vertical


class ConfirmExitScreen(ModalScreen):

    def compose(self):
        yield Container(
            Vertical(
                Label("  Do you wish to save your new configuration?"),
                Label("  (Press <ESC><ESC> to continue project configuration.)"),
                Container(
                    Horizontal(
                        Button("< Yes >", id="yes"),
                        Button("<  No  >", id="no"),
                    ),
                    classes="dialog-buttons"
                ),
            ),
            id="exit_dialog",
            classes="dialog-window"
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss("yes")
        elif event.button.id == "no":
            self.dismiss("no")

    def key_escape(self):
        self.dismiss(None)