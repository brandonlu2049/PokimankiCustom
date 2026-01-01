

import re
import os
from aqt import mw, gui_hooks, QCursor, dialogs
from aqt.qt import QPushButton, QTimer, QAction
from ..utils import *
from aqt.utils import openLink, tooltip
from aqt.sound import play
from .pokemankiConfig import change_log_popup_B, IS_RATE_THIS, CHANGE_LOG

ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"

POKE_TYPE = "PokeType"
from .path_manager import InfoDialog
from .more_info import show_more_info
from .pokemon_wiki import pokemon_web_view
from ..hooks.overview import reset_overview_globals


is_tarad_window_run = False


def addButtons(handled, message, context):

    if message == "shige_pokemanki_button_1":
        actions = mw.pokemenu.actions()
        for action in actions:
            if action.text() == "&Trade":
                action.trigger()
                break
        return (True, None)
    elif message == "shige_pokemanki_button_2":
        pos = QCursor.pos()
        try:mw.pokemenu.exec(pos)
        except:mw.pokemenu.exec_(pos)
        return (True, None)
    elif message == "shige_pokemanki_button_3":
        change_log_popup_B()
        config = mw.addonManager.getConfig(__name__)


        customBtns = []
        pokeReload_button = QPushButton("PokeReload")
        pokeReload_button.clicked.connect(lambda : close_new_deck_stats_dialog(dialogs))
        pokeReload_button.clicked.connect(mw.onStats)
        customBtns.append(pokeReload_button)

        if (config[IS_RATE_THIS]):
            config[POKE_TYPE] = not config[POKE_TYPE]
            if config[POKE_TYPE]:
                InfoDialog(
                    "Animated Pokemon mode!",
                    parent=mw,
                    title="Pokemanki Custom",
                    customBtns=customBtns
                )
            else:
                InfoDialog(
                    "Static Pokemon mode!",
                    parent=mw,
                    title="Pokemanki Custom",
                    customBtns=customBtns
                )
            mw.addonManager.writeConfig(__name__, config)

        return (True, None)
    elif message == "shige_pokemanki_button_4":
        QTimer.singleShot(0, show_more_info)
        return (True, None)

    elif "shige_pokemanki_button_5" in message:
        parts = message.split(":", 1)
        if len(parts) == 2:
            command, argument = parts
            # search_url = f"https://pokemon.fandom.com/wiki/{argument}"
            argument = re.sub(r'[^a-zA-Z]', '-', argument)
            argument = re.sub(r'-+', '-', argument)
            print(argument)
            search_url = f"https://www.pokemon.com/us/pokedex/{argument}"
            print(search_url)
            pokemon_web_view(search_url)

            argument = re.sub('Farfetchd', 'Farfetch_d', argument)
            addon_path = os.path.dirname(__file__)
            sound_path = os.path.join(addon_path,"pokemon_sound",f"{argument}.mp3")
            play(sound_path)

        # else:
        #     command = parts[0]
        #     argument = None

        return (True, None)

    elif "shige_pokemon_sound" in message:
        parts = message.split(":", 1)
        if len(parts) == 2:
            command, argument = parts
            addon_path = os.path.dirname(__file__)
            sound_path = os.path.join(addon_path,"pokemon_sound",f"{argument}.mp3")
            play(sound_path)
        return (True, None)

    elif "select_pokemon" in message:
        parts = message.split(":", 1)
        if len(parts) == 2:
            _, pokemon_id = parts
            from ..helpers.config import save_synced_conf
            save_synced_conf("current_pokemon_id", pokemon_id)
            print(f"Set current Pokemon ID to: {pokemon_id}")
            
            # Update the UI immediately via JavaScript
            if mw and hasattr(mw, 'web') and mw.web:
                js_code = f"""
                // Remove current highlighting from all cards
                document.querySelectorAll('.pk-st-current').forEach(card => {{
                    card.classList.remove('pk-st-current');
                }});
                
                // Find and highlight the new current Pokemon card
                document.querySelectorAll('.pk-st-card').forEach(card => {{
                    if (card.onclick && card.onclick.toString().includes('{pokemon_id}')) {{
                        card.classList.add('pk-st-current');
                    }}
                }});
                """
                mw.web.eval(js_code)
            
            # Update the top toolbar to show the newly selected pokemon (respecting config settings)
            config = mw.addonManager.getConfig(__name__)
            if config.get("show_pokemon_in_reviewer", True):
                from ..helpers.pokemon_helpers import get_pokemon_icon_and_level
                get_pokemon_icon_and_level(None)
            
            # Also clear cached data for future refreshes
            reset_overview_globals()
        return (True, None)
    elif message == "egg_exchange_pokemanki_button":
        print("Egg Exchange button clicked")
        actions = mw.pokemenu.actions()
        for action in actions:
            if action.text() == "&Egg Exchange":
                action.trigger()
                break
        return (True, None)

    elif message == "shop_pokemanki_button":
        print("Shop button clicked")
        actions = mw.pokemenu.actions()
        for action in actions:
            if action.text() == "&Shop":
                action.trigger()
                break
        return (True, None)

    elif "customize_pokemon" in message:
        parts = message.split(":", 1)
        if len(parts) == 2:
            _, pokemon_id = parts
            from ..gui.pokimanki_customization import open_pokemon_customization
            QTimer.singleShot(0, lambda: open_pokemon_customization(pokemon_id))
        return (True, None)

    else:
        return handled


