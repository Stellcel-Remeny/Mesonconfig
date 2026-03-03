#
# String editing widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from textual.widgets import Label, Button, Input
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen

# ---[ StringEditScreen ]--- #
class StringEditScreen(ModalScreen):

    BINDINGS = [
        ("left", "focus_left", ""),
        ("right", "focus_right", ""),
    ]

    def __init__(self, option):
        super().__init__()
        self.option = option
        self._buttons = []
        self._button_index = 0

    def compose(self):
        ok_btn = Button("<  Ok  >", id="ok")
        cancel_btn = Button("< Cancel >", id="cancel")

        self._buttons = [ok_btn, cancel_btn]

        yield Container(
            Vertical(
                Label(
                    "  Please enter a string value. Use the <TAB> key to move from the input\n"
                    "  field to the buttons below it."
                ),
                Container(
                    Input(
                        value=str(self.option.value or ""),
                        id="value_input"
                    ),
                    id="input_wrapper",
                ),
                Container(
                    Horizontal(
                        ok_btn,
                        cancel_btn,
                    ),
                    classes="dialog-buttons"
                ),
            ),
            id="string_dialog",
            classes="dialog-window"
        )

    def on_mount(self):
        self.query_one("#value_input", Input).focus()

    # --- Arrow navigation (only when buttons focused) ---
    def action_focus_left(self):
        if not self._buttons:
            return

        if isinstance(self.focused, Button):
            self._button_index = (self._button_index - 1) % len(self._buttons)
            self._focus_button()

    def action_focus_right(self):
        if not self._buttons:
            return

        if isinstance(self.focused, Button):
            self._button_index = (self._button_index + 1) % len(self._buttons)
            self._focus_button()

    def _focus_button(self):
        self._buttons[self._button_index].focus()

    # --- Button press ---
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok":
            value = self.query_one("#value_input", Input).value
            self.dismiss(value)
        elif event.button.id == "cancel":
            self.dismiss(None)

    def key_escape(self):
        self.dismiss(None)