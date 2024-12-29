# ui_text.py
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QLineEdit

def setup_text_input(app, right_side_layout):
        # Text Input Area
        app.text_input = QTextEdit()
        app.text_input.setPlaceholderText("Describe your drawing in a few words")
        app.text_input.setFixedHeight(100)  # Set a fixed height for the text box
        right_side_layout.addWidget(QLabel("Image Description:"))
        right_side_layout.addWidget(app.text_input)
        
        app.canvas_text_input = QLineEdit() # Add the text input method.
        app.canvas_text_input.setPlaceholderText("Enter text here")
        app.canvas_text_input.textChanged.connect(app.change_canvas_text)
        right_side_layout.addWidget(QLabel("Text to Draw"))
        right_side_layout.addWidget(app.canvas_text_input)
