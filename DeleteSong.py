from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pandas as pd
from Message_Dialog import MessageDialog

df = pd.read_csv('tracks_with_language.csv')
df = df.drop_duplicates(subset=['name', 'artists'], keep='first')
favorites_path = 'favorites.csv'

try:
    favorites = pd.read_csv(favorites_path)
except FileNotFoundError:
    favorites = pd.DataFrame(columns=df.columns)

class DeleteSongDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('#ece6db'))
        self.setPalette(palette)

        self.setWindowTitle("Видалити пісню")

        self.layout = QVBoxLayout()

        self.title_label = QLabel("Назва пісні:")
        self.layout.addWidget(self.title_label)

        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)

        self.artist_label = QLabel("Виконавець:")
        self.layout.addWidget(self.artist_label)

        self.artist_input = QLineEdit()
        self.layout.addWidget(self.artist_input)

        self.confirm_button = QPushButton("Підтвердити:")
        self.confirm_button.clicked.connect(self.delete_song)
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)

    def delete_song(self):
        try:
            favorites = pd.read_csv(favorites_path)
        except FileNotFoundError:
            favorites = pd.DataFrame(columns=df.columns)

        song_title = self.title_input.text()
        artist_name = self.artist_input.text()

        if not song_title or not artist_name:
            error_dialog = MessageDialog(self)
            error_dialog.show_warning("Поля 'Назва пісні' та 'Виконавець' мають бути заповнені.")
            return

        song_to_delete = favorites.loc[(favorites['name'].str.contains(song_title, case=False)) & (favorites['artists'].str.contains(artist_name, case=False))]

        if song_to_delete.empty:
            error_dialog = MessageDialog(self)
            error_dialog.show_warning("Пісню не знайдено у медіатеці.")
            return

        favorites = favorites.drop(song_to_delete.index)
        favorites.to_csv(favorites_path, index=False)

        success_dialog = MessageDialog(self)
        success_dialog.show_information("Успіх", "Пісню видалено з медіатеки.")
        self.close()
