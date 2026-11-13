# Changelog

## 1.5: Renamed to Wallwike - 2026-11-13
The app is now called Wallwike (it was briefly Wallsynk on the way): script, icon, exe, tray menu, Keywords window and log. A Start with Windows entry made under either old name is moved over the first time Wallwike starts.

## 1.4: Standalone exe, version number - 2026-11-13
build.bat builds a single SpanPaper.exe with PyInstaller that needs no Python and sits in the tray like the script did; it keeps its settings beside itself (or in AppData if that folder can't be written to). The Keywords window and Start with Windows now work from the exe. New icon file, and a version number in version.py that is shown at the bottom of the tray menu and names the 'build <version>' folder.

## 1.3: Left-click does nothing, refresh interval - 2026-11-13
Left-clicking the tray icon no longer changes the wallpaper; Next image is on the right-click menu and Ctrl+Alt+N only. Settings has a new Refresh interval: once a day (as before), every 12, 6, 3 or 1 hours, or every 30 or 15 minutes. The interval counts from the last change, so Next image restarts it, and a new choice takes effect within a minute.

## 1.2: Keywords window that stays open - 2026-11-13
Windows closes a tray menu after every click, so ticking several keywords meant opening the menu again each time. Keywords now opens a small window of tick boxes that stays open until you close it, with a box to type your own keyword; each tick is saved straight away. Crop position and Bing region stay as submenus.

## 1.1: Settings submenu - 2026-11-13
Edit settings is replaced by a Settings submenu in the tray menu: Keywords (a tick list of twelve topics, Add custom keyword, Clear all), Crop position for tall pictures (Top to Bottom) and Bing region, with Open config.json kept for the rest. One ticked keyword is picked at random per picture.

## 1.0: First build - 2026-11-13
The first version, called SpanPaper. A tray app that sets one daily wallpaper stretched across both monitors as a single picture, instead of the same picture twice. It reads the combined desktop size from Windows (3840x1080 for two 1920x1080 screens), crops and resizes the picture to exactly that, and sets it with the Windows 'Span' style. Pictures come from Wallhaven (32:9 wallpapers), Wikimedia Commons (featured panoramas), the Bing image of the day or NASA's Astronomy Picture of the Day; Auto tries Wallhaven, then Wikimedia, then Bing, and pictures that are too small are skipped. Tray menu: Next image (also left-click, and Ctrl+Alt+N from anywhere), Source, About this image, Edit settings (opens config.json in Notepad, where the keywords are), Open log, Start with Windows and Quit. A new picture once a day. Run with install.bat then run.bat; needs Python. Settings and the log are kept beside the script.
