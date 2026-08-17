import asyncio, os, sys, json, time
# Required for file directory grabs, reads, asynchronous functions, etc
import uvicorn, socket, threading
# Required for websocketing and site management
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# Required for web server hosting
from fastapi.responses import FileResponse
# Required for getting status from server
from contextlib import asynccontextmanager
# Required for managing the SBO -> HTML function
from SBOver import Version
# Version manager



sboWSver = Version
"""The program version (Y.M.DD.HHMM)"""



### Directories ###

directory = os.path.dirname(sys.executable)
"""The base directory of the program, where SBO-WS.exe resides"""

mainFolder = os.path.join(directory, "..", "..")
"""The main folder of SBO (2 folders up)"""
configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "SBO")
"""The folder path that should contain all the configuration files"""
site = os.path.abspath(os.path.join(mainFolder, "index.html"))
"""Stores the full path of the index.html file"""


funcConfigPath = os.path.join(configFolderPath, "functionConfig.json")
"""The full path to the functional config file (C:/Users/<user>/AppData/Local/SBO/functionConfig.json)"""
funcConfig = {}
"""The dictionary that contains all of the functional configuration"""

sboConfigPath = os.path.join(configFolderPath, "sboConfig.json")
"""The full path to the SBO visual config file (C:/Users/<user>/AppData/Local/SBO/sboConfig.json)"""
sboConfig = {}
"""The SBO configuration dictionary"""

if sys.stdout:
# if launched as a subprocess, and there's a standard output pipe
    sys.stdout.reconfigure(encoding="utf-8")
    # ensures it uses UTF-8 encoding
if sys.stdin:
# same thing, but for input
    sys.stdin.reconfigure(encoding="utf-8")
    # yep


### Variables ###

clients = set()
"""Creates a set/collection of elements"""

skipSBOcfgWin = False
"""Whether the SBO configuration window should be skipped (boolean)"""
addressType = None
"""The config option for the address to use (device/local, string)"""
httpPort = 6868
"""The websocket port (0-65333, int)"""
playerTimeout = 15
"""The time the player needs to be paused for before it hides itself, seconds (int)"""
webHostPort = 6870
"""The port to use for the SBO PTP connection (http_Port + 2, int)"""
enableBot = False
"""Whether to enable the Twitch Bot PTP connection (boolean)"""
enableShaaCompat = False
"""Whether SHAA compatibility should be enabled (boolean)"""

### Visuals ###

artistPrefix = "by"
"""A prefix string for the artist field (string)"""
albumPrefix = ""
"""A prefix string for the album field (string)"""

playerXaxisMod = 0
"""The number of pixels to add to the player width"""
playerYaxisMod = 0
"""The number of pixels to add to the player height"""

defaultSongColor = "ffffff"
"""The default color for song (string, hex)"""
defaultArtistColor = "ffffff"
"""The default color for artist (string, hex)"""
defaultAlbumColor = "ffffff"
"""The default color for album (string, hex)"""
defaultBorderColor = "ffffff, 00ff00, 0000ff"
"""The default color for border (string, hex)"""

defaultBarColor = "1ED760"
"""The default color for progress bar (string, hex)"""
defaultPauseColor = "FF2C00"
"""The default color for paused progress bar (string, hex)"""

### Field Mapper ##

allTypes = {
    "color": ["borderColor", "artistColor", "albumColor", "titleColor", "progressColor"],

    "track": ["title", "artist", "album", "cover", "paused", "id",
            "progress", "duration", "shaa"],

    "full": ["title", "artist", "album", "cover", "paused", "id", 
            "titleColor", "artistColor", "albumColor", "progressColor", "borderColor", 
            "progress", "duration", "shaa"],

    "progress": ["progress"]
}
# a map of what types of fields are added to the payload based on the key given via payloadBuilder
# color only updates the colors (no need to mess with the whole program)
# progress only updates the timestamps (basically just ensuring everything's working smooth)
# track updates all the song-related info (also includes timestamps to match them)
# full updates everything (means both song and at least 1 color has changed)
# progress means the progress change was too large (user skipped a part of song), just sets the progress to match

