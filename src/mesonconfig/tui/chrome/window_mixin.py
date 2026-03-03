#
# Window mixin for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig import core
from textual.screen import ModalScreen

# ---[ Window Chrome Mixin ]--- #
class WindowChromeMixin:
    def check_size(self) -> bool:
        # Checks if current terminal size is minimum or greater
        # Returns:
        #   True = Equal to or more than minimum size
        #   False = Less than minimum size
        width, height = self.size
        return width >= core.min_cols and height >= core.min_rows

    def header(self, text: str):
        # Updates the header label
        self.header_label.update(text)

    def update_header_separator(self):
        # Redraws header separator
        width = self.size.width
        if width > 1:
            self.header_separator.update("─" * (width - 2))

    def hide_main_content(self):
        main = self.query("#main_content").first()
        if main:
            main.add_class("hidden")

        # Hide active modal screen (without popping it)
        if len(self.screen_stack) > 1:
            self.screen.add_class("hidden")

        self.state.content_hidden = True

    def show_main_content(self):
        # Restore main body
        main = self.query("#main_content").first()
        if main:
            main.remove_class("hidden")

        # Restore modal if one exists
        if len(self.screen_stack) > 1:
            self.screen.remove_class("hidden")

        self.state.content_hidden = False

    def dismiss_all_modals(self) -> None:
        """Dismiss all ModalScreen instances and triggers callbacks."""
        while (
            len(self.screen_stack) > 1 and
            isinstance(self.screen_stack[-1], ModalScreen)
        ):
            top_screen = self.screen_stack[-1]
            top_screen.dismiss(None)