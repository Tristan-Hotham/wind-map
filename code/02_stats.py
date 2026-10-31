"""Step 2. All the statistics: land winds and seasonality (WorldClim), the global circulation (NCEP/NCAR Reanalysis 1),
the windiest places, wind farms (WRI Global Power Plant Database) against the wind at their sites, and the UK.
Writes the derived CSVs in data/ and work/stats.json (turned into data/results.json by step 3).
Run: python3 code/02_stats.py
"""
import sys, os, math, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy as np, pandas as pd
from rasterio.features import rasterize
from rasterio.transform import from_origin

wc = np.load(f"{WORK}/wc.npy")                      # 12 x NY x NX
valid = np.isfinite(wc[0])
ann = np.where(valid, np.nansum(wc, axis=0) / 12.0, np.nan).astype(np.float32)   # annual mean = mean of the 12 monthly means
cid = np.load(f"{WORK}/country.npy")
CL = jload(f"{WORK}/countries.json")
LAT = (90 - (np.arange(NY) + .5) * CELL); LON = (-180 + (np.arange(NX) + .5) * CELL)
WROW = np.cos(np.radians(LAT))                       # area weight of a cell in each row
W2 = np.broadcast_to(WROW[:, None], (NY, NX))
notant = LAT[:, None] >= -60
LANDX = valid & notant                                # land outside Antarctica
S = {}

# ---------- admin-1 raster, for naming places ----------
a1f = jload(f"{GEO}/ne_10m_admin_1_states_provinces.geojson")["features"]
A1 = [(f["properties"].get("name") or "", f["properties"].get("admin") or "") for f in a1f]
a1 = rasterize([(f["geometry"], i + 1) for i, f in enumerate(a1f)], out_shape=(NY, NX), transform=from_origin(-180, 90, CELL, CELL), fill=0, dtype="int32")
np.save(f"{WORK}/admin1.npy", a1)
jsave(A1, f"{WORK}/admin1.json")
PP = [f["properties"] for f in jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]]


def hav(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(min(1, x)))


def rc(lat, lon):
    return min(NY - 1, max(0, int((90 - lat) / CELL))), int(((lon + 180) % 360) / CELL) % NX


def near_val(grid, lat, lon, k=1):
    """Value at the cell, or the mean of valid cells within k cells (for points on the coast)."""
    r, c = rc(lat, lon)
    v = grid[..., r, c]
    if np.all(np.isfinite(v)):
        return v, "land"
    blk = grid[..., max(0, r - k):r + k + 1, max(0, c - k):c + k + 1]
    with np.errstate(invalid="ignore"):
        m = np.nanmean(blk.reshape(blk.shape[:-2] + (-1,)), axis=-1) if blk.ndim > 2 else np.nanmean(blk)
    return (m, "coast") if np.all(np.isfinite(m)) else (m, "sea")


def place_name(lat, lon):
    r, c = rc(lat, lon)
    blk = a1[max(0, r - 3):r + 4, max(0, c - 3):c + 4].ravel(); blk = blk[blk > 0]
    adm, ctry = A1[np.bincount(blk).argmax() - 1] if blk.size else ("", "")
    if not ctry:
        cb = cid[max(0, r - 6):r + 7, max(0, c - 6):c + 7].ravel(); cb = cb[cb > 0]
        ctry = CL[np.bincount(cb).argmax() - 1]["name"] if cb.size else ""
    best = min(PP, key=lambda p: hav(lat, lon, p["latitude"], p["longitude"]))
    return dict(admin1=adm, country=ctry, near=best["name"], near_km=round(hav(lat, lon, best["latitude"], best["longitude"])))


def wmean(x, w):
    m = np.isfinite(x)
    return float((x[m] * w[m]).sum() / w[m].sum())


# ---------- land winds ----------
S["meta"] = dict(wc_cells=int(valid.sum()), wc_dropped=int(np.load(f"{WORK}/dropped.npy")[0]), wc_period="1970 to 2000")
S["land"] = dict(mean=wmean(ann[LANDX], W2[LANDX]), mean_incl_ant=wmean(ann[valid], W2[valid]),
                 median=float(np.median(ann[LANDX])))
