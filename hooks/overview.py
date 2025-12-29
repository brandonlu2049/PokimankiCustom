# -*- coding: utf-8 -*-

# Pokémanki - Overview Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from aqt import mw
from aqt.overview import Overview, OverviewContent

from ..config import get_synced_conf
from ..display import pokemon_display
from ..utils import addon_dir

# Global variables for caching
overview_deck_html_map = {}

def reset_overview_globals():
    """Reset global variables for overview."""
    global overview_deck_html_map
    overview_deck_html_map = {}

def overview_open(overview: "Overview", content: "OverviewContent") -> None:
    """Handle overview opening and add Pokemon display."""
    global overview_deck_html_map

    config = mw.addonManager.getConfig(__name__)
    if not config.get("Show Pokemon in Home and overview", True):
        return

    js = (addon_dir / "web.js").read_text(encoding="utf-8")
    css = (addon_dir / "pokemanki_css" / "view_stats.css").read_text(encoding="utf-8")

    f = get_synced_conf()["decks_or_tags"]

    curr_deck = mw.col.decks.active()[0]
    print(curr_deck)

    if curr_deck in overview_deck_html_map:
        html = overview_deck_html_map[curr_deck]
        print("use saved html")
    else:
        config["Show Pokemon in Home and overview"] = False # Avoid Freeze
        mw.addonManager.writeConfig(__name__, config)

        html = pokemon_display(f, False).replace("`", "'") # currentDeck
        overview_deck_html_map[curr_deck] = html
        print("make new html")

        config["Show Pokemon in Home and overview"] = True # Avoid Freeze
        mw.addonManager.writeConfig(__name__, config)

    content.table += f"{html}"
    content.table += f"<script>{js}</script>"
    content.table += f"<style>{css}</style>"