from aqt import DialogManager

def close_new_deck_stats_dialog(dialog_manager: DialogManager):
    new_deck_stats_dialogs = dialog_manager._dialogs.get("NewDeckStats")
    dialog_instance = new_deck_stats_dialogs[1]
    if dialog_instance:
        dialog_instance.close()


def toggle_checkbox_state():
    config = mw.addonManager.getConfig(__name__)
    config["auto_open_trade"] = not config.get("auto_open_trade", False)
    mw.addonManager.writeConfig(__name__, config)


def toggle_checkbox_pokemon_overview():
    config = mw.addonManager.getConfig(__name__)
    # config["Show Pokemon in the overview"] = not config.get("Show Pokemon in the overview", True)
    config["show_pokemon_in_home_and_overview"] = not config.get("show_pokemon_in_home_and_overview", True)
    mw.addonManager.writeConfig(__name__, config)


def toggle_checkbox_pokemon_reviewer():
    config = mw.addonManager.getConfig(__name__)
    config["show_pokemon_in_reviewer"] = not config.get("show_pokemon_in_reviewer", True)
    mw.addonManager.writeConfig(__name__, config)
    from ..helpers.pokemon_helpers import toggle_on_or_off_top_toolbar
    toggle_on_or_off_top_toolbar()

def toggle_hide_banner_and_options():
    config = mw.addonManager.getConfig(__name__)
    config["hide_banner_and_options"] = not config.get("hide_banner_and_options", False)
    mw.addonManager.writeConfig(__name__, config)
    from ..hooks.initialization import reset_global_html
    reset_global_html()


def run_trade_window(*args,**kwargs):
    global is_tarad_window_run

    if is_tarad_window_run:
        return

    toggleaction = QAction("Open trade when Anki starts up", mw)
    toggleaction.setCheckable(True)
    toggleaction.triggered.connect(toggle_checkbox_state)


    # toggleaction_b = QAction("Show Pokemon in the overview", mw)

    toggleaction_b = QAction("Show Pokemon in Home and overview", mw)
    toggleaction_b.setCheckable(True)
    toggleaction_b.triggered.connect(toggle_checkbox_pokemon_overview)


    toggleaction_c = QAction("Show Pokemon in Reviewer", mw)
    toggleaction_c.setCheckable(True)
    toggleaction_c.triggered.connect(toggle_checkbox_pokemon_reviewer)

    toggleaction_e = QAction("Hide banner and options", mw)
    toggleaction_e.setCheckable(True)
    toggleaction_e.triggered.connect(toggle_hide_banner_and_options)

    def open_pokemanki_trade():
        config = mw.addonManager.getConfig(__name__)

        mw.pokemenu.addAction(toggleaction)
        toggleaction.setChecked(config.get("auto_open_trade",False))

        mw.pokemenu.addAction(toggleaction_b)
        # toggleaction_b.setChecked(config.get("Show Pokemon in the overview",True))
        toggleaction_b.setChecked(config.get("show_pokemon_in_home_and_overview",True))

        mw.pokemenu.addAction(toggleaction_c)
        toggleaction_c.setChecked(config.get("show_pokemon_in_reviewer",True))

        mw.pokemenu.addAction(toggleaction_e)
        toggleaction_e.setChecked(config.get("hide_banner_and_options", False))

        if config["auto_open_trade"]:
            actions = mw.pokemenu.actions()
            for action in actions:
                if action.text() == "&Trade":
                    action.trigger()
                    break
    QTimer.singleShot(1000, open_pokemanki_trade)

    is_tarad_window_run = True

