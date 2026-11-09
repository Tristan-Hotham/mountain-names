"""Shared paths, groupings and helpers for the mountain-names study ("Who's on the mountains?").

Raw inputs (read in place, never modified):
  MTN   /home/claude/newdata/raw_new9/mountains.tsv.gz
        Wikidata (CC0), queried through QLever: mountains, summits, hills, volcanoes, ranges and passes (P31 ?mtype) with a "named
        after" (P138) statement whose value is a human (?p); the feature's label, coordinates (?mcoord), elevation (?elev) and country
        (?mcountry); the person's label, date of birth, birthplace (?bplace), its coordinates and country, sex (P21) and occupations
        (P106). One row per combination of type and occupation; 01_clean.py deduplicates.
  REN   /home/claude/newdata/raw_new9/renamed.tsv.gz  Wikidata official names (P1448) with start and end dates, for renamed peaks.
  GEO   /home/claude/newdata/raw/geo/ (Natural Earth 1:10m countries and populated places; public domain).
  LABELS data/wikidata_labels.csv: English labels for the occupation, type, country and birthplace items in the extract, collected
        from other local Wikidata extracts and published Wikidata-derived lists on GitHub (CoDEx entity labels, occupation lists);
        Wikidata labels are CC0.
  INK   /home/claude/studies/moon-names (js/, fonts/ and base data files of the Inked World map style, copied into this study)
  FONTS /home/claude/ref/fonts
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAWD = os.environ.get("MT_RAW", "/home/claude/newdata/raw_new9")
MTN = f"{RAWD}/mountains.tsv.gz"
REN = f"{RAWD}/renamed.tsv.gz"
GEO = os.environ.get("MT_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("MT_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.environ.get("MT_WORK", "/home/claude/scratch/mountain-names/work")
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "mountain-names"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
CONT_ORDER = ["Europe", "North America", "Asia", "South America", "Africa", "Oceania", "Antarctica"]
CCOL = {"Europe": "#2F5FA7", "North America": "#C8322B", "Asia": "#E0A11B", "South America": "#2E9A8C", "Africa": "#7B57A8",
        "Oceania": "#B4532A", "Antarctica": "#7C93A3"}
# what the person did: the first group (in this order) that any of their Wikidata occupations falls in
OCC = [
    ("royal", "Royalty, rulers and politicians", r"monarch|king|queen|emperor|empress|prince|princess|aristocrat|noble|ruler|regent|politician|statesperson|stateswoman|statesman|president|prime minister|head of state|diplomat|governor|government minister|member of parliament|senator|official|civil servant|colonial administrator|lawyer|jurist|judge|revolutionary|activist"),
    ("military", "Military and naval officers", r"military|naval|officer|soldier|admiral|general|army|navy|marine|aircraft pilot|aviator"),
    ("survey", "Surveyors, geographers and cartographers", r"surveyor|geographer|cartographer|topograph|geodesist|hydrograph"),
    ("explore", "Explorers and mountaineers", r"explorer|mountaineer|climber|traveler|traveller|navigator|polar|seafarer|sailor|whaler|sealer|ski|trapper|frontiersman|hunter|guide"),
    ("science", "Scientists", r"geolog|naturalist|botan|zoolog|scien|physic|chem|astronom|mathemat|biolog|ornitholog|entomolog|meteorolog|glaciolog|mineralog|paleontolog|engineer|inventor|researcher|university teacher|professor|academic|anthropolog|ethnograph|economist|historian|philosopher|physician|surgeon|collector|volcanolog|seismolog|oceanograph|ecologist|archaeolog|linguist|teacher|educator"),
    ("arts", "Writers, artists and composers", r"writer|poet|novelist|author|journalist|painter|artist|composer|musician|singer|sculptor|photograph|architect|playwright|film|actor|actress|translator|illustrat"),
    ("religion", "Saints and clergy", r"saint|priest|clergy|cleric|bishop|missionary|monk|nun|theolog|pastor|rabbi|pope|religious|preacher|minister of religion"),
    ("business", "Business people and patrons", r"business|entrepreneur|merchant|banker|industrialist|philanthrop|patron|publisher|manufacturer|farmer|rancher|miner|prospector|trader"),
    ("other", "Others", r"."),
]
# Review fix: a single priority list put anyone Wikidata also calls a politician, lawyer, jurist or activist (Kelvin, Wallace,
# Suess, Nansen, Amelia Earhart) among the rulers, and caught 'marine biologist', 'general secretary' and 'art collector' in the
# wrong groups. People are now placed in tiers: (1) titles of rule (monarch, president, governor...), (2) specific professions
# (officers, surveyors, explorers and aviators, scientists, clergy), (3) politics without a title (politician, diplomat, lawyer...),
# (4) arts and business, (5) generic labels (military personnel, engineer, university teacher, writer...). The first tier with a match decides, and within a tier the group order.
OCC = [
    ("royal", "Royalty, rulers and politicians", None),
    ("military", "Military and naval officers", None),
    ("survey", "Surveyors, geographers and cartographers", None),
    ("explore", "Explorers, mountaineers and aviators", None),
    ("science", "Scientists", None),
    ("arts", "Writers, artists and composers", None),
    ("religion", "Saints and clergy", None),
    ("business", "Business people and patrons", None),
    ("other", "Others", None),
]
OCC_TIERS = [
    [("royal", r"monarch|\bking\b|queen|emperor|empress|prince|princess|aristocrat|\bnoble|ruler|regent|sovereign|consort|royalty|statesperson|statesman|stateswoman|president|prime minister|head ?of_?(state|government)|governor|colonial administrator|revolutionary|dictator|tsar|sultan|khan\b|pharaoh")],
    [("military", r"military officer|naval officer|army ?officer|^officer$|admiral|^general$|soldier|military leader|warrior|militaryflight|military commander|commander"),
     ("survey", r"surveyor|geographer|cartographer|topograph|geodesist|hydrograph"),
     ("explore", r"explorer|mountaineer|climber|alpinist|traveler|traveller|navigator|polar|seafarer|sailor|whaler|sealer|skier|trapper|frontiersman|hunter|mountain guide|discoverer|aircraft pilot|aviator"),
     ("science", r"geolog|naturalist|botan|zoolog|scien|physic|chem|astronom|mathemat|biolog|ornitholog|entomolog|meteorolog|glaciolog|mineralog|paleontolog|inventor|researcher|anthropolog|ethnograph|ethnolog|economist|physician|surgeon|botanicalcollector|scientificcollector|zoologicalcollector|volcanolog|seismolog|oceanograph|ecologist|archaeolog|linguist|statistician|mycolog|ichthyolog|malacolog|pteridolog|physiolog|anatom|pharmacist|astrophysic|geophysic"),
     ("religion", r"saint|priest|clergy|cleric|bishop|missionary|monk|\bnun\b|theolog|pastor|rabbi|pope|religious|preacher|minister of religion")],
    [("royal", r"politician|diplomat|ambassador|government minister|^minister$|member of parliament|senator|official|civil servant|lawyer|jurist|judge|barrister|activist|suffragist")],
    [("arts", r"poet|novelist|painter|artist|composer|musician|singer|sculptor|photograph|architect|playwright|film|actor|actress|illustrat|pianist|conductor|librettist|drawer"),
     ("business", r"business|entrepreneur|merchant|banker|industrialist|philanthrop|patron|publisher|manufacturer|farmer|rancher|\bminer\b|prospector|trader|art collector|land owner|plantationowner|media proprietor")],
    [("military", r"military|naval|army|navy|aviation"),
     ("science", r"engineer|university teacher|professor|academic|historian|philosopher|lecturer"),
     ("arts", r"writer|author|journalist|translator|editor|essayist|diarist|biographer")],
]


def occ_group(occs):
    """Occupation group for a list of Wikidata occupation labels (see OCC_TIERS); 'unknown' when there are none."""
    occs = [o.lower() for o in occs if o]
    if not occs: return "unknown"
    for tier in OCC_TIERS:
        for k, rx in tier:
            if any(re.search(rx, o) for o in occs): return k
    return "other"


OCC_NAME = {k: n for k, n, _ in OCC}
OCC_COL = {"royal": "#7B57A8", "military": "#2F5FA7", "survey": "#2E9A8C", "explore": "#C8322B", "science": "#E0A11B", "arts": "#9C7BC0",
           "religion": "#B4532A", "business": "#55803A", "other": "#9C9284", "unknown": "#C9C0B0"}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return {str(k): nonan(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "word": return WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}"
    if f == "Word": return (WORDS[int(v)] if int(v) < len(WORDS) else f"{int(v):,}").capitalize()
    raise ValueError(f)


def fill(tpl, R, keep=("DOI", "DOI_URL", "BLOG_URL")):
    return re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}",
                  lambda m: m.group(0) if m.group(1) in keep else fmt(get(R, m.group(1)), m.group(3)), tpl)




def gc_km(lon1, lat1, lon2, lat2):
    import numpy as np
    p1, p2 = np.radians(lat1), np.radians(lat2); dl = np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

# highest point of each country (metres, rounded up), used to catch elevations that Wikidata holds in feet
CMAX = {"United States": 4421, "Canada": 5959, "Antarctica": 4892, "Norway": 2469, "New Zealand": 3724, "Australia": 2228, "Russia": 5642,
        "France": 4808, "Austria": 3798, "Switzerland": 4634, "Italy": 4808, "Germany": 2962, "Greenland": 3694, "Argentina": 6961,
        "Chile": 6893, "Kazakhstan": 7010, "Kyrgyzstan": 7439, "Tajikistan": 7495, "China": 8849, "Nepal": 8849, "Pakistan": 8611,
        "India": 8586, "North Korea": 2744, "Japan": 3776, "United Kingdom": 1345, "Spain": 3718, "Czech Republic": 1603, "Poland": 2499,
        "Slovakia": 2655, "Ecuador": 6263, "Colombia": 5800, "Venezuela": 4978, "Papua New Guinea": 4509, "Indonesia": 4884,
        "Mongolia": 4374, "Georgia": 5193, "Armenia": 4090, "Turkey": 5137, "Iran": 5610, "Israel": 1208, "Mexico": 5636, "Peru": 6768,
        "Bolivia": 6542, "Svalbard (Norway)": 1717}


ALASKA_GIANTS = {"Denali (Mount McKinley)", "Mount Foraker", "Mount Blackburn", "Mount Sanford", "Mount Hubbard", "Mount Alverstone", "Mount Vancouver", "Mount Hayes", "Churchill Peaks", "Mount Saint Elias", "Mount Bona"}


def elev_m(e, country, lon, lat, name=""):
    """(metres, how): Wikidata's value, or the value read as feet when it is higher than the country's highest point."""
    import math as _m
    if e is None or (isinstance(e, float) and _m.isnan(e)): return None, ""
    cap = CMAX.get(country)
    if country == "United States" and lon < -130 and lat > 51:                       # Alaska: only its few giants exceed 4,000 m
        cap = 6190 if name in ALASKA_GIANTS else 4000
    if country == "Norway" and lat > 74: cap = 1717                                  # Svalbard
    if cap is None: return (e, "") if e <= 8849 else (round(e / 3.28084), "feet")
    if e <= cap * 1.01: return e, ""
    if e / 3.28084 <= cap * 1.01: return round(e / 3.28084), "feet"
    return None, "implausible"