newColors = asyncio.Queue()
"""A queue to tell the program to send colors via WebSocket"""
stopBotHost = threading.Event()
"""A threading event to kill the SBO -> WS connection (enabled by bot) on exit"""
uviServer = None
"""The uvicorn server setup"""
latestPayload = None
"""Stores the last full payload sent, to pass to new clients on connect"""
updateProgress = False
"""A boolean check to see if a new client has connected (if a progress update should be sent)"""



print(f"HTML overlay program {sboWSver} starting", flush=True)
# quick user update



### Color Split ###

def colorSplitter(colorString: str):
    """Function to split strings of color with no hex marker """

    if "," in colorString:
        # if there's any commas in the color string
        colorString = colorString.replace('"', "")
        # removes quotes it will have from being a string
        splitColors = colorString.split(",")
        # splits the colors into a list by commas
        for color in range(len(splitColors)):
            # goes through the list of colors
            splitColors[color] = "#" + splitColors[color].strip()
            # adds a # to the start of the hex code and strips empty space
        colorString = ", ".join(splitColors)
        # joins the string back together with commas (now with # in front of each code)
    else:
        # if no commas are found (1 color)
        if not colorString.startswith("#"):
        # if the color string doesn't have a # yet
            colorString = f"#{colorString}"
            # adds a # to the front to form a hex code
    return colorString
    # returns the formed color string (with fully-formed hex codes)



### Functional Config ###

def funcConfigManager():
    """Function that manages the functional configuration"""
    global funcConfig, httpPort, webHostPort, addressType, playerTimeout, enableBot, enableShaaCompat
    # global -> local

    if os.path.exists(funcConfigPath):
    # if the config file exists
        try:
        # tries to read the config file (try because it could fail)
            with open(funcConfigPath, "r", encoding="utf-8") as fncCfg:
            # opens the SHAA config
                funcConfig = dict(json.load(fncCfg))
                # stores the loaded config
                httpPort = int(funcConfig.get("httpPort", 6868))
                webHostPort = int(httpPort + 2)
                addressType = funcConfig.get("addressType", "Device")
                playerTimeout = int(funcConfig.get("hidePlayerTimeout", 15))
                enableBot = funcConfig.get("enableBot", True)
                enableShaaCompat = funcConfig.get("enableShaaCompat", False)
                # grabs the variables from the config file
        except Exception as fErr:
        # if the file can't be found/opened
            print(f"Can't open functional configuration file! Please re-run the configurator and verify correct installation ({fErr}, E0)", flush=True)
            # user warn
            raise SystemExit
            # quits
    else:
    # file doesn't exist
        print("Can't find functional configuration file! Please re-run the configurator and verify correct installation (E0)", flush=True)
        # user warn
        raise SystemExit
        # quits



### SBO Config ###

