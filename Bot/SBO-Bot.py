import configparser, os, sys, threading
# Required for basic function and getting the config options for bot
import asyncio, asqlite, socket, aiohttp
# Required to connect to the bot
import twitchio, logging
# Required for the bot to function
from twitchio import Client, eventsub
# Required for the bot -> Twitch connection
from twitchio import ChatMessage
# Required for the bot -> Chat connection
from twitchio.ext import commands
from twitchio.ext.commands import Command
# Required to use commands in chat
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import sqlite3
# Required for database access (tokens)



### Setup Section ###



SBO_Bot_ver = "v0.3.10.0900"
"""The SBO Bot version (y.m.dd.hhmm)"""



logFormat = "%(message)s"
# changes the format from "[systemtime] [TYPE] message" to just "message"

logging.basicConfig(
    level = logging.INFO, 
    format = logFormat
    )
    # sets up a basic config with the logging level and format

logging.getLogger("twitchio").setLevel(logging.WARNING)
# sets TwitchIO to only print if it has a warning or higher (otherwise it spams)

logging.getLogger("twitchio.client").setLevel(logging.ERROR)
# sets the TwitchIO Client to only print on error or higher (there's a couple irrelevant warnings)

LOGGER = logging.getLogger("BOT")
# starts the consoler logger


if getattr(sys, "frozen", False):
    # since the program bundled with pyInstaller, it's "frozen"
    directory = os.path.dirname(sys.executable)
    """The base directory of the program, where SBO-Bot.exe resides"""
else:
    # if somehow not in a bundled (frozen) state
    directory = os.path.dirname(__file__)
    """The base directory of the program, where SBO-Bot.exe resides"""

   
print(f"Starting SBO Twitch Bot {SBO_Bot_ver}", flush=True)
# quick user update on status

conduitPath = os.path.join(directory, "conduit.txt")
"""The path to conduit.txt (SBO/Bot/conduit.txt)"""

sbotxtPath = os.path.join(directory, "..", "WS", "sbo.txt")
"""The path to sbo.txt (SBO/WS/sbo.txt)"""

Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
"""The configuration file reader"""
ConfigPath = os.path.join(directory, "..", "config.ini")
"""The directory where the config sits in"""
Config.read(ConfigPath, "utf8")
# Where the config is read from, with UTF-8 format

commandPrefix = Config.get("Twitch-Bot", "command_Prefix")
"""The symbol or string to use in front of all commands (string)"""
if not commandPrefix:
    # ensures the command prefix is set
    commandPrefix = "!"
    # sets to default of ! if not (program will not like an empty string)

bot_Client_ID = Config.get("Twitch-Bot", "dev_Client_ID")
"""The Twitch Client ID from config"""
bot_Client_Secret = Config.get("Twitch-Bot", "dev_Client_Secret")
"""The Twitch Client Secret from config"""

ttvName = Config.get("Twitch-Bot", "twitch_Username")
"""The name of the channel whose chat the bot connects to"""
botName = Config.get("Twitch-Bot", "bot_Username")
"""The name of the bot"""

missingID = False
"""A boolean to check if the channel ID exists"""
try:
    # tries to find the twitch ID from config
    channelID = Config.get("Twitch-Bot", "twitch_ID")
    """The ID of the channel whose chat the bot connects to"""
    botID = Config.get("Twitch-Bot", "bot_ID")
    """The ID of the bot"""
    # stores the variables if they're set
except:
    # if even one of the IDs is missing, sets the flag to true
    missingID = True
    # this will trip the check at the bottom and stop the program



### Command Configuration ###



CommandConfig = configparser.ConfigParser(comment_prefixes= ["/", "#"], allow_no_value= True)
"""The Command configuration file reader"""
CmdCfgPath = os.path.join(directory, "commandConfig.ini")
"""The directory where the commandConfig sits in"""
CommandConfig.read(CmdCfgPath, "utf8")
# Where the command config is read from, with UTF-8 format


