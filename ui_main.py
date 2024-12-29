import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt
from canvas import OekakiCanvas
from ui_toolbar import setup_toolbar
from ui_palette import setup_color_palette, set_selected_color
from ui_text import setup_text_input
from ui_blender import setup_blender_palette
from ui_menus import setup_menus
from data_io import save_image_and_label

class OekakiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Earth & Dusk's Oekaki App")
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
        setup_color_palette(self, side_toolbar)
        setup_toolbar(self, side_toolbar)
        main_layout.addLayout(side_toolbar)

        # Canvas in the center
        main_layout.addWidget(self.canvas, 2) # stretch factor 2 so it takes more space

        # Right layout for color mixing area and text input area
        right_side_layout = QVBoxLayout()
        setup_blender_palette(self, right_side_layout)
        setup_text_input(self, right_side_layout)
        main_layout.addLayout(right_side_layout, 1) # stretch factor 1
        
        # Setup the menus for the main window.
        setup_menus(self)


    def set_selected_color(self, color):
      self.selected_color = color
      self.canvas.set_brush_color(color)

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
