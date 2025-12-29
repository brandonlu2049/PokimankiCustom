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

from .forms import pokemanki_egg_exchange
from ..custom_py.path_manager import (CustomDialog as QDialog)
from ..custom_py.set_js_message import POKE_TYPE
from ..config import get_synced_conf
from ..pokemon_helpers import RARITY_COLOR_MAP
from aqt.webview import AnkiWebViewKind
from anki.utils import pointVersion

if TYPE_CHECKING:
    from ..egg_exchange import EggExchange

# Rarity levels and colors for display
RARITY_ORDER = ["F", "E", "D", "C", "B", "A", "S"]
EGGS_REQUIRED_FOR_UPGRADE = 5


class EggExchangeWindow(QDialog):
    def __init__(self, parentObj, mw):
        super().__init__(mw)
        self.dialog = pokemanki_egg_exchange.Ui_Dialog()
        self.dialog.setupUi(self)
        self.setupUi(parentObj, mw)

    def setupUi(self, parent: "EggExchange", mw):
        # https://forums.ankiweb.net/t/add-ons-and-25-02-1-default-ankiwebview-api-access-workarounds/59309
        # https://github.com/ankitects/anki/pull/3933
        if pointVersion() >= 250201:
            self.dialog.webEngineView = AnkiWebView(parent=self, title="pokémanki egg exchange", kind=AnkiWebViewKind.EDITOR)
        else:
            self.dialog.webEngineView = AnkiWebView(parent=self, title="pokémanki egg exchange")

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

    def setup_content(self, eggs, egg_counts=None):
        """Set up the web view's html.

        :param list eggs: List of egg Pokemon dicts to display
        :param dict egg_counts: Optional dict mapping rarity to count
        """
        self.eggs = eggs
        if egg_counts is None:
            egg_counts = self._count_eggs_by_rarity(eggs)
        self.dialog.webEngineView.stdHtml(
            body=_egg_exchange_html(eggs, egg_counts),
            css=[f"{cssfolder}/view_egg_exchange.css", f"{cssfolder}/main.css"],
            context=self,
        )

    def _count_eggs_by_rarity(self, eggs):
        """Count eggs by rarity level."""
        counts = {r: 0 for r in RARITY_ORDER}
        for egg in eggs:
            rarity = egg.get("rarity", "F")
            if rarity in counts:
                counts[rarity] += 1
        return counts

    def open_egg_exchange(self, eggs, egg_counts=None):
        """Set up the web view's html and opens the egg exchange dialog.

        :param list eggs: List of eggs to display
        :param dict egg_counts: Optional dict mapping rarity to count
        """
        self.setup_content(eggs, egg_counts)
        self.show()

    def finished_exchange(self):
        """Refresh the egg exchange view after a successful exchange"""
        synced_conf = get_synced_conf()
        eggs = [p for p in synced_conf.get("pokemon_list", []) if p.get("name") == "Egg"]
        self.eggs = eggs
        self.setup_content(eggs)
        self.dialog.webEngineView.update()