### Playlist ###
enablePlaylist = CommandConfig.getboolean("Playlist", "enable", fallback=True)
"""Whether playlist command is enabled (boolean)"""
playlist_CD_chatter = CommandConfig.getint("Playlist", "cooldown_Chatter", fallback=600)
"""The cooldown applied per user (1/x, int)"""
playlist_CD_channel = CommandConfig.getint("Playlist", "cooldown_Channel", fallback=60)
"""The cooldown applied channel-wide (1/x, int)"""
playlistLevel = CommandConfig.get("Playlist", "required_Level", fallback="all").lower()
"""The level required to use the command (string) - ID 0"""

### Album ###
enableAlbum = CommandConfig.getboolean("Album", "enable", fallback=True)
"""Whether album command is enabled (boolean)"""
album_CD_chatter = CommandConfig.getint("Album", "cooldown_Chatter", fallback=300)
"""The cooldown applied per user (1/x, int)"""
album_CD_channel = CommandConfig.getint("Album", "cooldown_Channel", fallback=30)
"""The cooldown applied channel-wide (1/x, int)"""
albumLevel = CommandConfig.get("Album", "required_Level", fallback="all").lower()
"""The level required to use the command (string) - ID 1"""

### Song ###
enableSong = CommandConfig.getboolean("Song", "enable", fallback=True)
"""Whether song/track command is enabled (boolean)"""
song_CD_chatter = CommandConfig.getint("Song", "cooldown_Chatter", fallback=180)
"""The cooldown applied per user (1/x, int)"""
song_CD_channel = CommandConfig.getint("Song", "cooldown_Channel", fallback=30)
"""The cooldown applied channel-wide (1/x, int)"""
songLevel = CommandConfig.get("Song", "required_Level", fallback="all").lower()
"""The level required to use the command (string) - ID 2"""

### Pause ###
enablePause = CommandConfig.getboolean("Pause", "enable", fallback=True)
"""Whether pause command is enabled (boolean)"""
pause_CD_chatter = CommandConfig.getint("Pause", "cooldown_Chatter", fallback=180)
"""The cooldown applied per user (1/x, int)"""
pause_CD_channel = CommandConfig.getint("Pause", "cooldown_Channel", fallback=60)
"""The cooldown applied channel-wide (1/x, int)"""
pauseLevel = CommandConfig.get("Pause", "required_Level", fallback="vip").lower()
"""The level required to use the command (string) - ID 3"""

### Resume ###
enableResume = CommandConfig.getboolean("Resume", "enable", fallback=True)
"""Whether resume command is enabled (boolean)"""
resume_CD_chatter = CommandConfig.getint("Resume", "cooldown_Chatter", fallback=180)
"""The cooldown applied per user (1/x, int)"""
resume_CD_channel = CommandConfig.getint("Resume", "cooldown_Channel", fallback=60)
"""The cooldown applied channel-wide (1/x, int)"""
resumeLevel = CommandConfig.get("Resume", "required_Level", fallback="vip").lower()
"""The level required to use the command (string) - ID 4"""

### Skip ###
enableSkip = CommandConfig.getboolean("Skip", "enable", fallback=True)
"""Whether skip command is enabled (boolean)"""
skip_CD_chatter = CommandConfig.getint("Skip", "cooldown_Chatter", fallback=180)
"""The cooldown applied per user (1/x, int)"""
skip_CD_channel = CommandConfig.getint("Skip", "cooldown_Channel", fallback=60)
"""The cooldown applied channel-wide (1/x, int)"""
skipLevel = CommandConfig.get("Skip", "required_Level", fallback="vip").lower()
"""The level required to use the command (string) - ID 5"""

### Previous ###
enablePrevious = CommandConfig.getboolean("Previous", "enable", fallback=True)
"""Whether previous command is enabled (boolean)"""
previous_CD_chatter = CommandConfig.getint("Previous", "cooldown_Chatter", fallback=180)
"""The cooldown applied per user (1/x, int)"""
previous_CD_channel = CommandConfig.getint("Previous", "cooldown_Channel", fallback=60)
"""The cooldown applied channel-wide (1/x, int)"""
previousLevel = CommandConfig.get("Previous", "required_Level", fallback="vip").lower()
"""The level required to use the command (string) - ID 6"""

