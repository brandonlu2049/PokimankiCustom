# -*- coding: utf-8 -*-

# Pokémanki - Message Handler Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import Any, Tuple

from ..config import get_synced_conf
from ..display import pokemon_display

# Global variable for stats dialog
statsDialog = None

def reset_message_handler_globals():
    """Reset message handler global variables."""
    global statsDialog
    statsDialog = None

def message_handler(
    handled: Tuple[bool, Any], message: str, context: Any
) -> Tuple[bool, Any]:
    """Handle pycmd messages from the web interface."""
    # https://github.com/ankitects/anki/blob/main/qt/tools/genhooks_gui.py#L618
    if not message.startswith("Pokemanki#"):
        return handled
    if message == "Pokemanki#currentDeck":
        html = pokemon_display(False).replace("`", "'")
    elif message == "Pokemanki#wholeCollection":
        html = pokemon_display(True).replace("`", "'")
    else:
        starts = "Pokemanki#search#"
        term = message[len(starts) :]
        # Todo: implement selective
        return (True, None)
    statsDialog.form.web.eval(f"Pokemanki.setPokemanki(`{html}`)")
    return (True, None)
