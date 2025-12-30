# -*- coding: utf-8 -*-

# Pokémanki - Pokemon Customization Dialog
# Copyright (C) 2022 Exkywor and zjosua

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Pokemon Customization Dialog - Allows users to customize individual Pokemon
"""

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QPixmap, Qt, QFrame
)
from aqt.utils import tooltip

from ..helpers.config import get_synced_conf, save_synced_conf
from ..helpers.pokemon_helpers import get_pokemon_by_id, set_pokemon_by_id
from ..utils import pkmnimgfolder, pkmnimgfolder_B
from ..custom_py.path_manager import CustomDialog

from ..features.customization import save_changes


class PokemonCustomizationDialog(CustomDialog):
    """Dialog for customizing individual Pokemon"""

    def __init__(self, pokemon_id: str, parent=None):
        super().__init__(parent or mw)
        self.pokemon_id = pokemon_id
        self.pokemon_data = get_pokemon_by_id(pokemon_id)
        
        if not self.pokemon_data:
            tooltip("Pokemon not found!")
            self.close()
            return
            
        self.setup_ui()
        self.load_current_values()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(f"Customize Pokémon")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Pokemon header with image and name
        header_layout = QHBoxLayout()
        
        # Pokemon image
        self.pokemon_image = QLabel()
        config = mw.addonManager.getConfig(__name__)
        poke_type = config.get("PokeType", True) if config else True
        
        img_folder = pkmnimgfolder if poke_type else pkmnimgfolder_B
        img_path = f"{img_folder}/{self.pokemon_data['name']}.webp"
        
        # We'll set a placeholder size for the image label
        self.pokemon_image.setFixedSize(96, 96)
        self.pokemon_image.setStyleSheet("border: 1px solid #ccc; border-radius: 8px;")
        self.pokemon_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(self.pokemon_image)
        
        # Pokemon info
        info_layout = QVBoxLayout()
        
        name = self.pokemon_data.get("nickname") or self.pokemon_data.get("name", "Unknown")
        self.name_label = QLabel(f"<h2>{name}</h2>")
        info_layout.addWidget(self.name_label)
        
        level = self.pokemon_data.get("level", 0)
        self.level_label = QLabel(f"Level: {int(level)}")
        info_layout.addWidget(self.level_label)
        
        info_layout.addStretch()
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Nickname section
        nickname_group = QGroupBox("Nickname")
        nickname_layout = QHBoxLayout()
        
        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("Enter a nickname...")
        self.nickname_input.setMaxLength(20)
        nickname_layout.addWidget(self.nickname_input)
        
        self.clear_nickname_btn = QPushButton("Clear")
        self.clear_nickname_btn.clicked.connect(self.clear_nickname)
        nickname_layout.addWidget(self.clear_nickname_btn)
        
        nickname_group.setLayout(nickname_layout)
        layout.addWidget(nickname_group)
        
        # Items section
        items_group = QGroupBox("Items")
        items_layout = QVBoxLayout()
        
        self.everstone_checkbox = QCheckBox("Everstone (Prevents evolution)")
        items_layout.addWidget(self.everstone_checkbox)
        
        self.megastone_checkbox = QCheckBox("Mega Stone (Enables Mega Evolution)")
        items_layout.addWidget(self.megastone_checkbox)
        
        self.alolan_checkbox = QCheckBox("Alolan Passport (Alolan form)")
        items_layout.addWidget(self.alolan_checkbox)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_changes)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def clear_nickname(self):
        """Clear the nickname input"""
        self.nickname_input.clear()

    def load_current_values(self):
        """Load current pokemon values into the form"""
        # Load nickname
        nickname = self.pokemon_data.get("nickname", "")
        self.nickname_input.setText(nickname if nickname else "")
        
        # Load items status
        self.everstone_checkbox.setChecked(self.pokemon_data["items"]["everstone"])
        self.megastone_checkbox.setChecked(self.pokemon_data["items"]["megastone"])
        self.alolan_checkbox.setChecked(self.pokemon_data["items"]["alolan"])

    def _save_changes(self):
        save_changes(
            self.pokemon_id, 
            self.nickname_input.text().strip(), 
            self.everstone_checkbox.isChecked(), 
            self.megastone_checkbox.isChecked(), 
            self.alolan_checkbox.isChecked()
        )
        self.accept()

def open_pokemon_customization(pokemon_id: str):
    """Open the customization dialog for a specific pokemon"""
    dialog = PokemonCustomizationDialog(pokemon_id, mw)
    dialog.exec()

