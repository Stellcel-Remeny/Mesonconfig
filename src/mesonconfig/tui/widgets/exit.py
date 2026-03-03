#
# Exit screen confirmation widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from textual.screen import ModalScreen
from textual.widgets import Label, Button
from textual.containers import Container, Horizontal, Vertical

# ---[ ConfirmExitScreen ]--- #
class ConfirmExitScreen(ModalScreen):

    BINDINGS = [
        ("left", "focus_left", ""),
        ("right", "focus_right", ""),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._esc_timer = None
        self._button_index = 0
        self._buttons = []

    def compose(self):
        yes = Button("< Yes >", id="yes")
        no = Button("<  No  >", id="no")
        cancel = Button("<Cancel>", id="cancel")

        self._buttons = [yes, no, cancel]

        yield Container(
            Vertical(
                Label("  Do you wish to save your new configuration?"),
                Label("  (Press <ESC><ESC> to continue project configuration.)"),
                Container(
                    Horizontal(
                        yes,
                        no,
                        cancel,
                    ),
                    classes="dialog-buttons"
                ),
            ),
            id="exit_dialog",
            classes="dialog-window"
        )

    def on_mount(self):
        # Focus first button when dialog opens
        self._focus_button()

    # --- Arrow key actions ---
    def action_focus_left(self):
        self._button_index = (self._button_index - 1) % len(self._buttons)
        self._focus_button()

    def action_focus_right(self):
        self._button_index = (self._button_index + 1) % len(self._buttons)
        self._focus_button()

    def _focus_button(self):
        self._buttons[self._button_index].focus()

    # --- Button press handler ---
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss("yes")
        elif event.button.id == "no":
            self.dismiss("no")
        elif event.button.id == "cancel":
            self.dismiss("cancel")

    # --- ESC double press logic ---
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