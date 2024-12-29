import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
                             QColorDialog, QSlider, QLabel, QFileDialog, QComboBox, QFrame, QTextEdit,
                             QMessageBox, QGridLayout, QScrollArea, QLineEdit)
from PyQt6.QtGui import QPainter, QPen, QPixmap, QColor, QBrush, QPainterPath, QImage, QFont
from PyQt6.QtCore import Qt, QPoint, QDateTime, QSize, QPointF
import math

class OekakiCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QPixmap(800, 600)
        self.image.fill(Qt.GlobalColor.white)
        self.undo_stack = []
        self.drawing = False
        self.brush_size = 5
        self.brush_color = QColor(Qt.GlobalColor.black)  # Start with a QColor
        self.brush_shape = Qt.PenCapStyle.RoundCap
        self.last_point = QPointF()  # Stored as QPointF now
        self.tool = "pencil"
        self.custom_brush = None
        self.current_shape = None # Added for shapes
        self.shape_start = None # Added for shapes
        self.canvas_history = [] # Added for shape tracking
        self.canvas_history.append(self.image.copy())
        self.path = QPainterPath() # For smooth lines
        self.setMouseTracking(True) # Added Mouse Tracking.
        self.render_hint = QPainter.RenderHint.Antialiasing
        self.ghost_opacity = 0.2 # Default ghosting opacity
        self.blender_palette = [] # Added blender palette
        self.text_input = "" # Added for text tool
        self.font = QFont("Arial", 12)  # default font
        self.font.setPixelSize(20)


    def paintEvent(self, event):
      canvas_painter = QPainter(self)
      canvas_painter.setRenderHint(self.render_hint) # Set antialiasing
      canvas_painter.drawPixmap(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position()  # Correctly set to QPointF
            self.save_undo_state() # Undo point
            if self.tool == "rectangle":
                self.shape_start = event.position().toPoint()
            elif self.tool in ["pencil", "pen", "ink", "paint"]: # Added new pathing for smooth lines
                self.path.moveTo(event.position())
            elif self.tool == "blender":
              self.pick_blender_color(event.position()) # Get the color to blend.
            elif self.tool == "text":
                self.draw_text(event.position())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            if self.tool == "rectangle":
              self.draw_shape(event.position().toPoint())
            elif self.tool in ["pencil", "pen", "ink", "paint"]:
                self.draw_smooth_line(event.position())
            elif self.tool == "blender":
              self.draw_blender(event.position())
            else:
              self.draw(event.position().toPoint())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False
            if self.tool == "rectangle":
                self.shape_start = None # clear the point so we can make a new shape.
            elif self.tool in ["pencil", "pen", "ink", "paint"]:
              self.path = QPainterPath() # Clear the path

    def pick_blender_color(self, position):
      image = self.image.toImage()
      if image and position.x() < self.image.width() and position.y() < self.image.height() and position.x() >= 0 and position.y() >= 0:
        pixel_color = image.pixelColor(position.toPoint())
        if len(self.blender_palette) < 10:
          self.blender_palette.append(pixel_color)
        else:
          self.blender_palette.pop(0)
          self.blender_palette.append(pixel_color)
        self.update()

    def draw_shape(self, current_point):
          if self.shape_start: # if we have a previous point
            self.image = self.canvas_history[-1].copy() # set the image as the most recent image
            painter = QPainter(self.image)
            painter.setRenderHint(self.render_hint)
            pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(QBrush(self.brush_color)) # Set the fill color if you want
            painter.drawRect(self.shape_start.x(), self.shape_start.y(),
                             current_point.x() - self.shape_start.x(), current_point.y() - self.shape_start.y())
            self.update()
            
    def draw_smooth_line(self, current_point):
      painter = QPainter(self.image)
      painter.setRenderHint(self.render_hint)
      pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
      painter.setPen(pen)

      control_point = (self.last_point + current_point) / 2 # Add the QPointF objects directly
      self.path.quadTo(control_point, current_point)

      painter.drawPath(self.path)
      self.last_point = current_point # Set the last point as a QPointF
      self.update()
    
    def draw_blender(self, current_point):
      painter = QPainter(self.image)
      painter.setRenderHint(self.render_hint)
      
      brush_size_pixels = self.brush_size
      for color in self.blender_palette:
        pen = QPen(color, self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
        pen.setColor(QColor(color.red(), color.green(), color.blue(), 50))
        painter.setPen(pen)
        painter.drawEllipse(current_point.x() - brush_size_pixels // 2, current_point.y() - brush_size_pixels // 2,
                            brush_size_pixels, brush_size_pixels)

      self.last_point = current_point
      self.update()
    
    def draw_text(self, current_point):
        painter = QPainter(self.image)
        painter.setRenderHint(self.render_hint)
        painter.setFont(self.font)
        painter.setPen(self.brush_color)
        painter.drawText(current_point.toPoint(), self.text_input)
        self.last_point = current_point
        self.update()

    def draw(self, cursor_point):
      if self.tool == "pencil" or self.tool == "pen":
        self.draw_pencil(cursor_point)
      if self.tool == "ink":
        self.draw_ink(cursor_point)
      elif self.tool == "paint":
          self.draw_line(cursor_point)
      elif self.tool == "airbrush" and self.custom_brush:
        self.draw_custom_brush(cursor_point)
      elif self.tool == "eraser":
          self.draw_eraser(cursor_point)

    def draw_pencil(self, cursor_point):
      painter = QPainter(self.image)
      painter.setRenderHint(self.render_hint)
      pen = QPen(self.brush_color, self.brush_size / 2, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
      painter.setPen(pen)
      painter.drawPath(self.path)
      self.last_point = cursor_point
      self.update()

    def draw_ink(self, cursor_point):
      painter = QPainter(self.image)
      painter.setRenderHint(self.render_hint)
      pen = QPen(self.brush_color.darker(), self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
      painter.setPen(pen)
      painter.drawPath(self.path)
      self.last_point = cursor_point
      self.update()
      
    def draw_eraser(self, cursor_point):
        painter = QPainter(self.image)
        painter.setRenderHint(self.render_hint)
        pen = QPen(Qt.GlobalColor.white, self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawLine(self.last_point.toPoint(), cursor_point)
        self.last_point = cursor_point
        self.update()

    def draw_line(self, cursor_point):
      painter = QPainter(self.image)
      painter.setRenderHint(self.render_hint)
      pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
      painter.setPen(pen)
      painter.drawPath(self.path) # Use the painter path
      self.last_point = cursor_point
      self.update()
    
    def draw_custom_brush(self, cursor_point):
        painter = QPainter(self.image)
        brush_half_size = self.brush_size // 2
        painter.setRenderHint(self.render_hint)
        painter.drawPixmap(cursor_point.x() - brush_half_size, cursor_point.y() - brush_half_size,
                            self.custom_brush.scaled(self.brush_size, self.brush_size))
        self.last_point = cursor_point
        self.update()

    def set_brush_color(self, color):
        self.brush_color = color

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_shape(self, shape):
        self.brush_shape = shape

    def set_tool(self, tool):
        self.tool = tool

    def set_custom_brush(self, brush_path):
        self.custom_brush = QPixmap(brush_path)

    def clear_canvas(self):
      self.save_undo_state()
      self.image.fill(Qt.GlobalColor.white)
      self.update()

    def save_canvas(self, path):
        self.image.save(path, "PNG")

    def save_undo_state(self):
        
        # Add basic ghosting effect
        if len(self.canvas_history) > 0:
          ghost_image = self.canvas_history[-1].copy()
          ghost_painter = QPainter(ghost_image)
          ghost_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
          ghost_painter.setOpacity(self.ghost_opacity)
          ghost_painter.drawPixmap(self.rect(), self.image, self.image.rect())
          ghost_painter.end()

          self.image = ghost_image

        self.canvas_history.append(self.image.copy())
        self.undo_stack.append(self.image.copy())
        if len(self.undo_stack) > 10:  # Limit undo stack to 10
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.image = self.undo_stack.pop()
            self.update()

    def set_canvas_size(self, width, height):
        self.setFixedSize(width, height)
        self.image = QPixmap(width, height)
        self.image.fill(Qt.GlobalColor.white)
        self.update()

class OekakiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Earth & Dusk's Oekaki App")
        self.canvas = OekakiCanvas()
        self.init_ui()
        self.set_fixed_size_based_on_canvas()
        self.selected_color = QColor(Qt.GlobalColor.black)
        self.blender_colors = [] # Initialize blender colors

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Side toolbar
        side_toolbar = QVBoxLayout()

        # Color Palette
        color_palette_layout = QVBoxLayout()
        color_palette_label = QLabel("Color Palette")
        color_palette_layout.addWidget(color_palette_label)

        self.color_buttons = []
        color_grid = QGridLayout() # Use grid layout for buttons
        preset_colors = [Qt.GlobalColor.black, Qt.GlobalColor.red, Qt.GlobalColor.green,
                         Qt.GlobalColor.blue, Qt.GlobalColor.yellow, Qt.GlobalColor.white]
        row = 0
        col = 0
        for color in preset_colors:
            color_button = QPushButton()
            color_button.setFixedSize(25, 25)
            color_button.setStyleSheet(f"background-color: {color.name};")
            color_button.clicked.connect(lambda c=color, this=self: this.set_selected_color(c))
            self.color_buttons.append(color_button)
            color_grid.addWidget(color_button, row, col)
            col += 1
            if col == 3:
              col = 0
              row += 1
        color_palette_layout.addLayout(color_grid)
        side_toolbar.addLayout(color_palette_layout)

        # Color Selection
        color_button = QPushButton("Change Color")
        color_button.clicked.connect(self.change_color)
        side_toolbar.addWidget(color_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.canvas.clear_canvas)
        side_toolbar.addWidget(clear_button)

        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.canvas.undo)
        side_toolbar.addWidget(undo_button)

        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 50)
        size_slider.setValue(5)
        size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        size_slider.valueChanged.connect(self.change_brush_size)
        side_toolbar.addWidget(QLabel("Brush Size"))
        side_toolbar.addWidget(size_slider)

        shape_combo = QComboBox()
        shape_combo.addItems(["Round", "Square"])
        shape_combo.currentTextChanged.connect(self.change_brush_shape)
        side_toolbar.addWidget(QLabel("Brush Shape"))
        side_toolbar.addWidget(shape_combo)

        tool_combo = QComboBox()
        tool_combo.addItems(["Pencil", "Pen", "Ink", "Paint", "Airbrush", "Eraser", "Rectangle", "Blender", "Text"])
        tool_combo.currentTextChanged.connect(self.change_tool)
        side_toolbar.addWidget(QLabel("Tool"))
        side_toolbar.addWidget(tool_combo)

        custom_brush_button = QPushButton("Load Custom Brush")
        custom_brush_button.clicked.connect(self.load_custom_brush)
        side_toolbar.addWidget(custom_brush_button)

        canvas_size_combo = QComboBox()
        canvas_size_combo.addItems(["800x600", "1024x768", "1280x720", "1920x1080", "600x600", "512x512", "1024x1024"])
        canvas_size_combo.currentTextChanged.connect(self.change_canvas_size)
        side_toolbar.addWidget(QLabel("Canvas Size"))
        side_toolbar.addWidget(canvas_size_combo)
        
        # Ghost opacity slider
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(int(self.canvas.ghost_opacity * 100))
        opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        opacity_slider.valueChanged.connect(self.change_ghost_opacity)
        side_toolbar.addWidget(QLabel("Ghost Opacity"))
        side_toolbar.addWidget(opacity_slider)
        
        # Ghost toggle button
        self.ghost_toggle_button = QPushButton("Ghosting On")
        self.ghost_toggle_button.setCheckable(True) # Add checkable so it stays down.
        self.ghost_toggle_button.clicked.connect(self.toggle_ghosting)
        side_toolbar.addWidget(self.ghost_toggle_button)

        side_toolbar.addStretch(1)

        main_layout.addLayout(side_toolbar)

        # Canvas in the center
        main_layout.addWidget(self.canvas, 2) # stretch factor 2 so it takes more space

        # Right layout for color mixing area and text input area
        right_side_layout = QVBoxLayout()
        
        # Blender palette area
        blender_layout = QVBoxLayout()
        blender_label = QLabel("Blender Palette")
        blender_layout.addWidget(blender_label)
        self.blender_buttons = []
        blender_grid = QGridLayout()
        for i in range(10):
          blender_button = QPushButton()
          blender_button.setFixedSize(25,25)
          blender_button.setStyleSheet("background-color: white;")
          blender_grid.addWidget(blender_button, i // 2, i % 2)
          self.blender_buttons.append(blender_button)
        blender_layout.addLayout(blender_grid)
        right_side_layout.addLayout(blender_layout)

        # Color Mixing Area
        color_mixing_layout = QVBoxLayout()
        self.color_mixing_area = QFrame()
        self.color_mixing_area.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.color_mixing_area.setLineWidth(2)
        self.color_mixing_area.setStyleSheet("background-color: white;")
        color_mixing_layout.addWidget(self.color_mixing_area)
        self.color_mixing_area.setFixedSize(200, 200)
        self.color_mixing_area.setToolTip("Use this area to mix colors")
        right_side_layout.addLayout(color_mixing_layout)

        # Text Input Area
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Describe your drawing in a few words")
        self.text_input.setFixedHeight(100)  # Set a fixed height for the text box
        right_side_layout.addWidget(QLabel("Image Description:"))
        right_side_layout.addWidget(self.text_input)
        
        self.canvas_text_input = QLineEdit() # Add the text input method.
        self.canvas_text_input.setPlaceholderText("Enter text here")
        self.canvas_text_input.textChanged.connect(self.change_canvas_text)
        right_side_layout.addWidget(QLabel("Text to Draw"))
        right_side_layout.addWidget(self.canvas_text_input)

        # Save Button Area
        save_area_layout = QHBoxLayout()
        save_button = QPushButton("Save Image & Label")
        save_button.clicked.connect(self.save_image_and_label)
        save_area_layout.addWidget(save_button)

        right_side_layout.addLayout(save_area_layout)
        main_layout.addLayout(right_side_layout, 1) # stretch factor 1


    def change_color(self):
        color = QColorDialog.getColor(initial=self.selected_color)
        if color.isValid():
            self.set_selected_color(color)
        self.canvas.set_brush_color(self.selected_color) # Make sure the brush color is updated.

    def set_selected_color(self, color):
      self.selected_color = color
      self.canvas.set_brush_color(color)
      # Update Color button:
      #self.update_color_buttons() # REMOVE THIS LINE

    def update_color_buttons(self):
       pass # REMOVE ALL OF THIS METHOD

    def change_brush_size(self, size):
        self.canvas.set_brush_size(size)

    def change_brush_shape(self, shape):
        shape = shape.lower()
        if shape == "round":
            self.canvas.set_brush_shape(Qt.PenCapStyle.RoundCap)
        elif shape == "square":
            self.canvas.set_brush_shape(Qt.PenCapStyle.SquareCap)

    def change_tool(self, tool):
        self.canvas.set_tool(tool.lower())

    def load_custom_brush(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Custom Brush", "",
                                                   "Image Files (*.png *.jpg *.bmp);;All Files (*)")
        if file_path:
            self.canvas.set_custom_brush(file_path)

    def save_image_and_label(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please add a description to the textbox.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image & Label", "", "PNG Files (*.png);;All Files (*)")

        if file_path:
            # Generate the image name and description name
            base_name = os.path.splitext(file_path)[0]

            image_path = f"{base_name}.png"
            description_path = f"{base_name}.txt"

            # Save image and label
            self.canvas.save_canvas(image_path)

            with open(description_path, "w") as f:
                f.write(text)

            QMessageBox.information(self, "Success!",
                                    f"Image and label saved to {os.path.basename(os.path.dirname(file_path))}\\{os.path.basename(base_name)}.[png or txt]")

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
