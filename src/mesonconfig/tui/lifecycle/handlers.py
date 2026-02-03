#
# Lifecycle for Mesonconfig
# 2026, Remeny
#

from textual.events import Key
from mesonconfig import core

class LifecycleHandlers:
    def on_resize(self):
        self.update_header_separator()
        if not self.check_size():
            self.hide_main_content()
            self.set_secondary_status(
                f"Window too small, resize it: Minimum {core.min_cols}x{core.min_rows}"
            )
            return

        if self._content_hidden:
            self.show_main_content()
            if self._secondary_visible:
                self.set_status(self._last_status_text)

    def on_key(self, event: Key):
        if event.key.upper() == "Q":
            self.exit()

    def on_mount(self):
        self.header(f"Mesonconfig {core.get_version()}")
        self.set_status("Initializing...")
        self.dbg("Debug text will show in this color scheme, right down here.")