for t in (4, 5, 6):
    S["land"][f"share_ge{t}"] = float(W2[LANDX & (ann >= t)].sum() / W2[LANDX].sum())
S["land"]["share_lt2"] = float(W2[LANDX & (ann < 2)].sum() / W2[LANDX].sum())
nh = valid & (LAT[:, None] > 0); sh = LANDX & (LAT[:, None] < 0)
S["land"]["nh_month"] = [wmean(wc[m][nh], W2[nh]) for m in range(12)]
S["land"]["sh_month"] = [wmean(wc[m][sh], W2[sh]) for m in range(12)]
S["land"]["nh_windiest_month"] = MONTHS[int(np.argmax(S["land"]["nh_month"]))]
S["land"]["nh_calmest_month"] = MONTHS[int(np.argmin(S["land"]["nh_month"]))]
S["land"]["sh_windiest_month"] = MONTHS[int(np.argmax(S["land"]["sh_month"]))]
S["land"]["sh_calmest_month"] = MONTHS[int(np.argmin(S["land"]["sh_month"]))]
ant = valid & ~notant
r, c = np.unravel_index(np.nanargmax(np.where(ant, ann, np.nan)), ann.shape)
S["antarctica"] = dict(max=float(ann[r, c]), lat=round(float(LAT[r]), 2), lon=round(float(LON[c]), 2), mean=wmean(ann[ant], W2[ant]))

# windiest places: local peaks at least 500 km apart, outside Antarctica
order = np.argsort(np.where(LANDX, ann, -1).ravel())[::-1][:20000]
peaks = []
for i in order:
    r, c = divmod(int(i), NX)
    la, lo = float(LAT[r]), float(LON[c])
    if all(hav(la, lo, p["lat"], p["lon"]) >= 500 for p in peaks):
        peaks.append(dict(lat=round(la, 3), lon=round(lo, 3), wind=round(float(ann[r, c]), 2),
                          windiest_month=MONTHS[int(np.argmax(wc[:, r, c]))], calmest_month=MONTHS[int(np.argmin(wc[:, r, c]))],
                          months=[round(float(x), 2) for x in wc[:, r, c]], **place_name(la, lo)))
    if len(peaks) >= 20:
        break
S["windiest_places"] = peaks
pd.DataFrame([{k: v for k, v in p.items() if k != "months"} | {MON3[m]: p["months"][m] for m in range(12)} for p in peaks]).to_csv(f"{DATA}/windiest_places.csv", index=False)

# cities of a million or more
cities = []
for p in PP:
    if (p.get("pop_max") or 0) >= 1_000_000:
        v, how = near_val(wc, p["latitude"], p["longitude"], k=2)
        if how == "sea":
            continue
        cities.append(dict(name=p["name"], country=p["adm0name"], lat=round(p["latitude"], 3), lon=round(p["longitude"], 3), pop=int(p["pop_max"]),
                           wind=round(float(np.mean(v)), 2), ratio=round(float(np.max(v) / np.min(v)), 2), windiest_month=MONTHS[int(np.argmax(v))],
                           months=[round(float(x), 2) for x in v]))
cities.sort(key=lambda d: -d["wind"])
S["cities_n"] = len(cities)
S["cities_windiest"] = cities[:12]
S["cities_calmest"] = cities[::-1][:10]
S["city"] = {c["name"]: c for c in cities if c["name"] in ("London", "Chicago", "Wellington", "Beijing", "Delhi", "Paris", "New York", "Sydney", "Moscow", "Lagos", "Manchester", "Birmingham", "Glasgow", "Dublin", "Buenos Aires", "Karachi")}
pd.DataFrame([{k: v for k, v in c.items() if k != "months"} | {MON3[m]: c["months"][m] for m in range(12)} for c in cities]).to_csv(f"{DATA}/cities.csv", index=False)

# ---------- seasonality: windiest month / calmest month ----------
with np.errstate(invalid="ignore", divide="ignore"):
    mx = np.nanmax(np.where(valid, wc, -1), axis=0); mn = np.nanmin(np.where(valid, wc, 99), axis=0)
    ratio = np.where(valid, mx / np.maximum(mn, 1e-3), np.nan).astype(np.float32)
