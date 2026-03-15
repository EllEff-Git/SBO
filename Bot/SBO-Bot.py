import configparser, os, sys, time
# Required for basic OS/system function and getting the config options for bot
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
from twitchio.ext.commands.exceptions import CommandOnCooldown, CommandNotFound, MissingRequiredArgument
# Required to handle TwitchIO command errors without massive error logs
from twitchio.ext.commands.cooldowns import Bucket
# Required to manage cooldown types (chatter/channel) easier
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import sqlite3
# Required for database access (tokens)



### Setup Section ###



SBO_Bot_ver = "v0.3.15.0552"
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

sbotxtPath = os.path.join(directory, "..", "WS", "sbo.txt")
"""The path to sbo.txt (SBO/WS/sbo.txt)"""

Config = configparser.ConfigParser(comment_prefixes = ["/", "#"], allow_no_value = True)
"""The configuration file reader"""
ConfigPath = os.path.join(directory, "..", "config.ini")
"""The directory where the config sits in"""
Config.read(ConfigPath, "utf8")
# Where the config is read from, with UTF-8 format

commandPrefix = Config.get("Twitch-Bot", "command_Prefix", fallback="!")
"""The symbol or string to use in front of all commands (string)"""
cooldownMessage = Config.getboolean("Twitch-Bot", "enable_Cooldown_Messages", fallback=False)
"""Whether to reply to chatter with a cooldown message if command is on cooldown"""
webClientPort = (Config.getint("Function", "http_Port", fallback=6666) + 1)
"""The port to use for the PTP connection (http_Port + 1, int)"""

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

playbackControlsDisabled = False
"""A boolean to check if the playback controls should be disabled (meant as a temporary setting)"""


### Command Configuration ###


chatCommandConfig = configparser.ConfigParser(comment_prefixes= ["/", "#"], allow_no_value= True)
"""The command configuration file reader"""
CmdCfgPath = os.path.join(directory, "commandConfig.ini")
"""The directory where the commandConfig sits in"""
chatCommandConfig.read(CmdCfgPath, "utf8")
# Where the command config is read from, with UTF-8 format

defaultConfig = {
    "Playlist":         {"enable": True, "cooldown_Chatter": 600, "cooldown_Channel": 60, "required_Level": "all"},
    "Album":            {"enable": True, "cooldown_Chatter": 300, "cooldown_Channel": 30, "required_Level": "all"},
    "Song":             {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 30, "required_Level": "all"},
    "Last Song":        {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 30, "required_Level": "all"},
    "Pause":            {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "vip"},
    "Resume":           {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "vip"},
    "Skip":             {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "vip"},
    "Previous":         {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "vip"},
    "Queue":            {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "vip"},
    "Song Color":       {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "subscriber"},
    "Text Color":       {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "subscriber"},
    "Bar Color":        {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "subscriber"},
    "Overlay Color":    {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "subscriber"},
    "Custom Color":     {"enable": True, "cooldown_Chatter": 180, "cooldown_Channel": 60, "required_Level": "subscriber"},
    "Playback Control": {"enable": True, "cooldown_Chatter": 100, "cooldown_Channel": 30, "required_Level": "moderator"}
}
# a map of the default loaded settings 

commandOptions = {}
"""The stored command options from commandConfig.ini
    - Called with commandOptions["Command Name"]["Option"]
    - Valid options: enable, cooldown_Chatter, cooldown_Channel, required_Level"""

for command, defaults in defaultConfig.items():
    # goes through every command's options in the defaultConfig map
    section = command
    # sets the section name as the current command 
    commandOptions[command] = {
        "enable": chatCommandConfig.getboolean(section, "enable", fallback = defaults["enable"]),
        "cooldown_Chatter": chatCommandConfig.getint(section, "cooldown_Chatter", fallback = defaults["cooldown_Chatter"]),
        "cooldown_Channel": chatCommandConfig.getint(section, "cooldown_Channel", fallback = defaults["cooldown_Channel"]),
        "required_Level": chatCommandConfig.get(section, "required_Level", fallback = defaults["required_Level"]).lower(),
    }
    # stores the config options from the config file (falls back to defaultConfig's default values in case one isn't found)

print(f"Bot command configuration loaded successfully", flush=True)
# user inform that config succeeded

