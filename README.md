# TiDL : A streamrip powered Discord bot

This bot allows users of a server to share music using a premium Tidal account via streamrip.

## Installation
1. Clone the repo using `git clone https://github.com/CanadianBaconBoi/TiDL-Discord-Bot.git`
2. `cd TiDL-Discord-Bot`
3. Install the requirements using `pip install -r requirements.txt`
4. Configure `config.toml` accordingly
5. `python bot.py`
6. Login to Tidal using either the URL provided or the browser opened. Your credentials will be stored in `tidal.json` for further use.

## Usage
Command list is as follows:
- help : Lists commands and usages
- dl : Share track/album/playlist, usage: `$dl tidal.com/browse/track/101982419`

## Planned Features
- Enable/Disable certain media types (albums, playlists, tracks, etc)
- User blacklist
- Discord commands as opposed to chat commands
- Album/Track search


## Attributions
https://github.com/nathom/streamrip/ - Amazing tool used to download music from Tidal

https://github.com/parnexcodes/tidal-dl-discord-bot - Initial inspiration
