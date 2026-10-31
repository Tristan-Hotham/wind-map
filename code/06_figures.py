"""Step 6. Static figures for the blog post (release/blog/b_*.png) and the paper (release/paper/fig_*.png).
Run: python3 code/06_figures.py
"""
import sys, os, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *
import pandas as pd
from matplotlib.patches import Rectangle

R = jload(f"{DATA}/results.json")
BLOG = os.path.join(ROOT, "release", "blog"); PAP = os.path.join(ROOT, "release", "paper")
os.makedirs(BLOG, exist_ok=True); os.makedirs(PAP, exist_ok=True)
wc = np.load(f"{WORK}/wc.npy"); ann = np.load(f"{WORK}/ann.npy"); ratio = np.load(f"{WORK}/ratio.npy")
U, V, SP, nlat, nlon = ncep()


def save(fig, name):
    fig.savefig(f"{BLOG}/b_{name}.png", dpi=150, facecolor=fig.get_facecolor())
    shutil.copy(f"{BLOG}/b_{name}.png", f"{PAP}/fig_{name}.png")
    plt.close(fig)


def region(la0, la1, lo0, lo1):
    rows = np.arange(int((90 - la1) * 12), int((90 - la0) * 12)); cols = np.arange(int((lo0 + 180) * 12), int((lo1 + 180) * 12))
    return rows, cols


def wind_panel(ax, month, ext, density=2.2, fade=.45, lw=(.35, 1.6)):
    rows, cols = region(ext[2], ext[3], ext[0], ext[1])
    land = (ann if month is None else wc[month])[rows][:, cols]
    sea = ncep_on_grid(SP.mean(0) if month is None else SP[month], rows, cols)
    ax.imshow(wind_image(land, sea, fade), extent=[ext[0], ext[1], ext[2], ext[3]], aspect="auto", interpolation="nearest", zorder=1)
    coast(ax, lw=.35)
    streams(ax, U.mean(0) if month is None else U[month], V.mean(0) if month is None else V[month], nlat, nlon, ext, density=density, lw=lw)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)


def cbar(fig, rect, label):
    ca = fig.add_axes(rect); ca.imshow(wind_rgb(np.linspace(0, 16, 300))[None], extent=[0, 16, 0, 1], aspect="auto")
    ca.set_yticks([]); ca.set_xticks([0, 2, 4, 6, 8, 10, 12, 14, 16]); ca.tick_params(labelsize=9, colors=FG, length=3)
    for s in ca.spines.values(): s.set_color(MUT)
    ca.set_xlabel(label, fontsize=9, color=MUT)


# 1. world map, annual
fig = plt.figure(figsize=(12, 6.6), facecolor=BG)
ax = fig.add_axes([0.01, 0.13, 0.98, 0.85]); ext = (-180, 180, -60, 80)
wind_panel(ax, None, ext, density=2.6, fade=.55)
ax.set_aspect(1.15)
for t, x, y in [("north-east trades", -40, 17), ("south-east trades", -20, -14), ("westerlies", -30, 48), ("Roaring Forties", 40, -46), ("south-east trades", 85, -15), ("north-east trades", -150, 15)]:
    ax.text(x, y, t, fontsize=10, color=FG, ha="center", va="center", zorder=7, bbox=dict(fc=PAPER, ec="none", alpha=.82, pad=1.5))
cbar(fig, [0.3, 0.075, 0.4, 0.025], "mean wind speed, m/s. Land: WorldClim at 10 m, 1970 to 2000. Sea (faded): NCEP reanalysis, 1991 to 2020")
save(fig, "world_map")

# 2. monsoon, January and July
fig = plt.figure(figsize=(12, 5.6), facecolor=BG)
ext = (35, 105, -12, 32)
for k, (m, t) in enumerate([(0, "January"), (6, "July")]):
    ax = fig.add_axes([0.01 + k * 0.5, 0.2, 0.48, 0.71]); wind_panel(ax, m, ext, density=1.7, lw=(.5, 2.0))
    ax.set_aspect(1.0)
    fig.text(0.015 + k * 0.5, 0.95, t, fontproperties=DISP, fontsize=22, color=FG, va="top")
cbar(fig, [0.3, 0.1, 0.4, 0.03], "mean wind speed, m/s (land WorldClim, sea faded: NCEP)")
save(fig, "monsoon")

