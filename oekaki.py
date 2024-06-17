import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QColorDialog, QSlider, QLabel, QFileDialog, QComboBox, QFrame)
from PyQt6.QtGui import QPainter, QPen, QMouseEvent, QPixmap, QColor, QImage, QIcon
from PyQt6.QtCore import Qt, QPoint

class OekakiCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QPixmap(800, 600)
        self.image.fill(Qt.GlobalColor.white)
        self.undo_stack = []
        self.drawing = False
        self.brush_size = 5
        self.brush_color = Qt.GlobalColor.black
        self.brush_shape = Qt.PenCapStyle.RoundCap
        self.last_point = QPoint()
        self.tool = "pencil"
        self.custom_brush = None

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawPixmap(self.rect(), self.image, self.image.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.save_undo_state()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drawing:
            painter = QPainter(self.image)
            pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            if self.custom_brush:
                painter.drawPixmap(event.position().toPoint(), self.custom_brush.scaled(self.brush_size, self.brush_size))
            else:
                painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

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
        self.undo_stack.append(self.image.copy())
        if len(self.undo_stack) > 10:  # Limit undo stack to 10
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.image = self.undo_stack.pop()
            self.update()

    def set_canvas_size(self, width, height):
        self.image = QPixmap(width, height)
        self.image.fill(Qt.GlobalColor.white)
        self.update()

class OekakiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Earth & Dusk's Oekaki App")
        self.canvas = OekakiCanvas()
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        color_button = QPushButton("Change Color")
        color_button.clicked.connect(self.change_color)
        button_layout.addWidget(color_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.canvas.clear_canvas)
        button_layout.addWidget(clear_button)

        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.canvas.undo)
        button_layout.addWidget(undo_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_image)
        button_layout.addWidget(save_button)

        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 50)
        size_slider.setValue(5)
        size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        size_slider.valueChanged.connect(self.change_brush_size)
        button_layout.addWidget(QLabel("Brush Size"))
        button_layout.addWidget(size_slider)

        shape_combo = QComboBox()
        shape_combo.addItems(["Round", "Square"])
        shape_combo.currentTextChanged.connect(self.change_brush_shape)
        button_layout.addWidget(QLabel("Brush Shape"))
        button_layout.addWidget(shape_combo)

        tool_combo = QComboBox()
        tool_combo.addItems(["Pencil", "Pen", "Ink", "Paint", "Airbrush"])
        tool_combo.currentTextChanged.connect(self.change_tool)
        button_layout.addWidget(QLabel("Tool"))
        button_layout.addWidget(tool_combo)

        custom_brush_button = QPushButton("Load Custom Brush")
        custom_brush_button.clicked.connect(self.load_custom_brush)
        button_layout.addWidget(custom_brush_button)

        canvas_size_combo = QComboBox()
        canvas_size_combo.addItems(["800x600", "1024x768", "1280x720", "1920x1080", "600x600"])
        canvas_size_combo.currentTextChanged.connect(self.change_canvas_size)
        button_layout.addWidget(QLabel("Canvas Size"))
        button_layout.addWidget(canvas_size_combo)

        layout.addWidget(self.canvas)

        # Color Mixing Area
        self.color_mixing_area = QFrame()
        self.color_mixing_area.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.color_mixing_area.setLineWidth(2)
        self.color_mixing_area.setStyleSheet("background-color: white;")
        layout.addWidget(self.color_mixing_area)
        self.color_mixing_area.setFixedSize(200, 200)
        self.color_mixing_area.setToolTip("Use this area to mix colors")

    def change_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_brush_color(color)

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
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Custom Brush", "", "Image Files (*.png *.jpg *.bmp);;All Files (*)")
        if file_path:
            self.canvas.set_custom_brush(file_path)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;All Files (*)")
        if file_path:
            self.canvas.save_canvas(file_path)

    def change_canvas_size(self, size):
        width, height = map(int, size.split('x'))
        self.canvas.set_canvas_size(width, height)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OekakiApp()
    window.show()
    sys.exit(app.exec())