def sboConfigManager():
    """Function that manages the SBO configuration"""
    global sboConfig, artistPrefix, albumPrefix
    global playerXaxisMod, playerYaxisMod
    global defaultSongColor, defaultArtistColor, defaultAlbumColor
    global defaultBorderColor, defaultBarColor, defaultPauseColor
    # global -> local

    if os.path.exists(sboConfigPath):
    # if the config file exists
        try:
        # tries to read the config file (try because it could fail)
            with open(sboConfigPath, "r", encoding="utf-8") as sboCfg:
            # opens the SHAA config
                sboConfig = dict(json.load(sboCfg))
                # stores the loaded config
                artistPrefix = sboConfig.get("artistPrefix", "by")
                albumPrefix = sboConfig.get("albumPrefix", "")
                playerXaxisMod = sboConfig.get("playerXaxis", 0)
                playerYaxisMod = sboConfig.get("playerYaxis", 0)
                defaultSongColor = colorSplitter(sboConfig.get("titleColor", "ffffff"))
                defaultArtistColor = colorSplitter(sboConfig.get("artistColor", "ffffff"))
                defaultAlbumColor = colorSplitter(sboConfig.get("albumColor", "ffffff"))
                defaultBorderColor = colorSplitter(sboConfig.get("borderColors", "ff0000, 00ff00, 0000ff"))
                defaultBarColor = colorSplitter(sboConfig.get("progressColor", "1ED760"))
                defaultPauseColor = colorSplitter(sboConfig.get("progressPauseColor", "FF2C00"))
                # grabs the variables from the config file
        except Exception as fErr:
        # if the file can't be found/opened
            print(f"Can't read SBO configuration file! Please re-run the configurator and verify correct installation ({fErr}, E0)", flush=True)
            # user warn
            raise SystemExit
            # quits
    else:
    # file doesn't exist
        print("Can't find SBO configuration file! Please re-run the configurator and verify correct installation (E0)", flush=True)
        # user warn
        raise SystemExit
        # quits

funcConfigManager()
sboConfigManager()
# runs both config readers to get new variable data



HTMLconfig = {
    "httpPort": httpPort,
    "playerTimeout": playerTimeout,
    "playerXmod": playerXaxisMod,
    "playerYmod": playerYaxisMod,
    "shaaCompat": enableShaaCompat,
    "titleColor": defaultSongColor,
    "artistColor": defaultArtistColor,
    "albumColor": defaultAlbumColor,
    "borderColor": defaultBorderColor,
    "progressBarColor": defaultBarColor,
    "progressBarPaused": defaultPauseColor
}
# assembles a config dictionary that will get passed to the index.html

print(f"HTML config updated", flush=True)
# config read user update



if enableBot:
# if the bot is enabled
    webHost = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # creates the base webHost socket (defines)
    webHost.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # restarts sockets
    webHost.bind(("127.0.0.1", webHostPort))
    # sets the address and port (2 higher than the WS -> overlay)
    webHost.listen()
    # creates a websocket listener connection on localhost
    print(f"Started inter-python connection for SBO -> WS", flush=True)
    # debug print



async def getSBOdata() -> dict:
    """Function to read the SBO data from STDIN and return a modified dictionary"""

    try:
        line = await asyncio.to_thread(sys.stdin.readline)
        # waits for new data from SBO

    except OSError as gErr:
    # OS-level program stop 'error' (expected)
        print("SBO -> WS connection terminated", flush=True)
        # prints error
        return
        # stops

    if not line:
    # if there's nothing (SBO closed)
        uviServer.should_exit = True
        # tells the uvicorn server to close
        return
        # stop

    sbo = json.loads(line)
    # turns into dict form

    if artistPrefix:
        # if artistPrefix isn't empty (config)
        artistName = sbo.get("Artist Name")
        artistName = artistPrefix + " " + artistName
        # adds it to the start of the string
        sbo["Artist Name"] = artistName
        # replaces the original value with the new one

    if albumPrefix:
        # if albumPrefix isn't empty (config)
        albumName = sbo.get("Album Name")
        albumName = albumPrefix + " " + albumName
        # adds it to the start of the string
        sbo["Album Name"] = albumName
        # replaces the original value with the new one 

    return sbo
    # returns the dictionary to the calling function


def unixConverter(sbo: dict) -> tuple[int, int]:
    """Function that turns UNIX timestamps into progress and duration times"""
    try:
        songStart = int(sbo.get("UNIX Start"))
        # gets the timestamp for the song's start from the dictionary
        songEnd = int(sbo.get("UNIX End"))
        # gets the timestamp for the song's end from the dictionary
        timeNow = int(time.time())
        # grabs current time
        songProg = max(0, timeNow - songStart)
        # calculates progress by calculating how many seconds the difference between now and start is
        songDur = max(1, songEnd - songStart)
        # calculates duration by calculating end-start timestamps

        return songProg, songDur
        # returns the timestamps to the calling function

    except Exception:
        # if, for some reason, fails - defaults to 0 and 1 (start/end)
        return 0, 1