# a few cells carry a single impossible month (WorldClim station artefacts, e.g. 0.1 m/s in February between 3.1 and 2.1):
# flag a month below 0.35 times, or above 2.5 times, the mean of the months either side, and leave those cells out
nb = (np.roll(wc, 1, axis=0) + np.roll(wc, -1, axis=0)) / 2
with np.errstate(invalid="ignore"):
    spike = valid & ((wc < 0.35 * nb) | (wc > 2.5 * nb)).any(axis=0)
del nb
S["meta"]["spike_cells"] = int(spike.sum())
SEAS = LANDX & (ann >= 1.5) & ~spike    # seasonality only where the mean wind is at least 1.5 m/s
ratio[spike] = np.nan
amax = np.argmax(np.where(valid, wc, -1), axis=0).astype(np.uint8)
np.save(f"{WORK}/ratio.npy", ratio); np.save(f"{WORK}/spike.npy", spike); np.save(f"{WORK}/argmax.npy", amax); np.save(f"{WORK}/ann.npy", ann)
S["seas"] = dict(median=float(np.median(ratio[SEAS])), share_ge2=float(W2[SEAS & (ratio >= 2)].sum() / W2[SEAS].sum()),
                 share_lt13=float(W2[SEAS & (ratio < 1.3)].sum() / W2[SEAS].sum()), land_share_counted=float(W2[SEAS].sum() / W2[LANDX].sum()))
for name, msk in (("nh", SEAS & (LAT[:, None] > 23.5)), ("sh", SEAS & (LAT[:, None] < -23.5))):
    sh_m = [float(W2[msk & (amax == m)].sum() / W2[msk].sum()) for m in range(12)]
    S["seas"][f"{name}_windiest_month_share"] = sh_m
    S["seas"][f"{name}_winter_share"] = sum(sh_m[m] for m in ((11, 0, 1, 2) if name == "nh" else (5, 6, 7, 8)))
order = np.argsort(np.where(SEAS, ratio, -1).ravel())[::-1][:40000]
speaks = []
for i in order:
    r, c = divmod(int(i), NX)
    la, lo = float(LAT[r]), float(LON[c])
    if all(hav(la, lo, p["lat"], p["lon"]) >= 700 for p in speaks):
        speaks.append(dict(lat=round(la, 3), lon=round(lo, 3), ratio=round(float(ratio[r, c]), 2), wind=round(float(ann[r, c]), 2),
                           windiest_month=MONTHS[int(np.argmax(wc[:, r, c]))], calmest_month=MONTHS[int(np.argmin(wc[:, r, c]))],
                           max=round(float(wc[:, r, c].max()), 2), min=round(float(wc[:, r, c].min()), 2),
                           months=[round(float(x), 2) for x in wc[:, r, c]], **place_name(la, lo)))
    if len(speaks) >= 12:
        break
S["seasonal_places"] = speaks
pd.DataFrame([{k: v for k, v in p.items() if k != "months"} | {MON3[m]: p["months"][m] for m in range(12)} for p in speaks]).to_csv(f"{DATA}/most_seasonal_places.csv", index=False)

# ---------- countries: land wind ----------
# overseas parts left out of a country's land average (they hold none of the listed farms)
def keep_mask(a3):
    m = np.ones((NY, NX), bool)
    la, lo = LAT[:, None], LON[None, :]
    if a3 == "USA": m = (lo > -129) & (la < 50)                                  # conterminous states only
    if a3 == "FRA": m = (lo > -6) & (lo < 10) & (la > 41) & (la < 52)               # metropolitan France
    if a3 == "NOR": m = la < 72                                                    # without Svalbard and Jan Mayen
    if a3 == "NLD": m = la > 50                                                    # European Netherlands
    if a3 == "DNK": m = la < 60                                                    # without the Faroes
    if a3 == "GBR": m = la > 49                                                    # without overseas territories
    if a3 == "AUS": m = (lo > 110) & (lo < 155)
    if a3 == "NZL": m = la > -48
    if a3 == "CHL": m = lo > -80
    if a3 == "ECU": m = lo > -85
    if a3 == "ESP": m = la > 27
    return np.broadcast_to(m, (NY, NX))


