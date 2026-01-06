#
# Command-line TUI interface for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from .core import *

from textual.app import App
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Vertical, Center

class OkDialog(ModalScreen):

    CSS = """
    #box {
        width: 40;
        height: 7;
        padding: 1;
        border: round white;
        background: $surface;
    }

    Label {
        content-align: center middle;
        height: 3;
    }

    Button {
        width: 10;
        align-horizontal: center;
    }
    """

    def compose(self):
        yield Center(
            Vertical(
                Label("no this doesnt look like a dialog."),
                Button("OK", id="ok"),
                id="box"
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss()


class DialogApp(App):
    def on_mount(self):
        self.push_screen(OkDialog())

# ---[ Entry point ]--- #
def main():
    DialogApp().run()
