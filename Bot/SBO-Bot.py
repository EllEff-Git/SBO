import configparser, os, sys, threading
# Required for basic function and getting the config options for bot
import asyncio, asqlite, socket
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



SBO_Bot_ver = "v0.3.08.2239"
"""The SBO Bot version (y.m.dd.hhmm)"""


LOGGER: logging.Logger = logging.getLogger("Bot")
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

bot_Client_ID = Config.get("Twitch-Bot", "twitch_Client_ID")
"""The Twitch Client ID from config"""
bot_Client_Secret = Config.get("Twitch-Bot", "twitch_Client_Secret")
"""The Twitch Client Secret from config"""

ttvName = Config.get("Twitch-Bot", "twitch_Username")
"""The name of the channel whose chat the bot connects to"""
botName = "esbeohBot"
"""The name of the bot (SBO Bot)"""
botID = "1455638728"
"""The ID of the bot"""

missingID = False
"""A boolean to check if the channel ID exists"""

try:
    # tries to find the twitch ID from config
    channelID = Config.get("Twitch-Bot", "twitch_ID")
    """The ID of the channel whose chat the bot connects to"""
except:
    # if the ID is missing, sets the flag to true
    missingID = True



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
            force_subscribe = True,
        )
        # sets up the bot with the correct permissions and IDs

    async def setup_hook(self) -> None:
        # adds the component that adds commands
        await self.add_component(MyComponent(self))

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
            eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id),
        ]
        # what to "subscribe" to (listen to)
        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.error("Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id)

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

    async def event_ready(self) -> None:
        LOGGER.error(f"Successfully logged in as: esbeohBot, {self.bot_id}")



### Commands Component of Bot ###



class MyComponent(commands.Component):
    # An example of a Component with some simple commands and listeners
    # You can use Components within modules for a more organized codebase and hot-reloading.


    def __init__(self, bot: Bot) -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot

### Listener ###

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"{payload.chatter.name}: {payload.text}")

### Playlist ###

    @commands.command()
    async def playlist(self, context: commands.Context) -> None:
        """!playlist"""

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

    twitchio.utils.setup_logging(level=logging.ERROR)
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
    # checks if both the botID and channelID exist
        print(f"ChannelID not found, please enter it into the config file")
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