A3IDX = {c["a3"]: i + 1 for i, c in enumerate(CL)}
ISO2A3 = {}
for i, c in enumerate(CL):
    ISO2A3.setdefault(c["iso3"], c["a3"]); ISO2A3.setdefault(c["a3"], c["a3"])
ctry = {}
for a3, idx in A3IDX.items():
    m = (cid == idx) & valid
    if a3 in ("USA", "FRA", "NOR", "NLD", "DNK", "GBR", "AUS", "NZL", "CHL", "ECU", "ESP"):
        m = m & keep_mask(a3)
    if m.sum() < 3:
        continue
    v = ann[m]; w = W2[m]; o = np.argsort(v)
    cm = [wmean(wc[k][m], w) for k in range(12)]
    ctry[a3] = dict(a3=a3, name=CL[idx - 1]["name"], cells=int(m.sum()), area_km2=float(w.sum() * (111.32 * CELL) ** 2), land_mean=wmean(v, w), months=cm,
                    windiest_month=MONTHS[int(np.argmax(cm))], calmest_month=MONTHS[int(np.argmin(cm))], ratio=max(cm) / min(cm),
                    _v=v[o], _cw=np.cumsum(w[o]) / w.sum(), p75=float(v[o][np.searchsorted(np.cumsum(w[o]) / w.sum(), .75)]))


def pctile(a3, x):
    d = ctry[a3]; i = np.searchsorted(d["_v"], x)
    return float(d["_cw"][i - 1]) if i > 0 else 0.0


# ---------- wind farms ----------
g = pd.read_csv(GPPD, low_memory=False)
f = g[g.primary_fuel == "Wind"].copy()
rows = []
for _, r in f.iterrows():
    v, how = near_val(wc, r.latitude, r.longitude, k=1)
    rr, cc = rc(r.latitude, r.longitude)
    a3 = ISO2A3.get(r.country, r.country)
    w = float(np.mean(v)) if how != "sea" else None
    p = pctile(a3, w) if (how == "land" and a3 in ctry) else None
    rows.append(dict(name=r["name"], country=r.country, country_name=r.country_long, a3=a3, capacity_mw=float(r.capacity_mw), lat=float(r.latitude), lon=float(r.longitude),
                     year=None if pd.isna(r.commissioning_year) else int(r.commissioning_year), site=how,
                     wind=None if w is None else round(w, 2), country_pctile=None if p is None else round(p, 4),
                     admin1=A1[a1[rr, cc] - 1][0] if a1[rr, cc] > 0 else "", source=r.source))
F = pd.DataFrame(rows)
F.drop(columns=["a3"]).to_csv(f"{DATA}/wind_farms.csv", index=False)
F.to_pickle(f"{WORK}/farms.pkl")
L = F[F.site == "land"]
S["farms"] = dict(n=len(F), cap_gw=F.capacity_mw.sum() / 1000, n_countries=int(F.country.nunique()),
                  n_land=len(L), cap_land_gw=L.capacity_mw.sum() / 1000, cap_coast_gw=F[F.site == "coast"].capacity_mw.sum() / 1000,
                  cap_sea_gw=F[F.site == "sea"].capacity_mw.sum() / 1000, n_sea=int((F.site == "sea").sum()),
                  year_share=float(F.year.notna().mean()), year_max=int(F.year.max()), year_min=int(F.year.min()),
                  land_cw_wind=float((L.wind * L.capacity_mw).sum() / L.capacity_mw.sum()),
                  land_cw_pctile=float((L.country_pctile * L.capacity_mw).sum() / L.capacity_mw.sum()),
                  share_cap_above_median=float(L.capacity_mw[L.country_pctile > .5].sum() / L.capacity_mw.sum()),
                  share_cap_top_quarter=float(L.capacity_mw[L.country_pctile > .75].sum() / L.capacity_mw.sum()),
                  share_cap_bottom_half=float(L.capacity_mw[L.country_pctile <= .5].sum() / L.capacity_mw.sum()))
