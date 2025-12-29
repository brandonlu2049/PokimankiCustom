

from aqt import mw, gui_hooks
from aqt.toolbar import Toolbar

ENABLE_LABEL_ID = "shige_pokemanki_gold"
DISABLE_LABEL_ID = "disable_pokemanki_gold"
addon_package = mw.addonManager.addonFromModule(__name__)
POKEBALL_ICON =   f"/_addons/{addon_package}/custom_py/pokeball.png"
LABEL_PYCMD = "shige_pokemanki_clicked"
LABEL_INDEX = 6

def add_pokemon_top_toolbar(links: list, toolbar: Toolbar) -> None:
    try:
        config = mw.addonManager.getConfig(__name__)

        if not config.get("show_pokemon_in_reviewer",True):
            # return
            custom_label_id = DISABLE_LABEL_ID
        else:
            custom_label_id = ENABLE_LABEL_ID

        html_label = f"<img src='{POKEBALL_ICON}' alt='pokeball' style='height: 1em ;'>"

        shortcut_key = ""

        def create_link(cmd,label,func,tip,id,):#aria-labelがHTMLになるとﾊﾞｸﾞる
            toolbar.link_handlers[cmd] = func
            title_attr = f'title="{tip}"' if tip else ""
            id_attr = f'id="{id}"' if id else ""
            return (
                f"""<a class=hitem tabindex="-1" aria-label="pokemon" """
                f"""{title_attr} {id_attr} href=# onclick="return pycmd('{cmd}')">"""
                f"""{label}</a>"""
            )

        from .show_deck_option import pokemon_icon_click

        link = create_link(
            cmd = LABEL_PYCMD,
            label = html_label,
            func = pokemon_icon_click,
            tip = shortcut_key ,
            id = custom_label_id ,
        )
        links.insert(LABEL_INDEX, link)
    except Exception as e:
        print(e)
        pass

# Hook registration is now handled in hooks_append.py

# Inspired by this add-on
# AJT Flexible Grading / Tatsumoto
# https://ankiweb.net/shared/info/1715096333
# https://github.com/Ajatt-Tools/FlexibleGrading