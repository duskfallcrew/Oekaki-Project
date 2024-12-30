# ui_toolbar.py
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QSlider, QLabel, QComboBox
from PyQt6.QtCore import Qt

def setup_toolbar(app, side_toolbar):
        color_button = QPushButton("Change Color")
        color_button.clicked.connect(app.change_color)
        side_toolbar.addWidget(color_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(lambda: app.canvas.clear_canvas())
        side_toolbar.addWidget(clear_button)

        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(lambda: app.canvas.undo())
        side_toolbar.addWidget(undo_button)

        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 50)
        size_slider.setValue(5)
        size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        size_slider.valueChanged.connect(lambda value: app.change_brush_size(value))
        side_toolbar.addWidget(QLabel("Brush Size"))
        side_toolbar.addWidget(size_slider)

        shape_combo = QComboBox()
        shape_combo.addItems(["Round", "Square"])
        shape_combo.currentTextChanged.connect(lambda shape: app.change_brush_shape(shape))
        side_toolbar.addWidget(QLabel("Brush Shape"))
        side_toolbar.addWidget(shape_combo)

        tool_combo = QComboBox()
        tool_combo.addItems(["Pencil", "Pen", "Ink", "Paint", "Airbrush", "Eraser", "Rectangle", "Blender", "Text"])
        tool_combo.currentTextChanged.connect(lambda tool: app.change_tool(tool))
        side_toolbar.addWidget(QLabel("Tool"))
        side_toolbar.addWidget(tool_combo)

        custom_brush_button = QPushButton("Load Custom Brush")
        custom_brush_button.clicked.connect(app.load_custom_brush)
        side_toolbar.addWidget(custom_brush_button)

        canvas_size_combo = QComboBox()
        canvas_size_combo.addItems(["800x600", "1024x768", "1280x720", "1920x1080", "600x600", "512x512", "1024x1024"])
        canvas_size_combo.currentTextChanged.connect(lambda size: app.change_canvas_size(size))
        side_toolbar.addWidget(QLabel("Canvas Size"))
        side_toolbar.addWidget(canvas_size_combo)
        
        # Ghost opacity slider
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(int(app.canvas.ghost_opacity * 100))
        opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        opacity_slider.valueChanged.connect(lambda value: app.change_ghost_opacity(value))
        side_toolbar.addWidget(QLabel("Ghost Opacity"))
        side_toolbar.addWidget(opacity_slider)
        
        # Ghost toggle button
        app.ghost_toggle_button = QPushButton("Ghosting On")
        app.ghost_toggle_button.setCheckable(True) # Add checkable so it stays down.
        app.ghost_toggle_button.clicked.connect(app.toggle_ghosting)
        side_toolbar.addWidget(app.ghost_toggle_button)

        side_toolbar.addStretch(1)