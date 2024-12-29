# ui_palette.py
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

def setup_color_palette(app, side_toolbar):
        # Color Palette
        color_palette_layout = QVBoxLayout()
        color_palette_label = QLabel("Color Palette")
        color_palette_layout.addWidget(color_palette_label)

        app.color_buttons = []
        color_grid = QGridLayout() # Use grid layout for buttons
        preset_colors = [Qt.GlobalColor.black, Qt.GlobalColor.red, Qt.GlobalColor.green,
                         Qt.GlobalColor.blue, Qt.GlobalColor.yellow, Qt.GlobalColor.white]
        row = 0
        col = 0
        for color in preset_colors:
            color_button = QPushButton()
            color_button.setFixedSize(25, 25)
            color_button.setStyleSheet(f"background-color: {color.name};")
            color_button.clicked.connect(lambda c=color, this=app: this.set_selected_color(c))
            app.color_buttons.append(color_button)
            color_grid.addWidget(color_button, row, col)
            col += 1
            if col == 3:
              col = 0
              row += 1
        color_palette_layout.addLayout(color_grid)
        side_toolbar.addLayout(color_palette_layout)
        
def set_selected_color(app, color):
      app.selected_color = color
      app.canvas.set_brush_color(color)
