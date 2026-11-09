"""Reddit collage (reddit/mountain_names_collage.png, 3000 x 1900) and the social card (header.png, 1200 x 630).
Run from anywhere: python3 reddit/collage.py"""
import os, sys, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); ROOTD = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOTD, "code"))
G = runpy.run_path(os.path.join(ROOTD, "code", "04_figures.py"), run_name="figs")
globals().update({k: v for k, v in G.items() if not k.startswith("__")})
import matplotlib.pyplot as plt, matplotlib.patheffects as pe

SRC = "Data: Wikidata (CC0), Natural Earth  ·  Analysis and map: Dr Tristan Hotham  ·  maps.tristanhotham.com/mountain-names"
halo = [pe.withStroke(linewidth=4, foreground=SEA)]
fig = plt.figure(figsize=(15, 9.5), dpi=200, facecolor=PAPER)
ax = fig.add_axes([0.0, 0.1, 0.62, 0.8]); world(ax, ext=(-170, 190, -80, 82), lw=.45, a=.35)
# review: labels moved off the lines onto the paper above and below the map; leaders cross no other label
lab = dict(fontsize=12, color=INK, zorder=7, linespacing=1.25, clip_on=False)
ax.text(15, 104, "Svalbard: Swedes, Germans, Britons", ha="center", va="center", **lab)
ax.annotate("", xy=(17, 80), xytext=(17, 99), arrowprops=dict(arrowstyle="-", color=INK, lw=.8), annotation_clip=False)
ax.text(-160, -97, "Antarctica (along the lower edge):\neveryone from elsewhere", ha="left", va="center", **lab)
ax.text(100, -97, "New Zealand: {:.0f}%\nborn abroad".format(R["country_n"]["New Zealand"]["foreign_pct"]), ha="center", va="center", **lab)
ax.annotate("", xy=(171, -45), xytext=(133, -90), arrowprops=dict(arrowstyle="-", color=INK, lw=.8), annotation_clip=False)
fig.text(0.635, 0.94, "Who's on the mountains?", fontproperties=DISP, fontsize=34, color=INK, va="top")
fig.text(0.635, 0.86, f"{R['source']['features']:,} mountains named after people,\nlinked to where those people were born", fontsize=13.5, color=MUT, va="top", linespacing=1.35)
S = [(f"{R['anz']['other_pct']:.0f}%", "of Australia and NZ's\nperson-named peaks honour\nsomeone born on\nanother continent"),
     (f"{R['cont']['Europe']['europe_pct']:.0f}%", "of Europe's honour someone\nborn in Europe"),
     (f"{R['women']['pct']:.1f}%", "of the namings\nhonour a woman"),
     (f"{R['occ']['science']['pct']:.0f}%", "were scientists; {:.0f}%\nroyals or politicians".format(R['occ']['royal']['pct']))]
for i, (b, s) in enumerate(S):
    x = 0.635 + (i % 2) * 0.19; y = 0.77 - (i // 2) * 0.17
    fig.text(x, y, b, fontproperties=DISP, fontsize=36, color=RED, va="top")
    fig.text(x, y - 0.06, s, fontsize=11, color=INK, va="top", linespacing=1.3)
bx = fig.add_axes([0.765, 0.13, 0.215, 0.28]); bx.set_facecolor(PAPER)
rows = ["Europe", "North America", "Oceania", "South America", "Asia"][::-1]
for i, c in enumerate(rows):
    b = R["cont"][c]["bcont"]; tot = sum(b.values()); left = 0
    for k in LEG:
        v = 100 * b.get(k, 0) / tot; bx.barh(i, v, left=left, color=CCOL[k], height=.7, edgecolor=PAPER, lw=.6); left += v
bx.set_yticks(range(len(rows))); bx.set_yticklabels(rows, fontsize=10.5); bx.set_xticks([]); [bx.spines[s].set_visible(False) for s in bx.spines]
bx.set_title("Mountains in (rows), and where\nthe honoured were born (colours)", loc="right", fontsize=11.5, color=MUT)
fig.legend([plt.Line2D([], [], marker="^", ls="", color=CCOL[c], ms=9) for c in LEG] + [plt.Line2D([], [], marker="o", ls="", mfc="#FBF5E4", mec=INK, ms=6)],
           ["Mountain, namesake born in " + LEG[0]] + ["born in " + c for c in LEG[1:]] + ["Birthplace"], loc="lower left", ncol=7, frameon=False, fontsize=10.5, bbox_to_anchor=(0.02, 0.045), handletextpad=.2, columnspacing=1.2)
fig.text(0.02, 0.018, SRC + "  ·  Lines: great circles from each mountain to its namesake's birthplace.", fontsize=9, color=MUT)
out = os.path.join(HERE, "mountain_names_collage.png")
fig.savefig(out, dpi=200, facecolor=PAPER); plt.close(fig)

fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=PAPER)
ax = fig.add_axes([0.42, 0.04, 0.58, 0.92]); world(ax, ext=(-170, 190, -60, 82), lw=.35, a=.3)
fig.text(0.04, 0.86, "Who's on the", fontproperties=DISP, fontsize=44, color=INK, va="top")
fig.text(0.04, 0.70, "mountains?", fontproperties=DISP, fontsize=44, color=RED, va="top")
fig.text(0.04, 0.44, f"{R['anz']['other_pct']:.0f}% of Australia and New Zealand's", fontsize=13.5, color=INK)
fig.text(0.04, 0.39, "person-named peaks honour someone", fontsize=13.5, color=INK)
fig.text(0.04, 0.34, "born on another continent", fontsize=13.5, color=INK)
fig.text(0.04, 0.26, f"Only {R['women']['pct']:.1f}% honour a woman", fontsize=13.5, color=INK)
fig.text(0.04, 0.08, "Dr Tristan Hotham · maps.tristanhotham.com/mountain-names", fontsize=11, color=MUT)
fig.savefig(os.path.join(ROOTD, "header.png"), dpi=100, facecolor=PAPER); plt.close(fig)
from PIL import Image
print(Image.open(out).size, Image.open(os.path.join(ROOTD, "header.png")).size)
