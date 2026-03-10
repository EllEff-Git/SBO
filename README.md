***SBO*** (*Spotify Browser Overlay*) is a program that takes your current Spotify playback and dynamically creates an HTML page, locally, based on your current Spotify status


![Imgur Image](https://i.imgur.com/KDsuOwK.png)

This can then be used to display a custom playback window in a browser or added to OBS/other services as a browser capture to display in recordings/streams

</br>

There's tons of configuration in the included config.ini file, and full access to the HTML file for even more control

</br>

SBO also includes an *optional* Twitch Bot method, which can be used to add a Twitch Bot, which can then respond to requests about the currently playing Spotify state via chat commands (!playlist, !album, !song/!track)

</br>

The bot also, optionally, features playback control support inside Twitch chat (!pause, !skip, !queue...) </br>
Playback control requires the stream to be live, so no unwanted playback changes occur while the stream is offline
</br>

The authorised user level can be tweaked per-command (any chatter, subscriber, VIP/Artist, mod, lead mod, streamer) via config </br>
The cooldown for each command can also be set on a per-user and per-channel level

</br>

The installation guide is found at https://elleffnotelf.com/guides/sbo </br>
The bot's installation guide is found at https://elleffnotelf.com/guides/sbo-bot </br>
The bot's command info is found at https://elleffnotelf.com/guides/sbo-commands </br>

</br>

**Requires a Spotify Premium account, which is used to create a Spotify developer app, in order to fetch/control playback** </br>
*Local songs cannot be accessed via Spotify API, will result in preset text*
</br>

</br>

Default appearance at localhost website: (white background is a browser rendering, capture does not keep that) </br>
![Imgur Image](https://i.imgur.com/6aGvPmw.png)

Default appearance in OBS: (background is VSCode, not in the overlay itself) </br>
![Imgur Image](https://i.imgur.com/eG1Pb2N.png)
