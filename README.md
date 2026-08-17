# Spotify Browser Overlay  - SBO

### SBO is a Python program that takes your current Spotify playback and dynamically creates an HTML page, locally
> #### *The program can be set up to run on a separate device and accessed over a local network connection (>v0.3.24.1012)*

<br>

*Customised appearance with different colored elements*

![Main Demo](https://i.imgur.com/AhKIc3f.png)

<br>

#### The HTML can be used to display a custom playback window in a browser or added to OBS/other services as a browser capture to display in recordings/streams

#### There's tons of customisation to be done in the included configurator(s), and full access to the HTML file for even more control!

<br>

## SBO Twitch Bot
### There's an *optional* Twitch Bot program, which is feature-built to be extremely chat-interactive!
>### The bot allows for playback control directly from Twitch chat via commands such as !pause, !resume, !skip, !queue...
> #### Chat can also change the colors of elements of the overlay via the bot's commands!

*There's a configuration option that requires the stream to be live for overlay/playback control, so no unwanted visual or playback-related changes occur while the stream is offline*


*Each command's user level and cooldown can be tweaked individually for maximum control*
>##### *The levels can be set to; chatter, subscriber, VIP/Artist, mod, lead mod and streamer*
>##### *The cooldown for each command can also be set on a per-user and per-channel level, and is internally managed by the program (the streamer bypasses all cooldowns)*

<br>

## Spotify
### **Requires a Spotify Premium account, which is used to create a Spotify developer app, in order to fetch/control playback**
>#### *Local songs cannot be accessed via Spotify API, will result in preset text both in-overlay and for command returns*
>#### *Private playlists are not supported when using !playlist, results in a preset text return*

 <br>

## SHAA/DSI
### **Running SBO alongside DSI will allow DSI to act as a "host", fully replacing SBO's own Spotify API request logic**
>#### *This way, you only have one source of Spotify API requests happening. Personally, this is how I intend the program(s) be used*
### **If DSI is configured to use SHAA, and you enable SHAA compatibility in SBO, you'll get an extra field in the overlay with statistics regarding the current song**

<br>

## Preview

*Default appearance at localhost website: (white background is browser rendering, not included in capture)* 

![Imgur Image](https://i.imgur.com/C1Vr0WS.png)

*Default appearance, but with a green border* 

![Imgur Image](https://i.imgur.com/SvMiDyR.png)

*Twitch Chat commands for color changes, including a gradient effect*
> ###### Requires Twitch bot to be configured and for the stream to be live *(or the live checking to be disabled via config)*

![Border Demo](https://i.imgur.com/idzqGT9.gif)
*https://i.imgur.com/idzqGT9.gif (color change demo link, if GIF is not showing up)*
> ##### The color changing function is the same, but the appearance is a little different in newer versions *(the borders are always rounded by default as of v0.3.24.1012)*