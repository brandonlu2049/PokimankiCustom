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

import ctypes
import platform
import random
import re

from typing import TYPE_CHECKING

from aqt.qt import QDialog, qtmajor
from aqt.webview import AnkiWebView

if TYPE_CHECKING or qtmajor >= 6:
    from PyQt6 import QtWidgets
else:
    from PyQt5 import QtWidgets

from ..utils import cssfolder, pkmnimgfolder, pkmnimgfolder_B
from aqt import mw, Qt
from .forms import pokemanki_trade
from ..custom_py.path_manager import (CustomWidget as QWidget,CustomMessageBox as QMessageBox,CustomDialog as QDialog,
                                        random_trainer_image)
from ..custom_py.set_js_message import POKE_TYPE
from ..helpers.config import get_synced_conf

from aqt.webview import AnkiWebViewKind
from anki.utils import pointVersion

if TYPE_CHECKING:
    from ..features.trades import Trades


class TradeWindow(QDialog):
    def __init__(self, parentObj, mw):
        super().__init__(mw)
        self.dialog = pokemanki_trade.Ui_Dialog()
        self.dialog.setupUi(self)
        self.trades = None
        self.setupUi(parentObj, mw)

    def setupUi(self, parent:"Trades", mw):
        # self.dialog.webEngineView = AnkiWebView(parent=self, title="pokémanki trades")

        # https://forums.ankiweb.net/t/add-ons-and-25-02-1-default-ankiwebview-api-access-workarounds/59309
        # https://github.com/ankitects/anki/pull/3933
        if pointVersion() >= 250201:
            self.dialog.webEngineView = AnkiWebView(parent=self, title="pokémanki trades", kind=AnkiWebViewKind.EDITOR)
        else:
            self.dialog.webEngineView = AnkiWebView(parent=self, title="pokémanki trades")

        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.dialog.webEngineView.sizePolicy().hasHeightForWidth()
        )
        self.dialog.webEngineView.setSizePolicy(sizePolicy)
        self.dialog.webEngineView.setObjectName("webEngineView")
        self.dialog.verticalLayout_2.addWidget(self.dialog.webEngineView)

        self.dialog.webEngineView.set_bridge_command(parent.on_bridge_cmd, parent)

        # Set in the middle of the screen
        if platform.system() == "Windows":
            user32 = ctypes.windll.user32
            posX = int(user32.GetSystemMetrics(0) / 2 - self.width() / 2)
            posY = int(user32.GetSystemMetrics(1) / 2 - self.height() / 2)
        else:
            posX = int(mw.frameGeometry().width() / 2 - self.width() / 2)
            posY = int(mw.frameGeometry().height() / 2 - self.height() / 2)

        self.setGeometry(posX, posY, self.width(), self.height())

    def setup_trades(self, trades):
        """Set up the web view's html.

        :param list trades: List of trade Pokemon dicts to display
        """
        self.trades = trades
        # Get current pokemon to show what the user will trade away
        synced_conf = get_synced_conf()
        current_pokemon_id = synced_conf.get("current_pokemon_id")
        current_pokemon = None
        if current_pokemon_id:
            for p in synced_conf.get("pokemon_list", []):
                if p.get("id") == current_pokemon_id:
                    current_pokemon = p
                    break

        self.dialog.webEngineView.stdHtml(
            body=_trades_html(trades, current_pokemon),
            css=[f"{cssfolder}/view_trade.css", f"{cssfolder}/main.css"],
            context=self,
        )

    def open_trades(self, trades):
        """Set up the web view's html and opens the trade dialog.

        :param list trades: List of trades to display
        """

        self.setup_trades(trades)
        self.show()
        # self.open()
        # self.raise_()

    def finished_trade(self):
        """Refresh the trade view after a successful trade """
        # Reload trades from config and refresh the view
        synced_conf = get_synced_conf()
        trades = synced_conf.get("trades", [])
        self.trades = trades
        self.setup_trades(trades)
        self.dialog.webEngineView.update()
            