def noneRemover(string: str):
    """Function that ensures no "None" values are sent through payload (None breaks JS)"""
    return None if string in (None, "None", "") else string
    # if the given string matches None, "None" or "", it returns None - otherwise returns the string



def payloadBuilder(map: dict, type: str, fields: list) -> str:
    """Dynamically constructs a payload based on the data passed and turns into a json string"""
    # takes a map (dictionary) of data (payloads), the type that triggered the change and the fields that should be added into the payload
    # for example, if a color is set as the type (and fields), it constructs a payload with all the color fields as keys (titleColor, supportColor...) 

    builtPayload = {
        key: map[key] for key in fields if key in map
    }
    # builds the payload from the passed fields, using format of: "map = {key:value}", if key exists

    builtPayload["type"] = type
    # sets the payload's type field to match the passed argument (track, color or progress)

    return json.dumps(builtPayload)
    # returns the full built payload in json format



def webHostListener():
    """Websocket message host/listener"""

    print(f"Waiting for SBO to connect", flush=True)
    # prints the message on program start

    while not stopBotHost.is_set():
    # while the threading event hasn't been called yet
        try:
            webHost.settimeout(1.0)
            # sets a timeout of 1 second per attempt
            try:
            # tries to form a connection...
                client_socket, client_address = webHost.accept()
                # waits for a client connection, in a while loop so it can reconnect
            except socket.timeout:
            # if it can't find it in time
                continue
                # resets loop

            with client_socket:
            # while there's a connection
                while not stopBotHost.is_set():
                # while the stop hasn't been called yet
                    try:
                        rawMessage = client_socket.recv(1024)
                        # grabs any messages sent (1024 bytes max, shouldn't use more than a few)
                        if not rawMessage:
                            # if the message is empty (disconnect)
                            break
                            # breaks to reset the connection

                        message = rawMessage.decode("utf-8").strip()
                        # decodes it (bytes -> string) and strips empty space
                        print(f"HTML command received:", message, flush=True)
                        # prints a Python to Python (Peer to Peer) inform
                        newColors.put_nowait(message)
                        # puts the color list into the queue

                    except ConnectionAbortedError:
                        print(f"Connection aborted by Windows (10053)", flush=True)
                        # generic windows websocket error
                        break
                        # reset

                    except socket.error as soc:
                        print(f"Socket error with command: {soc}", flush=True)
                        # generic error with the socket (ideally not windows)
                        break
                        # reset

        except socket.error as socF:
        # any failed attempts to connect
            if not stopBotHost.is_set():
            # only prints if the stop hasn't been called (if it has, then what's the point of erroring?)
                print(f"Error forming connection: {socF}", flush=True)



async def sendToAll(message: str):
    """Small function to ensure all connected clients receive messages"""
    global clients
    brokenClients = set()
    # creates an empty set of clients that failed to connect

    for client in list(clients):
    # goes through each client in the connected list (global)
        try:
        # tries to send message
            await client.send_text(message)
            # sends the message to a client

        except (WebSocketDisconnect, ConnectionResetError, RuntimeError):
            # if a client is disconnected (refresh, close) or has a runtime error (also due to a client that has disconnected)
            brokenClients.add(client)
            # adds the disconnected client into the set
        except Exception as err:
            # any other error gets caught
            if "Cannot call" in err:
                # if the error is "cannot call "send" once a close message has been sent" (client not connected)
                brokenClients.add(client)
                # adds the disconnected client into the set
            else:
            # if the error is something other than "cannot call"
                print(f"Error with Websocket: {err}", flush=True)
                # user inform on error
                brokenClients.add(client)
                # adds the disconnected client into the set

    for each in brokenClients:
    # goes through each client in the broken client set (if any)
        clients.discard(each)
        # discards each broken client



