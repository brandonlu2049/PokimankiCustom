# -*- coding: utf-8 -*-

# Pokémanki
# Copyright (C) 2022 Exkywor and zjosua

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
import shutil
import random

from typing import List, Tuple, Union

from aqt import mw

from .compute import MultiPokemon, TagPokemon, ProfilePokemon
from .pokemon_helpers import RARITY_COLOR_MAP
from .config import get_local_conf
from .utils import *
from aqt.utils import tooltip

from .custom_py.set_js_message import *
from .custom_py.count_time import shigeTaskTimer


def pokemon_display(assignment_mode: str, wholecollection: bool = True) -> str:
    """
    Control the generation of the html code to display.

    :param bool istagmon: True to switch to use tag's display, False for deck.
    :param bool wholecollection: True if multiple Pokémon, false if single.
    :return: The html text to display.
    :rtype: str
    """

    # Get list of Pokémon from tags or decks.
    #   For decks, if wholeCollection, get all assigned Pokémon and assign to Pokémon,
    #   else, show Pokémon for either single deck or all subdecks and store in Pokémon
    if assignment_mode == "tags":
        pokemon = TagPokemon()
    elif assignment_mode == "decks":
        pokemon = MultiPokemon(wholecollection)
    else:
        pokemon = ProfilePokemon()

    if pokemon is not None:
        pokemon = pokemon[:999]

    result = _show(pokemon, assignment_mode)
    return result

def _show(
    data: Union[List[dict], None],
    assignment_mode: str,
) -> str:
    """
    Generate the html to inject into the new stats window.
    :param List|None data: Pokémon information.
    :param str assignment_mode: The mode of assignment.
    :return: The html code to display.
    :rtype: str
    """

    if not data:
        return ""

    # # Pokemanki container header
    # txt = (
    #     '<h1 style="text-align: center; font-weight: 700; margin-top: 40px;">Pokémon</h1>'
    #     '<div style="text-align: center;">Your Pokémon</div>'
    # )
    addon_package = mw.addonManager.addonFromModule(__name__)
    mediafolder = f"/_addons/{addon_package}/media"
    # print(">87")
    # # Pokemanki container header
    # txt = (
    #     f'<h1 style="text-align: center; margin-top: 10px;"><img src="{mediafolder}/pokemanki.webp" style="height: 100px;"></h1>'
    #     '<div style="text-align: center;">Your Pokémon</div>'
    # )

    # Pokemanki container header


    # f = get_synced_conf()["decks_or_tags"]
    # buttons_html = ''
    # if f != "tags":
    #     buttons_html += f'<button style="font-size: 12px; display: block; width: 80px;" onclick="pycmd(\'shige_pokemanki_button_1\')">Trade</button>'
    # buttons_html += f'<button style="font-size: 12px; display: block; width: 80px;" onclick="pycmd(\'shige_pokemanki_button_2\')">Option</button>'
    # buttons_html += f'<button style="font-size: 12px; display: block; width: 80px;" onclick="pycmd(\'shige_pokemanki_button_3\')">PokeType</button>'
    # buttons_html += f'<button style="font-size: 12px; display: block; width: 80px;" onclick="pycmd(\'shige_pokemanki_button_4\')">MoreInfo</button>'

    # f = get_synced_conf()["decks_or_tags"]
    common_style = "font-size: 12px; display: block; width: 80px; border-radius: 0; font-weight: normal; padding: 0;"
    buttons_html = ''
    # if f != "tags":
    buttons_html += f'<button style="{common_style}" onclick="pycmd(\'shige_pokemanki_button_1\')">Trade</button>'
    buttons_html += f'<button style="{common_style}" onclick="pycmd(\'egg_exchange_pokemanki_button\')">Egg Exchange</button>'
    buttons_html += f'<button style="{common_style}" onclick="pycmd(\'shige_pokemanki_button_2\')">Options</button>'
    buttons_html += f'<button style="{common_style}" onclick="pycmd(\'shige_pokemanki_button_3\')">PokeType</button>'
    buttons_html += f'<button style="{common_style}" onclick="pycmd(\'shige_pokemanki_button_4\')">More Info</button>'

    pokemanki_banner = "pokemanki_02.jpg"
    # pokemanki_banner = "pokemanki.webp"
    
    pokemanki_title = f'<img src="{mediafolder}/{pokemanki_banner}" style="height: 100px; border-radius: 10px;">'

    txt = (
        f'<div style="display: flex; justify-content: center; align-items: center;">'
        f'{pokemanki_title}'
        f'<div style="margin-left: 10px;">'
        f'{buttons_html}'
        f'</div>'
        f'</div>'
        '<div style="text-align: center;">Choose a Pokémon to bring with you!</div>'
    )

    config = mw.addonManager.getConfig(__name__)
    if config.get("hide_banner_and_options", False):
        txt = (
            f'<div style="text-align: center;">'
            f'<a href="{ANKI_WEB_URL}" style="color: inherit; text-decoration: none;">Choose a Pokémon to bring with you!</a></div>')


    # If single Pokémon, show centered card
    display_deck_or_tag_name = assignment_mode != "profile"
    if type(data) == dict:
        txt += '<div class="pk-st-single">'
        txt += _card_html(data, False, display_deck_or_tag_name)
    # If multiple Pokémon, show flex row of cards
    elif type(data) == list:
        if len(data) == 1:
            txt += '<div class="pk-st-single">'
            multi = False
        else:
            conf = get_local_conf()
            card_flow = conf.get("align_cards", "wrap")
            if card_flow == "wrap":
                txt += '<div class="pk-st-container">'
            elif card_flow == "hscroll":
                txt += '<div class="pk-st-container" style="flex-wrap: nowrap; \
                        justify-content: flex-start;">'
            elif card_flow == "scrollbox":
                max_height_px = conf.get("max_height_px", "500")
                txt +=  f'<div class="pk-st-container" style="max-height: {max_height_px}px;'\
                        'border: 1px solid rgb(150, 150, 150); border-radius: 10px;">'
            else:
                txt += '<div class="pk-st-container">'

            multi = True

        # print(">173")

        sortedData = sorted(data, key=lambda k: k["level"], reverse=True)
        shigeTaskTimer.start("sortedData")
        for pokemon in sortedData:
            txt += _card_html(
                pokemon,
                multi,
                display_deck_or_tag_name
            )
        shigeTaskTimer.end("sortedData")

    # Close cards container
    txt += "</div>"

    # Pokémon total
    txt += f'<h4 style="text-align: center; margin-top: 5px;"><b>Total:</b> {len(data)} Pokémon</h4>'
    # print(">191")
    # Return txt
    return txt


