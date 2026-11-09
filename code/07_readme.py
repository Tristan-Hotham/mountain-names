"""Step 7: README.md and reddit/post.md from data/results.json."""
from common import *
R = jload(f"{DATA}/results.json"); S = R["source"]; C = R["cont"]; CN = R["country_n"]
t = f"""# Who's on the mountains? The birthplaces of the people the world's mountains are named after

A map and analysis of {S['features']:,} mountains, summits, hills, volcanoes and ranges that Wikidata says are named after a person ({S['namings']:,} namings, {S['people']:,} people), each linked to its namesake's birthplace. Click a mountain and the map draws the great-circle line home.

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24075305}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/mountain-names/}}

## Headline results

- In Europe {C['Europe']['europe_pct']:.1f}% of person-named mountains honour someone born in Europe. Elsewhere the names are imported: {R['anz']['other_pct']:.1f}% in Australia and New Zealand honour someone born on another continent ({R['anz']['europe_pct']:.1f}% in Europe), {C['South America']['other_pct']:.1f}% in South America, {C['North America']['other_pct']:.1f}% in North America. Outside Europe and Antarctica, {R['outside']['noneurope_peaks_europe_born_pct']:.1f}% honour someone born in Europe.
- Foreign-born namesakes by country: New Zealand {CN['New Zealand']['foreign_pct']:.1f}%, Australia {CN['Australia']['foreign_pct']:.1f}%, Svalbard {CN['Svalbard (Norway)']['foreign_pct']:.1f}%, Canada {CN['Canada']['foreign_pct']:.1f}%, United States {CN['United States']['foreign_pct']:.1f}%.
- Who: scientists {R['occ']['science']['pct']:.1f}%, royals, rulers and politicians {R['occ']['royal']['pct']:.1f}%, explorers, mountaineers and aviators {R['occ']['explore']['pct']:.1f}%, military and naval officers {R['occ']['military']['pct']:.1f}%, surveyors and geographers {R['occ']['survey']['pct']:.1f}%. Most honoured: Ferdinand von Mueller ({R['top_people'][0]['n']}).
- Women: {R['women']['pct']:.1f}% of namings with a recorded sex.
- Tallest: Mount Everest ({R['tallest'][0]['elev']:,} m), Ismoil Somoni Peak ({R['tallest'][1]['elev']:,} m), Lenin Peak ({R['tallest'][2]['elev']:,} m).
- Renamings recorded in Wikidata: Denali, Black Elk Peak, Doso Doyabi, Mount Blue Sky, Kuwohi and others; {len(R['dual'])} dual names such as Aoraki / Mount Cook.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/03_build_site.py`): a MapLibre map in the Inked World style with mountains, birthplaces and great-circle lines, filters by continent and occupation, and charts. |
| `header.png` | Social card, 1200 x 630. |
| `data/peaks.csv` | One row per mountain and person: Wikidata ids, name, types, coordinates, elevation (as given, and in metres with any feet conversion), modern country and continent, the person, birthplace continent and country, distance. |
| `data/people.csv` | One row per person: sex, birth year, birthplace item, label and coordinates, modern country and continent, occupations and group. |
| `data/overrides.csv` | Documented corrections: wrong links removed, features that are not mountains, birthplaces that are only a country, state or empire, corrected birthplaces, elevations in feet, missing names. |
| `data/renamings.csv` | Renamed mountains, from Wikidata's dated official names and "named after" links to former names. |
| `data/wikidata_labels.csv` | English labels for the Wikidata items in the extract (occupations, types, countries, birthplaces). |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json` | Page data. Other files in `data/`, `js/` and `fonts/` belong to the Inked World map style. |
| `code/` | Scripts, run in order, templates, and `qa.js` for screenshots. |
| `release/` | Paper PDF and LaTeX (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots at desktop and phone widths. |

## Method in brief

- One Wikidata query (QLever) for mountains, summits, hills, volcanoes, ranges and passes named after a human, with the person's birthplace, dates, sex and occupations. {S['rows']:,} rows, deduplicated.
- Left out: {S['passes']} mountain passes, {S['off_earth']} features on the Moon and Mars, {S['undersea']} undersea ridges, {S['not_mountains']} features that are not mountains (two ravines and a road).
- Checks: every naming whose name does not contain the namesake's name was read ({S['links_removed']} links removed: wrong people, former names and saints honoured by dedication); {S['bp_unmapped']} birthplaces that are only a country, state or empire left unmapped; {S['bp_fixed']} corrected; {S['elev_feet']} elevations read as feet because they exceed the country's highest point (or, checked by hand, a state's or island's).
- Modern countries and continents from Natural Earth; Antarctica south of 60 S; Svalbard apart from mainland Norway. Occupations grouped by keyword in tiers (titles of rule, specific professions, politics, arts and business, generic labels); see `code/common.py`.

## Caveats

Wikidata is not a complete list of named mountains and its coverage is uneven. "Named after" links can refer to former names. Modern borders are applied to old birthplaces. Sex is as recorded in Wikidata.

## Sources and licences

- Wikidata contributors (CC0), queried with QLever.
- Natural Earth (public domain). Map style on OpenStreetMap data (ODbL) via OpenFreeMap.
- Text, figures and derived data CC BY 4.0; code MIT (see LICENSE).

## How to rerun

```
cd code
python3 01_clean.py && python3 02_analysis.py && python3 03_build_site.py && python3 04_figures.py && python3 05_paper.py
cd .. && python3 reddit/collage.py && python3 code/07_readme.py && cd code && python3 06_release.py
```
Raw input paths are documented in `code/common.py`.

## Citation

Hotham, T. (2026) Who's on the mountains? The birthplaces of the people the world's mountains are named after. Zenodo. {{https://doi.org/10.5281/zenodo.24075305}}

{AI}
"""
for bad in ("—", "–", "--"): assert bad not in t.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(t)
p = f"""**Title:** [OC] Who's on the mountains? I linked {S['features']:,} mountains named after people to their namesakes' birthplaces: {R['anz']['other_pct']:.0f}% of the person-named peaks of Australia and New Zealand honour someone born on another continent

**Body:**

Everest, Kosciuszko, Cook, McKinley: lots of mountains carry a person's name. Using Wikidata I drew a line from every person-named mountain to the place its namesake was born.

- In Europe {C['Europe']['europe_pct']:.0f}% of person-named peaks honour someone born in Europe. In Australia and New Zealand {R['anz']['other_pct']:.0f}% honour someone born on another continent; in South America {C['South America']['other_pct']:.0f}%; in North America {C['North America']['other_pct']:.0f}%.
- {CN['New Zealand']['foreign_pct']:.0f}% of New Zealand's person-named peaks honour people born abroad, mostly in Britain. The longest line: Mount Grey, NZ, to George Grey's birthplace in Lisbon, {R['dist']['longest'][0]['km']:,} km.
- Scientists are {R['occ']['science']['pct']:.0f}% of the people honoured, royals, rulers and politicians {R['occ']['royal']['pct']:.0f}%. Only {R['women']['pct']:.1f}% are women.
- Recent renamings in the data: Denali, Black Elk Peak, Doso Doyabi, Mount Blue Sky, Kuwohi.

Interactive map (click a mountain to draw the line home): {PAGE}

**Source comment:**

Data: Wikidata (CC0) "named after" (P138) statements for mountains, summits, hills, volcanoes and ranges, with each person's birthplace (P19), sex and occupations, queried through QLever; {S['people_located']:,} people with a mapped birthplace. I removed {S['links_removed']} links that were wrong, out of date or to a saint honoured by a church rather than in memory, and left {S['bp_unmapped']} country-level birthplaces off the map. Countries and continents are modern, from Natural Earth. Wikidata is not a complete list of mountains. Tools: Python (pandas, geopandas, matplotlib), MapLibre. Paper, data and code: {REPO}
"""
for bad in ("—", "–", "--"): assert bad not in p, bad
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(p)
print("README", len(t.split()), "words; post", len(p.split()))
