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
import bisect
import os
import random
from datetime import date as dt

from typing import List, Optional, Tuple, Union

from .config import get_local_conf, get_synced_conf, save_synced_conf
from .utils import *

from .gui.pokemanki_trade import *
from .custom_py.path_manager import (CustomWidget as QWidget,
                                    CustomMessageBox as QMessageBox,
                                    CustomDialog as QDialog,
                                    InfoDialog as showInfo)

from .pokemon_helpers import generate_by_rarity, get_pokemon_by_id, remove_pokemon_by_id, create_pokemon

TRADES_PER_DAY = 3

class Trades:
    _trade_window = None

    def __init__(self) -> None:
        self.dirname = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        self.mediafolder = mediafolder
        self._trade_window = TradeWindow(self, mw)

    def open(self) -> None:
        """Open the Trade window"""

        # Check if current pokemon is an egg - can't trade eggs
        synced_config_data = get_synced_conf()
        current_pokemon_id = synced_config_data.get("current_pokemon_id")
        current_pokemon = get_pokemon_by_id(current_pokemon_id)
        
        if current_pokemon and current_pokemon.get("name") == "Egg":
            msg = QMessageBox()
            msg.setWindowTitle("Pokémanki")
            msg.setText("You cannot trade while your current Pokémon is an Egg. Wait for it to hatch first!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        self.trades = self._update_trades()
        self._trade_window.open_trades(self.trades)

    def on_bridge_cmd(self, cmd: str) -> Optional[int]: #
        if cmd in ["0", "1", "2"]:
            self._make_trade(int(cmd))

        if cmd == "refresh_trades":
            self._refresh_trades()

        if cmd == "Happy Easter, Exkywor":
            img_path = f"{addon_dir}/pokemon_images/Exkywor.webp"

            from typing import TYPE_CHECKING
            from aqt.qt import QDialog, qtmajor

            if TYPE_CHECKING or qtmajor >= 6:
                from PyQt6 import QtWidgets
            else:
                from PyQt5 import QtWidgets
            from .custom_py.path_manager import (CustomDialog as QDialog)

            class Ui_Dialog(object):
                def setupUi(self, Dialog: QDialog) -> None:
                    Dialog.setObjectName("Dialog")
                    Dialog.setWindowTitle(cmd)
                    Dialog.resize(386, 332)
                    self.gridLayout = QtWidgets.QGridLayout(Dialog)
                    self.gridLayout.setObjectName("gridLayout")
                    self.label = QtWidgets.QLabel(Dialog)
                    self.label.setText(f'<img source="{img_path}" />')
                    self.label.setObjectName("label")
                    self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

            class EggDialog(QDialog):
                def __init__(self, parent: QDialog) -> None:
                    super(EggDialog, self).__init__(parent=parent)
                    self.dialog = Ui_Dialog()
                    self.dialog.setupUi(self)

            egg = EggDialog(self._trade_window)
            return egg.exec()

    def _get_new_trades(self) -> None:
        """Get new trades."""

        tradePokemonList = []
        thresholds = [50, 75, 85, 90, 95, 99]
        rarities = ["F", "E", "D", "C", "B", "A", "S"]
        for _ in range(TRADES_PER_DAY):
            rarity_level = random.randint(0, 100)
            rarity = rarities[bisect.bisect_left(thresholds, rarity_level)]
            tradePokemonList.append(create_pokemon(name="Egg", level=1, rarity=rarity, nickname=None))
        tradePokemonList = generate_by_rarity(tradePokemonList)
        # Make all S-rank Pokemon into Eggs
        for pokemon in tradePokemonList:
            if pokemon["rarity"] == "S":
                pokemon["name"] = "Egg"
        save_synced_conf("trades", tradePokemonList)
        save_synced_conf("trades_date", dt.today().strftime("%d/%m/%Y"))
        return tradePokemonList

    def _update_trades(self) -> bool:
        """Update trades if the date has changed."""

        synced_config_data = get_synced_conf()
        tradeData = synced_config_data["trades"]

        if tradeData:
            currentDate = dt.today().strftime("%d/%m/%Y")
            if currentDate != synced_config_data["trades_date"]:
                tradeData = self._get_new_trades()
        else:
            tradeData = self._get_new_trades()

        return tradeData

    def _make_trade(
        self, tradeIndex: int
    ) -> None:
        """Make a trade.
        
        :param int tradeIndex: Index of the trade in the trades list
        """

        synced_config_data = get_synced_conf()

        tradePokemon = synced_config_data["trades"][tradeIndex]
        tradePokemonDisplaytext = "%s (Level %s)" % (
                        tradePokemon["name"],
                        int(tradePokemon["level"]),
                    )

        current_pokemon_id = synced_config_data["current_pokemon_id"]
        current_pokemon = get_pokemon_by_id(current_pokemon_id)

        currentPokemonDisplaytext = "%s (Level %s)" % (
            current_pokemon["name"],
            int(current_pokemon["level"]),
        )

        confirmation = QMessageBox()
        confirmation.setWindowTitle("Pokémanki")
        confirmation.setText(
            "Are you sure you want to trade your %s for a %s?" % (currentPokemonDisplaytext, tradePokemonDisplaytext)
        )

        confirmation.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirmation.setDefaultButton(QMessageBox.StandardButton.No)
        result = confirmation.exec()
        if result == QMessageBox.StandardButton.Yes:
            # Swap the current pokemon and the trade pokemon
            removed_pokemon = remove_pokemon_by_id(current_pokemon_id).copy()
            synced_config_data = get_synced_conf()  # Refresh after removal
            synced_config_data["pokemon_list"].append(tradePokemon.copy())
            save_synced_conf("pokemon_list", synced_config_data["pokemon_list"])

            save_synced_conf("current_pokemon_id", tradePokemon["id"])

            # Update the trade slot with the removed pokemon
            synced_config_data["trades"][tradeIndex] = removed_pokemon
            save_synced_conf("trades", synced_config_data["trades"])

            self._trade_window.finished_trade()
            showInfo(
                f"You have traded your {currentPokemonDisplaytext} for a {tradePokemonDisplaytext}!",
                parent=self._trade_window,
                title="Pokémanki",
            )
            
            # Trigger overview rerender
            from .hooks.initialization import reset_global_html
            reset_global_html()
            mw.reset()
            # Force refresh the deck browser/overview webview if visible
            if mw.state == "deckBrowser":
                mw.deckBrowser.refresh()
            elif mw.state == "overview":
                mw.overview.refresh()

    
    def _refresh_trades(self):
        """Refresh the trade view after a trade refresh"""
        synced_conf = get_synced_conf()
        trade_refresh_count = synced_conf.get("trade_refresh_counter", 1)
        if trade_refresh_count > 0:
            tradeData = self._get_new_trades()
            # Re-render the trade window with the new trades
            self.trades = tradeData
            self._trade_window.setup_trades(tradeData)
            trade_refresh_count -= 1
            save_synced_conf("trade_refresh_counter", trade_refresh_count)
            return tradeData