#
# Help screen widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
# textual tui libs
from textual.widgets import Label, Button, Static
from textual.containers import Container, Vertical
from textual.screen import ModalScreen

# ---[ HelpScreen ]--- #
class HelpScreen(ModalScreen):
    """Popup help viewer."""

    def __init__(self, title: str, content: str):
        super().__init__()
        self.title = title
        self.content = content

    def compose(self):
        yield Container(
            Vertical(
                Label(f"[bold]{self.title}[/bold]"),
                Static(self.content),
                Button("Close", id="close"),
            ),
            id="help_window",
        )

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()
