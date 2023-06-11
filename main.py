from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from Message_Dialog import MessageDialog
from DeleteSong import DeleteSongDialog
from AddSong import AddSongDialog
from SpotifyLink import LinkDelegate

client_credentials_manager = SpotifyClientCredentials(client_id="13486ce669094ba5a6eea9cba155c49d", client_secret="b17f0d03a76b4d5ab23d16610184e94d")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

df = pd.read_csv('tracks_with_language.csv')
df = df.drop_duplicates(subset=['name', 'artists'], keep='first')
favorites_path = 'favorites.csv'

try:
    favorites = pd.read_csv(favorites_path)
except FileNotFoundError:
    favorites = pd.DataFrame(columns=df.columns)

class MainGui(QMainWindow):
    def __init__(self):
        super(MainGui, self).__init__()
        uic.loadUi("mainwindow.ui", self)

        # Set the background image
        background = QPixmap("background_1.png")
        background = background.scaled(self.size(), Qt.IgnoreAspectRatio)
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)
        self.setWindowTitle("Music recommendation system")
        # Make the table view and its viewport background transparent
        self.tableView.setStyleSheet("background-color: transparent;")
        self.tableView.viewport().setStyleSheet("background-color: transparent;")

        # Set the style of the header row and the vertical header column
        self.tableView.horizontalHeader().setStyleSheet("QHeaderView::section{background-color: #cdbd9f;}")
        self.tableView.verticalHeader().setStyleSheet("QHeaderView::section{background-color: #cdbd9f;}")

        # Show the song list immediately
        self.show_my_songs()

        self.tableView.setShowGrid(False)

        # Connect the buttons
        button_style = """
            QPushButton {
                background-color: #cdbd9f;
                border-radius: 10px;
                color: #324260;
            }

            QPushButton:hover {
                background-color: #b49c6f;
            }

            QPushButton:pressed {
                background-color: #b6b6b6;
            }
        """
        self.my_songs_button.setStyleSheet(button_style)
        self.recommended_songs.setStyleSheet(button_style)
        self.add_song.setStyleSheet(button_style)
        self.delete_song.setStyleSheet(button_style)
        self.search_button.setStyleSheet(button_style)

        self.my_songs_button.setFixedHeight(21)
        self.recommended_songs.setFixedHeight(21)
        self.add_song.setFixedHeight(21)
        self.delete_song.setFixedHeight(21)
        self.search_button.setFixedHeight(21)

        self.search_line.setStyleSheet("background-color: #f8f6f2;")  # Set the desired color for the search line

        self.my_songs_button.clicked.connect(self.show_my_songs)
        self.recommended_songs.clicked.connect(self.recommend_songs)
        self.add_song.clicked.connect(self.open_add_song_dialog)
        self.delete_song.clicked.connect(self.open_delete_song_dialog)
        self.search_button.clicked.connect(self.search_song)

        self.tableView.setStyleSheet(
            "QTableView::item:selected { background-color: #dbe1ec; }")  # Set highlighting color
        self.show()

        self.global_top.setStyleSheet(button_style)
        self.global_top.setFixedHeight(21)
        self.global_top.clicked.connect(lambda: self.show_top_songs('37i9dQZEVXbNG2KDcFcKOF'))

        self.Ukraine_top.setStyleSheet(button_style)
        self.Ukraine_top.setFixedHeight(21)
        self.Ukraine_top.clicked.connect(lambda: self.show_top_songs('37i9dQZEVXbNcoJZ65xktI'))

        # Set column sizes
        self.tableView.setColumnWidth(0, 250)
        self.tableView.setColumnWidth(1, 250)
        self.tableView.setColumnWidth(2, 110)  # Set width for release date column
        self.tableView.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        # Enable sorting in the table view and connect sorting signal
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().sectionClicked.connect(self.sort_table)

    def to_table_model(self, songs):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Назва пісні', 'Виконавець', 'Дата випуску', 'Посилання'])

        for index, row in songs.iterrows():
            artist = row['artists'][0:len(row['artists'])].replace("'", "").replace("[", "").replace("]", "")
            name = row['name']
            url = f"https://open.spotify.com/track/{row['id']}"

            if isinstance(row['release_date'], pd.Timestamp):
                release_date = row['release_date'].strftime("%Y-%m-%d")
            elif isinstance(row['release_date'], int):
                # You may need to adjust the format of the date here
                release_date = str(row['release_date'])
            else:
                try:
                    release_date = datetime.strptime(row['release_date'], '%Y-%m-%d').strftime("%Y-%m-%d")
                except ValueError:
                    release_date = str(row['release_date'])  # Use the original value if it cannot be parsed as a date

            model.appendRow([
                QStandardItem(name),
                QStandardItem(artist),
                QStandardItem(release_date),
                QStandardItem(url),
            ])

        link_delegate = LinkDelegate(self.tableView)
        self.tableView.setItemDelegateForColumn(3, link_delegate)

        return model

    def show_my_songs(self):
        global favorites
        try:
            favorites = pd.read_csv(favorites_path)
        except FileNotFoundError:
            favorites = pd.DataFrame(columns=df.columns)

        if favorites.empty:
            error_dialog = MessageDialog(self)
            error_dialog.show_information("Увага", "Не було додано жодної пісні до улюблених")
        model = self.to_table_model(favorites)
        self.tableView.setModel(model)

    def search_song(self):
        search_query = self.search_line.text().strip()  # Remove leading and trailing spaces

        if not search_query:  # Check if the search query is empty
            error_dialog = MessageDialog(self)
            error_dialog.show_warning("Введіть принаймні один символ для пошуку.")
            return

        search_result = df[
            df['name'].fillna('').str.contains(search_query, case=False) | df['artists'].fillna('').str.contains(
                search_query, case=False)]

        # Limit the search result to a maximum of 200 songs
        search_result = search_result.tail(200)

        model = self.to_table_model(search_result)
        self.tableView.setModel(model)

    @staticmethod
    def parse_date(date_str):
        date_str = str(date_str)
        if '-' not in date_str:
            return f"{date_str}-01-01"
        elif date_str.count('-') == 1:
            return f"{date_str}-01"
        else:
            return date_str

    def recommend_songs(self):
        global favorites

        if favorites.empty:
            error_dialog = MessageDialog(self)
            error_dialog.show_warning("Неможливо створити рекомендації, оскільки немає пісень в медіатецію")
            return

        # process 'release_date' field
        if df['release_date'].dtype == 'object':  # apply only if it's not already in datetime format
            df['release_date'] = df['release_date'].apply(MainGui.parse_date)
            df['release_date'] = pd.to_datetime(df['release_date'])

        df['release_year'] = df['release_date'].dt.year

        favorites['release_date'] = favorites['release_date'].apply(MainGui.parse_date)
        favorites['release_date'] = pd.to_datetime(favorites['release_date'])

        favorites['release_year'] = favorites['release_date'].dt.year

        # Select the features you want to use for the KNN
        features = ['danceability', 'energy', 'key', 'loudness', 'speechiness',
                    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'language', 'release_year']

        # Separate the language feature
        lang_features = ['language']
        other_features = list(set(features) - set(lang_features))

        # Apply one-hot encoding to the language feature
        one_hot_encoder = OneHotEncoder(sparse_output=False)
        df_lang = one_hot_encoder.fit_transform(df[lang_features])
        favorites_lang = one_hot_encoder.transform(favorites[lang_features])

        df_other = df[other_features]
        favorites_other = favorites[other_features]

        # Normalize the other features
        min_max_scaler = MinMaxScaler()
        df_other = min_max_scaler.fit_transform(df_other)
        favorites_other = min_max_scaler.transform(favorites_other)

        # Concatenate the one-hot encoded and the normalized features
        df_features = np.concatenate([df_other, df_lang], axis=1)
        favorites_features = np.concatenate([favorites_other, favorites_lang], axis=1)

        # Build the KNN model
        knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
        knn_model.fit(df_features)

        # Get recommendations for each favorite song
        recommendations = []
        for favorite_song in favorites_features:
            distances, indices = knn_model.kneighbors([favorite_song], n_neighbors=300)
            for i in range(len(indices.flatten())):
                recommendations.append({
                    'song': df.iloc[indices.flatten()[i]],
                    'distance': distances.flatten()[i]
                })

        # Sort recommendations by distance and remove duplicates
        recommendations.sort(key=lambda x: x['distance'])
        recommendations_df = pd.DataFrame([rec['song'] for rec in recommendations]).drop_duplicates()

        # Remove songs that are already in the favorites library
        favorites_ids = favorites['id'].values  # Replace 'song_id' with your unique identifier column
        recommendations_df = recommendations_df[~recommendations_df['id'].isin(favorites_ids)]  # Replace 'song_id'

        recommendations_df = recommendations_df.head(150)

        model = self.to_table_model(recommendations_df)
        self.tableView.setModel(model)

    def open_add_song_dialog(self):
        dialog = AddSongDialog(self)
        dialog.exec_()
        # Make the table view and its viewport background transparent
        self.tableView.setStyleSheet("background-color: transparent;")
        self.tableView.viewport().setStyleSheet("background-color: transparent;")

        self.tableView.horizontalHeader().setStyleSheet("QHeaderView::section{background-color: #cdbd9f;}")
        self.tableView.verticalHeader().setStyleSheet("QHeaderView::section{background-color: #cdbd9f;}")

    def open_delete_song_dialog(self):
        dialog = DeleteSongDialog(self)
        dialog.exec_()

    def show_top_songs(self, id:str):
        playlist_id = id
        results = sp.playlist_tracks(playlist_id)

        # Parse the JSON response and convert it to a DataFrame
        track_list = []
        for item in results['items']:
            track_name = item['track']['name']
            artist_name = item['track']['artists'][0]['name']

            release_date = item['track']['album']['release_date']
            url = item['track']['external_urls']['spotify']
            track_id = item['track']['id']  # Get track id

            track_list.append([track_name, artist_name, release_date, url, track_id])

        global_top_df = pd.DataFrame(track_list, columns=['name', 'artists', 'release_date', 'url', 'id'])

        # Display the DataFrame in your table
        model = self.to_table_model(global_top_df)
        self.tableView.setModel(model)

    def sort_table(self, logical_index):
        # Get the current sort order for the clicked column
        current_order = self.tableView.horizontalHeader().sortIndicatorOrder()

        # Toggle the sort order
        new_order = Qt.AscendingOrder if current_order == Qt.DescendingOrder else Qt.DescendingOrder

        # Set the new sort order for the clicked column
        self.tableView.sortByColumn(logical_index, new_order)



def main():
    app = QApplication([])
    window = MainGui()
    app.exec()


if __name__ == "__main__":
    main()
