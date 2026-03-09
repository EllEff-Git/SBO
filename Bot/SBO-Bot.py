import configparser, os, sys, threading, random
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



SBO_Bot_ver = "v0.3.09.0400"
"""The SBO Bot version (y.m.dd.hhmm)"""



logFormat = "%(message)s"
# changes the format from "[systemtime] [TYPE] message" to just "message"

if not logging.getLogger("Bot").hasHandlers():
    # checks if the bot logger has handlers (well, if it doesn't)
    logging.basicConfig(level=logging.INFO, format=logFormat)
    # sets up a basic config with the logging level and format

logging.getLogger("twitchio").setLevel(logging.WARNING)
# sets TwitchIO to only print if it has a warning or higher (otherwise it spams)

logging.getLogger("twitchio.client").setLevel(logging.ERROR)
# sets the TwitchIO Client to only print on error or higher (there's a couple irrelevant warnings)

LOGGER = logging.getLogger("Bot")
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
playbackControl = Config.getboolean("Twitch-Bot", "enable_Playback_Control")
"""Whether to enable Twitch chat playback control (boolean)"""
allowSubControl = Config.getboolean("Twitch-Bot", "allow_Subscriber_Control")
"""Whether to allow subscribers to control playback (boolean)"""

bot_Client_ID = Config.get("Twitch-Bot", "dev_Client_ID")
"""The Twitch Client ID from config"""
bot_Client_Secret = Config.get("Twitch-Bot", "dev_Client_Secret")
"""The Twitch Client Secret from config"""

ttvName = Config.get("Twitch-Bot", "twitch_Username")
"""The name of the channel whose chat the bot connects to"""
botName = Config.get("Twitch-Bot", "bot_Name")
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
    # if one of the IDs is missing, sets the flag to true
    missingID = True
    # this will trip the check at the bottom and stop the program



### Playback Control ###



if playbackControl:
    # if the Twitch chat playback control is enabled
    webClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    webClient.connect(("localhost", 6666))
    # creates a socket connection on localhost

def dataPasser(command: str, uri: str):
    """A function to send commands to SBO (takes the command and spotify URI/URL as parameters)"""
    while True:
        # while the program is running
        if not playbackControl:
            # if playback is disabled
            return "Playback control disabled"
            # sends the response back to the bot so it can reply

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
            print("DEBUG: unknown format for web socket")
            return "Error with command"



### Text File -> Dictionary ###



def getData():
    """Function to get the current playlist/track/whatever else"""

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
    """Function to check if the calling chatter is authorised"""
    def chatterChecker(ctx):
        """Helper function"""
        chatter = ctx.author
        # assigns the author as a chatter
        if allowSubControl and chatter.subscriber:
            # if subscribers are allowed to use 
            return True
        elif chatter.vip or chatter.admin or chatter.broadcaster or chatter.lead_moderator or chatter.moderator:
            # checks if the chatter's roles fits any of these
            return True
            # if yes, returns true
        else:
            return False
            # if not, returns false
    return chatterChecker
        


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
                    # if data key doesn't exist or is empty
                    return False
                    # returns false, which keeps the boolean for live false

### Check Status of Live Check ###

    async def checkLiveCheck(self):
        # runs liveCheck every minute to see if the channel has started stream
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
                    if not logged:
                        # if the live status hasn't already been logged once
                        LOGGER.info(f"{ttvName} is now live!")
                        # prints a live message
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
        LOGGER.info(f"Successfully logged in as {self.botName}")
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
    @commands.cooldown(rate = 1, per=30, key=commands.BucketType.channel)
    async def playlist(self, context: commands.Context) -> None:
        """!playlist"""

        if self.bot.channelLive:
        # checks if the channel is live first
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

### Song ###

    @commands.command(aliases=["song"])
    @commands.cooldown(rate = 1, per=15, key=commands.BucketType.channel)
    async def track(self, context: commands.Context) -> None:
        """!track and !song"""

        if self.bot.channelLive:
        # checks if the channel is live first
            sbo = getData()
            # calls the data grabber to get the package (dictionary)
            track = sbo.get("Song Name")
            # gets the track from the dictionary
            artist = sbo.get("Artist Name")
            # gets the artist name from the dictionary
            trackURL = sbo.get("Spotify URL")
            # gets the track URL from the dictionary
            
            if trackURL == "A local song":
                # if the song is local (SBO sets it to this if a local song is detected)
                await context.reply(f"{ttvName} is listening to a locally stored song")
                # sends a local song message
            else:
                # if the song return is anything else
                await context.reply(f"Current song: {track} by {artist}. {trackURL}")
                # sends a message with the song URL

