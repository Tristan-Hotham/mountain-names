"""Step 3: build index.html from code/page_template.html. Every number is a {{path|format}} token filled from data/results.json;
peaks and people (data/site.json) load when the page opens. Facts stated in words are checked here.
10.5281/zenodo.24075305, https://doi.org/10.5281/zenodo.24075305 and https://blog.tristanhotham.com/2026/10/31/mountain-names/ stay as placeholders for the publisher."""
import json
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
K = pd.read_csv(f"{DATA}/peaks.csv", keep_default_na=False, na_values=[""])
C = R["cont"]
# facts stated in words (page, blog, paper, collage, post)
assert C["Oceania"]["other_pct"] > 80 and C["Oceania"]["top_bcont"] == "Europe"           # "four in five"
assert C["Europe"]["europe_pct"] > 95
assert C["South America"]["other_pct"] > C["North America"]["other_pct"]
assert R["country_n"]["New Zealand"]["top_born"] == "United Kingdom"
assert [x["name"] for x in R["dist"]["longest"][:1]] == ["Mount Grey / Maukatere"] and R["dist"]["longest"][0]["bctry"] == "Portugal"
assert set(R["country_n"]["Svalbard (Norway)"]["top_foreign"]) == {"Sweden", "Germany", "United Kingdom"}
assert R["occ"]["science"]["pct"] > R["occ"]["royal"]["pct"] > R["occ"]["explore"]["pct"] > R["occ"]["military"]["pct"] > R["occ"]["survey"]["pct"]
assert R["anz"]["other_pct"] > 80 and R["anz"]["europe_pct"] < R["anz"]["other_pct"]
assert [t["name"] for t in R["tallest"][:3]] == ["Mount Everest", "Ismoil Somoni Peak", "Lenin Peak"]
assert R["top_people"][0]["name"] == "Ferdinand von Mueller" and R["top_people"][0]["n"] > R["top_people"][1]["n"]
for p in ("Josiah Whitney", "William Henry Brewer", "Charles F. Hoffmann", "James Dwight Dana", "Beatrice Tinsley", "Nancy Tyson Burbidge", "Fay Fuller", "Amelia Earhart", "Jean Batten"):
    assert (K.person == p).any(), p
W = K[K.sex == "female"]
assert {"Mount Victoria", "Queen Maud Mountains"} <= set(W.name)
assert 4.5 < R["women"]["pct"] < 6                                                         # "one in twenty"
assert any(r["name"] == "Denali" for r in R["renamed"]) and "Aoraki / Mount Cook" in R["dual"]
assert R["antarctica"]["n"] == len(K[(K.continent == "Antarctica") & K.bcont.notna()])


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    R2 = dict(R); R2["dual"] = ", ".join(R["dual"][:-1]) + " and " + R["dual"][-1]
    html = fill(tpl, R2)
    left = set(re.findall(r"\{\{[^}]*\}\}", html))
    assert left <= {"10.5281/zenodo.24075305", "https://doi.org/10.5281/zenodo.24075305", "https://blog.tristanhotham.com/2026/10/31/mountain-names/"}, left
    html = html.replace("/*RESULTS*/", json.dumps(R, ensure_ascii=False, separators=(",", ":")))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
