# Spotify Browser Overlay  - SBO

### SBO is a Python program that takes your current Spotify playback and dynamically creates an HTML page, locally

#### *Customised appearance with different colored element*s </br>
![Main Demo](https://i.imgur.com/KDsuOwK.png) </br>

#### *Twitch Chat commands for color changes, including a gradient effect*
![Border Demo](https://i.imgur.com/idzqGT9.gif) </br>

#### The HTML can be used to display a custom playback window in a browser or added to OBS/other services as a browser capture to display in recordings/streams

#### There's tons of configuration in the included config.ini file, and full access to the HTML file for even more control

</br>

#### SBO also includes an *optional* Twitch Bot addition, which can be used to add a Twitch Bot, which can then respond to requests about the currently playing Spotify state via chat commands (!playlist, !album, !song/!track)

</br>

#### The bot features playback control directly from Twitch chat (!pause, !skip, !queue...) </br>
###### Playback control requires the stream to be live, so no unwanted playback changes occur while the stream is offline

</br>

#### The authorised user level can be tweaked per-command via the config
##### The levels can be set to; chatter, subscriber, VIP/Artist, mod, lead mod or streamer </br>
##### The cooldown for each command can also be set on a per-user and per-channel level (streamer bypasses all cooldowns)

</br>

> #### The installation guide is found at https://elleffnotelf.com/guides/sbo </br>
> #### The bot's installation guide is found at https://elleffnotelf.com/guides/sbo-bot </br>
> #### The bot's command info is found at https://elleffnotelf.com/guides/sbo-commands </br>

</br>

### **Requires a Spotify Premium account, which is used to create a Spotify developer app, in order to fetch/control playback** </br>
#### *Local songs cannot be accessed via Spotify API, will result in preset text both in-overlay and for command returns*
#### *Private playlists are not supported, will return a default string when using !playlist*

</br>

*Default appearance at localhost website: (white background is browser rendering, not included in capture)* </br>
![Imgur Image](https://i.imgur.com/6aGvPmw.png)

*Default appearance in OBS: (background is VSCode, not in the overlay itself)* </br>
![Imgur Image](https://i.imgur.com/eG1Pb2N.png)
