# CONUHACKS VI
# Project Written by Luiza Nogueira Costa
# PalTunes - A playlist recommendation system using Spotify API
# Using the Spotipy API - "https://spotipy.readthedocs.io/en/2.19.0/#
# Created on January 29th, 2022
# Part of the TouchTunes Spotify Recommendation System Sponsored Challenge

import requests
import json
import spotipy
import os
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

#Spotipy Authentication
#Enter information for local machine during setup
os.environ["SPOTIPY_CLIENT_ID"] = "your_client_id"
os.environ["SPOTIPY_CLIENT_SECRET"] = "your_client_secret"

redirect_uri = "http://localhost:8888/callback/"
scope = "user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-currently-playing user-library-read"


print("Dev authentication complete!")

def welcome():
    print("Welcome to PalTunes, your terminal-friendly playlist recommendation system.")
    print("Here we like to keep things simple - we will ask to connect to you and your friends' Spotify accounts.")
    print("Then, with a little coding magic, we will generate a neat playlist that will hopefully be enjoyed by all of you!")
    print("Perfect for long car trips, study sessions, hangouts, and more.")
    print("Alright. Let us begin!")


def create_playlist_forAll(friends, mode=1):
        songs_to_add = set()
        friends2 = set(friends)
        print("How many songs would you like to include per person?")
        limit = input("Enter the number of songs: ")
        for friend in friends:
            if mode == 1:       #Top Tracks
                toadd = friend.get_top_songs(limit)
                song_list = toadd['items']
                for track in song_list:
                    songs_to_add.add(track['uri'])
            elif mode == 2:     #Top Artists
                toadd = friend.get_top_artists(limit)
                song_list = toadd['tracks']
                for track in song_list:
                    songs_to_add.add(track['uri'])
            elif mode == 3:     #Random genres
                toadd = friend.get_top_genres(limit)
                song_list = toadd['tracks']
                for track in song_list:
                    songs_to_add.add(track['uri'])


        created = 0
        playlist_name = "test"
        while(created == 0):
            print("Who will be the playlist owner?")
            username = input("Enter your name:\n")
            for friend in friends:
                if friend.username == username:
                    #Creating the playlist
                    print("What would you like to name your playlist?")
                    playlist_name = input("Enter the playlist name:")
                    playlist_description = 'Created using PalTunes'
                    friend.spot.user_playlist_create(user=friend.username, name=playlist_name, public=True,
                                                            description=playlist_description)

                    #ID of new playlist and adding the tracks
                    empty_play = friend.spot.user_playlists(user=friend.username)
                    playlist = empty_play['items'][0]['id']
                    friend.spot.user_playlist_add_tracks(user=friend.username, playlist_id=playlist,
                                                                tracks=songs_to_add)
                    #Make users follow the created playlist:
                    for friend2 in friends2:
                        friend2.spot.current_user_follow_playlist(playlist)

                    created = 1
                    break

            if(created == 1):
                print("Playlist was created successfully.")
                print("Happy Listening!")
            else:
                print("Name invalid. Try again.")

class Friend:
    def __init__(self, username):

        self.username = username
        token = SpotifyOAuth(scope=scope, redirect_uri=redirect_uri, username=username, show_dialog=True)  #Autenthication token using Spotify. Will require login and authorization on user side.
        self.spot = spotipy.Spotify(auth_manager=token)

    def get_top_songs(self, limit = 10): #top tracks from user
        return self.spot.current_user_top_tracks(limit=limit, offset=0, time_range='medium_term')

    def get_top_artists(self, limit=10):  #top tracks based on user's favorite artist
        print(self.username + ", enter your top artist:\n")
        artist_name = input("Artist name:  ")
        results = self.spot.search(q=artist_name, limit=1, offset=0, type='artist', market=None)
        art_list = results['artists']
        for track in art_list['items']:
            return self.spot.artist_top_tracks(artist_id=track['id'])
    def get_top_genres(self, limit):  #generates a random list of tracks based on genres
        songs_to_add = self.spot.recommendation_genre_seeds()
        genres = list()
        song_list = songs_to_add['genres']
        for track in song_list:
            genres.append(track)
        return self.spot.recommendations(seed_genres=genres[:3], limit = limit)



if __name__ == '__main__':
    welcome()

    friends = set()

    print("We will now ask your friends' information.")
    num_of_friends = 0
    while num_of_friends <= 0 or num_of_friends > 5:
        num_of_friends = int(input("How many of you are there? Please enter a number between 1 and 5. \n"))

    i = 0

    while i < num_of_friends:
        print("Adding friend #{0}:".format(str(i + 1)))
        username = input("Enter your Spotify username: \n ")
        friend_to_add = Friend(username)
        friends.add(friend_to_add)
        i += 1
    done = False
    while not done:
        print("Great! What sort of playlist would you like to create for everyone to enjoy?")
        print("1 - Top tracks.")
        print("2 - Top artists.")
        print("3 - Randomize genres.")
        mode = input("Please enter one of the above indexes to make your selection.\n")
        if int(mode) > 0 and int(mode) < 4:
            create_playlist_forAll(friends, int(mode))
        else:  #Default in case of incorrect input
            create_playlist_forAll(friends, 1)

        print("Would you like to create more playlists?")
        answer = input("Y\\N: ")
        if answer == 'Y' or answer == 'y':
            print("Creating new playlist...")
        else:
            done = True




