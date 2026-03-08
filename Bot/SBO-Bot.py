import configparser, os, sys, time
# Required for basic function and getting the config options for bot
import asyncio, asqlite
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



### Setup Section ###



SBO_Bot_ver = "v0.3.08.0800"
"""The SBO Bot version (y.m.dd.hhmm)"""


LOGGER: logging.Logger = logging.getLogger("Bot")

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


ttv_Client_ID = Config.get("Twitch-Bot", "twitch_Client_ID")
"""The Twitch Client ID from config"""
ttv_Client_Secret = Config.get("Twitch-Bot", "twitch_Client_Secret")
"""The Twitch Client Secret from config"""

ttvName = Config.get("Twitch-Bot", "twitch_Username")
"""The name of the channel whose chat the bot connects to"""
botName = Config.get("Twitch-Bot", "bot_Name")
"""The name of the bot inside the chat"""

missingIDs = False
"""A boolean to check if both the IDs exist"""
try:
    # tries to find the twitch ID from config
    channelID = Config.get("Twitch-Bot", "twitch_ID")
    """The ID of the channel whose chat the bot connects to"""
except:
    # if the ID is missing, sets the flag to true
    missingIDs = True

try:
    # tries to find the bot ID from config
    botID = Config.get("Twitch-Bot", "bot_ID")
    """The ID of the bot inside the chat"""
except:
    # if the ID is missing, sets the flag to true
    missingIDs = True

botOauth = Config.get("Twitch-Bot", "bot_oauth_Token")
"""The bot channel's generated OAUTH token"""
botRefresh = Config.get("Twitch-Bot", "refreshtoken")
"""The bot channel's generated refresh token"""
botClientID = Config.get("Twitch-Bot", "bot_Client_ID")
"""The bot's Client ID"""



async def IDgrabber() -> None:
    """The function to get the channel and bot IDs"""
    async with twitchio.Client(client_id=ttv_Client_ID, client_secret=ttv_Client_Secret) as client:
        # connects to twitch api with the set ID/secret
        await client.login()
        # waits for the client to connect
        toPrint = await client.fetch_users(logins=[ttvName, botName])
        for both in toPrint:
            print(f"The ID for {both.user} is {both.id}")
        print(f"Please enter these IDs in the config.ini file in their respective fields")
        time.sleep(10)
        input(f"Press enter to exit the program")
        raise SystemExit
        


class Bot(commands.AutoBot):
    def __init__(self, *, token_database: asqlite.Pool, subs: list[eventsub.SubscriptionPayload]) -> None:
        self.token_database = token_database

        super().__init__(
            client_id=ttv_Client_ID,
            client_secret=ttv_Client_Secret,
            bot_id=botID,
            owner_id=channelID,
            prefix="!",
            subscriptions=subs,
            force_subscribe=True,
        )

    async def setup_hook(self) -> None:
        # Add our component which contains our commands...
        await self.add_component(MyComponent(self))

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload) -> None:
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id:
            return

        if payload.user_id == self.bot_id:
            # We usually don't want subscribe to events on the bots channel...
            return

        # A list of subscriptions we would like to make to the newly authorized channel...
        subs: list[eventsub.SubscriptionPayload] = [
            eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id),
        ]

        resp: twitchio.MultiSubscribePayload = await self.multi_subscribe(subs)
        if resp.errors:
            LOGGER.warning("Failed to subscribe to: %r, for user: %s", resp.errors, payload.user_id)

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
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

        LOGGER.info("Added token to the database for user: %s", resp.user_id)
        return resp

    async def event_ready(self) -> None:
        LOGGER.info("Successfully logged in as: %s", self.bot_id)


class MyComponent(commands.Component):
    # An example of a Component with some simple commands and listeners
    # You can use Components within modules for a more organized codebase and hot-reloading.

    def __init__(self, bot: Bot) -> None:
        # Passing args is not required...
        # We pass bot here as an example...
        self.bot = bot

    # An example of listening to an event
    # We use a listener in our Component to display the messages received.
    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage) -> None:
        print(f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}")

    @commands.command()
    async def hi(self, ctx: commands.Context) -> None:
        """Command that replies to the invoker with Hi <name>!

        !hi
        """
        await ctx.reply(f"Hi {ctx.chatter}!")

    @commands.command()
    async def say(self, ctx: commands.Context, *, message: str) -> None:
        """Command which repeats what the invoker sends.

        !say <message>
        """
        await ctx.send(message)

    @commands.command(aliases=["thanks", "thank"])
    async def give(self, ctx: commands.Context, user: twitchio.User, amount: int, *, message: str | None = None) -> None:
        """A more advanced example of a command which has makes use of the powerful argument parsing, argument converters and
        aliases.

        The first argument will be attempted to be converted to a User.
        The second argument will be converted to an integer if possible.
        The third argument is optional and will consume the reast of the message.

        !give <@user|user_name> <number> [message]
        !thank <@user|user_name> <number> [message]
        !thanks <@user|user_name> <number> [message]
        """
        msg = f"with message: {message}" if message else ""
        await ctx.send(f"{ctx.chatter.mention} gave {amount} thanks to {user.mention} {msg}")

    @commands.group(invoke_fallback=True)
    async def socials(self, ctx: commands.Context) -> None:
        """Group command for our social links.

        !socials
        """
        await ctx.send("discord.gg/..., youtube.com/..., twitch.tv/...")

    @socials.command(name="discord")
    async def socials_discord(self, ctx: commands.Context) -> None:
        """Sub command of socials that sends only our discord invite.

        !socials discord
        """
        await ctx.send("discord.gg/...")


async def setup_database(db: asqlite.Pool) -> tuple[list[tuple[str, str]], list[eventsub.SubscriptionPayload]]:
    # Create our token table, if it doesn't exist..
    # You should add the created files to .gitignore or potentially store them somewhere safer
    # This is just for example purposes...

    query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
    async with db.acquire() as connection:
        await connection.execute(query)

        # Fetch any existing tokens...
        rows: list[sqlite3.Row] = await connection.fetchall("""SELECT * from tokens""")

        tokens: list[tuple[str, str]] = []
        subs: list[eventsub.SubscriptionPayload] = []

        for row in rows:
            tokens.append((row["token"], row["refresh"]))

            if row["user_id"] == botID:
                continue

            subs.extend([eventsub.ChatMessageSubscription(broadcaster_user_id=row["user_id"], user_id=botID)])

    return tokens, subs


# Our main entry point for our Bot
# Best to setup_logging here, before anything starts
def main() -> None:
    twitchio.utils.setup_logging(level=logging.INFO)

    async def runner() -> None:
        async with asqlite.create_pool("tokens.db") as tdb:
            tokens, subs = await setup_database(tdb)

            async with Bot(token_database=tdb, subs=subs) as bot:
                for pair in tokens:
                    await bot.add_token(*pair)

                await bot.start(load_tokens=False)

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt")

if missingIDs:
    # checks if both the botID and channelID exist
        print(f"BotID or ChannelID not found, grabbing")
        # user inform
        asyncio.run(IDgrabber())
        # runs the IDgrabber, which will print them


if __name__ == "__main__":
    main()






