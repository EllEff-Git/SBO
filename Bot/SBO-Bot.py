import json, os, sys, time
# Required for basic OS/system function and getting the config options for bot
import asyncio, asqlite, socket
# Required to connect to the bot
import twitchio, logging, webbrowser
# Required for the bot to function
from twitchio import *
# Required for the bot -> Chat connection
from twitchio.ext import commands
from twitchio.ext.commands import *
# Required to use commands in chat
from twitchio.ext.commands.exceptions import *
# Required to handle TwitchIO command errors without massive error logs
from botcfg import TwitchClientID
# Required to authorise twitch account
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
# Required imports to manage the PyQt window
from SBOver import Version
# Version manager



### Version ###

sboBotVer = Version
"""The SBO Bot version (Y.M.DD.HHMM)"""



### Logging Setup ###

logFormat = "%(message)s"
# changes the format from "[systemtime] [TYPE] message" to just "message"

logging.basicConfig(level = logging.INFO, format = logFormat)
# sets up a basic config with the logging level and format

logging.getLogger("twitchio").setLevel(logging.WARNING)
# sets TwitchIO to only print if it has a warning or higher (otherwise it spams)
logging.getLogger("twitchio.client").setLevel(logging.ERROR)
# sets the TwitchIO Client to only print on error or higher (there's a couple irrelevant warnings)
logging.getLogger("twitchio.commands").setLevel(logging.CRITICAL)
# sets the TwitchIO Commands to only print on critical errors (prints some useless stuff by default)
twitchio.utils.setup_logging(level=logging.ERROR)
# sets up a console log writer

if sys.stdout:
# if launched as a subprocess, and there's a standard output pipe
    sys.stdout.reconfigure(encoding="utf-8")
    # ensures it uses UTF-8 encoding
if sys.stdin:
# same thing, but for input
    sys.stdin.reconfigure(encoding="utf-8")
    # yep



### Setup ###

directory = os.path.dirname(sys.executable)
"""The base directory of the program, where SBO-Bot.exe resides"""

mainFolder = os.path.join(directory, "..", "..")
"""The main folder of SBO (2 folders up)"""
configFolderPath = os.path.join(os.environ["LOCALAPPDATA"], "SBO")
"""The folder path that should contain all the configuration files"""

funcConfigPath = os.path.join(configFolderPath, "functionConfig.json")
"""The full path to the functional config file (C:/Users/<user>/AppData/Local/SBO/functionConfig.json)"""
funcConfig = {}
"""The dictionary that contains all of the functional configuration"""

botConfigPath = os.path.join(configFolderPath, "botConfig.json")
"""The full path to the bot config file (C:/Users/<user>/AppData/Local/SBO/botConfig.json)"""
botConfig = {}
"""The dictionary that contains all of the bot's configuration"""

commandConfigPath = os.path.join(configFolderPath, "commandConfig.json")
"""The full path to the commandConfig.json file (C:/Users/<user>/AppData/Local/SBO/commandConfig.json)"""

tokenDatabase = os.path.join(configFolderPath, "tokens.db")
"""The full path to the Twitch token database (C:/Users/<user>/AppData/Local/SBO/tokens.db)"""
chatWindowPath = os.path.join(mainFolder, "runtime", "Qt", "botChatWindow", "botChatWindow.exe")
"""The full path to the chat window executable (SBO/Bot/botChatWindow.exe)"""



print(f"Loading SBO Twitch Bot {sboBotVer}...", flush=True)
# quick user update on status



### Variables ###

try:
# tries to read the funcConfig.json
    with open(funcConfigPath, "r", encoding="utf-8") as funcCfg:
    # opens the config file in read mode
        funcConfig = json.load(funcCfg)
        # stores the contents in the variable
except:
# if it can't (file doesn't exist)
    print("Unable to read the functional config file (E2)", flush=True)
    # user inform
    raise SystemExit
    # quits

webClientPort = (int(funcConfig.get("httpPort", 6868)) + 1)
"""The port to use for the PTP connection (http_Port + 1, int)"""



### Bot Variables ###

try:
# tries to read the botConfig.json
    with open(botConfigPath, "r", encoding="utf-8") as botCfg:
    # opens the config file in read mode
        botConfig = json.load(botCfg)
        # stores the contents in the variable
except:
# if it can't (file doesn't exist)
    print("Unable to read the bot's config file (E1)", flush=True)
    # user inform
    raise SystemExit
    # quits

commandPrefix = botConfig.get("commandPrefix", "!")
"""The symbol/string to use in front of all commands (default: !)"""
cooldownMessage = botConfig.get("cooldownMessages", False)
"""Whether to reply to chatter with a cooldown message if command is on cooldown (default: False)"""
cooldownMessageFormat = str(botConfig.get("cooldownMessageFormat", "Command is on cooldown ({duration})"))
"""The cooldown message's format (uses formatting: {duration} = remaining cooldown, {chatter} = chatter, {command} = command in question)"""
playbackControl = True
"""A boolean to check if the playback controls are enabled, boolean"""
overlayControl = True
"""A boolean to check if the overlay controls are enabled, boolean"""
requireLive = botConfig.get("controlLiveOnly", True)
"""Whether to require live status for commands, boolean"""
useSeparateBot = botConfig.get("useSeparateBot", True)
"""Whether to require two accounts (streamer + bot) for Twitch access"""

twitchClientID = TwitchClientID
"""The Twitch developer Client ID (from SBO Client Bot dev console)"""
sbo = {}
"""The data dictionary all the song information sits in (arrives from SBO main)"""

botScopes = twitchio.Scopes(
    user_read_chat=True,
    user_write_chat=True,
    user_bot=True
)
"""The Twitch access scopes used by the bot account""" 
streamScopes = twitchio.Scopes(
    channel_bot = True
)
"""The Twitch scope used by the stream account (allows the bot to enter)"""



### Command Configuration ###



commandConfig = {}
"""The dictionary that contains all of the command configuration"""
storedCommands = []
"""All commands stored in the configuration file"""
enabledCommands = []
"""All enabled commands in the config file"""

def commandConfigLoader():
    """Function to load the command configuration (allows for mid-operation reload)"""
    global commandConfig, storedCommands, enabledCommands
    # global -> local

    try:
    # tries to read the commandConfig.json
        with open(commandConfigPath, "r", encoding="utf-8") as cmdCfg:
        # opens the config file in read mode
            commandConfig = json.load(cmdCfg)
            # stores the contents in the variable
    except:
    # if it can't (file doesn't exist/error reading it)
        print("Unable to read the command config file (E2)", flush=True)
        # user inform
        raise SystemExit
        # quits

    storedCommands = []
    enabledCommands = []
    # resets both lists, since append would just double them immediately
    
    for cmd, detail in commandConfig.items():
    # goes through each command and its configuration
        storedCommands.append(cmd)
        # adds to the stored commands list
        if detail.get("enabled", False):
        # checks the enabled section of the command
            enabledCommands.append(cmd)
            # adds to the list of enabled commands

    print(f"{len(enabledCommands)} commands enabled for bot (of {len(storedCommands)})\nUsing command prefix '{commandPrefix}' (eg. {commandPrefix}song)", flush=True)
    # prints how many commands are enabled