# 3. wind belts by latitude
z = pd.DataFrame(R["zonal"]); z = z[(z.ocean_share >= .2) & (z.lat.abs() <= 75)]
fig, ax = plt.subplots(figsize=(10, 7.2), facecolor=BG); ax.set_facecolor(BG)
ax.barh(z.lat, z.u, height=2.1, color=[GOLD if v < 0 else TEAL for v in z.u], alpha=.9)
ax2 = ax.twiny(); ax2.plot(z.speed, z.lat, color=DEEP, lw=2.4); ax2.set_xlim(0, 14); ax2.set_xlabel("mean speed over the oceans, m/s (line)", color=DEEP, fontsize=10)
ax2.tick_params(colors=DEEP, labelsize=9); [ax2.spines[s].set_visible(False) for s in ("right", "bottom", "left")]; ax2.spines["top"].set_color(DEEP)
ax.axvline(0, color=FG, lw=.8); ax.set_xlim(-9, 9); ax.set_ylim(-75, 75)
ax.set_yticks(range(-75, 76, 15)); ax.set_yticklabels([f"{abs(v)}°{'N' if v > 0 else 'S' if v < 0 else ''}" for v in range(-75, 76, 15)])
ax.set_xlabel("mean west to east wind over the oceans, m/s (bars): left from the east, right from the west", fontsize=10)
style(ax)
for t, la, x, c in [("north-east trades", 15, -8.6, GOLD), ("south-east trades", -15, -8.6, GOLD), ("westerlies", 47.5, 4.2, TEAL), ("Roaring Forties", -42, -8.6, TEAL), ("Furious Fifties", -53, -8.6, TEAL)]:
    ax.text(x, la, t, color=c, fontsize=11, va="center", fontweight="bold", ha="left")
fig.tight_layout(); save(fig, "belts")

# 4. windiest places
P = R["windiest_places"]
fig, ax = plt.subplots(figsize=(10, 7.4), facecolor=BG); ax.set_facecolor(BG)
y = np.arange(len(P))[::-1]
ax.barh(y, [p["wind"] for p in P], color=wind_rgb([p["wind"] for p in P]), edgecolor=MUT, lw=.4, height=.72)
for yy, p in zip(y, P):
    ax.text(-.2, yy, p["label"] if p["label_country"] in p["label"] else f"{p['label']}, {p['label_country']}", ha="right", va="center", fontsize=10, family=SER)
    ax.text(p["wind"] + .15, yy, f"{p['wind']:.1f}", va="center", fontsize=9.5)
ax.set_yticks([]); ax.set_xlim(0, 17.5); style(ax); ax.spines["left"].set_visible(False)
ax.set_xlabel("annual mean wind at 10 m, m/s (WorldClim, 1970 to 2000)", fontsize=10)
fig.tight_layout(); fig.subplots_adjust(left=.40); save(fig, "windiest")

# 5. seasons: ratio map and monthly lines
fig = plt.figure(figsize=(12, 5.4), facecolor=BG)
ax = fig.add_axes([0.0, 0.2, 0.62, 0.78]); ext = (-180, 180, -58, 80)
rows, cols = region(ext[2], ext[3], ext[0], ext[1])
rr = ratio[rows][:, cols]; aa = ann[rows][:, cols]
img = np.ones(rr.shape + (3,)) * np.array([.86, .89, .91])
lm = np.isfinite(aa); img[lm] = [.84, .84, .82]
mm = np.isfinite(rr) & (aa >= 1.5); img[mm] = seas_rgb(rr[mm])
ax.imshow(img, extent=[ext[0], ext[1], ext[2], ext[3]], aspect=1.15, interpolation="nearest"); ax.axis("off")
ca = fig.add_axes([0.13, 0.13, 0.36, 0.03]); ca.imshow(seas_rgb(np.linspace(1, 4, 300))[None], extent=[1, 4, 0, 1], aspect="auto")
ca.set_yticks([]); ca.set_xticks([1, 1.5, 2, 3, 4]); ca.set_xticklabels(["1×", "1.5×", "2×", "3×", "4×+"]); ca.tick_params(labelsize=9)
ca.set_xlabel("windiest month / calmest month (land, mean wind at least 1.5 m/s)", fontsize=9, color=MUT)
ax2 = fig.add_axes([0.68, 0.16, 0.30, 0.74]); ax2.set_facecolor(BG)
for lab, arr, col in [("Northern land", R["land"]["nh_month"], TEAL), ("Southern land", R["land"]["sh_month"], GOLD), ("UK", R["uk"]["months"], DEEP)]:
    ax2.plot(range(12), arr, color=col, lw=2.4, marker="o", ms=4, label=lab)
