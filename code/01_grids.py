"""Step 1. Read the raw grids into WORK.
  wc.npy        : WorldClim 2.1 monthly mean wind speed at 10 m, 12 x 2160 x 4320 (m/s, NaN = sea or no data), 90N to 90S
  country.npy   : 5 arc minute raster of Natural Earth 1:10m countries (index into countries.json, 0 = none)
  uk_county.npz : 1 arc minute raster of UK counties over 49.8N to 61N, 11W to 2E (index into the county list)
  ncep.npz      : NCEP/NCAR Reanalysis 1 long-term monthly mean u, v and speed at sigma 0.995, 2.5 degrees
Run: python3 code/01_grids.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import numpy as np, rasterio, netCDF4
from rasterio.features import rasterize
from rasterio.transform import from_origin
from shapely.geometry import shape

wc = np.empty((12, NY, NX), np.float32)
for m in range(12):
    with rasterio.open(f"{RAW_WC}/wc2.1_5m_wind_{m + 1:02d}.tif") as r:
        a = r.read(1); assert a.shape == (NY, NX) and abs(r.transform.a - CELL) < 1e-9 and r.transform.c == -180 and r.transform.f == 90
        a[a < -1e30] = np.nan; wc[m] = a
np.save(f"{WORK}/wc.npy", wc)
print("WorldClim land cells", int(np.isfinite(wc[0]).sum()), "range", np.nanmin(wc), np.nanmax(wc))

ne = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")["features"]
cl, shapes = [], []
for i, f in enumerate(ne):
    p = f["properties"]; a3 = p["ADM0_A3"]
    cl.append({"a3": a3, "iso3": p.get("ISO_A3") if p.get("ISO_A3") not in (None, "-99") else a3, "name": p["NAME"], "long": p.get("NAME_LONG") or p["NAME"],
               "continent": p.get("CONTINENT")})
    shapes.append((f["geometry"], i + 1))
cid = rasterize(shapes, out_shape=(NY, NX), transform=from_origin(-180, 90, CELL, CELL), fill=0, dtype="int16")
np.save(f"{WORK}/country.npy", cid)
# land check: WorldClim cells with no Natural Earth land within one cell are dropped (a handful of isolated sea cells)
from scipy.ndimage import binary_dilation
touch = rasterize(shapes, out_shape=(NY, NX), transform=from_origin(-180, 90, CELL, CELL), fill=0, dtype="int16", all_touched=True) > 0
landok = binary_dilation(touch, iterations=1)
valid = np.isfinite(wc[0])
print("WorldClim cells dropped as not near land:", int((valid & ~landok).sum()))
wc[:, ~landok] = np.nan
np.save(f"{WORK}/wc.npy", wc)
np.save(f"{WORK}/dropped.npy", np.array([int((valid & ~landok).sum())]))
jsave(cl, f"{WORK}/countries.json")

uk = jload(f"{GEO}/counties_uk.geojson")["features"]
UKB = dict(top=61.0, left=-11.0, cell=1 / 60, w=13 * 60, h=int(11.2 * 60))
ucid = rasterize([(f["geometry"], i + 1) for i, f in enumerate(uk)], out_shape=(UKB["h"], UKB["w"]),
                 transform=from_origin(UKB["left"], UKB["top"], UKB["cell"], UKB["cell"]), fill=0, dtype="int16", all_touched=False)
np.savez_compressed(f"{WORK}/uk_county.npz", cid=ucid, names=np.array([f["properties"]["county"] for f in uk]),
                    nations=np.array([f["properties"]["nation"] for f in uk]))

out = {}
for v in ("uwnd", "vwnd", "wspd"):
    d = netCDF4.Dataset(f"{RAW_WC}/{v}.mon.ltm.nc")
    x = np.array(d.variables[v][:], dtype=np.float32); x[np.abs(x) > 1e30] = np.nan; out[v] = x
    cb = d.variables["climatology_bounds"][:]; units = d.variables["time"].units
    out["lat"] = np.array(d.variables["lat"][:]); out["lon"] = np.array(d.variables["lon"][:])
    y0 = netCDF4.num2date(cb[0][0], units).year; y1 = netCDF4.num2date(cb[-1][1], units).year
    d.close()
np.savez(f"{WORK}/ncep.npz", u=out["uwnd"], v=out["vwnd"], s=out["wspd"], lat=out["lat"], lon=out["lon"], y0=y0, y1=y1)
print("NCEP climatology", y0, "to", y1, out["uwnd"].shape)
