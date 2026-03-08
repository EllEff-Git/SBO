import subprocess, configparser
# Required to run the websocket program and to read config
import os, sys, time, threading, datetime
# Required for system information, background tasking and queueing
import spotipy, requests, json
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for token exceptions (errors)



### Setup Section ###



SBO_ver = "v0.3.08.0445"
"""The SBO program version (y.m.dd.hhmm)"""


if getattr(sys, "frozen", False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    """The base directory of the program, where SBO-WS.exe resides"""
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    """The base directory of the program, where SBO-WS.exe resides"""


### SBO WebSocket ###

sbotxtPath = os.path.join(directory, "WS", "sbo.txt")
"""The path to sbo.txt (SBO/WS/sbo.txt)"""

sbowsExe = "SBO-WS.exe"
"""The name of the SBO-WS.exe file"""
sbowsDir = os.path.join(directory, "WS") 
"""The websocket folder (SBO/WS)"""
sbowsPath = os.path.join(sbowsDir + sbowsExe)
"""The full path to the SBO-WS.exe (SBO/WS/SBO-WS.exe)"""

### SBO Bot ###

sboBotExe = "SPO-Bot.exe"
"""The name of the SBO-Bot.exe file"""
sboBotDir = os.path.join(directory, "Bot")
"""The bot's folder (SBO/Bot) """
sboBotPath = os.path.join(sboBotDir + sboBotExe)
"""The full path to the SBO-Bot.exe (SBO/Bot/SBO-Bot.exe)"""


def Time():
    """Function that returns the current time, formatted"""

    return (datetime.datetime.now().strftime("%H:%M:%S") + " ")
    # shortens the call to current system timestamp, adds empty space so the brackets have a gap

   
print(f"{Time()}[START]: Starting SBO {SBO_ver}\n")
# quick user update on status


# Event Thread #


songEvent = threading.Event()
"""Creates an empty threading event list for song"""

spotifyLock = threading.Lock()
"""Creates a locking method to prevent redundant API calls (or 2 calls at once)"""


### Config ###


Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
"""The configuration file reader"""
ConfigPath = os.path.join(directory, "config.ini")
"""The directory where the config sits in"""
Config.read(ConfigPath, "utf8")
# Where the config is read from, with UTF-8 format

sp_client_ID = Config.get("Required", "spotify_Client_ID")
sp_client_secret = Config.get("Required", "spotify_Client_Secret")
sp_redirect = Config.get("Required", "http_Redirect")

sp_cache = os.path.join(directory, "Data", "spotifycache.json")
"""The directory where the spotify cache (token) sits in"""


if len(sp_client_secret) > 5:
    # checks if the client secret has at least 5 characters
    None
else:
    print(f"{Time()}[ERROR]: Required info not found in config.ini, please enter and try again")
    time.sleep(30)
    raise SystemExit


### Auth ###


sessionID = requests.Session()
"""Tells the auth to keep one stable connection, rather than re-connecting every request"""

authorisation = SpotifyOAuth(
    scope = "user-read-playback-state", 
    client_id = sp_client_ID, 
    client_secret = sp_client_secret, 
    redirect_uri = sp_redirect,
    cache_path = sp_cache
    )
"""The argument for auth_manager, containing the variables from config + scope of data request"""

main = spotipy.Spotify(auth_manager = authorisation, requests_session = sessionID)
"""Handles the authentication and user identification"""


### Variables ###


pauseStart = None
"""Makes a starter variable that stores a timestamp when a pause occurs"""

currentURI = None
"""Stores the currently playing track's URI"""

currentInfo = None
"""Song info dictionary"""

pauseUpdated = False
"""A check to see if the pause state has been registered properly"""

oldCount = 0
"""Variable for song counter"""

trackCounter = 0
"""A counter to track the current song's 'ID'"""



### Spotify Data Grabber Function ###



def authPlayback():
    """Function to more "safely" handle Spotify API requests and errors"""
    
    global main
    # takes the global variable and makes it local

    with spotifyLock:
        # uses a threading lock, to prevent multiple requests at once

        tokenRefresh = False
        # a boolean to determine whether to print the token refresh or reconnect text

        for attempt in range(3):
            # tries a max of 3 times to get Spotify data (typically succeeds 1st try, so if it doesn't work in 3, there's a bigger issue)

            try:
                # first tries to send an API request to Spotify
                
                success = main.current_playback()
                # if it works, returns the Spotify playback package (dictionary)

                if attempt != 0 and not tokenRefresh:
                    # if it's not the first attempt, meaning the reconnect attempt print has already been pushed once
                    print(f"{Time()}[INFO]: Reconnect successful!")
                    # prints user update

                elif tokenRefresh:
                    # if the tokenrefresh variable is set to true, that means a connectionerror occurred at least once
                    print(f"{Time()}[INFO]: Token refreshed successfully!")
                    # prints user update

                return success
                # sends back the successfully found dictionary to the calling function (should only be looper)
                

            except (SpotifyException, requests.exceptions.RequestException, ConnectionResetError) as error:
                # if it fails to acquire a Spotify playback package

                if isinstance(error, requests.exceptions.ConnectionError):
                    # if the error is a connection error (token expired)
                    print(f"{Time()}[INFO]: Refreshing Spotify token")
                    # doesn't sleep because this is a token error and should get fixed nearly instantly
                    # expected to print just about every 3600 seconds (1h)
                    tokenRefresh = True
                    # sets the tokenRefresh mode to true so it prints the token text on success

                else:
                    # if the error is anything else
                    print(f"{Time()}[ERROR]: Spotify errored due to {error}.\n{Time()}[INFO]: Attempting to reconnect ({attempt+1}/3)")

                if attempt == 2:
                    # if it's the last attempt (range(3) = 0,1,2) and it fails
                    print(f"{Time()}[CRITICAL]: All attempts to reconnect failed due to {error}\nPlease manually restart SBO. Exiting...")
                    time.sleep(60)
                    raise SystemExit
                    # prompts user, then exits

                time.sleep(3)
                # waits 3 seconds to give it some time



### TTV ###



def runSBOws():
    """Function to start the SBO-WS.exe"""
    with subprocess.Popen([sbowsPath], cwd=sbowsDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as sbowsPrint:
        # opens the SBO-WS.exe file and reads its output
        for line in sbowsPrint.stdout:
            # every time a new line is sent
            print(f"{Time()}[WS]: {line.rstrip()}")
            # prints the line (clears right side)


def runSBOBot():
    """Function to start the SBO Twitch Bot"""
    with subprocess.Popen([sboBotPath], cwd=sboBotDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as sboBotPrint:
        # opens the SBO-Bot.exe file and reads its output 
        for line in sboBotPrint.stdout:
            # every time a new line is sent
            print(f"{Time()}[Bot]: {line.rstrip()}")
            # prints the line (clears right side)



### Song Data File Field Selection/Creation ###



def song():
    """The function that handles all song data gathering and parsing, as well as pushing to C++ via text"""
    global pauseStart, currentInfo, trackCounter, oldCount
    # pulls some global variables to local

    while True:

        songEvent.wait()
        # waits for looper() to set an event

        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 

        csArtistString = []

        csFull = currentInfo
        # gets a huge dictionary containing all the information about current song
        # "cs" in the variables just stands for CurrentSong, which, while descriptive, made the later variables insanely long

        if not csFull or not csFull.get("item"):
            # checks if the dictionary is valid and can be called
            time.sleep(5)
            # waits for a few seconds
            continue
            # sends back to the start of song() to restart the song query

        csItem = csFull.get("item")
        # takes the first part of the song's info (leaving out device info and various user states)
        csAlbum = csItem.get("album")
        # takes a smaller part of the song's info (still contains a ton of extra)

        csName = csItem.get("name")
        # stores the name of the song

        isLocalSong = csItem.get("is_local")
        # checks if the song is a local song (can't use standard API info requests if so)

        if not isLocalSong:
            # these fields are only valid when it's not a local song

            csImages = csAlbum.get("images")
            # gets the information about the album's images
            csCover = csImages[0].get("url")
            # gets the album cover url (used to pass to Discord if pictureCycle = Spotify)

            csArtists = csAlbum.get("artists")
            # stores all the artists listed on the song

            csArtistList = []
            # creates an empty list of artists
            for musician in csArtists:
                # for every artist in the list of artists (from Spotify)
                artist = musician.get("name")
                # gets the name of the artist from a dictionary
                csArtistList.append(artist)
                # appends it to the list of artists 

            if len(csArtistList) > 1:
                # if there's more than 1 artist
                csArtistFirstHalf = csArtistList[0:-1]
                # grabs all the artists except the last one
                csArtistLast = csArtistList[-1]
                # grabs the last artist

                if len(csArtistFirstHalf) > 1:
                    # checks if there's more than 1 artist in the first half
                    csArtistString = ", ".join(csArtistFirstHalf)
                    # joins together with commas
                else:
                    # if there's not more than 1 artist in the first half
                    csArtistString = "".join(csArtistFirstHalf)
                    # just joins with nothing (turns into a string basically)

                csArtistString = (csArtistString + " and ")
                # adds the "and" in between the first half and the last artist
                csArtistString = (csArtistString + csArtistLast)
                # adds the last artist to the string
                csArtistName = csArtistString
                # constructs a string from the artist names
            else:
                # if there's not more (just 1)
                csArtistName = csArtistList[0]
                # gets the name of the only artist
            
            csAlbumName = csAlbum.get("name")
            # stores the album name

        csLength = int(csItem.get("duration_ms")/1000)
        # stores the length of the song in seconds
        csProgress = int(csFull.get("progress_ms")/1000)
        # saves the current song progress in seconds

        csUnixStart = int(time.time() - csProgress + 1)
        # stores the start time of the song by taking current time and subtracting progress
        csUnixEnd = (csUnixStart + csLength)
        # stores the end time of the song (by adding up the start + duration)

        csPlayState = bool(csFull.get("is_playing"))
        # grabs the playback state (true/false)

        pauseState = False
        # defaults the pauseState to false

        if not csPlayState:
            # if the song is paused

            if pauseStart is None:
                # if there's no set pause time
                pauseStart = int(time.time() + 1)
                # sets the pause time to current time

            pauseState = True
            # sets the pauseState to True

            songNameList.append("Paused on:")
            # adds the "paused on" text to list

        elif pauseStart is not None and (trackCounter == oldCount):
            # if there's a set pause time from before (and the song hasn't changed)
            pauseDuration = int(time.time() - pauseStart)
            # calculates the time spent on pause
            csUnixStart += pauseDuration
            csUnixEnd += pauseDuration
            # sets the start and end times to match the time spent paused (by adding the time spent paused)
            pauseStart = None
            # resets the pauseStart to None, so it can get checked again

        elif trackCounter != oldCount and csPlayState:
            # checks if the song has changed

            oldCount = trackCounter
            # updates the song counter

        if not isLocalSong:
            # can't access these if the playing song is local
            cstrackURL = csItem.get("external_urls")
            # stores the list that contains track's url
            csURL = cstrackURL.get("spotify")
            # grabs the spotify track URL
            csPlaylist = csFull.get("context")
            # stores the list that contains the playlist url

            if csPlaylist != None:
                # checks if user is playing a playlist
                csPlaylistURL = csPlaylist.get("external_urls")
                # gets *all* the URLs for the playlist
                csPlaylistURL = csPlaylistURL.get("spotify")
                # gets only the playlist URL (only one in there, unsure why it's a dictionary but ok Spotify)
        
        else:
            # if the song is local
            csURL = "A local song"
            csPlaylistURL = "No playlist"

        songNameList.append(csName)
        # adds the song name to list
        
        ttvSongName = " ".join(songNameList)
        # joins together the list (just paused state + song name)

        ttvArtistName = csArtistName
        # assigns the artist name

        ttvAlbumName = csAlbumName
        # assigns the album name

        ttvURL = csURL
        # assigns the URL (this is the Spotify track URL)


        ### TTV Text File Writer ###


        ttvFull = (
                    f"Song Name = {ttvSongName}\n"
                    f"Artist Name = {ttvArtistName}\n"
                    f"Album Name = {ttvAlbumName}\n"
                    f"Spotify URL = {ttvURL}\n"
                    f"Spotify Image = {csCover}\n"
                    f"Playlist URL = {csPlaylistURL}\n"
                    f"UNIX Start = {str(csUnixStart)}\n"
                    f"UNIX End = {str(csUnixEnd)}\n"
                    f"Pause State = {str(pauseState)}\n"
                    )
        # merges all the song information together, split by newlines

        with open(sbotxtPath, "w", encoding="utf-8") as txt:
            # opens the songData text file
            txt.write(ttvFull)
            # writes the full song information to the text file
            print(f"{Time()}[INFO]: Song data file updated")
            # prints an update

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



def looper():
    """Function that checks song info on a loop"""
    global currentURI, currentInfo, pauseUpdated, trackCounter
    # grabs the "global" variable (outside the function) as a local variables
    while True:
        # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not

        info = authPlayback()
        # picks up all the info Spotify sends in an update

        if not info or not info.get("item"):
            # checks if the info has something and if it can be called
            print(f"{Time()}[WARN]: No playing state detected, re-checking in 2 seconds\n")
            time.sleep(2.5)
            # waits for a few seconds
            continue
        
        currentInfo = info
        # sets the global variable to match

        songURI = (info.get("item")).get("uri")
        # grabs the URI of the song, stores it
        songName = (info.get("item").get("name"))
        # stores name for display purposes
        songProg = ((info.get("progress_ms")) / 1000)
        # grabs the progress of the song at the pull time (ms/1000 = seconds)
        playing = info.get("is_playing")
        # checks the pause state (True if playing, False if not)

        if currentURI is None:
            # when the program first starts, the currentURI will be "None", this updates it
            currentURI = songURI
            # sets the current song to match 
            currentProg = songProg
            # updates the current progress
            trackCounter += 1
            # adds 1 to counter
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            print(f"{Time()}[SONG]: First song: {songName}, has been successfully processed\n")

        songDur = ((info.get("item")).get("duration_ms")/1000)
        # grabs both the current time and length of the song (in seconds)
        songLeft = (songDur-songProg)
        # calculates the time left on the song

        if (currentURI != songURI) or (songProg < currentProg) or (pauseUpdated and playing):
        # if there's a song change (if the URI or there's somehow less time left than previously) or if the pause has been triggered

            if not pauseUpdated:
                # if console updates are enabled and this change wasn't triggered by a pause
                print(f"\n{Time()}[SONG]: New song detected: {songName}, duration: {songDur:,.0f} seconds")
                # user update on new song (makes a new line before itself so it separates tracks)
            elif pauseUpdated:
                # if console updates are enabled and this change *was* triggered by a pause
                print(f"\n{Time()}[SONG]: Unpaused: {songName}")

            currentURI = songURI
            # changes the internal variable to match new song
            currentProg = songProg
            # changes timestamp variable to match
            songEvent.set()
            # sets an event to make song() update the text file

            if pauseUpdated:
                # if it's playing and the pauseUpdate has been set to true
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice
            else:
                # if it's playing but pauseUpdate is false
                trackCounter += 1
                # adds 1 to counter (means track has changed)

            time.sleep(2.5)
            # waits 5 seconds
            continue
            # sends back to the start of looper to check for a new song (5 second checks after a song change to check for a song skip)

        if not playing and not pauseUpdated and currentURI == songURI:
        # if the song is paused, hasn't yet updated the pause state *and* the song is the same
            songEvent.set()
            # sets an event to make song() update the text file (this way it doesn't spam)
            pauseUpdated = True
            # sets the pause check to True, meaning it has been checked and acted on
            print(f"\n{Time()}[SONG]: Paused on: {songName}")
            # user inform (new line to split from main updates, only prints once anyway)
            sleepfor = 2.5
            # sets the sleep timer to the config-set refresh time

        else:
        # if the current song is the same, and is not paused
            if songLeft > 2.5:
                # checks if there's more than 5s left
                sleepfor = 2.5
                # sets the sleep timer to 5s
            else:
                # if there's less song time left than 5s
                sleepfor = songLeft + 1
                # sleeps for the rest of the song (+1s to ensure the song has ended)

        time.sleep(sleepfor)
        # sleeps for the determined time


### Load Commands ###



songThread = threading.Thread(target = song)
# creates the song thread
songThread.start()
# starts the song thread to get updated info

sbowsThread = threading.Thread(target = runSBOws)
# creates a thread for the SBO-WS program to run in - this way it won't stop the main process
sbowsThread.start()
# starts the SBO-WS thread

looper()
# runs the looper, which manages the song refresh cycles