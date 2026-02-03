#
# Status & Secondary status bar mixin for Mesonconfig
# 2026, Remeny
#

class StatusMixin:
    def _show_primary_status(self):
        self.secondary_status.add_class("hidden")
        self.primary_status.remove_class("hidden")
        self._secondary_visible = False

    def _show_secondary_status(self):
        self.primary_status.add_class("hidden")
        self.secondary_status.remove_class("hidden")
        self._secondary_visible = True

    def set_status(self, text: str):
        self._last_status_text = text
        self._show_primary_status()
        self.primary_status.update(text)

    def set_secondary_status(self, text: str):
        self._show_secondary_status()
        self.secondary_status.update(text)

    def dbg(self, text: str):
        if self._verbose:
            self.set_secondary_status(text)
