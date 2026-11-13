"""SpanPaper - daily wallpaper spanned as ONE image across a dual-monitor desktop (Windows).

Run modes:
    pythonw spanpaper.py          tray app (normal use)
    python  spanpaper.py --once   change the wallpaper now and exit
    python  spanpaper.py --test   check which image sources are reachable (changes nothing)
"""
import ctypes
import datetime
import glob
import io
import json
import logging
import os
import random
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser

from PIL import Image

APP = "SpanPaper"
COMPANY = "EAGER - Softech"
CREDIT = "An engineering by Er. K.K."
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CONFIG_PATH = os.path.join(HERE, "config.json")
STATE_PATH = os.path.join(DATA, "state.json")
LOG_PATH = os.path.join(DATA, "spanpaper.log")
IS_WIN = sys.platform == "win32"
UA = "SpanPaper/1.0 (personal daily wallpaper script; Python urllib)"
SOURCES = ["auto", "wallhaven", "wikimedia", "bing", "apod"]
SOURCE_LABELS = {
    "auto": "Auto (Wallhaven > Wikimedia > Bing)",
    "wallhaven": "Wallhaven (32:9 wallpapers)",
    "wikimedia": "Wikimedia Commons (featured panoramas)",
    "bing": "Bing image of the day",
    "apod": "NASA Astronomy Picture of the Day",
}
DEFAULT_CONFIG = {
    "source": "auto",
    "keywords": ["mountains", "landscape", "forest", "coast"],
    "hotkey": "ctrl+alt+n",
    "canvas": None,
    "vertical_anchor": 0.5,
    "bing_market": "en-IN",
    "wallhaven_api_key": "",
    "wallhaven_categories": "100",
    "nasa_api_key": "DEMO_KEY",
}
Image.MAX_IMAGE_PIXELS = 400_000_000

os.makedirs(DATA, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()]
    if sys.stderr else [logging.FileHandler(LOG_PATH, encoding="utf-8")],
)
log = logging.getLogger(APP)
_lock = threading.Lock()


# ---------------------------------------------------------------- config / state
def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return dict(default)
    except Exception as e:  # broken JSON: keep running on defaults
        log.warning("Could not read %s (%s); using defaults", path, e)
        return dict(default)


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(load_json(CONFIG_PATH, {}))
    if cfg.get("source") not in SOURCES:
        cfg["source"] = "auto"
    return cfg


def save_config_value(key, value):
    cfg = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    cfg[key] = value
    save_json(CONFIG_PATH, cfg)


def load_state():
    st = {"last_date": "", "history": [], "current": {}}
    st.update(load_json(STATE_PATH, {}))
    return st


def pick_keyword(cfg):
    kw = cfg.get("keywords") or ""
    if isinstance(kw, list):
        kw = random.choice(kw) if kw else ""
    return str(kw).strip()


# ---------------------------------------------------------------- http
def http_get(url, params=None, timeout=30):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def http_json(url, params=None, timeout=30):
    return json.loads(http_get(url, params, timeout).decode("utf-8"))


# ---------------------------------------------------------------- sources
# Each returns {"id", "url", "title", "page", "source"} or raises.
def fetch_wallhaven(cfg, seen, fresh):
    kw = pick_keyword(cfg)
    tiers = [("32x9", "3840x1080"), ("21x9", "3440x1440"), ("16x9", "3840x2160")]
    for ratio, atleast in tiers:
        params = {"ratios": ratio, "atleast": atleast, "purity": "100",
                  "categories": cfg.get("wallhaven_categories", "100"), "sorting": "random"}
        if kw:
            params["q"] = kw
        if cfg.get("wallhaven_api_key"):
            params["apikey"] = cfg["wallhaven_api_key"]
        items = http_json("https://wallhaven.cc/api/v1/search", params, timeout=12).get("data", [])
        for it in items:
            if "wallhaven:" + it["id"] not in seen:
                return {"id": "wallhaven:" + it["id"], "url": it["path"], "page": it.get("url", ""),
                        "title": "Wallhaven %s (%s, %s)" % (it["id"], it.get("resolution", "?"), kw or "any"),
                        "source": "wallhaven"}
    raise RuntimeError("Wallhaven: no unseen result for keyword %r" % kw)


