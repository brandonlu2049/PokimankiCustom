import csv
import os
import random
import re
import uuid
from typing import Any, Dict, List, Tuple, Union

from anki.cards import Card
from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import showInfo

from .config import get_local_conf, get_synced_conf, save_synced_conf
from ..utils import pkmnimgfolder, pkmnimgfolder_B, addon_package, addon_dir
from ..stats import MultiStats, TagStats, cardInterval, cardIdsFromDeckIds
from ..custom_py.path_manager import (CustomWidget as QWidget, CustomMessageBox as QMessageBox)
from ..custom_py.count_time import shigeTaskTimer

IMAGE_HEIGHT = "3em"

ENABLE_LABEL_ID = "shige_pokemanki_gold"
DISABLE_LABEL_ID = "disable_pokemanki_gold"

LABEL_PYCMD = "shige_pokemanki_clicked"
LABEL_INDEX = 6

POKEMON_EMPTY = f"/_addons/{addon_package}/custom_py/pokemon_empty.png"
POKEBALL_ICON = f"/_addons/{addon_package}/custom_py/pokeball.png"

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


# =============================================================================
# Pokemon Generation Loading
# =============================================================================

def loadPokemonGenerations(
    csv_fpath: Union[str, bytes],
    pokemonlist: List[str],
    tiers: List[str],
    evolutionLevel1: List[Union[int, None]],
    evolution1: List[Union[str, None]],
    evolutionLevel2: List[Union[int, None]],
    evolution2: List[Union[str, None]],
) -> None:
    with open(csv_fpath, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for line in csv_reader:
            pokemon = line["pokemon"]
            tier = line["tier"]
            first_ev_lv = line["first_evolution_level"]
            if first_ev_lv.isnumeric():
                first_ev_lv = int(first_ev_lv)
            else:
                first_ev_lv = None
            first_ev = line["first_evolution"]
            if first_ev == "NA":
                first_ev = None
            second_ev_lv = line["second_evolution_level"]
            if second_ev_lv.isnumeric():
                second_ev_lv = int(second_ev_lv)
            else:
                second_ev_lv = None
            second_ev = line["second_evolution"]
            if second_ev == "NA":
                second_ev = None

            pokemonlist.append(pokemon)
            tiers.append(tier)
            evolutionLevel1.append(first_ev_lv)
            evolution1.append(first_ev)
            evolutionLevel2.append(second_ev_lv)
            evolution2.append(second_ev)
    return


def load_pokemon_gen_all(
    pokemonlist: List[str],
    tiers: List[str],
    evolutionLevel1: List[Union[int, None]],
    evolution1: List[Union[str, None]],
    evolutionLevel2: List[Union[int, None]],
    evolution2: List[Union[str, None]],
) -> None:
    def load_pokemon_gen(csv_name: str) -> None:
        csv_fpath = addon_dir / "pokemon_evolutions" / csv_name
        loadPokemonGenerations(
            csv_fpath,
            pokemonlist,
            tiers,
            evolutionLevel1,
            evolution1,
            evolutionLevel2,
            evolution2,
        )

    load_pokemon_gen("pokemon_gen1.csv")
    if get_local_conf()["gen2"]:
        load_pokemon_gen("pokemon_gen2.csv")
        if get_local_conf()["gen4_evolutions"]:
            load_pokemon_gen("pokemon_gen1_plus2_plus4.csv")
            load_pokemon_gen("pokemon_gen2_plus4.csv")
        else:
            load_pokemon_gen("pokemon_gen1_plus2_no4.csv")
            load_pokemon_gen("pokemon_gen2_no4.csv")
    else:
        if get_local_conf()["gen4_evolutions"]:
            # a lot of gen 4 evolutions that affect gen 1 also include gen 2 evolutions
            # so let's just include gen 2 for these evolution lines
            load_pokemon_gen("pokemon_gen1_plus2_plus4.csv")
        else:
            load_pokemon_gen("pokemon_gen1_no2_no4.csv")
    if get_local_conf()["gen3"]:
        load_pokemon_gen("pokemon_gen3.csv")
    if get_local_conf()["gen4"]:
        load_pokemon_gen("pokemon_gen4.csv")
    if get_local_conf()["gen5"]:
        load_pokemon_gen("pokemon_gen5.csv")

# =============================================================================
# Starter Pokemon
# =============================================================================

def randomStarter() -> List[str]:
    available_generations = [1]
    if get_local_conf()["gen2"]:
        available_generations.append(2)
    if get_local_conf()["gen3"]:
        available_generations.append(3)
    if get_local_conf()["gen4"]:
        available_generations.append(4)
    if get_local_conf()["gen5"]:
        available_generations.append(5)

    choice_generation = random.choice(available_generations)
    if choice_generation == 1:
        return ["Bulbasaur", "Charmander", "Squirtle"]
    elif choice_generation == 2:
        return ["Chikorita", "Cyndaquil", "Totodile"]
    elif choice_generation == 3:
        return ["Treecko", "Torchic", "Mudkip"]
    elif choice_generation == 4:
        return ["Turtwig", "Chimchar", "Piplup"]
    elif choice_generation == 5:
        return ["Snivy", "Tepig", "Oshawott"]

# =============================================================================
# Profile Pokemon
# =============================================================================

def ProfilePokemon() -> Union[List[dict], None]:
    """
    Generate an array of ProfilePokemon

    :return: List of ProfilePokemon.
    :rtype: List
    """
    print("Fetching Pokemon from profile")
    FirstProfilePokemon()

    pokemontotal = get_synced_conf()["pokemon_list"]

    if not pokemontotal:
        return  # If no pokemanki.json, make empty pokemontotal and modifiedpokemontotal lists

    return pokemontotal


def validate_pokemon_data() -> None:
    """
    Validate Pokemon data from old list format [name, deck, level, nickname] 
    to new dictionary format {"id": ..., "name": ..., "deck": ..., "level": ..., "nickname": ...}
    """
    synced_config_data = get_synced_conf()
    
    # Migrate pokemon_list
    pokemon_list = synced_config_data.get("pokemon_list", [])
    migrated_pokemon = []
    needs_migration = False
    
    for pokemon in pokemon_list:
        if isinstance(pokemon, list):
            # Old format: [name, deck, level, nickname?]
            migrated = {
                "id": str(uuid.uuid4()),
                "name": pokemon[0],
                "deck": pokemon[1], 
                "level": pokemon[2],
                "nickname": pokemon[3] if len(pokemon) > 3 else None
            }
            migrated_pokemon.append(migrated)
            needs_migration = True
        else:
            migrated_pokemon.append(pokemon)
    
    if needs_migration:
        save_synced_conf("pokemon_list", migrated_pokemon)
        print("Migrated pokemon_list to dictionary format with UUIDs")
    
    # Migrate tagmon_list  
    tagmon_list = synced_config_data.get("tagmon_list", [])
    migrated_tagmon = []
    needs_tagmon_migration = False
    
    for pokemon in tagmon_list:
        if isinstance(pokemon, (list, tuple)):
            # Old format: (name, deck, level, nickname?)
            migrated = {
                "id": str(uuid.uuid4()),
                "name": pokemon[0],
                "deck": pokemon[1],
                "level": pokemon[2], 
                "nickname": pokemon[3] if len(pokemon) > 3 else None
            }
            migrated_tagmon.append(migrated)
            needs_tagmon_migration = True
        else:
            migrated_tagmon.append(pokemon)
    
    if needs_tagmon_migration:
        save_synced_conf("tagmon_list", migrated_tagmon)
        print("Migrated tagmon_list to dictionary format with UUIDs")

    # Check for items
    for pokemon in pokemon_list:
        if "items" not in pokemon:
            pokemon["items"] = {
                "everstone": False,
                "megastone": False,
                "alolan": False,
            }
            print("Added items to pokemon: ", pokemon["name"])
        else:
            if "alolan" not in pokemon["items"]:
                pokemon["items"]["alolan"] = False
            if "everstone" not in pokemon["items"]:
                pokemon["items"]["everstone"] = False
            if "megastone" not in pokemon["items"]:
                pokemon["items"]["megastone"] = False
    save_synced_conf("pokemon_list", pokemon_list)


def FirstProfilePokemon() -> None:
    """
    Ensure that at least 1 pokemon is in the profile Pokemon list.
    Set current pokemon index to 0 if unassigned.

    :return: None
    """
    
    # Migrate data first
    validate_pokemon_data()

    synced_config_data = get_synced_conf()
    
    # Handle case where synced config doesn't exist or is missing keys
    if synced_config_data is None:
        from .config import setup_default_synced_conf
        setup_default_synced_conf()
        synced_config_data = get_synced_conf()
    
    pokemon_list = synced_config_data.get("pokemon_list", [])

    if not pokemon_list or len(pokemon_list) == 0:
        # Choose a starter Pokemon
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Pokémanki")
        if hasattr(msgbox, 'change_icon_path'): msgbox.change_icon_path_professors()
        msgbox.setText(
            f"Choose a starter Pokémon!"
        )

        starters = randomStarter()
        for starter in starters:
            msgbox.addButton(starter, QMessageBox.ButtonRole.AcceptRole)
            if hasattr(msgbox, 'change_icon_path'): msgbox.display_image_below_text(starter)
        msgbox.exec()
        starter_pokemon_name = msgbox.clickedButton().text()
        starter_pokemon = create_pokemon(starter_pokemon_name, 1, "A")
        pokemon_list.append(starter_pokemon)
        save_synced_conf("pokemon_list", pokemon_list)
        print("Added starter pokemon to profile Pokemon list: ", starter_pokemon_name)

    if not get_synced_conf().get("current_pokemon_id") and pokemon_list:
        save_synced_conf("current_pokemon_id", pokemon_list[0]["id"])

    return


# =============================================================================
# Pokemon Creation and Management
# =============================================================================

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
        "nickname": nickname,
        "items": {
            "everstone": False,
            "megastone": False,
            "alolan": False,
        },
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
        # Ensure items dict exists (for backwards compatibility with old data)
        items = pokemon.get("items", {"everstone": False, "megastone": False, "alolan": False})
        if pokemon["name"] in evolutions and evolutions[pokemon["name"]]["next_evolution_level"] < pokemon["level"] and items.get("everstone") == False:
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


# =============================================================================
# Pokemon Display
# =============================================================================

def get_pokemon_image_name(pokemon) -> str:
    """
    Get the image name based on the Pokémon's name and any special attributes.

    :param str name: Pokémon's name.
    :return: The image name to be used to retrieve it.
    :rtype: str
    """

    pkmnimgfolder = addon_dir / "pokemon_images"

    fullname = pokemon["name"]
    # Ensure items dict exists (for backwards compatibility with old data)
    items = pokemon.get("items", {"everstone": False, "megastone": False, "alolan": False})
    if items.get("everstone"):
        if pokemon["name"] == "Pikachu":
            if random.randint(1, 5) != 1:  # 4 in 5 chance
                fullname += "_Ash" + str(random.randint(1, 4)) # added
    if items.get("megastone"):
        if any([pokemon["name"] + "_Mega" in imgname for imgname in os.listdir(pkmnimgfolder)]):
            fullname += "_Mega"
            if pokemon["name"] == "Charizard" or pokemon["name"] == "Mewtwo":
                fullname += get_local_conf()["X_or_Y_mega_evolutions"]
    if items.get("alolan"):
        if any([pokemon["name"] + "_Alola" in imgname for imgname in os.listdir(pkmnimgfolder)]):
            fullname += "_Alola"

    return fullname

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

        pokemon_image_name = get_pokemon_image_name(current_pokemon)

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

    if "card_counter" not in synced_config_data:
        synced_config_data["card_counter"] = 0
    save_synced_conf("card_counter", synced_config_data["card_counter"] + 1)
    
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
