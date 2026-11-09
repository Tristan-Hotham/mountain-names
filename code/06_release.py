"""Step 6: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24075305, https://doi.org/10.5281/zenodo.24075305 and https://blog.tristanhotham.com/2026/10/31/mountain-names/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Mountain_Names"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}

# facts in words in the blog and its alt text
import pandas as pd
K = pd.read_csv(f"{DATA}/peaks.csv", keep_default_na=False, na_values=[""])
mu = K[K.person == "Ferdinand von Mueller"]; assert mu.continent.isin(["Oceania"]).mean() > .5
ob = R["occ_by_cont"]
for c in ("North America", "Oceania"): assert max(ob[c], key=ob[c].get) == "royal", c
assert 30 < 100 * ob["Antarctica"]["science"] / sum(ob["Antarctica"].values()) < 37
assert R["dist"]["longest"][0]["km"] > 19000
b = R["cont"]
assert 60 < 100 * b["North America"]["bcont"]["North America"] / b["North America"]["n"] < 70 and 30 < b["North America"]["europe_pct"] < 37
assert 60 < b["South America"]["europe_pct"] < 70 and 45 < b["Asia"]["europe_pct"] < 55
assert 4.5 < R["women"]["pct"] < 6 and R["cont"]["Oceania"]["other_pct"] > 80

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = fill(post, R)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
from PIL import Image
for img in used:
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used: os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Who's on the mountains? The birthplaces of the people the world's peaks are named after",
        "slug": "mountain-names",
        "excerpt": f"I linked {R['source']['features']:,} mountains named after people to their namesakes' birthplaces. {R['anz']['other_pct']:.0f}% of the person-named peaks of Australia and New Zealand honour someone born on another continent.",
        "seo_description": f"Whose names are on the world's mountains? {R['source']['features']:,} peaks linked to their namesakes' birthplaces: the colonial survey layer, mapped.",
        "tags": ["maps", "mountains", "place names", "toponymy", "colonialism", "Wikidata", "data visualisation", "geography"],
        "header_alt": f"Title card reading 'Who's on the mountains?' in black and red on parchment, beside a world map with coloured lines from mountains to the birthplaces of the people they are named after, and the lines '{R['anz']['other_pct']:.0f}% of the person-named peaks of Australia and New Zealand honour someone born on another continent' and 'Only {R['women']['pct']:.1f}% honour a woman'."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z): os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/{SLUG}_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith(".pyc") or fn == "__pycache__": continue
        z.write(os.path.join(ROOT, "code", fn), f"{SLUG}/code/{fn}")
    for fn in ("peaks.csv", "people.csv", "overrides.csv", "renamings.csv", "wikidata_labels.csv", "results.json", "site.json"):
        z.write(os.path.join(DATA, fn), f"{SLUG}/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"{SLUG}/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), f"{SLUG}/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&").replace("{\\textendash}", "")
ab = re.sub(r"\\textit\{([^}]*)\}", r"\1", ab)
ab = ab.replace("``", "\u201c").replace("''", "\u201d")
zmeta = {"title": "Who's on the Mountains? The Birthplaces of the People the World's Mountains Are Named After",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/mountain-names/}}.</p><p>Sources: Wikidata (CC0), queried with QLever; Natural Earth (public domain); map style on OpenStreetMap data (ODbL) via OpenFreeMap. Derived data and text CC BY 4.0, code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["mountains", "toponymy", "place names", "commemoration", "colonialism", "surveying", "Wikidata", "maps", "open data"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
