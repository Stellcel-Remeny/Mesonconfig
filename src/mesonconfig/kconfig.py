#
# KConfig definitions & classes file
# 2026, Remeny
#

"""
Grammar:

mainmenu ::= 'mainmenu' STRING
menu     ::= 'menu' STRING entries 'endmenu'
choice   ::= 'choice' entries 'endchoice'
entries  ::= (menu | choice | config | comment)*
config   ::= 'config' NAME type [default] [depends] [help]
source   ::= 'source' STRING
"""

# ---[ Libraries ]--- #
from dataclasses import dataclass, field
from typing import List, Literal, Optional, Union
from enum import Enum, auto
from pathlib import Path

# ---[ Classes ]--- #
class ParseContext(Enum):
    ROOT = auto()
    MENU = auto()
    CHOICE = auto()
    OPTION = auto()

# ---[ Dataclasses ]--- #
@dataclass
class KEntry:
    pass

@dataclass
class KOption(KEntry):
    name: str
    opt_type: Literal["bool", "int", "string"]
    prompt: Optional[str] = None
    default: Optional[Union[bool, int, str]] = None
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
    def __init__(self, path: str) -> None:
        self.path = path
        self.mainmenu: Optional[str] = None
        self.entries: list[KEntry] = []
        self._options_index: dict[str, KOption] = {}

        self._build_tree(path)
        self._validate_tree()
        self._apply_defaults()

    def _normalize_value(self, opt: KOption, raw: str) -> Union[bool, int, str]:
        raw = raw.strip()

        if opt.opt_type == "bool":
            return raw.lower() in ("y", "yes", "true", "1")

        if opt.opt_type == "int":
            return int(raw)

        if opt.opt_type == "string":
            return raw.strip('"')

        return raw

    def _build_tree(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Stack holds where new entries go
        stack: list[list[KEntry]] = [self.entries]
        context_stack: list[ParseContext] = [ParseContext.ROOT]

        current_option: Optional[KOption] = None
        current_choice: Optional[KChoice] = None
        current_menu: Optional[KMenu] = None

        base_dir = Path(path).parent

        in_help = False
        help_indent = 0

        for lineno, raw in enumerate(lines, 1):
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

            # If we're inside an option but the current line is not an option-field,
            # then close the option context proactively.
            # (This avoids an OPTION remaining on the context_stack when we hit endmenu.)
            if current_option:
                # lines that belong to an option
                option_prefixes = ("bool ", "string ", "int ", "default ", "depends on", "help")
                if not stripped.startswith(option_prefixes):
                    # close option context
                    current_option = None
                    if context_stack and context_stack[-1] == ParseContext.OPTION:
                        context_stack.pop()

            # ---- mainmenu ----
            if stripped.startswith("mainmenu"):
                if self.mainmenu is not None:
                    raise SyntaxError(
                        f"Line {lineno}: Duplicate 'mainmenu'\n"
                        f"  >> {line}\n"
                        f"Expected: config | menu | comment"
                    )
                
                self.mainmenu = stripped.split('"', 1)[1].rsplit('"', 1)[0]
                continue

            # ---- menu ----
            if stripped.startswith("menu "):
                if context_stack[-1] not in (ParseContext.ROOT, ParseContext.MENU):
                    raise SyntaxError(
                        f"Line {lineno}: unexpected 'menu'\n"
                        f"  >> {line}\n"
                        f"Expected: config | comment"
                    )

                title = stripped.split('"', 1)[1].rsplit('"', 1)[0]
                menu = KMenu(title=title)
                stack[-1].append(menu)
                stack.append(menu.entries)
                context_stack.append(ParseContext.MENU)
                current_option = None
                current_menu = menu
                continue

            if stripped == "endmenu":
                # If we have an open OPTION context, close it first.
                while context_stack and context_stack[-1] == ParseContext.OPTION:
                    context_stack.pop()
                    current_option = None

                if context_stack[-1] != ParseContext.MENU:
                    raise SyntaxError(
                        f"Line {lineno}: unexpected 'endmenu'\n"
                        f"  >> {line}\n"
                        f"Expected: config | menu | comment"
                    )
                stack.pop()
                context_stack.pop()

                # also clear choice state if any (defensive)
                current_choice = None
                current_option = None
                current_menu = None
                continue

            # ---- choice ----
            if stripped == "choice":
                if context_stack[-1] != ParseContext.MENU:
                    raise SyntaxError(f"Line {lineno}: nested 'choice' is not allowed")

                current_choice = KChoice()
                stack[-1].append(current_choice)
                stack.append(current_choice.entries)
                context_stack.append(ParseContext.CHOICE)
                current_option = None
                continue

            if stripped == "endchoice":
                # Close any open OPTION context first
                while context_stack and context_stack[-1] == ParseContext.OPTION:
                    context_stack.pop()
                    current_option = None

                if context_stack[-1] != ParseContext.CHOICE:
                    raise SyntaxError(
                        f"Line {lineno}: unexpected 'endchoice'\n"
                        f"  >> {line}\n"
                        f"Expected: config | menu | comment"
                    )
                stack.pop()
                context_stack.pop()

                current_choice = None
                current_option = None
                continue
            
            # ---- comment ----
            if stripped.startswith("comment"):
                current_option = None
                text = stripped.split(" ", 1)[1].strip('"')
                stack[-1].append(KComment(text=text))
                continue

            # ---- source ----
            if stripped.startswith("source "):
                raw = stripped.split(" ", 1)[1].strip().strip('"')

                # no variable expansion yet — keep it simple
                src_path = base_dir / raw

                if not src_path.is_file():
                    raise FileNotFoundError(f"source file not found: {src_path}")

                # recursively parse source file
                sub_kc = KConfig(str(src_path))

                # merge entries
                stack[-1].extend(sub_kc.entries)

                # merge option index (detect duplicates)
                for name, opt in sub_kc._options_index.items():
                    if name in self._options_index:
                        raise ValueError(f"Duplicate option from source(): {name}")
                    self._options_index[name] = opt

                continue

            # ---- config ----
            if stripped.startswith("config "):
                # leave OPTION context if already in one
                if context_stack[-1] == ParseContext.OPTION:
                    context_stack.pop()

                name = stripped.split()[1]
                current_option = KOption(name=name, opt_type="bool")  # temporary
                stack[-1].append(current_option)
                self._options_index[name] = current_option

                context_stack.append(ParseContext.OPTION)
                continue

            # ---- depends ----
            if stripped.startswith("depends on"):
                if current_option:
                    current_option.depends_on = stripped.split("on", 1)[1].strip()
                    continue

                if current_menu:
                    current_menu.depends_on = stripped.split("on", 1)[1].strip()
                    continue

                if current_choice:
                    current_choice.depends_on = stripped.split("on", 1)[1].strip()
                    continue

            # ---- option fields ----
            if current_option:
                if stripped.startswith(("bool ", "string ", "int ")):
                    typ, rest = stripped.split(" ", 1)
                    current_option.opt_type = typ
                    current_option.prompt = rest.strip('"')
                    continue
                
                # after handling type lines
                if stripped.startswith("config ") and current_option and current_option.prompt is None:
                    raise SyntaxError(
                        f"Line {lineno}: Config '{current_option.name} is missing type'\n"
                        f"  >> {line}\n"
                        f"Expected: bool | string | int"
                    )

                if stripped.startswith("default "):
                    raw = stripped.split(" ", 1)[1]
                    current_option.default = self._normalize_value(current_option, raw)
                    continue

                if stripped.startswith("depends on"):
                    current_option.depends_on = stripped.split("on", 1)[1].strip()
                    continue

                if stripped == "help":
                    in_help = True
                    help_indent = indent
                    current_option.help = ""
                    continue

    def _apply_defaults(self) -> None:
        """Apply parsed defaults into option.value so visibility can use them."""
        for opt in self._options_index.values():
            if opt.default is not None:
                # default was already normalized during parsing
                opt.value = opt.default

    def _validate_tree(self) -> None:
        seen: set[str] = set()

        def walk(entries: list[KEntry]) -> None:
            for e in entries:
                if isinstance(e, KOption):
                    # ---- name uniqueness ----
                    if e.name in seen:
                        raise ValueError(f"Duplicate option '{e.name}'")
                    seen.add(e.name)

                    # ---- required fields ----
                    if e.prompt is None:
                        raise ValueError(f"Option '{e.name}' missing prompt")
                    if e.opt_type not in ("bool", "int", "string"):
                        raise ValueError(f"Option '{e.name}' has invalid type")

                    # ---- depends_on validation ----
                    if e.depends_on:
                        for tok in e.depends_on.replace("&&", " ").replace("||", " ").split():
                            if tok.isidentifier() and tok not in self._options_index:
                                raise ValueError(
                                    f"Option '{e.name}' depends on unknown option '{tok}'"
                                )

                elif isinstance(e, KChoice):
                    if not e.entries:
                        raise ValueError("Choice block must contain at least one entry")
                    walk(e.entries)

                elif isinstance(e, KMenu):
                    if e.depends_on:
                        for tok in e.depends_on.replace("&&", " ").replace("||", " ").split():
                            if tok.isidentifier() and tok not in self._options_index:
                                raise ValueError(
                                    f"Menu '{e.title}' depends on unknown option '{tok}'"
                                )
                    walk(e.entries)

        walk(self.entries)

    def _eval_depends(self, expr: str) -> bool:
        # --- Tokenize ---
        import re
        token_pattern = re.compile(r'(!|\(|\)|\w+|&&|\|\|)')
        tokens = token_pattern.findall(expr)
        tokens = ['and' if t=='&&' else 'or' if t=='||' else t for t in tokens]

        pos = 0

        def resolve(name: str) -> bool:
            opt = self._options_index.get(name)
            if opt is None or opt.value is None:
                return False
            return bool(opt.value)

        def parse_expr():
            return parse_or()

        def parse_or():
            nonlocal pos
            val = parse_and()
            while pos < len(tokens) and tokens[pos] == "or":
                pos += 1
                val = val or parse_and()
            return val

        def parse_and():
            nonlocal pos
            val = parse_not()
            while pos < len(tokens) and tokens[pos] == "and":
                pos += 1
                val = val and parse_not()
            return val

        def parse_not():
            nonlocal pos
            if tokens[pos] == "!":
                pos += 1
                return not parse_not()
            return parse_atom()

        def parse_atom():
            nonlocal pos
            tok = tokens[pos]
            if tok == "(":
                pos += 1
                val = parse_expr()
                if pos >= len(tokens) or tokens[pos] != ")":
                    raise ValueError("Unmatched '(' in depends_on")
                pos += 1
                return val
            elif tok in ("and", "or", ")"):
                raise ValueError(f"Unexpected token '{tok}' in atom")
            pos += 1
            return resolve(tok)

        result = parse_expr()
        if pos != len(tokens):
            raise ValueError(f"Unexpected token remaining: {tokens[pos:]}")
        return result

    def _is_visible_local(self, opt: KOption, parent_depends: Optional[str] = None) -> bool:
        exprs = []

        if parent_depends:
            exprs.append(parent_depends)

        if opt.depends_on:
            exprs.append(opt.depends_on)

        if not exprs:
            return True

        return self._eval_depends(" and ".join(exprs))
    
    def find_option(self, name: str) -> Optional[KOption]:
        return self._options_index.get(name)
    
    def is_visible(self, opt: KOption) -> bool:
        """
        Return True if the option would actually appear in the UI.
        """
        def walk(entries, parent_depends=None):
            for e in entries:
                if e is opt:
                    return self._is_visible_local(opt, parent_depends)

                if isinstance(e, KMenu):
                    combined = e.depends_on
                    if parent_depends and combined:
                        combined = f"{parent_depends} and {combined}"
                    elif parent_depends:
                        combined = parent_depends

                    if combined is None or self._eval_depends(combined):
                        res = walk(e.entries, combined)
                        if res is not None:
                            return res
                elif isinstance(e, KChoice):
                    res = walk(e.entries, parent_depends)
                    if res is not None:
                        return res
            return None

        return bool(walk(self.entries))
        
    def get_option_parents(self, opt_name: str) -> Optional[str]:
        """
        Walk the tree and return the combined parent/menu `depends_on` expression
        that applies to the option. Returns None if no parent depends exist.
        """
        def walk(entries: list[KEntry], acc: Optional[str]) -> Optional[str]:
            for e in entries:
                if isinstance(e, KOption):
                    if e.name == opt_name:
                        return acc
                elif isinstance(e, KMenu) or isinstance(e, KChoice):
                    # accumulate depends: parent AND this entry's depends
                    new_acc = acc
                    if e.depends_on:
                        new_acc = e.depends_on if new_acc is None else f"{new_acc} and {e.depends_on}"
                    res = walk(e.entries, new_acc)
                    if res is not None:
                        return res
            return None

        return walk(self.entries, None)
    
    def get_visible_entries(self, entries=None, parent_depends=None):
        if entries is None:
            entries = self.entries

        visible = []

        for e in entries:
            if isinstance(e, KOption):
                if self._is_visible_local(e, parent_depends):
                    visible.append(e)

            elif isinstance(e, KMenu):
                # compute combined depends
                combined = e.depends_on
                if parent_depends and combined:
                    combined = f"{parent_depends} and {combined}"
                elif parent_depends:
                    combined = parent_depends

                if combined is None or self._eval_depends(combined):
                    # include the menu itself
                    visible.append(e)
                    # **recurse into children**
                    e.visible_entries = self.get_visible_entries(e.entries, combined)

            elif isinstance(e, KChoice):
                visible.append(e)

            elif isinstance(e, KComment):
                visible.append(e)

        return visible
    
    def load_config(self, path: str) -> None:
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

    def save_config(self, path: str) -> None:
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

    def set_option(self, name: str, value) -> None:
        opt = self._options_index.get(name)
        if not opt:
            raise KeyError(name)

        opt.value = self._normalize_value(opt, str(value))


    # ---[ Test ]--- #
    def dump(self, entries=None, depth=0) -> None:
        if entries is None:
            entries = self.entries

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
