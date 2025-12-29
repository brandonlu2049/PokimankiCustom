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

import os
from pathlib import Path
import re

from aqt import mw, gui_hooks
from anki.decks import DeckTreeNode
from aqt.overview import Overview, OverviewContent
from aqt.webview import WebContent

from ..config import get_synced_conf
from ..utils import pkmnimgfolder,pkmnimgfolder_B
from ..custom_py.set_js_message import POKE_TYPE

# not used.

def on_webview_will_set_content(web_content: WebContent, context, *args, **kwargs):
    if not isinstance(context, Overview):
        return
    config = mw.addonManager.getConfig(__name__)
    if not config.get("Show Pokemon in the overview", True):
        return

    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(
        f"/_addons/{addon_package}/custom_py/web_overview.js")


def on_overview_will_render_content(overview: Overview, content: OverviewContent, *args, **kwargs) -> None:
    config = mw.addonManager.getConfig(__name__)
    if not config.get("Show Pokemon in the overview", True):
        return

    conf = get_synced_conf()
    if not conf:
        return
    pokemons = conf["pokemon_list"]

    current_Deck_ID = None

    if mw.state in ["overview"]:
        current_Deck_ID = mw.col.decks.current()['id']

    if current_Deck_ID:
        def get_child_deck_ids(deck_node:DeckTreeNode ):
            child_ids = []
            for child in deck_node.children:
                child_ids.append(child.deck_id)
                child_ids.extend(get_child_deck_ids(child))
            return child_ids

        deck_tree = mw.col.sched.deck_due_tree(current_Deck_ID)

        child_deck_ids = get_child_deck_ids(deck_tree)
        deck_ids = child_deck_ids + [current_Deck_ID]


        card =""
        for deck_id in deck_ids:
            # ﾎﾟｹﾓﾝﾘｽﾄからﾃﾞｯｷIDが一致するﾎﾟｹﾓﾝを探す
            matching_pokemons = []
            for pokemon in pokemons:
                if pokemon["deck"] == deck_id:
                    matching_pokemons.append((pokemon["name"], pokemon["level"]))

            # ﾏｯﾁしたﾎﾟｹﾓﾝから名前とﾚﾍﾞﾙを取得する｡ﾏｯﾁするﾎﾟｹﾓﾝがなければNoneを返す
            name, level = next(iter(matching_pokemons), (None, None))

            if name:
                if level is not None and level < 5: # 追加
                    name = "Egg"

                card += """
                <style>
                @keyframes bounce {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-20px); }
                }
                </style>
                """

                config = mw.addonManager.getConfig(__name__)
                pokemon_sound_name = re.sub(r"'", '_', name) # for Farfetchd
                if config[POKE_TYPE]:
                    card += f'<img style="cursor: pointer;" src="{pkmnimgfolder}/{name}.webp" onclick="Pokemanki.bounce(this); pycmd(\'shige_pokemon_sound:{pokemon_sound_name}\');"/>'
                else:
                    card += f'<img style="cursor: pointer;" src="{pkmnimgfolder_B}/{name}.webp" onclick="Pokemanki.bounce(this); pycmd(\'shige_pokemon_sound:{pokemon_sound_name}\');"/>'

    content.table += f"<div>{card}</div>"

def set_hook_poke_overview(): # not used
    gui_hooks.overview_will_render_content.append(on_overview_will_render_content)
    gui_hooks.webview_will_set_content.append(on_webview_will_set_content)