### Queue ###
enableQueue = CommandConfig.getboolean("Queue", "enable", fallback=True)
"""Whether queue command is enabled (boolean)"""
queue_CD_chatter = CommandConfig.getint("Queue", "cooldown_Chatter", fallback=180)
"""The cooldown applied per user (1/x, int)"""
queue_CD_channel = CommandConfig.getint("Queue", "cooldown_Channel", fallback=60)
"""The cooldown applied channel-wide (1/x, int)"""
queueLevel = CommandConfig.get("Queue", "required_Level", fallback="vip").lower()
"""The level required to use the command (string) - ID 7"""


### Command Level Mapping ###


commandLevels = [playlistLevel, 
                 albumLevel, 
                 songLevel, 
                 pauseLevel, 
                 resumeLevel, 
                 skipLevel, 
                 previousLevel, 
                 queueLevel]
"""A list of all the command requirement levels"""
# takes all the user level requirement variables and puts into a list

commandLevelList = []
"""A list of command levels, in number format (1-6 with 3 fallback)"""
# creates an empty list to append numbers into below

for i in commandLevels:
    # goes through every command's set level and appends a number based on the config setting
    if i == "all":
        commandLevelList.append(1)
        # if the command level is "all", assigns value 1
    elif i == "subscriber" or i == "sub":
        commandLevelList.append(2)
        # if the command level is "subscriber"/"sub", assigns value 2
    elif i == "vip":
        commandLevelList.append(3)
        # if the command level is "vip", assigns value 3
    elif i == "mod" or i == "moderator":
        commandLevelList.append(4)
        # if the command level is "mod", assigns value 4
    elif i == "lead moderator" or i == "lead" or i == "lead mod":
        commandLevelList.append(5)
        # if the command level is "lead mod"/"lead moderator"/"lead", assigns value 5
    elif i == "broadcaster" or i == "streamer":
        commandLevelList.append(6)
        # if the command level is "broadcaster" or "streamer", assigns value 6
    else:
        commandLevelList.append(4)
        # if the command level is none of the above, assigns default fallback of 4 (Moderator), to prevent accidentally allowing unwanted control

permissionMap = {
    "playlist": commandLevelList[0],
    "album": commandLevelList[1],
    "song": commandLevelList[2],
    "pause": commandLevelList[3],
    "resume": commandLevelList[4],
    "skip": commandLevelList[5],
    "previous": commandLevelList[6],
    "queue": commandLevelList[7]
}
"""A map of required levels to use each command (0-6), based on the command's internal ID (0 ->)"""
# stores each of the command's required use level as a permission map that can be called by isCoolChatter to check


if any([enablePause,enableResume,enableSkip,enablePrevious,enableQueue]):
    # checks if any of the "playback control" commands are enabled
    playbackControls = True
    # sets playbackControls to True if any are (this just tells the startup print what to display, debug/QoL)
else:
    # if none are
    playbackControls = False
    # sets playbackControls to False



### Playback Control ###



webClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sets up the webclient socket
webClient.connect(("127.0.0.1", 6666))
# creates a socket connection on localhost
print(f"Attempting to connect to PTP", flush=True)
# (debug) print

def dataPasser(command: str, uri: str):
    """A function to send commands to SBO (takes the command and spotify URI/URL as parameters)"""

    if command == "skip":
        # if the command is skip
        msg = "Skip"
        webClient.send(msg.encode())
        # sends a message to SBO to skip
        return "Skipped"
        # sends the response back to the bot so it can reply

    elif command == "pause":
        # if the command is pause
        msg = "Pause"
        webClient.send(msg.encode())
        # sends a message to SBO to pause
        return "Paused"
        # sends the response back to the bot so it can reply
    
    elif command == "resume":
        # if the command is resume
        msg = "Resume"
        webClient.send(msg.encode())
        # sends a message to SBO to resume
        return "Resumed"
        # sends the response back to the bot so it can reply

    elif command == "previous":
        # if the command is previous
        msg = "Previous"
        webClient.send(msg.encode())
        # sends a message to SBO to pause
        return "Went back"
        # sends the response back to the bot so it can reply

    elif command == "queue":
        # if the command has queue (means it has a link, too)
        msg = f"Queue: {uri}"
        webClient.send(msg.encode())
        # sends the link 
        return "Queued song"
        # sends the response back to the bot so it can reply
    
    else:
        print(f"Playback control ready", flush=True)
        # indicates that the playback control has been started (since the run sends bs parameters)



