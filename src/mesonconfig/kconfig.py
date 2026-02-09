#
# KConfig definitions & classes file
# 2026, Remeny
#

# TODO: Fix 'depends_on' issue (with nested menus)

# ---[ Libraries ]--- #
from dataclasses import dataclass, field
from typing import List, Optional, Union

# ---[ Classes ]--- #
@dataclass
class KEntry:
    pass

@dataclass
class KOption(KEntry):
    name: str
    opt_type: str
    prompt: Optional[str] = None
    default: Optional[str] = None
    depends_on: Optional[str] = None
    help: str = ""

    value: Optional[Union[bool, int, str]] = None


@dataclass(repr=False)
class KMenu(KEntry):
    title: str
    depends_on: Optional[str] = None
    entries: List[KEntry] = field(default_factory=list)


@dataclass(repr=False)
class KChoice(KEntry):
    prompt: Optional[str] = None
    depends_on: Optional[str] = None
    entries: List[KEntry] = field(default_factory=list)


@dataclass
class KComment(KEntry):
    text: str

class KConfig:
    def __init__(self, path: str):
        self.path = path
        self.mainmenu: Optional[str] = None
        self.entries: list[KEntry] = []
        self._options_index: dict[str, KOption] = {}

        self._parse_file(path)
        self._apply_defaults()

    def find_option(self, name: str) -> Optional[KOption]:
        return self._options_index.get(name)

    def _normalize_value(self, opt: KOption, raw: str):
        raw = raw.strip()

        if opt.opt_type == "bool":
            return raw.lower() in ("y", "yes", "true", "1")

        if opt.opt_type == "int":
            return int(raw)

        if opt.opt_type == "string":
            return raw.strip('"')

        return raw

    def _parse_file(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Stack holds where new entries go
        stack: list[list[KEntry]] = [self.entries]

        current_option: Optional[KOption] = None
        current_choice: Optional[KChoice] = None

        in_help = False
        help_indent = 0

        for raw in lines:
            line = raw.rstrip("\n")

            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip())
            stripped = line.strip()

            # ---- help block continuation ----
            if in_help:
                if indent > help_indent:
                    current_option.help += stripped + "\n"
                    continue
                else:
                    in_help = False

            # ---- mainmenu ----
            if stripped.startswith("mainmenu"):
                self.mainmenu = stripped.split('"', 1)[1].rsplit('"', 1)[0]
                continue

            # ---- menu ----
            if stripped.startswith("menu "):
                title = stripped.split('"', 1)[1].rsplit('"', 1)[0]
                menu = KMenu(title=title)
                stack[-1].append(menu)
                stack.append(menu.entries)
                continue

            if stripped == "endmenu":
                stack.pop()
                continue

            # ---- choice ----
            if stripped == "choice":
                current_choice = KChoice()
                stack[-1].append(current_choice)
                stack.append(current_choice.entries)
                continue

            if stripped == "endchoice":
                stack.pop()
                current_choice = None
                continue

            # ---- comment ----
            if stripped.startswith("comment"):
                text = stripped.split(" ", 1)[1].strip('"')
                stack[-1].append(KComment(text=text))
                continue

            # ---- config ----
            if stripped.startswith("config "):
                name = stripped.split()[1]
                current_option = KOption(name=name, opt_type="")
                stack[-1].append(current_option)
                self._options_index[name] = current_option
                continue

            # ---- option fields ----
            if current_option:
                if stripped.startswith(("bool ", "string ", "int ")):
                    typ, rest = stripped.split(" ", 1)
                    current_option.opt_type = typ
                    current_option.prompt = rest.strip('"')
                    continue

                if stripped.startswith("default "):
                    current_option.default = stripped.split(" ", 1)[1]
                    continue

                if stripped.startswith("depends on"):
                    current_option.depends_on = stripped.split("on", 1)[1].strip()
                    continue

                if stripped == "help":
                    in_help = True
                    help_indent = indent
                    current_option.help = ""
                    continue

    def _apply_defaults(self):
        for opt in self._options_index.values():
            if opt.default is not None:
                opt.value = self._normalize_value(opt, opt.default)

    def _eval_depends(self, expr: str) -> bool:
        tokens = expr.replace("&&", " and ").replace("||", " or ").replace("!", " not ").split()

        resolved = []
        for tok in tokens:
            if tok.isidentifier():
                opt = self._options_index.get(tok)
                resolved.append(str(bool(opt and opt.value)))
            else:
                resolved.append(tok)

        try:
            return bool(eval(" ".join(resolved)))
        except Exception:
            return False

    def is_visible(self, opt: KOption) -> bool:
        if not opt.depends_on:
            return True
        return self._eval_depends(opt.depends_on)
    
    def load_config(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                name, raw = line.split("=", 1)
                opt = self._options_index.get(name)
                if not opt:
                    continue

                opt.value = self._normalize_value(opt, raw)

    def save_config(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            for name, opt in sorted(self._options_index.items()):
                if opt.value is None:
                    continue

                if opt.opt_type == "bool":
                    val = "y" if opt.value else "n"
                elif opt.opt_type == "string":
                    val = f"\"{opt.value}\""
                else:
                    val = str(opt.value)

                f.write(f"{name}={val}\n")

    def get_visible_entries(self, entries=None):
        entries = entries or self.entries

        visible = []
        for e in entries:
            if isinstance(e, KOption):
                if self.is_visible(e):
                    visible.append(e)

            elif isinstance(e, KMenu):
                visible.append(e)

            elif isinstance(e, KChoice):
                visible.append(e)

            elif isinstance(e, KComment):
                visible.append(e)

        return visible

    def set_option(self, name: str, value):
        opt = self._options_index.get(name)
        if not opt:
            raise KeyError(name)

        opt.value = self._normalize_value(opt, str(value))


    # ---[ Test ]--- #
    def dump(self, entries=None, depth=0):
        entries = entries or self.entries

        for e in entries:
            indent = "  " * depth

            if isinstance(e, KMenu):
                print(f"{indent}MENU: {e.title}")
                self.dump(e.entries, depth + 1)

            elif isinstance(e, KChoice):
                print(f"{indent}CHOICE")
                self.dump(e.entries, depth + 1)

            elif isinstance(e, KOption):
                print(f"{indent}CONFIG {e.name} ({e.opt_type})")

            elif isinstance(e, KComment):
                print(f"{indent}# {e.text}")

# ---[ Functions ]--- #
#   Test   #
def dbg_disp_menu_mockup(menu, kc, depth=0):
    indent = "  " * depth

    for entry in kc.get_visible_entries(menu.entries):
        if isinstance(entry, KMenu):
            print(f"{indent}[+] {entry.title}")
            dbg_disp_menu_mockup(entry, kc, depth + 1)

        elif isinstance(entry, KChoice):
            print(f"{indent}( ) choice")
            for opt in entry.entries:
                state = "*" if opt.value else " "
                print(f"{indent}  ({state}) {opt.prompt}")

        elif isinstance(entry, KOption):
            if entry.opt_type == "bool":
                state = "[X]" if entry.value else "[ ]"
                print(f"{indent}{state} {entry.prompt}")
            else:
                print(f"{indent}{entry.prompt}: {entry.value}")

        elif isinstance(entry, KComment):
            print(f"{indent}# {entry.text}")