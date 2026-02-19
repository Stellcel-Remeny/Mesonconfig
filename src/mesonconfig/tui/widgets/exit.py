#
# Exit screen confirmation widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, Button
from textual.containers import Container, Horizontal, Vertical

# ---[ MenuDisplay ]--- #
class ConfirmExitScreen(Container):

    def __init__(self):
        super().__init__()
        self.on_close = None

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
        
    def on_button_pressed(self, event):
        if self.on_close:
            self.on_close(event.button.id)
