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
        margin: 0 3 1 2;
    }}

    .menu-description {{
        padding-left: 2;
        padding-right: 1;
    }}

    ListView {{
        background: transparent;
        padding-left: 0;
        width: 100%;
    }}
    
    ListView ListItem Label {{
        content-align: center middle;
        width: 100%;
    }}
    
    .menu-frame {{
        border: solid {window_fg};
        margin: 0 1 2 1;
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
    }}

    .menu-list ListItem Label {{
        width: 100%;
        content-align: left top;
    }}
    """
