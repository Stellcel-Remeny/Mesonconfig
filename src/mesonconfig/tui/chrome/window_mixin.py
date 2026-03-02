#
# Window mixin for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from mesonconfig import core

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
        # Hide main content area
        main = self.query("#main_content").first()
        if main:
            main.add_class("hidden")

        # Hide any active modal screen
        if len(self.screen_stack) > 1:
            self._hidden_screen = self.screen
            self.pop_screen()

        self.state.content_hidden = True


    def show_main_content(self):
        # Restore main content
        main = self.query("#main_content").first()
        if main:
            main.remove_class("hidden")

        # Restore previously hidden modal if one existed
        if getattr(self, "_hidden_screen", None):
            self.push_screen(self._hidden_screen)
            self._hidden_screen = None

        self.state.content_hidden = False