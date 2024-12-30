# ui_main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFileDialog, QColorDialog, QLineEdit, QTextEdit, QLabel, QPushButton
from PyQt6.QtCore import Qt
from canvas import OekakiCanvas
from ui_toolbar import setup_toolbar
from ui_palette import setup_color_palette, set_selected_color
from ui_text import setup_text_input
from ui_blender import setup_blender_palette
from ui_menus import setup_menus
from data_io import save_image_and_label
from color_utils import create_pen

class OekakiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oekaki: Draw your own Dataset App") # changed the title
        self.canvas = OekakiCanvas()
        self.selected_color = Qt.GlobalColor.black
        self.init_ui()
        self.set_fixed_size_based_on_canvas()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Side toolbar
        side_toolbar = QVBoxLayout()
        #setup_color_palette(self, side_toolbar) # REMOVED PALETTE
        setup_toolbar(self, side_toolbar)
        main_layout.addLayout(side_toolbar)

        # Canvas in the center
        main_layout.addWidget(self.canvas, 2) # stretch factor 2 so it takes more space

        # Right layout for color mixing area and text input area
        right_side_layout = QVBoxLayout()
        #setup_blender_palette(self, right_side_layout) # REMOVED BLENDER PALETTE
        
        # Text Input Area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Describe your drawing in a few words")
        self.text_input.setFixedHeight(100)  # Set a fixed height for the text box
        right_side_layout.addWidget(QLabel("Image Description:"))
        right_side_layout.addWidget(self.text_input)

        # Save Button Area
        save_area_layout = QHBoxLayout()
        save_button = QPushButton("Save Image & Label")
        save_button.clicked.connect(self.save_image_and_label)
        save_area_layout.addWidget(save_button)

        right_side_layout.addLayout(save_area_layout)
        main_layout.addLayout(right_side_layout, 1) # stretch factor 1
        
        # Setup the menus for the main window.
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False) # Fix for the mac menu.
        self.setMenuWidget(menu_bar) # Set the menu to be visible on Mac.
        setup_menus(self)


    def set_selected_color(self, color):
      self.selected_color = color
      self.canvas.set_brush_color(color)

    def change_color(self):
      color = QColorDialog.getColor(initial=self.selected_color)
      if color.isValid():
          self.set_selected_color(color)

    def change_brush_size(self, size):
      self.canvas.set_brush_size(size)

    def change_brush_shape(self, shape):
      self.canvas.set_brush_shape(shape)
    
    def change_tool(self, tool):
      self.canvas.set_tool(tool)
      self.canvas.set_cursor_for_tool()

    def load_custom_brush(self):
      file_path, _ = QFileDialog.getOpenFileName(self, "Load Custom Brush", "",
                                                   "Image Files (*.png *.jpg *.bmp);;All Files (*)")
      if file_path:
            self.canvas.set_custom_brush(file_path)

    def change_canvas_size(self, size):
      width, height = map(int, size.split('x'))
      self.canvas.set_canvas_size(width, height)
      self.set_fixed_size_based_on_canvas()

    def change_ghost_opacity(self, value):
      self.canvas.ghost_opacity = value / 100
      
    def toggle_ghosting(self):
      if self.ghost_toggle_button.isChecked():
        self.canvas.ghost_opacity = 0.2
        self.ghost_toggle_button.setText("Ghosting On")
      else:
        self.canvas.ghost_opacity = 0
        self.ghost_toggle_button.setText("Ghosting Off")
    
    def change_canvas_text(self, text):
        self.canvas.text_input = text

    def save_image_and_label(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please add a description to the textbox.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image & Label", "", "PNG Files (*.png);;All Files (*)")

        if file_path:
          save_image_and_label(self.canvas, text, file_path)
          

    def set_fixed_size_based_on_canvas(self):
        # Get the canvas size and set the main window size accordingly
        canvas_size = self.canvas.size()
        top_toolbar_height = 40  # Estimated height of top toolbar
        side_toolbar_width = 200  # Estimated width of side toolbar
        color_mixing_area_width = 200  # Fixed size as set
        right_area_width = 200  # Estimated width of right side area, adjust as needed
        margin = 20  # Margin to ensure the window is not too tight

        # Calculate total window size
        window_width = canvas_size.width() + side_toolbar_width + right_area_width + margin
        window_height = canvas_size.height() + top_toolbar_height + margin
        self.setMinimumSize(window_width, window_height)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OekakiApp()
    window.show()
    sys.exit(app.exec())