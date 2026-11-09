# Who's on the mountains? The birthplaces of the people the world's mountains are named after

A map and analysis of 2,228 mountains, summits, hills, volcanoes and ranges that Wikidata says are named after a person (2,241 namings, 2,010 people), each linked to its namesake's birthplace. Click a mountain and the map draws the great-circle line home.

Interactive page: https://maps.tristanhotham.com/mountain-names/
Paper: https://doi.org/10.5281/zenodo.24075305
Blog post: https://blog.tristanhotham.com/2026/10/31/mountain-names/

## Headline results

- In Europe 97.9% of person-named mountains honour someone born in Europe. Elsewhere the names are imported: 83.8% in Australia and New Zealand honour someone born on another continent (78.9% in Europe), 70.7% in South America, 35.1% in North America. Outside Europe and Antarctica, 53.2% honour someone born in Europe.
- Foreign-born namesakes by country: New Zealand 87.5%, Australia 83.8%, Svalbard 73.0%, Canada 54.6%, United States 29.0%.
- Who: scientists 29.4%, royals, rulers and politicians 19.2%, explorers, mountaineers and aviators 17.3%, military and naval officers 11.8%, surveyors and geographers 10.9%. Most honoured: Ferdinand von Mueller (6).
- Women: 5.1% of namings with a recorded sex.
- Tallest: Mount Everest (8,849 m), Ismoil Somoni Peak (7,495 m), Lenin Peak (7,134 m).
- Renamings recorded in Wikidata: Denali, Black Elk Peak, Doso Doyabi, Mount Blue Sky, Kuwohi and others; 9 dual names such as Aoraki / Mount Cook.

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

- One Wikidata query (QLever) for mountains, summits, hills, volcanoes, ranges and passes named after a human, with the person's birthplace, dates, sex and occupations. 11,175 rows, deduplicated.
- Left out: 81 mountain passes, 16 features on the Moon and Mars, 6 undersea ridges, 3 features that are not mountains (two ravines and a road).
- Checks: every naming whose name does not contain the namesake's name was read (49 links removed: wrong people, former names and saints honoured by dedication); 59 birthplaces that are only a country, state or empire left unmapped; 2 corrected; 112 elevations read as feet because they exceed the country's highest point (or, checked by hand, a state's or island's).
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

Hotham, T. (2026) Who's on the mountains? The birthplaces of the people the world's mountains are named after. Zenodo. https://doi.org/10.5281/zenodo.24075305

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
