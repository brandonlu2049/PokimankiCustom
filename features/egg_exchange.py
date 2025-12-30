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

import inspect
import os
from typing import Optional

from aqt import mw

from ..helpers.config import get_synced_conf, save_synced_conf
from ..utils import mediafolder
from ..gui.pokemanki_egg_exchange import EggExchangeWindow
from ..custom_py.path_manager import (
    CustomMessageBox as QMessageBox,
    InfoDialog as showInfo
)
from ..helpers.pokemon_helpers import get_pokemon_by_id, remove_pokemon_by_id, create_pokemon

# Rarity levels in order from lowest to highest
RARITY_ORDER = ["F", "E", "D", "C", "B", "A", "S"]
EGGS_REQUIRED_FOR_UPGRADE = 5


def get_next_rarity(current_rarity: str) -> Optional[str]:
    """Get the next higher rarity level.
    
    :param str current_rarity: The current rarity level
    :return: The next rarity level, or None if already at max
    """
    if current_rarity not in RARITY_ORDER:
        return None
    current_index = RARITY_ORDER.index(current_rarity)
    if current_index >= len(RARITY_ORDER) - 1:
        return None  # Already at max rarity (S)
    return RARITY_ORDER[current_index + 1]


class EggExchange:
    _exchange_window = None

    def __init__(self) -> None:
        self.dirname = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        self.mediafolder = mediafolder
        self._exchange_window = EggExchangeWindow(self, mw)

    def open(self) -> None:
        """Open the Egg Exchange window"""
        eggs = self._get_eggs()
        egg_counts = self._count_eggs_by_rarity(eggs)

        self._exchange_window.open_egg_exchange(eggs, egg_counts)

    def _get_eggs(self) -> list:
        """Get all eggs from the pokemon list."""
        synced_conf = get_synced_conf()
        pokemon_list = synced_conf.get("pokemon_list", [])
        eggs = [p for p in pokemon_list if p.get("name") == "Egg"]
        return eggs

    def _count_eggs_by_rarity(self, eggs: list) -> dict:
        """Count eggs by rarity level.
        
        :param list eggs: List of egg dicts
        :return: Dict mapping rarity to count
        """
        counts = {r: 0 for r in RARITY_ORDER}
        for egg in eggs:
            rarity = egg.get("rarity", "F")
            if rarity in counts:
                counts[rarity] += 1
        return counts

    def on_bridge_cmd(self, cmd: str) -> Optional[int]:
        """Handle bridge commands from the webview.
        
        :param str cmd: The command string from pycmd()
        """
        if cmd.startswith("upgrade_selected:"):
            # Format: upgrade_selected:rarity:id1,id2,id3,id4,id5
            parts = cmd.split(":", 2)
            if len(parts) == 3:
                rarity = parts[1]
                egg_ids = parts[2].split(",")
                self._upgrade_selected_eggs(rarity, egg_ids)
        elif cmd.startswith("upgrade:"):
            rarity = cmd.split(":", 1)[1]
            self._upgrade_eggs(rarity)

    def _upgrade_selected_eggs(self, rarity: str, egg_ids: list) -> None:
        """Upgrade specific selected eggs to 1 egg of higher rarity.
        
        :param str rarity: The rarity level of eggs being upgraded
        :param list egg_ids: List of egg IDs to upgrade
        """
        next_rarity = get_next_rarity(rarity)
        if not next_rarity:
            showInfo(
                "S-rank eggs are already at maximum rarity!",
                parent=self._exchange_window,
                title="Pokémanki",
            )
            return

        if len(egg_ids) < EGGS_REQUIRED_FOR_UPGRADE:
            showInfo(
                f"You need to select {EGGS_REQUIRED_FOR_UPGRADE} eggs to upgrade. You selected {len(egg_ids)}.",
                parent=self._exchange_window,
                title="Pokémanki",
            )
            return

        # Verify all eggs exist and are of the correct rarity
        eggs_to_remove = []
        for egg_id in egg_ids[:EGGS_REQUIRED_FOR_UPGRADE]:
            egg = get_pokemon_by_id(egg_id)
            if not egg:
                showInfo(
                    f"Could not find one of the selected eggs.",
                    parent=self._exchange_window,
                    title="Pokémanki",
                )
                return
            if egg.get("name") != "Egg":
                showInfo(
                    f"One of the selected items is not an egg!",
                    parent=self._exchange_window,
                    title="Pokémanki",
                )
                return
            if egg.get("rarity") != rarity:
                showInfo(
                    f"One of the selected eggs is not {rarity}-rank!",
                    parent=self._exchange_window,
                    title="Pokémanki",
                )
                return
            eggs_to_remove.append(egg)

        # Confirm upgrade
        confirmation = QMessageBox()
        confirmation.setWindowTitle("Pokémanki")
        confirmation.setText(
            f"Trade {EGGS_REQUIRED_FOR_UPGRADE} selected {rarity}-rank eggs for 1 {next_rarity}-rank egg?"
        )
        confirmation.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirmation.setDefaultButton(QMessageBox.StandardButton.No)
        result = confirmation.exec()

        if result == QMessageBox.StandardButton.Yes:
            # Check if current pokemon is one of the eggs being removed
            synced_conf = get_synced_conf()
            current_pokemon_id = synced_conf.get("current_pokemon_id")
            removed_ids = [egg["id"] for egg in eggs_to_remove]
            current_was_removed = current_pokemon_id in removed_ids
            
            # Remove the selected eggs
            for egg in eggs_to_remove:
                remove_pokemon_by_id(egg["id"])

            # Create a new egg with higher rarity
            new_egg = create_pokemon(name="Egg", level=1, rarity=next_rarity, nickname=None)

            # Add the new egg to the list
            synced_conf = get_synced_conf()  # Refresh after removal
            synced_conf["pokemon_list"].append(new_egg)
            save_synced_conf("pokemon_list", synced_conf["pokemon_list"])

            # If current pokemon was removed, set to the new egg
            if current_was_removed:
                save_synced_conf("current_pokemon_id", new_egg["id"])

            self._exchange_window.finished_exchange()
            showInfo(
                f"Successfully upgraded {EGGS_REQUIRED_FOR_UPGRADE} {rarity}-rank eggs to 1 {next_rarity}-rank egg!",
                parent=self._exchange_window,
                title="Pokémanki",
            )

            # Trigger overview rerender
            from ..hooks.initialization import reset_global_html
            reset_global_html()
            mw.reset()
            if mw.state == "deckBrowser":
                mw.deckBrowser.refresh()
            elif mw.state == "overview":
                mw.overview.refresh()

    def _upgrade_eggs(self, rarity: str) -> None:
        """Upgrade 5 eggs of the same rarity to 1 egg of higher rarity (auto-select first 5).
        
        :param str rarity: The rarity level of eggs to upgrade
        """
        next_rarity = get_next_rarity(rarity)
        if not next_rarity:
            showInfo(
                "S-rank eggs are already at maximum rarity!",
                parent=self._exchange_window,
                title="Pokémanki",
            )
            return

        # Get all eggs of this rarity
        eggs = self._get_eggs()
        eggs_of_rarity = [e for e in eggs if e.get("rarity") == rarity]

        if len(eggs_of_rarity) < EGGS_REQUIRED_FOR_UPGRADE:
            showInfo(
                f"You need {EGGS_REQUIRED_FOR_UPGRADE} {rarity}-rank eggs to upgrade. You have {len(eggs_of_rarity)}.",
                parent=self._exchange_window,
                title="Pokémanki",
            )
            return

        # Confirm upgrade
        confirmation = QMessageBox()
        confirmation.setWindowTitle("Pokémanki")
        confirmation.setText(
            f"Trade {EGGS_REQUIRED_FOR_UPGRADE} {rarity}-rank eggs for 1 {next_rarity}-rank egg?"
        )
        confirmation.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirmation.setDefaultButton(QMessageBox.StandardButton.No)
        result = confirmation.exec()

        if result == QMessageBox.StandardButton.Yes:
            # Check if current pokemon is one of the eggs being removed
            synced_conf = get_synced_conf()
            current_pokemon_id = synced_conf.get("current_pokemon_id")
            eggs_to_remove = eggs_of_rarity[:EGGS_REQUIRED_FOR_UPGRADE]
            removed_ids = [egg["id"] for egg in eggs_to_remove]
            current_was_removed = current_pokemon_id in removed_ids
            
            # Remove the eggs
            for egg in eggs_to_remove:
                remove_pokemon_by_id(egg["id"])

            # Create a new egg with higher rarity
            new_egg = create_pokemon(name="Egg", level=1, rarity=next_rarity, nickname=None)

            # Add the new egg to the list
            synced_conf = get_synced_conf()  # Refresh after removal
            synced_conf["pokemon_list"].append(new_egg)
            save_synced_conf("pokemon_list", synced_conf["pokemon_list"])

            # If current pokemon was removed, set to the new egg
            if current_was_removed:
                save_synced_conf("current_pokemon_id", new_egg["id"])

            self._exchange_window.finished_exchange()
            showInfo(
                f"Successfully upgraded {EGGS_REQUIRED_FOR_UPGRADE} {rarity}-rank eggs to 1 {next_rarity}-rank egg!",
                parent=self._exchange_window,
                title="Pokémanki",
            )

            # Trigger overview rerender
            from ..hooks.initialization import reset_global_html
            reset_global_html()
            mw.reset()
            if mw.state == "deckBrowser":
                mw.deckBrowser.refresh()
            elif mw.state == "overview":
                mw.overview.refresh()
