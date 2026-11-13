# SpanPaper

Daily wallpaper for a dual-monitor Windows desktop: one image spanned across both screens.

*SpanPaper by EAGER - Softech. An engineering by Er. K.K.*

## Setup
1. Double-click `install.bat` - installs Pillow and pystray, then tests which image sources your network can reach.
2. Double-click `run.bat` - a tray icon (two small screens) appears and today's wallpaper is set.
3. Right-click the tray icon > **Start with Windows** to run it at every logon.

## Use
- **Next image**: left-click the tray icon, or press **Ctrl+Alt+N**.
- **Source**: right-click > Source. *Auto* tries Wallhaven, then Wikimedia Commons, then Bing.
- **Keywords**: right-click > Edit settings, change `"keywords"` in `config.json`, save. One keyword is
  picked at random per image. Applies to Wallhaven and Wikimedia (Bing and NASA have no search).
- A new image is set once per day (checked at start and every 5 minutes; retries when offline).

## Settings (`config.json`)
| Key | Meaning |
|---|---|
| `source` | `auto`, `wallhaven`, `wikimedia`, `bing`, `apod` |
| `keywords` | list of topics, e.g. `["mountains", "space"]` |
| `hotkey` | e.g. `ctrl+alt+n`; `""` disables (restart the app after changing) |
| `canvas` | `null` = detect combined desktop size; or force e.g. `[3840, 1080]` |
| `vertical_anchor` | which part to keep when cropping tall images: 0 = top, 0.5 = middle, 1 = bottom |
| `bing_market` | Bing region, e.g. `en-IN` |
| `wallhaven_api_key` | optional |
| `nasa_api_key` | `DEMO_KEY` works; a free key from api.nasa.gov lifts its rate limit |

## Troubleshooting
- `python spanpaper.py --test` shows which sources work; `data\spanpaper.log` has details.
- `python spanpaper.py --once` sets a wallpaper without the tray app.

(c) EAGER - Softech. An engineering by Er. K.K.
