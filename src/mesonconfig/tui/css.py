#
# Textual CSS for Mesonconfig
# 2026, Remeny
#

# ---[ Utilities ]--- #

def _safe(value: str, fallback: str) -> str:
    """Defensive color fallback."""
    return value if value else fallback


# ---[ CSS Builders ]--- #

def _base_layout(background: str) -> str:
    return f"""
    Screen {{
        background: {background};
        color: cyan;

        #main_content {{
            height: 1fr;
        }}

        .hidden {{
            display: none;
        }}
    }}
    """


def _header_css(window_bg: str, window_fg: str) -> str:
    return f"""
    #header_label {{
        content-align: left middle;
        height: 1;
        padding-left: 1;
    }}

    #header_separator {{
        color: cyan;
        height: 1;
        padding-left: 1;
    }}

    #primary_status,
    #secondary_status {{
        height: 1;
        width: 100%;
        padding-left: 1;
    }}

    #primary_status {{
        background: {window_bg};
        color: {window_fg};
    }}

    #secondary_status {{
        background: black;
        color: lightgreen;
    }}
    """


def _menu_display_css(highlight: str, window_border: str, window_bg: str, window_fg: str) -> str:
    return f"""
    MenuDisplay {{
        height: 1fr;
        width: 100%;
        background: {window_bg};
        color: {window_fg};
        border: {window_border} {window_fg};
        border-title-align: center;
        margin: 0 3 1 2;

        .menu-description {{
            padding-left: 2;
            padding-right: 1;
        }}

        .menu-frame {{
            border: {window_border} {window_fg};
            margin: 0 1 0 1;
            padding-left: 4;
            padding-right: 4;
            height: 1fr;
        }}

        .menu-list-wrapper {{
            width: 100%;
            align-horizontal: center;
        }}

        .menu-list {{
            width: 50%;
            background: transparent;
            
            ListItem {{
                Label {{
                    width: 100%;
                    content-align: left top;
                    color: {window_fg};
                }}
            }}
            
            ListItem.-highlight {{
                background: {highlight};
                
                Label {{
                    color: white;
                }}
            }}
        }}
    }}
    """


def _list_view_css() -> str:
    return """
    ListView {
        background: transparent;
        padding-left: 0;
        width: 100%;

        ListItem {
            Label {
                content-align: center middle;
                width: 100%;
            }
        }
    }
    """


def _control_bar_css(highlight_color: str, window_fg: str) -> str:
    return f"""
    #control_bar {{
        height: 1;
        align-horizontal: center;

        Button {{
            min-width: 0;
            width: auto;
            padding: 0;
            margin: 0 2;
            border: none;
            background: transparent;
            color: {window_fg};
        }}

        Button:focus {{
            background: white;
            color: {highlight_color};
        }}
    }}
    """


# ---[ Public Entry Point ]--- #

def app_css(
    background: str,
    window_border: str,
    window_bg: str,
    window_fg: str
) -> str:
    """
    Generates full Textual CSS theme.
    Textual-compatible.
    No functionality removed.
    """

    background = _safe(background, "black")
    window_border = _safe(window_border, "solid")
    window_bg = _safe(window_bg, "black")
    window_fg = _safe(window_fg, "white")

    return "\n".join([
        _base_layout(background),
        _header_css(window_bg, window_fg),
        _menu_display_css(background, window_border, window_bg, window_fg),
        _list_view_css(),
        _control_bar_css(background, window_fg),
    ])
