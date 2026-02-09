#
# KConfig definitions & classes file
# 2026, Remeny
#

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

    def find_option(self, name: str) -> Optional[KOption]:
        return self._options_index.get(name)

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

