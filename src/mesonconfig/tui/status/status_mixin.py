#
# Status & Secondary status bar mixin for Mesonconfig
# 2026, Remeny
#

# ----[ Libraries ]--- #
from mesonconfig.core import log_debug
import time

# ---[ Status Mixin ]--- #
class StatusMixin:
    def _show_primary_status(self):
        # Show primary, hide secondary
        self.secondary_status.add_class("hidden")
        self.primary_status.remove_class("hidden")
        self.state.secondary_visible = False

    def _show_secondary_status(self):
        # Show secondary, hide primary
        self.primary_status.add_class("hidden")
        self.secondary_status.remove_class("hidden")
        self.state.secondary_visible = True

    def set_status(self, text: str):
        # Updates the primary status bar
        self.state.last_status_text = text
        self._show_primary_status()
        self.primary_status.update(text)

    def set_secondary_status(self, text: str):
        # Updates the secondary status bar
        self._show_secondary_status()
        self.secondary_status.update(text)

    def dbg(self, text: str):
        """
        Show debug text in the secondary status bar and wait some seconds
        so it's visible before resuming execution.

        Only shows if verbose mode is enabled.
        """
        if self.config.verbose:
            if self.config.logging:
                log_debug(msg=text, log_file=self.config.log_file)
            self.set_secondary_status(text)
            # Halts the program for specified seconds
            time.sleep(self.config.debug_timer)