async def looper():
    """The function that manages the SBO -> HTML process"""
    global allTypes, newColors, latestPayload, updateProgress
    # grabs some variables (payload-related)
    try:
    # goes to send the first package immediately

        sbo = await getSBOdata()
        # calls sbo data grabber and then stores the dictionary here as sbo
        songProg, songDur = unixConverter(sbo)
        # stores the progress and duration times from unixConverter

        initialPayload = {
            "title": sbo.get("Song Name", ""),
            "artist": sbo.get("Artist Name", ""),
            "album": sbo.get("Album Name", ""),
            "cover": sbo.get("Spotify Image", ""),
            "paused": sbo.get("Pause State", False),
            "id": sbo.get("Track ID", ""),
            "titleColor": noneRemover(sbo.get("Song Color")),
            "artistColor": noneRemover(sbo.get("Artist Color")),
            "albumColor": noneRemover(sbo.get("Album Color")),
            "progressColor": noneRemover(sbo.get("Bar Color")),
            "borderColor": noneRemover(sbo.get("Overlay Color"))
        }
        # constructs an initial payload that

        lastPayload = initialPayload.copy()
        # saves a copy of the initial payload payload to compare to later

        initialPayload["progress"] = songProg
        initialPayload["duration"] = songDur
        # adds the timestamp keys after copying (because the progress will change *every* update, and sending a payload because of that is wasteful)

        initialPayload["shaa"] = sbo.get("State") if enableShaaCompat else " "
        # gets the State (contains the "x plays <> y minutes" string) or nothing, if SHAA is disabled

        lastColors = {
            "titleColor": initialPayload["titleColor"],
            "artistColor": initialPayload["artistColor"],
            "albumColor": initialPayload["albumColor"],
            "progressColor": initialPayload["progressColor"],
            "borderColor": initialPayload["borderColor"]
        }
        # stores a map of the last colors sent, to be compared in the next update

        oldTrackID = initialPayload["id"]
        # stores the ID to check for a song change

        oldPauseState = sbo.get("Pause State", False)
        # grabs the first pause state boolean

        oldTimestamp = sbo.get("Timestamp", round(time.time(), 0))
        # stores the initial timestamp (or a rounded timestamp of current)

        builtPayload = payloadBuilder(initialPayload, "full", allTypes["full"])
        # sends all the details to the payloadBuilder and stores the response

        latestPayload = builtPayload
        # stores the complete payload in the global variable

        await sendToAll(builtPayload)
        # sends the payload to websockets

        await asyncio.sleep(2)
        # sleeps 2 seconds after sending initial payload

        while True:
        # this runs constantly after, with a short cooldown, thanks to the "await asyncio.sleep(2)" at the end of the loop

            try:
                # cheks if there are new colors
                message = newColors.get_nowait()
                # if there's new colors, gets the message
                command, colors = message.split(": ")
                # splits the message so that the command stays on its own
                colorMap = {
                    command: colors
                }
                # creates a map with the element and colors

                await sendToAll(payloadBuilder(colorMap, "color", allTypes["color"]))
                # tells the websocket there's new colors, constructs new payload
                newColors.task_done()
                # tells the queue that the task is done

                await asyncio.sleep(2)
                # sleeps for a couple seconds
                continue
                # goes back to loop start

            except asyncio.QueueEmpty:
                # if the queue is empty
                pass
                # goes to next part, because that's expected

            sbo = await getSBOdata()
            # calls readSBO and then stores the dictionary here as sbo
            
            fileTimestamp = sbo.get("Timestamp", round(time.time(), 0))
            # gets the timestamp from the file (or uses current time if it can't find any)

            if (fileTimestamp != oldTimestamp) or updateProgress:
                # if the timestamps are different (means SBO has updated *something*), or there's a request to update progress

            ### Payload Comparison ###

                oldTimestamp = fileTimestamp
                # sets the current timestamp

                songProg, songDur = unixConverter(sbo)
                # stores the progress and duration times from unixConverter

                currentPauseState = sbo.get("Pause State", False)
                # stores the current pause state

                payload = {
                    "title": sbo.get("Song Name", ""),
                    "artist": sbo.get("Artist Name", ""),
                    "album": sbo.get("Album Name", ""),
                    "cover": sbo.get("Spotify Image", ""),
                    "paused": sbo.get("Pause State", False),
                    "id": sbo.get("Track ID", ""),
                    "titleColor": noneRemover(sbo.get("Song Color")),
                    "artistColor": noneRemover(sbo.get("Artist Color")),
                    "albumColor": noneRemover(sbo.get("Album Color")),
                    "progressColor": noneRemover(sbo.get("Bar Color")),
                    "borderColor": noneRemover(sbo.get("Overlay Color"))
                }
                # constructs a new payload

                currentColors = {
                    "titleColor": payload["titleColor"],
                    "artistColor": payload["artistColor"],
                    "albumColor": payload["albumColor"],
                    "progressColor": payload["progressColor"],
                    "borderColor": payload["borderColor"]
                }
                # stores a map of the newly updated colors

                if payload != lastPayload:
                    # if a pause, song change or any color change has happened *or* progress has a mismatch
                    lastPayload = payload.copy()
                    # changes the temp payload variable to match
                    payloadDiff = True
                    # sets the boolean to True
                else:
                    payloadDiff = False
                    # sets the boolean to False

                payload["progress"] = songProg
                payload["duration"] = songDur
                # adds the timestamps *after* checking against the old version

                payload["shaa"] = sbo.get("State") if enableShaaCompat else " "
                # gets the State (contains the "x plays <> y minutes" string)

            ### Track ID Check ###

                if payload["id"] != oldTrackID:
                    # checks if the old track ID matches the new one (song change)
                    oldTrackID = payload["id"]
                    # sets the variable to match
                    songChange = True
                    # sets boolean to True
                else:
                    # if the song hasn't changed
                    songChange = False
                    # sets boolean to False

            ### Color Check ###

                if currentColors != lastColors:
                    # if any of the colors have changed
                    lastColors = currentColors.copy()
                    # copies the current colors to the previous' variable
                    colorChange = True
                    # sets color boolean to True
                else:
                    # if none of the colors have changed
                    colorChange = False
                    # sets color boolean to False

            ### Pause Check ###

                if currentPauseState != oldPauseState:
                    # checks if the previous pause state was the same
                    oldPauseState = currentPauseState
                    # reassigns variable to match
                    pauseChange = True
                    # sets pause boolean to True
                else:
                    pauseChange = False
                    # sets pause boolean to False

            ### Payload Selection ###

                if colorChange and payloadDiff or updateProgress:
                    # if the color has changed AND *any* of the other 3 *or* the progress update is requested
                    # needs to be full, because it'll give *all* relevant information to the new client, including progress
                    builtPayload = payloadBuilder(payload, "full", allTypes["full"])
                    # forms a full payload (track + colors)
                    updateProgress = False
                    # sets the boolean to False so it doesn't re-run accidentally
                    latestPayload = builtPayload
                    # stores the current payload in the global variable

                elif colorChange:
                    # if the color has changed, all the other 3 haven't
                    builtPayload = payloadBuilder(payload, "color", allTypes["color"])
                    # forms only a color payload

                elif songChange or pauseChange:
                    # if either of the track elements has changed, color hasn't (progress doesn't matter because it's included in track)
                    builtPayload = payloadBuilder(payload, "track", allTypes["track"])
                    # forms the track payload
                    latestPayload = builtPayload
                    # stores the current payload in the global variable

                else:
                    # if there's a progress mismatch, but no song or pause change and no color update
                    builtPayload = payloadBuilder(payload, "progress", allTypes["progress"])
                    # forms the progress payload

                await sendToAll(builtPayload)
                # sends the finished payload

            await asyncio.sleep(2)
            # sleeps for 2 seconds between

    except Exception as ex:
    # if it somehow fails
        print(f"Websocket error: {ex}", flush=True)
        # user inform

    except asyncio.CancelledError:
    # if the looper is cancelled (stopped)
        print(f"Shutting down websocket", flush=True)
        # user inform



