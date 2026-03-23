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

# ---[ Prefixes ]--- #
TYPE_PREFIXES = ("bool ", "string ", "int ")

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
    default_if: Optional[str] = None
    depends_on: Optional[str] = None
    help: str = ""

    value: Optional[Union[bool, int, str]] = None

    filename: Optional[str] = None
    lineno: Optional[int] = None


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
        self._depends_cache = {}

        self._build_tree(path)
        self._validate_tree()
        self._apply_defaults()

        self._initial_values = {
            name: opt.value for name, opt in self._options_index.items()
        }

    def _normalize_value(self, opt: KOption, raw: str) -> Union[bool, int, str]:
        raw = raw.strip()

        if opt.opt_type == "bool":
            return raw.lower() in ("y", "yes", "true", "1")

        if opt.opt_type == "int":
            return int(raw)

        if opt.opt_type == "string":
            raw = raw.strip()
            if (raw.startswith('"') and raw.endswith('"')) or \
            (raw.startswith("'") and raw.endswith("'")):
                raw = raw[1:-1]
            return raw

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
            if stripped.startswith("mainmenu "):
                if self.mainmenu is not None:
                    self._syntax_error(lineno, line, "Duplicate 'mainmenu'")
                
                self.mainmenu = self._parse_text_after_keyword(stripped, "mainmenu")
                continue

            # ---- menu ----
            if stripped.startswith("menu "):
                if context_stack[-1] not in (ParseContext.ROOT, ParseContext.MENU):
                    self._syntax_error(lineno, line, "unexpected 'menu'")

                title = self._parse_text_after_keyword(stripped, "menu")
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
                    self._syntax_error(lineno, line, "unexpected 'endmenu'")

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
                    self._syntax_error(lineno, line, "nested 'choice' is not allowed'")

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
                    self._syntax_error(lineno, line, "unexpected 'endchoice'")

                stack.pop()
                context_stack.pop()

                current_choice = None
                current_option = None
                continue
            
            # ---- comment ----
            if stripped.startswith("comment "):
                current_option = None
                text = self._parse_text_after_keyword(stripped, "comment")
                stack[-1].append(KComment(text=text))
                continue

            # ---- source ----
            if stripped.startswith("source "):
                #untested block of code
                # TODO: Do testing...
                raw = self._parse_text_after_keyword(stripped, "source")

                # no variable expansion yet — keep it simple
                src_path = base_dir / raw

                if not src_path.is_file():
                    self._file_not_found_error(lineno, line, src_path)

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

            # ---- option fields without config ----
            if stripped.startswith(TYPE_PREFIXES):
                if current_option is None:
                    self._syntax_error(lineno, line, "option type without 'config NAME'")

            # ---- config ----
            if stripped.startswith("config "):

                # nested config is not allowed
                if context_stack[-1] == ParseContext.OPTION:
                    self._syntax_error(lineno, line, "nested 'config' is not allowed")

                # previous option missing type
                if current_option and current_option.prompt is None:
                    self._syntax_error(lineno, line, f"option '{current_option.name}' missing type")

                name = stripped.split()[1]

                current_option = KOption(
                    name=name,
                    opt_type="bool",
                    filename=Path(path).name,
                    lineno=lineno
                )

                stack[-1].append(current_option)
                self._options_index[name] = current_option

                context_stack.append(ParseContext.OPTION)
                continue

            # ---- depends ----
            if stripped.startswith("depends on "):
                expr = stripped[11:].strip()

                if current_option:
                    current_option.depends_on = expr
                elif current_menu:
                    current_menu.depends_on = expr
                elif current_choice:
                    current_choice.depends_on = expr
                else:
                    self._syntax_error(lineno, line, "'depends on' outside valid context")
                
                continue

            # ---- choice prompt ----
            if current_choice and stripped.startswith("prompt "):
                current_choice.prompt = self._parse_text_after_keyword(stripped, "prompt")
                continue

            # ---- option fields ----
            if current_option:
                if stripped.startswith(TYPE_PREFIXES):
                    typ, rest = stripped.split(" ", 1)
                    current_option.opt_type = typ
                    current_option.prompt = rest.strip('"')
                    continue
                
                # after handling type lines
                if stripped.startswith("config ") and current_option and current_option.prompt is None:
                    self._syntax_error(lineno, line, f"Config '{current_option.name}' is missing type")

                if stripped.startswith("default "):
                    raw = stripped.split(" ", 1)[1]

                    if " if " in raw:
                        val, cond = raw.split(" if ", 1)
                        current_option.default = self._normalize_value(current_option, val.strip())
                        current_option.default_if = cond.strip()
                    else:
                        current_option.default = self._normalize_value(current_option, raw.strip())

                    continue

                if stripped.startswith("depends on "):
                    current_option.depends_on = stripped.split("on ", 1)[1].strip()
                    continue

                if stripped == "help":
                    in_help = True
                    help_indent = indent
                    current_option.help = ""
                    continue

        # Close open option at EOF
        if current_option and context_stack[-1] == ParseContext.OPTION:
            context_stack.pop()

        if len(context_stack) != 1:
            self._syntax_error(lineno, line, "Unclosed block (missing endmenu or endchoice)")

    def _apply_defaults(self) -> None:
        """Apply parsed defaults into option.value so visibility can use them."""
        for opt in self._options_index.values():

            if opt.default is None:
                continue

            if opt.default_if:
                if self._eval_depends(opt.default_if):
                    opt.value = opt.default
            else:
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

        # Meant to speed up results but destroys dependency visibility
        #if expr in self._depends_cache:
        #    return self._depends_cache[expr]
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

        self._depends_cache[expr] = result
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
    
    def _parse_text_after_keyword(self, line: str, keyword: str) -> str:
        # We strip quotes on text after keyword, if they exist.
        text = line[len(keyword):].strip()

        # remove trailing comments
        if "#" in text:
            text = text.split("#",1)[0].strip()

        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]

        return text

    def _depends_satisfied(self, opt: KOption) -> bool:
        exprs = []

        parent = self.get_option_parents(opt.name)
        if parent:
            exprs.append(parent)

        if opt.depends_on:
            exprs.append(opt.depends_on)

        if not exprs:
            return True

        return self._eval_depends(" and ".join(exprs))

    def _load_config_dict(self, path: str) -> dict[str, str]:
        result = {}

        p = Path(path)
        if not p.exists():
            return result  # empty baseline

        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                name, raw = line.split("=", 1)
                name = name.strip()
                raw = raw.strip().strip("'\"")

                result[name] = raw

        return result

    def _serialize_config_dict(self) -> dict[str, str]:
        result = {}

        for name, opt in self._options_index.items():
            if opt.value is None:
                continue

            if opt.opt_type == "bool":
                val = "true" if opt.value else "false"
            elif opt.opt_type == "string":
                val = str(opt.value)
            else:
                val = str(opt.value)

            result[name] = val

        return result

    def _write_entries(self, f, entries, depth=0):
        for e in entries:
            if isinstance(e, KMenu):
                title = e.title.strip()

                f.write("\n#\n")
                f.write(f"# {title}\n")
                f.write("#\n")

                self._write_entries(f, e.entries, depth + 1)

                f.write(f"# end of {title}\n")

            elif isinstance(e, KOption):
                if e.value is None:
                    continue

                # TODO
                #name = f"CONFIG_{e.name}"
                name = e.name

                if e.opt_type == "bool":
                    f.write(f"{name} = {'true' if e.value else 'false'}\n")

                elif e.opt_type == "string":
                    f.write(f"{name} = '{e.value}'\n")

                elif e.opt_type == "int":
                    f.write(f"{name} = {e.value}\n")
                    
                else:
                    # wtf?
                    raise ValueError(f"Unknown option type: {e.opt_type}")

            elif isinstance(e, KComment):
                f.write("#\n")
                f.write(f"# {e.text}\n")
                f.write("#\n\n")

            elif isinstance(e, KChoice):
                # choices behave like flat groups
                self._write_entries(f, e.entries, depth + 1)

    def _syntax_error(self, lineno, line, msg):
        raise SyntaxError(
            f"Line {lineno}: {msg}\n"
            f"  >> {line}"
        )

    def _file_not_found_error(self, lineno, line, path):
        raise FileNotFoundError(
            f"Line {lineno}: {path}\n"
            f"  >> {line}"
        )

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
                    combined = e.depends_on
                    if parent_depends and combined:
                        combined = f"{parent_depends} and {combined}"
                    elif parent_depends:
                        combined = parent_depends

                    if combined is None or self._eval_depends(combined):
                        res = walk(e.entries, combined)
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
                combined = e.depends_on
                if parent_depends and combined:
                    combined = f"{parent_depends} and {combined}"
                elif parent_depends:
                    combined = parent_depends

                if combined is None or self._eval_depends(combined):
                    visible.append(e)
                    # propagate visibility to children
                    e.visible_entries = self.get_visible_entries(e.entries, combined)

            elif isinstance(e, KComment):
                visible.append(e)

        return visible
    
    def enforce_dependencies(self) -> None:
        """
        Iteratively enforce dependency constraints until stable.
        This avoids order-dependent inconsistencies.
        """
        changed = True

        while changed:
            changed = False

            for opt in self._options_index.values():
                if not self._depends_satisfied(opt):
                    if opt.opt_type == "bool":
                        new_val = False
                    elif opt.opt_type == "string":
                        new_val = ""
                    elif opt.opt_type == "int":
                        new_val = 0
                    else:
                        continue

                    if opt.value != new_val:
                        opt.value = new_val
                        changed = True

    def load_config(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                # Strip whitespace
                line = line.strip()

                # Ignore empty or commented lines.
                if not line or line.startswith("#"):
                    continue

                # No equals means it is not a valid option assignment, skip it.
                if "=" not in line:
                    continue

                # Split into name and value and get rid of whitespace yet again
                name, raw = line.split("=", 1)
                name = name.strip()
                raw = raw.strip()

                # Now set the option.
                self.set_option(name, raw)

        # update baseline snapshot
        self._initial_values = {
            name: opt.value for name, opt in self._options_index.items()
        }

    def save_config(self, path: str, tool_name: str = "Diana", tool_version: str = "Burnwood") -> None:
        from datetime import datetime
        from textwrap import dedent

        # Handle dependencies
        self.enforce_dependencies()

        target = Path(path)
        old_file = target.with_suffix(target.suffix + ".old")  # filename.old

        # If target exists, handle old file
        if target.exists():
            if old_file.exists():
                old_file.unlink()  # delete existing .old
            target.rename(old_file)  # move current file to .old

        # Write new config
        with open(target, "w", encoding="utf-8") as f:
            f.write(dedent(f"""\
                #
                # Automatically generated by {tool_name} {tool_version}
                # From {self.path}
                # Time: {datetime.now().isoformat()}
                #\n
                """))

            f.write("[project options]\n")
            self._write_entries(f, self.entries)

    def set_option(self, name: str, value) -> None:
        opt = self._options_index.get(name)
        if not opt:
            raise KeyError(name)

        opt.value = self._normalize_value(opt, str(value))

    def get_option_location(self, opt_name: str) -> list[str]:
        path = []

        def walk(entries, stack):
            for e in entries:
                if isinstance(e, KOption):
                    if e.name == opt_name:
                        if e.opt_type == "bool":
                            val = "y" if e.value else "n"
                        elif e.opt_type == "string":
                            val = f'"{e.value}"' if e.value is not None else '""'
                        elif e.opt_type == "int":
                            val = str(e.value) if e.value is not None else "0"
                        else:
                            val = str(e.value)

                        return stack + [f"{e.prompt} ({e.name} [={val}])"]
                elif isinstance(e, KMenu):
                    res = walk(e.entries, stack + [e.title])
                    if res:
                        return res
                elif isinstance(e, KChoice):
                    res = walk(e.entries, stack)
                    if res:
                        return res
            return None

        result = walk(self.entries, [])
        return result or []

    def has_changes(self, output_path: str) -> bool:
        current = self._serialize_config_dict()
        existing = self._load_config_dict(output_path)

        return current != existing

    def reset_to_defaults(self) -> None:
        """
        Reset all option values to their default state.
        """
        # Clear all values first
        for opt in self._options_index.values():
            opt.value = None

        # Reapply defaults
        self._apply_defaults()

        # Reset baseline snapshot
        self._initial_values = {
            name: opt.value for name, opt in self._options_index.items()
        }

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
