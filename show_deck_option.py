from aqt import QMenu, QSizePolicy, mw, QPushButton
from aqt.utils import openLink


def pokemon_icon_click():
    config = mw.addonManager.getConfig(__name__)
    show_pokemon_in_reviewer = config.get("show_pokemon_in_reviewer", True)

    if show_pokemon_in_reviewer:
        button_text = "Toggle OFF"
        info_text = "Now enabled, do you want to disable it?"
    else:
        button_text = "Toggle ON"
        info_text = "Now disabled, do you want to enable it?"


    def toggle_checkbox_pokemon_reviewer():
        config = mw.addonManager.getConfig(__name__)
        checked = config["show_pokemon_in_reviewer"] = not config.get("show_pokemon_in_reviewer", True)
        mw.addonManager.writeConfig(__name__, config)
        from .pokemon_helpers import toggle_on_or_off_top_toolbar
        toggle_on_or_off_top_toolbar()

        if hasattr(mw, 'pokemenu') and isinstance(mw.pokemenu, QMenu):
            for action in mw.pokemenu.actions():
                if action.text() == "Show Pokemon in Reviewer":
                    if action and hasattr(action, 'setChecked'):
                        action.setChecked(checked)

    customBtns = []
    togle_off_button = QPushButton(button_text)
    togle_off_button.clicked.connect(toggle_checkbox_pokemon_reviewer)
    customBtns.append(togle_off_button)

    from .custom_py.path_manager import InfoDialog
    InfoDialog(
        f"Show pokemon in reviewer: {info_text}",
        type = "shige",
        parent=mw,
        title="Pokemanki Custom",
        customBtns = customBtns)
