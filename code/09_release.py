"""Step 9. Blog post (release/blog/post.html from code/blog_template.html) and release/blog/meta.json, the Zenodo folder
(paper PDF, key CSVs, results.json, a code-and-data zip and metadata.json) and README.md.
Image placeholders {{IMG|file|alt|caption}} and the links {{DOI}}, {{DOI_URL}} and https://blog.tristanhotham.com/2026/10/31/wind-map/ are left for the publisher.
Run: python3 code/09_release.py
"""
import importlib.util, json, os, re, shutil, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "05_build_site.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
R = b.R
NAME = "Hotham_Where_the_Wind_Blows"
DASH = ("—", "–", "--")
TOK = re.compile(r"\{\{(?!IMG\|)([^{}|]+)(\|(\w+))?\}\}")
for k in ("NOR", "AUS", "BRA", "MEX"):
    assert R["fc"][k]["farm_cw_pctile"] >= R["fc"]["NOR"]["farm_cw_pctile"]
assert all(.4 < R["fc"][k]["farm_cw_pctile"] < .5 for k in ("IRL", "MAR", "SWE"))
assert R["cities_calmest"][4]["wind"] < 1.0

# blog
t = open(os.path.join(HERE, "blog_template.html"), encoding="utf-8").read()
t = TOK.sub(b.sub, t)
left = set(re.findall(r"\{\{(\w+)\}\}", t))
assert left <= b.PLACEHOLDERS, left
vis = re.sub(r"<!--.*?-->", "", t, flags=re.S)
for bad in DASH + ("DSIT", "DCMS", "civil serv"): assert bad not in vis, bad
BL = os.path.join(ROOT, "release", "blog"); os.makedirs(BL, exist_ok=True)
open(os.path.join(BL, "post.html"), "w", encoding="utf-8").write(t)
imgs = re.findall(r"\{\{IMG\|([^|]+)\|", t)
for m in imgs: assert os.path.exists(os.path.join(BL, m)), m
assert 5 <= len(imgs) <= 8, len(imgs)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = dict(
    title="Where the wind blows: the world's winds, and are wind farms in the windy places?",
    slug="wind-map",
    excerpt=(f"I mapped the world's winds month by month, from the trade winds to the Roaring Forties and the monsoon, and set {R['farms']['n']:,} wind farms "
             f"against the wind at their sites. {round(R['farms']['share_cap_above_median'] * 100)}% of onshore capacity stands on ground windier than its country's median."),
    seo_description="A month by month map of the world's winds, the windiest places on land, the UK at 9 km, and whether wind farms stand where the wind blows.",
    tags=["wind", "climate", "weather", "wind farms", "renewable energy", "maps", "data visualisation", "monsoon"],
    header_alt=("Title card reading 'Where the wind blows' in navy on pale paper, with a line saying "
                f"{round(R['farms']['share_cap_above_median'] * 100)}% of onshore wind farm capacity sits on ground windier than its country's median. "
                "Below, a world map of mean wind speed: pale green land in the tropics, deeper blue over windy plains and coasts, faded pink and violet oceans "
                "crossed by dark streamlines of the trade winds and the westerlies racing round the Southern Ocean."))
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
for v in meta.values():
    for bad in DASH: assert bad not in str(v)
json.dump(meta, open(os.path.join(BL, "meta.json"), "w"), indent=2, ensure_ascii=False)

# README
rd = open(os.path.join(HERE, "readme_template.md"), encoding="utf-8").read()
rd = TOK.sub(b.sub, rd)
assert set(re.findall(r"\{\{(\w+)\}\}", rd)) <= b.PLACEHOLDERS
for bad in DASH: assert bad not in re.sub(r"(?m)^\|[-|]+\|$", "", rd), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(rd)