commandConfigLoader()
# runs once immediately to get the command configuration dictionary



levelMap = {
    "Chatter": 0, 
    "Subscriber": 1,
    "VIP": 2,
    "Moderator": 3,
    "Lead Moderator": 4,
    "Streamer": 5
}
"""Map of chat levels (verbose -> digit)"""

queryCommands = ["playlist", "artist", "album", "song", "lastSong"]
"""The commands classified as 'query-only' (info requests, not playback controls)"""
playbackControlCommands = ["pause", "resume", "skip", "previous"]
"""The commands classified as 'playback control' (modify current Spotify playback somehow)"""
overlayControlCommands = ["songColor", "artistColor", "albumColor", "barColor", "overlayColor"]
"""The commands classified as 'overlay control' (modify current overlay visuals)"""



### Playback Control ###

async def dataPasser(command: str, arg2: str | None = None) -> str | None:
    """A function to send commands to SBO (takes the command / optionally: a string argument to pass to SBO)"""

    try:
        if arg2 is None:
        # if the second argument is empty (is just a playback command, eg. skip)
            msg = command
            # creates a message from just the command
        else:
        # if the second argument isn't empty (means there's a link, query, color attached)
            msg = f"{command}: {arg2}"
            # creates a string from the command and argument (uri/url/color...) 

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as webClient:
        # starts a new connection (with the same parameters)
            webClient.connect(("127.0.0.1", webClientPort))
            # connects to the existing host
            webClient.sendall(msg.encode("utf-8"))
            # sends the message

            returnableCommands = ["Playlist", "Queue", "QueueQ", "Custom Color"]
            # all the commands that expect a return 

            if command in returnableCommands:
            # if the command is one of the return-expecting ones, that means the reply requires data to be sent back from SBO
                response = webClient.recv(1024).decode("utf-8")
                # gets the response from SBO
            else:
            # if the command is anything else
                response = None
                # doesn't do anything, because that's expected

            webClient.close()
            # stops the connection when it's done
            return response
            # returns to calling function (command)

    except Exception as err:
    # if it fails for some reason
        print(f"Failed to send the command via PTP: {err}", flush = True)
        # prints an error inform
        return None
        # returns None



### Permission Check (Playback Control) ###

async def isCoolChatter(commandComponent: CommandComponent, context: commands.Context) -> bool:
    """Function to check if the calling chatter is authorised to use sent command"""

    if requireLive and not commandComponent.bot.channelLive:
    # if the live requirement is on and the channel isn't live
        await commandComponent.chatProcessSend(f"Live-only config option enabled, stream is not live", "SBOT")
        # user inform
        return False
        # stops

    chatter = context.author
    # assigns the message sender's author as "chatter"
    cmd = context.command.name
    # grabs the name of the command (no prefix/arguments)

    if not playbackControl:
    # if the playback controls are disabled
        if cmd in playbackControlCommands:
        # if the command is one of the playback controlling commands
            await commandComponent.chatProcessSend(f"Playback controls are disabled", "SBOT")
            # user inform in command log
            return False
            # stops running the function (not allowed)
        
    if not overlayControl:
    # if the overlay controls are disabled
        if cmd in overlayControlCommands:
        # if the ocmmand is one of the overlay controlling commands
            await commandComponent.chatProcessSend(f"Overlay controls are disabled", "SBOT")
            # user inform in command log
            return False
            # stops running the command (not allowed)
    
    reqLevelV = commandConfig.get(cmd, {}).get("requiredLevel", "Streamer")
    # gets the required level (verbose) for the command (defaults to Streamer if not found)
    reqLevel = levelMap[reqLevelV]
    # gets the digit from the level map
    chatterLevel = 0
    # starts variable as 0

    if chatter.broadcaster:
    # if the chatter is the streamer
        chatterLevel = 5
        # sets the level to 5 (highest)
    elif chatter.lead_moderator:
    # if the chatter is a lead moderator
        chatterLevel = 4
        # sets the level to 4
    elif chatter.moderator:
    # if the chatter is a moderator
        chatterLevel = 3
        # sets the level to 3
    elif chatter.vip or chatter.artist:
    # if the chatter is a VIP or artist
        chatterLevel = 2
        # sets the level to 2
    elif chatter.subscriber:
    # if the chatter is a subscriber
        chatterLevel = 1
        # sets the level to 1
    # if the user isn't any of the above, assumes normal user (chatter) (also fits admin, staff, etc)
    
    if chatterLevel >= reqLevel:
    # if the required level is lower or equal to the current chatter's level
        await commandComponent.chatProcessSend(f"Ran {cmd} for {chatter.display_name}", "SBOT")
        # user inform
        return True
        # returns the result; the chatter is, in fact, cool enough
    else:
    # level required is higher than user's level
        await commandComponent.chatProcessSend(f"{chatter.display_name} doesn't have the permission to run {commandPrefix}{cmd}: Required: {reqLevelV} (level {reqLevel}), {chatter.display_name} is level {chatterLevel})", "SBOT")
        # user inform
        return False
        # returns the result; the chatter, unfortunately, isn't cool enough :(



### Bot Class ###

class Bot(commands.Bot):
    """Twitch Bot class"""

    def __init__(self, *, tokenDatabase: asqlite.Pool, botAccID:str, strmAccID:str):
    # initialises with the passed token database
        self.tdb = tokenDatabase
        # stores the passed database in self
        self.streamID = str(strmAccID)
        # stores the stream ID reference in self
        # unsure why, but after setup, TwitchIO decides it should use owner_id = bot_id, and it breaks the 2-user conf

        super().__init__(
        # handles the passed argument assignment
            client_id = twitchClientID,
            client_secret=None,
            bot_id = botAccID,
            owner_id = strmAccID,
            prefix = commandPrefix
        )
        # initialisation with passed arguments/globals

        print(f"Twitch bot initialising...", flush=True)
        # user inform

        self.channelLive = False
        # boolean for if the channel is live

### Component Setup ###

    async def setup_hook(self) -> None:
        """Function that begins Bot setup"""

        self.commandComponent = CommandComponent(self)
        # instantiates the commands class

        await self.add_component(self.commandComponent)
        # adds the command class formed below to the bot
        await self.add_component(ErrorComponent(self))
        # adds the error handler component from below 
        # (this exists largely to prevent INSANE log spam with 5-row messages about missing command when a chatter just types "hi")

### Token Load ###

    async def load_tokens(self, path=None):
        """Function to load tokens"""
        # auto-called by the class on login

        async with self.tdb.acquire() as connection:
        # connects to the database
            rows = await connection.fetchall(
                """
                SELECT user_id, access_token, refresh_token
                FROM tokens
                ORDER BY CASE status
                    WHEN 'Bot' THEN 0
                    WHEN 'Stream' THEN 1
                END
                """
            )
            # grabs access and refresh tokens (ensures the ordering)

        for row in rows:
        # goes through every row in the database
            await self.add_token(
                row["access_token"],
                row["refresh_token"]
            )
            # adds both tokens to the bot twitchio client (this way they'll be managed by twitchio for refreshing and such)

