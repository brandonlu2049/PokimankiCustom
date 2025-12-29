

import random
import re
import uuid
from anki.cards import Card
from aqt import mw, gui_hooks
from typing import Any, Dict

from .config import get_synced_conf, save_synced_conf
from .utils import pkmnimgfolder, pkmnimgfolder_B, addon_package
from .compute import load_pokemon_gen_all

IMAGE_HEIGHT = "3em"

ENABLE_LABEL_ID = "shige_pokemanki_gold"
DISABLE_LABEL_ID = "disable_pokemanki_gold"

LABEL_PYCMD = "shige_pokemanki_clicked"
LABEL_INDEX = 6

POKEMON_EMPTY =  f"/_addons/{addon_package}/custom_py/pokemon_empty.png"
POKEBALL_ICON =   f"/_addons/{addon_package}/custom_py/pokeball.png"

DEFAULT_POKEMON_HTML = f"""
<div style='display: flex; align-items: center;'>
    <div style='flex-shrink: 0; min-width: {IMAGE_HEIGHT}; min-height: {IMAGE_HEIGHT};'>
        <div style='flex-shrink: 0; min-width: {IMAGE_HEIGHT}; min-height: {IMAGE_HEIGHT};'>
            <img src='{POKEMON_EMPTY}' alt='empty_pokemon' style='height: {IMAGE_HEIGHT};'>
        </div>
    </div>
    <div style='margin-left: 10px; min-width: {IMAGE_HEIGHT}; min-height: {IMAGE_HEIGHT};'>
        <div style='text-align: left; color: gray;'>
            Pokemon
        </div>
        <div style='text-align: left; color: gray;'>
            Lv.
        </div>
        <span style='text-align: left; color: gray; font-size: 0.8em;'>deck or tag</span>

    </div>
</div>
""".replace("\n", "")

LEVEL_INCREMENT_AMOUNT = 0.01
HATCH_EGG_LEVEL = {"S": 15, "A": 10, "B": 9, "C": 8, "D": 7, "E": 6, "F": 5}

RARITY_COLOR_MAP = {
    "F": "#9E9E9E",  # Gray - Common
    "E": "#8BC34A",  # Green - Uncommon
    "D": "#03A9F4",  # Blue - Rare
    "C": "#9C27B0",  # Purple - Epic
    "B": "#E91E63",  # Pink - Legendary
    "A": "#F44336",  # Red - Mythic
    "S": "#FFD700",  # Gold - Ultimate
}

# Global cache for pokemon evolution mapping
_pokemon_evolution_mapping = None

# Centralized function to create a pokemon dictionary. Always use this function to create a pokemon.
# Arguments:
# - name: str - The name of the pokemon
# - level: float - The level of the pokemon
# - rarity: str - The rarity of the pokemon
# - nickname: str = None - The nickname of the pokemon
# Returns: dict - The pokemon dictionary
def create_pokemon(name: str, level: float, rarity: str, nickname: str = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "level": level,
        "rarity": rarity,
        "nickname": nickname
    }

def get_all_pokemon_tiered():
    pokemonlist = []
    tiers = []
    evolutionLevel1 = []
    evolution1 = []
    evolutionLevel2 = []
    evolution2 = []

    load_pokemon_gen_all(
        pokemonlist, tiers, evolutionLevel1, evolution1, evolutionLevel2, evolution2
    )

    tierdict = {"S": [],"A": [], "B": [], "C": [], "D": [], "E": [], "F": []}
    for i, tier in enumerate(tiers):
        tierdict[tier].append(pokemonlist[i])
    return tierdict

def generate_by_rarity(pokemonList):
    tierdict = get_all_pokemon_tiered()
    generatedPokemonList = []

    for pokemon in pokemonList:
        pokemontier = pokemon["rarity"]
        tiernumber = len(tierdict[pokemontier])
        tierlabel = tierdict[pokemontier]
        randno = random.randint(0, tiernumber - 1)
        pokemon["name"] = tierlabel[randno]
        generatedPokemonList.append(pokemon)

    return generatedPokemonList

def add_xp_to_pokemon(pokemon, xp):
    pokemon["level"] += xp
    print("adding xp to pokemon", pokemon)
    if pokemon["name"] == "Egg":
        if pokemon["level"] > HATCH_EGG_LEVEL[pokemon["rarity"]]:
            pokemon = generate_by_rarity([pokemon])[0]
    else:
        evolutions = get_pokemon_evolution_mapping()
        if pokemon["name"] in evolutions and evolutions[pokemon["name"]]["next_evolution_level"] < pokemon["level"]:
            pokemon["name"] = evolutions[pokemon["name"]]["next_evolution"]
    set_pokemon_by_id(pokemon["id"], pokemon)
    return

