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
from ..gui.pokemanki_shop import ShopWindow
from ..custom_py.path_manager import (
    CustomMessageBox as QMessageBox,
    InfoDialog as showInfo
)


class Shop:
    _shop_window = None

    def __init__(self) -> None:
        self.dirname = os.path.dirname(
            os.path.abspath(inspect.getfile(inspect.currentframe()))
        )
        self.mediafolder = mediafolder
        self._shop_window = ShopWindow(self, mw)

    def open(self) -> None:
        """Open the Shop window"""
        self._shop_window.open_shop()

    def on_bridge_cmd(self, cmd: str) -> Optional[int]:
        """Handle bridge commands from the webview.
        
        :param str cmd: The command string from pycmd()
        """
        # TODO: Implement shop commands
        pass

