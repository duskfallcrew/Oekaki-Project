# ui_menus.py
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

def setup_menus(app):
  menu_bar = app.menuBar()
  file_menu = QMenu("File", app)
  menu_bar.addMenu(file_menu)
  
  exit_action = QAction("Exit", app)
  exit_action.triggered.connect(app.close)
  file_menu.addAction(exit_action)
