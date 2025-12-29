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

import json
import shutil

from pathlib import Path
from typing import Any, List, Tuple, Union

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

from .config import get_synced_conf
from .custom_py.path_manager import (CustomWidget as QWidget, CustomMessageBox as QMessageBox,
                                    CustomDialog as QDialog, InfoDialog as showInfo)
# Find current directory
addon_package = mw.addonManager.addonFromModule(__name__)
addon_dir = Path(__file__).parents[0]
# Assign Pokemon Image folder directory name

pkmnimgfolder = f"/_addons/{addon_package}/pokemon_images"
pkmnimgfolder_B = f"/_addons/{addon_package}/pokemon_images_static"

cssfolder = f"/_addons/{addon_package}/pokemanki_css"

mediafolder = Path(mw.col.media.dir())

def reset_utils_global():
    global addon_package, addon_dir, pkmnimgfolder, pkmnimgfolder_B, cssfolder, mediafolder
    addon_package = mw.addonManager.addonFromModule(__name__)
    addon_dir = Path(__file__).parents[0]
    pkmnimgfolder = f"/_addons/{addon_package}/pokemon_images"
    pkmnimgfolder_B = f"/_addons/{addon_package}/pokemon_images_static"
    cssfolder = f"/_addons/{addon_package}/pokemanki_css"
    mediafolder = Path(mw.col.media.dir())


# maybe not use
def copy_directory(dir_addon: str, dir_anki: str = None) -> None:
    if not dir_anki:
        dir_anki = dir_addon
    fromdir = addon_dir / dir_addon
    todir = mediafolder / dir_anki
    if not fromdir.is_dir():
        return
    if not todir.is_dir():
        shutil.copytree(str(fromdir), str(todir))
    else:
        try:
            import distutils.dir_util
            distutils.dir_util.copy_tree(str(fromdir), str(todir))
        except:
            pass


def set_default(file_name: str, default: Any) -> None:
    if not get_json(file_name, None):
        write_json(file_name, default)


def get_json(file_name: str, default=None) -> Any:
    file_path = mediafolder / file_name
    value = None
    if file_path.exists():
        with open(file_path, "r") as f:
            value = json.load(f)
    if not value:  # includes json with falsy value
        value = default
    return value


def write_json(file_name: str, value: Any) -> None:
    file_path = mediafolder / file_name
    with open(file_path, "w") as f:
        json.dump(value, f)


def no_pokemon() -> None:
    showInfo(
        "Please open the Stats window to get your Pokémon.",
        parent=mw,
        title="Pokémanki",
    )

# TODO: remove this function
def get_pokemons() -> Tuple[List[str], str]:

    pokemons = get_synced_conf()["pokemon_list"]
    if pokemons is None:
        no_pokemon()
        return (None, None)
    # patch - remove deplicates from pokemon json
    # TODO: fix the code duplicating pokemon
    ids = []
    ret_pokemons = []
    for pokemon in pokemons:
        if pokemon["deck"] not in ids:  # only one pokemon per id
            ret_pokemons.append(pokemon)
            ids.append(pokemon["deck"])
    return (ret_pokemons, f)

def get_pokemons_list() -> List[dict]:
    return get_synced_conf()["pokemon_list"]


def line(i: List[str], a: str, b: Union[int, str], bold: bool = True) -> None:
    # T: Symbols separating first and second column in a statistics table. Eg in "Total:    3 reviews".
    colon = ":"
    if bold:
        i.append(
            ("<tr><td width=200 align=right>%s%s</td><td><b>%s</b></td></tr>")
            % (a, colon, b)
        )
    else:
        i.append(
            ("<tr><td width=200 align=right>%s%s</td><td>%s</td></tr>") % (a, colon, b)
        )


def lineTbl(i: List[str]) -> str:
    return "<table width=400>" + "".join(i) + "</table>"
    