def get_pokemon_evolution_mapping() -> Dict[str, Dict[str, Any]]:
    """Get cached pokemon evolution mapping, creating it if necessary.
    
    Returns:
        Dict mapping pokemon names to their evolution info:
        {"pokemon_name": {"next_evolution": "evolved_name", "next_evolution_level": level}}
    """
    global _pokemon_evolution_mapping

    # Return cached version if available
    if _pokemon_evolution_mapping is not None:
        return _pokemon_evolution_mapping
    
    # Create the mapping
    try:
        from ..compute import load_pokemon_gen_all
        
        pokemonlist = []
        tiers = []
        evolutionLevel1 = []
        evolution1 = []
        evolutionLevel2 = []
        evolution2 = []
        
        load_pokemon_gen_all(
            pokemonlist, tiers, evolutionLevel1, evolution1, evolutionLevel2, evolution2
        )
        
        # Create mapping: pokemon_name -> {"next_evolution": name, "next_evolution_level": level}
        evolution_mapping = {}
        
        for i, pokemon in enumerate(pokemonlist):
            if i < len(evolutionLevel1) and i < len(evolution1):
                evolution_level_1 = evolutionLevel1[i]
                evolution_1 = evolution1[i]
                evolution_level_2 = evolutionLevel2[i]
                evolution_2 = evolution2[i]

                # Only add if there's actually an evolution
                if evolution_level_1 is not None and evolution_1 is not None:
                    evolution_mapping[pokemon] = {
                        "next_evolution": evolution_1,
                        "next_evolution_level": evolution_level_1
                    }

                if evolution_level_2 is not None and evolution_2 is not None:
                    evolution_mapping[evolution_1] = {
                        "next_evolution": evolution_2,
                        "next_evolution_level": evolution_level_2
                    }
        
        # Cache the mapping
        _pokemon_evolution_mapping = evolution_mapping
        print(f"Created and cached pokemon evolution mapping with {len(evolution_mapping)} entries")
        
        return evolution_mapping
        
    except Exception as e:
        print(f"Error creating pokemon evolution mapping: {e}")
        # Cache empty mapping as fallback
        _pokemon_evolution_mapping = {}
        return _pokemon_evolution_mapping


def clear_pokemon_evolution_cache() -> None:
    """Clear the cached pokemon evolution mapping.
    
    This can be useful if the user changes generation settings and wants
    to reload the evolution data.
    """
    global _pokemon_evolution_mapping
    _pokemon_evolution_mapping = None

# Return HTML to display pokemon icon and level on top toolbar. xp_gain is the amount of xp to add to the current pokemon level.
def get_pokemon_icon_and_level(card):
    config = mw.addonManager.getConfig(__name__)

    if not config.get("show_pokemon_in_reviewer",True):
        return

    pokemon_data = get_synced_conf()
    
    if not pokemon_data:
        return

    config = mw.addonManager.getConfig(__name__)
    if config.get("PokeType", True):
        poke_type = pkmnimgfolder
    else:
        poke_type = pkmnimgfolder_B

    name, level = None, None
    nickname = None
    deck_or_tag_name = None

    current_pokemon_id = pokemon_data.get("current_pokemon_id")
    current_pokemon = get_pokemon_by_id(current_pokemon_id)
    
    # Handle case where current_pokemon_id points to a removed Pokemon
    if current_pokemon is None:
        # Try to set a new current pokemon from the list
        pokemon_list = pokemon_data.get("pokemon_list", [])
        if pokemon_list:
            # Find the first non-egg Pokemon, or fall back to any Pokemon
            for p in pokemon_list:
                if p and p.get("name") != "Egg":
                    current_pokemon = p
                    break
            if current_pokemon is None and pokemon_list:
                current_pokemon = pokemon_list[0]
            
            if current_pokemon:
                # Update the current_pokemon_id
                from .config import save_synced_conf
                save_synced_conf("current_pokemon_id", current_pokemon.get("id"))
    
    if current_pokemon:
        name, level, nickname = current_pokemon["name"], current_pokemon["level"], current_pokemon["nickname"]
    else:
        # No Pokemon available at all
        name, level, nickname = None, 0, None

    print(f"poke : {name} : {level} : {nickname} : {deck_or_tag_name}")

    # render pokemon icon and level if name is present
    if name:
        show_level = int(level)

        if nickname:
            display_name = nickname
        else:
            display_name = name

        pokemon_image_name = re.sub(r"'", '_', name)

        if deck_or_tag_name is not None:
            deck_or_tag_name = re.sub(r'[<>&"\'`]', ' ', deck_or_tag_name)
            deck_or_tag_name = deck_or_tag_name.split('::')[-1]
            if len(deck_or_tag_name) > 20:
                deck_or_tag_name = deck_or_tag_name[:20] + '...'
            deck_or_tag_name = f"<br><span style='text-align: left; color: gray; font-size: 0.8em;'>{deck_or_tag_name}</span>"
        else:
            deck_or_tag_name = ""

        # Calculate progress to next level (0-100%)
        progress_to_next_level = (level % 1.0) * 100.0
        
        xp_bar = f"""
        <div style='width: 100%; background-color: #e0e0e0; border-radius: 3px; margin-top: 2px; height: 4px;'>
            <div style='width: {progress_to_next_level}%; background-color: #4CAF50; height: 100%; border-radius: 3px; transition: width 0.3s ease;'></div>
        </div>
        """

        pokemon_icon = f"{poke_type}/{pokemon_image_name}.webp"
        # pokemon_icon_html = f"<img src='{pokemon_icon}' alt='{name}' style='height: {IMAGE_HEIGHT};'> {name} Lv.{show_level}"

        pokemon_icon_html = f"""
        <div style='display: flex; align-items: center;'>
            <div style='flex-shrink: 0; min-width: {IMAGE_HEIGHT}; min-height: {IMAGE_HEIGHT};'>
                <img src='{pokemon_icon}' alt='{pokemon_image_name}' style='height: {IMAGE_HEIGHT};'>
            </div>
            <div style='margin-left: 10px; min-width: {IMAGE_HEIGHT}; min-height: {IMAGE_HEIGHT};'>
                <div style='text-align: left;'>
                    {display_name}<br>
                    Lv.{show_level}
                    {deck_or_tag_name}
                    {xp_bar}
                </div>
            </div>
        </div>
        """.replace("\n", "")

    else:
        pokemon_icon_html = DEFAULT_POKEMON_HTML

    change_pokemon_icon_on_top_tool_bar(pokemon_icon_html)


