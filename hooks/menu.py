# -*- coding: utf-8 -*-

# Pokémanki - Menu Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from aqt import mw
from aqt.qt import QAction, QMenu, qconnect

from ..config import get_synced_conf
from ..pokemon import *
from ..tags import run_tags_window
from ..trades import Trades
from ..egg_exchange import EggExchange
from ..custom_py.more_info import show_more_info

# Global variables
tradeclass = object()
eggexchangeclass = object()
tags = object()

def reset_menu_globals():
    """Reset global menu variables."""
    global tradeclass, eggexchangeclass, tags
    tradeclass = object()
    eggexchangeclass = object()
    tags = object()

def build_menu() -> None:
    """Build the Pokemanki menu."""
    global tradeclass, eggexchangeclass

    # Make actions for settings and reset
    nicknameaction = QAction("&Nicknames", mw)
    resetaction = QAction("&Reset", mw)
    tradeaction = QAction("&Trade", mw)
    eggexchangeaction = QAction("&Egg Exchange", mw)
    toggleaction = QAction("&Decks vs. Tags", mw)
    tagsaction = QAction("&Tags", mw)
    prestigeaction = QAction("&Prestige Pokémon", mw)
    unprestigeaction = QAction("&Unprestige Pokémon", mw)

    everstoneaction = QAction("&Give Everstone", mw)
    uneverstoneaction = QAction("&Take Everstone", mw)

    megastoneaction = QAction("&Give Mega Stone", mw)
    unmegastoneaction = QAction("&Take Mega Stone", mw)
    alolanaction = QAction("&Give Alolan Passport", mw)
    unalolanaction = QAction("&Take Alolan Passport", mw)
    
    bottomaction = QAction("Move Pokémon to &Bottom", mw)
    topaction = QAction("Move Pokémon to &Top", mw)
    
    aAbout = QAction("About", mw)

    # Connect actions to functions
    tradeclass = Trades()
    eggexchangeclass = EggExchange()
    qconnect(nicknameaction.triggered, nickname)
    qconnect(resetaction.triggered, reset_pokemanki)
    qconnect(tradeaction.triggered, tradeclass.open)
    qconnect(eggexchangeaction.triggered, eggexchangeclass.open)
    qconnect(toggleaction.triggered, Toggle)
    qconnect(tagsaction.triggered, run_tags_window)
    qconnect(prestigeaction.triggered, PrestigePokemon)
    qconnect(unprestigeaction.triggered, UnprestigePokemon)
    qconnect(everstoneaction.triggered, giveEverstone)
    qconnect(uneverstoneaction.triggered, takeEverstone)
    qconnect(megastoneaction.triggered, giveMegastone)
    qconnect(unmegastoneaction.triggered, takeMegastone)
    qconnect(alolanaction.triggered, giveAlolanPassport)
    qconnect(unalolanaction.triggered, takeAlolanPassport)
    qconnect(bottomaction.triggered, MovetoBottom)
    qconnect(topaction.triggered, MovetoTop)
    qconnect(aAbout.triggered, show_more_info)

    mw.pokemenu.clear()

    mw.form.menuTools.addMenu(mw.pokemenu)
    mw.pokemenu.addAction(toggleaction)
    mw.pokemenu.addAction(nicknameaction)
    mw.prestigemenu = QMenu("&Prestige Menu", mw)
    mw.pokemenu.addMenu(mw.prestigemenu)
    mw.prestigemenu.addAction(prestigeaction)
    mw.prestigemenu.addAction(unprestigeaction)

    f = get_synced_conf()["decks_or_tags"]
    if f == "tags":
        mw.pokemenu.addAction(tagsaction)
    else:  # Not yet implemented for tagmon
        mw.everstonemenu = QMenu("&Everstone", mw)
        mw.pokemenu.addMenu(mw.everstonemenu)
        mw.everstonemenu.addAction(everstoneaction)
        mw.everstonemenu.addAction(uneverstoneaction)
        mw.megastonemenu = QMenu("&Mega Stone", mw)
        mw.pokemenu.addMenu(mw.megastonemenu)
        mw.megastonemenu.addAction(megastoneaction)
        mw.megastonemenu.addAction(unmegastoneaction)
        mw.alolanmenu = QMenu("&Alolan Passport", mw)
        mw.pokemenu.addMenu(mw.alolanmenu)
        mw.alolanmenu.addAction(alolanaction)
        mw.alolanmenu.addAction(unalolanaction)

    # Add trade and egg exchange actions
    mw.pokemenu.addAction(tradeaction)
    mw.pokemenu.addAction(eggexchangeaction)
    mw.pokemenu.addAction(resetaction)
    mw.pokemenu.addAction(aAbout)

    # Debug menu items
    config = mw.addonManager.getConfig(__name__)
    if config.get("is_enable_debug_mode", False):
        from ..show_test_tags import test_tag_matching
        testaction = QAction("Test Tag Matching", mw)
        qconnect(testaction.triggered, test_tag_matching)
        mw.pokemenu.addAction(testaction)
