from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from Message_Dialog import MessageDialog

client_credentials_manager = SpotifyClientCredentials(client_id="13486ce669094ba5a6eea9cba155c49d", client_secret="b17f0d03a76b4d5ab23d16610184e94d")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

df = pd.read_csv('tracks_with_language.csv')
df = df.drop_duplicates(subset=['name', 'artists'], keep='first')
favorites_path = 'favorites.csv'

try:
    favorites = pd.read_csv(favorites_path)
except FileNotFoundError:
    favorites = pd.DataFrame(columns=df.columns)

class AddSongDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor('#ece6db'))
        self.setPalette(palette)

        self.setWindowTitle("Додати пісню")
        self.layout = QVBoxLayout()

        self.title_label = QLabel("Назва пісні:")
        self.layout.addWidget(self.title_label)

        self.title_input = QLineEdit()
        self.layout.addWidget(self.title_input)

        self.artist_label = QLabel("Виконавець:")
        self.layout.addWidget(self.artist_label)

        self.artist_input = QLineEdit()
        self.layout.addWidget(self.artist_input)

        self.confirm_button = QPushButton("Підтвердити")
        self.confirm_button.clicked.connect(self.add_song)
        self.layout.addWidget(self.confirm_button)

        self.setLayout(self.layout)

    def add_song(self):

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

        song = df.loc[(df['name'].str.contains(song_title, case=False)) & (df['artists'].str.contains(artist_name, case=False))]

        if song.empty:
            error_dialog = MessageDialog(self)
            error_dialog.show_warning("Пісню не було знайдено.")
            return



        favorites = pd.concat([favorites, song]).drop_duplicates()
        favorites.to_csv(favorites_path, index=False)

        success_dialog = MessageDialog(self)
        success_dialog.show_information("Успіх", "Пісню додано до медіатеки.")
        self.close()