### Text File -> Dictionary ###



def getData():
    """Function to get the current playlist/track/whatever else from the sbo.txt file"""

    if not os.path.exists(sbotxtPath):
        # ensures the text file exists
        return "No text file found"
    
    sbo = {}
    # empty dictionary to store the contents in

    with open(sbotxtPath, "r") as sboText:
        # opens the text file with utf-8 encoding
        for line in sboText:
            # for every line in the file
            if "=" in line:
                # if there's an equals sign (all lines)
                identifier, data = line.strip().split("=", 1)
                # strips and splits the line to the left and right side (identifier and data)
                sbo[identifier.strip()] = data.strip()
                # stores inside the made dictionary as keyed entries

    return sbo
    # sends back the updated dictionary



### Permission Check (Playback Control) ###



def isCoolChatter():
    """Function to check if the calling chatter is authorised to use sent command"""
    def chatterChecker(sender, command):
        """Helper function, takes the sent message's context and the command as parameter"""
        chatter = sender.author
        # assigns the message sender's author as "chatter"
        reqLevel = permissionMap.get(command)
        # gets the required level from the permission map (all, subscriber, vip, mod)
        currentLevel = 0
        # sets the current level to 0 to start with (0=nothing, 1=any, 2=sub, 3=vip/artist,)

        if chatter.subscriber:
            # if the chatter is a subscriber
            currentLevel = 2

        elif chatter.vip or chatter.artist:
            # if the chatter is a VIP or artist
            currentLevel = 3

        elif chatter.moderator:
            # if the chatter is a moderator
            currentLevel = 4

        elif chatter.lead_moderator:
            # if the chatter is a lead moderator
            currentLevel = 5

        elif chatter.broadcaster:
            # if the chatter is the streamer
            currentLevel = 6

        else:
            # if the user isn't any of the above, assumes normal user (also fits admin, staff, etc)
            currentLevel = 1

        if reqLevel <= currentLevel:
            # if the required level is lower or equal to the current chatter's level
            return True
            # tells isCoolChatter() the chatter is, in fact, cool
        else:
            return False
            # tells isCoolChatter() the chatter, unfortunately, isn't cool :(

    return chatterChecker
    # returns the result to calling command

        


### Bot Class ###


class Bot(commands.AutoBot):
    def __init__(self, *, token_database: asqlite.Pool, subs: list[eventsub.SubscriptionPayload]) -> None:
        self.token_database = token_database

        super().__init__(
            client_id = bot_Client_ID,
            client_secret = bot_Client_Secret,
            bot_id = botID,
            owner_id = channelID,
            prefix = commandPrefix,
            subscriptions = subs,
            force_subscribe = True
        )
        # sets up the bot with the correct permissions and IDs
        self.channelLive = False
        # stores the channel live status (False by default)
        self.botName = botName
        # stores the botname as a class variable (used for a print)

### Live Check ###

    async def liveCheck(self, channelID: str) -> bool:
        # checks if the channel is live (shouldn't be able to use playback commands if offline)
        channelURL = f"https://api.twitch.tv/helix/streams?user_login={channelID}"
        # creates a url for the channel in question
        urlHeader = {
            "Client-ID": bot_Client_ID
        }
        # constructs the header with the bot client ID

        async with aiohttp.ClientSession() as session:
            # starts an aio client to connect to Twitch API
            async with session.get(channelURL, headers=urlHeader) as reply:
                # queries the channel ID with header, stores response as "reply"
                data = await reply.json()
                # takes the data from a json file that's returned
                if "data" in data and data["data"]:
                    # if "data" key is found and isn't empty (means the stream is live)
                    return True
                    # returns true, which sets the boolean for live to true
                else:
                    return True
                    # if data key doesn't exist or is empty
                    # return False
                    # returns false, which keeps the boolean for channelLive false, disallowing commands that require it

