#
# Help screen widget for Mesonconfig
# 2026, Remeny
#

from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Container, Vertical, Horizontal


class HelpScreen(ModalScreen):

    def __init__(self, title: str, content: str):
        super().__init__()
        self.title = title
        self.content = content

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

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "exit":
            self.dismiss()

    def key_escape(self):
        self.dismiss()