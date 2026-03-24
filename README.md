# Spotify Browser Overlay  - SBO

### SBO is a Python program that takes your current Spotify playback and dynamically creates an HTML page, locally
> #### *As of v0.3.24.1012, the program can be set up to run on a separate device and accessed over a local network connection*

<br>

*Customised appearance with different colored elements*

![Main Demo](https://i.imgur.com/AhKIc3f.png)

<br>

#### The HTML can be used to display a custom playback window in a browser or added to OBS/other services as a browser capture to display in recordings/streams

#### There's tons of configuration in the included config.ini file, and full access to the HTML file for even more control!

<br>

#### SBO also includes an *optional* Twitch Bot program, which is feature-built to be extremely chat-interactive!


#### The bot allows for playback control directly from Twitch chat 
>##### !pause, !resume, !skip, !queue...

#### Chat can also change the colors of elements of the overlay via the bot's commands!

>###### *Currently supported elements; the overlay border, the song field, the artist and album fields (one command) and the progress bar*

>#### *There's a custom color manager built-in, so you can add whatever colors you'd like as text input, rather than having to type hex codes every time!*

>###### *(ex. "!customColor set cottonCandy #00eeff" will now allow "cottonCandy" to be used as a "color" as a parameter in any color command)*

*All commands require the stream to be live, so no unwanted visual or playback-related changes occur while the stream is offline*


*Each command's user level and cooldown can be tweaked individually for maximum control*
>##### *The levels can be set to; chatter, subscriber, VIP/Artist, mod, lead mod and streamer*
>##### *The cooldown for each command can also be set on a per-user and per-channel level, and is internally managed by the program (the streamer bypasses all cooldowns)*

<br>

## Guides
> #### The installation guide is found at https://elleffnotelf.com/guides/sbo 
> #### The bot's installation guide is found at https://elleffnotelf.com/guides/sbo-bot 
> #### The bot's command info is found at https://elleffnotelf.com/guides/sbo-commands

<br>

## Spotify
### **Requires a Spotify Premium account, which is used to create a Spotify developer app, in order to fetch/control playback**
>#### *Local songs cannot be accessed via Spotify API, will result in preset text both in-overlay and for command returns*
>#### *Private playlists are not supported, will return a default string when using !playlist*

<br>

## Preview

*Default appearance at localhost website: (white background is browser rendering, not included in capture)* 

![Imgur Image](https://i.imgur.com/C1Vr0WS.png)

*Default appearance, but with a green border* 

![Imgur Image](https://i.imgur.com/SvMiDyR.png)

*Twitch Chat commands for color changes, including a gradient effect*
> ###### Requires Twitch bot to be configured and for the stream to be live *(or the live checking to be disabled via config)*

![Border Demo](https://i.imgur.com/idzqGT9.gif)
*https://i.imgur.com/idzqGT9.gif (color change link, if GIF is not showing up)*
> ##### The color changing function is the same, but the appearance is a little different in newer versions *(the borders are always rounded by default as of v0.3.24.1012)*