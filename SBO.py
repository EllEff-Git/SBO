import subprocess, configparser, socket
# Required to run the websocket program, the python intercommunication system and to read config
import os, sys, time, threading, datetime, queue, concurrent.futures
# Required for system information, background tasking and queueing
import spotipy, requests, json
# Required for basic function of Spotify data requests and storing
from spotipy.oauth2 import SpotifyOAuth
# Required for authorizing with Spotify
from spotipy.exceptions import SpotifyException
# Required to check for token exceptions (errors)



### Setup Section ###



SBO_ver = "v0.3.13.0041"
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
"""Whether to enable the Twitch Bot PTP connection  (boolean)"""
runBot = Config.getboolean("Twitch-Bot", "sbo_Runs_Bot")
"""Whether to automatically start the bot program (boolean)"""

if runBot:
    # if SBO should run the bot
    enableBot = True
    # also enables the bot connection

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

currentURI = currentInfo = csPlaylistID = None
"""The current track information (URI is Spotify's idenfitier, Info contains the whole track package as a dict, csPlaylistID is the current track's playlist's ID)"""

pauseUpdated = False
"""Song state boolean checker to see if the pause has been registered"""

oldCount = trackCounter = 0
"""Variables for song counter"""

updateProgress = 0
"""A counter to check when/if progress was updated"""

songColorHex = textColorHex = barColorHex = overlayColorHex = None
"""Saves all the colors as empty, so that they can hold hex codes later"""

callSong = False
"""A check to see if song() should be called regardless of song change state (due to a color change)"""

lastSong = lastArtist = lastPlaylistURL = None
"""Previous track's identifiers"""



### Spotify API Request ###



