# brushes.py
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QPointF

def draw_brushes(canvas, cursor_point):
  if canvas.tool == "pencil" or canvas.tool == "pen":
      draw_pencil(canvas, cursor_point)
  if canvas.tool == "ink":
    draw_ink(canvas, cursor_point)
  elif canvas.tool == "paint":
      draw_line(canvas, cursor_point)
  elif canvas.tool == "airbrush" and canvas.custom_brush:
    draw_custom_brush(canvas, cursor_point)
  elif canvas.tool == "eraser":
      draw_eraser(canvas, cursor_point)


def draw_pencil(canvas, cursor_point):
    painter = QPainter(canvas.image)
    painter.setRenderHint(canvas.render_hint)
    pen = QPen(canvas.brush_color, canvas.brush_size / 2, Qt.PenStyle.SolidLine, canvas.brush_shape, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawPath(canvas.path)
    canvas.last_point = cursor_point
    canvas.update()

def draw_ink(canvas, cursor_point):
    painter = QPainter(canvas.image)
    painter.setRenderHint(canvas.render_hint)
    pen = QPen(canvas.brush_color.darker(), canvas.brush_size, Qt.PenStyle.SolidLine, canvas.brush_shape, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawPath(canvas.path)
    canvas.last_point = cursor_point
    canvas.update()

def draw_eraser(canvas, cursor_point):
    painter = QPainter(canvas.image)
    painter.setRenderHint(canvas.render_hint)
    pen = QPen(Qt.GlobalColor.white, canvas.brush_size, Qt.PenStyle.SolidLine, canvas.brush_shape, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(canvas.last_point.toPoint(), cursor_point)
    canvas.last_point = cursor_point
    canvas.update()

def draw_line(canvas, cursor_point):
  painter = QPainter(canvas.image)
  painter.setRenderHint(canvas.render_hint)
  pen = QPen(canvas.brush_color, canvas.brush_size, Qt.PenStyle.SolidLine, canvas.brush_shape, Qt.PenJoinStyle.RoundJoin)
  painter.setPen(pen)
  painter.drawPath(canvas.path) # Use the painter path
  canvas.last_point = cursor_point
  canvas.update()
    
def draw_custom_brush(canvas, cursor_point):
    painter = QPainter(canvas.image)
    brush_half_size = canvas.brush_size // 2
    painter.setRenderHint(canvas.render_hint)
    painter.drawPixmap(cursor_point.x() - brush_half_size, cursor_point.y() - brush_half_size,
                        canvas.custom_brush.scaled(canvas.brush_size, canvas.brush_size))
    canvas.last_point = cursor_point
    canvas.update()
