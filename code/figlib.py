"""Shared drawing helpers for the static figures, the header and the collage: fonts, the wind palette used on the page,
and loaders for the grids (WorldClim land, NCEP sea and direction) on a common 5 arc minute raster."""
import os, sys
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import ListedColormap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(os.path.join(FONTS, f))
DISP = fm.FontProperties(fname=os.path.join(FONTS, "FrauncesVar.ttf"), weight=900)
SER, MONO = "Source Serif 4", "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 11})
BG, FG, MUT, RULE, PAPER = "#F4F2EC", "#16202A", "#5B6470", "#D9D4C8", "#FBFAF6"
DEEP, TEAL, PLUM, CORAL, GOLD, SEA = "#24356B", "#1F7A8C", "#7A2E74", "#D9583B", "#D99A1E", "#DCE4E8"
WSTOPS = [(0, (246, 243, 233)), (1, (232, 236, 212)), (2, (199, 224, 194)), (3, (141, 202, 183)), (4, (77, 169, 173)), (5, (40, 129, 165)), (6, (37, 92, 150)),
          (7, (44, 61, 125)), (8.5, (76, 41, 119)), (10, (128, 37, 112)), (12.5, (182, 53, 92)), (16, (226, 104, 72))]
SSTOPS = [(1, (238, 238, 230)), (1.25, (238, 224, 178)), (1.6, (232, 186, 96)), (2.1, (216, 124, 52)), (3, (168, 58, 48)), (4.5, (92, 28, 62))]


def ramp(stops, x):
    x = np.asarray(x, float); xs = [s[0] for s in stops]; cs = np.array([s[1] for s in stops]) / 255
    return np.stack([np.interp(x, xs, cs[:, k]) for k in range(3)], axis=-1)


wind_rgb = lambda s: ramp(WSTOPS, s)
seas_rgb = lambda r: ramp(SSTOPS, r)
WIND_CMAP = ListedColormap(wind_rgb(np.linspace(0, 16, 256)))
SEAS_CMAP = ListedColormap(seas_rgb(np.linspace(1, 4.5, 256)))
LAT = 90 - (np.arange(NY) + .5) * CELL; LON = -180 + (np.arange(NX) + .5) * CELL


def ncep():
    z = np.load(f"{WORK}/ncep.npz")
    return z["u"], z["v"], z["s"], z["lat"], z["lon"]


def ncep_on_grid(arr, rows, cols):
    """Bilinear NCEP field (73 x 144, 90N..90S, 0..357.5E) sampled at the 5' cells rows x cols."""
    la, lo = LAT[rows], LON[cols]
    fy = (90 - la) / 2.5; fx = (lo % 360) / 2.5
    y0 = np.clip(np.floor(fy).astype(int), 0, 71); ty = np.clip(fy - y0, 0, 1)
    x0 = np.floor(fx).astype(int) % 144; x1 = (x0 + 1) % 144; tx = fx - np.floor(fx)
    a = arr[y0][:, x0] * (1 - tx) + arr[y0][:, x1] * tx
    b = arr[y0 + 1][:, x0] * (1 - tx) + arr[y0 + 1][:, x1] * tx
    return a * (1 - ty)[:, None] + b * ty[:, None]


def wind_image(land, sea, sea_fade=.45):
    """RGB image: land in the full palette, sea (NCEP) faded towards white."""
    img = wind_rgb(np.nan_to_num(sea))
    img = img * (1 - sea_fade) + np.array([.97, .97, .96]) * sea_fade
    m = np.isfinite(land)
    img[m] = wind_rgb(land[m])
    return img


def streams(ax, u, v, lat, lon, extent, density=2.2, color=FG, lw=(.35, 1.6), alpha=.75, arrows=1.0):
    """Streamlines from an NCEP field on a plain lon/lat axis."""
    U = np.roll(u, 72, axis=1)[::-1]; V = np.roll(v, 72, axis=1)[::-1]
    x = ((np.roll(lon, 72) + 180) % 360) - 180; y = lat[::-1]
    U = np.concatenate([U, U[:, :1]], 1); V = np.concatenate([V, V[:, :1]], 1); x = np.append(x, 180.0)
    j = (y >= extent[2] - 5) & (y <= extent[3] + 5)
    sp = np.hypot(U[j], V[j])
    ax.streamplot(x, y[j], U[j], V[j], density=density, color=color, linewidth=lw[0] + (lw[1] - lw[0]) * np.clip(sp / 12, 0, 1),
                  arrowsize=arrows, arrowstyle="-|>", minlength=.15, maxlength=4, integration_direction="forward", zorder=5)
    for c in ax.collections[-1:]:
        c.set_alpha(alpha)
    for p in ax.patches:
        p.set_alpha(alpha)


def coast(ax, lw=.4, color="#3A4450", alpha=.6):
    import json
    for f in jload(f"{GEO}/ne_50m_land.geojson")["features"]:
        g = f["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            a = np.array(poly[0]); ax.plot(a[:, 0], a[:, 1], color=color, lw=lw, alpha=alpha, zorder=4)


def style(ax, grid=True):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(MUT)
    ax.tick_params(colors=FG, labelsize=10)
    if grid: ax.grid(axis="x", color=RULE, lw=.8); ax.set_axisbelow(True)
