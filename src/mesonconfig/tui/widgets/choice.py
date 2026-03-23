#
# Choice selection widget for Mesonconfig
# 2026, Remeny
#

from textual.widgets import Label, Button, ListView, ListItem
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen


class ChoiceScreen(ModalScreen):

    BINDINGS = [
        ("up", "cursor_up", ""),
        ("down", "cursor_down", ""),
        ("space", "toggle", ""),
        ("enter", "select", ""),
    ]

    def __init__(self, choice):
        super().__init__()
        self.choice = choice
        self.options = choice.entries

        # determine default selected index
        self._selected_index = self._get_initial_index()

    # --- UI --- #
    def compose(self):
        self.list_view = ListView(
            *[self._make_item(i) for i in range(len(self.options))],
            id="choice_list"
        )

        select_btn = Button("<Select>", id="select")
        help_btn = Button("< Help >", id="help")
        cancel_btn = Button("< Cancel >", id="cancel")

        yield Container(
            Vertical(
                Label(
                    "  Use arrow keys to navigate. Press <SPACE> to select.\n"
                    "  Press <?> for help."
                ),
                Container(
                    self.list_view,
                    id="choice_list_wrapper"
                ),
                Container(
                    Horizontal(select_btn, help_btn, cancel_btn),
                    classes="dialog-buttons"
                ),
            ),
            id="choice_dialog",
            classes="dialog-window"
        )

    def on_mount(self):
        title = self.choice.prompt or "Select Option"
        dialog = self.query_one("#choice_dialog")
        dialog.border_title = f"[bold]{title}[/bold]"

        self.list_view.focus()
        self.list_view.index = self._selected_index

    # --- Helpers --- #
    def _get_initial_index(self) -> int:
        for i, opt in enumerate(self.options):
            if opt.value:
                return i

        # fallback to default
        for i, opt in enumerate(self.options):
            if opt.default:
                return i

        return 0

    def _make_item(self, index: int) -> ListItem:
        opt = self.options[index]
        selected = (index == self._selected_index)

        marker = "(X)" if selected else "( )"
        text = f"{marker} {opt.prompt}"

        return ListItem(Label(text))

    # --- Actions --- #
    def action_cursor_up(self):
        self.list_view.action_cursor_up()

    def action_cursor_down(self):
        self.list_view.action_cursor_down()

    def action_toggle(self):
        self._selected_index = self.list_view.index
        self._commit_and_close()

    def action_select(self):
        self._commit_and_close()

    # --- Events --- #
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "select":
            self._commit_and_close()

        elif event.button.id == "cancel":
            self.dismiss(None)

        elif event.button.id == "help":
            self._open_help()

    def on_list_view_selected(self, event: ListView.Selected):
        # ENTER or mouse double-click
        self._selected_index = event.list_view.index
        self._commit_and_close()

    # --- Logic --- #
    def _commit_and_close(self):
        # apply selection
        for i, opt in enumerate(self.options):
            opt.value = (i == self._selected_index)

        self.dismiss(self._selected_index)

    def _is_in_choice(self, opt) -> bool:
        return opt in self.choice.entries

    def _open_help(self):
        index = self.list_view.index
        opt = self.options[index]

        help_text = opt.help.strip() or " There is no help available for this option."

        # --- Symbol value ---
        if opt.opt_type == "bool":
            symbol_val = "y" if opt.value else "n"
        elif opt.opt_type == "string":
            symbol_val = f'"{opt.value}"' if opt.value else '""'
        elif opt.opt_type == "int":
            symbol_val = str(opt.value or 0)
        else:
            symbol_val = str(opt.value)

        # --- Location path ---
        location = self.app.kconfig.get_option_location(opt.name)
        location_str = "\n".join(
            f"{' ' * (5 + i*2)}-> {p}" for i, p in enumerate(location)
        )

        # --- Depends (choice case) ---
        depends_str = "<choice>" if self._is_in_choice(opt) else (opt.depends_on or "None")

        # --- File info ---
        filename = getattr(opt, "filename", "unknown")
        lineno = getattr(opt, "lineno", "?")

        # --- Final formatted content ---
        content = (
            f"{help_text}\n"
            f" Symbol: {opt.name} [={symbol_val}]\n"
            f" Type  : {opt.opt_type}\n"
            f" Defined at {filename}:{lineno}\n"
            f"   Prompt: {opt.prompt}\n"
            f"   Depends on: {depends_str}\n"
            f"   Location:\n"
            f"{location_str}\n"
        )

        from mesonconfig.tui.widgets.help import HelpScreen

        self.app.push_screen(
            HelpScreen(
                title=opt.prompt,
                content=content,
                markdown=False,
            )
        )