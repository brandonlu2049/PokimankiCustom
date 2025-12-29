# -*- coding: utf-8 -*-

# Pokémanki - Stats Module
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import aqt
from ..utils import addon_dir

def _onStatsOpen(dialog: aqt.stats.NewDeckStats) -> None:
    """Internal stats dialog handler."""
    from .message_handler import statsDialog
    # Set the global statsDialog reference
    import sys
    message_handler_module = sys.modules[__name__.replace('.stats', '.message_handler')]
    message_handler_module.statsDialog = dialog
    
    js = (addon_dir / "web.js").read_text(encoding="utf-8")
    dialog.form.web.eval(js)

def onStatsOpen(statsDialog: aqt.stats.NewDeckStats) -> None:
    """Handle stats dialog opening."""
    statsDialog.form.web.loadFinished.connect(lambda _: _onStatsOpen(statsDialog))
