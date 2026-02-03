#
# Textual CSS for Mesonconfig
# 2026, Remeny
#

# ---[ CSS ]--- #
def app_css(background: str, window_bg: str, window_fg: str) -> str:
    return f"""
    Screen {{
        background: {background};
        color: cyan;
    }}

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
        background: lightgray;
        color: black;
    }}

    #secondary_status {{
        background: black;
        color: lightgreen;
    }}

    .hidden {{
        display: none;
    }}

    #main_content {{
        height: 1fr;
    }}

    MenuDisplay {{
        height: 1fr;
        width: 100%;
        background: {window_bg};
        color: {window_fg};
        border: solid {window_fg};
        border-title-align: center;
        padding-top: 0;
        padding-left: 2;
        padding-right: 1;
        margin: 0 3 1 2;
    }}

    ListView .list-item--highlighted {{
        background: white;
        color: black;
    }}

    ListView .list-item--highlighted Label {{
        color: black;
    }}
    """
