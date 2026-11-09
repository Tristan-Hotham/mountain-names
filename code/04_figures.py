"""Step 4: static figures for the blog (release/blog/b_*.png, 1800 px wide) and the paper (release/paper/f_*.png)."""
import shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import LineCollection
import numpy as np, pandas as pd, geopandas as gpd
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
plt.rcParams.update({"font.family": "IBM Plex Mono", "font.size": 12, "axes.edgecolor": "#6E604E", "text.color": "#2B2119",
                     "xtick.color": "#6E604E", "ytick.color": "#6E604E"})
PAPER, INK, MUT, RED, SEA, LAND = "#F6EED8", "#2B2119", "#6E604E", "#A3261B", "#DCE6E1", "#ECD9AC"
R = jload(f"{DATA}/results.json")
K = pd.read_csv(f"{DATA}/peaks.csv", keep_default_na=False, na_values=[""])
BLOG = os.path.join(ROOT, "release", "blog"); PAP = os.path.join(ROOT, "release", "paper")
os.makedirs(BLOG, exist_ok=True); os.makedirs(PAP, exist_ok=True)
NE = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson")
NE = NE[NE.ADMIN != "Antarctica"].copy(); NE["geometry"] = NE.geometry.simplify(0.05)


def save(fig, name):
    fig.savefig(f"{BLOG}/b_{name}.png", dpi=200, facecolor=fig.get_facecolor())
    shutil.copy(f"{BLOG}/b_{name}.png", f"{PAP}/f_{name}.png"); plt.close(fig)


def title(fig, t, s):
    H = fig.get_figheight(); y = 1 - 0.3 / H
    fig.text(0.04, y, t, fontproperties=DISP, fontsize=26, color=INK, va="top")
    if s: fig.text(0.04, y - 0.52 / H, s, fontsize=11, color=MUT, va="top")


def foot(fig, s="Data: Wikidata (CC0), Natural Earth  ·  maps.tristanhotham.com/mountain-names"):
    fig.text(0.04, 0.012, s, fontsize=8.5, color=MUT)


def gc(lon1, lat1, lon2, lat2, n=60):
    r = np.pi / 180
    v1 = np.array([np.cos(lat1 * r) * np.cos(lon1 * r), np.cos(lat1 * r) * np.sin(lon1 * r), np.sin(lat1 * r)])
    v2 = np.array([np.cos(lat2 * r) * np.cos(lon2 * r), np.cos(lat2 * r) * np.sin(lon2 * r), np.sin(lat2 * r)])
    d = np.arccos(np.clip(v1 @ v2, -1, 1))
    if d < 1e-6: return []
    t = np.linspace(0, 1, n)[:, None]
    v = (np.sin((1 - t) * d) * v1 + np.sin(t * d) * v2) / np.sin(d)
    lon = np.degrees(np.arctan2(v[:, 1], v[:, 0])); lat = np.degrees(np.arcsin(v[:, 2]))
    cut = np.where(np.abs(np.diff(lon)) > 180)[0]
    segs = np.split(np.c_[lon, lat], cut + 1)
    return [s for s in segs if len(s) > 1]


def world(ax, sub=None, ext=(-170, 190, -80, 82), lw=0.35, a=0.32):
    ax.set_facecolor(SEA); NE.plot(ax=ax, color=LAND, edgecolor="#9C8656", lw=0.25)
    d = K if sub is None else K[sub]
    d = d[d.blat.notna()]
    segs, cols = [], []
    for r in d.itertuples():
        for s in gc(r.lon, r.lat, r.blon, r.blat):
            segs.append(s); cols.append(CCOL.get(r.bcont, "#9C9284"))
    ax.add_collection(LineCollection(segs, colors=cols, lw=lw, alpha=a, zorder=3))
    ax.scatter(d.blon, d.blat, s=7, facecolor="#FBF5E4", edgecolor=[CCOL.get(c, "#9C9284") for c in d.bcont], lw=.6, zorder=4)
    ax.scatter(d.lon, d.lat, s=14, marker="^", color=[CCOL.get(c, "#9C9284") for c in d.bcont], edgecolor=INK, lw=.3, zorder=5)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect(1.15); ax.axis("off")