### Token Refresh ###

    async def event_token_refreshed(self, payload: twitchio.TokenRefreshedPayload) -> None:
        """Token refresh event handler"""

        query = """
        UPDATE tokens
        SET access_token = ?,
            refresh_token = ?
        WHERE user_id = ?
        """
        # updates the databased token and refresh token, keeps the user_id

        async with self.tdb.acquire() as connection:
        # connects to the database
            await connection.execute(query, (payload.token, payload.refresh_token, payload.user_id))
            # executes the query (updates the tokens for given user_id)

        print(f"Refreshed Twitch token", flush=True)
        # user inform

### Ready Console Log ### 

    async def event_ready(self) -> None:
        """Ready status event (triggered when the rest of the setup is done)"""

        subs = self.websocket_subscriptions()
        # requests all the active twitch event subscriptions

        print(f"Active websocket subscriptions: {len(subs)}", flush=True)
        # pseudo-debug (only matters if this value is in the range of double-digit, before that it's pretty benign)

        #for sub in subs.values():
        # goes through every subscription
            #print(f"Sub type: {sub.type}, sub details: {sub.condition}", flush=True)
            # spits out the type of subscription and the condition

        onlineSub = eventsub.StreamOnlineSubscription(broadcaster_user_id = self.streamID)
        # forms a payload for the event "stream is *online*" to listen to (this account)

        offlineSub = eventsub.StreamOfflineSubscription(broadcaster_user_id = self.streamID)
        # forms a payload for the event "stream is *offline*"" to listen to (this account)

        self.channelLive = await self.liveCheck()
        # runs the live check once at start to ensure channel wasn't live before bot was started

        await self.subscribe_websocket(payload = onlineSub, as_bot = True)
        # subscribes to the online event

        await self.subscribe_websocket(payload = offlineSub, as_bot = True)
        # subscribes to the offline event

        chatSub = eventsub.ChatMessageSubscription(broadcaster_user_id = self.streamID, user_id = self.bot_id)
        # forms a payload to "subscribe" to a chat (room), passes the chat to subscribe to (broadcaster) and who to subscribe as (user)

        await self.subscribe_websocket(payload = chatSub, as_bot = True)
        # subscribes to an eventsub websocket (the payload formed above)

        print(f"Successfully logged in as {self.user.display_name}!", flush=True)
        # prints the login message to console (for the bot)

        if requireLive and not self.channelLive:
        # if all the checks are done, the channel is not yet live and live is required
            print("Control commands disabled ('Control Only When Live' is enabled)", flush=True)
            # user inform
        elif not requireLive and not self.channelLive:
        # if all the checks are done, the channel is not live yet and live isn't required
            print("Control commands enabled ('Control Only When Live' is disabled)", flush=True)
            # user inform

### Stream Status Checks ###

    async def liveCheck(self) -> bool:
        """Function to grab live status once"""
        
        streams = [stream async for stream in self.fetch_streams(user_ids=[self.streamID], token_for=self.bot_id)]
        # goes through "every stream" (just one) and fetches status

        return bool(streams)
        # returns the boolean on whether the given stream is live

    async def event_stream_online(self, payload: twitchio.StreamOnline) -> None:
        """Function that triggers when the stream goes live"""
        self.channelLive = True
        # sets the boolean right away
        print(f"{self.user.display_name} is now online!", flush=True)
        # user inform

    async def event_stream_offline(self, payload: twitchio.StreamOffline) -> None:
        """Function that triggers when the stream goes offline"""
        self.channelLive = False
        # sets the boolean right away
        print(f"{self.user.display_name} is now offline!", flush=True)
        # user inform



### Cooldown Manager ###

class CooldownManager:
    """Class that hosts a cooldown management function"""
    def __init__(self):
    # initialisation

        self.chatterCDs = {}
        # tracks the per-chatter cooldowns (key = chatterID, command) (timestamp)
        self.channelCDs = {}
        # tracks the per-channel cooldowns (key = channel, command) (timestamp)

    async def cooldownCheck(self, commandComponent: CommandComponent, context:commands.Context) -> int:
        """Function to check the cooldown of passed command, returns the cooldown remaining (0 if none)"""

        await commandComponent.chatProcessSend(context.message.text, context.chatter.display_name)
        # calls the chat process sender with the message + user

        passedCommand = context.command.name
        # stores the command name
        passedCmdConfig = commandConfig.get(passedCommand, {})
        # gets the command cooldown configuration of the passed command

        if not passedCmdConfig.get("enabled", False):
        # if the command's configuration has the enabled bool set to False (not True)
            await commandComponent.chatProcessSend(f"{passedCommand} is disabled via config", "SBOT")
            # user inform via chat process (window)
            return 62701
            # returns an arbitrary number to prevent the command from running 
            # (I literally did "random number between 9999 and 99999", odds of anyone having *this* cooldown are so slim it's not a real concern)

        chatterStatus = context.author
        # stores the chatter's "status" (details)
        if chatterStatus.broadcaster:
            # checks if the chatter is the streamer
            return 0
            # skips everything and returns 0 (no cooldown for streamer)

        chatterCDTime = passedCmdConfig.get("chatterCooldown", 60)
        channelCDTime = passedCmdConfig.get("channelCooldown", 60)
        # gets the chatter and channel cooldown times 

        chatterName = chatterStatus.display_name
        # stores the chatter's name (debug)

        now = int(time.time())
        # stores the current UNIX time (in seconds)
        chatterKey = (context.author.id, passedCommand)
        # stores the chatter's ID and the command used as a tuple (x, y)
        channelKey = (context.channel.name, passedCommand)
        # stores the channel's name and the command used as a tuple (x, y)

        chatterCD = self.chatterCDs.get(chatterKey, 0)
        # gets the last time the chatter in question ran the command (current time, if none is found)
        channelCD = self.channelCDs.get(channelKey, 0)
        # gets the last time *anyone* used the command (current time, if none is found)

        chatterCDduration = max(0, (chatterCDTime - (now - chatterCD)))
        # gets the duration of the cooldown for the chatter
        channelCDduration = max(0, (channelCDTime - (now - channelCD)))
        # gets the duration of the cooldown for the channel

        cdDuration = max(chatterCDduration, channelCDduration)
        # gets the highest cooldown duration for the command

        if cdDuration > 0:
        # if there's more than 0 seconds left on *any* cooldown
            await commandComponent.chatProcessSend(f"{chatterName} has {cdDuration}s left on cooldown!", "SBOT")
            # user inform via chat process (window)
            return cdDuration
            # returns the duration of the cooldown

        self.chatterCDs[chatterKey] = now
        # sets the last time the user ran the command to match current time
        self.channelCDs[channelKey] = now
        # sets the last time the command was run channel-wide to match the current time

        return 0
        # returns 0 now that the timestamps have been updated

    async def cooldownReply(self, context: commands.Context, cdDuration: int):
        """Function to reply to the command sender with a cooldown message"""

        if not cooldownMessage:
        # if cooldown messages are disabled via config
            return
            # doesn't run command

        if cdDuration == 62701:
        # if the cooldown is *exactly* 62701 (bypass number)
            return
            # doesn't run command

        try:
        # tries to...
            reply = cooldownMessageFormat.format(
                duration = cdDuration,
                chatter = context.author.display_name,
                command = context.command.name
            )
            # forms a reply based on the user-configured cooldown message format
        except KeyError as spell:
        # if there's a spelling mistake in one of the variables
            print(f"Incorrect variable in cooldown message format: {spell}", flush=True)
            # user inform
        except Exception as err:
        # some other error
            print(f"Error forming cooldown message from format: {err}", flush=True)
            # user inform

        await context.reply(reply)
        # replies with the formed reply



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

