# -*- coding: utf-8 -*-

# Pokémanki - Menu Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from aqt import mw
from aqt.qt import QAction, QMenu, qconnect

from ..helpers.config import get_synced_conf
from ..helpers.pokemon_helpers import reset_pokemanki
from ..features.trades import Trades
from ..features.egg_exchange import EggExchange
from ..features.shop import Shop
from ..custom_py.more_info import show_more_info

# Global variables
tradeclass = object()
eggexchangeclass = object()
shopclass = object()
tags = object()

def reset_menu_globals():
    """Reset global menu variables."""
    global tradeclass, eggexchangeclass, shopclass, tags
    tradeclass = object()
    eggexchangeclass = object()
    shopclass = object()
    tags = object()

def build_menu() -> None:
    """Build the Pokemanki menu."""
    global tradeclass, eggexchangeclass, shopclass

    # Make actions for settings and reset
    nicknameaction = QAction("&Nicknames", mw)
    resetaction = QAction("&Reset", mw)
    tradeaction = QAction("&Trade", mw)
    eggexchangeaction = QAction("&Egg Exchange", mw)
    shopaction = QAction("&Shop", mw)
    
    aAbout = QAction("About", mw)

    # Connect actions to functions
    tradeclass = Trades()
    eggexchangeclass = EggExchange()
    shopclass = Shop()
    qconnect(resetaction.triggered, reset_pokemanki)
    qconnect(tradeaction.triggered, tradeclass.open)
    qconnect(eggexchangeaction.triggered, eggexchangeclass.open)
    qconnect(shopaction.triggered, shopclass.open)
    qconnect(aAbout.triggered, show_more_info)

    mw.pokemenu.clear()

    # Add the Pokémanki menu to Tools menu
    mw.form.menuTools.addMenu(mw.pokemenu)

    # Add trade, egg exchange, and shop actions
    mw.pokemenu.addAction(tradeaction)
    mw.pokemenu.addAction(eggexchangeaction)
    mw.pokemenu.addAction(shopaction)
    mw.pokemenu.addAction(resetaction)
    mw.pokemenu.addAction(aAbout)
        
