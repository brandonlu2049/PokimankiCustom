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

import bisect
import os
import random
import time
from datetime import datetime, timedelta

from aqt import mw
from aqt.webview import AnkiWebView

from ..helpers.config import get_synced_conf, save_synced_conf
from ..helpers.pokemon_helpers import get_pokemon_by_id, set_pokemon_by_id, add_xp_to_pokemon, create_pokemon

# Constants
LEVEL_INCREMENT_AMOUNT_COMPLETION = 0.05
CARDS_PER_EGG = 300


def get_cards_since_last_session():
    """Get cards reviewed since last session end (syncs across devices via revlog)"""
    if not mw or not mw.col:
        return 0
    
    synced_config = get_synced_conf()
    last_session_time = synced_config.get("last_session_end_time", 0)
    
    count = mw.col.db.scalar(
        "SELECT COUNT() FROM revlog WHERE id > ?",
        last_session_time
    )
    return count or 0


def save_session_end_time():
    """Save current time as last session end (in milliseconds for revlog comparison)"""
    save_synced_conf("last_session_end_time", int(time.time() * 1000))


def pokemon_finish_session(*args, **kwargs):    
    """Called when a study session ends to calculate and award XP"""

    if mw and mw.col:
        synced_config_data = get_synced_conf()
        
        # Get cards reviewed since last session (from synced revlog - works across devices)
        cards_since_last_session = get_cards_since_last_session()
        
        # Initialize card_counter if it doesn't exist (for backward compatibility)
        if "card_counter" not in synced_config_data:
            synced_config_data["card_counter"] = 0
        
        # Add cards from this session to the persistent counter
        # card_counter tracks remaining cards after subtracting eggs/trades earned
        card_counter = synced_config_data["card_counter"] + cards_since_last_session
        
        print(f"Congratulations! Cards studied this session (across all devices): {cards_since_last_session}")
        print(f"Current egg counter (before rewards): {card_counter}")
        
        current_pokemon_id = synced_config_data["current_pokemon_id"]
        current_pokemon = get_pokemon_by_id(current_pokemon_id)

        print(f"Granting: {cards_since_last_session * LEVEL_INCREMENT_AMOUNT_COMPLETION} XP for finishing the study session!")
        add_xp_to_pokemon(current_pokemon, cards_since_last_session * LEVEL_INCREMENT_AMOUNT_COMPLETION)
        set_pokemon_by_id(current_pokemon_id, current_pokemon)

        # Calculate eggs based on persistent counter
        eggs_earned = int(card_counter // CARDS_PER_EGG)
        print(f"You received {eggs_earned} eggs! for reviewing {card_counter} cards total!")

        thresholds = [30, 50, 70, 80, 90, 99]
        rarities = ["F", "E", "D", "C", "B", "A", "S"]
        for _ in range(eggs_earned):
            rarity_level = random.randint(0, 100)
            rarity = rarities[bisect.bisect_left(thresholds, rarity_level)]
            synced_config_data["pokemon_list"].append(create_pokemon(name="Egg", level=1, rarity=rarity, nickname=None))
        save_synced_conf("pokemon_list", synced_config_data["pokemon_list"])

        # Calculate trade refresh counter
        trade_refreshes_earned = int(card_counter // CARDS_PER_EGG)
        print(f"You received {trade_refreshes_earned} trade refreshes! for reviewing {card_counter} cards total!")
        if "trade_refresh_counter" not in synced_config_data:
            synced_config_data["trade_refresh_counter"] = 0
        trade_refresh_counter = synced_config_data["trade_refresh_counter"]
        trade_refresh_counter += trade_refreshes_earned
        save_synced_conf("trade_refresh_counter", trade_refresh_counter)
        
        # Subtract the cards used for eggs/trades from card_counter (keep the remainder)
        remaining_card_counter = card_counter - (eggs_earned * CARDS_PER_EGG)
        save_synced_conf("card_counter", remaining_card_counter)
        print(f"Remaining card counter (after rewards): {remaining_card_counter}")
        
        # Save the current time so next session knows where to start counting from
        save_session_end_time()
        
    return