### Chat Process ###

        self.chatProcess = QProcess(botApp)
        # a process to host a pseudo-chat window
        self.chatProcess.start(chatWindowPath)
        # starts the chat window as a subprocess of this process
        botApp.aboutToQuit.connect(self.chatProcess.terminate)
        # tries to close the chat process when the application is closing

### Listener ###

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        """Message grabber/listener"""

        if not useSeparateBot:
        # single-account users require this to be called manually (otherwise it doesn't process commands)
            await self.bot.process_commands(payload)
            # calls the bot command processor to process the chat message

### Chat Process Sender ###

    async def chatProcessSend(self, message:str, sender:str):
        """Function to send messages to the chat process"""

        finalMessage = f'{time.strftime("%H:%M:%S", time.localtime())} | {sender}: {message}\n'
        # formats cleanly to include following format: HH:MM:SS | TWITCHUSER/SBOT/SBO-SYS: !verycoolmessage

        try:
            self.chatProcess.write(finalMessage.encode("utf-8"))
            # writes to the QProcess to keep it in a deque, encodes with utf-8
        except:
        # if there's an error (someone calls a message right as program closes or crashes)
            pass
            # does nothing

### Message Argument Failure ###

    async def commandArgumentError(self, context: commands.Context):
        """Function to send a reply on a failed argument check"""

        try:
        # tries to
            cmd = f"{context.command.name} "
            # grabs the command
        except:
        # can't get command name
            cmd = " "
            # sets the string to nothing

        await context.reply(f"Please double-check your arguments! Try {commandPrefix}sboHelp {cmd}for usage tips")
        # general failure reply

### Not Playing Spotify Reply ###

    async def notSpotifyPlaybackReply(self, context: commands.Context):
        """Function to send a reply on a no-playstate context"""

        await context.reply(f"{context.channel.display_name} isn't currently listening to Spotify")
        # general playback-less reply



### Playlist ###

    playlistAlias = commandConfig.get("playlist", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[playlistAlias] if playlistAlias else [])
    async def playlist(self, context: commands.Context) -> None:
        """playlist"""

        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 
                
        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify
                playlistName = await dataPasser("Playlist")
                # passes the command to dataPasser -> SBO
                if playlistName:
                # if the string is returned
                    await context.reply(f"{playlistName}")
                    # replies with the returned message
                else:
                # if the string isn't returned for some reason
                    await context.reply(f"Couldn't find playlist, sorry!")
                    # fail state reply
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Album ###

    albumAlias = commandConfig.get("album", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[albumAlias] if albumAlias else [])
    async def album(self, context: commands.Context) -> None:
        """album"""

        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify

                albumURL = sbo.get("Album URL")
                # gets the album URL from the dictionary
                if albumURL == "A local album":
                # if the album isn't set (SBO sets it to this if playback is local)
                    await context.reply(f"{context.channel.display_name} is listening to a local album")
                    # sends a album-less message
                else:
                # if the url is anything else
                    albumName = sbo.get("Album Name")
                    # gets the name of the album, too
                    await context.reply(f"Current album: {albumName} {albumURL}")
                    # sends a message with the album URL
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Artist ###

    artistAlias = commandConfig.get("artist", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[artistAlias] if artistAlias else [])
    async def artist(self, context: commands.Context) -> None:
        """artist"""

        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify

                artistURL = sbo.get("Artist URL")
                # gets the artist name from the dictionary
                if artistURL == "A local artist":
                # if the artist isn't set (SBO sets it to this if playback is local)
                    await context.reply(f"{context.channel.display_name} is listening to a local artist")
                    # sends a album-less message
                else:
                # if the url is anything else
                    artistName = sbo.get("Artist Name")
                    # gets the name of the artist, too
                    await context.reply(f"Current artist: {artistName} {artistURL}")
                    # sends a message with the artist URL
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Song ###

    songAlias = commandConfig.get("song", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[songAlias] if songAlias else [])
    async def song(self, context: commands.Context) -> None:
        """song"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify
                track = sbo.get("Song Name")
                # gets the track from the dictionary
                artist = sbo.get("Artist Name")
                # gets the artist name from the dictionary
                trackURL = sbo.get("Spotify URL")
                # gets the track URL from the dictionary
                
                if trackURL == "A local song":
                # if the song is local (SBO sets it to this if playback is local)
                    await context.reply(f"{context.channel.display_name} is listening to a local song")
                    # sends a local song message
                elif trackURL == "None" or trackURL == None:
                # if the song is empty
                    await context.reply(f"{context.channel.display_name} is not listening to Spotify")
                    # replies with a no song detected message
                    print(f"If you see this message, but your Spotify is playing, check the status of SBO and Spotify", flush=True)
                    # user inform in case something went wrong
                else:
                # if the song return is anything else
                    await context.reply(f"{track} by {artist} {trackURL}")
                    # sends a message with the song URL
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Last Song ###

    lastSongAlias = commandConfig.get("lastSong", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[lastSongAlias] if lastSongAlias else [])
    async def lastSong(self, context: commands.Context) -> None:
        """lastSong"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify
                track = sbo.get("Last Song")
                # gets the track from the dictionary
                artist = sbo.get("Last Artist")
                # gets the artist name from the dictionary
                trackURL = sbo.get("Last URI")
                # gets the track URL from the dictionary
                
                if trackURL == "A local song":
                # if the song is local (SBO sets it to this if playback is local)
                    await context.reply(f"{context.channel.display_name} last listened to a local song")
                    # sends a local song message
                elif trackURL == "None" or trackURL == None:
                # if the song is empty
                    await context.reply(f"Couldn't find previous song for {context.channel.display_name}, sorry!")
                    # replies with a no last song message
                    print(f"If you see this message, but your Spotify is playing (and the program has been up for more than 1 song), check the status of SBO and Spotify", flush=True)
                    # user inform in case it fails
                else:
                # if the song return is anything else
                    await context.reply(f"Last song: {track} by {artist} {trackURL}")
                    # sends a message with the song URL
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Pause ###

    pauseAlias = commandConfig.get("pause", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[pauseAlias] if pauseAlias else [])
    async def pause(self, context: commands.Context) -> None:
        """pause"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify
                await dataPasser("Pause")
                # calls the dataPasser function

                await context.reply(f"Paused")
                # replies to user
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Resume ###

    resumeAlias = commandConfig.get("resume", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[resumeAlias] if resumeAlias else [])
    async def resume(self, context: commands.Context) -> None:
        """resume"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify
                await dataPasser("Resume")
                # calls the dataPasser function

                await context.reply(f"Resumed")
                # replies to user
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Skip ###

    skipAlias = commandConfig.get("skip", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[skipAlias] if skipAlias else [])
    async def skip(self, context: commands.Context) -> None:
        """skip"""
    
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify
                await dataPasser("Skip")
                # calls the dataPasser function

                await context.reply("Skipped")
                # replies to user
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Previous ###

    previousAlias = commandConfig.get("previous", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[previousAlias] if previousAlias else [])
    async def previous(self, context: commands.Context) -> None:
        """previous"""

        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            if sbo.get("Playback State", True):
            # checks if the user is listening to Spotify
                await dataPasser("Previous")
                # calls the dataPasser function

                await context.reply(f"Went back")
                # replies to user
            else:
            # if no playback is detected
                await self.notSpotifyPlaybackReply(context)
                # calls the playback-less function to reply with a default string