### Check Status of Live Check ###

    async def checkLiveCheck(self):
        # runs liveCheck every minute to see if the channel is live
        logged = False
        # sets a boolean to check if the status has been logged already
        while True:
            # while program is running
            channelLive = await self.liveCheck(self.owner_id)
            # sets the boolean based on the liveCheck result
            if channelLive != self.channelLive:
                # if the local and class booleans don't match
                self.channelLive = channelLive
                # ensures they do
                if channelLive:
                    # if the channel is live
                    if not logged and playbackControls:
                        # if the live status hasn't already been logged once and playback controls are on (at least one playback command is enabled)
                        print(f"{ttvName} is live! Playback control enabled for at least one command! ", flush=True)
                        # prints a live message
                        logged = True
                        # changes boolean to True to prevent constant logging
                    elif not logged and not playbackControls:
                        # if the live status hasn't already been logged once, but all "playback controls" are off
                        print(f"{ttvName} is live! All playback controls are disabled via config")
                        logged = True
                        # changes boolean to True to prevent constant logging
                else:
                    # if the channel isn't live
                    logged = False
                    # changes/ensures boolean is False

            await asyncio.sleep(60)
            # sleeps for a minute

### Command Setup ###

    async def setup_hook(self) -> None:
        # adds the component that adds commands
        await self.add_component(CommandComponent(self))

### Auth ###

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            # if there's no user id set
            return
            # closes

        if payload.user_id == self.bot_id:
            # if the id is the same as the bot
            return
            # closes

        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(
                broadcaster_user_id = payload.user_id, 
                user_id = self.bot_id)
        ]
        # what to "subscribe" to (listen to)
        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.error("Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id)

### Token Storage ###

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # calls super() to get required permissions and such
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # stores tokens in SQL database (tokens.db)
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        return resp

### Ready Console Log ### 

    async def event_ready(self) -> None:
        print(f"Successfully logged in as {self.botName}", flush=True)
        # prints the login message to console
        asyncio.create_task(self.checkLiveCheck())
        # creates a "task" to run checkLiveCheck



### Commands Component of Bot ###



class CommandComponent(commands.Component):
    """Class/component that stores all the commands"""

### Init ###

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        # passes the bot class
        super().__init__()

### Listener ###

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        """Message grabber"""

### Playlist ###

    @commands.command()
    @commands.cooldown(rate=1, per=playlist_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate=1, per=playlist_CD_chatter, key=commands.BucketType.chatter)
    async def playlist(self, context: commands.Context) -> None:
        """playlist"""

        if self.bot.channelLive and enablePlaylist:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "playlist"):
                sbo = getData()
                # calls the data grabber to get the package (dictionary)
                playlist = sbo.get("Playlist URL")
                # gets the playlist URL from the dictionary 

                if playlist == "No playlist":
                    # if the playlist isn't set (SBO sets it to this if no playlist is active)
                    await context.reply(f"{ttvName} is not currently listening to a playlist")
                    # sends a playlist-less message
                else:
                    # if the playlist return is anything else
                    await context.reply(f"Current playlist: {playlist}")
                    # sends a message with the playlist URL

### Album ###

    @commands.command()
    @commands.cooldown(rate = 1, per=album_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate = 1, per=album_CD_chatter, key=commands.BucketType.chatter)
    async def album(self, context: commands.Context) -> None:
        """album"""

        if self.bot.channelLive and enableAlbum:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "album"):
                sbo = getData()
                # calls the data grabber to get the package (dictionary)
                album = sbo.get("Album URL")
                # gets the album URL from the dictionary 

                if album == "A local album":
                    # if the album isn't set (SBO sets it to this if playback is local)
                    await context.reply(f"No album found")
                    # sends a album-less message
                else:
                    # if the playlist return is anything else
                    await context.reply(f"Current album: {album}")
                    # sends a message with the album URL

