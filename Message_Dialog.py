from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MessageDialog(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('#ECE6DB'))
        self.setPalette(palette)

    def show_warning(self, message):
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle("Помилка")
        self.setText(message)
        self.exec_()

    def show_information(self, title,  message):
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(message)
        self.exec_()