top = F.groupby("country_name").capacity_mw.sum().sort_values(ascending=False)
S["farms"]["top_countries"] = [dict(name=k, cap_gw=v / 1000) for k, v in top.head(6).items()]
S["farms"]["top3_share"] = float(top.head(3).sum() / top.sum())
ly = L[L.year.notna()]
S["farms"]["pctile_pre2010"] = float((ly.country_pctile * ly.capacity_mw)[ly.year < 2010].sum() / ly.capacity_mw[ly.year < 2010].sum())
S["farms"]["pctile_2010on"] = float((ly.country_pctile * ly.capacity_mw)[ly.year >= 2010].sum() / ly.capacity_mw[ly.year >= 2010].sum())
S["farms"]["n_pre2010"] = int((ly.year < 2010).sum()); S["farms"]["n_2010on"] = int((ly.year >= 2010).sum())

crow = []
for a3, grp in F.groupby("a3"):
    if a3 not in ctry:
        continue
    lg = grp[grp.site == "land"]
    d = ctry[a3]
    e = dict(a3=a3, name=d["name"], farms=len(grp), cap_mw=float(grp.capacity_mw.sum()), land_farms=len(lg), land_cap_mw=float(lg.capacity_mw.sum()),
             sea_cap_mw=float(grp.capacity_mw[grp.site == "sea"].sum()), coast_cap_mw=float(grp.capacity_mw[grp.site == "coast"].sum()),
             land_mean=d["land_mean"], p75=d["p75"])
    if len(lg):
        e["farm_cw_wind"] = float((lg.wind * lg.capacity_mw).sum() / lg.capacity_mw.sum())
        e["farm_cw_pctile"] = float((lg.country_pctile * lg.capacity_mw).sum() / lg.capacity_mw.sum())
        e["farm_ratio"] = e["farm_cw_wind"] / d["land_mean"]
        e["share_top_quarter"] = float(lg.capacity_mw[lg.country_pctile > .75].sum() / lg.capacity_mw.sum())
    crow.append(e)
C = pd.DataFrame(crow).sort_values("cap_mw", ascending=False)
BIG = C[(C.land_cap_mw >= 400) & (C.land_farms >= 8)].copy()
S["farm_countries_n"] = len(BIG)
S["farm_countries_windier"] = int((BIG.farm_ratio > 1).sum())
S["farm_countries"] = BIG[["a3", "name", "farms", "cap_mw", "land_farms", "land_cap_mw", "sea_cap_mw", "land_mean", "farm_cw_wind", "farm_ratio", "farm_cw_pctile", "share_top_quarter"]].to_dict("records")
S["fc"] = {r["a3"]: r for r in S["farm_countries"]}
for a3 in ("DEU",):
    r = C[C.a3 == a3].iloc[0].to_dict(); S["fc_" + a3] = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in r.items()}
# countries table
out = []
for a3, d in ctry.items():
    row = dict(a3=a3, country=d["name"], land_km2=round(d["area_km2"]), land_mean_ms=round(d["land_mean"], 3), windiest_month=d["windiest_month"], calmest_month=d["calmest_month"],
               month_ratio=round(d["ratio"], 3), **{f"{MON3[m]}_ms": round(d["months"][m], 3) for m in range(12)})
    cc = C[C.a3 == a3]
    if len(cc):
        x = cc.iloc[0]
        row.update(wind_farms=int(x.farms), wind_capacity_mw=round(x.cap_mw, 1), land_farms=int(x.land_farms), land_capacity_mw=round(x.land_cap_mw, 1),
                   farm_cw_wind_ms=round(x.farm_cw_wind, 3) if pd.notna(x.get("farm_cw_wind")) else None,
                   farm_cw_pctile=round(x.farm_cw_pctile, 4) if pd.notna(x.get("farm_cw_pctile")) else None)
    out.append(row)