LEG = ["Europe", "North America", "Asia", "South America", "Africa", "Oceania"]
# 1. world
fig = plt.figure(figsize=(9, 6.2), facecolor=PAPER)
ax = fig.add_axes([0.01, 0.1, 0.98, 0.74]); world(ax)
title(fig, "Who's on the mountains?", "Person-named mountains (triangles) linked to the birthplaces, by continent of birth.")
fig.legend([plt.Line2D([], [], marker="^", ls="", color=CCOL[c], ms=8) for c in LEG], ["Born in " + c for c in LEG], loc="lower center", ncol=6, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 0.035), handletextpad=.2, columnspacing=1)
foot(fig); save(fig, "world")
# 2. Oceania close-up
fig = plt.figure(figsize=(9, 6.2), facecolor=PAPER)
ax = fig.add_axes([0.01, 0.1, 0.98, 0.74]); world(ax, sub=K.continent == "Oceania", lw=.45, a=.4)
title(fig, "From the other side of the world", f"Australia and New Zealand: {R['anz']['other_pct']:.0f}% of person-named peaks honour someone born elsewhere.")
fig.legend([plt.Line2D([], [], marker="^", ls="", color=CCOL[c], ms=8) for c in LEG], ["Born in " + c for c in LEG], loc="lower center", ncol=6, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 0.035), handletextpad=.2, columnspacing=1)
foot(fig); save(fig, "oceania")
# 3. continent x continent
fig, ax = plt.subplots(figsize=(9, 5), facecolor=PAPER); fig.subplots_adjust(left=0.2, right=0.97, top=0.8, bottom=0.18)
rows = ["Europe", "North America", "Oceania", "South America", "Asia"][::-1]
for i, c in enumerate(rows):
    b = R["cont"][c]["bcont"]; tot = sum(b.values()); left = 0
    for k in LEG:
        v = 100 * b.get(k, 0) / tot
        ax.barh(i, v, left=left, color=CCOL[k], height=.7, edgecolor=PAPER, lw=.6)
        if v > 8: ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=9.5, color="white")
        left += v
    ax.text(101, i, f"n={tot}", va="center", fontsize=9, color=MUT)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows); ax.set_xlim(0, 110); ax.set_xticks([]); ax.set_facecolor(PAPER); [ax.spines[s].set_visible(False) for s in ax.spines]
fig.legend([plt.Rectangle((0, 0), 1, 1, color=CCOL[c]) for c in LEG], ["Born in " + c for c in LEG], loc="lower center", ncol=3, frameon=False, fontsize=8.5, bbox_to_anchor=(0.55, 0.0), handletextpad=.3, columnspacing=1)
title(fig, "Where the honoured were born", "Person-named mountains by continent (rows) and the continent of the namesake's birth.")
save(fig, "continents")
# 4. foreign-born share by country
fig, ax = plt.subplots(figsize=(9, 4.8), facecolor=PAPER); fig.subplots_adjust(left=0.27, right=0.9, top=0.8, bottom=0.1)
CT = sorted(R["countries"], key=lambda x: x["foreign_pct"])
ax.barh([c["country"] for c in CT], [c["foreign_pct"] for c in CT], color=RED, height=.65)
for i, c in enumerate(CT): ax.text(c["foreign_pct"] + 1, i, f"{c['foreign_pct']:.0f}%  (n={c['n']})", va="center", fontsize=10)
ax.set_xlim(0, 115); ax.set_xticks([]); ax.set_facecolor(PAPER); [ax.spines[s].set_visible(False) for s in ("top", "right", "bottom")]
title(fig, "Honouring the foreign-born", "Share of person-named mountains whose namesake was born abroad (25+ namings).")
foot(fig); save(fig, "countries")
# 5. occupations by continent
ks = list(R["occ_names"].keys())
fig, ax = plt.subplots(figsize=(9, 5.4), facecolor=PAPER); fig.subplots_adjust(left=0.2, right=0.97, top=0.82, bottom=0.24)
rows = ["Europe", "North America", "Oceania", "South America", "Asia", "Antarctica"][::-1]
for i, c in enumerate(rows):
    v = R["occ_by_cont"][c]; tot = sum(v.values()); left = 0
    for k in ks:
        x = 100 * v[k] / tot; ax.barh(i, x, left=left, color=R["occ_cols"][k], height=.7, edgecolor=PAPER, lw=.6)
        if x > 9: ax.text(left + x / 2, i, f"{x:.0f}%", ha="center", va="center", fontsize=9, color="white")
        left += x
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows); ax.set_xlim(0, 100); ax.set_xticks([]); ax.set_facecolor(PAPER); [ax.spines[s].set_visible(False) for s in ax.spines]
fig.legend([plt.Rectangle((0, 0), 1, 1, color=R["occ_cols"][k]) for k in ks], [R["occ_names"][k] for k in ks], loc="lower center", ncol=3, frameon=False, fontsize=8.5, bbox_to_anchor=(0.55, 0.0))
title(fig, "What the honoured people did", "Namings by the person's occupation group, by continent of the mountain.")
save(fig, "occupations")
# 6. tallest
T = R["tallest"][:12][::-1]
fig, ax = plt.subplots(figsize=(9, 5.4), facecolor=PAPER); fig.subplots_adjust(left=0.33, right=0.97, top=0.82, bottom=0.08)
ax.barh([t["name"] for t in T], [t["elev"] for t in T], color="#7C93A3", height=.65)
for i, t in enumerate(T): ax.text(t["elev"] + 60, i, f"{t['elev']:,} m  {t['person']}", va="center", fontsize=9)
ax.set_xlim(0, 13500); ax.set_xticks([]); ax.set_facecolor(PAPER); [ax.spines[s].set_visible(False) for s in ("top", "right", "bottom")]
title(fig, "The highest mountains with a person's name", "Elevations from Wikidata; implausible values read as feet.")
foot(fig); save(fig, "tallest")
print(sorted(os.listdir(BLOG)))
