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

from typing import TYPE_CHECKING

from aqt.qt import QDialog, qtmajor
from aqt.webview import AnkiWebView

if TYPE_CHECKING or qtmajor >= 6:
    from PyQt6 import QtWidgets
else:
    from PyQt5 import QtWidgets

from ..utils import cssfolder, pkmnimgfolder, pkmnimgfolder_B
from aqt import mw

from .forms import pokemanki_shop
from ..custom_py.path_manager import (CustomDialog as QDialog)
from ..custom_py.set_js_message import POKE_TYPE
from ..helpers.config import get_synced_conf
from aqt.webview import AnkiWebViewKind
from anki.utils import pointVersion
from ..utils import cssfolder, pkmnimgfolder, pkmnimgfolder_B

if TYPE_CHECKING:
    from ..features.shop import Shop


class ShopWindow(QDialog):
    def __init__(self, parentObj, mw):
        super().__init__(mw)
        self.dialog = pokemanki_shop.Ui_Dialog()
        self.dialog.setupUi(self)
        self.setupUi(parentObj, mw)

    def setupUi(self, parent: "Shop", mw):
        # https://forums.ankiweb.net/t/add-ons-and-25-02-1-default-ankiwebview-api-access-workarounds/59309
        # https://github.com/ankitects/anki/pull/3933
        if pointVersion() >= 250201:
            self.dialog.webEngineView = AnkiWebView(parent=self, title="pokémanki shop", kind=AnkiWebViewKind.EDITOR)
        else:
            self.dialog.webEngineView = AnkiWebView(parent=self, title="pokémanki shop")

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

    def setup_content(self):
        """Set up the web view's html."""
        self.dialog.webEngineView.stdHtml(
            body=_shop_html(),
            css=[f"{cssfolder}/view_shop.css", f"{cssfolder}/main.css"],
            context=self,
        )

    def open_shop(self):
        """Set up the web view's html and opens the shop dialog."""
        self.setup_content()
        self.show()


def _shop_html():
    """Generate the html code for the shop window.

    :return: The html code.
    :rtype: str
    """
    config = mw.addonManager.getConfig(__name__)
    addon_package = mw.addonManager.addonFromModule(__name__)
    mediafolder = f"/_addons/{addon_package}/media"

    synced_conf = get_synced_conf()
    pokecoin_count = synced_conf.get("card_counter", 0)

    img_folder_name = "pokemon_images" if config[POKE_TYPE] else "pokemon_images_static"

    # Add shop title
    txt = f'<h1 class="shop-title-container">Pokémart</h2>'

    img_style = 'style="height: 80px; width: auto;"'
    if pokecoin_count > 1000:
        pokecoin_image = f'<img src="{mediafolder}/coin-bundle-xlarge.webp" {img_style}>'
    elif pokecoin_count > 500:
        pokecoin_image = f'<img src="{mediafolder}/coin-bundle-large-v2.webp" {img_style}>'
    elif pokecoin_count > 100:
        pokecoin_image = f'<img src="{mediafolder}/coin-bundle-medium_v2.webp" {img_style}>'
    elif pokecoin_count > 10:
        pokecoin_image = f'<img src="{mediafolder}/coin-bundle-small_v2.webp" {img_style}>'
    elif pokecoin_count > 0:
        pokecoin_image = f'<img src="{mediafolder}/coin-bundle-xsmall.webp" {img_style}>'
    else:
        pokecoin_image = f'<img src="{mediafolder}/coin-bundle-xxsmall.webp" {img_style}>'
        
    # Add coin counter
    txt += f'<div class="shop-pokecoin-container"> {pokecoin_image} {pokecoin_count}</div>'

    # Add shop items
    txt += '<h2 class="shop-heading-container">Items</h2>'
    txt += '<div class="shop-items-container">'
    
    # Egg Machine item
    txt += f'''
    <div class="shop-item shop-item-egg" onclick="pycmd('buy_egg')">
        <div class="shop-item-glow"></div>
        <div class="shop-item-image">
            <img src="{pkmnimgfolder if config[POKE_TYPE] else pkmnimgfolder_B}/Egg.webp" alt="Egg">
        </div>
        <div class="shop-item-name">Egg Machine</div>
        <div class="shop-item-description">Hatch a random Pokémon!</div>
        <div class="shop-item-price">
            <img src="{mediafolder}/coin-bundle-xsmall.webp" alt="coins">
            <span>200</span>
        </div>
        <button class="shop-item-buy-btn">Purchase</button>
    </div>
    '''
    
    txt += f'<div class="shop-item shop-item-coming-soon"><span>More coming soon...</span></div>'
    txt += '</div>'
    return txt

