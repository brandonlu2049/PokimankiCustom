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

from typing import Any, Dict, Optional

from aqt import mw

# Module-level cache for pokemon evolution mapping
_pokemon_evolution_mapping: Optional[Dict[str, Dict[str, Any]]] = None


def init_config() -> None:
    if not get_synced_conf():

        from .legacy import LegacyImporter

        importer = LegacyImporter()
        importer.import_legacy_conf()
        if not get_synced_conf():
            setup_default_synced_conf()


def get_local_conf() -> Dict[str, Any]:
    return mw.addonManager.getConfig(__name__)


def save_local_conf(config: Dict[str, Any]) -> None:
    mw.addonManager.writeConfig(__name__, config)


def get_synced_conf() -> Dict[str, Any]:
    return mw.col.get_config("pokemanki", default=None)


def save_synced_conf(key: str, value: Any) -> None:
    """Write a single key of the "pokemanki" config of the collection.

    :param str key: Config key
    :param value: New config value
    :rtype: None
    """
    conf = get_synced_conf()
    conf[key] = value
    mw.col.set_config("pokemanki", conf)


def setup_default_synced_conf() -> None:
    default = {
        "alolanlist": [],
        "everstonelist": [],
        "everstonepokemonlist": [],
        "evolution_thresholds": {
            "decks": [100, 250, 500, 750, 1000],
            "tags": [50, 125, 250, 375, 500],
        },
        "megastonelist": [],
        "current_pokemon_id": None,
        "pokemon_list": [],
        "prestigelist": [],
        "tagmon_list": [],
        "tags": [],
        "trades": [],
        "cards_this_session": 0,
        "card_counter": 0,
        "trade_refresh_counter": 0,
    }
    mw.col.set_config("pokemanki", default)

