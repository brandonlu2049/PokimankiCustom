# -*- coding: utf-8 -*-

# Pokémanki - Initialization Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import List

import aqt
from aqt import mw, gui_hooks
from aqt.qt import QMenu
from aqt.utils import askUser

from ..config import init_config
from .menu import build_menu

def remove_config(dialog: aqt.addons.AddonsDialog, addons: List[str]) -> None:
    """Handle addon removal and optionally remove config."""
    for name in ["1677779223", "pokemanki"]:
        if name in addons:
            delete_pokemanki_conf = askUser(
                """\
The Pokémanki add-on will be deleted.
Do you want to remove its config too?
This will delete your Pokémon.
""",
                parent=dialog,
                title="Remove Pokémanki config?",
            )
            if delete_pokemanki_conf:
                mw.col.remove_config("pokemanki")

def pokemanki_init() -> None:
    """Initialize Pokemanki addon."""
    init_config()
    mw.pokemenu = QMenu("&Pokémanki", mw)
    build_menu()

def delayed_init() -> None:
    """Delayed initialization with timers."""
    mw.progress.single_shot(50, pokemanki_init)
    from ..custom_py.set_js_message import run_trade_window
    mw.progress.single_shot(500, run_trade_window)

def reset_global_html(*args, **kwargs):
    """Reset global HTML caches."""
    from .overview import reset_overview_globals
    
    reset_overview_globals()
