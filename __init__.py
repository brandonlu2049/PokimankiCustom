# -*- coding: utf-8 -*-

# Pokémanki
# Copyright (C) 2022-2023 Exkywor and zjosua
# Copyright (C) 2023-2024 Shigeyuki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from aqt import QPushButton, gui_hooks, mw
# from aqt.utils import showWarning

# from .custom_py.pokemankiConfig import set_gui_hook_rate_this
# set_gui_hook_rate_this()

from .custom_py.popup.popup_config import set_gui_hook_change_log
set_gui_hook_change_log()


opened = False

def startup():
    global opened
    
    # Import modules that depend on mw.col being available
    from .hooks_append import all_gui_hooks_append
    
    # Add images and CSS to media server (moved from main.py)
    mw.addonManager.setWebExports(
        __name__, r"(media|pokemon_images|custom_py|custom_py/Trainer_100|pokemon_images_static|progress_bars|pokemanki_css)/.*(css|webp|png|jpg|js)"
    )
    
    # Initialize hooks (moved from main.py)
    all_gui_hooks_append()
    
    if opened:
        from .custom_py.path_manager import InfoDialog

        menu = mw.form.menuTools
        customBtns = []
        for action in menu.actions():
            if action.text() == "Anki Restart":
                submenu = action.menu()
                for subaction in submenu.actions():
                    if subaction.text() == "Restart Anki now":
                        restart_button = QPushButton("Restart Anki now")
                        restart_button.clicked.connect(subaction.trigger)
                        customBtns.append(restart_button)
                        break

        warning_text = """
                Hello Pokemon Trainer!<br>
                Pokemanki does not yet support profile changes,<br>
                so please restart Anki.<br>
                """

        cancel_button = QPushButton("No")
        customBtns.append(cancel_button)
        warning_text += """
                <br>
                Using AnkiRestart to reboot the Anki now? Thank you!
                """

        InfoDialog(warning_text, title="Pokemanki Custom", type="shige",textFormat="rich",customBtns=customBtns)

    opened = True

    # from .custom_py.poke_add_overview import set_hook_poke_overview
    # set_hook_poke_overview()


gui_hooks.profile_did_open.append(startup)

# MAIN WINDOW INIT HOOK - Register toolbar hook after main window is ready
_toolbar_hook_registered = False

def register_toolbar_hook_after_main_window():
    global _toolbar_hook_registered
    if _toolbar_hook_registered:
        return
        
    try:
        from .top_toolbar_init import add_pokemon_top_toolbar
        gui_hooks.top_toolbar_did_init_links.append(add_pokemon_top_toolbar)
        _toolbar_hook_registered = True
        print("Successfully registered toolbar hook after main window init")
        
        # Also try to trigger toolbar redraw
        if hasattr(mw, 'toolbar') and mw.toolbar:
            mw.toolbar.draw()
    except Exception as e:
        print(f"Failed to register toolbar hook: {e}")

gui_hooks.main_window_did_init.append(register_toolbar_hook_after_main_window)

# ｽﾃｰﾀｽ画面にﾘｰﾛｰﾄﾞﾎﾞﾀﾝを追加 -----------------
try:
    from aqt import QDialog, QDialogButtonBox
    from aqt.stats import NewDeckStats
except: pass
def add_button_to_stats_dialog(dialog:QDialog):
    try:
        if isinstance(dialog, NewDeckStats):
            new_button = QPushButton("PokeReload")
            new_button.clicked.connect(dialog.close)
            new_button.clicked.connect(mw.onStats)
            dialog.form.buttonBox.addButton(new_button, QDialogButtonBox.ButtonRole.ActionRole)
    except:pass
try:gui_hooks.stats_dialog_will_show.append(add_button_to_stats_dialog)
except: pass
# ---------------------------------------------