import asyncio, os, sys, json, time, configparser
# Required for file directory grabs, reads, asynchronous functions, etc
import uvicorn
# Required for websocketing and site management
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# Required for web server hosting
from fastapi.responses import FileResponse
# Required for getting status from server


SBO_WSver = "v0.3.11.1457"
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
"""Creates a FastAPI client"""
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

defaultTitleColor = "#" + Config.get("Title", "title_Color", fallback="#ffffff")
"""The default color for title (may be overwritten via SBO due to Bot (string, hex))"""

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

defaultSupportColors = "#" + Config.get("Support", "support_Colors", fallback="#ffffff")
"""The default color for support texts (may be overwritten via SBO due to Bot (string, hex))"""

### Border ###

borderStyle = Config.get("Border", "border_Style").lower()
"""The border styling in HTML (string)"""
defaultBorderColor = "#" + Config.get("Border", "border_Color", fallback="#ffffff")
"""The default color for border (may be overwritten via SBO due to Bot (string, hex))"""

### Progress Bar ###

defaultBarColor = "#" + Config.get("Bar", "progress_Bar_Color")
"""The default color for bar (may be overwritten via SBO due to Bot (string, hex))"""
progressBarPaused = "#" + Config.get("Bar", "progress_Bar_Paused")
"""The progress bar color when paused in HTML (hex)"""

### Field Mapper ##

allTypes = {
    "color": ["titleColor", "supportColor", "progressColor", "borderColor"],

    "track": ["title", "artist", "album", "cover", "paused", "id",
            "progress", "duration"],

    "full": ["title", "artist", "album", "cover", "paused", "id", 
            "titleColor", "supportColor", "progressColor", "borderColor", 
            "progress", "duration"]
}
# a map of what types of fields are added to the payload based on the key given via payloadBuilder
# color only updates the colors (no need to mess with the whole program)
# progress only updates the timestamps (basically just ensuring everything's working smooth)
# track updates all the song-related info (also includes timestamps to match them)
# full updates everything (means both song and at least 1 color has changed)


print(f"HTML overlay program {SBO_WSver} starting", flush=True)
# quick user update


HTMLconfig = {
    "httpPort": httpPort,
    "playerWidth": playerWidth,
    "playerHeight": playerHeight,
    "playerOpacity": playerOpacity,
    "titleStyle": titleStyle,
    "titleWeight": titleWeight,
    "titleColor": defaultTitleColor,
    "supportStyles": supportStyles,
    "supportWeights": supportWeights,
    "supportColors": defaultSupportColors,
    "borderStyle": borderStyle,
    "borderColor": defaultBorderColor,
    "progressBarColor": defaultBarColor,
    "progressBarPaused": progressBarPaused,
    "enableScrolling": enableScrolling
}
# assembles a config dictionary that will get passed to HTML/localhost


with open(jsonCfg, "w") as htmlcfg:
    # opens the json config file
    json.dump(HTMLconfig, htmlcfg, indent=3) 
    # stores the HTMLconfig inside


print(f"HTML config updated", flush=True)
# config read user update


def readSBO() -> dict:
    """Function to read the sbo.txt file and return "sbo", a dictionary"""
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
        # if artistPrefix isn't empty (config)
        artistName = sbo.get("Artist Name")
        artistName = artistPrefix + " " + artistName
        # adds it to the start of the string
        sbo["Artist Name"] = artistName

    if albumPrefix:
        # if albumPrefix isn't empty (config)
        albumName = sbo.get("Album Name")
        albumName = albumPrefix + " " + albumName
        # adds it to the start of the string
        sbo["Album Name"] = albumName

    sbo["Pause State"] = sbo.get("Pause State", "False").strip().lower() == "true"
    # grabs the pause state and ensures it's a boolean here

    return sbo
    # returns the dictionary to the calling function


def unixConverter(sbo: dict) -> int:
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


def noneRemover(string: str) -> str:
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


@program.get("/")
# gets the HTML page
def index():
    return FileResponse(site)


@program.get("/config.json")
# gets the config file
def configPush():
    return FileResponse(jsonCfg, media_type="application/json")
    # sends the json dictionary that python made from config.ini
    # this can be seen by going to localhost:(port)/config.json