def _card_html(
    pokemon: dict,
    multi: bool = False,
    display_deck_or_tag_name: bool = True,
) -> str:
    """
    Generate the html text for a Pokémon card.

    :param dict pokemon: The pokemon data.
    :param bool multi: True if multiple Pokémon are being rendered.
    :param bool display_deck_or_tag_name: True if the deck or tag name should be displayed.
    :return: The card html.
    :rtype: str
    """

    print(f"pokemon: {pokemon}")
    # Get pokemon data
    name = pokemon["name"]
    source = pokemon["deck"]
    level = pokemon["level"]
    nickname = pokemon["nickname"]
    id = pokemon["id"]
    current_pokemon_id = get_synced_conf()["current_pokemon_id"]

    # Start card
    current_class = " pk-st-current" if current_pokemon_id == id else ""
    card = f'<div class="pk-st-card{" pk-st-shrink" if multi else ""}{current_class}" onclick="pycmd(\'select_pokemon:{id}\')" style="cursor: pointer;">'

    #############
    # Head info
    #############
    card += (
        '<div class="pk-st-card-info" style="margin-bottom: auto;">'
        '<div class="pk-st-card-top">'
    )

    # split_index = -3  # ここに数値を設定します
    conf = get_local_conf()
    value = conf.get("Number of deck name splits", 3)
    if isinstance(value, int):
        split_index = -value
    else:
        split_index = 3
    font_size = "small"
    pokemon_name_style = '"cursor: pointer; text-decoration: none;" onmouseover="this.style.textDecoration=\'underline\'" onmouseout="this.style.textDecoration=\'none\'"'
    
    search_pokemon_name = re.sub(r"'", '', name)
    deck_or_tag_name = _get_source_name(source)
    
    card += (
        f'<div class="pk-st-card-name">'
        f'<span><b><span style={pokemon_name_style} onclick="pycmd(\'shige_pokemanki_button_5:{search_pokemon_name}\')">{nickname if nickname else name}</span></b></span>'
        # f'<span><b><span style="cursor: pointer;" onclick="pycmd(\'shige_pokemanki_button_5:{name}\')">{nickname if nickname != "" else name}</span></b></span>'
        # f'<span><b>{nickname if nickname != "" else name}</b></span>'
    )

    if name == "Egg":
        rarity = pokemon["rarity"]
        rarity_string = "Rarity: " + rarity
        card += f'<span style="color:{RARITY_COLOR_MAP[rarity]};margin-top: 3px;">{rarity_string}</span>'


    if display_deck_or_tag_name:
        # Level
        card += (
            f"<span style='font-size: {font_size};'><i>{'<br>'.join(deck_or_tag_name.split('::')[split_index:])}</i></span>"
            "</div>"
            '<div class="pk-st-card-lvl">'
            '<span style="text-align: right;">Lvl</span>'
            '<span style="text-align: right;">'
            f'<b>{int(level-50) if _in_list("prestige", source) else int(level)}</b>'
            "</span>"
            "</div>"
            "</div>"
        )
    else:
        card += (
            "</div>" 
            '<div class="pk-st-card-lvl" style="margin-left: 0; align-self: center; text-align: center;">'
            '<span>Lvl ' 
            f'{int(level-50) if _in_list("prestige", source) else int(level)}</span>'
            "</div>"
            "</div>"
        )

    # Divider and end of top info
    card += '<div class="pk-st-divider" style="margin-top: 10px;"></div>' "</div>"

    #############
    # Image
    #############

    card += """
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    </style>
    """

    config = mw.addonManager.getConfig(__name__)
    
    pokemon_sound_name = re.sub(r"'", '_', name)  # for Farfetchd
    
    if config[POKE_TYPE]:
        card += f'<img style="cursor: pointer;" src="{pkmnimgfolder}/{_image_name(name, source)}.webp" class="pk-st-card-img" onclick="Pokemanki.bounce(this); pycmd(\'shige_pokemon_sound:{pokemon_sound_name}\');"/>'
    else:
        card += f'<img style="cursor: pointer;" src="{pkmnimgfolder_B}/{_image_name(name, source)}.webp" class="pk-st-card-img" onclick="Pokemanki.bounce(this); pycmd(\'shige_pokemon_sound:{pokemon_sound_name}\');"/>'



    #############
    # Bottom info
    #############
    card += (
        '<div class="pk-st-card-info" style="margin-top: auto;">'
        '<div class="pk-st-divider" style="margin-bottom: 10px;"></div>'
    )
    # Held/SP
    held = _held_html(source)
    if held != "":
        card += '<div class="pk-st-card-sp">' "<span><b>SP: </b></span>"
        card += held
        card += "</div>"
    # Progress bar
    if name == "Egg":
        card += f'<span class="pk-st-card-xp">{_egg_hatch_text(level)}</span>'
    else:
        card += f'<img src="/_addons/{addon_package}/progress_bars/{_calculate_xp_progress(level)}.webp" class="pk-st-card-xp"/>'
    card += "</div>"

    # End card
    card += "</div>"

    # TODO: Add # of Pokémon
    # Make bottom line using function from stats.py and assign to text_lines
    # line( text_lines, "<b>Total</b>", "</b>%s Pokémon<b>" % _num_pokemon)

    return card