### Queue ###

    queueAlias = commandConfig.get("queue", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[queueAlias] if queueAlias else [])
    async def queue(self, context: commands.Context) -> None:
        """queue"""

        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            try:
                songLink = context.content.split(" ", 1)[1].strip()
                # splits the command and link, stores link, strips of whitespace

                if len(songLink) == 22 or songLink.startswith("https://open.spotify.com/") or songLink.startswith("spotify:"):
                # must be one of: "song uri, id, or url", so it checks if the length matches an ID's 22 character length
                # or if the song starts with https://open.spotify.com/ or spotify: (signs of a valid URL or track URI)

                    if "?si=" in songLink:
                    # if the song link has a 'tracker' from Spotify at the end
                        songLink = songLink.split("?si=", 1)[0]
                        # splits the track link via the tracker, grabs the 0th element

                    trackName = await dataPasser("Queue", songLink)
                    # calls the dataPasser function with the link
                    if trackName:
                        # if the track name is returned successfully (trackName actually has track + artist)
                        await context.reply(f"{trackName}")
                        # replies to user
                else:
                # link not long enough, doesn't start with spotify url or track id
                    await context.reply(f"Add a valid Spotify link, ID or URI after {commandPrefix}queue, please")
                    # replies to user
            except Exception as err:
            # if the command fails
                await context.reply(f"Add a valid Spotify link, ID or URI after {commandPrefix}queue, please")
                # replies to user 

### QueueQ ###

    queueqAlias = commandConfig.get("queueq", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[queueqAlias] if queueqAlias else [])
    async def queueq(self, context: commands.Context) -> None:
        """queueq"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met

            fullMsg = context.content
            # gets the full message from the contents
            try:
                cmd, songDetails = fullMsg.split(" ", 1)
                # splits the command and link, stores link
                songDetails.strip()
                # ensures no spaces make it through unintentionally

                if songDetails:
                # if there's something in the arguments
                    trackName = await dataPasser("QueueQ", songDetails)
                    # calls the dataPasser function with the link
                    if trackName:
                    # if the track name is returned successfully (trackName actually has track + artist)
                        await context.reply(f"{trackName}")
                        # replies to user
                else:
                # no arguments
                    await context.reply(f"Add a song name after {commandPrefix}queueq, please!")
                    # replies to user
            except:
            # if there's an issue with split or something (likely missing arguments)
                await context.reply(f"Add a song name after {commandPrefix}queueq, please!")
                # replies to user

### Song Color ###

    songColorAlias = commandConfig.get("songColor", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[songColorAlias] if songColorAlias else [])
    async def songColor(self, context: commands.Context) -> None:
        """songColor"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            fullMsg = context.content
            # gets the full message from the contents
            try:
                cmd, color = fullMsg.split(" ", 1)
                # splits the command, stores the hex color code as color

                color = color.strip()
                # ensures no empty space makes it through

                await dataPasser("Song Color", color)
                # calls the dataPasser function with the color

                if color.lower() == "clear":
                    await context.reply(f"Clearing song text color")
                else:
                    await context.reply(f"Changing song text color")

            except:
                # if the command fails
                await context.reply(f"Add a valid color/hex code after {commandPrefix}songColor, please")
                # replies to user 

### Artist Color ###

    artistColor = commandConfig.get("artistColor", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[artistColor] if artistColor else [])
    async def artistColor(self, context: commands.Context) -> None:
        """artistColor"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            fullMsg = context.content
            # gets the full message from the contents
            try:
                cmd, color = fullMsg.split(" ", 1)
                # splits the command, stores the hex color code as color

                color = color.strip()
                # ensures no empty space makes it through

                await dataPasser("Artist Color", color)
                # calls the dataPasser function with the color

                if color.lower() == "clear":
                    await context.reply(f"Clearing text color")
                else:
                    await context.reply(f"Changing text color")

            except:
                # if the command fails
                await context.reply(f"Add a valid color/hex code after {commandPrefix}textColor, please")
                # replies to user 

### Album Color ###

    albumColorAlias = commandConfig.get("albumColor", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[albumColorAlias] if albumColorAlias else [])
    async def albumColor(self, context: commands.Context) -> None:
        """albumColor"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            fullMsg = context.content
            # gets the full message from the contents
            try:
                cmd, color = fullMsg.split(" ", 1)
                # splits the command, stores the hex color code as color

                color = color.strip()
                # ensures no empty space makes it through

                await dataPasser("Album Color", color)
                # calls the dataPasser function with the color

                if color.lower() == "clear":
                    await context.reply(f"Clearing text color")
                else:
                    await context.reply(f"Changing text color")

            except:
                # if the command fails
                await context.reply(f"Add a valid color/hex code after {commandPrefix}textColor, please")
                # replies to user 

