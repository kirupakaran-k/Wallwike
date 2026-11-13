# Wallwike

**Two monitors, one wallpaper.** Windows puts the same picture on each screen. Wallwike finds a
wide photo, cuts it to fit both screens exactly and stretches it across them as a single view,
then swaps it for a new one every day. Or every 15 minutes, if you get bored easily.

*Wallwike by EAGER - Softech · An engineering by Er. K.K.*

![Before: the same picture on both monitors. With Wallwike: one wide picture across both.](docs/screenshots/span.png)

## Why you might like it

- 🖼️ **One picture across both screens.** Left half on the left monitor, right half on the right,
  lined up to the pixel. No black bars, no stretching, no picture repeated twice.
- 🌄 **Photos worth looking at.** Featured panoramas from Wikimedia Commons (mountains, lakes,
  cities, the night sky) and the Bing picture of the day.
- 🎯 **You choose the mood.** Tick *mountains*, *waterfall*, *space* or type your own word, and
  Wallwike picks from those.
- ⏱️ **As fresh as you want.** A new picture once a day, or every 12, 6, 3 or 1 hours, or every
  30 or 15 minutes.
- ⌨️ **Don't like today's?** Press **Ctrl+Alt+N** from anywhere and it's gone.
- 🔎 **"Where is that?"** *About this image* opens the photo's own page, with the place and the
  photographer.
- 🪶 **Stays out of the way.** One small icon near the clock. No window, no account, no ads,
  nothing to install.

## Download

Get **`Wallwike.exe`** from the [latest release](https://github.com/kirupakaran-k/Wallwike/releases/latest)
and run it. A tray icon (two small screens) appears near the clock and your first wallpaper
is set a few seconds later. Windows 10 or 11.

The app isn't code-signed, so the first time Windows SmartScreen may say *"Windows protected
your PC"*: click **More info → Run anyway**.

## Everything is on the right-click menu

Right-click the tray icon. That menu is the whole app.

![Wallwike's tray menu with the Settings submenu open](docs/screenshots/tray-menu.png)

| Menu item | What it does |
|---|---|
| **Next image** | A different picture, now. Same as Ctrl+Alt+N. |
| **Source** | *Auto* (Wikimedia Commons first, Bing if that fails), or just one of the two |
| **About this image** | Opens the picture's web page |
| **Settings** | Keywords, how often to change, which part of tall pictures to keep, Bing region |
| **Open log** | What Wallwike has been up to, if something looks wrong |
| **Start with Windows** | Tick it once and Wallwike is there after every restart |

Left-clicking the icon does nothing, on purpose, so a stray click never costs you a picture
you liked.

### Pick your topics

**Settings → Keywords** opens a small window that stays open while you tick. One ticked topic is
picked at random for each new picture; tick none for anything goes.

![The Keywords window: tick boxes for topics such as mountains, forest, lake and space](docs/screenshots/keywords.png)

## Good to know

- **Offline?** Wallwike keeps the picture you have and tries again every minute until it's back.
- **A site is blocked on your network?** If one source can't be reached while the other works,
  Wallwike tries it last for the next 6 hours instead of making every change wait for it.
- **Built a newer version or moved the folder?** *Start with Windows* follows the copy you ran
  last.
- **Odd screen sizes?** Wallwike asks Windows for the combined size of your desktop (3840x1080
  for two 1920x1080 screens) and makes the picture exactly that big.
- Your settings, the log and the current wallpaper live in `%APPDATA%\Wallwike`, shared by every
  version.

## For tinkerers

The menu covers the everyday settings. The rest are in `config.json` (**Settings → Open
config.json**):

| Key | Meaning |
|---|---|
| `source` | `auto`, `wikimedia` or `bing` |
| `keywords` | list of topics, e.g. `["mountains", "space"]` |
| `hotkey` | e.g. `ctrl+alt+n`; `""` turns it off (restart the app after changing) |
| `refresh_minutes` | `0` = once a day; otherwise minutes between changes |
| `canvas` | `null` = detect the combined desktop size; or force one, e.g. `[3840, 1080]` |
| `vertical_anchor` | which part to keep when cropping tall pictures: 0 = top, 0.5 = middle, 1 = bottom |
| `bing_market` | Bing region, e.g. `en-IN` |

### Run it from source

Needs Python 3.10 or newer.

1. Double-click `install.bat`. It installs Pillow and pystray, then checks which picture sources
   your network can reach.
2. Double-click `run.bat`. The tray icon appears and today's wallpaper is set.

`python wallwike.py --test` shows which sources work, and `python wallwike.py --once` sets a
wallpaper without the tray app.

### Build the exe

Double-click `build.bat`. It sets up the build tools the first time and puts `Wallwike.exe` in a
`build <version>` folder next to the `version` folders. The exe needs no Python.

| File | What it does |
|---|---|
| `wallwike.py` | The whole app: picture sources, cropping, setting the wallpaper, tray menu, hotkey |
| `version.py` | The name, version number and company (shown in the tray menu; names the build folder) |
| `build.bat` | Builds `Wallwike.exe` |
| `exe_info.py` | The exe's details: name, version, company and copyright |
| `install.bat`, `run.bat` | Run from source without building |

## Version history

Every version is kept here as its own commit and tag, from the very first build. Pick one under
[Releases](https://github.com/kirupakaran-k/Wallwike/releases) or
[Tags](https://github.com/kirupakaran-k/Wallwike/tags) to see or download exactly that version's
code. What changed each time is in [CHANGELOG.md](CHANGELOG.md). Up to 1.4 the app was called
**SpanPaper**.

| | Highlights |
|---|---|
| **1.8** | Wallhaven and NASA removed; this README |
| **1.7** | Unreachable sources no longer slow things down; Start with Windows repairs itself |
| **1.5 - 1.6** | Renamed to Wallwike; settings in AppData; one folder per version |
| **1.4** | Standalone exe, version number |
| **1.1 - 1.3** | Settings menu, Keywords window, refresh interval |
| **1.0** | First build: one wallpaper spanned across two monitors |

## Licence

Wallwike is free software under the **GNU General Public License v3.0** ([LICENSE](LICENSE)):
you may use, study, share and change it; versions you share must stay under the GPL with their
source. It uses Pillow (MIT-CMU) and pystray (LGPL-3.0), each under its own licence.

Wallpapers are downloaded from Wikimedia Commons and Bing and remain under their owners' terms.
The photo in the pictures above is
[Forum romanum 6k](https://commons.wikimedia.org/wiki/File:Forum_romanum_6k_(5760x2097).jpg)
by BeBo86, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0), via Wikimedia Commons.

© EAGER - Softech · An engineering by Er. K.K.