def _egg_exchange_html(eggs, egg_counts):
    """Generate the html code for the egg exchange window.

    :param list eggs: List of egg Pokemon to display
    :param dict egg_counts: Dict mapping rarity to count
    :return: The html code.
    :rtype: str
    """
    config = mw.addonManager.getConfig(__name__)

    txt = """
<script>
// Track selected eggs by rarity
let selectedEggs = {};
const EGGS_REQUIRED = """ + str(EGGS_REQUIRED_FOR_UPGRADE) + """;

function initSelection() {
    selectedEggs = {};
    ['F', 'E', 'D', 'C', 'B', 'A', 'S'].forEach(r => selectedEggs[r] = []);
}
initSelection();

function toggleEggSelection(id, rarity) {
    const card = document.getElementById('egg-' + id);
    const idx = selectedEggs[rarity].indexOf(id);
    
    if (idx > -1) {
        // Deselect
        selectedEggs[rarity].splice(idx, 1);
        card.classList.remove('egg-selected');
    } else {
        // Select (only if under limit)
        if (selectedEggs[rarity].length < EGGS_REQUIRED) {
            selectedEggs[rarity].push(id);
            card.classList.add('egg-selected');
        }
    }
    updateUpgradeButtons();
    updateSelectionCounters();
}

function updateSelectionCounters() {
    ['F', 'E', 'D', 'C', 'B', 'A'].forEach(rarity => {
        const counter = document.getElementById('selection-count-' + rarity);
        if (counter) {
            counter.textContent = selectedEggs[rarity].length + '/' + EGGS_REQUIRED + ' selected';
        }
    });
}

function updateUpgradeButtons() {
    ['F', 'E', 'D', 'C', 'B', 'A'].forEach(rarity => {
        const btn = document.getElementById('upgrade-btn-' + rarity);
        if (btn) {
            const hasEnough = selectedEggs[rarity].length >= EGGS_REQUIRED;
            btn.disabled = !hasEnough;
            btn.textContent = hasEnough ? 'Upgrade Selected' : 'Select ' + EGGS_REQUIRED + ' Eggs';
        }
    });
}

function selectAllOfRarity(rarity) {
    const eggs = document.querySelectorAll('.egg-card[data-rarity="' + rarity + '"]');
    selectedEggs[rarity] = [];
    
    // Deselect all first
    eggs.forEach(card => card.classList.remove('egg-selected'));
    
    // Select up to EGGS_REQUIRED
    let count = 0;
    eggs.forEach(card => {
        if (count < EGGS_REQUIRED) {
            const id = card.dataset.id;
            selectedEggs[rarity].push(id);
            card.classList.add('egg-selected');
            count++;
        }
    });
    
    updateUpgradeButtons();
    updateSelectionCounters();
}

function clearSelection(rarity) {
    selectedEggs[rarity] = [];
    document.querySelectorAll('.egg-card[data-rarity="' + rarity + '"]').forEach(card => {
        card.classList.remove('egg-selected');
    });
    updateUpgradeButtons();
    updateSelectionCounters();
}

function callUpgradeSelected(rarity) {
    if (selectedEggs[rarity].length >= EGGS_REQUIRED) {
        const ids = selectedEggs[rarity].join(',');
        pycmd('upgrade_selected:' + rarity + ':' + ids);
    }
}
</script>
"""

    # Group eggs by rarity
    eggs_by_rarity = {r: [] for r in RARITY_ORDER}
    for egg in eggs:
        rarity = egg.get("rarity", "F")
        if rarity in eggs_by_rarity:
            eggs_by_rarity[rarity].append(egg)

    txt += '<div class="egg-upgrade-section">'
    txt += f'<div class="egg-upgrade-title">🥚 Egg Exchange - Select {EGGS_REQUIRED_FOR_UPGRADE} eggs to upgrade</div>'
    
    # Generate sections for each rarity (except S which can't be upgraded)
    for i, rarity in enumerate(RARITY_ORDER[:-1]):
        next_rarity = RARITY_ORDER[i + 1]
        rarity_eggs = eggs_by_rarity.get(rarity, [])
        count = len(rarity_eggs)
        color = RARITY_COLOR_MAP.get(rarity, "#888")
        next_color = RARITY_COLOR_MAP.get(next_rarity, "#888")
        
        txt += f'<div class="rarity-section">'
        
        # Header
        txt += f'''
        <div class="rarity-header">
            <div class="rarity-header-left">
                <span class="rarity-badge" style="background: {color}; color: white;">{rarity}</span>
                <span class="rarity-info">{count} egg{"s" if count != 1 else ""} available</span>
                <span class="selection-count" id="selection-count-{rarity}">0/{EGGS_REQUIRED_FOR_UPGRADE} selected</span>
            </div>
            <div class="rarity-actions">
                <button class="action-btn select-all-btn" onclick="selectAllOfRarity('{rarity}')" {"disabled" if count == 0 else ""}>Select All</button>
                <button class="action-btn clear-btn" onclick="clearSelection('{rarity}')">Clear</button>
            </div>
        </div>
        '''
        
        # Eggs grid
        if rarity_eggs:
            txt += '<div class="eggs-grid">'
            for egg in rarity_eggs:
                txt += _egg_card_html(egg, config)
            txt += '</div>'
        else:
            txt += f'<div class="no-eggs-msg">No {rarity}-rank eggs</div>'
        
        # Upgrade row
        txt += f'''
        <div class="upgrade-row">
            <span style="color: #aaa;">Trade {EGGS_REQUIRED_FOR_UPGRADE} selected eggs for:</span>
            <span class="rarity-badge" style="background: {next_color}; color: white;">{next_rarity}</span>
            <button class="upgrade-btn" id="upgrade-btn-{rarity}" onclick="callUpgradeSelected('{rarity}')" disabled>
                Select {EGGS_REQUIRED_FOR_UPGRADE} Eggs
            </button>
        </div>
        '''
        
        txt += '</div>'
    
    # S-rank section (can't upgrade further)
    s_eggs = eggs_by_rarity.get("S", [])
    s_count = len(s_eggs)
    txt += f'''
    <div class="rarity-section">
        <div class="rarity-header">
            <div class="rarity-header-left">
                <span class="rarity-badge" style="background: {RARITY_COLOR_MAP["S"]}; color: black;">S</span>
                <span class="rarity-info">{s_count} egg{"s" if s_count != 1 else ""} - Maximum Rarity!</span>
            </div>
        </div>
    '''
    if s_eggs:
        txt += '<div class="eggs-grid">'
        for egg in s_eggs:
            txt += _egg_card_html(egg, config)
        txt += '</div>'
    else:
        txt += '<div class="no-eggs-msg">No S-rank eggs yet</div>'
    txt += '<div class="s-rank-section">S-rank eggs are at maximum rarity.</div>'
    txt += '</div>'
    
    txt += '</div>'

    return txt


def _egg_card_html(egg, config):
    """Generate the html code for a single egg card.

    :param dict egg: The egg Pokemon dict
    :param dict config: The addon config
    :return: Egg card's html.
    :rtype: str
    """
    egg_id = egg.get("id", "")
    egg_name = egg.get("name", "Egg")
    egg_level = egg.get("level", 1)
    egg_rarity = egg.get("rarity", "F")

    html = f'''
    <div class="egg-card" id="egg-{egg_id}" data-id="{egg_id}" data-rarity="{egg_rarity}" 
         onclick="toggleEggSelection('{egg_id}', '{egg_rarity}')">
        <img src="{pkmnimgfolder if config.get(POKE_TYPE, True) else pkmnimgfolder_B}/{egg_name}.webp" alt="Egg"/>
        <div class="egg-card-level">Lv. {int(egg_level)}</div>
    </div>
    '''
    return html