def fetch_wikimedia(cfg, seen, fresh):
    kw = pick_keyword(cfg)
    base = "%s panorama filetype:bitmap filew:>3839 fileh:>1079" % kw
    for extra in (' incategory:"Featured pictures on Wikimedia Commons"', ""):
        d = http_json("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
            "gsrlimit": "50", "gsrsort": "random", "gsrsearch": base + extra,
            "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "3840"})
        pages = list(d.get("query", {}).get("pages", {}).values())
        random.shuffle(pages)
        for p in pages:
            ii = (p.get("imageinfo") or [{}])[0]
            w, h = ii.get("width", 0), ii.get("height", 1)
            # 2.2..3.55 wide: the 3840px rendition is then at least 1080px tall
            if not 2.2 <= w / h <= 3.55 or "thumburl" not in ii:
                continue
            pid = "wikimedia:%s" % p["pageid"]
            if pid in seen:
                continue
            title = p["title"].replace("File:", "").rsplit(".", 1)[0]
            return {"id": pid, "url": ii["thumburl"], "page": ii.get("descriptionurl", ""),
                    "title": "%s (Wikimedia Commons)" % title, "source": "wikimedia"}
    raise RuntimeError("Wikimedia: no unseen wide image for keyword %r" % kw)


def fetch_bing(cfg, seen, fresh):
    idxs = list(range(1, 8)) if fresh else [0]
    random.shuffle(idxs)
    last = None
    for idx in idxs + ([0] if fresh else []):
        d = http_json("https://www.bing.com/HPImageArchive.aspx",
                      {"format": "js", "idx": idx, "n": 1, "mkt": cfg.get("bing_market", "en-IN")})
        im = d["images"][0]
        last = {"id": "bing:" + im["urlbase"], "url": "https://www.bing.com" + im["urlbase"] + "_UHD.jpg",
                "page": im.get("copyrightlink", ""), "title": im.get("copyright", "Bing image"),
                "source": "bing"}
        if last["id"] not in seen:
            return last
    return last  # only 8 days of Bing images exist; reuse one rather than fail


def fetch_apod(cfg, seen, fresh):
    params = {"api_key": cfg.get("nasa_api_key") or "DEMO_KEY"}
    if fresh:
        params["count"] = 5
    d = http_json("https://api.nasa.gov/planetary/apod", params)
    for it in (d if isinstance(d, list) else [d]):
        if it.get("media_type") != "image":
            continue
        pid = "apod:" + it.get("date", "")
        if pid in seen and fresh:
            continue
        return {"id": pid, "url": it.get("hdurl") or it["url"], "page": "https://apod.nasa.gov/apod/",
                "title": "%s (NASA APOD %s)" % (it.get("title", ""), it.get("date", "")), "source": "apod"}
    raise RuntimeError("APOD: today's entry is not an image")


FETCHERS = {"wallhaven": fetch_wallhaven, "wikimedia": fetch_wikimedia, "bing": fetch_bing, "apod": fetch_apod}


def source_chain(cfg):
    s = cfg["source"]
    if s == "auto":
        return ["wallhaven", "wikimedia", "bing"]
    return [s] + [x for x in ("bing",) if x != s]  # Bing as last-resort fallback


# ---------------------------------------------------------------- image + desktop
def canvas_size(cfg):
    c = cfg.get("canvas")
    if c:
        return int(c[0]), int(c[1])
    if IS_WIN:
        u = ctypes.windll.user32
        return u.GetSystemMetrics(78), u.GetSystemMetrics(79)  # SM_CX/CYVIRTUALSCREEN
    return 3840, 1080


def compose(raw, size, anchor=0.5):
    """Cover-crop the image to exactly the combined desktop size."""
    W, H = size
    im = Image.open(io.BytesIO(raw))
    if im.width < 1920 or im.height < 800:
        raise RuntimeError("image too small (%dx%d)" % im.size)
    im = im.convert("RGB")
    scale = max(W / im.width, H / im.height)
    nw, nh = max(W, round(im.width * scale)), max(H, round(im.height * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - W) // 2
    top = int((nh - H) * min(max(anchor, 0.0), 1.0))
    return im.crop((left, top, left + W, top + H))


def set_wallpaper(path):
    if not IS_WIN:
        log.info("(not Windows) would set wallpaper: %s", path)
        return
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "WallpaperStyle", 0, winreg.REG_SZ, "22")  # 22 = Span
        winreg.SetValueEx(k, "TileWallpaper", 0, winreg.REG_SZ, "0")
    # SPI_SETDESKWALLPAPER = 20; 3 = update ini file + broadcast change
    if not ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3):
        raise ctypes.WinError()


