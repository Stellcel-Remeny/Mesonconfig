#
# Help screen widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, Button, Static
from textual.containers import Container, Vertical, Horizontal

# ---[ HelpScreen ]--- #
class HelpScreen(Container):
    """Popup help viewer."""

    def __init__(self, title, content):
        super().__init__()
        self.title = title
        self.content = content
        self.on_close = None

    def compose(self):
        yield Container(
            Vertical(
                Static(self.content, expand=True),
                Horizontal(
                    Button("< Exit >", id="exit"),
                    classes="dialog-buttons"
                ),
            ),
            id="help_dialog",
            classes="dialog-window"
        )

    def on_button_pressed(self, event):
        if self.on_close:
            self.on_close()