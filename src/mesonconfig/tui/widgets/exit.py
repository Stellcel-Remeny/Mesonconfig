#
# Exit screen confirmation widget for Mesonconfig
# 2026, Remeny
#

from textual.screen import ModalScreen
from textual.widgets import Label, Button
from textual.containers import Container, Horizontal, Vertical

class ConfirmExitScreen(ModalScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._esc_timer = None

    def compose(self):
        yield Container(
            Vertical(
                Label("  Do you wish to save your new configuration?"),
                Label("  (Press <ESC><ESC> to continue project configuration.)"),
                Container(
                    Horizontal(
                        Button("< Yes >", id="yes"),
                        Button("<  No  >", id="no"),
                        Button("<Cancel>", id="cancel"),
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
        elif event.button.id == "cancel":
            self.dismiss("cancel")

    def key_escape(self):
        if self._esc_timer is None:
            self.app.set_secondary_status("Press ESC again to continue project configuration.")
            self._esc_timer = self.set_timer(1.0, self._reset_esc)
        else:
            self._esc_timer.stop()
            self._reset_esc()
            self.dismiss("cancel")

    def _reset_esc(self):
        self._esc_timer = None
        self.app._show_primary_status()