### Skip ###

    @commands.command()
    @commands.cooldown(rate = 1, per=10, key=commands.BucketType.channel)
    async def skip(self, context: commands.Context) -> None:
        """!skip"""

        if self.bot.channelLive:
        # checks if the channel is live first
            if isCoolChatter()(context):
                # checks if the permissions are met
                dataPasser("skip", "")
                # calls the dataPasser function
                await context.reply("Skipped")
            
            else:
                print("No permission")

### Pause ###

    @commands.command()
    @commands.cooldown(rate = 1, per=10, key=commands.BucketType.channel)
    async def pause(self, context: commands.Context) -> None:
        """!pause"""

        if self.bot.channelLive:
        # checks if the channel is live first
            if isCoolChatter()(context):
                dataPasser("pause", "")
                # calls the dataPasser function

                await context.reply(f"Paused")
                # replies to user

### Resume ###

    @commands.command()
    @commands.cooldown(rate = 1, per=10, key=commands.BucketType.channel)
    async def resume(self, context: commands.Context) -> None:
        """!resume"""

        if self.bot.channelLive:
        # checks if the channel is live first
            if isCoolChatter()(context):
                # checks if the permissions are met
                dataPasser("resume", "")
                # calls the dataPasser function

                await context.reply(f"Resumed")
                # replies to user

### Previous ###

    @commands.command()
    @commands.cooldown(rate = 1, per=10, key=commands.BucketType.channel)
    async def previous(self, context: commands.Context) -> None:
        """!previous"""

        if self.bot.channelLive:
        # checks if the channel is live first
            if isCoolChatter()(context):
                # checks if the permissions are met
                dataPasser("previous", "")
                # calls the dataPasser function

                await context.reply(f"Went back")
                # replies to user

### Queue ###

    @commands.command()
    @commands.cooldown(rate = 1, per=15, key=commands.BucketType.channel)
    async def queue(self, context: commands.Context) -> None:
        """!queue"""

        if self.bot.channelLive:
        # checks if the channel is live first
            if isCoolChatter()(context):
                # checks if the permissions are met
                fullMsg = context.content
                # gets the full message from the contents
                try:
                    cmd, songLink = fullMsg.split(" ", 1)
                    # splits the command, stores the link for the song as songLink

                    dataPasser("queue", songLink)
                    # calls the dataPasser function with the link

                    await context.reply(f"Queued song")
                    # replies to user

                except:
                    # if the command was entered incorrectly
                    await context.reply(f"Add a valid Spotify link after !queue, please")
                    # replies to user 


### SBO ###

    @commands.command(aliases=["SBO"])
    @commands.cooldown(rate = 1, per=60, key=commands.BucketType.channel)
    async def sbo(self, context: commands.Context) -> None:
        """!sbo / !SBO"""

        await context.reply(f"The SBO Bot (esbeohBot) is a Twitch bot made by LP, currently on {SBO_Bot_ver}")
        # replies with the SBO details

### Unfound Command ###

    @commands.Component.listener()
    async def unfound(self, context: commands.Context, error: Exception) -> None:
        """Handles commands that don't exist (if the message has the right prefix, wrong cmd)"""
        if isinstance(error, commands.CommandNotFound):
            # if the command returns a "command not found"
            return
            # doesn't return anything
        LOGGER.error(f"Error handling {context.command}: {error}")
        # if it's something else

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
        LOGGER.warning("Shutting down due to KeyboardInterrupt")



### Startup ###



if missingID:
    # checks if the channelID exists (required for connection)
        print(f"ChannelID not found, please enter it into the config file")
        # user inform
        input("Press enter to exit")
        raise SystemExit

if not ttvName:
    # checks if the channel name exists (required for conduit/connection)
        print(f"Channel name not found, please enter it into the config file")
        # user inform
        input("Press enter to exit")
        raise SystemExit

if playbackControl:
    # if the Twitch chat playback is enabled
    dataPassThread = threading.Thread(target = lambda: dataPasser("start", "uri"))
    # creates a thread for websocket connection
    dataPassThread.start()
    # starts the websocket thread


if __name__ == "__main__":
    logWriter()
    # starts the console writer