### Bar Color ###

    barColorAlias = commandConfig.get("barColor", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[barColorAlias] if barColorAlias else [])
    async def barColor(self, context: commands.Context) -> None:
        """barColor"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            fullMsg = context.content
            # gets the full message from the contents
            try:
                cmd, color = fullMsg.split(" ", 1)
                # splits the command, stores the hex color code as color
                color = color.strip()
                # ensures no empty space makes it through

                await dataPasser("Bar Color", color)
                # calls the dataPasser function with the color

                if color.lower() == "clear":
                    await context.reply(f"Clearing progress bar color")
                else:
                    await context.reply(f"Changing progress bar color")

            except:
                # if the command fails
                await context.reply(f"Add a valid color/hex code after {commandPrefix}barColor, please")
                # replies to user 

### Overlay Color ###

    overlayColorAlias = commandConfig.get("songColor", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[overlayColorAlias] if overlayColorAlias else [])
    async def overlayColor(self, context: commands.Context) -> None:
        """overlayColor"""
        
        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            fullMsg = context.content
            # gets the full message from the contents
            try:
                cmd, color = fullMsg.split(" ", 1)
                # splits the command, stores the hex color code as color

                color = color.strip()
                # ensures no empty space makes it through

                await dataPasser("Overlay Color", color)
                # calls the dataPasser function with the color

                if color.lower() == "clear":
                    await context.reply(f"Clearing overlay color")
                else:
                    await context.reply(f"Changing overlay color")

            except:
                # if the command fails
                await context.reply(f"Add a valid color/hex code after {commandPrefix}overlayColor, please")
                # replies to user 

### Custom Color ###

    customColorAlias = commandConfig.get("customColor", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[customColorAlias] if customColorAlias else [])
    async def customColor(self, context: commands.Context) -> None:
        """customColor"""

        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            fullMsg = context.content
            # gets the full message from the contents
            try:
                cmd, args = fullMsg.split(" ", 1)
                # splits the message to command and arguments by the empty space

                reply = await dataPasser("Custom Color", args)
                # calls the dataPasser function with the arguments, waits for return

                await context.reply(f"{reply}")
                # replies to user with string from SBO
            except:
                # if the command fails
                await context.reply(f"Command parse error, please check parameters and try again")
                # replies to user 

### SBO Help ###

    sboHelpAlias = commandConfig.get("sboHelp", {}).get("alias", None)
    # gets any aliases, passes them to the command

    @commands.command(aliases=[sboHelpAlias] if sboHelpAlias else [])
    async def sboHelp(self, context: commands.Context) -> None:
        """sboHelp"""

        cmdCD = await self.cooldowns.cooldownCheck(self, context)              
        # runs the cooldown check with the message context to get the duration of cooldown left
        if cmdCD > 0:
        # if there's more than 0 seconds left (there's an active cooldown)
            await self.cooldowns.cooldownReply(context, cmdCD)
            # runs the cooldown reply with the message context
            return 
            # stops the command from progressing 

        if await isCoolChatter(self, context):
        # checks if the permissions are met
            fullMsg = context.content
            # gets the full message from the contents
            try:
            # tries to split the message
                args = fullMsg.split(" ", 1)[1]
                # splits the message to command and arguments by the empty space, grabs arguments only
                if args:
                # if arguments (some command) were passed
                    args = args.lower()
                    # lowercase (just a safety thing)
                    if commandPrefix in args:
                    # if the command prefix (eg. !) is in the argument
                        args = args.strip(commandPrefix)
                        # removes the prefix
                    if args == "commands":
                    # if it's to get commands list
                        await context.reply(f"Channel-enabled commands: {", ".join(enabledCommands)}")
                        # joins the enabled commands
                        return
                        # stops
                    if args in enabledCommands:
                    # if the 'arguments' match an enabled command
                        commandSyntax = commandConfig.get(args, {}).get("syntax")
                        # gets the command's syntax from the config
                        if commandSyntax:
                        # if there's stored syntax for that command
                            await context.reply(f"{args}: {commandSyntax}")
                            # replies to user with command syntax
                            return
                            # stops (since a match was found)
                        else:
                        # stores syntax
                            await context.reply(f"{args} has no usage guide set, sorry!")
                            # replies to user with no command syntax
                            return
                            # stops (since a match was found)
                else:
                # no arguments
                    raise
                    # causes fault to trigger fallback
            except:
            # no arguments (fallback)
                await context.reply(f"Run {commandPrefix}sboHelp with a command name (eg. {commandPrefix}sboHelp queue) or 'commands' ({commandPrefix}sboHelp commands)")
                # replies to user with default fallback text about sboHelp



### Command Errors ###

class ErrorComponent(commands.Component):
    """Class to handle TwitchIO errors (via twitchio docs, modified to suppress errors)"""
    def __init__(self, bot: Bot) -> None:

        self.original = bot.event_command_error
        # stores the original error handler (something something it'll get unloaded and then break?)
        bot.event_command_error = self.event_command_error
        # overrides the default bot error handler with the new custom one
        self.bot = bot
        # stores ref to bot class

    async def component_teardown(self) -> None:
        self.bot.event_command_error = self.original
        # reassigns the command handler again (don't ask me how this works, this is from TwitchIO's docs)

    async def event_command_error(self, payload: commands.CommandErrorPayload):
        """Handles Twitch(IO) command errors"""
        context = payload.context
        # stores the payload context as context
        command = context.command
        # stores the command
        error = payload.exception
        # stores the error message

        if command and command.has_error and context.error_dispatched:
        # if the error has been handled (dispatched)
            return
            # stops

        elif isinstance(error, commands.CommandNotFound):
        # if the error is "command not found"
            return
            # stops (expected)

        elif isinstance(error, commands.GuardFailure):
        # if the error is permission (guard) related
            return
            # stops (expected)

        print(f"Unable to handle message error with command '{command}'; {error}", flush=True)
        # if the error isn't one of the above, and it reaches the print, sends a debug message



### Auth Accept Inputs ###

class UserInteractWindow(QDialog):
    """Class to call when the user needs to interact with something before continuing"""
    def __init__(self, message: str, title:str, linkMode:bool, link:str | None=None, parent=None):
        # init
        super().__init__(parent)

        self.setWindowTitle(title)
        # sets the window title from passed arguments
        self.setMinimumSize(750, 450)
        # sets window min size
        self.resize(750, 450)
        # ensures the window is that size

        self.messageLabel = QLabel(message)
        # creates a label for the passed message to go into
        self.messageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.statusLabel = QLabel(" ")
        # creates a label for user inform status
        self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # centers the text

        self.uiwLayout = QGridLayout()
        # layout to place all widgets into
        self.uiwBtnLayout = QGridLayout()
        # layout to place all buttons into
        self.link = link
        # stores the passed link to self (if one is passed)

        if linkMode:
        # if this is for copying/opening a link
            self.statusLabel.setText("Avoid sharing the links to anyone")
            # changes the status text to a warning

            self.copyButton = QPushButton("Copy Link")
            self.copyButton.setToolTip("Copy link to clipboard")
            self.copyButton.setFixedSize(150, 50)
            # button to copy link
            self.openBrowserButton = QPushButton("Open Link")
            self.openBrowserButton.setToolTip("Open link in default browser")
            self.openBrowserButton.setFixedSize(150, 50)
            # button to open the link

            self.copyButton.clicked.connect(lambda: self.linkFunction("Copy"))
            # connects the copy button to copy the passed link to clipboard for user to paste
            self.openBrowserButton.clicked.connect(lambda: self.linkFunction("Open"))
            # connects the open button to open the default browser with passed link

            self.uiwBtnLayout.addWidget(self.copyButton, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.uiwBtnLayout.addWidget(self.openBrowserButton, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds both to layout (bottom row, 2nd and 3rd col)

        else:
        # not for links (checks)
            self.continueButton = QPushButton("Continue")
            self.continueButton.setFixedSize(150, 50)
            # button to continue
            self.continueButton.clicked.connect(self.accept)
            # connects the continue button to accept
            self.uiwBtnLayout.addWidget(self.continueButton, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            # adds the continue button to the 2nd column of row 2 (0,1)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setFixedSize(150, 50)
        # button to cancel
        self.cancelButton.clicked.connect(self.reject)
        # connects the buttons to acceptance and rejection (can be captured)

        self.uiwLayout.addWidget(self.messageLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.uiwLayout.addWidget(self.statusLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        self.uiwLayout.addLayout(self.uiwBtnLayout, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the labels + button layout
        self.uiwBtnLayout.addWidget(self.cancelButton, 2, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        # adds the cancel button to the bottom left

        self.setLayout(self.uiwLayout)
        # sets the central layout 

    def linkFunction(self, action:str):
        """Function to manipulate the buttons and their link actions"""

        if action == "Copy":
        # copy link action
            self.copyButton.setText("Copied!")
            # sets the text on the button to indicate it was copied
            QApplication.clipboard().setText(self.link)
            # copies the link to clipboard
        else:
        # open link action
            self.openBrowserButton.setText("Opened!")
            # sets the text on the button to indicate it was opened
            webbrowser.open(self.link)
            # opens the link in browser

        self.statusLabel.setText(f"Continuing authentication in 5 seconds\nThis window will close...")
        # user inform
        QTimer.singleShot(5000, self.accept)
        # waits 5 seconds, then calls "accept" to close the window and move on



### Authorisation Class ###

class OAuthClient(twitchio.Client):
    """The intial Twitch authorisation handler class"""
    def __init__(self, *, tokenDatabase: asqlite.Pool, scopes: twitchio.Scopes):
        # init requirements (needs the database and the requested scopes)

        self.tdb = tokenDatabase
        # stores the passed database as tdb in self(TokenDataBase)

        super().__init__(
            client_id=twitchClientID,
            scopes=scopes
        )
        # initialises with the developer client ID token (from SBO developer dashboard) and the scopes



### Database / Token Storage Setup ###

async def setupTokenDB(db: asqlite.Pool) -> None:
    """Function to create a token database"""

    query = """
    CREATE TABLE IF NOT EXISTS tokens(
        user_id INTEGER PRIMARY KEY,
        access_token TEXT NOT NULL,
        refresh_token TEXT NOT NULL,
        status TEXT NOT NULL UNIQUE CHECK (status IN ('Bot', 'Stream'))
    )
    """
    # the query to use to create the database 
    # user_id is the userID of the twitch user
    # access_token and refresh_token slots house the, well, tokens
    # status is "Bot" or "Stream", determines which account type is targeted (unique makes sure there's only one of each)

    async with db.acquire() as connection:
    # calls .acquire to get the information from the database
        await connection.execute(query)
        # executes the afore-formed query



### Database Grab ###

async def getStoredUser(db: asqlite.Pool, status:str):
    """Function to get the stored user data from database"""

    async with db.acquire() as connection:
    # connects to the database
        row = await connection.fetchone(
        # targets all items in the database for one row (databases store *rows* of data)
            """
            SELECT user_id, access_token, refresh_token, status
            FROM tokens
            WHERE status = ?
            """,
            (status,)
        )
        # grabs all the database items

    return row if row else None
    # returns the list (row) of data (user's info + access and refresh tokens)


### Auth Twitch Accounts ###

async def authenticateTwitchUsers():
    """Startup/run function"""

    async with asqlite.create_pool(tokenDatabase) as tdb:
    # 'connects' to the tokens.db file, references as tbd (tokenDataBase)
        await setupTokenDB(tdb)
        # waits for setup to be done

        print(f"Authenticating Twitch...", flush=True)
        # user inform

        botAccount = await getStoredUser(tdb, "Bot")
        # grabs the stored database of info on the bot account
        streamAccount = await getStoredUser(tdb, "Stream")
        # grabs the stored database of info on the stream account

        botID = str(botAccount["user_id"]) if botAccount else None
        # grabs the account ID for the bot account, falls back to None if the database doesn't contain that info
        streamID = str(streamAccount["user_id"]) if streamAccount else None
        # grabs the user_id for the stream account, too

        if botID is None:
        # if there's nothing yet (first launch)
            print(f"Please authenticate your Twitch Bot account!", flush=True)
            # user inform

            if useSeparateBot:
            # if the use-two account config option is on
                userInteractString = (f"Authorise Bot Account\n\n"
                                    "This step is to link the account sending the messages in the stream to SBO\n"
                                    "You've selected to use two accounts, the bot will appear as the bot account in chat\n\n"
                                    "Please ensure you're logged into the account you wish to use as the Bot at this stage\n"
                                    "You'll be prompted once more and given the option to copy the authorisation link\n"
                                    "\n\n"
                                    "This action *is* reversible, nothing is permanent, so don't stress too much :)")
                # forms a string to pass
            else:
            # only one account
                userInteractString = (f"Authorise Dual-Purpose Account\n\n"
                                    "This step is to link the account used both as the bot and the stream\n"
                                    "You've selected to use one account, the bot will appear as your main account in chat\n\n"
                                    "Please ensure you're logged into your main account\n"
                                    "You'll be prompted once more and given the option to copy the authorisation link\n"
                                    "\n\n"
                                    "This action *is* reversible, nothing is permanent, so don't stress too much :)")
                # forms a string to pass

            userInteract = UserInteractWindow(userInteractString, "Twitch Bot Authorisation", False)
            # creates a window for the user to press, passes the pre-formed string
            interactResult = userInteract.exec()
            # runs the window, captures result

            if interactResult == QDialog.DialogCode.Accepted:
            # if the user pressed continue
                botID = await authoriseTwitch(tdb, botScopes, "Bot")
                # calls the auth twitch function to get the ID of the bot account
            else:
            # user closed or pressed cancel
                print(f"Cancelling authentication...\nPlease restart SBO to retry authorisation", flush=True)
                # user inform
                await asyncio.sleep(5)
                # waits 5 seconds
                raise SystemExit
                # stops

        if useSeparateBot and (streamID is None):
        # if the config option to use 2 separate accounts is set to True
            print(f"Please authenticate your Twitch Stream account!", flush=True)
            # user inform

            userInteractString = (f"Authorise Main/Stream Account\n\n"
                                "This step is to link the account which owns the stream/chatroom\n"
                                "Please ensure you're logged into the account you wish the Bot to chat in at this stage\n\n"
                                "You'll be prompted once more and given the option to copy the authorisation link\n"
                                "\n\n"
                                "This action *is* reversible, nothing is permanent, so don't stress too much :)")
            # forms a string to pass

            userInteract = UserInteractWindow(userInteractString, "Twitch Stream Authorisation", False)
            # creates a window for the user to press, passes the pre-formed string
            interactResult = userInteract.exec()
            # runs the window, captures result

            if interactResult == QDialog.DialogCode.Accepted:
            # if the user pressed continue
                streamID = await authoriseTwitch(tdb, streamScopes, "Stream")
                # calls the auth twitch function to get the ID of the stream account
            else:
            # user closed or pressed cancel
                print(f"Cancelling authentication...\nPlease restart SBO to retry authorisation", flush=True)
                # user inform
                await asyncio.sleep(5)
                # waits 5 seconds
                raise SystemExit
                # stops

        elif not useSeparateBot and (streamID is None):
        # config option is to use one account and there's no ID yet
            streamID = botID
            # sets them to match

        async with Bot(tokenDatabase = tdb, botAccID = botID, strmAccID = streamID) as bot:
        # initialises the Bot class, passes the token database and the account IDs
            await bot.login_dcf(load_token=True)
            # initialises the DCF cycle
            await bot.start_dcf()
            # starts DCF -> the bot



### Initial Twitch Auth ###

async def authoriseTwitch(tdb: asqlite.Pool, scopes: twitchio.Scopes, status:str) -> str:
    """Function to initially authorise a Twitch account with SBO's devAPI"""

    oauth = OAuthClient(tokenDatabase=tdb, scopes=scopes)
    # instantiates the OAuthClient class (which handles first-time Twitch authorisation)

    async with oauth:
    # uses the OAuthClient class to make a Device Code Flow login
        payload = await oauth.login_dcf(
            load_token=False,
            save_token=False,
        )
        # forms a dcf login, stores it as payload (tokens don't get stored here)

        userInteractString = (f"Choose how you'd like to authenticate your {status} Twitch account\n\n"
                            f"Pressing 'Copy Link' will copy the URL to your clipboard,\nfrom there you should paste it into a browser where you are logged in to your {status} Twitch account\n\n"
                            f"Pressing 'Open Link' will open the URL in your default browser automatically,\nwhere you should be logged in to your {status} Twitch account\n\n"
                            "Either action will close this window after 5 seconds and begin the authorisation check")
        # forms a string to pass

        userInteract = UserInteractWindow(userInteractString, "Twitch Stream Authorisation", True, payload["verification_uri"])
        # creates a window for the user to press
        interactResult = userInteract.exec()
        # runs the window, captures result

        if interactResult == QDialog.DialogCode.Accepted:
        # if the user pressed continue
            pass
            # lets it continue
        else:
        # user closed or pressed cancel
            print(f"Cancelling authentication...\nPlease restart SBO to retry authorisation", flush=True)
            # user inform
            await asyncio.sleep(5)
            # waits 5 seconds
            raise SystemExit
            # stops

        reasonableInterval = max(payload.get("interval", 10), 10)
        # gets a "reasonable" number of seconds to poll Twitch status repeatedly 
        # (I ran into a slow_down error that crashed the bot, don't really want to deal with that again)

        await oauth.start_dcf(
            device_code=payload["device_code"],
            interval=reasonableInterval,
            timeout=30,
            block=False
        )
        # grabs the payload device code from the formed authentication, starts a DCF connection

        userID = oauth.user.id
        # stores the user ID of the auth user
        tokenData = oauth.tokens[userID]
        # gets the token data for the user in question

        query = """
        INSERT INTO tokens (
            user_id,
            access_token,
            refresh_token,
            status
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            access_token = excluded.access_token,
            refresh_token = excluded.refresh_token,
            status = excluded.status;
        """
        # forms a query to push the twitch account details into database
        # takes the userID of the twitch user, the tokens and the status (Bot vs Stream)
        # if there's a "conflict" (the row already exists), updates all the other details except ID

        async with tdb.acquire() as connection:
        # connects to the database (file)
            await connection.execute(query, (userID, tokenData["token"], tokenData["refresh"], status))
            # executes the query with the grabbed payload variables

    return str(userID)
    # returns the userID of the authorised user


