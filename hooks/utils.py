# -*- coding: utf-8 -*-

# Pokémanki - Hook Utilities Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

def reset_all_main_globals():
    """Reset all main global variables across modules."""
    from .menu import reset_menu_globals
    from .overview import reset_overview_globals
    from .message_handler import reset_message_handler_globals
    
    reset_menu_globals()
    reset_overview_globals()
    reset_message_handler_globals()

def reset_utils_global_variables():
    """Reset utils global variables."""
    from ..utils import reset_utils_global
    reset_utils_global()
