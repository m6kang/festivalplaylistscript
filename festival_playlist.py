import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
import json
import inquirer

questions = [
    inquirer.List("Festival",
                  message="Which festival are you attending?",
                  choices=["Nocturnal Wonderland", "Escape Halloween", "Countdown", "Beyond Wonderland", "EDC Las Vegas"],
                  ),
]

festival = inquirer.prompt(questions)
festival = festival["Festival"]
if festival == "Nocturnal Wonderland":
    url = "https://www.nocturnalwonderland.com/lineup/"
elif festival == "Escape Halloween":
    url = "https://escapehalloween.com/lineup/"
elif festival == "Countdown":
    url = "https://countdownnye.com/lineup/"
elif festival == "Beyond Wonderland":
    url = "https://socal.beyondwonderland.com/lineup/"
elif festival == "EDC Las Vegas":
    url = "https://lasvegas.electricdaisycarnival.com/lineup/"

web_page = requests.get(url)
soup = BeautifulSoup(web_page.text, "html.parser")
artists = soup.find_all("a", class_="js-wp-template-Modal no-barba")
artist_list = [artist.get_text() for artist in artists]
artist_list = list(set(artist_list))
for i in range(0, len(artist_list)):
    if "(" in artist_list[i]:
        if "B2B" in artist_list[i]:
            B2B_artists = artist_list[i].split("(")
            if "B2B" in B2B_artists[0]:
                B2B_artists = B2B_artists[0].split("B2B")
                B2B_artist_1 = B2B_artists[0].replace(" ", "")
                B2B_artist_2 = B2B_artists[1].replace(" ", "", 1)
                B2B_artist_2 = B2B_artist_2.replace(")", "")
                artist_list.pop(i)
                artist_list.append(B2B_artist_1)
                artist_list.append(B2B_artist_2)
            else:
                B2B_artists = B2B_artists[1].split("B2B")
                B2B_artist_1 = B2B_artists[0].replace(" ", "")
                B2B_artist_2 = B2B_artists[1].replace(" ", "", 1)
                B2B_artist_2 = B2B_artist_2.replace(")", "")
                artist_list.pop(i)
                artist_list.append(B2B_artist_1)
                artist_list.append(B2B_artist_2)
        else:
            count = 0
            for j in artist_list[i]:
                if j == "(":
                    artist_name = artist_list[i][:count - 1]
                    artist_list.pop(i)
                    artist_list.append(artist_name)
                else:
                    count += 1
artist_list.sort()


questions = [
    inquirer.Checkbox("Artists",
                      message = "Select Your Artists (Use Up/Down Arrow to Move and Space to Select)",
                      choices = artist_list,
                      ),
]

artist_list = inquirer.prompt(questions)
artist_list = artist_list["Artists"]
print("Creating Playlist!")

spotify_client_id = "315ab312ad1d41c799ca39168bd977de"
spotify_secret = "7529802a18c64fd78ea1c1282b6da1a1"
spotify_redirect_uri = "http://127.0.0.1:5000/redirect"

scope = "playlist-modify-public"

spotify_object = spotipy.Spotify(auth_manager=SpotifyOAuth (client_id=spotify_client_id, client_secret=spotify_secret, redirect_uri=spotify_redirect_uri, scope=scope))

current_user = spotify_object.current_user()
current_user_id = current_user["id"]

playlist = spotify_object.user_playlist_create(user=current_user_id, name=festival, public=True, description="{} playlist created by minty_k".format(festival))

playlist_id = playlist["id"].split(":")[0]

try:
    for a in artist_list:
        artist = spotify_object.search(a, limit=1, type="artist")
        artist_link = artist["artists"]["items"][0]["uri"]

        artist_top_tracks = spotify_object.artist_top_tracks(artist_link)
        artist_top_track_ids = []
        
        for track in artist_top_tracks["tracks"][:10]:
            artist_top_track_ids.append(track["id"])
            
        results = spotify_object.user_playlist_add_tracks(user=current_user_id, playlist_id=playlist_id, tracks= artist_top_track_ids)
except:
    print("Created the playlist with some of the songs!")
else:
    print("Successfully created the playlist!")
    