@asynccontextmanager
async def lifespan(app):
# manages the "lifespan" of the looper function
    looperTask = asyncio.create_task(looper())
    # creates an async task for the looper to run
    try:
        yield
        # lets the rest of the program run normally
    finally:
    # once the program is done (shut down)
        if enableBot:
        # if the bot as enabled and ran
            stopBotHostFunc()
            # calls the function responsible for closing the bot
        try:
            await looperTask.cancel()
            # "cancels" (stops) the looperTask
        except asyncio.CancelledError:
        # if there's an error in cancelling
            pass
            # does nothing



program = FastAPI(lifespan=lifespan)
"""Creates a FastAPI client, adds the lifespan function inside"""



@program.get("/")
# gets the HTML page
async def index():
    return FileResponse(site)
    # pushes the index.html up



@program.get("/config.json")
# gets the config file
async def configPush():
    return HTMLconfig
    # sends the json dictionary that python made from config.ini
    # this can be seen by going to localhost:(port)/config.json



@program.websocket("/ws")
# handles the websocket
async def websocket(ws: WebSocket):
    global clients, updateProgress
    # global -> local

    await ws.accept()
    # accepts the websocket connection and stores the details
    clients.add(ws)
    # adds the websocket connection to the set of clients
    updateProgress = True
    # sets the progress update requirement to True (sends a progress update)

    if latestPayload is not None:
    # checks if the latestPayload is already defined by looper()
        try:
        # if yes
            await ws.send_text(latestPayload)
            # sends the latestPayload (full payload) to the new client
        except Exception:
        # if it fails
            pass
            # does nothing
 
    try: 
    # just starts a while True loop to keep it active
        while True:
        # doesn't really do much
            await ws.receive_text()
            # "awaits" some text (never gets sent, since all clients should be receive-only)
    except WebSocketDisconnect:
    # if there's a disconnect
        pass
        # doesn't do anything
    finally:
    # when the connection ends
        clients.discard(ws)
        # removes the websocket connection