def change_wallpaper(fresh=False):
    """fresh=False: today's image. fresh=True: user asked for a different one."""
    with _lock:
        cfg, st = load_config(), load_state()
        seen = set(st["history"])
        size = canvas_size(cfg)
        for name in source_chain(cfg):
            try:
                info = FETCHERS[name](cfg, seen, fresh)
                log.info("Downloading [%s] %s", name, info["url"])
                img = compose(http_get(info["url"], timeout=120), size, cfg.get("vertical_anchor", 0.5))
                out = os.path.join(DATA, "wallpaper_%d.jpg" % int(time.time()))
                img.save(out, "JPEG", quality=95, subsampling=0)
                set_wallpaper(out)
                for old in glob.glob(os.path.join(DATA, "wallpaper_*.jpg")):
                    if old != out:
                        try:
                            os.remove(old)
                        except OSError:
                            pass
                st["history"] = (st["history"] + [info["id"]])[-300:]
                st["last_date"] = datetime.date.today().isoformat()
                st["current"] = {"title": info["title"], "page": info["page"], "source": name, "file": out}
                save_json(STATE_PATH, st)
                log.info("Wallpaper set %dx%d: %s", size[0], size[1], info["title"])
                return info
            except Exception as e:
                log.warning("Source %s failed: %s", name, e)
        log.error("All sources failed; will retry later")
        return None


def run_test():
    cfg = load_config()
    print("Combined desktop size:", "%dx%d" % canvas_size(cfg))
    for name, fn in FETCHERS.items():
        try:
            info = fn(cfg, set(), True)
            n = len(http_get(info["url"], timeout=120))
            print("OK    %-10s %s  (%.1f MB)" % (name, info["title"][:70], n / 1e6))
        except Exception as e:
            print("FAIL  %-10s %s" % (name, e))


# ---------------------------------------------------------------- Windows integration
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def autostart_command():
    exe = sys.executable
    pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(pyw):
        exe = pyw
    return '"%s" "%s"' % (exe, os.path.abspath(__file__))


def autostart_enabled():
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, APP)
        return True
    except OSError:
        return False


def set_autostart(on):
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            winreg.SetValueEx(k, APP, 0, winreg.REG_SZ, autostart_command())
        else:
            try:
                winreg.DeleteValue(k, APP)
            except OSError:
                pass


def hotkey_thread(spec, callback):
    """Global hotkey via RegisterHotKey, e.g. 'ctrl+alt+n'."""
    from ctypes import wintypes
    mods, vk = 0x4000, None  # MOD_NOREPEAT
    for part in spec.lower().replace(" ", "").split("+"):
        if part in ("ctrl", "control"):
            mods |= 0x0002
        elif part == "alt":
            mods |= 0x0001
        elif part == "shift":
            mods |= 0x0004
        elif part == "win":
            mods |= 0x0008
        elif len(part) == 1 and part.isalnum():
            vk = ord(part.upper())
        elif part.startswith("f") and part[1:].isdigit():
            vk = 0x6F + int(part[1:])  # VK_F1 = 0x70
    if vk is None:
        log.warning("Hotkey %r not understood; hotkey disabled", spec)
        return
    user32 = ctypes.windll.user32
    if not user32.RegisterHotKey(None, 1, mods, vk):
        log.warning("Hotkey %s is already used by another program; hotkey disabled", spec)
        return
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        if msg.message == 0x0312:  # WM_HOTKEY
            callback()


def tray_icon_image():
    from PIL import ImageDraw
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((2, 16, 30, 46), 4, fill=(40, 120, 200), outline="white", width=2)
    d.rounded_rectangle((34, 16, 62, 46), 4, fill=(60, 170, 120), outline="white", width=2)
    d.polygon([(6, 42), (22, 24), (40, 42)], fill="white")
    d.polygon([(30, 42), (46, 28), (58, 42)], fill="white")
    return im