def pokemon_show_answer(card, *args, **kwargs):
    config = mw.addonManager.getConfig(__name__)

    synced_config_data = get_synced_conf()

    current_pokemon_id = synced_config_data["current_pokemon_id"]
    current_pokemon = get_pokemon_by_id(current_pokemon_id)
    add_xp_to_pokemon(current_pokemon, LEVEL_INCREMENT_AMOUNT)

    if "cards_this_session" not in synced_config_data:
        synced_config_data["cards_this_session"] = 0
    save_synced_conf("cards_this_session", synced_config_data["cards_this_session"] + 1)

    if "egg_counter" not in synced_config_data:
        synced_config_data["egg_counter"] = 0
    save_synced_conf("egg_counter", synced_config_data["egg_counter"] + 1)
    
    if config.get("show_pokemon_in_reviewer",True):
        get_pokemon_icon_and_level(card)
    else:
        pokemon_icon_html = ""
        change_pokemon_icon_on_top_tool_bar(pokemon_icon_html)

def pokemon_show_question(card, *args, **kwargs):
    config = mw.addonManager.getConfig(__name__)

    if config.get("show_pokemon_in_reviewer",True):
        get_pokemon_icon_and_level(card)
    else:
        pokemon_icon_html = ""
        change_pokemon_icon_on_top_tool_bar(pokemon_icon_html)

def change_pokemon_icon_on_top_tool_bar(new_label):
    js_code = f"""
    (function() {{
        const elem = document.getElementById("{ENABLE_LABEL_ID}");
        if (!elem) {{
            return false;
        }}
        elem.innerHTML = "{new_label}";
        return true;
    }})();
    """
    def callback(is_empty):
        if is_empty:
            mw.toolbar.web.adjustHeightToFit()

    mw.toolbar.web.evalWithCallback(js_code, callback)


def toggle_on_or_off_top_toolbar():

    config = mw.addonManager.getConfig(__name__)
    if config.get("show_pokemon_in_reviewer", True):
        old_element_id = DISABLE_LABEL_ID
        new_element_id = ENABLE_LABEL_ID
        if mw.state == "review":
            new_label = DEFAULT_POKEMON_HTML
        else:
            new_label = f"<img src='{POKEBALL_ICON}' alt='pokeball' style='height: 1em ;'>"
    else:
        old_element_id = ENABLE_LABEL_ID
        new_element_id = DISABLE_LABEL_ID
        new_label = f"<img src='{POKEBALL_ICON}' alt='pokeball' style='height: 1em ;'>"

    js_code = f"""
    {{
        const elem = document.getElementById("{old_element_id}");
        if (elem) {{
            elem.id = "{new_element_id}";
            elem.innerHTML = "{new_label}";
        }}
    }};
    """

    mw.toolbar.web.eval(js_code)
    mw.toolbar.web.adjustHeightToFit()

def get_pokemon_by_id(id: str) -> dict:
    pokemons = get_synced_conf()["pokemon_list"]
    for pokemon in pokemons:
        if pokemon["id"] == id:
            return pokemon
    return None

def set_pokemon_by_id(id: str, pokemon: dict) -> None:
    pokemon_list = get_synced_conf()["pokemon_list"]
    for i, p in enumerate(pokemon_list):
        if p["id"] == id:
            pokemon_list[i] = pokemon
            break
    save_synced_conf("pokemon_list", pokemon_list)

def remove_pokemon_by_id(id: str) -> None:
    pokemon_list = get_synced_conf()["pokemon_list"]
    removed_pokemon = None
    for i, p in enumerate(pokemon_list):
        if p["id"] == id:
            removed_pokemon = pokemon_list.pop(i)
            break
    save_synced_conf("pokemon_list", pokemon_list)
    return removed_pokemon
