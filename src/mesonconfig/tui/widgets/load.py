#
# Load alternate configuration dialog
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig.tui.widgets.help import HelpScreen
from textual.widgets import Label, Button, Input
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen


# ---[ LoadScreen ]--- #
class LoadScreen(ModalScreen):

    BINDINGS = [
        ("left", "focus_left", ""),
        ("right", "focus_right", ""),
    ]

    def __init__(self, default_value="local.conf"):
        super().__init__()
        self._buttons = []
        self._button_index = 0
        self._default_value = default_value

    def compose(self):
        ok_btn = Button("<  Ok  >", id="ok")
        cancel_btn = Button("< Cancel >", id="cancel")
        help_btn = Button("< Help >", id="help")

        self._buttons = [ok_btn, cancel_btn, help_btn]

        yield Container(
            Vertical(
                Label(
                    "  Enter the name of the configuration file you wish\n"
                    "  to load.  Accept the name shown to restore the\n"
                    "  configuration you last retrieved. Leave blank to\n"
                    "  abort."
                ),
                Container(
                    Input(
                        value=self._default_value,
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
            id="load_dialog",
            classes="dialog-window"
        )

    def on_mount(self):
        dialog = self.query_one("#load_dialog")
        dialog.border_title = "[bold]Load Alternate Configuration[/bold]"

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
            value = self.query_one("#value_input", Input).value.strip()
            self.dismiss(value if value else None)

        elif event.button.id == "cancel":
            # Same as empty input
            self.dismiss(None)

        elif event.button.id == "help":
            self._open_help()

    def key_escape(self):
        self.dismiss(None)

    # --- Help ---
    def _open_help(self):
        content = (
            "\n For various reasons, one may wish to keep several different\n"
            " configurations available on a single machine.\n\n"
            " If you have saved a previous configuration in a file other than the\n"
            " default one, entering its name here will allow you to modify that\n"
            " configuration.\n\n"
            " If you are uncertain, then you have probably never used alternate\n"
            " configuration files. You should therefore leave this blank to abort.\n"
        )

        self.app.push_screen(
            HelpScreen(
                title="Load Alternate Configuration",
                content=content,
                markdown=False,
            )
        )