@program.websocket("/ws")
# handles the websocket
async def websocket(ws: WebSocket):
    global allTypes

    await ws.accept()
    # gets the connection
    clients.add(ws)
    # adds clients to websocket

    try:
    # goes to send the first package immediately

        sbo = readSBO()
        # calls readSBO and then stores the dictionary here as sbo
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
            "supportColor": noneRemover(sbo.get("Text Color")),
            "progressColor": noneRemover(sbo.get("Bar Color")),
            "borderColor": noneRemover(sbo.get("Overlay Color"))
        }
        # constructs an initial payload that

        lastPayload = initialPayload.copy()
        # saves a copy of the initial payload payload to compare to later

        initialPayload["progress"] = songProg
        initialPayload["duration"] = songDur
        # adds the timestamp keys after copying (because the progress will change *every* update, and sending a payload because of that is wasteful)

        lastColors = {
            "titleColor": initialPayload["titleColor"],
            "supportColor": initialPayload["supportColor"],
            "progressColor": initialPayload["progressColor"],
            "borderColor": initialPayload["borderColor"]
        }
        # stores a map of the last colors sent, to be compared in the next update

        oldTrackID = initialPayload["id"]
        # stores the ID to check for a song change

        await ws.send_text(payloadBuilder(initialPayload, "full", allTypes["full"]))
        # sends the payload with "track" type for when payloadBuilder returns it

        await asyncio.sleep(2)
        # sleeps 2 seconds after sending initial payload

        while True:
        # this runs constantly after, with a short cooldown, thanks to the "await asyncio.sleep(2)" at the end of the loop

            sbo = readSBO()
            # calls readSBO and then stores the dictionary here as sbo
            
            songProg, songDur = unixConverter(sbo)
            # stores the progress and duration times from unixConverter

            payload = {
                "title": sbo.get("Song Name", ""),
                "artist": sbo.get("Artist Name", ""),
                "album": sbo.get("Album Name", ""),
                "cover": sbo.get("Spotify Image", ""),
                "paused": sbo.get("Pause State", False),
                "id": sbo.get("Track ID", ""),
                "titleColor": noneRemover(sbo.get("Song Color")),
                "supportColor": noneRemover(sbo.get("Text Color")),
                "progressColor": noneRemover(sbo.get("Bar Color")),
                "borderColor": noneRemover(sbo.get("Overlay Color"))
            }
            # constructs a new payload

            currentColors = {
                "titleColor": payload["titleColor"],
                "supportColor": payload["supportColor"],
                "progressColor": payload["progressColor"],
                "borderColor": payload["borderColor"]
            }
            # stores a map of the newly updated colors

            if payload != lastPayload:
                # if the payloads aren't the same at this stage (means there's some data to update HTML)
                # if they are, just skips to sleep and restarts loop
                lastPayload = payload.copy()
                # changes the temp payload variable to match

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

                payload["progress"] = songProg
                payload["duration"] = songDur
                # adds the timestamps *after* checking against the old version

                if currentColors != lastColors:
                    # if any of the colors have changed
                    if songChange:
                        # if the song has also changed
                        await ws.send_text(payloadBuilder(payload, "full", allTypes["full"]))
                        # sends a full payload (track + colors)
                    else:
                        # if the song hasn't changed
                        await ws.send_text(payloadBuilder(payload, "color", allTypes["color"]))
                        # sends only a color payload
                else:
                    # if no colors have changed (must mean something in the track has)
                    await ws.send_text(payloadBuilder(payload, "track", allTypes["track"]))
                    # sends the track payload

            await asyncio.sleep(2)
            # sleeps for 2 seconds between

    except (WebSocketDisconnect, ConnectionResetError):
        # any "disconnect" (leaving the site, refreshing, etc)
        pass
        # doesn't do anything

    except Exception as ex:
        # if it somehow fails
        print("Websocket error", ex, flush=True)

    finally:
        # deletes itself when the connection ends
        clients.discard(ws)


if __name__ == "__main__":
    # runs the socket starter
    print(f"Overlay online at localhost:{httpPort}!", flush=True)
    # prints first, otherwise won't print
    uvicorn.run(program, host="127.0.0.1", port=httpPort, log_level="warning", access_log=False)
    # starts the web server as the FastAPI program, using a preset IP of (local) with the configurable httpPort - disables non-error prints and http requests