class SpotifyQueue:
    """A class that handles Spotify API calls, with call queueing"""

    def __init__(self, main, spotifyLock):
        self.main = main
        self.spotifyLock = spotifyLock
        # sets the variables in scope
        self.spotifyCallQueue = queue.Queue()
        # creates a queue to place API calls into
        self.spCallQueueTracker = set()
        # creates an empty set to clone the API calls to keep track of the length

    def queueManager(self, call: str, URI: str = None):
        """Function to manage the queue (URI can be empty if call is a playback request or control, future can be empty if no return is expected)"""

        futureObj = concurrent.futures.Future()
        # creates a new future object in case the function wanted a return on data

        nextCall = (call, URI, futureObj)
        # creates the next call from the arguments

        with self.spotifyLock:
        # uses a threading lock, to prevent multiple requests at once
            if nextCall not in self.spCallQueueTracker:
                # ensures the next call isn't already in queue (uses the set to check, since you can't check the queue directly)
                self.spotifyCallQueue.put(nextCall)
                # adds the call to the queue
                self.spCallQueueTracker.add(nextCall)
                # also adds the call into the set

        return futureObj
        # returns the future object so the function can wait for the result

    def spotifyAPIPrepper(self):
        """Function that prepares the calls for spotifyAPICall"""
        while True:
        # while the function is running, keeps running requests (only when it's ready, prevents multiple calls at once)

            nextAPICall = self.spotifyCallQueue.get(block = True)
            # grabs the next call from the queue (removes it at the same time), blocks progress until there's something in the queue
            self.spCallQueueTracker.remove(nextAPICall)
            # deletes the 0th element (first), since that's the same element the queue stores
            call, link, future = nextAPICall
            # splits the queue item into its call, link and future components

            self.controlList = ["pause", "resume", "skip", "previous"]
            # makes a list of the playback control options (these don't have special conditions and don't return anything)

            if call == "playback":
                # if the call is to get new data
                success = self.spotifyAPICall(call)
                # calls spotifyAPICall with just a playback request

            elif call == "playlist":
                # if the call is to get playlist information
                success = self.spotifyAPICall(call, link)
                # calls spotifyAPICall with a playlist command and a link
            
            elif call in self.controlList:
                # if the call is a part of the playback control list (no returns)
                success = self.spotifyAPICall(call)
                # simply passes the call to spotifyAPICall
            
            elif call == "queue":
                # if the call is to add an item to queue
                success = self.spotifyAPICall(call, link)
                # calls the spotifyAPICall with a queue command and a link

            future.set_result(success)
            # sets the future object's return to be the success (if there's a return from the API call, it gets passed back)
            time.sleep(1)
            # waits a second before even starting next call

    def spotifyAPICall(self, call:str, URI:str = None):
        """Function to perform Spotify API calls and handle errors gracefully"""

        tokenRefresh = False
        # a boolean to determine whether to print the token refresh or reconnect text (purely QoL)
        internalError = False
        # a boolean to determine if the error was Spotify's internal error (purely QoL)

        for attempt in range(3):
            # tries a max of 3 times to get Spotify data (typically succeeds 1st try, so if it doesn't work in 3, there's a bigger issue)    
            try:
                ### API Requests / Returns ###
                if call == "playback":
                    # if the request is for playback
                    success = main.current_playback()
                    # gets the current playback
                elif call == "playlist":
                    # if the request is for a playlist's details
                    playlist = main.playlist(URI)
                    # gets the playlist info via URI (takes ID, not link)
                    try:
                        # tries to *also* get the number of tracks
                        tracks = main.playlist_items(URI, fields="total")
                        # saves the number of tracks in "tracks"
                        success = playlist, tracks
                        # turns the return into a tuple of the playlist and track information
                    except:
                        # if it can't (error for some reason or another)
                        success = playlist, 0
                        # turns success into a tuple, so that the calling function knows there's no track information

                ### API Push / No Return ###
                elif call == "queue":
                    # if the call is to add a song to queue
                    try:
                        package = main.track(URI)
                        # sends the URI to Spotify to get the track's details
                        if package:
                            # ensures the track information is received first
                            trackName = package.get("name")
                            # gets the name of the track first
                            trackArtistDict = package.get("artists")[0]
                            # gets the dictionary of the first artist
                            trackArtist = trackArtistDict.get("name")
                            # gets the artist name
                            main.add_to_queue(URI)
                            # pushes the URI into the Spotify queue
                            success = f"Queued: {trackName} by {trackArtist}"
                            # creates a string from the track and artist
                            print(f"{Time()}[spAPI]: {success}")
                            # prints a confirm message with the song name
                    except:
                        print(f"{Time()}[spAPI]: Queue failed")
                        # prints a fail message
                        success = f"Unable to queue"

                ### Controls / No Return ###
                elif call == "pause":
                    # if the call is to pause playback
                    playing = main.current_playback()
                    # grabs the current playback status
                    if playing and playing.get("is_playing", False):
                        # checks if the playback state is valid and if it's playing 
                        success = main.pause_playback()
                        # pauses the playback
                        print(f"{Time()}[spAPI]: Paused playback")
                        # prints a confirm message
                    else:
                        print(f"{Time()}[spAPI]: Playback already paused")
                        # prints a no-no message
                        success = None
                elif call == "resume":
                    # if the call is to resume playback
                    playing = main.current_playback()
                    # grabs the current playback status
                    if not playing or not playing.get("is_playing", False):
                        # checks if the playback state is valid and if it's paused (not playing)
                        success = main.start_playback()
                        # "starts" playback (continue)
                        print(f"{Time()}[spAPI]: Resumed playback")
                        # prints a confirm message
                    else:
                        print(f"{Time()}[spAPI]: Already playing")
                        # prints a no-no message
                        success = None
                elif call == "skip":
                    # if the call is to skip a track
                    playing = main.current_playback()
                    # grabs the current playback status
                    if playing and playing.get("item"):
                        # checks if the playback state is valid 
                        success = main.next_track()
                        # goes to next track (skips)
                        print(f"{Time()}[spAPI]: Skipped track")
                        # prints a confirm message
                    else:
                        print(f"{Time()}[spAPI]: Can't skip")
                        # prints a no-no message
                        success = None
                elif call == "previous":
                    # if the call is to go back to previous track
                    playing = main.current_playback()
                    # grabs the current playback status
                    if playing and playing.get("is_playing", False):
                        # checks if the playback state is valid and if it's playing 
                        success = main.previous_track()
                        # goes back to previous track
                        print(f"{Time()}[spAPI]: Went back to previous track")
                        # prints a confirm message
                    else:
                        print(f"{Time()}[spAPI]: Couldn't go back")
                        # prints a no-no message
                        success = None

                ### Unregistered Call ###
                else:
                    raise ValueError(f"Unregistered API call: {call}")
                    # if an unintended call sneaks through

                ### Connection Reacquisition ###
                if attempt != 0 and not tokenRefresh:
                    # if it's not the first attempt, meaning the reconnect attempt print has already been pushed once after an error
                    print(f"{Time()}[spAPI]: Reconnect successful!")
                    # prints user update
                elif tokenRefresh:
                    # if the tokenRefresh variable is set to true, means a connectionError occurred at least once
                    print(f"{Time()}[spAPI]: Token refreshed successfully!")
                    # prints user update

                # if it works, returns the Spotify API package (dictionary)
                return success
                # sends back the successfully found dictionary to the calling function (should only be looper)

            except (SpotifyException, requests.exceptions.RequestException, ConnectionResetError) as error:
                # if it fails to acquire a Spotify playback package
                if isinstance(error, requests.exceptions.ConnectionError):
                    # if the error is a connection error (token expired)
                    print(f"\n{Time()}[spAPI]: Refreshing Spotify token")
                    # doesn't sleep because this is a token error and should get fixed nearly instantly
                    # expected to print just about every 3600 seconds (1h)
                    tokenRefresh = True
                    # sets the tokenRefresh mode to true so it prints the token text on success
                elif isinstance(error, requests.exceptions.ReadTimeout):
                    # if the error is a read timeout (sort of random)
                    print(f"{Time()}[spAPI]: Spotify API timeout, retrying in 5 seconds ({attempt+1}/3)")
                    time.sleep(2)
                    # sleeps for 2 seconds (because there's a function-wide 3-second cooldown added on top)
                elif isinstance(error, SpotifyException) and error.http_status == 403:
                    # if the error is 403 (forbidden)
                    print(f"{Time()}[spAPI]: Spotify API call failed (Code 403), action not allowed")
                    # prints an "error" message (403 is the result of the API not being able to do something, like pause a paused song)
                    break
                    # breaks here (doesn't let the attempts continue)
                elif isinstance(error, SpotifyException) and error.http_status == 500:
                    # if the error is 500 (internal error fail)
                    print(f"{Time()}[spAPI]: Spotify internal error (Code 500). Attempting to reconnect ({attempt+1}/3)]")
                    # prints an error message
                    internalError = True
                    # should never happen, but very very rarely does
                    time.sleep(2)
                    # adds 2 seconds of sleep (just to slow down, maybe catch a lucky reconnect)
                elif isinstance(error, SpotifyException) and error.http_status == 400:
                    # if the error is 400 (bad syntax, likely a faulty link)
                    print(f"{Time()}[spAPI]: Faulty link or call syntax, can't process request")
                    # prints "error" message
                    break
                    # stops the try loop (if it's faulty, no point in pushing again)
                else:
                    # if the error is anything else
                    print(f"{Time()}[spAPI]: Spotify errored due to {error}.\n{Time()}[INFO]: Attempting to reconnect ({attempt+1}/3)")
                    # prints generic error message

                ### Too Many Errors ###

                if attempt == 2 and not internalError:
                    # if it's the last attempt (range(3) = 0,1,2) and it fails
                    print(f"{Time()}[CRITICAL]: All attempts to reconnect to Spotify API failed due to {error}\n\nPlease manually restart SBO. Exiting...")
                    time.sleep(600)
                    raise SystemExit
                    # prompts user, then exits
                elif attempt == 2 and internalError:
                    # if it's the last attempt and fails due to internal error
                    print(f"{Time()}[CRITICAL]: All attempts to reconnect to Spotify API failed due to Spotify's internal error.\n\nPlease manually restart SBO. Exiting...")
                    time.sleep(600)
                    raise SystemExit
                    # prompts user, then exits

            time.sleep(3)
            # waits 3 seconds to give it some time between tries

        self.spotifyCallQueue.task_done()
        # tells the queue the task is complete

        return {}
        # on fail, returns an empty dictionary



