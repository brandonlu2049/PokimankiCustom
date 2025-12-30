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
from ..utils import addon_dir
from ..helpers.pokemon_helpers import get_pokemon_icon_and_level


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

    try:
        config = mw.addonManager.getConfig(__name__)
        if not config.get("show_pokemon_in_home_and_overview", True):
            return
    except:
        return

    js = (addon_dir / "web.js").read_text(encoding="utf-8")
    css = (addon_dir / "pokemanki_css" / "view_stats.css").read_text(encoding="utf-8")

    config["show_pokemon_in_home_and_overview"] = False # Avoid Freeze
    mw.addonManager.writeConfig(__name__, config)

    html_home = pokemon_display(True).replace("`", "'") # wholeCollection

    print("Making new Pokemon rendering")

    config["show_pokemon_in_home_and_overview"] = True # Avoid Freeze
    mw.addonManager.writeConfig(__name__, config)

    config = mw.addonManager.getConfig(__name__)

    if config.get("show_pokemon_in_reviewer",True):
        get_pokemon_icon_and_level(None)

    content.stats += f"{html_home}"
    content.stats += f"<script>{js}</script>"
    content.stats += f"<style>{css}</style>"
