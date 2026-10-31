"""Step 5. Build index.html from code/page_template.html, code/page_text.html and code/page_charts.js. Every number in
the text is a {{path|format}} token filled from data/results.json; facts stated in words are checked by the asserts below.
The placeholders {{DOI}}, {{DOI_URL}} and https://blog.tristanhotham.com/2026/10/31/wind-map/ are left for the publisher to fill.
Run: python3 code/05_build_site.py
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
WORK = os.environ.get("WIND_WORK", "/dev/shm/wind-map")
PLACEHOLDERS = {"DOI", "DOI_URL", "BLOG_URL"}


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "pct": return f"{round(v * 100)}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "abs1": return f"{abs(v):.1f}"
    raise ValueError(f)


def sub(m):
    if m.group(1).strip() in PLACEHOLDERS:
        return m.group(0)
    return fmt(get(m.group(1).strip()), m.group(3))


# ---- facts stated in words (page, paper, blog, collage) ----
c, mo = R["circ"], R["monsoon"]
assert c["trade_n_u"] < 0 and c["trade_n_v"] < 0 and c["trade_s_u"] < 0 and c["trade_s_v"] > 0      # NE and SE trades
assert c["west_n_u"] > 0 and c["west_s_u"] > c["west_n_u"] and c["roar_s"] > c["roar_n"]
assert c["roar_n_Jan"] > c["roar_s_Jan"] and c["roar_s_Jul"] > c["roar_n_Jul"] and c["west_steady_n"] < c["trade_steady"]
assert c["sh_max_lat"] == -52.5 and 80 <= c["ocean_max"]["lon"] <= 95 and c["ocean_max"]["lat"] <= -45
assert mo["arabian_jan"]["from_pt"] == "north-east" and mo["arabian_jul"]["from_pt"] == "south-west"
assert mo["bengal_jan"]["from_pt"] == "north-east" and mo["bengal_jul"]["from_pt"] == "south-west"
assert R["windiest_places"][0]["label"] == "Vatnajökull ice cap" and [p["label"] for p in R["windiest_places"][1:4]] == ["Jan Mayen", "East Greenland ice sheet", "Southern Patagonian Ice Field"]
assert R["ctry_windiest"][0]["name"] == "Iceland" and [d["a3"] for d in R["ctry_windiest"][:4]] == ["ISL", "GRL", "SAH", "GBR"] and R["ctry_calmest"][0]["a3"] == "COG"
assert R["antarctica"]["max"] > R["windiest_places"][0]["wind"]
assert [x["name"] for x in R["cities_windiest"][:5]] == ["Marseille", "The Hague", "Melbourne", "Auckland", "Adelaide"]
assert [x["name"] for x in R["cities_calmest"][:5]] == ["Bogota", "Cali", "Srinagar", "Medellín", "Mandalay"]
assert R["land"]["nh_windiest_month"] == "April" and R["land"]["nh_calmest_month"] == "August" and R["land"]["sh_windiest_month"] == "October" and R["land"]["sh_calmest_month"] == "May"
assert R["derived"]["nh_spring_share"] > .5
sp = [p["label"] for p in R["seasonal_places"]]
assert {"Kutch, Gujarat", "Odisha coast", "Southern Maldives", "Chagos Archipelago", "Sistan, Farah province", "Watson Lake, Yukon"} <= set(sp) and sp[0].startswith("Kolyma")
assert 0.24 < R["land"]["share_lt2"] < 0.26     # "a quarter"
fc = R["fc"]
assert fc["MEX"]["farm_cw_pctile"] == max(r["farm_cw_pctile"] for r in R["farm_countries"])
assert fc["CHL"]["farm_ratio"] < 1 and fc["GBR"]["farm_ratio"] < 1.1 and fc["BRA"]["farm_ratio"] > 1.5
assert [r["a3"] for r in R["farm_countries"]][:3] == ["USA", "CHN", "GBR"] and R["fc_DEU"]["land_farms"] < 20
uk = R["uk_counties"]
assert [d["county"] for d in uk[:5]] == ["Shetland Islands", "Na h-Eileanan Siar", "Orkney Islands", "Argyll and Bute", "North Ayrshire"]
assert [d["county"] for d in uk if d["nation"] == "England"][:3] == ["Cornwall", "Cumbria", "East Riding of Yorkshire"]
assert [d["county"] for d in uk[-3:]] == ["Worcestershire", "Shropshire", "Herefordshire"]
assert R["uk"]["Scotland"] == max(R["uk"][n] for n in ("England", "Scotland", "Wales", "Northern Ireland"))
assert R["uk"]["windiest_month"] == "January" and R["uk"]["calmest_month"] == "August" and R["uk"]["max"]["label"] == "St Kilda"
assert R["uk_farms"]["largest"][0]["name"].startswith("Hornsea 1") and [d["county"] for d in R["uk_farms"]["top_counties"][:3]] == ["Highland", "Northern Ireland", "South Lanarkshire"]
assert R["meta"]["ncep_period"] == "1991 to 2020"

TOK = re.compile(r"\{\{([^}|]+)(\|(\w+))?\}\}")


def check_text(html):
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    return vis


if __name__ == "__main__":
    tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    txt = open(os.path.join(HERE, "page_text.html"), encoding="utf-8").read()
    parts = dict(re.findall(r"<!--@(\w+)-->(.*?)<!--@end-->", txt, flags=re.S))
    for k in ("INTRO", "BODY"):
        tpl = tpl.replace(f"/*{k}*/", parts[k].strip())
    tpl = tpl.replace("/*CHARTS*/", open(os.path.join(HERE, "page_charts.js"), encoding="utf-8").read())
    tpl = tpl.replace("/*FULLSCREEN*/", open(os.path.join(HERE, "fullscreen_snippet.html"), encoding="utf-8").read().strip())
    html = TOK.sub(sub, tpl)
    html = html.replace("/*PD*/", json.dumps(json.load(open(os.path.join(WORK, "page_data.json"))), ensure_ascii=False, separators=(",", ":")))
    left = set(re.findall(r"\{\{(\w+)\}\}", html))
    assert left <= PLACEHOLDERS and "{{" not in re.sub(r"\{\{(DOI|DOI_URL|BLOG_URL)\}\}", "", html), left
    check_text(html)
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()), "bytes")
