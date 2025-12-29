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

import csv
import random
import uuid

from typing import List, Tuple, Union

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .config import get_local_conf, get_synced_conf, save_synced_conf
from .utils import *
from .stats import MultiStats, TagStats, cardInterval, cardIdsFromDeckIds
from .custom_py.path_manager import (CustomWidget as QWidget,CustomMessageBox as QMessageBox)

from .custom_py.count_time import shigeTaskTimer

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
        csv_reader = csv.DictReader(csv_file, delimiter=",") # CSVﾌｧｲﾙを読み込む
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


def alertMsgText(
    mon: str,
    id,
    name: str,
    level: int,
    previousLevel: int,
    nickname: str,
    already_assigned: bool,
) -> str:
    prestigelist = get_synced_conf()["prestigelist"]
    msgtxt = ""
    if already_assigned == True:
        if name == "Egg":
            if level == 2 and previousLevel < 2:
                if nickname:
                    msgtxt = f"{nickname} needs more time to hatch."
                else:
                    msgtxt = "Your egg needs more time to hatch."
            elif level == 3 and previousLevel < 3:
                if nickname:
                    msgtxt = f"{nickname} moves occasionally. It should hatch " "soon."
                else:
                    msgtxt = "Your egg moves occasionally. It should hatch " "soon."
            elif level == 4 and previousLevel < 4:
                if nickname:
                    msgtxt = f"{nickname} is making sounds! It's about to " "hatch!"
                else:
                    msgtxt = "Your egg is making sounds! It's about to hatch!"
        elif previousLevel < 5:
            if nickname:
                msgtxt = f"{nickname} has hatched! It's a {mon}!"
            else:
                msgtxt = f"Your egg has hatched! It's a {mon}!"
            previousLevel = level
        if name != mon and name != "Egg" and previousLevel < level:
            if nickname:
                msgtxt = (
                    f"{nickname} has evolved into a {name} "
                    f"(Level {level})! (+{level - previousLevel})"
                )
            else:
                msgtxt = (
                    f"Your {mon} has evolved into a {name} "
                    f"(Level {level})! (+{level - previousLevel})"
                )
        elif previousLevel < level and name != "Egg":
            displayName = name
            if nickname:
                displayName = nickname
            if id in prestigelist:
                msgtxt = (
                    f"{displayName} is now level {level - 50}! "
                    f"(+{level - previousLevel})"
                )
            else:
                msgtxt = (
                    f"Your {displayName} is now level {level}! "
                    f"(+{level - previousLevel})"
                )
    else:
        if name == "Egg":
            msgtxt = "You found an egg!"
        else:
            msgtxt = f"You caught a {name} (Level {level})"
    if msgtxt:
        # return "\n" + msgtxt
        from os.path import dirname, join
        addon_path = dirname(__file__)
        poke_image_path = join(addon_path, "pokemon_images_static", f"{name}.webp")
        # poke_image = f'<img src="{poke_image_path}" alt="poke" style="width:1em; height:1em;">'
        poke_image = f'<img src="{poke_image_path}" alt="poke" width=30 height=30>'
        return "<br>" + poke_image + msgtxt
        # return "\n" + poke_image + msgtxt

    else:
        return ""


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


def getPokemonIndex(
    pokemon_name: str,
    pokemons1: List[str],
    pokemons2: List[Union[str, None]],
    pokemons3: List[Union[str, None]],
) -> str:
    """Returns the index of a Pokémon in the list of Pokémon

    Returns a string of integer because 0 is a falsey value, while '0' is
    truthy.
    pokemon_name should exist in only one of the lists

    :param str pokemon_name: name of Pokémon whose index is requested
    :param List pokemons1: 1st list in which the Pokémon should be searched for
    :param List pokemons2: 2nd list in which the Pokémon should be searched for
    :param List pokemons3: 3rd list in which the Pokémon should be searched for
    :rtype: str or None
    :return: index of pokemon_name in the list it was found in or None
    """

    def getIndex(pokemons: List[Union[str, None]]) -> Union[str, None]:
        try:
            return str(pokemons.index(pokemon_name))
        except:
            return None

    return getIndex(pokemons1) or getIndex(pokemons2) or getIndex(pokemons3)

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

def migrate_pokemon_data() -> None:
    """
    Migrate Pokemon data from old list format [name, deck, level, nickname] 
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

def FirstProfilePokemon() -> None:
    """
    Ensure that at least 1 pokemon is in the profile Pokemon list.
    Set current pokemon index to 0 if unassigned.

    :return: None
    """
    
    # Migrate data first
    migrate_pokemon_data()

    synced_config_data = get_synced_conf()
    pokemon_list = synced_config_data["pokemon_list"]

    if not pokemon_list or len(pokemon_list) == 0:
        # Choose a starter Pokemon
        msgbox = QMessageBox()
        msgbox.setWindowTitle("Pokémanki")
        if hasattr(msgbox, 'change_icon_path'): msgbox.change_icon_path_professors() # ｶｽﾀﾑ
        msgbox.setText(
            f"Choose a starter Pokémon!"
        )

        starters = randomStarter()
        for starter in starters:
            msgbox.addButton(starter, QMessageBox.ButtonRole.AcceptRole)
            if hasattr(msgbox, 'change_icon_path'): msgbox.display_image_below_text(starter) # ｶｽﾀﾑ
        msgbox.exec()
        starter_pokemon_name = msgbox.clickedButton().text()
        pokemon_list.append({
            "id": str(uuid.uuid4()),
            "name": starter_pokemon_name,
            "deck": -1,
            "level": 1,
            "nickname": None
        })
        save_synced_conf("pokemon_list", pokemon_list)
        print("Added starter pokemon to profile Pokemon list: ", starter_pokemon_name)

    if (not get_synced_conf()["current_pokemon_id"]):
        save_synced_conf("current_pokemon_id", pokemon_list[0]["id"])

    return
