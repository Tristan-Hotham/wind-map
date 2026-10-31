"""Step 4. Files the interactive page reads (data/page/). Rasters are coded into PNGs; the page decodes them in the browser.
  vis_year.png, vis_m01.png .. vis_m12.png, vis_seas.png, vis_peak.png : PICTURES of the WorldClim layers, 5 arc minutes,
               84N to 60S (4320 x 1728), as palette images whose colours are broad classes (wind 0.5 m/s classes up to 8 m/s,
               then wider). WorldClim may not be redistributed, so the grids themselves are not published.
  sum_1.png .. sum_5.png : the values the page reads out on click: 0.5 degree means (720 x 288), rounded to 0.5 m/s,
               code = 1 + 2 * m/s, 0 = no land. Channels in order: year, January, ..., December (last two empty).
  ncep.png   : NCEP/NCAR Reanalysis 1, 144 x (73 x 13): blocks of 73 rows for months 1 to 12 and the annual mean.
               R = u, G = v (code 128 + round(5 * m/s)), B = speed (code round(10 * m/s)). Row 0 = 90N, column 0 = 0E.
  farms.json : wind farms from the WRI Global Power Plant Database v1.3 with the WorldClim wind at their site.
  borders.json, places.json : Natural Earth country outlines and populated places; UK counties.
Run: python3 code/04_page_data.py
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy as np, pandas as pd
from PIL import Image
from shapely.geometry import shape, mapping

wc = np.load(f"{WORK}/wc.npy"); ann = np.load(f"{WORK}/ann.npy"); ratio = np.load(f"{WORK}/ratio.npy"); amax = np.load(f"{WORK}/argmax.npy")
r0, r1 = (90 - 84) * 12, (90 + 60) * 12
sys.path.insert(0, HERE_ := os.path.dirname(os.path.abspath(__file__)))
from figlib import wind_rgb, seas_rgb

# WorldClim is shown only as pictures: palette PNGs whose colours are classes, not values (WorldClim may not be redistributed).
# Wind classes: 0.5 m/s wide up to 8 m/s, 1 m/s to 12, then 12 to 16 and 16 or more. Index 0 = transparent (sea).
WB = list(np.arange(0, 8.01, .5)) + [9, 10, 11, 12, 16]
WMID = [(WB[i] + WB[i + 1]) / 2 for i in range(len(WB) - 1)] + [17]
SB = [1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4]
SMID = [(SB[i] + SB[i + 1]) / 2 for i in range(len(SB) - 1)] + [4.5]
MCOL = [(47, 84, 150), (62, 120, 178), (70, 160, 150), (96, 170, 92), (160, 190, 70), (228, 196, 64), (236, 150, 50), (214, 98, 52), (176, 60, 72), (128, 52, 110), (88, 60, 140), (56, 66, 140)]


def palette_png(cls, cols, path):
    """cls: uint8 class grid (0 = transparent); cols: RGB tuples for classes 1..n."""
    im = Image.fromarray(cls, "P")
    pal = [0, 0, 0] + [int(round(c)) for col in cols for c in col]
    im.putpalette(pal + [0] * (768 - len(pal)))
    im.info["transparency"] = 0
    im.save(path, optimize=True, transparency=0)


wcols = [tuple(x * 255) for x in wind_rgb(WMID)]
def wclass(a):
    c = np.digitize(np.nan_to_num(a, nan=-1), WB[1:-1]) + 1
    c[~np.isfinite(a)] = 0
    return c.astype(np.uint8)


for f in os.listdir(PAGE):
    if f.startswith(("wc_", "vis_", "sum_")): os.remove(os.path.join(PAGE, f))
palette_png(wclass(ann)[r0:r1], wcols, f"{PAGE}/vis_year.png")
for m in range(12):
    palette_png(wclass(wc[m])[r0:r1], wcols, f"{PAGE}/vis_m{m + 1:02d}.png")
valid = np.isfinite(ann)
sc = np.where(np.isfinite(ratio) & (ann >= 1.5), np.digitize(np.nan_to_num(ratio), SB[1:]) + 2, np.where(valid, 1, 0)).astype(np.uint8)
palette_png(sc[r0:r1], [(215, 215, 210)] + [tuple(x * 255) for x in seas_rgb(SMID)], f"{PAGE}/vis_seas.png")
palette_png(np.where(valid, amax + 1, 0).astype(np.uint8)[r0:r1], MCOL, f"{PAGE}/vis_peak.png")

# readout values: a coarse summary, 0.5 degree means of the 5' cells (at least a third of them land), rounded to 0.5 m/s
def coarse(a):
    b = a[r0:r1].reshape((r1 - r0) // 6, 6, NX // 6, 6)
    n = np.isfinite(b).sum(axis=(1, 3))
    with np.errstate(invalid="ignore"):
        m = np.nanmean(np.where(np.isfinite(b), b, np.nan).transpose(0, 2, 1, 3).reshape(b.shape[0], b.shape[2], -1), axis=2)
    m[n < 12] = np.nan
    return m


code = lambda a: np.where(np.isfinite(a), np.clip(np.round(np.nan_to_num(a) * 2) + 1, 1, 255), 0).astype(np.uint8)
layers = [code(coarse(ann))] + [code(coarse(wc[m])) for m in range(12)]
layers += [np.zeros_like(layers[0])] * 2
for k in range(5):
    Image.fromarray(np.dstack(layers[3 * k:3 * k + 3]), "RGB").save(f"{PAGE}/sum_{k + 1}.png", optimize=True)
jsave(dict(wind_breaks=WB, seas_breaks=SB, note="Display classes only; readout values from the 0.5 degree summary (sum_*.png: code = 1 + 2 * m/s; channels year, Jan..Dec)"), f"{PAGE}/legend.json")

z = np.load(f"{WORK}/ncep.npz")
U, V, SP = z["u"], z["v"], z["s"]
U = np.concatenate([U, U.mean(0, keepdims=True)]); V = np.concatenate([V, V.mean(0, keepdims=True)]); SP = np.concatenate([SP, SP.mean(0, keepdims=True)])
enc = lambda a: np.clip(128 + np.round(a * 5), 0, 255).astype(np.uint8)
img = np.dstack([enc(U).reshape(-1, 144), enc(V).reshape(-1, 144), np.clip(np.round(SP * 10), 0, 255).astype(np.uint8).reshape(-1, 144)])
Image.fromarray(img, "RGB").save(f"{PAGE}/ncep.png", optimize=True)
assert np.abs(U).max() < 25 and np.abs(V).max() < 25

F = pd.read_pickle(f"{WORK}/farms.pkl")
farms = [[r["name"], round(r.lat, 4), round(r.lon, 4), round(r.capacity_mw, 1), None if pd.isna(r.year) else int(r.year),
          None if pd.isna(r.wind) else round(r.wind, 2), None if pd.isna(r.country_pctile) else round(r.country_pctile * 100), r.site[0], r.country_name]
         for _, r in F.sort_values("capacity_mw", ascending=False).iterrows()]
jsave(farms, f"{PAGE}/farms.json")


def simplify_geo(feats, tol, nd, key):
    out = []
    for f in feats:
        g = shape(f["geometry"]).simplify(tol, preserve_topology=True)
        if g.is_empty: continue
        def r(c):
            if isinstance(c[0], (int, float)): return [round(c[0], nd), round(c[1], nd)]
            return [r(x) for x in c]
        m = mapping(g)
        out.append({"type": "Feature", "properties": {"n": f["properties"][key]}, "geometry": {"type": m["type"], "coordinates": r(m["coordinates"])}})
    return out


ne = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]
cb = simplify_geo(ne, 0.04, 2, "NAME")
uk = simplify_geo(jload(f"{GEO}/counties_uk.geojson")["features"], 0.004, 3, "county")
jsave({"countries": cb, "uk": uk}, f"{PAGE}/borders.json")
PP = [f["properties"] for f in jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]]
places = sorted([[p["name"], round(p["latitude"], 3), round(p["longitude"], 3), int(p.get("pop_max") or 0), p.get("adm0name") or ""] for p in PP], key=lambda x: -x[3])
cts = []
for f in ne:
    b = shape(f["geometry"]).bounds
    cts.append([f["properties"]["NAME"], round(b[1], 2), round(b[0], 2), round(b[3], 2), round(b[2], 2)])
jsave({"places": places, "countries": cts}, f"{PAGE}/places.json")

# small tables embedded in the page
R = jload(f"{DATA}/results.json")
nlat = z["lat"]; nlon = z["lon"]
landf = np.load(f"{WORK}/ncep_landf.npy"); OCE = landf < .1
cw = np.cos(np.radians(nlat))[:, None] * np.ones((1, 144))


def boxm(a, la0, la1, lo0, lo1):
    m = (nlat[:, None] >= la0) & (nlat[:, None] <= la1) & (nlon[None, :] >= lo0) & (nlon[None, :] <= lo1) & OCE
    return float((a * cw)[m].sum() / cw[m].sum())


PD = dict(
    arabian=[[round(boxm(U[m], 7.5, 17.5, 55, 70), 2), round(boxm(V[m], 7.5, 17.5, 55, 70), 2), round(boxm(SP[m], 7.5, 17.5, 55, 70), 2)] for m in range(12)],
    bengal=[[round(boxm(U[m], 10, 17.5, 82.5, 92.5), 2), round(boxm(V[m], 10, 17.5, 82.5, 92.5), 2), round(boxm(SP[m], 10, 17.5, 82.5, 92.5), 2)] for m in range(12)],
    zonal=[[z_["lat"], z_["u"], z_["speed"], z_["u_jan"], z_["u_jul"]] for z_ in R["zonal"] if z_["u"] is not None and abs(z_["lat"]) <= 75 and z_["ocean_share"] >= .2],
    nh=R["land"]["nh_month"], sh=R["land"]["sh_month"], uk=R["uk"]["months"],
    places=[[p["label"], p["label_country"], p["lat"], p["lon"], p["wind"], p["windiest_month"][:3], p["calmest_month"][:3]] for p in R["windiest_places"]],
    seasonal=[[p["label"], p["label_country"], p["lat"], p["lon"], p["ratio"], p["wind"], p["windiest_month"][:3], p["calmest_month"][:3]] for p in R["seasonal_places"]],
    cities=[[c["name"], c["country"], c["lat"], c["lon"], c["wind"]] for c in R["cities_windiest"][:10]] + [[c["name"], c["country"], c["lat"], c["lon"], c["wind"]] for c in R["cities_calmest"][:10]],
    farmc=[[r["name"], r["a3"], round(r["land_mean"], 2), round(r["farm_cw_wind"], 2), round(r["farm_cw_pctile"] * 100), round(r["land_cap_mw"]), r["land_farms"], round(r["sea_cap_mw"])]
           for r in R["farm_countries"]],
    ukc=[[d["county"], d["nation"], round(d["wind"], 2)] for d in R["uk_counties"]],
)
jsave(PD, f"{WORK}/page_data.json")
for f in sorted(os.listdir(PAGE)): print(f, os.path.getsize(f"{PAGE}/{f}"))
