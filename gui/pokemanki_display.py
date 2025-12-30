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
import random
import uuid

from typing import List, Union

from aqt import mw

from ..helpers.pokemon_helpers import ProfilePokemon, RARITY_COLOR_MAP, HATCH_EGG_LEVEL, set_pokemon_by_id
from ..helpers.config import get_local_conf
from ..utils import *

from ..custom_py.set_js_message import *
from ..custom_py.count_time import shigeTaskTimer


def pokemon_display(wholecollection: bool = True) -> str:
    """
    Control the generation of the html code to display.

    :param bool wholecollection: True if multiple Pokémon, false if single.
    :return: The html text to display.
    :rtype: str
    """

    pokemon = ProfilePokemon()

    pokemon.append({
        "id": str(uuid.uuid4()),
        "name": "Charizard",
        "level": 50,
        "rarity": "A",
        "nickname": None,
        "items": {
            "everstone": False,
            "megastone": True,
        },
    })
    pokemon.append({
        "id": str(uuid.uuid4()),
        "name": "Mewtwo",
        "level": 50,
        "rarity": "S",
        "nickname": None,
        "items": {
            "everstone": False,
            "megastone": True,
        },
    })
    pokemon.append({
        "id": str(uuid.uuid4()),
        "name": "Diglett",
        "level": 50,
        "rarity": "A",
        "nickname": None,
        "items": {
            "everstone": False,
            "megastone": False,
            "alolan": True,
        },
    })

    result = _show(pokemon)
    return result

def _show(
    data: Union[List[dict], None],
) -> str:
    """
    Generate the html to inject into the new stats window.
    :param List|None data: Pokémon information.
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
        '<div style="text-align: center; margin-top: 10px;">Choose a Pokémon to bring with you!</div>'
    )

    config = mw.addonManager.getConfig(__name__)
    if config.get("hide_banner_and_options", False):
        txt = (
            f'<div style="text-align: center;">'
            f'<a href="{ANKI_WEB_URL}" style="color: inherit; text-decoration: none;">Choose a Pokémon to bring with you!</a></div>')


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

    sortedData = sorted(data, key=lambda k: k["level"], reverse=True)
    shigeTaskTimer.start("sortedData")
    for pokemon in sortedData:
        txt += _card_html(
            pokemon,
            multi,
        )
    shigeTaskTimer.end("sortedData")

    # Close cards container
    txt += "</div>"

    # Pokémon total
    txt += f'<h4 style="text-align: center; margin-top: 5px;"><b>Total:</b> {len(data)} Pokémon</h4>'
    return txt


def _card_html(
    pokemon: dict,
    multi: bool = False,
) -> str:
    """
    Generate the html text for a Pokémon card.

    :param dict pokemon: The pokemon data.
    :param bool multi: True if multiple Pokémon are being rendered.
    :return: The card html.
    :rtype: str
    """

    # Get pokemon data
    name = pokemon["name"]
    if pokemon["items"]["megastone"]:
        name = "Mega " + name
        if pokemon["name"] == "Charizard" or pokemon["name"] == "Mewtwo":
            name += " " + get_local_conf()["X_or_Y_mega_evolutions"]
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

    pokemon_name_style = '"cursor: pointer; text-decoration: none;" onmouseover="this.style.textDecoration=\'underline\'" onmouseout="this.style.textDecoration=\'none\'"'
    
    search_pokemon_name = re.sub(r"'", '', name)
    
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

    card += (
        "</div>" 
        '<div class="pk-st-card-lvl" style="margin-left: 0; align-self: center; text-align: center;">'
        '<span>Lvl ' 
        f'{int(level)}</span>'
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
        card += f'<img style="cursor: pointer;" src="{pkmnimgfolder}/{_image_name(pokemon)}.webp" class="pk-st-card-img" onclick="Pokemanki.bounce(this); pycmd(\'shige_pokemon_sound:{pokemon_sound_name}\');"/>'
    else:
        card += f'<img style="cursor: pointer;" src="{pkmnimgfolder_B}/{_image_name(pokemon)}.webp" class="pk-st-card-img" onclick="Pokemanki.bounce(this); pycmd(\'shige_pokemon_sound:{pokemon_sound_name}\');"/>'



    #############
    # Bottom info
    #############
    card += (
        '<div class="pk-st-card-info" style="margin-top: auto;">'
        '<div class="pk-st-divider" style="margin-bottom: 10px;"></div>'
    )
    # Held/SP
    held = _held_html(pokemon)
    if held != "":
        card += '<div class="pk-st-card-sp">' "<span><b>SP: </b></span>"
        card += held
        card += "</div>"
    # Progress bar
    if name == "Egg":
        card += f'<span class="pk-st-card-xp">{_egg_hatch_text(level, pokemon.get("rarity", "F"))}</span>'
    else:
        card += f'<img src="/_addons/{addon_package}/progress_bars/{_calculate_xp_progress(level)}.webp" class="pk-st-card-xp"/>'
    
    # Customize button
    card += f'<button class="pk-st-customize-btn" onclick="event.stopPropagation(); pycmd(\'customize_pokemon:{id}\')" style="margin-top: 8px; padding: 4px 12px; font-size: 11px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; background: linear-gradient(to bottom, #f8f8f8, #e8e8e8); color: #333;">Customize</button>'
    
    card += "</div>"

    # End card
    card += "</div>"

    # TODO: Add # of Pokémon
    # Make bottom line using function from stats.py and assign to text_lines
    # line( text_lines, "<b>Total</b>", "</b>%s Pokémon<b>" % _num_pokemon)

    return card

def _image_name(pokemon) -> str:
    """
    Get the image name based on the Pokémon's name and any special attributes.

    :param str name: Pokémon's name.
    :return: The image name to be used to retrieve it.
    :rtype: str
    """

    pkmnimgfolder = addon_dir / "pokemon_images"

    fullname = pokemon["name"]
    if pokemon["items"]["everstone"]:
        if pokemon["name"] == "Pikachu":
            if random.randint(1, 5) != 1:  # 4 in 5 chance
                fullname += "_Ash" + str(random.randint(1, 4)) # added
    if pokemon["items"]["megastone"]:
        if any([pokemon["name"] + "_Mega" in imgname for imgname in os.listdir(pkmnimgfolder)]):
            fullname += "_Mega"
            if pokemon["name"] == "Charizard" or pokemon["name"] == "Mewtwo":
                fullname += get_local_conf()["X_or_Y_mega_evolutions"]

    return fullname


def _egg_hatch_text(level: float, rarity: str) -> str:
    """
    Get the egg's hatch text.

    :param float level: The level of the egg.
    :return: The hatch text.
    :rtype: str
    """
    hatch_level = HATCH_EGG_LEVEL[rarity]
    hatch_interval = hatch_level / 4
    if level < hatch_interval:
        return "Needs a lot more time to hatch"
    elif level < 2 * hatch_interval:
        return "Will take some time to hatch"
    elif level < 3 * hatch_interval:
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


def _held_html(pokemon) -> str:
    """
    Generate the held html code for the given Pokémon.

    :param int|str source: Id of the deck or tag name the Pokémon belongs to.
    :return: The concatenation of all held items' html. Empty if it has no items.
    :rtype: str
    """

    held = ""
    everstone_html = f'<img src="{pkmnimgfolder}/item_Everstone.webp" height="20px"/>'
    megastone_html = f'<img src="{pkmnimgfolder}/item_Mega_Stone.webp" height="25px"/>'

    if pokemon["items"]["everstone"]:
        held += everstone_html
    if pokemon["items"]["megastone"]:
        held += megastone_html

    return held