def run_tray():
    import pystray
    from pystray import Menu, MenuItem as Item

    if IS_WIN:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # real pixels on scaled displays
        except Exception:
            pass
    cfg = load_config()
    if not os.path.exists(CONFIG_PATH):
        save_json(CONFIG_PATH, cfg)

    def refresh_title():
        cur = load_state().get("current", {})
        icon.title = ("%s - %s" % (APP, cur.get("title", "")))[:120]

    def do_change(fresh):
        def work():
            if change_wallpaper(fresh) is None:
                try:
                    icon.notify("Could not download a wallpaper. Will retry.", APP)
                except Exception:
                    pass
            refresh_title()
        threading.Thread(target=work, daemon=True).start()

    def choose_source(name):
        def handler(icon_, item):
            save_config_value("source", name)
            do_change(True)
        return handler

    def toggle_autostart(icon_, item):
        set_autostart(not autostart_enabled())

    def open_page(icon_, item):
        page = load_state().get("current", {}).get("page")
        if page:
            webbrowser.open(page)

    # ---- Settings submenu -------------------------------------------------
    PRESETS = ["mountains", "landscape", "forest", "coast", "lake", "river", "waterfall",
               "desert", "snow", "city", "night sky", "space"]

    def get_keywords():
        kw = load_config().get("keywords") or []
        if isinstance(kw, str):
            kw = [kw] if kw.strip() else []
        return [str(k) for k in kw]

    def set_keywords(lst):
        save_config_value("keywords", lst)
        icon.update_menu()

    def toggle_keyword(k):
        def handler(icon_, item):
            lst = get_keywords()
            if k in lst:
                lst.remove(k)
            else:
                lst.append(k)
            set_keywords(lst)
        return handler

    def add_keyword(icon_, item):
        def work():
            import subprocess
            script = ("import tkinter as tk\n"
                      "from tkinter import simpledialog\n"
                      "r = tk.Tk(); r.withdraw(); r.attributes('-topmost', True)\n"
                      "v = simpledialog.askstring('SpanPaper', 'Keyword to add (e.g. himalaya):', parent=r)\n"
                      "print(v or '')\n")
            try:
                out = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True,
                                     timeout=300, creationflags=0x08000000 if IS_WIN else 0).stdout.strip()
            except Exception as e:
                log.warning("Keyword dialog failed: %s", e)
                return
            if out and out not in get_keywords():
                set_keywords(get_keywords() + [out])
        threading.Thread(target=work, daemon=True).start()

    def keyword_items():
        current = get_keywords()
        names = PRESETS + [k for k in current if k not in PRESETS]
        items = [Item(k, toggle_keyword(k), checked=lambda it, k=k: k in get_keywords()) for k in names]
        items += [Menu.SEPARATOR,
                  Item("Add custom keyword...", add_keyword),
                  Item("Clear all (any topic)", lambda i, it: set_keywords([]))]
        return items

    def choose_value(key, value):
        def handler(icon_, item):
            save_config_value(key, value)
        return handler

    def radio_menu(key, options):
        return Menu(*[Item(label, choose_value(key, val), radio=True,
                           checked=lambda it, val=val: load_config().get(key) == val)
                      for label, val in options])

    settings_menu = Menu(
        Item("Keywords (Wallhaven, Wikimedia)", Menu(keyword_items)),
        Item("Crop position (tall images)", radio_menu("vertical_anchor", [
            ("Top", 0.0), ("Upper", 0.25), ("Middle", 0.5), ("Lower", 0.75), ("Bottom", 1.0)])),
        Item("Bing region", radio_menu("bing_market", [
            ("India", "en-IN"), ("United States", "en-US"), ("United Kingdom", "en-GB"),
            ("Japan", "ja-JP"), ("Germany", "de-DE")])),
        Menu.SEPARATOR,
        Item("Open config.json (advanced)", lambda i, it: os.startfile(CONFIG_PATH)),
    )

    hot = cfg.get("hotkey") or ""
    menu = Menu(
        Item("Next image" + (" (%s)" % hot.upper() if hot else ""), lambda i, it: do_change(True), default=True),
        Item("Source", Menu(*[
            Item(SOURCE_LABELS[s], choose_source(s), radio=True,
                 checked=lambda it, s=s: load_config()["source"] == s) for s in SOURCES])),
        Item("About this image (open web page)", open_page),
        Item("Settings", settings_menu),
        Item("Open log", lambda i, it: os.startfile(LOG_PATH)),
        Item("Start with Windows", toggle_autostart, checked=lambda it: autostart_enabled()),
        Menu.SEPARATOR,
        Item("%s by %s" % (APP, COMPANY), None, enabled=False),
        Item(CREDIT, None, enabled=False),
        Item("Quit", lambda i, it: icon.stop()),
    )
    icon = pystray.Icon(APP, tray_icon_image(), APP, menu)

    def daily_loop():
        while True:
            try:
                if load_state()["last_date"] != datetime.date.today().isoformat():
                    change_wallpaper(False)
                    refresh_title()
            except Exception:
                log.exception("daily loop error")
            time.sleep(300)  # also the retry interval when offline

    threading.Thread(target=daily_loop, daemon=True).start()
    if hot and IS_WIN:
        threading.Thread(target=hotkey_thread, args=(hot, lambda: do_change(True)), daemon=True).start()
    refresh_title()
    icon.run()


if __name__ == "__main__":
    if IS_WIN:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass
    if "--test" in sys.argv:
        run_test()
    elif "--once" in sys.argv:
        sys.exit(0 if change_wallpaper("--next" in sys.argv) else 1)
    else:
        run_tray()
