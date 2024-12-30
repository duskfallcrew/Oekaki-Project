# color_utils.py
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtCore import Qt
def create_pen(color, brush_size, brush_shape):
  """Creates a QPen object with the passed parameters. Returns a QPen object"""
  if isinstance(color, QColor):
    return QPen(color, brush_size, Qt.PenStyle.SolidLine, brush_shape, Qt.PenJoinStyle.RoundJoin)
  else:
      return QPen(QColor(Qt.GlobalColor.black), brush_size, Qt.PenStyle.SolidLine, brush_shape, Qt.PenJoinStyle.RoundJoin)