### Web Host / Listener ###



def webHostListener():
    """Websocket message host/listener"""
    print(f"{Time()}[PTP]: Waiting for SBO-Bot to connect")
    # prints the message on program start

    while True:
        client_socket, client_address = webHost.accept()
        # waits for a client connection, in a while loop so it can reconnect if it ever disconnects
        print(f"{Time()}[PTP]: SBO-Bot connected")
        # prints a Python to Python (Peer to Peer) inform when Bot connects successfully

        while True:
            # while the program is running
            rawMessage = client_socket.recv(1024)
            # grabs any messages sent (1024 bytes max, shouldn't use more than a few)

            if not rawMessage:
                # if the message is empty (disconnect)
                break
                # breaks to reset the connection

            message = rawMessage.decode().strip()
            # decodes it (bytes -> string) and strips empty space

            print(f"{Time()}[PTP]: Command received:", message)
            # prints a Python to Python (Peer to Peer) inform

            botCommand(message, client_socket)
            # calls botCommand with the decoded/stripped message, as well as the client socket (to pass back messages)


### Bot Commands ###


def botCommand(command: str, client_socket):
    """Helper function to pick what control function to call"""
    global csPlaylistID
    # grabs the current song's playlist ID from global variable
    playbackCommands = {
        "Skip": skip,
        "Pause": pause,
        "Resume": resume,
        "Previous": previous
    }
    # list of playback controlling commands

    if command in playbackCommands:
        # if the command is one of the playback controls
        playbackCommands[command]()
        # constructs a call dynamically from the command and calls the function
        return
        # stops checks

    if command.startswith("Playlist"):
        # if the command starts with "playlist"
        playlistID = csPlaylistID
        # saves the current song's playlist's ID as playlistID
        playlistInfo(playlistID, client_socket)
        # sends a command to the playlist info request function to add the ID into the Spotify call queue
        return
        # stops checks

    if command.startswith("Queue:"):
        # if the command starts with "queue"
        x, uri = command.split(" ", 1)
        # splits the command into scrap (command) and the URI to pass
        queueTrack(uri, client_socket)
        # sends a command to the queue function to add the URI/URL/ID into the Spotify queue
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
    spotifyQueueInstance.queueManager("skip")
    # calls the queue manager to add a skip call to the call queue

