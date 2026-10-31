"""Step 7. header.png: 1200 x 630 social card (title, a line of text and the world's annual winds with streamlines).
Run: python3 code/07_header.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *

R = jload(f"{DATA}/results.json")
ann = np.load(f"{WORK}/ann.npy"); U, V, SP, nlat, nlon = ncep()
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([0.0, 0.0, 1.0, 0.66]); ext = (-170, 190, -58, 75)
rows = np.arange(int((90 - 75) * 12), int((90 + 58) * 12)); cols = np.arange(NX)
land = ann[rows]; sea = ncep_on_grid(SP.mean(0), rows, cols)
ax.imshow(wind_image(land, sea, .55), extent=[-180, 180, -58, 75], aspect="auto", interpolation="bilinear")
streams(ax, U.mean(0), V.mean(0), nlat, nlon, (-180, 180, -58, 75), density=2.0, lw=(.4, 1.5), arrows=.8)
ax.set_xlim(-180, 180); ax.set_ylim(-58, 75); ax.axis("off")
fig.text(0.035, 0.95, "Where the wind blows", fontproperties=DISP, fontsize=52, color=DEEP, va="top")
fig.text(0.037, 0.79, f"The world's winds month by month: trade winds, westerlies, Roaring Forties and monsoon.\n"
         f"{round(R['farms']['share_cap_above_median'] * 100)}% of onshore wind farm capacity sits on ground windier than its country's median.",
         fontsize=14, family=SER, color=FG, va="top", linespacing=1.35)
fig.text(0.965, 0.95, "maps.tristanhotham.com", fontsize=10.5, family=MONO, color=MUT, ha="right", va="top")
fig.savefig(os.path.join(ROOT, "header.png"), facecolor=BG); plt.close(fig)
print("header written")