### Command Level Mapping ###

commandLevels = [
                commandOptions["Playlist"]["required_Level"], 
                commandOptions["Album"]["required_Level"], 
                commandOptions["Song"]["required_Level"],
                commandOptions["Last Song"]["required_Level"],
                commandOptions["Pause"]["required_Level"], 
                commandOptions["Resume"]["required_Level"], 
                commandOptions["Skip"]["required_Level"], 
                commandOptions["Previous"]["required_Level"], 
                commandOptions["Queue"]["required_Level"],
                commandOptions["Song Color"]["required_Level"],
                commandOptions["Text Color"]["required_Level"],
                commandOptions["Bar Color"]["required_Level"],
                commandOptions["Overlay Color"]["required_Level"],
                commandOptions["Custom Color"]["required_Level"],
                commandOptions["Playback Control"]["required_Level"]
                ]
"""A list of all the command requirement levels"""
# takes all the user level requirement variables and puts into a list

commandLevelList = []
"""A list of command levels, in number format (1 - 6, fallback = 3)"""
# creates an empty list to append numbers into below

for i in commandLevels:
    # goes through every command's set level and appends a number based on the config setting
    if i == "all":
        commandLevelList.append(1)
        # if the command level is "all", assigns value 1
    elif i == "subscriber" or i == "sub":
        commandLevelList.append(2)
        # if the command level is "subscriber"/"sub", assigns value 2
    elif i == "vip" or i == "artist":
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
                "Playlist": commandLevelList[0],
                "Album": commandLevelList[1],
                "Song": commandLevelList[2],
                "Last Song": commandLevelList[3],
                "Pause": commandLevelList[4],
                "Resume": commandLevelList[5],
                "Skip": commandLevelList[6],
                "Previous": commandLevelList[7],
                "Queue": commandLevelList[8],
                "Song Color": commandLevelList[9],
                "Text Color": commandLevelList[10],
                "Bar Color": commandLevelList[11],
                "Overlay Color": commandLevelList[12],
                "Custom Color": commandLevelList[13],
                "Playback Control": commandLevelList[14]
                }
"""A map of required levels to use each command (0-6)"""
# stores each of the command's required use level as a permission map that can be called by isCoolChatter to check

if any([
        commandOptions["Pause"]["enable"],
        commandOptions["Resume"]["enable"],
        commandOptions["Skip"]["enable"],
        commandOptions["Previous"]["enable"],
        commandOptions["Queue"]["enable"]
    ]):
    # checks if any of the "playback control" commands are enabled
    playbackControls = True
    # sets playbackControls to True if any are (this just tells the startup print what to display, debug/QoL)
else:
    # if none are
    playbackControls = False
    # sets playbackControls to False



### Playback Control ###



def dataPasser(command: str, arg2: str):
    """A function to send commands to SBO (takes the command / optionally: a string argument to pass to SBO)"""
    try:
        if arg2 == "":
            # if the second argument is empty (is just a playback command, eg. skip)
            msg = command
            # creates a message from just the command
        else:
            # if the second argument isn't empty (means there's a link or color attached)
            msg = f"{command}: {arg2}"
            # creates a string from the command and argument (uri/url/color...) 

        playbackControlCommands = ["Pause", "Resume", "Previous", "Skip", "Queue"]
        # all the commands that are related to playback

        if command in playbackControlCommands and playbackControlsDisabled:
            # if the command is in the list of playback control commands *and* the playbackControlsDisabled flag is true
            print(f'Playback controls (temporarily) stopped with "playbackControls pause/stop"', flush=True)
            # prints console message about disabled playback control
            pass
            # doesn't progress

        print(f"Sending command {command} via PTP", flush=True)
        # user inform

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as webClient:
        # starts a new connection (with the same parameters)
            webClient.connect(("127.0.0.1", webClientPort))
            # connects to the existing host
            webClient.sendall(msg.encode("utf-8"))
            # sends the message

            returnableCommands = ["Playlist", "Queue", "Custom Color"]
            # all the commands that require a return 

            if command in returnableCommands:
            # if the command is one of the return-expecting ones, that means the reply requires data to be sent back from SBO
                response = webClient.recv(1024).decode("utf-8")
                # gets the response from SBO
                return response
                # returns to calling function (command)
            else:
            # if the command is anything else
                None
                # doesn't do anything, because that's expected

            webClient.close()
            # stops the connection when it's done

    except Exception as err:
        # if it fails for some reason
        print(f"Failed to send the command via PTP: {err}", flush=True)
        # prints an error inform
        return None
        # returns None


