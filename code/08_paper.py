"""Step 8. Paper PDF: fill code/paper_template.tex from data/results.json, write release/paper/Hotham_Where_the_Wind_Blows.tex
and compile it with xelatex (figures from step 6). Set WIND_DOI (for example 10.5281/zenodo.1234567) to print the DOI;
without it the paper shows the placeholder {{DOI}}.
Run: WIND_DOI=... python3 code/08_paper.py
"""
import importlib.util, os, re, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
spec = importlib.util.spec_from_file_location("b", os.path.join(HERE, "05_build_site.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
R = b.R
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Where_the_Wind_Blows"
DOI = os.environ.get("WIND_DOI", "")
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct": return f"{v * 100:.0f}\\%"
    if f == "pct1": return f"{v * 100:.1f}\\%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "abs1": return f"{abs(v):.1f}"
    return tex(str(v))


def sub(m):
    path, _, f = m.group(1).partition("|")
    return fmt(b.get(path.strip()), f.strip() or "raw")


rows = "".join(f"{i + 1} & {tex(p['label'])} & {tex(p['label_country'])} & {p['lat']:.2f}, {p['lon']:.2f} & {p['wind']:.1f} & {p['windiest_month'][:3]} \\\\\n"
               for i, p in enumerate(R["windiest_places"]))
TP = ("\\begin{table}[tbp]\\centering\\small\\caption{The 20 windiest distinct places on land outside Antarctica: annual mean wind at 10 m (WorldClim 2.1, "
      "1970 to 2000), each at least 500 km from any windier one, with the windiest month.}\\label{tab:places}"
      "\\begin{tabular}{rllrrl}\\toprule & Place & Country or territory & Lat, lon & m/s & Peak\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
fr = "".join(f"{tex(r['name'].replace('United States of America', 'United States'))} & {r['land_farms']} & {r['land_cap_mw']:,.0f} & {r['sea_cap_mw']:,.0f} & {r['land_mean']:.2f} & {r['farm_cw_wind']:.2f} & {r['farm_cw_pctile'] * 100:.0f} & {r['share_top_quarter'] * 100:.0f}\\\\\n"
             for r in R["farm_countries"])
TF = ("\\begin{table}[tbp]\\centering\\small\\caption{Countries with at least 400 MW in 8 or more listed onshore wind farms (WRI Global Power Plant Database, 2021): "
      "onshore farms and capacity, capacity at sea, mean wind at 10 m over the land and capacity-weighted at the onshore farms (m/s), the farms' mean percentile "
      "in the country's land wind, and the share of onshore capacity in the windiest quarter of the land (\\%).}\\label{tab:farms}"
      "\\begin{tabular}{lrrrrrrr}\\toprule Country & Farms & MW land & MW sea & Land & Farms & Pctile & Top quarter\\\\\\midrule\n" + fr + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(HERE, "paper_template.tex"), encoding="utf-8").read()
link = f"\\href{{https://doi.org/{DOI}}}{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\}\\}"
t = t.replace("{{DOILINK}}", link).replace("{{TABLE_PLACES}}", TP).replace("{{TABLE_FARMS}}", TF)
t = re.sub(r"\{\{(?!TABLE_)([^{}]+?)\}\}", sub, t)
assert "{{" not in t.replace("\\{\\{DOI\\}\\}", "") and "--" not in t and "—" not in t and "–" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
if r.returncode: print(r.stdout[-3000:])
for ext in (".aux", ".log", ".out"):
    p = os.path.join(OUT, NAME + ext)
    if os.path.exists(p): os.remove(p)
print("paper written", r.returncode)
