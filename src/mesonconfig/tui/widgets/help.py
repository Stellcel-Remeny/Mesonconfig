#
# Help screen widget for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown
from textual.containers import Container, Vertical, Horizontal, VerticalScroll

# ---[ HelpScreen ]--- #
class HelpScreen(ModalScreen):

    BINDINGS = [
        ("left", "focus_left", ""),
        ("right", "focus_right", ""),
        ("up", "scroll_up", ""),
        ("down", "scroll_down", ""),
    ]

    def __init__(self, title: str, content: str):
        super().__init__()
        self.title = title
        self.content = content
        self._buttons = []
        self._button_index = 0

    def compose(self):
        exit_btn = Button("< Exit >", id="exit")
        self._buttons = [exit_btn]

        yield Container(
            Vertical(
                VerticalScroll(
                    Markdown(self.content, id="help_content"),
                    id="help_scroll",
                    can_focus=True,
                ),
                Horizontal(
                    exit_btn,
                    classes="dialog-buttons"
                ),
            ),
            id="help_dialog",
            classes="dialog-window"
        )

    def on_mount(self):
        dialog = self.query_one("#help_dialog")
        dialog.border_title = f"[bold]{self.title}[/bold]"
        dialog.border_title_align = "center"

        scroll = self.query_one("#help_scroll")
        scroll.focus()

    # --- Arrow navigation ---
    def action_focus_left(self):
        if not self._buttons:
            return
        self._button_index = (self._button_index - 1) % len(self._buttons)
        self._focus_button()

    def action_focus_right(self):
        if not self._buttons:
            return
        self._button_index = (self._button_index + 1) % len(self._buttons)
        self._focus_button()

    def action_scroll_up(self):
        self.query_one("#help_scroll").scroll_up()

    def action_scroll_down(self):
        self.query_one("#help_scroll").scroll_down()

    def _focus_button(self):
        self._buttons[self._button_index].focus()

    # --- Button press ---
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "exit":
            self.dismiss()

    def key_escape(self):
        self.dismiss()