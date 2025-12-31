# -*- coding: utf-8 -*-

# Pokémanki - Deck Browser Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from bs4 import BeautifulSoup
from pathlib import Path

from aqt import mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent

from ..helpers.config import get_synced_conf
from ..gui.pokemanki_display import pokemon_display
from ..utils import addon_dir, addon_package
from ..helpers.pokemon_helpers import get_pokemon_icon_and_level

# In-memory flag to prevent re-entrant calls during rendering
_is_rendering = False


def replace_gears(deck_browser: DeckBrowser, content: DeckBrowserContent) -> None:
    """Replace gear icon with Pokemon-themed gear."""
    soup = BeautifulSoup(content.tree, "html.parser")
    for tr in soup.select("tr.deck"):
        if len(tr.select("img.gears")) > 0:
            tr.select("img.gears")[0]["class"] = "gears pokemon"
    style = soup.new_tag("style")
    style.string = ".gears.pokemon{filter:none;opacity:1}"
    soup.append(style)
    content.tree = soup

def deck_browser_open(deck_browser: "DeckBrowser", content: "DeckBrowserContent") -> None:
    """Handle deck browser opening and add Pokemon display."""
    global _is_rendering

    # Prevent re-entrant calls during rendering
    if _is_rendering:
        return

    try:
        config = mw.addonManager.getConfig(__name__)
        if not config.get("show_pokemon_in_home_and_overview", True):
            return
    except:
        return

    js = (addon_dir / "web.js").read_text(encoding="utf-8").replace("{{ADDON_PACKAGE}}", addon_package)
    css = (addon_dir / "pokemanki_css" / "view_stats.css").read_text(encoding="utf-8")

    _is_rendering = True  # Use in-memory flag instead of config
    try:
        html_home = pokemon_display(True).replace("`", "'") # wholeCollection
        print("Making new Pokemon rendering")
    finally:
        _is_rendering = False  # Always reset, even if an exception occurs

    config = mw.addonManager.getConfig(__name__)

    if config.get("show_pokemon_in_reviewer",True):
        get_pokemon_icon_and_level(None)

    content.stats += f"{html_home}"
    content.stats += f"<script>{js}</script>"
    content.stats += f"<style>{css}</style>"