def pause():
    """Pauses playback"""
    spotifyQueueInstance.queueManager("pause")
    # calls the queue manager to add a pause call to the call queue

def resume():
    """Resumes playback"""
    spotifyQueueInstance.queueManager("resume")
    # calls the queue manager to add a resume call to the call queue

def previous():
    """Goes back to previous song"""
    spotifyQueueInstance.queueManager("previous")
    # calls the queue manager to add a previous call to the call queue

def queueTrack(link: str, client_socket):
    """Queues a given song via Spotify link"""
    futureQT = spotifyQueueInstance.queueManager("queue", link)
    # calls the queue manager to add a link to the play queue
    trackName = futureQT.result()
    # gets the result via future object
    client_socket.sendall(trackName.encode())

def playlistInfo(link: str, client_socket):
    """Requests playlist information via Spotify link"""
    if link != "Not a playlist":
        # if the current link is NOT set to not a playlist (SBO has detected it's not a playlist and thus set it to that string) 
        futurePL = spotifyQueueInstance.queueManager("playlist", link)
        # calls the queue manager to add a playlist info request to the call queue
        playlistData, playlistTracks = futurePL.result()
        # gets the results via a future object (waits until it's ready) (returns a tuple of data, tracks)
        if playlistTracks:
            # if the track dictionary exists and is valid
            playlistTracks = playlistTracks.get("total")
            # gets the number only
        else:
            playlistTracks = "a number of"
            # creates a generic string instead
        if playlistData:
            # if there's a return that contains data
            isPublic = playlistData.get("public", False) == True
            # checks if the playlist is public, defaults to False (if the return is True, returns True, else False)
            playlistName = playlistData.get("name", "Unknown Playlist")
            # grabs the playlist name from the dictionary (defaults to Unknown Playlist if can't find)
            if isPublic:
            # if the playlist is public
                try:
                # tries to grab the data
                    urls = playlistData.get("external_urls", {})
                    # gets the urls first, uses an empty dict if not found
                    owner = playlistData.get("owner", {})
                    # gets the owner info first, uses an empty dict if not found
                    playlistURL = urls.get("spotify", "Link unavailable")
                    # grabs the Spotify URL from the external urls
                    playlistOwner = owner.get("display_name", "Mystery Owner")
                    # grabs the owner's name from the owner sub-dictionary
                    playlistNameStr = f"{playlistName} by {playlistOwner} with {playlistTracks:,.0f} songs. {playlistURL}"
                    # constructs a full response from the given info
                except Exception as fail:
                # if it fails to get valid data from the dictionary (sometimes Spotify sends bricked dictionaries that don't include everything)
                    print(f"{Time()}[spAPI]: Failed to construct playlist information fully due to error {fail}")
                    # console print of failure
                    playlistNameStr = f"A playlist named {playlistName}, further information unavailable"
                    # constructs a response from available data (name)
            else:
            # if the playlist is private
                playlistNameStr = f"A private playlist named {playlistName}"
                # constructs a response to not include a link or anything, just a name
        else:
            # if the return has no data
            playlistNameStr = f"Couldn't find specified playlist"
            # constructs a response to inform of an error
    else:
        playlistNameStr = f"Not currently listening to a playlist"
        # if the playlist link is set to a "not a playlist" string, it means the track is being listened to off-playlist
    client_socket.sendall(playlistNameStr.encode())
    # sends the response back to SBO-Bot to reply with in chat