pd.DataFrame(out).sort_values("land_mean_ms", ascending=False).to_csv(f"{DATA}/countries.csv", index=False)
big_ctry = sorted([d for d in ctry.values() if d["area_km2"] >= 50000 and d["a3"] != "ATA"], key=lambda d: -d["land_mean"])  # 50,000 km2 or more
S["ctry_windiest"] = [dict(a3=d["a3"], name=d["name"], wind=d["land_mean"]) for d in big_ctry[:8]]
S["ctry_calmest"] = [dict(a3=d["a3"], name=d["name"], wind=d["land_mean"]) for d in big_ctry[::-1][:8]]
S["ctry"] = {a3: dict(name=d["name"], wind=d["land_mean"], ratio=d["ratio"], windiest_month=d["windiest_month"], calmest_month=d["calmest_month"], months=d["months"])
             for a3, d in ctry.items() if a3 in ("GBR", "IRL", "USA", "CHN", "DEU", "IND", "BRA", "ESP", "FRA", "AUS", "CAN", "ISL", "NZL", "ARG", "DNK", "SOM", "NLD", "FLK", "KEN", "COD")}

# ---------- NCEP: the circulation ----------
z = np.load(f"{WORK}/ncep.npz")
U, V, SP, nlat, nlon = z["u"], z["v"], z["s"], z["lat"], z["lon"]
S["meta"]["ncep_period"] = f"{int(z['y0'])} to {int(z['y1'])}"
Ua, Va, Sa = U.mean(0), V.mean(0), SP.mean(0)
# land fraction of each 2.5 degree cell from the WorldClim mask (plus Antarctica)
ri = np.clip(np.round((90 - LAT) / 2.5).astype(int), 0, 72); ci = np.round(((LON % 360) / 2.5)).astype(int) % 144
idx = (ri[:, None] * 144 + ci[None, :]).ravel()
wl = W2.ravel()
landf = (np.bincount(idx, weights=wl * valid.ravel(), minlength=73 * 144) / np.maximum(np.bincount(idx, weights=wl, minlength=73 * 144), 1e-9)).reshape(73, 144)
np.save(f"{WORK}/ncep_landf.npy", landf)
OCE = landf < 0.1
cw = np.cos(np.radians(nlat))[:, None] * np.ones((1, 144))


def belt(arr, lo, hi, mask=OCE):
    m = mask & (nlat[:, None] >= lo) & (nlat[:, None] <= hi)
    return float((arr * cw)[m].sum() / cw[m].sum())


steady = np.hypot(Ua, Va) / Sa
S["circ"] = dict(
    trade_n_u=belt(Ua, 7.5, 22.5), trade_s_u=belt(Ua, -22.5, -7.5), trade_n_v=belt(Va, 7.5, 22.5), trade_s_v=belt(Va, -22.5, -7.5),
    trade_n_speed=belt(Sa, 7.5, 22.5), trade_s_speed=belt(Sa, -22.5, -7.5),
    trade_steady=(belt(steady, 7.5, 22.5) + belt(steady, -22.5, -7.5)) / 2,
    west_n_u=belt(Ua, 40, 55), west_s_u=belt(Ua, -55, -40), west_steady_s=belt(steady, -55, -40), west_steady_n=belt(steady, 40, 55),
    roar_s=belt(Sa, -50, -40), roar_n=belt(Sa, 40, 50), fifties_s=belt(Sa, -60, -50.01),
    ocean_mean=belt(Sa, -60, 60), land_mean_ncep=belt(Sa, -60, 75, mask=landf > .9))
for mm in (0, 6):
    S["circ"][f"roar_s_{MON3[mm]}"] = belt(SP[mm], -50, -40); S["circ"][f"roar_n_{MON3[mm]}"] = belt(SP[mm], 40, 50)
zon = []
for j, la in enumerate(nlat):
    m = OCE[j]
    zon.append(dict(lat=float(la), u=float(Ua[j][m].mean()) if m.any() else None, v=float(Va[j][m].mean()) if m.any() else None,
                    speed=float(Sa[j][m].mean()) if m.any() else None, u_all=float(Ua[j].mean()), speed_all=float(Sa[j].mean()),
                    u_jan=float(U[0, j][m].mean()) if m.any() else None, u_jul=float(U[6, j][m].mean()) if m.any() else None,
                    ocean_share=float(m.mean())))
