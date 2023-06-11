from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QEvent, Qt, QUrl

class LinkDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        text = index.model().data(index)
        document = QTextDocument()
        document.setHtml(f'<a href="{text}">Spotify</span></a>')

        # Check if the cell is selected
        if option.state & QStyle.State_Selected:
            # Set the color you want when selected
            painter.fillRect(option.rect, QColor("#dbe1ec"))

        painter.save()
        painter.translate(option.rect.topLeft())
        document.drawContents(painter)
        painter.restore()


    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            if option.rect.contains(event.pos()):
                QDesktopServices.openUrl(QUrl(index.data()))
                return True

        return super().editorEvent(event, model, option, index)
