"""Shared paths and helpers for the wind-map study.
Raw inputs (read in place, never copied into the repo):
  WorldClim 2.1 monthly wind speed, 5 arc minutes: RAW_WC/wc2.1_5m_wind_01.tif .. _12.tif
  NCEP/NCAR Reanalysis 1 long-term monthly means (sigma 0.995): RAW_WC/uwnd.mon.ltm.nc, vwnd.mon.ltm.nc, wspd.mon.ltm.nc
  WRI Global Power Plant Database v1.3: GPPD
  Natural Earth and UK boundaries: GEO
Intermediates are written to WORK (outside the repo by default)."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_WC = os.environ.get("WIND_RAW", "/home/claude/newdata/raw2/wind")
GPPD = os.environ.get("WIND_GPPD", "/home/claude/newdata/raw2/global-power-plant-database/output_database/global_power_plant_database.csv")
GEO = os.environ.get("WIND_GEO", "/home/claude/newdata/raw/geo")
DATA = os.path.join(ROOT, "data")
PAGE = os.path.join(DATA, "page")
WORK = os.environ.get("WIND_WORK", "/dev/shm/wind-map")
FONTS = os.environ.get("FONT_DIR", "/home/claude/ref/fonts")
for d in (DATA, PAGE, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "wind-map"
PAGE_URL = "https://maps.tristanhotham.com/wind-map/"
REPO = "https://github.com/Tristan-Hotham/wind-map"
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MON3 = [m[:3] for m in MONTHS]
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
# WorldClim 5 arc minute grid
NX, NY, CELL = 4320, 2160, 1 / 12


def dash(v):
    """House style: no em or en dashes, no double hyphens, in anything written to data/."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"), default=_np)


def _np(o):
    import numpy as np
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.bool_): return bool(o)
    if isinstance(o, np.ndarray): return o.tolist()
    raise TypeError(type(o))


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compass(deg):
    """Compass point (16) for a direction in degrees the wind blows FROM."""
    pts = ["north", "north-north-east", "north-east", "east-north-east", "east", "east-south-east", "south-east", "south-south-east",
           "south", "south-south-west", "south-west", "west-south-west", "west", "west-north-west", "north-west", "north-north-west"]
    return pts[int(round((deg % 360) / 22.5)) % 16]