pd.DataFrame(zon).round(3).to_csv(f"{DATA}/zonal_winds.csv", index=False)
S["zonal"] = zon
sz = [(z_["speed"], z_["lat"]) for z_ in zon if z_["speed"] is not None and z_["lat"] < 0 and z_["ocean_share"] > .8]
S["circ"]["sh_max_speed"], S["circ"]["sh_max_lat"] = max(sz)
j, i = np.unravel_index(np.argmax(np.where(OCE, Sa, -1)), Sa.shape)
S["circ"]["ocean_max"] = dict(speed=float(Sa[j, i]), lat=float(nlat[j]), lon=float(nlon[i] if nlon[i] <= 180 else nlon[i] - 360))


def box(arr, la0, la1, lo0, lo1):
    m = (nlat[:, None] >= la0) & (nlat[:, None] <= la1) & (nlon[None, :] >= lo0) & (nlon[None, :] <= lo1) & OCE
    return float((arr * cw)[m].sum() / cw[m].sum())


def vec(mm, la0, la1, lo0, lo1):
    u, v = box(U[mm], la0, la1, lo0, lo1), box(V[mm], la0, la1, lo0, lo1)
    frm = (math.degrees(math.atan2(-u, -v)) + 360) % 360
    return dict(u=u, v=v, vec=math.hypot(u, v), speed=box(SP[mm], la0, la1, lo0, lo1), from_deg=frm, from_pt=compass(frm))


S["monsoon"] = dict(arabian_jan=vec(0, 7.5, 17.5, 55, 70), arabian_jul=vec(6, 7.5, 17.5, 55, 70),
                    bengal_jan=vec(0, 10, 17.5, 82.5, 92.5), bengal_jul=vec(6, 10, 17.5, 82.5, 92.5),
                    somali_jul=vec(6, 5, 12.5, 50, 57.5))
ang = np.degrees(np.arccos(np.clip((U[0] * U[6] + V[0] * V[6]) / np.maximum(np.hypot(U[0], V[0]) * np.hypot(U[6], V[6]), 1e-6), -1, 1)))
rev = (ang >= 135) & (np.hypot(U[0], V[0]) >= 2) & (np.hypot(U[6], V[6]) >= 2) & (np.abs(nlat[:, None]) <= 60)
np.save(f"{WORK}/reversal.npy", rev)
tropics = np.abs(nlat[:, None]) <= 60
S["monsoon"]["reversal_share"] = float((cw * rev).sum() / (cw * tropics).sum())
S["monsoon"]["reversal_cells"] = int(rev.sum())
# check NCEP against WorldClim over solid land
fine = np.bincount(idx, weights=np.nan_to_num(ann).ravel() * wl * valid.ravel(), minlength=73 * 144) / np.maximum(np.bincount(idx, weights=wl * valid.ravel(), minlength=73 * 144), 1e-9)
fine = fine.reshape(73, 144)
m = (landf >= .9) & (nlat[:, None] >= -60) & (nlat[:, None] <= 75)
S["check"] = dict(n=int(m.sum()), r=float(np.corrcoef(Sa[m], fine[m])[0, 1]), ratio_median=float(np.median(Sa[m] / fine[m])))

# ---------- UK and Ireland ----------
u = np.load(f"{WORK}/uk_county.npz")
ucid, unames, unat = u["cid"], u["names"], u["nations"]
H, Wd = ucid.shape
flat = 61 - (np.arange(H) + .5) / 60; flon = -11 + (np.arange(Wd) + .5) / 60
pr = ((90 - flat) / CELL).astype(int); pc = ((flon + 180) / CELL).astype(int)
fa = ann[pr][:, pc]; fm = wc[:, pr][:, :, pc]
fw = np.cos(np.radians(flat))[:, None] * np.ones((1, Wd))
cty = []
for k, nm in enumerate(unames):
    mk = (ucid == k + 1) & np.isfinite(fa)
    if mk.sum() == 0:
        continue
    months = [float((fm[mm][mk] * fw[mk]).sum() / fw[mk].sum()) for mm in range(12)]
    jj = np.argmax(np.where(mk, fa, -1)); r0, c0 = np.unravel_index(jj, fa.shape)
    cty.append(dict(county=str(nm), nation=str(unat[k]), wind=float((fa[mk] * fw[mk]).sum() / fw[mk].sum()), max=float(fa[r0, c0]),
                    max_lat=round(float(flat[r0]), 3), max_lon=round(float(flon[c0]), 3), ratio=max(months) / min(months),
                    windiest_month=MONTHS[int(np.argmax(months))], calmest_month=MONTHS[int(np.argmin(months))], months=months))
