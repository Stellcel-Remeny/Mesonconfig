#
# Window mixin for Mesonconfig
# 2026, Remeny
#

from mesonconfig import core

class WindowChromeMixin:
    def check_size(self) -> bool:
        width, height = self.size
        return width >= core.min_cols and height >= core.min_rows

    def header(self, text: str):
        self.header_label.update(text)

    def update_header_separator(self):
        width = self.size.width
        if width > 1:
            self.header_separator.update("─" * (width - 1))

    def hide_main_content(self):
        self.main_content.add_class("hidden")
        self._content_hidden = True

    def show_main_content(self):
        self.main_content.remove_class("hidden")
        self._content_hidden = False
