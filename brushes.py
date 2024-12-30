# brushes.py
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QPixmap
from PyQt6.QtCore import Qt, QPointF
from color_utils import create_pen

def draw_brushes(canvas, cursor_point):
  painter = QPainter(canvas.image)
  painter.setRenderHint(canvas.render_hint)

  if canvas.tool == "pencil" or canvas.tool == "pen":
      draw_pencil(painter, canvas, cursor_point, canvas.brush_color, canvas.brush_shape, canvas.brush_size)
  if canvas.tool == "ink":
      draw_ink(painter, canvas, cursor_point, canvas.brush_color, canvas.brush_shape, canvas.brush_size)
  elif canvas.tool == "paint":
      draw_line(painter, canvas, cursor_point, canvas.brush_color, canvas.brush_shape, canvas.brush_size)
  elif canvas.tool == "airbrush" and canvas.custom_brush:
      draw_custom_brush(painter, canvas, cursor_point)
  elif canvas.tool == "eraser":
      draw_eraser(painter, canvas, cursor_point)


def draw_pencil(painter, canvas, cursor_point, color, brush_shape, brush_size):
  pen = create_pen(color, brush_size / 2, brush_shape)
  painter.setPen(pen)
  painter.drawLine(canvas.last_point, cursor_point)
  canvas.last_point = cursor_point
  canvas.update()

def draw_ink(painter, canvas, cursor_point, color, brush_shape, brush_size):
  pen = create_pen(color.darker(), brush_size, brush_shape)
  painter.setPen(pen)
  painter.drawLine(canvas.last_point, cursor_point)
  canvas.last_point = cursor_point
  canvas.update()

def draw_eraser(painter, canvas, cursor_point):
    pen = create_pen(Qt.GlobalColor.white, canvas.brush_size, canvas.brush_shape)
    painter.setPen(pen)
    brush_half_size = canvas.brush_size // 2
    painter.drawEllipse(int(cursor_point.x() - brush_half_size), int(cursor_point.y() - brush_half_size),
                            canvas.brush_size, canvas.brush_size)
    canvas.last_point = cursor_point
    canvas.update()

def draw_line(painter, canvas, cursor_point, color, brush_shape, brush_size):
  pen = create_pen(color, brush_size, brush_shape)
  painter.setPen(pen)
  brush_half_size = brush_size // 2
  painter.drawEllipse(int(cursor_point.x() - brush_half_size), int(cursor_point.y() - brush_half_size),
                           brush_size, brush_size)
  canvas.last_point = cursor_point
  canvas.update()
    
def draw_custom_brush(painter, canvas, cursor_point):
    brush_half_size = canvas.brush_size // 2
    painter.drawPixmap(int(cursor_point.x() - brush_half_size), int(cursor_point.y() - brush_half_size),
                        canvas.custom_brush.scaled(canvas.brush_size, canvas.brush_size))
    canvas.last_point = cursor_point
    canvas.update()