### Song ###

    @commands.command(aliases=["song"])
    @commands.cooldown(rate = 1, per=song_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate = 1, per=song_CD_chatter, key=commands.BucketType.chatter)
    async def track(self, context: commands.Context) -> None:
        """track and song"""

        if self.bot.channelLive and enableSong:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "song"):
                sbo = getData()
                # calls the data grabber to get the package (dictionary)
                track = sbo.get("Song Name")
                # gets the track from the dictionary
                artist = sbo.get("Artist Name")
                # gets the artist name from the dictionary
                trackURL = sbo.get("Spotify URL")
                # gets the track URL from the dictionary
                
                if trackURL == "A local song":
                    # if the song is local (SBO sets it to this if playback is local)
                    await context.reply(f"{ttvName} is listening to a local song")
                    # sends a local song message
                elif trackURL == None:
                    # if the song is empty
                    await context.reply(f"{ttvName} is not listening to Spotify")
                    print(f"If you see this message, but your Spotify is playing, check the status of SBO and Spotify", flush=True)
                else:
                    # if the song return is anything else
                    await context.reply(f"Current song: {track} by {artist}. {trackURL}")
                    # sends a message with the song URL

### Skip ###

    @commands.command()
    @commands.cooldown(rate = 1, per=skip_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate = 1, per=skip_CD_chatter, key=commands.BucketType.chatter)
    async def skip(self, context: commands.Context) -> None:
        """skip"""

        if self.bot.channelLive and enableSkip:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "skip"):
                # checks if the permissions are met
                dataPasser("skip", "")
                # calls the dataPasser function
                await context.reply("Skipped")
            
            else:
                print(f"No permission", flush=True)

### Pause ###

    @commands.command()
    @commands.cooldown(rate = 1, per=pause_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate = 1, per=pause_CD_chatter, key=commands.BucketType.chatter)
    async def pause(self, context: commands.Context) -> None:
        """pause"""

        if self.bot.channelLive and enablePause:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "pause"):
                dataPasser("pause", "")
                # calls the dataPasser function

                await context.reply(f"Paused")
                # replies to user

### Resume ###

    @commands.command(aliases=["continue"])
    @commands.cooldown(rate = 1, per=resume_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate = 1, per=resume_CD_chatter, key=commands.BucketType.chatter)
    async def resume(self, context: commands.Context) -> None:
        """resume"""

        if self.bot.channelLive and enableResume:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "resume"):
                # checks if the permissions are met
                dataPasser("resume", "")
                # calls the dataPasser function

                await context.reply(f"Resumed")
                # replies to user

### Previous ###

    @commands.command()
    @commands.cooldown(rate = 1, per=previous_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate = 1, per=previous_CD_chatter, key=commands.BucketType.chatter)
    async def previous(self, context: commands.Context) -> None:
        """previous"""

        if self.bot.channelLive and enablePrevious:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "previous"):
                # checks if the permissions are met
                dataPasser("previous", "")
                # calls the dataPasser function

                await context.reply(f"Went back")
                # replies to user

### Queue ###

    @commands.command()
    @commands.cooldown(rate = 1, per=queue_CD_channel, key=commands.BucketType.channel)
    @commands.cooldown(rate = 1, per=queue_CD_chatter, key=commands.BucketType.chatter)
    async def queue(self, context: commands.Context) -> None:
        """queue"""

        if self.bot.channelLive and enableQueue:
        # checks if the channel is live and the command is enabled
            if isCoolChatter()(context, "queue"):
                # checks if the permissions are met
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, songLink = fullMsg.split(" ", 1)
                    # splits the command, stores the link for the song as songLink

                    if len(songLink) == 22 or songLink.startswith(["http:", "https:", "spotify:"]):
                        # must be one of: "song uri, id, or url", so it checks if the length matches an ID's 22 character length
                        # or if the song starts with http:, https: or spotify: (signs of a URL or URI)

                        dataPasser("queue", songLink)
                        # calls the dataPasser function with the link

                        await context.reply(f"Queued song")
                        # replies to user

                except:
                    # if the command fails
                    await context.reply(f"Add a valid Spotify link after !queue, please")
                    # replies to user 

