"""r/dataisbeautiful collage: reddit/where_the_wind_blows.png (2400 x 3000) on light paper.
Hero: the world's annual winds with streamlines. Then the monsoon in January and July, four big numbers,
wind farms against their country's land, and the UK. Every number comes from ../data/results.json.
Also writes reddit/post.md (title, body and source comment) from the same results.
Run: python3 reddit/collage.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "code"))
from figlib import *
import pandas as pd

R = jload(os.path.join(ROOT, "data", "results.json"))
ann = np.load(f"{WORK}/ann.npy"); wc = np.load(f"{WORK}/wc.npy"); U, V, SP, nlat, nlon = ncep()
pct = lambda v: f"{round(v * 100)}%"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)


def region(la0, la1, lo0, lo1):
    return np.arange(int((90 - la1) * 12), int((90 - la0) * 12)), np.arange(int((lo0 + 180) * 12), int((lo1 + 180) * 12))


def panel(ax, month, ext, fade, density, lw):
    rows, cols = region(ext[2], ext[3], ext[0], ext[1])
    land = (ann if month is None else wc[month])[rows][:, cols]
    sea = ncep_on_grid(SP.mean(0) if month is None else SP[month], rows, cols)
    ax.imshow(wind_image(land, sea, fade), extent=[ext[0], ext[1], ext[2], ext[3]], aspect="auto", interpolation="nearest")
    streams(ax, U.mean(0) if month is None else U[month], V.mean(0) if month is None else V[month], nlat, nlon, ext, density=density, lw=lw, arrows=.9)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)


# title
fig.text(0.04, 0.978, "Where the wind blows,", fontproperties=DISP, fontsize=46, color=FG, va="top")
fig.text(0.04, 0.935, "and are the wind farms there?", fontproperties=DISP, fontsize=46, color=TEAL, va="top")
fig.text(0.04, 0.886, "Mean wind speed over land at 10 m (WorldClim, 1970 to 2000, about 9 km cells) and over the sea (NCEP reanalysis,\n"
         "1991 to 2020, faded). Lines show the average direction of the near-surface wind through the year.",
         family=SER, fontsize=14, color=FG, va="top", linespacing=1.4)

# hero world map
ax = fig.add_axes([0.04, 0.595, 0.92, 0.24]); ext = (-180, 180, -58, 78)
panel(ax, None, ext, .62, 2.4, (.35, 1.5))
lab = dict(fontsize=11, color=FG, ha="center", va="center", family=MONO, bbox=dict(fc=PAPER, ec="none", alpha=.92, pad=2), zorder=10)
for t, x, y in [("north-east trades", -38, 16), ("north-east trades", -150, 14), ("south-east trades", -18, -14), ("south-east trades", 80, -14),
                ("westerlies", -35, 45), ("Roaring Forties", 20, -46), ("Roaring Forties", 160, -48)]:
    ax.text(x, y, t, **lab)
# legend for the colours
ca = fig.add_axes([0.25, 0.578, 0.5, 0.01]); ca.imshow(wind_rgb(np.linspace(0, 16, 300))[None], extent=[0, 16, 0, 1], aspect="auto")
ca.set_yticks([]); ca.set_xticks(range(0, 17, 2)); ca.tick_params(labelsize=10, length=3, colors=FG)
for s in ca.spines.values(): s.set_color(MUT)
fig.text(0.5, 0.552, "mean wind speed, metres per second (land: full colour; sea: faded)", ha="center", fontsize=10.5, color=MUT, family=MONO)

# monsoon: January and July
fig.text(0.04, 0.525, "THE MONSOON TURNS AROUND", fontsize=11, color=MUT, family=MONO)
mo = R["monsoon"]
for k, (m, t, d) in enumerate([(0, "January", mo["arabian_jan"]), (6, "July", mo["arabian_jul"])]):
    a = fig.add_axes([0.04 + k * 0.235, 0.385, 0.225, 0.13]); panel(a, m, (38, 98, -8, 30), .45, 1.3, (.5, 1.8))
    fig.text(0.04 + k * 0.235, 0.378, f"Arabian Sea wind from the\n{d['from_pt']}, {d['vec']:.1f} m/s", fontsize=10.5, color=FG, family=MONO, va="top", linespacing=1.3)
    fig.text(0.045 + k * 0.235, 0.511, t, fontproperties=DISP, fontsize=17, color=FG, va="top", bbox=dict(fc=PAPER, ec="none", alpha=.85, pad=2))

# big numbers
nums = [(pct(R["farms"]["share_cap_above_median"]), CORAL, "of onshore wind farm capacity stands on\nground windier than its country's median"),
        (f"{R['circ']['roar_s']:.1f} m/s", DEEP, f"over the Roaring Forties (40 to 50° S),\nagainst {R['circ']['roar_n']:.1f} at 40 to 50° N"),
        (R["land"]["nh_windiest_month"], PLUM, f"is the windiest month on northern land,\n{R['land']['nh_calmest_month']} the calmest: spring, not winter"),
        (f"{R['uk']['mean']:.1f} m/s", TEAL, f"the UK's land average, {R['derived']['uk_vs_land']:.1f} times\nthe world's. Windiest: St Kilda, {R['uk']['max']['wind']:.1f} m/s")]
for i, (big, col, small) in enumerate(nums):
    y = 0.525 - i * 0.047
    fig.text(0.53, y, big, fontproperties=DISP, fontsize=27, color=col, va="top")
    fig.text(0.715, y - .002, small, family=SER, fontsize=11, color=FG, va="top", linespacing=1.3)

# farms against land
FC = sorted(R["farm_countries"], key=lambda r: r["farm_cw_pctile"])
keep = ["MEX", "BRA", "AUS", "NOR", "IND", "USA", "CHN", "FRA", "GBR", "ESP", "IRL", "CHL"]
FC = [r for r in FC if r["a3"] in keep]
af = fig.add_axes([0.2, 0.09, 0.36, 0.17]); af.set_facecolor(BG)
for i, r in enumerate(FC):
    af.plot([r["land_mean"], r["farm_cw_wind"]], [i, i], color=CORAL if r["farm_cw_wind"] >= r["land_mean"] else MUT, lw=2.4)
    af.scatter([r["land_mean"]], [i], s=26, color=MUT, zorder=3); af.scatter([r["farm_cw_wind"]], [i], s=34, color=CORAL, edgecolor="white", lw=.6, zorder=4)
    af.text(0.95, i, r["name"].replace("United States of America", "United States"), ha="right", va="center", fontsize=10, family=MONO)
    af.text(6.1, i, pct(r["farm_cw_pctile"]), ha="right", va="center", fontsize=10, family=MONO, fontweight="bold")
af.set_xlim(1, 6.15); af.set_yticks([]); af.set_xticks([1, 2, 3, 4, 5]); af.tick_params(labelsize=9.5)
for s in ("top", "right", "left"): af.spines[s].set_visible(False)
af.spines["bottom"].set_color(MUT)
fig.text(0.04, 0.33, "ARE THE WIND FARMS IN THE WINDY PLACES?", fontsize=11, color=MUT, family=MONO)
fig.text(0.04, 0.318, "Mean wind at 10 m, m/s. Grey dot: the country's land.\nCoral dot: its onshore wind farms, weighted by capacity.\nRight: share of the country's land less windy than the farms.", fontsize=9.5, color=FG, family=MONO, va="top", linespacing=1.35)

# UK
F = pd.read_pickle(f"{WORK}/farms.pkl")
au = fig.add_axes([0.62, 0.08, 0.34, 0.21]); ext = (-8.4, 2.0, 49.85, 58.8)
rows, cols = region(ext[2], ext[3], ext[0], ext[1]); land = ann[rows][:, cols]
img = np.ones(land.shape + (3,)) * np.array([.96, .95, .93]); m_ = np.isfinite(land); img[m_] = wind_rgb(land[m_])
au.imshow(img, extent=[ext[0], ext[1], ext[2], ext[3]], aspect=1 / np.cos(np.radians(54.5)), interpolation="nearest")
uf = F[(F.lat > ext[2]) & (F.lat < ext[3]) & (F.lon > ext[0]) & (F.lon < ext[1])]
for site, col in (("land", CORAL), ("coast", CORAL), ("sea", DEEP)):
    q = uf[uf.site == site]; au.scatter(q.lon, q.lat, s=1.5 + np.sqrt(q.capacity_mw) * .9, color=col, edgecolor="white", lw=.25, zorder=5)
au.set_xlim(ext[0], ext[1]); au.set_ylim(ext[2], ext[3]); au.axis("off")
fig.text(0.62, 0.33, "UK AND IRELAND: WIND AND WIND FARMS", fontsize=11, color=MUT, family=MONO)
au.scatter([], [], s=30, color=CORAL, label="wind farm on land"); au.scatter([], [], s=30, color=DEEP, label="wind farm at sea")
fig.legend(*au.get_legend_handles_labels(), loc="upper left", bbox_to_anchor=(0.61, 0.326), ncol=2, frameon=False, fontsize=9.5, handletextpad=.3, columnspacing=1)

# footer
fig.text(0.04, 0.068, "Data: WorldClim 2.1 monthly wind speed (Fick and Hijmans 2017, free for non-commercial use with citation); NCEP/NCAR Reanalysis 1\n"
         "long-term monthly means 1991 to 2020 (NOAA PSL, public domain; Kalnay et al. 1996); WRI Global Power Plant Database v1.3, a 2021\n"
         "snapshot with uneven coverage (CC BY 4.0); Natural Earth. Wind at 10 m, not at turbine height.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib.   maps.tristanhotham.com/wind-map",
         family=MONO, fontsize=9.5, color=MUT, va="top", linespacing=1.45)
fig.savefig(os.path.join(HERE, "where_the_wind_blows.png"), facecolor=BG)
print("collage written")

p = pct
post = f"""# Reddit post

