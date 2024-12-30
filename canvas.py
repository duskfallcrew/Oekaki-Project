# canvas.py
from PyQt6.QtCore import Qt, QPoint, QDateTime, QSize, QPointF
from PyQt6.QtGui import QPainter, QPen, QPixmap, QColor, QBrush, QPainterPath, QImage, QFont, QCursor
from PyQt6.QtWidgets import QWidget
import math
from brushes import draw_brushes

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
      self.draw(current_point)
    
    def draw_blender(self, current_point):
      painter = QPainter(self.image)
      painter.setRenderHint(self.render_hint)
      
      brush_size_pixels = self.brush_size
      for color in self.blender_palette:
        pen = QPen(color, self.brush_size, Qt.PenStyle.SolidLine, self.brush_shape, Qt.PenJoinStyle.RoundJoin)
        pen.setColor(QColor(color.red(), color.green(), color.blue(), 50))
        painter.setPen(pen)
        painter.drawEllipse(int(cursor_point.x() - brush_half_size), int(cursor_point.y() - brush_half_size),
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
        draw_brushes(self, cursor_point)

    def set_brush_color(self, color):
        self.brush_color = color

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_shape(self, shape):
       if shape == "round":
            self.brush_shape = Qt.PenCapStyle.RoundCap
       elif shape == "square":
            self.brush_shape = Qt.PenCapStyle.SquareCap

    def set_tool(self, tool):
        self.tool = tool
        self.set_cursor_for_tool()

    def set_custom_brush(self, brush_path):
        self.custom_brush = QPixmap(brush_path)

    def clear_canvas(self):
      self.save_undo_state()
      self.image.fill(Qt.GlobalColor.white)
      self.update()

    def save_canvas(self, path):
        self.image.save(path, "PNG")

    def save_undo_state(self):
        if self.ghost_opacity != 0 and len(self.canvas_history) > 0:
            # Add basic ghosting effect
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
    
    def set_cursor_for_tool(self):
        if self.tool == "text":
          self.setCursor(Qt.CursorShape.IBeamCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_canvas_size(self, width, height):
        self.setFixedSize(width, height)
        self.image = QPixmap(width, height)
        self.image.fill(Qt.GlobalColor.white)
        self.update()