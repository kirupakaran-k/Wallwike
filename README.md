# Wallwike

Daily wallpaper for a dual-monitor Windows desktop: one image spanned across both screens.

*Wallwike by EAGER - Softech. An engineering by Er. K.K.*

## Download
Get **`Wallwike.exe`** from the [latest release](https://github.com/kirupakaran-k/Wallwike/releases/latest)
and run it. Nothing to install. Windows 10 or 11. A tray icon (two small screens) appears and
today's wallpaper is set.

The app isn't code-signed, so the first time Windows SmartScreen may say *"Windows protected
your PC"*: click **More info > Run anyway**.

## Or run it from source (needs Python)
1. Double-click `install.bat` - installs Pillow and pystray, then tests which image sources your network can reach.
2. Double-click `run.bat` - a tray icon (two small screens) appears and today's wallpaper is set.
3. Right-click the tray icon > **Start with Windows** to run it at every logon. It always starts
   the copy you ran last, so it keeps working after you build a newer version or move the folder.

## Use
- **Next image**: right-click > Next image, or press **Ctrl+Alt+N**. Left-click does nothing.
- **Source**: right-click > Source. *Auto* tries Wallhaven, then Wikimedia Commons, then Bing.
  A source your network can't reach is tried last for the next 6 hours, so it doesn't slow every
  change down; picking a source in the menu tries it again straight away.
- **Settings**: right-click > Settings. Tick keywords (one ticked keyword is picked at random per
  image; applies to Wallhaven and Wikimedia), add a custom one, set crop position and Bing region.
  Changes apply from the next image.
- A new image is set once per day (checked at start and every 5 minutes; retries when offline).

## Settings (`config.json`)
| Key | Meaning |
|---|---|
| `source` | `auto`, `wallhaven`, `wikimedia`, `bing`, `apod` |
| `keywords` | list of topics, e.g. `["mountains", "space"]` |
| `hotkey` | e.g. `ctrl+alt+n`; `""` disables (restart the app after changing) |
| `refresh_minutes` | `0` = once a day; otherwise minutes between changes (also in Settings > Refresh interval) |
| `canvas` | `null` = detect combined desktop size; or force e.g. `[3840, 1080]` |
| `vertical_anchor` | which part to keep when cropping tall images: 0 = top, 0.5 = middle, 1 = bottom |
| `bing_market` | Bing region, e.g. `en-IN` |
| `wallhaven_api_key` | optional |
| `nasa_api_key` | `DEMO_KEY` works; a free key from api.nasa.gov lifts its rate limit |

## Troubleshooting
- `python wallwike.py --test` shows which sources work; `%APPDATA%\Wallwike\data\wallwike.log` has details.
- `python wallwike.py --once` sets a wallpaper without the tray app.

## Build the exe
Install Python 3.10 or newer, then double-click `build.bat`. It sets up the build tools the first
time and puts `Wallwike.exe` in a `build <version>` folder next to the `version` folders. The exe
needs no Python.

## Where things are kept
- Settings, the log and the current wallpaper: `%APPDATA%\Wallwike` (shared by every version).
- Each version's source is kept in its own folder, `version 1\1.0 - First build`, `version 1\1.1 - Settings submenu` and so on, with
  `What changed in each version.txt` beside them.

## Files
| File | What it does |
|---|---|
| `wallwike.py` | The whole app: image sources, cropping, setting the wallpaper, tray menu, hotkey |
| `version.py` | The name, version number and company (shown in the tray menu; names the build folder) |
| `build.bat` | Builds `Wallwike.exe` |
| `exe_info.py` | The exe's details: name, version, company and copyright |
| `install.bat`, `run.bat` | Run from source without building: install libraries, then start the tray app |

## Licence
GPL-3.0. Bundled libraries: Pillow (MIT-CMU), pystray (LGPL-3.0).
Wallpapers are downloaded from third-party sites and remain under their owners' terms.

(c) EAGER - Softech. An engineering by Er. K.K.
