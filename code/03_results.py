"""Step 3. data/results.json: every number used on the page, in the paper, the blog post, the collage and the Reddit post.
Adds plain-English labels for the windiest and most seasonal places (checked against their coordinates).
Run: python3 code/03_results.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

S = jload(f"{WORK}/stats.json")

# labels for the windiest places, in rank order, with the position each must match
WL = [("Vatnajökull ice cap", "Iceland", 64.6, -17.5), ("Jan Mayen", "Norway", 71.0, -8.2), ("East Greenland ice sheet", "Greenland", 68.9, -29.9),
      ("Southern Patagonian Ice Field", "Chile", -50.6, -73.3), ("North-west Greenland", "Greenland", 77.8, -55.0),
      ("Cordillera Darwin, Tierra del Fuego", "Chile", -54.6, -69.7), ("Heard Island", "Australia", -53.1, 73.7),
      ("Macquarie Island", "Australia", -54.7, 158.9), ("High Andes of Mendoza", "Argentina", -33.4, -69.8), ("Bouvet Island", "Norway", -54.4, 3.3),
      ("South Sandwich Islands", "UK overseas territory", -59.5, -27.1), ("Campbell Island", "New Zealand", -52.5, 169.1),
      ("South Greenland, near Narsarsuaq", "Greenland", 61.8, -44.5), ("Norway's west coast, Sogn og Fjordane", "Norway", 61.9, 4.8),
      ("Kerguelen Islands", "France", -49.3, 69.6), ("Rat Islands, Aleutians", "United States", 51.9, 179.7),
      ("Northern Patagonian Ice Field, Aysén", "Chile", -46.1, -71.9), ("St Kilda", "United Kingdom", 57.8, -8.6), ("Faroe Islands", "Denmark", 62.3, -7.2),
      ("Fiordland", "New Zealand", -45.5, 167.1)]
for p, (lab, ct, la, lo) in zip(S["windiest_places"], WL):
    assert abs(p["lat"] - la) < .15 and abs(p["lon"] - lo) < .15, (p, lab)
    p["label"], p["label_country"] = lab, ct
SL = [("Kolyma uplands, Yakutia", "Russia", 67.6, 143.9), ("Altai, north Xinjiang", "China", 47.0, 89.5), ("Transbaikal, near Kyakhta", "Russia", 50.0, 108.0),
      ("Madang coast", "Papua New Guinea", -5.2, 145.0), ("Chagos Archipelago", "UK overseas territory", -6.6, 71.3),
      ("Central Siberian Plateau", "Russia", 64.1, 101.2), ("Kutch, Gujarat", "India", 23.7, 70.1), ("Southern Maldives", "Maldives", 0.3, 73.5),
      ("Odisha coast", "India", 21.0, 86.4), ("Watson Lake, Yukon", "Canada", 61.2, -128.3), ("Greater Khingan, near Genhe", "China", 51.5, 120.0),
      ("Sistan, Farah province", "Afghanistan", 31.5, 61.2)]
for p, (lab, ct, la, lo) in zip(S["seasonal_places"], SL):
    assert abs(p["lat"] - la) < .15 and abs(p["lon"] - lo) < .15, (p, lab)
    p["label"], p["label_country"] = lab, ct
S["uk"]["max"]["label"] = "St Kilda"
assert abs(S["uk"]["max"]["lat"] - 57.8) < .1 and abs(S["uk"]["max"]["lon"] + 8.6) < .1


def rnd(v):
    if isinstance(v, float): return round(v, 4)
    if isinstance(v, list): return [rnd(x) for x in v]
    if isinstance(v, dict): return {k: rnd(x) for k, x in v.items()}
    return v


R = rnd(S)
R["meta"].update(gppd_version="1.3.0", gppd_snapshot="2021", wc_res="5 arc minutes", ncep_res="2.5 degrees")
# a few derived figures used in the text
c = R["circ"]
R["derived"] = dict(roar_ratio=c["roar_s"] / c["roar_n"], ocean_land_ratio=c["ocean_mean"] / c["land_mean_ncep"],
                    farm_land_ratio=R["farms"]["land_cw_wind"] / R["land"]["mean"],
                    uk_vs_land=R["uk"]["mean"] / R["land"]["mean"], sea_share_uk=R["uk_farms"]["cap_sea_gw"] / R["uk_farms"]["cap_gw"],
                    nh_spring_share=sum(R["seas"]["nh_windiest_month_share"][2:5]),
                    jul_roar_ratio=c["roar_s_Jul"] / c["roar_n_Jul"], arabian_jul_jan=R["monsoon"]["arabian_jul"]["vec"] / R["monsoon"]["arabian_jan"]["vec"])
R["derived"] = rnd(R["derived"])
jsave(R, f"{DATA}/results.json", indent=1)
print("results.json", os.path.getsize(f"{DATA}/results.json"), "bytes")
