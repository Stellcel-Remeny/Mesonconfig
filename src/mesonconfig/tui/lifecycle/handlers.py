#
# Lifecycle for Mesonconfig
# 2026, Remeny
#

# ---[ Libraries ]--- #
from textual.events import Key
from mesonconfig import core

# ---[ Lifecycle Handlers ]--- #
class LifecycleHandlers:
    # Stuff to happen on program resize
    def on_resize(self):
        self.update_header_separator()
        if not self.check_size() and not self.config.disable_minimum_size_check:
            self.hide_main_content()
            self.set_secondary_status(
                f"Window too small, resize it: Minimum {core.min_cols}x{core.min_rows}"
            )
            return

        # If the content was previously hidden and only now the user has resized it properly, show all stuff and get old status text
        if self.state.content_hidden:
            self.show_main_content()
            if self.state.secondary_visible:
                self.set_status(self.state.last_status_text)

    # Stuff to happen on user Key press
    def on_key(self, event: Key):
        if event.key.upper() == "Q": # Quit key
            self.exit()

    def on_mount(self):
        # Program logic here...
        self.header(f"Mesonconfig {core.get_version()}")
        self.set_status("Initializing...")
        self.dbg("Debug text will show in this color scheme, right down here.")