def _get_source_name(item: Union[int, str]) -> str:
    """
    Get the name of the tag or deck based on the input item.

    :param int item: Element to find the source of
    :return: The name of the deck
    """

    if not item:
        return ""

    if isinstance(item, int):
        return mw.col.decks.name(item)
    else:
        return item


def _in_list(listname: str, item: str) -> bool:
    """
    Check if an item is in a list.

    :param str listname: Name of the list to check in.
    :param str item: Item to find in the list
    :return: True if the list exists and the item is in it, otherwise false.
    :rtype: bool
    """

    if listname not in ["prestige", "everstone", "megastone", "alolan"]:
        return False

    return item in get_synced_conf()[f"{listname}list"]


def _image_name(name: str, source: Union[int, str]) -> str:
    """
    Get the image name based on the Pokémon's name and any special attributes.

    :param str name: Pokémon's name.
    :param int|str source: Id of the deck or tag name the Pokémon belongs to.
    :return: The image name to be used to retrieve it.
    :rtype: str
    """

    pkmnimgfolder = addon_dir / "pokemon_images"

    fullname = name
    if _in_list("everstone", source):
        # FIX: name is never declared!u
        if name == "Pikachu":
            # fullname += "_Ash" + str(random.randint(1, 5))
            if random.randint(1, 5) != 1:  # 4 in 5 chance
                fullname += "_Ash" + str(random.randint(1, 4)) # added
    if _in_list("megastone", source):
        if any([name + "_Mega" in imgname for imgname in os.listdir(pkmnimgfolder)]):
            fullname += "_Mega"
            if name == "Charizard" or name == "Mewtwo":
                fullname += get_local_conf()["X_or_Y_mega_evolutions"]
    if _in_list("alolan", source):
        if any([name + "_Alolan" in imgname for imgname in os.listdir(pkmnimgfolder)]):
            fullname += "_Alolan"

    return fullname


def _egg_hatch_text(level: float) -> str:
    """
    Get the egg's hatch text.

    :param float level: The level of the egg.
    :return: The hatch text.
    :rtype: str
    """
    if level < 2:
        return "Needs a lot more time to hatch"
    elif level < 3:
        return "Will take some time to hatch"
    elif level < 4:
        return "Moves around inside sometimes"
    else:
        return "Making sounds inside"


def _calculate_xp_progress(level: float) -> int:
    """
    Calculate the xp progress for the xp bar based on the given level.

    :param float level: The level to base the calculations on.
    :return: The progress in the xp bar.
    :rtype: int
    """
    return int(float(20 * (float(level) - int(float(level)))))


def _held_html(source: Union[int, str]) -> str:
    """
    Generate the held html code for the given Pokémon.

    :param int|str source: Id of the deck or tag name the Pokémon belongs to.
    :return: The concatenation of all held items' html. Empty if it has no items.
    :rtype: str
    """

    held = ""
    everstone_html = f'<img src="{pkmnimgfolder}/item_Everstone.webp" height="20px"/>'
    megastone_html = f'<img src="{pkmnimgfolder}/item_Mega_Stone.webp" height="25px"/>'
    alolan_html = f'<img src="{pkmnimgfolder}/item_Alolan_Passport.webp" height="25px"/>'

    if _in_list("prestige", source):
        held += "<span>Prestiged </span>"
    if _in_list("everstone", source):
        held += everstone_html
    if _in_list("alolan", source):
        held += alolan_html
    if _in_list("megastone", source):
        held += megastone_html

    return held