# Zenodo
Z = os.path.join(ROOT, "release", "zenodo"); os.makedirs(Z, exist_ok=True)
pt = open(os.path.join(ROOT, "release", "paper", NAME + ".tex"), encoding="utf-8").read()
ab = pt.split("\\begin{center}\\textbf{Abstract}\\end{center}")[1].split("\\textbf{Keywords:}")[0].strip()
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("~", " ")
assert "\\" not in ab and "$" not in ab, ab
zmeta = dict(
    title="Where the Wind Blows: The World's Winds Month by Month, Its Windiest Places, and Whether Wind Farms Stand in Them",
    upload_type="publication", publication_type="workingpaper",
    description=(f"<p>{ab}</p><p>Interactive version: <a href=\"https://maps.tristanhotham.com/wind-map/\">https://maps.tristanhotham.com/wind-map/</a>. "
                 "Data and code: <a href=\"https://github.com/Tristan-Hotham/wind-map\">https://github.com/Tristan-Hotham/wind-map</a>. Blog post: https://blog.tristanhotham.com/2026/10/31/wind-map/.</p>"
                 "<p>Text, figures, code (MIT) and derived data: CC BY 4.0, except that values derived from WorldClim 2.1 (Fick and Hijmans 2017) are shared for research "
                 "and non-commercial use under the WorldClim terms; the WorldClim grids themselves are not redistributed (the interactive map shows them as pictures in colour classes, with values from a 0.5 degree summary). NCEP/NCAR Reanalysis 1: NOAA PSL, public domain. "
                 "Wind farms: WRI Global Power Plant Database v1.3 (CC BY 4.0). Boundaries: Natural Earth (public domain) and ONS (Open Government Licence v3).</p>"),
    creators=[{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
    keywords=["wind", "wind speed", "atmospheric circulation", "trade winds", "Roaring Forties", "monsoon", "seasonality", "wind farms",
              "WorldClim", "NCEP/NCAR reanalysis", "Global Power Plant Database", "United Kingdom", "data visualisation"],
    license="cc-by-4.0", language="eng",
    related_identifiers=[
        dict(identifier="https://github.com/Tristan-Hotham/wind-map", relation="isSupplementedBy", resource_type="software"),
        dict(identifier="https://maps.tristanhotham.com/wind-map/", relation="isSupplementedBy", resource_type="other"),
        dict(identifier="10.1002/joc.5086", relation="references", scheme="doi"),
        dict(identifier="https://psl.noaa.gov/data/gridded/data.ncep.reanalysis.derived.html", relation="isDerivedFrom", resource_type="dataset"),
        dict(identifier="https://datasets.wri.org/dataset/globalpowerplantdatabase", relation="isDerivedFrom", resource_type="dataset"),
        dict(identifier="https://www.naturalearthdata.com", relation="isDerivedFrom", resource_type="dataset")])
s = json.dumps(zmeta, ensure_ascii=False)
for bad in DASH: assert bad not in s, bad
json.dump(zmeta, open(os.path.join(Z, "metadata.json"), "w"), indent=2, ensure_ascii=False)
shutil.copy(os.path.join(ROOT, "release", "paper", NAME + ".pdf"), Z)
for f in ["results.json", "countries.csv", "wind_farms.csv", "windiest_places.csv", "uk_counties.csv", "zonal_winds.csv"]:
    shutil.copy(os.path.join(ROOT, "data", f), Z)
zp = os.path.join(Z, "wind-map_code_and_data.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
    for base in ("code", "data", "reddit"):
        for dp, dn, fn in os.walk(os.path.join(ROOT, base)):
            dn[:] = [d for d in dn if d not in ("__pycache__",)]
            for f in fn:
                if f.endswith(".png") and base == "reddit": continue
                zf.write(os.path.join(dp, f), os.path.join("wind-map", os.path.relpath(os.path.join(dp, f), ROOT)))
    for f in ("README.md", "LICENSE"): zf.write(os.path.join(ROOT, f), os.path.join("wind-map", f))
print("release written; blog words", words, "images", len(imgs))
for f in sorted(os.listdir(Z)): print(" ", f, os.path.getsize(os.path.join(Z, f)))