### Color Changing ###


def colorChanger(func: str, color: str):
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

def songColor(color: str):
    """Changes the color of the song text"""
    global songColorHex
    if color == "clear":
        # if the command is to clear, not to set a color
        songColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Song text color cleared")
        # color user inform
    else:
        songColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Song text color set to: {color}")
        # color user inform

def textColor(color: str):
    """Changes the color of the overlay text"""
    global textColorHex
    if color == "clear":
        # if the command is to clear, not to set a color
        textColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Text color cleared")
        # color user inform
    else:
        textColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Text color set to: {color}")
        # color user inform

def barColor(color: str):
    """Changes the color of the progress bar"""
    global barColorHex
    if color == "clear":
        # if the command is to clear, not to set a color
        barColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Progress bar color cleared")
        # color user inform
    else:
        barColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Progress bar color set to: {color}")
        # color user inform

def overlayColor(color: str):
    """Changes the color of the overlay borders"""
    global overlayColorHex
    if color == "clear":
        # if the command is to clear, not to set a color
        overlayColorHex = "Clear"
        # sets the field to "Clear" so that SBO-WS can add the default value
        print(f"{Time()}[RGBA]: Overlay color cleared")
        # color user inform
    else:
        overlayColorHex = color
        # sets the color to match
        print(f"{Time()}[RGBA]: Overlay color set to: {color}")
        # color user inform



### SBO WebSocket ###