def _trades_html(trades, current_pokemon):
    """Generate the html code for the trades window.

    :param list trades: List of trade Pokemon to display
    :param dict current_pokemon: The user's current Pokemon dict (what they will trade away)
    :return: The html code.
    :rtype: str
    """

    # Write trade function
    txt = """
<script>
function callTrade(n) { pycmd(n); }
function callRefresh() { pycmd("refresh_trades"); }
function click_handler(e) { if(e.shiftKey) { pycmd("Happy Easter, Exkywor") } }
</script>
"""

    synced_conf = get_synced_conf()
    trade_refresh_count = synced_conf.get("trade_refresh_counter", 0)

    # Add refresh button at top
    txt += f'<div class="pk-td-refresh-container" style="text-align: center; margin-bottom: 15px;">'
    txt += f'<span class="pk-td-refresh-count">Refresh count: {trade_refresh_count}</span>'
    txt += '</div>'
    txt += '<div class="pk-td-refresh-container" style="text-align: center; margin-bottom: 15px;">'
    txt += '<button class="pk-button" onclick="callRefresh()">Refresh</button>'
    txt += '</div>'

    # Open trades container
    txt += '<div class="pk-td-container">'

    # Generate each of the trades
    for i in range(len(trades)):
        txt += _trade_html(i, trades[i], current_pokemon)

    # Close trades container
    txt += "</div>"

    return txt


def _trade_html(i, trade_pokemon, current_pokemon):
    """Generate the html code for a trade.

    :param int i: Trade number.
    :param dict trade_pokemon: The Pokemon being offered in this trade
    :param dict current_pokemon: The user's current Pokemon (what they will trade away)
    :return: Trade's html.
    :rtype: str
    """

    # Open trade container with rarity class for fancy border styling
    rarity = trade_pokemon.get("rarity", "F")
    trade = f'<div class="pk-td-trade rarity-{rarity}">'

    ###########
    # Easter
    ###########
    onclick = ""
    if i == 0:
        onclick = 'onclick="click_handler(event)" '

    ###########
    # Head info
    ###########

    trade += (
        '<div class="pk-td-trainer" style="display: flex; align-items: center;">'
        f'<img src="{random_trainer_image[i + 1]}" alt="random-trainer-image" style="width: auto; height: auto; margin-right: 10px;">'
        f'<h2 {onclick}><b>Trainer {i + 1}</b></h2>'
        '<div class="pk-divider" style="margin-top: 10px;"></div>'
        "</div>"
    )

    config = mw.addonManager.getConfig(__name__)

    pokemon_name_style = '"cursor: pointer; text-decoration: none;" onmouseover="this.style.textDecoration=\'underline\'" onmouseout="this.style.textDecoration=\'none\'"'


    # Render trade pokemon
    # Get trade pokemon name (use nickname if available, otherwise name)
    trade_pokemon_name = trade_pokemon.get("name", "Unknown")
    trade_pokemon_nickname = trade_pokemon.get("nickname") or trade_pokemon_name
    if trade_pokemon_name == "Egg":
        trade_pokemon_nickname = "Mysterious Egg"
    trade_pokemon_level = trade_pokemon.get("level", 1)
    search_pokemon_name = re.sub(r"'", '', trade_pokemon_name)

    trade += (
        '<div class="pk-td-offer">'
        '<div class="pk-td-offer-txt">'
        f'<span class="pk-td-offer-txt-name" style={pokemon_name_style} onclick="pycmd(\'shige_pokemanki_button_5:{search_pokemon_name}\')">'
        f'<b>{trade_pokemon_nickname} (Lv. {int(trade_pokemon_level)})</b></span>'
        "</div>"
        '<div class="pk-td-img-container">'
        f'<img src="{pkmnimgfolder if config[POKE_TYPE] else pkmnimgfolder_B}/{trade_pokemon_name}.webp" class="pk-td-offer-img"/>'
        "</div>"
        "</div>"
    )

    # Render current pokemon
    current_pokemon_name = current_pokemon.get("name", "Unknown")
    current_pokemon_nickname = current_pokemon.get("nickname") or current_pokemon_name
    current_pokemon_level = current_pokemon.get("level", 1)
    search_current_name = re.sub(r"'", '', current_pokemon_name)

    trade += (
        '<div class="pk-td-offer">'
        '<div class="pk-td-offer-txt">'
        '<span class="pk-td-offer-txt-title"><b>for your:</b></span>'
        f'<span class="pk-td-offer-txt-name" style={pokemon_name_style} onclick="pycmd(\'shige_pokemanki_button_5:{search_current_name}\')">'
        f'<b>{current_pokemon_nickname} (Lv. {int(current_pokemon_level)})</b></span>'
        "</div>"
        '<div class="pk-td-img-container">'
        f'<img src="{pkmnimgfolder if config[POKE_TYPE] else pkmnimgfolder_B}/{current_pokemon_name}.webp" class="pk-td-offer-img"/>'
        "</div>"
        "</div>"
    )

    ##########
    # Bottom
    ##########
    trade += (
        '<div class="pk-td-bottom">'
        '<div class="pk-divider" style="margin-bottom: 10px"></div>'
        f'<button class"pk-button" onclick="callTrade({i})">Trade</button>'
        "</div>"
    )

    # Close trade
    trade += "</div>"

    return trade
