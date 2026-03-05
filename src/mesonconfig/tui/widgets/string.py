#
# String editing widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig.tui.widgets.help import HelpScreen
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
        help_btn = Button("< Help >", id="help")

        self._buttons = [ok_btn, cancel_btn, help_btn]

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
                        help_btn,
                    ),
                    classes="dialog-buttons"
                ),
            ),
            id="string_dialog",
            classes="dialog-window"
        )

    def on_mount(self):
        title = (
            getattr(self.option, "prompt", None)
            or getattr(self.option, "name", None)
            or "Edit Value"
        )

        dialog = self.query_one("#string_dialog")
        dialog.border_title = f"[bold]{title}[/bold]"

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

        elif event.button.id == "help":
            self._open_help()

    def key_escape(self):
        self.dismiss(None)

    # --- Functions --- #
    def _open_help(self):
        help_text = getattr(self.option, "help", "").strip() or "No help available."

        symbol_val = self.option.value
        if self.option.opt_type == "bool":
            symbol_val = "y" if self.option.value else "n"

        filename = getattr(self.option, "filename", "unknown")
        lineno = getattr(self.option, "lineno", "?")

        content = (
            f"{self.option.name}:\n\n"
            f"{help_text}\n\n"
            f" Symbol: {self.option.name} [={symbol_val}]\n"
            f" Type  : {self.option.opt_type}\n"
            f" Defined at {filename}:{lineno}\n"
            f"   Prompt: {self.option.prompt}"
        )

        self.app.push_screen(
            HelpScreen(
                title=self.option.prompt or self.option.name,
                content=content,
                markdown=False,
            )
        )