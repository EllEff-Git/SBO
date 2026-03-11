import subprocess, configparser, socket
# Required to run the websocket program, the python intercommunication system and to read config
import os, sys, time, threading, datetime
# Required for system information, background tasking and queueing
import spotipy, requests, json
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for token exceptions (errors)



### Setup Section ###



SBO_ver = "v0.3.11.1545"
"""The SBO program version (y.m.dd.hhmm)"""


if getattr(sys, "frozen", False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    """The base directory of the program, where SBO.exe resides"""
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    """The base directory of the program, where SBO.exe resides"""


### SBO WebSocket ###

sbotxtPath = os.path.join(directory, "WS", "sbo.txt")
"""The path to sbo.txt (SBO/WS/sbo.txt)"""

sbowsExe = "SBO-WS.exe"
"""The name of the SBO-WS.exe file"""
sbowsDir = os.path.join(directory, "WS") 
"""The websocket folder (SBO/WS)"""
sbowsPath = os.path.join(sbowsDir, sbowsExe)
"""The full path to the SBO-WS.exe (SBO/WS/SBO-WS.exe)"""

### SBO Bot ###

sboBotExe = "SBO-Bot.exe"
"""The name of the SBO-Bot.exe file"""
sboBotDir = os.path.join(directory, "Bot")
"""The bot's folder (SBO/Bot) """
sboBotPath = os.path.join(sboBotDir, sboBotExe)
"""The full path to the SBO-Bot.exe (SBO/Bot/SBO-Bot.exe)"""

### Time Function (Console) ###

def Time():
    """Function that returns the current time, formatted"""

    return (datetime.datetime.now().strftime("%H:%M:%S") + " ")
    # shortens the call to current system timestamp, adds empty space so the brackets have a gap

   
print(f"{Time()}[START]: Starting SBO {SBO_ver}\n")
# quick user update on status


# Event Thread / Auth Lock #

songEvent = threading.Event()
"""Creates an empty threading event list for song"""

spotifyLock = threading.Lock()
"""Creates a locking method to prevent multiple API calls stacking"""


### Config ###


Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
"""The configuration file reader"""
ConfigPath = os.path.join(directory, "config.ini")
"""The directory where the config sits in"""
Config.read(ConfigPath, "utf8")
# Where the config is read from, with UTF-8 format

enableBot = Config.getboolean("Twitch-Bot", "enable_Twitch_Bot")
"""Whether to enable the Twitch Bot part of the program (boolean)"""
runBot = Config.getboolean("Twitch-Bot", "sbo_Runs_Bot")
"""Whether to automatically start the bot (boolean)"""

if runBot:
    # if SBO should run the bot
    enableBot = True
    # also enables the bot

if enableBot:
    # if the bot is enabled
    webHost =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # creates the base webHost socket (defines)
    webHost.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # restarts sockets
    webHost.bind(("127.0.0.1", 6666))
    # sets the address and port
    webHost.listen()
    # creates a websocket listener connection on localhost
    print(f"{Time()}[PTP]: Started inter-python connection")
    # debug print

sp_client_ID = Config.get("Required", "spotify_Client_ID")
"""The Spotify Client ID from Developer Dashboard (string)"""
sp_client_secret = Config.get("Required", "spotify_Client_Secret")
"""The Spotify Secret from Developer Dashboard (string)"""
sp_redirect = Config.get("Required", "http_Redirect")
"""The Spotify redirect URL from Developer Dashboard"""
sp_cache = os.path.join(directory, "Data", "spotifycache.json")
"""The directory where the spotify cache (token) sits in"""

if len(sp_client_secret) > 5:
    # checks if the client secret has at least 5 characters
    None
else:
    print(f"{Time()}[ERROR]: Required info not found in config.ini, please enter the identifiers and try again")
    time.sleep(30)
    raise SystemExit


### Auth ###


sessionID = requests.Session()
"""Tells the auth to keep one stable connection, rather than re-connecting every request"""

authorisation = SpotifyOAuth(
    scope = ["user-read-playback-state", "user-modify-playback-state"], 
    client_id = sp_client_ID, 
    client_secret = sp_client_secret, 
    redirect_uri = sp_redirect,
    cache_path = sp_cache
    )
"""The argument for auth_manager, containing the variables from config + scope of data request"""

main = spotipy.Spotify(auth_manager = authorisation, requests_session = sessionID)
"""Handles the authentication and user identification"""


### Variables ###


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

songColorHex = textColorHex = barColorHex = overlayColorHex = None
"""Saves all the colors as empty, so that they can hold hex codes later"""

callSong = False
"""A check to see if song() should be called regardless of song change state (due to a color change)"""



### Spotify Data Grabber Function ###



def authPlayback():
    """Function to more "safely" handle Spotify API requests and errors"""
    
    global main
    # takes the global variable and makes it local

    with spotifyLock:
        # uses a threading lock, to prevent multiple requests at once

        tokenRefresh = False
        # a boolean to determine whether to print the token refresh or reconnect text

        internalError = False
        # a boolean to determine if the error was Spotify's internal error (changes final print)

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
                    print(f"\n{Time()}[INFO]: Refreshing Spotify token")
                    # doesn't sleep because this is a token error and should get fixed nearly instantly
                    # expected to print just about every 3600 seconds (1h)
                    tokenRefresh = True
                    # sets the tokenRefresh mode to true so it prints the token text on success
                    internalError = False
                    # sets the flag to false

                elif isinstance(error, requests.exceptions.ReadTimeout):
                    # if the error is a read timeout (sort of random)
                    print(f"{Time()}[ERROR]: Spotify API timeout, retrying in 5 seconds ({attempt+1}/3)")
                    time.sleep(2)
                    # sleeps for 2 seconds (because there's a function-wide 3-second cooldown added on top)

                elif isinstance(error, SpotifyException) and error.http_status == 500:
                    # if the error is 500 (internal error fail)
                    print(f"{Time()}[ERROR]: Spotify internal error (Code 500). Attempting to reconnect ({attempt+1}/3)]")
                    # prints an error message
                    internalError = True
                    # should never happen, but very very rarely does

                else:
                    # if the error is anything else
                    print(f"{Time()}[ERROR]: Spotify errored due to {error}.\n{Time()}[INFO]: Attempting to reconnect ({attempt+1}/3)")
                    internalError = False
                    # sets the flag to false

                ### Too Many Errors ###

                if attempt == 2 and not internalError:
                    # if it's the last attempt (range(3) = 0,1,2) and it fails
                    print(f"{Time()}[CRITICAL]: All attempts to reconnect failed due to {error}\n\nPlease manually restart SBO. Exiting...")
                    time.sleep(600)
                    raise SystemExit
                    # prompts user, then exits

                elif attempt == 2 and internalError:
                    # if it's the last attempt and fails due to internal error
                    print(f"{Time()}[CRITICAL]: All attempts to reconnect failed due to Spotify's internal error.\n\nPlease manually restart SBO. Exiting...")
                    time.sleep(600)
                    raise SystemExit
                    # prompts user, then exits

                time.sleep(3)
                # waits 3 seconds to give it some time between tries



### Web Host / Listener ###



def webHostListener():
    """Websocket message host/listener"""
    print(f"{Time()}[PTP]: Waiting for SBO-Bot to connect")
    # prints the message on program start

    while True:
        client_socket, client_address = webHost.accept()
        # waits for a client connection
        print(f"{Time()}[PTP]: SBO-Bot connected")
        # prints a Python to Python (Peer to Peer) inform when Bot connects successfully

        while True:
            # while the program is running
            rawMessage = client_socket.recv(1024)
            # grabs any messages sent (1024 bytes, shouldn't use more than a few)

            if not rawMessage:
                # if the message is empty (disconnect)
                break
                # breaks to reset the connection

            message = rawMessage.decode().strip()
            # decodes it (bytes -> string) and strips empty space

            print(f"{Time()}[PTP]: Command received:", message)
            # prints a Python to Python (Peer to Peer) inform

            botCommand(message)
            # calls botCommand with the decoded and stripped message



### Bot Commands ###



def botCommand(command: str):
    """Helper function to pick what control function to call"""
    playbackCommands = {
        "Skip": skip,
        "Pause": pause,
        "Resume": resume,
        "Previous": previous,
    }
    # list of playback controlling commands

    if command in playbackCommands:
        # if the command is one of the playback controls
        playbackCommands[command]()
        # constructs a call dynamically from the command and calls the function
        return
        # stops checks

    if command.startswith("Queue:"):
        # if the command starts with "queue"
        x, uri = command.split(" ", 1)
        # splits the command into scrap (command) and the URI to pass
        queue(uri)
        return
        # stops checks

    if command.startswith(("Song Color:", "Text Color:", "Bar Color:", "Overlay Color:")):
        func, color = command.split(": ", 1)
        # splits the command into the function and the color to pass
        colorChanger(func, color)
        # calls the colorChanger with the parsed function and color as parameters
        return
        # stops cheks
    
    print(f"{Time()}[PTP]: Unknown command:", command)
    # if the command is somehow not recognized (shouldn't ever happen, but this way won't break)

def skip():
    """Skips to next song"""
    try:
        main.next_track()
        print(f"{Time()}[SBOT]: Skipped song")
        # success log print
    except:
        print(f"{Time()}[SBOT]: Couldn't skip song")
        # print if there's an error

def pause():
    """Pauses playback"""
    try:
        main.pause_playback()
        print(f"{Time()}[SBOT]: Paused playback")
        # success log print
    except:
        print(f"{Time()}[SBOT]: Couldn't pause playback")
        # print if there's an error

def resume():
    """Resumes playback"""
    try:
        main.start_playback()
        print(f"{Time()}[SBOT]: Resuming playback")
        # success log print
    except:
        print(f"{Time()}[SBOT]: Couldn't resume playback")
        # print if there's an error

def previous():
    """Goes back to previous song"""
    try:
        main.previous_track()
        print(f"{Time()}[SBOT]: Previous song")
        # success log print
    except:
        print(f"{Time()}[SBOT]: Couldn't go to previous song")
        # print if there's an error

def queue(link):
    """Queues a given song via Spotify link"""
    try:
        main.add_to_queue(link)
        print(f"{Time()}[SBOT]: Song added to queue")
        # success log print
    except:
        print(f"{Time()}[SBOT]: Error adding to queue")
        # print if there's an error (shouldn't be a type error since SBO-Bot checks type before sending)



def colorChanger(func, color):
    """Helper function to call the correct color changer function"""
    global callSong
    # grabs the boolean from global -> local

    colorFunctions = {
        "Song Color": songColor,
        "Text Color": textColor,
        "Bar Color": barColor,
        "Overlay Color": overlayColor
    }
    # stores all the color-related functions in a map

    if color != "clear" and not color.startswith("#"):
        # checks if the color already has a # and that it isn't "clear"
        color = "#" + color
        # if not, adds the # (needed to pass hex values to HTML)

    colorFunctions[func](color)
    # calls a function based on the parameters
    callSong = True
    # turns the flag to call song() to True (tells looper to run a song() instance regardless of song update)

def songColor(color):
    """Changes the color of the song text"""
    global songColorHex
    if color == "clear":
        songColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Song text color cleared")
    else:
        songColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Song text color set to: {color}")

def textColor(color):
    """Changes the color of the overlay text"""
    global textColorHex
    if color == "clear":
        textColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Text color cleared")
    else:
        textColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Text color set to: {color}")

def barColor(color):
    """Changes the color of the progress bar"""
    global barColorHex
    if color == "clear":
        barColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Progress bar color cleared")
    else:
        barColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Progress bar color set to: {color}")

def overlayColor(color):
    """Changes the color of the overlay borders"""
    global overlayColorHex
    if color == "clear":
        overlayColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Overlay color cleared")
    else:
        overlayColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Overlay color set to: {color}")



### SBO WebSocket ###



def runSBOws():
    """Function to start the SBO-WS.exe"""
    with subprocess.Popen([sbowsPath], cwd=sbowsDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as sbowsPrint:
        # opens the SBO-WS.exe file and reads its output
        for line in sbowsPrint.stdout:
            # every time a new line is sent
            print(f"{Time()}[WS]: {line.rstrip()}")
            # prints the line (clears right side)



### Twitch Bot ###



def runSBOBot():
    """Function to start the SBO Twitch Bot"""
    with subprocess.Popen([sboBotPath], cwd=sboBotDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as sboBotPrint:
        # opens the SBO-Bot.exe file and reads its output 
        for line in sboBotPrint.stdout:
            # every time a new line is sent
            print(f"{Time()}[SBOT]: {line.rstrip()}")
            # prints the line (clears right side)



### Song Data File Field Selection/Creation ###



def song():
    """The function that handles all song data gathering and parsing, as well as pushing to C++ via text"""
    global currentInfo, trackCounter, oldCount, songColorHex, textColorHex, barColorHex, overlayColorHex
    # pulls some global variables to local

    while True:

        songEvent.wait()
        # waits for looper() to set an event

        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 

        csArtistString = []
        # creates an empty list for artists to get added into as the loop progresses

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
        paused = not(csPlayState)
        # stores the opposite of playstate (if playing, paused = false, if not, paused = true)

        if not csPlayState:
            # if the song is paused

            songNameList.append("Paused on:")
            # adds the "paused on" text to list

        elif trackCounter != oldCount and csPlayState:
            # checks if the song has changed (and song is playing, this way won't activate on paused songs and cause flashing elements)

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
            csAlbumURLs = csAlbum.get("external_urls")
            # stores the album urls 
            sboAlbumURL = csAlbumURLs.get("spotify")
            # gets the spotify url 

        else:
            # if the song is local
            csURL = "A local song"
            sboAlbumURL = "A local album"

        if csPlaylist != None:
            # checks if user is playing a playlist
            csPlaylistURL = csPlaylist.get("external_urls")
            # gets *all* the URLs for the playlist
            csPlaylistURL = csPlaylistURL.get("spotify")
            # gets only the playlist URL (only one in there, unsure why it's a dictionary but ok Spotify)
        
        else:
            # if there's no playlist
            csPlaylistURL = "No playlist"
            csPlaylist = "No playlist"

        songNameList.append(csName)
        # adds the song name to list
        
        sboSongName = " ".join(songNameList)
        # joins together the list (just paused state + song name)

        sboArtistName = csArtistName
        # assigns the artist name

        sboAlbumName = csAlbumName
        # assigns the album name

        sboURL = csURL
        # assigns the URL (this is the Spotify track URL)


        ### SBO-WS Text File Writer ###


        sboFull = (
                    f"Song Name = {sboSongName}\n"
                    f"Artist Name = {sboArtistName}\n"
                    f"Album Name = {sboAlbumName}\n"
                    f"Album URL = {sboAlbumURL}\n" 
                    f"Spotify URL = {sboURL}\n"
                    f"Spotify Image = {csCover}\n"
                    f"Playlist Name = {csPlaylist}\n"
                    f"Playlist URL = {csPlaylistURL}\n"
                    f"UNIX Start = {str(csUnixStart)}\n"
                    f"UNIX End = {str(csUnixEnd)}\n"
                    f"Pause State = {str(paused)}\n"
                    f"Track ID = {str(trackCounter)}\n"
                    f"Song Color = {songColorHex}\n"
                    f"Text Color = {textColorHex}\n"
                    f"Bar Color = {barColorHex}\n"
                    f"Overlay Color = {overlayColorHex}\n"
                    )
        # merges all the song/color/other information together, split by newlines

        with open(sbotxtPath, "w", encoding="utf-8") as txt:
            # opens the songData text file
            txt.write(sboFull)
            # writes the full song information to the text file
            print(f"{Time()}[INFO]: Song data file updated")
            # prints an update

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



def looper():
    """Function that checks song info on a loop"""
    global currentURI, currentInfo, pauseUpdated, trackCounter, callSong
    # grabs the "global" variables (outside the function) as local variables
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
        songProg = int((info.get("progress_ms")) / 1000)
        # grabs the progress of the song at the pull time (ms/1000 = seconds)
        songStart = int(time.time() - songProg)
        # stores the start time of the song by taking current time and subtracting progress
        playing = info.get("is_playing")
        # checks the pause state (True if playing, False if not)

        if currentURI is None:
            # when the program first starts, the currentURI will be "None", this updates it
            currentURI = songURI
            # sets the current song to match 
            storedStart = songStart
            # updates the timestamp to match
            trackCounter += 1
            # adds 1 to counter
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            print(f"{Time()}[SONG]: First song: {songName}, has been successfully processed\n")

        songDur = int((info.get("item")).get("duration_ms")/1000)
        # grabs both the current time and length of the song (in seconds)
        songLeft = (songDur - songProg)
        # calculates the time left on the song

        if (currentURI != songURI) or ((songStart-5) > storedStart) or (pauseUpdated and playing):
        # if there's a song change (if the URI has changed or the start timestamp is higher than the stored timestamp) or if the pause has been triggered

            if not pauseUpdated:
                # if console updates are enabled and this change wasn't triggered by a pause
                print(f"\n{Time()}[SONG]: New song: {songName}, duration: {songDur:,.0f} seconds")
                # user update on new song (makes a new line before itself so it separates tracks)
            elif pauseUpdated:
                # if console updates are enabled and this change *was* triggered by a pause
                print(f"\n{Time()}[SONG]: Unpaused: {songName}")

            currentURI = songURI
            # changes the internal variable to match new song
            storedStart = songStart
            # changes timestamp variable to match
            songEvent.set()
            # sets an event to make song() update the text file
            callSong = False
            # if a new song is set, it'll run the song() normally, no need to separately run

            if pauseUpdated:
                # if it's playing and the pauseUpdate has been set to true
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice
            else:
                # if it's playing but pauseUpdate is false
                trackCounter += 1
                # adds 1 to counter (means track has changed)

            time.sleep(2)
            # waits a second
            continue
            # sends back to the start of looper to check for a new song (1 second checks after a song change to check for a song skip)

        if not playing and not pauseUpdated and currentURI == songURI:
        # if the song is paused, hasn't yet updated the pause state *and* the song is the same
            songEvent.set()
            # sets an event to make song() update the text file
            callSong = False
            # if song() gets called anyway, no need to separately run
            pauseUpdated = True
            # sets the pause check to True, meaning it has been checked and acted on
            print(f"\n{Time()}[SONG]: Paused on: {songName}")
            # user inform (new line to split from main updates, only prints once anyway)
            sleepfor = 2
            # sets the sleep timer to the config-set refresh time

        if callSong:
            # if there's a callSong request from colorChanger, and both checks passed (no new song, no pause state)
            songEvent.set()
            # sets an event to make song() update the text file
            callSong = False
            # turns off so it doesn't call again

        else:
        # if the current song is the same, and is not paused
            if songLeft > 2:
                # checks if there's more than 2s left
                sleepfor = 2
                # sets the sleep timer to 2s
            else:
                # if there's less song time left than 2s
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


if enableBot:
    # if the config option to enable the bot is on (enabled by bot runner if not already)
    ptpThread = threading.Thread(target = webHostListener)
    # creates a thread for the webhost listener
    ptpThread.start()
    # starts the ptp thread


if runBot:
    # if the config option to have SBO run the bot program is enabled
    botThread = threading.Thread(target = runSBOBot)
    # creates a thread for the SBO-Bot program to run in - this way it won't stop the main process
    botThread.start()
    # starts the SBO-Bot thread


looper()
# runs the looper, which manages the song refresh cycles