def runSBOws() -> subprocess.Popen:
    """Function to start the SBO-WS.exe"""
    with subprocess.Popen([sbowsPath], cwd=sbowsDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as sbowsPrint:
        # opens the SBO-WS.exe file and reads its output
        for line in sbowsPrint.stdout:
            # every time a new line is sent
            print(f"{Time()}[WS]: {line.rstrip()}")
            # prints the line (clears right side)



### Twitch Bot ###



def runSBOBot() -> subprocess.Popen:
    """Function to start the SBO Twitch Bot"""
    with subprocess.Popen([sboBotPath], cwd=sboBotDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as sboBotPrint:
        # opens the SBO-Bot.exe file and reads its output 
        for line in sboBotPrint.stdout:
            # every time a new line is sent
            print(f"{Time()}[SBOT]: {line.rstrip()}")
            # prints the line (clears right side)



### Song Data File Field Selection/Creation ###



def song():
    """The function that handles all song data gathering and parsing, as well as pushing to the websocket via text"""
    global currentInfo, trackCounter, oldCount, songColorHex, textColorHex, barColorHex, overlayColorHex
    global lastSong, lastArtist, lastPlaylistURL, updateProgress, csPlaylistID
    # pulls some global variables to local

    while True:

        songEvent.wait()
        # waits for looper() to set an event

        songNameList = []
        # creates an empty list for strings to get added into as the loop progresses 

        csArtistString = []
        # creates an empty list for artists to get added into as the loop progresses

        songChanged = False
        # a function-contained boolean to check if the song changed later on (used to change the previous song/artist/url)

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

            songChanged = True
            # changes the songChanged boolean to true, tells the loop to update the song names later

        if not isLocalSong and csItem:
            # can't access these if the playing song is local or csItem is None
            cstrackURL = csItem.get("external_urls")
            # stores the list that contains track's url
            csURL = cstrackURL.get("spotify")
            # grabs the spotify track URL
            csPlaylist = csFull.get("context")
            # stores the list that contains the playlist/artist/album url
            csContextType = csPlaylist.get("type")
            # gets the context's type (this can be "playlist", "artist", "album" or "show")
            if csContextType == "playlist":
                # if the "context's" type is playlist
                csPlaylistID = csPlaylist.get("uri").split(":")[-1]
                # grabs the playlist ID by getting the playlist's URI (spotify:playlist:base62) and only taking the ID (base62)
            else:
                # if the context doesn't match
                csPlaylistID = "Not a playlist"
                # stores a preset string 
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

        now = round(time.time(), 0)
        # saves the current time (SBO-WS can read this and see if it should do anything)


        ### SBO-WS Text File Writer ###


        sboFull = (
                    f"Song Name = {sboSongName}\n"
                    f"Artist Name = {sboArtistName}\n"
                    f"Album Name = {sboAlbumName}\n"
                    f"Album URL = {sboAlbumURL}\n" 
                    f"Spotify URL = {sboURL}\n"
                    f"Spotify Image = {csCover}\n"
                    f"Playlist URL = {csPlaylistURL}\n"
                    f"UNIX Start = {str(csUnixStart)}\n"
                    f"UNIX End = {str(csUnixEnd)}\n"
                    f"Pause State = {str(paused)}\n"
                    f"Track ID = {str(trackCounter)}\n"
                    f"Song Color = {songColorHex}\n"
                    f"Text Color = {textColorHex}\n"
                    f"Bar Color = {barColorHex}\n"
                    f"Overlay Color = {overlayColorHex}\n"
                    f"Last Song = {lastSong}\n"
                    f"Last Artist = {lastArtist}\n"
                    f"Last Playlist URL = {lastPlaylistURL}\n"
                    f"Progress Mismatch = {updateProgress}\n"
                    f"Timestamp = {now}"
                    )
        # merges all the song/color/other information together, split by newlines
        
        with open(sbotxtPath, "w", encoding="utf-8") as txt:
            # opens the sbo text file
            txt.write(sboFull)
            # writes the full song information to the text file
            print(f"{Time()}[INFO]: sbo.txt updated")
            # prints an update

        if songChanged:
            # if the song has changed (changes after the text file to prevent the songs being the same
            lastSong = sboSongName
            # sets the previous song to match
            lastArtist = sboArtistName
            # sets the previous artist to match
            lastPlaylistURL = csPlaylistURL
            # sets the previous playlist URL match
            songChanged = False
            # shouldn't matter, since songChanged is self-contained and should default to false every loop, but just in case, sets to False

        songEvent.clear()
        # clears the event queue, ready to get new requests



### Information Checking Loop ###



def looper():
    """Function that checks song info on a loop"""
    global currentURI, currentInfo, pauseUpdated, trackCounter, callSong, updateProgress
    # grabs the "global" variables (outside the function) as local variables
    while True:
        # this loop checks if the song playing is the same as the previous update, waits if yes, updates the song to match if not

        loopFuture = spotifyQueueInstance.queueManager("playback", None)
        # sends a call to the Spotify API call queue manager to get a new playback dictionary

        info = loopFuture.result()
        # picks up all the info the Spotify API function sends (dictionary)

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
        timeNow = int(time.time())
        # grabs the current time
        songStart = int(timeNow - songProg)
        # stores the start time of the song by taking current time and subtracting progress
        playing = info.get("is_playing")
        # checks the pause state (True if playing, False if not)

        if currentURI is None:
            # when the program first starts, the currentURI will be "None", this updates it, along with other variables
            currentURI = songURI
            # sets the current song to match 
            storedStart = songStart
            # updates the timestamp to match
            expectProg = int(timeNow - songStart)
            # calculates the expected progress from the current time - the starting timestamp
            progressMismatch = False
            # initialises the progress boolean as false
            trackCounter += 1
            # adds 1 to counter
            songEvent.set()
            # since this only runs when the program first starts, sets an event immediately to song, to refresh data
            print(f"{Time()}[SONG]: First song: {songName}, has been successfully processed\n")
            # user inform on first song

        songDur = int((info.get("item")).get("duration_ms")/1000)
        # grabs both the current time and length of the song (in seconds)
        songLeft = (songDur - songProg)
        # calculates the time left on the song
        progressOffset = abs(songProg - expectProg)
        # checks if the difference between the Spotify given progress and the calculated progress

        if (progressOffset >= 6):
            # checks if there's a mismatch between expected and real progress of > 6 seconds (generally it's ~2-3 seconds)
            progressMismatch = True
            # if there is, sets the flag to true (will cause an update)
            expectProg = int(timeNow - songStart)
            # calculates the expected progress from the current time - the starting timestamp 
        else:
            # if the mismatch isn't big enough, re-assigns the variable wtih a new value
            expectProg = int(timeNow - songStart)
            # calculates the expected progress from the current time - the starting timestamp 

        if (currentURI != songURI) or ((songStart-5) > storedStart) or (pauseUpdated and playing) or progressMismatch:
        # if there's a reason to update the text file;
        # a song change (if the URI has changed)
        # the starting timestamps don't match
        # if there's a pause or the start timestamp is higher than the stored timestamp) or if the pause has been triggered

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
            if progressMismatch:
                # checks if there was a progress mismatch
                progressMismatch = False
                # sets the mismatch flag to false
                updateProgress += 1
                # adds 1 to the updateProgress counter

            if pauseUpdated:
                # if it's playing and the pauseUpdate has been set to true
                pauseUpdated = False
                # sets the pauseUpdated to false, so it doesn't run twice
            else:
                # if it's playing but pauseUpdate is false
                trackCounter += 1
                # adds 1 to counter (means track has changed)

            time.sleep(1.5)
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



spotifyQueueInstance = SpotifyQueue(main, spotifyLock)
# creates the Spotify queue instance
spotifyQueueRunner = threading.Thread(target = spotifyQueueInstance.spotifyAPIPrepper)
# creates the Spotify queue thread for APIPrepper
spotifyQueueRunner.start()
# starts the spotifyQueue thread


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