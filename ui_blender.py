# ui_blender.py
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGridLayout, QPushButton

def setup_blender_palette(app, right_side_layout):
        # Blender palette area
        blender_layout = QVBoxLayout()
        blender_label = QLabel("Blender Palette")
        blender_layout.addWidget(blender_label)
        app.blender_buttons = []
        blender_grid = QGridLayout()
        for i in range(10):
          blender_button = QPushButton()
          blender_button.setFixedSize(25,25)
          blender_button.setStyleSheet("background-color: white;")
          blender_grid.addWidget(blender_button, i // 2, i % 2)
          app.blender_buttons.append(blender_button)
        blender_layout.addLayout(blender_grid)
        right_side_layout.addLayout(blender_layout)
