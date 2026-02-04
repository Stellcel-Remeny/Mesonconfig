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
        self.main_content.add_class("hidden")
        self.state.content_hidden = True

    def show_main_content(self):
        self.main_content.remove_class("hidden")
        self.state.content_hidden = False