cty.sort(key=lambda d: -d["wind"])
S["uk_counties"] = [dict(county=d["county"], nation=d["nation"], wind=d["wind"]) for d in cty]
S["uk_county_n"] = len(cty)
S["uk_county"] = {d["county"]: d for d in cty}
pd.DataFrame([{k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items() if k != "months"} | {f"{MON3[m]}_ms": round(d["months"][m], 3) for m in range(12)} for d in cty]).to_csv(f"{DATA}/uk_counties.csv", index=False)
ukm = (ucid > 0) & np.isfinite(fa)
ukmonths = [float((fm[mm][ukm] * fw[ukm]).sum() / fw[ukm].sum()) for mm in range(12)]
S["uk"] = dict(mean=float((fa[ukm] * fw[ukm]).sum() / fw[ukm].sum()), months=ukmonths, windiest_month=MONTHS[int(np.argmax(ukmonths))],
               calmest_month=MONTHS[int(np.argmin(ukmonths))], ratio=max(ukmonths) / min(ukmonths))
for nat in ("England", "Scotland", "Wales", "Northern Ireland"):
    ids = [k + 1 for k in range(len(unames)) if unat[k] == nat]
    mk = np.isin(ucid, ids) & np.isfinite(fa)
    S["uk"][nat] = float((fa[mk] * fw[mk]).sum() / fw[mk].sum())
jj = np.argmax(np.where(ukm, fa, -1)); r0, c0 = np.unravel_index(jj, fa.shape)
S["uk"]["max"] = dict(wind=float(fa[r0, c0]), lat=float(flat[r0]), lon=float(flon[c0]), county=str(unames[ucid[r0, c0] - 1]))
S["uk"]["share_ge5"] = float(fw[ukm & (fa >= 5)].sum() / fw[ukm].sum())
uf = F[F.country == "GBR"]
ul = uf[uf.site == "land"]
fr = ((61 - ul.lat) * 60).astype(int).clip(0, H - 1); fc_ = ((ul.lon + 11) * 60).astype(int).clip(0, Wd - 1)
ul = ul.assign(county=[str(unames[ucid[a, b] - 1]) if ucid[a, b] > 0 else "" for a, b in zip(fr, fc_)])
bycty = ul.groupby("county").capacity_mw.sum().sort_values(ascending=False)
S["uk_farms"] = dict(n=len(uf), cap_gw=uf.capacity_mw.sum() / 1000, n_land=len(ul), cap_land_gw=ul.capacity_mw.sum() / 1000,
                     cap_sea_gw=uf.capacity_mw[uf.site == "sea"].sum() / 1000, cap_coast_gw=uf.capacity_mw[uf.site == "coast"].sum() / 1000,
                     n_sea=int((uf.site == "sea").sum()),
                     scot_share_land=float(ul.capacity_mw[ul.county.isin([str(unames[k]) for k in range(len(unames)) if unat[k] == "Scotland"])].sum() / ul.capacity_mw.sum()),
                     top_counties=[dict(county=k, cap_mw=float(v)) for k, v in bycty.head(5).items()])
big = uf.sort_values("capacity_mw", ascending=False).head(3)
S["uk_farms"]["largest"] = [dict(name=r["name"], cap_mw=float(r.capacity_mw), site=r.site) for _, r in big.iterrows()]
S["ireland"] = dict(mean=ctry["IRL"]["land_mean"])
jsave(S, f"{WORK}/stats.json")
print("stats written")