### SBO ###

    @commands.command(aliases=["SBO"])
    @commands.cooldown(rate = 1, per=300, key=commands.BucketType.channel)
    async def sbo(self, context: commands.Context) -> None:
        """!sbo / !SBO"""

        await context.reply(f"SBO is a Twitch Bot base made to simplify Spotify-Twitch connection, currently on {SBO_Bot_ver} // LP")
        # replies with the SBO details

### Command Error ###

    async def event_command_error(self, context: commands.Context, error: Exception):
        """Handles Twitch(IO) command errors"""
        if isinstance(error, commands.CommandNotFound):
            # if the command returns a "command not found"
            return
            # doesn't return anything, because it's expected behavior
        if isinstance(error, commands.CommandOnCooldown):
            # if the command returns a "cooldown"
            cooldown = round(error.remaining)
            # stores the time remaining for user/channel cooldown
            await print(f"Command is on cooldown for {cooldown} seconds", flush=True)
            # logs a cooldown message
            return
        if isinstance(error, commands.MissingRequiredArgument):
            # if there's a missing
            await context.reply(f"Missing parameter")
            # sends a parameter message
            return
        else:
            # if it's something else
            await print(f"Error handling {context.command}: {error}", flush=True)
            # logs an error
            
### Database / Token Storage ###

async def setup_database(db: asqlite.Pool) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    """Function to setup the database from given (db)"""
    query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
    # SQL query string that'll create a token database
    async with db.acquire() as connection:
        # gets a connection from the connection pool
        await connection.execute(query)
        # executes the SQL query

        rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")
        # gets all the rows from the table of tokens

        tokens: list[tuple[str, str]] = []
        # makes an empty list of tuples to store tokens into
        subs: list[eventsub.SubscriptionPayload] = []
        # makes an empty list of chat messages ("subscribed" channel payload events)

        for row in rows:
            # repeats for every row in the token table
            tokens.append((row["token"], row["refresh"]))
            # gets the token and refresh values from the row, turns into a tuple

            if row["user_id"] == botID:
                # skips the botID events
                continue

            subs.extend([eventsub.ChatMessageSubscription(broadcaster_user_id=row["user_id"], user_id=botID)])
            # makes a "subscription" for the token being checked, adds to "subs"

    return tokens, subs
    # returns tuple of lists



### Console Log ###



def logWriter() -> None:
    """Logging function"""

    twitchio.utils.setup_logging(level=logging.INFO)
    # sets up a console log writer (currently set to "ERROR" to avoid massive print)

    async def runner() -> None:
        """A run function for the chatbot"""
        async with asqlite.create_pool("tokens.db") as tdb:
            # creates a tokens.db (database) file
            tokens, subs = await setup_database(tdb)
            # ensures the database is done

            async with Bot(token_database=tdb, subs=subs) as bot:
                # takes the database data
                for pair in tokens:
                    await bot.add_token(*pair)

                await bot.start(load_tokens=False)
                # starts the chatbot
    try:
        asyncio.run(runner())
        # runs the runner...
    except KeyboardInterrupt:
        # user quits
        print(f"Quitting SBOT", flush=True)



### Startup ###



if missingID:
    # checks if the channelID exists (required for connection)
        print(f"ChannelID/BotID not found, please enter into the config file", flush=True)
        # user inform
        input("Press enter to exit", flush=True)
        raise SystemExit

if not ttvName or not botName:
    # checks if the channel/bot name exist (required for conduit/connection)
        print(f"Twitch username or bot username not found, please enter into the config file", flush=True)
        # user inform
        input("Press enter to exit", flush=True)
        raise SystemExit

dataPassThread = threading.Thread(target = lambda: dataPasser("start", "uri"))
# creates a thread for websocket connection
dataPassThread.start()
# starts the websocket thread


if __name__ == "__main__":
    logWriter()
    # starts the console writer