### Text File -> Dictionary ###



def getData() -> dict:
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



def isCoolChatter(sender, command) -> bool:
    """Function to check if the calling chatter is authorised to use sent command"""
    chatter = sender.author
    # assigns the message sender's author as "chatter"
    reqLevel = permissionMap.get(command, 3)
    # gets the required level from the permission map (0-6, defaults to 3 if none is found)
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
        # returns the result; the chatter is, in fact, cool enough
    else:
        return False
        # returns the result; the chatter, unfortunately, isn't cool enough :(

        

### Bot Class ###



class Bot(commands.AutoBot):
    """Bot setup class, handles all variable assignments"""
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
        """Function that checks if the given twitch channel is live"""
        channelURL = f"https://api.twitch.tv/helix/streams?user_login={channelID}"
        # creates a url for the channel in question
        urlHeader = {
            "Client-ID": bot_Client_ID
        }
        # constructs the header with the bot client ID (this is what it uses to make an api request)
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
                    return False
                    # if data key doesn't exist or is empty - returns false, which keeps channelLive false, disallowing commands that require it

### Check Status of Live Check ###

    async def checkLiveCheck(self):
        """Function that gets called to run liveCheck every minute to see if the channel is live"""
        logged = False
        # sets a boolean to check if the status has been logged already
        while True:
            # while program is running
            self.channelLive = await self.liveCheck(self.owner_id)
            # sets the boolean based on the liveCheck result
            if self.channelLive:
                # if the channel is live
                if not logged and playbackControls:
                    # if the live status hasn't already been logged once and playback controls are on (at least one playback command is enabled)
                    print(f"{ttvName} is live! Playback control enabled for at least one command! ", flush=True)
                    # prints a live message
                    logged = True
                    # changes boolean to True to prevent constant logging
                elif not logged and not playbackControls:
                    # if the live status hasn't already been logged once, but all "playback controls" are off
                    print(f"{ttvName} is live! All playback controls are disabled via config", flush=True)
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



### Cooldown Manager ###



class CooldownManager:
    """Class that hosts a cooldown management function"""
    def __init__(self):
        self.chatterCDs = {}
        # tracks the per-chatter cooldowns (key = chatterID, command) (timestamp)
        self.channelCDs = {}
        # tracks the per-channel cooldowns (key = channel, command) (timestamp)

    async def cooldownCheck(self, context, chatterCDTime: int, channelCDTime: int):
        """Function to check the cooldown - takes the context (message), the user cooldown (int) and channel cooldown (int)"""
        chatterStatus = context.author
        # stores the chatter's "status" (details)
        now = int(time.time())
        # stores the current UNIX time (in seconds)
        chatterKey = (context.author.id, context.command.name)
        # stores the chatter's ID and the command used
        channelKey = (context.channel.name, context.command.name)
        # stores the channel's name and the command used

        if chatterStatus.broadcaster:
            # checks if the chatter is the streamer
            return True
            # skips everything and returns True (no cooldown for streamer)

        chatterCD = self.chatterCDs.get(chatterKey, 0)
        # gets the last time the chatter in question ran the command (0 if none is found)

        if now - chatterCD < chatterCDTime:
        # if (the current time - chatter cooldown duration) is less than the config-set cooldown:
            return False
            # returns false (meaning cooldown isn't done yet)

        channelCD = self.channelCDs.get(channelID, 0)
        # gets the last time *anyone* used the command (0 if none is found)

        if now - channelCD < channelCDTime:
        # if (the current time - channel cooldown duration) is less than the config-set cooldown:
            return False
            # returns false (cooldown isn't done)

        self.chatterCDs[chatterKey] = now
        # sets the last time the user ran the command to match current time
        self.channelCDs[channelKey] = now
        # sets the last time the command was run to match the current time
        return True
        # if neither prior "return"s triggered, that means the command is off-cooldown and can be run - returns True



### Commands Component of Bot ###