## Title

[OC] Where the wind blows: the world's winds month by month, and are wind farms in the windy places? {p(R['farms']['share_cap_above_median'])} of onshore wind farm capacity sits on ground windier than its country's median

## Body (optional)

Land winds are WorldClim's monthly means at 10 m (1970 to 2000, about 9 km cells); sea winds and the streamlines are from the NCEP/NCAR reanalysis (1991 to 2020). The Roaring Forties average {R['circ']['roar_s']:.1f} m/s over the ocean at 40 to 50° S, against {R['circ']['roar_n']:.1f} m/s at the same latitudes in the north, and in the Arabian Sea the wind swings from the {mo['arabian_jan']['from_pt']} in January to the {mo['arabian_jul']['from_pt']} in July. On northern land the windiest month is {R['land']['nh_windiest_month']}, not midwinter. I then set the {R['farms']['n']:,} wind farms in WRI's Global Power Plant Database (a 2021 snapshot) against the wind at their sites: the average farm stands on ground windier than {p(R['farms']['land_cw_pctile'])} of its country's land, most of all in Mexico ({p(R['fc']['MEX']['farm_cw_pctile'])}) and Brazil ({p(R['fc']['BRA']['farm_cw_pctile'])}); Chile's farms ({p(R['fc']['CHL']['farm_cw_pctile'])}) sit far from its windy Patagonia. Caveats: 10 m is not hub height, 9 km cells cannot see the ridge a farm is built on, and the database's coverage is uneven. Explore it month by month: https://maps.tristanhotham.com/wind-map/

## Source comment

Sources: WorldClim 2.1 monthly mean wind speed at 5 arc minutes (Fick, S.E. and Hijmans, R.J. 2017, WorldClim 2: new 1 km spatial resolution climate surfaces for global land areas, International Journal of Climatology; free for research and non-commercial use); NCEP/NCAR Reanalysis 1 long-term monthly means, 1991 to 2020, sigma level 0.995 (NOAA PSL, public domain; Kalnay et al. 1996); WRI Global Power Plant Database v1.3 (CC BY 4.0); boundaries and places from Natural Earth and ONS.

Tools: Python (numpy, pandas, rasterio, netCDF4, matplotlib, Pillow); Leaflet for the interactive map.

Interactive map: https://maps.tristanhotham.com/wind-map/
Blog post: {{https://blog.tristanhotham.com/2026/10/31/wind-map/}}
Paper and data: {{https://doi.org/10.5281/zenodo.23844511}}
"""
for b in ("—", "–", "--"): assert b not in post
open(os.path.join(HERE, "post.md"), "w").write(post)
print("post written")
