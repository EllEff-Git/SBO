import asyncio, os, sys, json, time, configparser
# Required for file directory grabs, reads, asynchronous functions, etc
import websockets, uvicorn, requests
# Required for websocketing and site management
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# Required for web server hosting
from fastapi.responses import FileResponse
# Required for getting status from server


SBO_WSver = "v0.3.08.0412"
"""The program version (y.m.dd.hhmm)"""

### Directories ###


if getattr(sys, "frozen", False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    """The base directory of the program, where SBO-WS.exe resides"""
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    """The base directory of the program, where SBO-WS.exe resides"""

sboTxt = os.path.join(directory, "sbo.txt")
"""Stores the full path of the sbo.txt file"""
site = os.path.abspath(os.path.join(directory, "..", "Web", "index.html"))
"""Stores the full path of the index.html file"""
jsonCfg = os.path.join(directory, "config.json")
"""Stores the full path of the config.json file"""

### Variables ###

program = FastAPI()
"""Creates a FastAPI program"""
clients = set()
"""Creates a set/collection of elements"""

### Required ###

Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
"""The configuration file reader"""
ConfigPath = os.path.join(directory, "..", "config.ini")
"""The directory where the config sits in"""
Config.read(ConfigPath, "utf8")
# Where the config is read from, with UTF-8 format

### Function ###

httpPort = Config.getint("Function", "http_Port")
"""The websocket port (4-digit int)"""
enableScrolling = Config.getboolean("Function", "enable_Text_Scrolling")
"""Whether to enable text scrolling in HTML player (boolean)"""

### Visuals ###

playerWidth = Config.getint("Visuals", "player_Width")
"""The width of the player in HTML (int, pixels)"""
playerHeight = Config.getint("Visuals", "player_Height")
"""The height of the player in HTML (int, pixels)"""
playerOpacity = Config.getfloat("Visuals", "player_Opacity")
"""The opacity of the player in HTML (float)"""
artistPrefix = Config.get("Visuals", "artist_Prefix")
"""A prefix string for the artist field (string)"""
albumPrefix = Config.get("Visuals", "album_Prefix")
"""A prefix string for the album field (string)"""

### Title ###

titleStyle = Config.get("Title", "title_Style").lower()
"""The title styling in HTML (string)"""
titleWeight = Config.get("Title", "title_Weight")
"""The title font weight in HTML (string)"""
try:
    # tries to change the titleWeight to an integer (if it's stores as such)
    titleWeight = int(titleWeight)
except:
    # if it can't save as integer, turns into lowercase
    titleWeight = titleWeight.lower()

titleColor = "#" + Config.get("Title", "title_Color")
"""The color of the title txt in HTML (hex)"""

### Support ###

supportStyles = Config.get("Support", "support_Styles").lower()
"""The supporting string styling in HTML (string)"""
supportWeights = Config.get("Support", "support_Weights")
"""The supporting string weight in HTML (string)"""
try:
    # tries to change the supportWeights to an integer (if it's stores as such)
    supportWeights = int(supportWeights)
except:
    # if it can't save as integer, turns into lowercase
    supportWeights = supportWeights.lower()

supportColors = "#" + Config.get("Support", "support_Colors")
"""The color of text elements in HTML (hex)"""

### Border ###

borderStyle = Config.get("Border", "border_Style").lower()
"""The border styling in HTML (string)"""
borderColor = "#" + Config.get("Border", "border_Color")
"""The color of the border element in HTML (hex)"""

### Progress Bar ###

progressBarDefault = "#" + Config.get("Bar", "progress_Bar_Color")
"""The progress bar's fill color in HTML (hex)"""
progressBarPaused = "#" + Config.get("Bar", "progress_Bar_Paused")
"""The progress bar color when paused in HTML (hex)"""


print(f"Websocket program {SBO_WSver} started successfully", flush=True)
# quick user update


HTMLconfig = {
    "httpPort": httpPort,
    "playerWidth": playerWidth,
    "playerHeight": playerHeight,
    "playerOpacity": playerOpacity,
    "titleStyle": titleStyle,
    "titleWeight": titleWeight,
    "titleColor": titleColor,
    "supportStyles": supportStyles,
    "supportWeights": supportWeights,
    "supportColors": supportColors,
    "borderStyle": borderStyle,
    "borderColor": borderColor,
    "progressBarColor": progressBarDefault,
    "progressBarPaused": progressBarPaused,
    "enableScrolling": enableScrolling
}
# assembles a config dictionary that will get passed to HTML


with open(jsonCfg, "w") as htmlcfg:
    # opens the json config file
    json.dump(HTMLconfig, htmlcfg, indent=3) 
    # stores the HTMLconfig inside


print(f"HTML config has been read successfully", flush=True)
# config update


def readSBO():
    """Function to read the sbo.txt file"""
    sbo = {}
    # empty dictionary to store the contents in

    with open(sboTxt, encoding="utf-8") as content:
        # opens the text file with utf-8 encoding
        for line in content:
            # for every line in the file
            if "=" in line:
                # if there's an equals sign (all lines)
                identifier, data = line.strip().split("=", 1)
                # strips and splits the line to the left and right side (identifier and data)
                sbo[identifier.strip()] = data.strip()
                # stores inside the made dictionary as keyed entries

    if artistPrefix:
        # if artistPrefix isn't empty
        artistName = sbo.get("Artist Name")
        artistName = artistPrefix + " " + artistName
        # adds it to the start of the string
        sbo["Artist Name"] = artistName
    if albumPrefix:
        # if albumPrefix isn't empty
        albumName = sbo.get("Album Name")
        albumName = albumPrefix + " " + albumName
        # adds it to the start of the string
        sbo["Album Name"] = albumName

    sbo["Pause State"] = sbo.get("Pause State", "False").strip().lower() == "true"
    # grabs the pause state and ensures it's a boolean here

    return sbo
    # returns the dictionary to the calling function


def unixConverter(sbo):
    """Function that turns UNIX timestamps into a progress bar"""
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


@program.get("/")
# gets the HTML page
def index():
    return FileResponse(site)


@program.get("/config.json")
# gets the config file
def configPush():
    return FileResponse(jsonCfg, media_type="application/json")
    # sends the json dictionary that python made from config.ini


@program.websocket("/ws")
# handles the websocket
async def websocket(ws: WebSocket):

    await ws.accept()
    clients.add(ws)

    try:
    # goes to send the first package immediately

        sbo = readSBO()
        # calls readTTV and then stores the dictionary here as ttv
        songProg, songDur = unixConverter(sbo)
        # stores the progress and duration times from unixConverter

        payload = json.dumps({
            "title": sbo.get("Song Name", ""),
            "artist": sbo.get("Artist Name", ""),
            "album": sbo.get("Album Name", ""),
            "cover": sbo.get("Spotify Image", ""),
            "progress": songProg,
            "duration": songDur,
            "paused": sbo.get("Pause State", "")
        })

        await ws.send_text(payload)
        # sends the payload

        while True:
        # this runs constantly after

            await asyncio.sleep(1)
            # waits a second

            sbo = readSBO()
            # calls readTTV and then stores the dictionary here as ttv
            songProg, songDur = unixConverter(sbo)
            # stores the progress and duration times from unixConverter

            payload = json.dumps({
                "title": sbo.get("Song Name", ""),
                "artist": sbo.get("Artist Name", ""),
                "album": sbo.get("Album Name", ""),
                "cover": sbo.get("Spotify Image", ""),
                "progress": songProg,
                "duration": songDur,
                "paused": sbo.get("Pause State", "")
            })
            # constructs a "payload" (data to send to html) out of the read file data

            await ws.send_text(payload)
            # sends the payload to websocket

    except (WebSocketDisconnect, ConnectionResetError):
        # any "disconnect" (leaving the site)
        pass

    except Exception as ex:
        # if it somehow fails
        print("Websocket error", ex, flush=True)

    finally:
        # deletes itself when the connection ends
        clients.discard(ws)


if __name__ == "__main__":
    # runs the socket starter
    print(f"Websocket started!", flush=True)
    uvicorn.run(program, host="127.0.0.1", port=httpPort, log_level="warning", access_log=False)
    # starts the web server as the FastAPI program, using a preset IP of (local) with the configurable httpPort - disables non-error prints and http requests