class CommandComponent(commands.Component):
    """Class/component that stores all the commands"""

### Init ###

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        # passes the bot class
        self.cooldowns = CooldownManager()
        # instantiates the cooldown manager
        super().__init__()

### Listener ###

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        """Message grabber/listener"""

### Command Error ###

    async def event_command_error(self, context: commands.Context, error: commands.CommandError):
        """Handles Twitch(IO) command errors"""
        if isinstance(error, commands.CommandNotFound):
            # if the command returns a "command not found"
            return
            # doesn't return anything, because it's expected behavior

        if isinstance(error, commands.MissingRequiredArgument):
            # if there's a missing
            await context.reply(f"Missing parameter")
            # sends a parameter message
            return
        
        print(f"Error handling {context.command}: {error}", flush=True)
        # logs an error if it's something else

### Playlist ###

    @commands.command()
    async def playlist(self, context: commands.Context) -> None:
        """playlist"""

        if self.bot.channelLive and commandOptions["Playlist"]["enable"]:
        # checks if the channel is live and the command is enabled

            if not await self.cooldowns.cooldownCheck(context, commandOptions["Playlist"]["cooldown_Chatter"], commandOptions["Playlist"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 
                    
            if isCoolChatter(context, "Playlist"):
                # if the chatter is cool enough to use the playlist command
                playlistName = dataPasser("Playlist", "")
                # passes the command to dataPasser -> SBO
                if playlistName:
                    # if the string is returned
                    await context.reply(f"{playlistName}")
                    # replies with the returned message
                else:
                    # if the string isn't returned for some reason
                    await context.reply(f"Couldn't execute playlist command")
                    # replies with fail message

### Album ###

    @commands.command()
    async def album(self, context: commands.Context) -> None:
        """album"""

        if self.bot.channelLive and commandOptions["Album"]["enable"]:
        # checks if the channel is live and the command is enabled

            if not await self.cooldowns.cooldownCheck(context, commandOptions["Album"]["cooldown_Chatter"], commandOptions["Album"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Album"):
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
    async def track(self, context: commands.Context) -> None:
        """track and song"""

        if self.bot.channelLive and commandOptions["Song"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Song"]["cooldown_Chatter"], commandOptions["Song"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Song"):
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
                elif trackURL == "None" or trackURL == None:
                    # if the song is empty
                    await context.reply(f"{ttvName} is not listening to Spotify")
                    # replies with a no song detected message
                    print(f"If you see this message, but your Spotify is playing, check the status of SBO and Spotify", flush=True)
                    # user inform in case something went wrong
                else:
                    # if the song return is anything else
                    await context.reply(f"Current song is: {track} by {artist}. {trackURL}")
                    # sends a message with the song URL

### Last Song ###

    @commands.command(aliases=["last"])
    async def lastSong(self, context: commands.Context) -> None:
        """lastSong / last"""

        if self.bot.channelLive and commandOptions["Last Song"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Last Song"]["cooldown_Chatter"], commandOptions["Last Song"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Last Song"):
                sbo = getData()
                # calls the data grabber to get the package (dictionary)
                track = sbo.get("Last Song")
                # gets the track from the dictionary
                artist = sbo.get("Last Artist")
                # gets the artist name from the dictionary
                trackURL = sbo.get("Last Playlist URL")
                # gets the track URL from the dictionary
                
                if trackURL == "A local song":
                    # if the song is local (SBO sets it to this if playback is local)
                    await context.reply(f"{ttvName} last listened to a local song")
                    # sends a local song message
                elif trackURL == "None" or trackURL == None:
                    # if the song is empty
                    await context.reply(f"Couldn't find previous song for {ttvName}, sorry!")
                    # replies with a no last song message
                    print(f"If you see this message, but your Spotify is playing (and the program has been up for more than 1 song), check the status of SBO and Spotify", flush=True)
                    # user inform in case it fails
                else:
                    # if the song return is anything else
                    await context.reply(f"Last song was: {track} by {artist}. {trackURL}")
                    # sends a message with the song URL

### Skip ###

    @commands.command()
    async def skip(self, context: commands.Context) -> None:
        """skip"""

        if self.bot.channelLive and commandOptions["Skip"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Skip"]["cooldown_Chatter"], commandOptions["Skip"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Skip"):
                # checks if the permissions are met
                dataPasser("Skip", "")
                # calls the dataPasser function
                await context.reply("Skipped")
            

### Pause ###

    @commands.command(aliases=["stop"])
    async def pause(self, context: commands.Context) -> None:
        """pause and stop"""

        if self.bot.channelLive and commandOptions["Pause"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Pause"]["cooldown_Chatter"], commandOptions["Pause"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Pause"):
                dataPasser("Pause", "")
                # calls the dataPasser function

                await context.reply(f"Paused")
                # replies to user

### Resume ###

    @commands.command(aliases=["continue", "play"])
    async def resume(self, context: commands.Context) -> None:
        """resume"""

        if self.bot.channelLive and commandOptions["Resume"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Resume"]["cooldown_Chatter"], commandOptions["Resume"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Resume"):
                # checks if the permissions are met
                dataPasser("Resume", "")
                # calls the dataPasser function

                await context.reply(f"Resumed")
                # replies to user

### Previous ###

    @commands.command()
    async def previous(self, context: commands.Context) -> None:
        """previous"""

        if self.bot.channelLive and commandOptions["Previous"]["enable"]:
        # checks if the channel is live and the command is enabled

            if not await self.cooldowns.cooldownCheck(context, commandOptions["Previous"]["cooldown_Chatter"], commandOptions["Previous"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Previous"):
                # checks if the permissions are met
                dataPasser("Previous", "")
                # calls the dataPasser function

                await context.reply(f"Went back")
                # replies to user

### Queue ###

    @commands.command()
    async def queue(self, context: commands.Context) -> None:
        """queue"""

        if self.bot.channelLive and commandOptions["Queue"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Queue"]["cooldown_Chatter"], commandOptions["Queue"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Queue"):
                # checks if the permissions are met
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, songLink = fullMsg.split(" ", 1)
                    # splits the command and link, stores link
                    if len(songLink) == 22 or songLink.startswith(("https://open.spotify.com/", "spotify:")):
                        # must be one of: "song uri, id, or url", so it checks if the length matches an ID's 22 character length
                        # or if the song starts with https://open.spotify.com/ or spotify: (signs of a valid URL or track URI)

                        trackName = dataPasser("Queue", songLink)
                        # calls the dataPasser function with the link

                        if trackName:
                            # if the track name is returned successfully (trackName actually has track + artist)
                            await context.reply(f"{trackName}")
                            # replies to user

                except:
                    # if the command fails
                    await context.reply(f"Add a valid Spotify link after !queue, please")
                    # replies to user 

### Song Color ###

    @commands.command(aliases=["songC"])
    async def songColor(self, context: commands.Context) -> None:
        """songColor / songC"""

        if self.bot.channelLive and commandOptions["Song Color"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Song Color"]["cooldown_Chatter"], commandOptions["Song Color"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Song Color"):
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, color = fullMsg.split(" ", 1)
                    # splits the command, stores the hex color code as color
                    dataPasser("Song Color", color)
                    # calls the dataPasser function with the color

                    if color.lower() == "clear":
                        await context.reply(f"Clearing song text color")
                    else:
                        await context.reply(f"Changing song text color")

                except:
                    # if the command fails
                    await context.reply(f"Add a valid color/hex code after !songColor, please")
                    # replies to user 

### Text Color ###

    @commands.command(aliases=["textC"])
    async def textColor(self, context: commands.Context) -> None:
        """textColor / textC"""

        if self.bot.channelLive and commandOptions["Text Color"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Text Color"]["cooldown_Chatter"], commandOptions["Text Color"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Text Color"):
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, color = fullMsg.split(" ", 1)
                    # splits the command, stores the hex color code as color
                    dataPasser("Text Color", color)
                    # calls the dataPasser function with the color

                    if color.lower() == "clear":
                        await context.reply(f"Clearing text color")
                    else:
                        await context.reply(f"Changing text color")

                except:
                    # if the command fails
                    await context.reply(f"Add a valid color/hex code after !textColor, please")
                    # replies to user 

### Bar Color ###

    @commands.command(aliases=["barC"])
    async def barColor(self, context: commands.Context) -> None:
        """barColor / barC"""

        if self.bot.channelLive and commandOptions["Bar Color"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Bar Color"]["cooldown_Chatter"], commandOptions["Bar Color"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Bar Color"):
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, color = fullMsg.split(" ", 1)
                    # splits the command, stores the hex color code as color
                    dataPasser("Bar Color", color)
                    # calls the dataPasser function with the color

                    if color.lower() == "clear":
                        await context.reply(f"Clearing progress bar color")
                    else:
                        await context.reply(f"Changing progress bar color")

                except:
                    # if the command fails
                    await context.reply(f"Add a valid color/hex code after !barColor, please")
                    # replies to user 

### Overlay Color ###

    @commands.command(aliases=["overlayC"])
    async def overlayColor(self, context: commands.Context) -> None:
        """overlayColor / overlayC"""

        if self.bot.channelLive and commandOptions["Overlay Color"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Overlay Color"]["cooldown_Chatter"], commandOptions["Overlay Color"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Overlay Color"):
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, color = fullMsg.split(" ", 1)
                    # splits the command, stores the hex color code as color

                    dataPasser("Overlay Color", color)
                    # calls the dataPasser function with the color

                    if color.lower() == "clear":
                        await context.reply(f"Clearing overlay color")
                    else:
                        await context.reply(f"Changing overlay color")

                except:
                    # if the command fails
                    await context.reply(f"Add a valid color/hex code after !overlayColor, please")
                    # replies to user 

### Custom Color ###

    @commands.command(aliases=["customC"])
    async def customColor(self, context: commands.Context) -> None:
        """customColor"""

        if self.bot.channelLive and commandOptions["Custom Color"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Custom Color"]["cooldown_Chatter"], commandOptions["Custom Color"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Custom Color"):
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, args = fullMsg.split(" ", 1)
                    # splits the command, stores the arguments as "args"

                    reply = dataPasser("Custom Color", args)
                    # calls the dataPasser function with the arguments, waits for return

                    await context.reply(f"{reply}")
                    # replies to user with string from SBO
                except:
                    # if the command fails
                    await context.reply(f"Command parse error, please check parameters and try again")
                    # replies to user 

### Playback Control ###

    @commands.command()
    async def playbackControl(self, context: commands.Context) -> None:
        """playbackControl"""
        global playbackControlsDisabled
        # stores the boolean here as a variable

        if self.bot.channelLive and commandOptions["Playback Control"]["enable"]:
        # checks if the channel is live and the command is enabled
        
            if not await self.cooldowns.cooldownCheck(context, commandOptions["Playback Control"]["cooldown_Chatter"], commandOptions["Playback Control"]["cooldown_Channel"]):
                # runs the cooldown check with the command options and message context
                if cooldownMessage:
                    # if the cooldown message config is enabled
                    await context.reply(f"Command is on cooldown")
                    # replies with cooldown message
                    return 
                    # stops the command from progressing 

            if isCoolChatter(context, "Playback Control"):
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, order = fullMsg.split(" ", 1)
                    # splits the command, stores the type of order given as "order"

                    order = order.lower().strip()
                    # lowercases and strips the command just in case

                    if order == "pause" or order == "stop":
                        # if the "order" is pause or stop
                        playbackControlsDisabled = True
                        # sets the playback control flag to true, preventing playback controls from running
                    elif order == "resume" or order == "continue":
                        # if the "order" is resume or continue
                        playbackControlsDisabled = False
                        # sets the playback control flag to false, allowing playback controls to run

                except:
                    # if the command fails
                    await context.reply(f"Please ensure correct parameter use")
                    # replies to user 

### SBO ###

    @commands.command(aliases=["SBO"])
    @commands.cooldown(rate = 1, per=300, key=commands.BucketType.channel)
    async def sbo(self, context: commands.Context) -> None:
        """sbo / SBO"""

        await context.reply(f"SBO is a Twitch Bot base made to simplify Spotify-Twitch connection, currently on {SBO_Bot_ver} // LP")
        # replies with the SBO details


            
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
    # checks if the channel/bot name exist (required for twitch API connection)
        print(f"Twitch/Bot username not found, please enter into the config file", flush=True)
        # user inform
        input("Press enter to exit", flush=True)
        raise SystemExit

if __name__ == "__main__":
    logWriter()
    # starts the console writer