### Stop Bot WS ###

def stopBotHostFunc():
    """Function to stop the Bot -> SBO -> WS connection on exit"""
    stopBotHost.set()
    # sets the threading event to prevent any further calls
    if webHost is not None:
    # if the bot webhost exists
        webHost.close()
        # closes it


if enableBot:
    # if the config option to enable the bot is on
    webHostThread = threading.Thread(target=webHostListener, daemon=True)
    # creates a thread for the webhostlistener to sit in
    webHostThread.start()
    # starts the thread

if addressType == "Device":
    # if the config is set to device-only
    ipAddress = "127.0.0.1"
    # sets the address to device local-only
else:
    # if the config option isn't device-only
    ipAddress = "0.0.0.0"
    # sets the address to network-wide



### Overlay Start ###

async def hostOverlay():
    """Function to host the overlay locally"""
    global uviServer
    # global -> local

    uviConfig = uvicorn.Config(program, host=ipAddress, port=httpPort, log_level="warning", access_log=False)
    # configures the uvicorn web server as the FastAPI program, using the config-based IP, with configurable httpPort (also disables non-error prints and http requests)
    uviServer = uvicorn.Server(uviConfig)
    # forms the uvicorn server based on the config

    print(f"Overlay coming online at {ipAddress}:{httpPort}!", flush=True)
    # prints first, otherwise won't print

    try:
        await uviServer.serve()
        # starts the server
    except OSError as gErr:
    # OS-level program stop 'error' (expected)
        pass
        # does nothing
    finally:
        print("Shutting down overlay host", flush=True)
        # user inform


if __name__ == "__main__":
# at startup
    asyncio.run(hostOverlay())
    # runs the overlay hosting function