### Setup ###

async def setupSetup() -> None:
    """Setup function"""

    try:
        await authenticateTwitchUsers()
        # runs the runner...
    except KeyboardInterrupt:
    # user quits
        print(f"Quitting SBO Twitch Bot", flush=True)
        # user inform on exit
    except Exception as err:
    # other fail 
        print(f"Ran into exception {err!r}", flush=True) 
        # user inform on exit



### STDIN Read ###

async def getSBOdata() -> dict:
    """Function to read the SBO data from STDIN and return a modified dictionary"""
    global sbo, playbackControl, overlayControl
    # global -> local

    if not sys.stdin:
    # if there's no stdinput (debugging use)
        return
        # stops

    while True:
    # keeps running on a loop
        try:
            line = await asyncio.to_thread(sys.stdin.readline)
            # waits for new data from SBO

        except OSError as gErr:
        # OS-level program stop 'error' (expected)
            print("SBO -> Bot connection terminated", flush=True)
            # prints error
            return
            # stops

        if not line:
        # if there's nothing (SBO closed)
            print("SBO -> Bot connection terminated", flush=True)
            # user inform
            return
            # end-of-file
        try:
            dataDict = json.loads(line)
            # turns into dict form

        except json.JSONDecodeError as e:
        # if the received data isn't valid JSON
            print(f"Invalid JSON from SBO: {line!r} ({e})", flush=True)
            # debug -> shows the invalid data
            continue
            # waits for the next message

        if dataDict.get("Playback Control") is not None:
        # if the dictionary is for playback control enable/disable
            state = bool(dataDict["Playback Control"])
            # gets the state (True/False for Enable/Disable)
            playbackControl = state
            # sets the playback control mode to match
            if state is True:
            # enabled
                print(f"Enabled playback controls!", flush=True)
                # user inform
            else:
            # disabled
                print(f"Disabled playback controls", flush=True)
                # user inform

        elif dataDict.get("Overlay Control") is not None:
        # if the dictionary is for overlay control enable/disable
            state = bool(dataDict["Overlay Control"])
            # gets the state
            overlayControl = state
            # sets the overlay control mode to match
            if state is True:
            # enabled
                print(f"Enabled overlay controls!", flush=True)
                # user inform
            else:
            # disabled
                print(f"Disabled overlay controls", flush=True)
                # user inform

        elif dataDict.get("Config Reload") is not None:
        # if the dictionary is for command config reload
            commandConfigLoader()
            # runs the loader to get an up-to-date command configuration
            print("Reloaded Twitch command configuration", flush=True)
            # user inform

        else:
        # not any of the above dictionaries, must be an SBO song dictionary
            sbo = dataDict
            # sets the SBO dictionary to match



### Startup ###

async def main():
    """Main startup function"""
    await asyncio.gather(getSBOdata(), setupSetup())
    # starts both async functions

if __name__ == "__main__":
# startup
    botApp = QApplication(sys.argv)
    # starts a QApplication (needed to run PyQt windows)
    asyncio.run(main())
    # runs the main function