ax2.set_xticks(range(12)); ax2.set_xticklabels([m[0] for m in MONTHS]); ax2.set_ylabel("mean wind at 10 m, m/s", fontsize=10)
style(ax2, grid=False); ax2.grid(axis="y", color=RULE); ax2.legend(frameon=False, fontsize=9, loc="center right", ncol=1, bbox_to_anchor=(1.0, .5))
save(fig, "seasons")

# 6. farms against land
FC = sorted(R["farm_countries"], key=lambda r: r["farm_cw_pctile"])
fig, ax = plt.subplots(figsize=(10, 7.6), facecolor=BG); ax.set_facecolor(BG)
for i, r in enumerate(FC):
    ax.plot([r["land_mean"], r["farm_cw_wind"]], [i, i], color=CORAL if r["farm_cw_wind"] >= r["land_mean"] else MUT, lw=2.6, zorder=2)
    ax.scatter([r["land_mean"]], [i], s=46, color=MUT, zorder=3); ax.scatter([r["farm_cw_wind"]], [i], s=64, color=CORAL, edgecolor="white", zorder=4)
    ax.text(6.55, i, f"{round(r['farm_cw_pctile'] * 100)}%", va="center", ha="right", fontsize=10, fontweight="bold")
ax.set_yticks(range(len(FC))); ax.set_yticklabels([r["name"].replace("United States of America", "United States") for r in FC], fontsize=10, family=SER)
ax.set_xlim(1, 6.6); ax.set_xlabel("mean wind at 10 m, m/s.  Grey: country's land.  Coral: capacity-weighted onshore farms", fontsize=10)
ax.text(6.55, len(FC) - .1 + .6, "land less windy\nthan the average farm", ha="right", va="bottom", fontsize=8.5, color=MUT)
style(ax); fig.tight_layout(); save(fig, "farms")

# 7. UK and Ireland
F = pd.read_pickle(f"{WORK}/farms.pkl")
fig = plt.figure(figsize=(8, 10), facecolor=BG)
ax = fig.add_axes([0.02, 0.1, 0.96, 0.88]); ext = (-11, 2.2, 49.8, 61)
rows, cols = region(ext[2], ext[3], ext[0], ext[1])
land = ann[rows][:, cols]; sea = ncep_on_grid(SP.mean(0), rows, cols)
img = np.ones(land.shape + (3,)) * np.array([0.89, 0.92, 0.93]); m_ = np.isfinite(land); img[m_] = wind_rgb(land[m_])
ax.imshow(img, extent=[ext[0], ext[1], ext[2], ext[3]], aspect=1 / np.cos(np.radians(55)), interpolation="nearest")
for f in jload(f"{GEO}/counties_uk.geojson")["features"]:
    g = f["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    for poly in polys:
        a = np.array(poly[0]); ax.plot(a[:, 0], a[:, 1], color="white", lw=.35, alpha=.7)
uf = F[(F.lat > 49.8) & (F.lat < 61) & (F.lon > -11) & (F.lon < 2.2)]
for site, col, lab in [("land", CORAL, "wind farm on land"), ("coast", CORAL, None), ("sea", DEEP, "wind farm at sea")]:
    q = uf[uf.site == site]
    ax.scatter(q.lon, q.lat, s=4 + np.sqrt(q.capacity_mw) * 2.2, color=col, edgecolor="white", lw=.4, alpha=.9, zorder=5, label=lab)
ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.axis("off")
ax.legend(loc="lower left", bbox_to_anchor=(0.0, 0.9), frameon=False, fontsize=10, markerscale=1.2)
ax.text(-8.85, 57.82, "St Kilda, windiest in the UK", fontsize=9.5, ha="right", va="center")
cbar(fig, [0.15, 0.06, 0.7, 0.022], "mean wind speed at 10 m, m/s (WorldClim, 1970 to 2000).  Farms: WRI database, 2021")
save(fig, "uk")

# paper only: four months
fig = plt.figure(figsize=(12, 7.2), facecolor=BG); ext = (-180, 180, -60, 80)
for k, m in enumerate([0, 3, 6, 9]):
    ax = fig.add_axes([0.005 + (k % 2) * 0.5, 0.53 - (k // 2) * 0.43, 0.49, 0.40]); wind_panel(ax, m, ext, density=1.4, lw=(.25, 1.0))
    ax.text(-176, 74, MONTHS[m], fontsize=13, fontproperties=DISP, color=FG, va="top", bbox=dict(fc=PAPER, ec="none", alpha=.8, pad=2))
cbar(fig, [0.3, 0.06, 0.4, 0.025], "mean wind speed, m/s")
fig.savefig(f"{PAP}/fig_months.png", dpi=150, facecolor=BG); plt.close(fig)
print("figures written:", sorted(os.listdir(BLOG)))
