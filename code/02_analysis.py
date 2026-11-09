"""Step 2: every number quoted anywhere goes into data/results.json; the page data into data/site.json.
Unit: a 'naming' is a mountain feature and a person it is named after (a feature named after two people counts twice).
Shares of birthplace are of namings whose person has a located birthplace. Antarctica (south of 60 S) is reported apart,
because nobody is born there: every Antarctic naming honours someone born on another continent."""
import pandas as pd, numpy as np
from common import *

K = pd.read_csv(f"{DATA}/peaks.csv", keep_default_na=False, na_values=[""])
P = pd.read_csv(f"{DATA}/people.csv", keep_default_na=False, na_values=[""])
CM = jload(f"{WORK}/clean_meta.json")
OV = pd.read_csv(f"{DATA}/overrides.csv")
RNM = pd.read_csv(f"{DATA}/renamings.csv")
pc = lambda a, b: round(100 * a / b, 2) if b else None
em = [elev_m(e, c, lo, la, n) for e, c, lo, la, n in zip(K.elev, K.country, K.lon, K.lat, K.name)]
K["elev_m"] = [x[0] for x in em]; K["elev_note"] = [x[1] for x in em]
# review: values below the country's highest point that are still feet (above a state or island high point, or the known height)
ft = K.mid.isin(OV[OV.field == "elev_feet"].wikidata_value); assert K[ft].mid.nunique() == (OV.field == "elev_feet").sum()
K.loc[ft, "elev_m"] = (K.loc[ft, "elev"] / 3.28084).round(); K.loc[ft, "elev_note"] = "feet"
K.to_csv(f"{DATA}/peaks.csv", index=False)
L = K[K.bcont.notna()]
NA = L[L.continent != "Antarctica"]
R = {"meta": {"page": PAGE, "repo": REPO}}
R["source"] = {"rows": CM["rows"], "features": int(K.mid.nunique()), "namings": len(K), "people": len(P), "people_located": int(P.blat.notna().sum()),
               "located_namings": len(L), "passes": CM["passes"], "off_earth": CM["off_earth"], "undersea": CM["undersea"], "not_mountains": CM["not_mountains"],
               "links_removed": CM["links_removed"], "bp_unmapped": int((OV.field == "birthplace_unknown").sum()),
               "bp_fixed": int((OV.field == "birthplace").sum()), "names_fixed": int((OV.field == "name").sum()),
               "multi": int((K.groupby("mid").pid.nunique() > 1).sum()), "elev_known": int(K.drop_duplicates("mid").elev_m.notna().sum()),
               "elev_feet": int((K.drop_duplicates("mid").elev_note == "feet").sum()), "elev_bad": int((K.drop_duplicates("mid").elev_note == "implausible").sum()),
               "antarctic": int(K[K.continent == "Antarctica"].mid.nunique()), "antarctic_pct": pc(K[K.continent == "Antarctica"].mid.nunique(), K.mid.nunique()),
               "countries": int(K[K.continent != "Antarctica"].country.nunique())}
# where the mountains are
fc = K.drop_duplicates("mid").continent.value_counts()
R["peak_cont"] = {c: int(fc.get(c, 0)) for c in CONT_ORDER + ["Ocean islands"]}
cty = K[K.continent != "Antarctica"].drop_duplicates("mid").country.value_counts()
R["peak_countries"] = [{"country": a, "n": int(b)} for a, b in cty.head(12).items()]

# born on another continent: the colonial survey layer
CO = {}
for c in ["Europe", "North America", "Oceania", "Asia", "South America", "Africa", "Ocean islands"]:
    g = L[L.continent == c]; bc = g.bcont.value_counts()
    CO[c] = {"n": len(g), "other_pct": pc((g.bcont != c).sum(), len(g)), "europe_pct": pc((g.bcont == "Europe").sum(), len(g)),
             "same_country_pct": pc((g.bctry == g.country).sum(), len(g)), "top_bcont": bc.index[0] if len(bc) else None,
             "bcont": {k: int(v) for k, v in bc.items()}}
R["cont"] = CO
AZ = L[L.country.isin(["Australia", "New Zealand"])]
R["anz"] = {"n": len(AZ), "other_pct": pc((AZ.bcont != "Oceania").sum(), len(AZ)), "europe_pct": pc((AZ.bcont == "Europe").sum(), len(AZ)),
            "oceania_n": len(L[L.continent == "Oceania"])}
R["outside"] = {"n": len(NA), "other_pct": pc((NA.bcont != NA.continent).sum(), len(NA)), "europe_born_pct": pc((NA.bcont == "Europe").sum(), len(NA)),
                "same_country_pct": pc((NA.bctry == NA.country).sum(), len(NA)),
                "noneurope_peaks_europe_born_pct": pc(((NA.continent != "Europe") & (NA.bcont == "Europe")).sum(), (NA.continent != "Europe").sum()),
                "noneurope_n": int((NA.continent != "Europe").sum())}
A = L[L.continent == "Antarctica"]
R["antarctica"] = {"n": len(A), "europe_pct": pc((A.bcont == "Europe").sum(), len(A)), "na_pct": pc((A.bcont == "North America").sum(), len(A))}
R["all_europe_born_pct"] = pc((L.bcont == "Europe").sum(), len(L))
# countries: share honouring people born elsewhere (countries with 25+ located namings outside Antarctica)
CT = []
for c, g in NA.groupby("country"):
    if len(g) >= 25:
        home = "Norway" if c == "Svalbard (Norway)" else c
        CT.append({"country": c, "n": len(g), "foreign_pct": pc((g.bctry != home).sum(), len(g)), "top_born": g.bctry.value_counts().index[0],
                   "top_foreign": [x for x in g[g.bctry != home].bctry.value_counts().head(3).index]})
R["countries"] = sorted(CT, key=lambda x: -x["n"])
R["country_n"] = {x["country"]: x for x in CT}
# what they did
oc = K.drop_duplicates(["mid", "pid"]).occ.value_counts(); known = oc.drop("unknown", errors="ignore").sum()
R["occ"] = {k: {"n": int(oc.get(k, 0)), "pct": pc(oc.get(k, 0), known), "name": OCC_NAME[k]} for k, *_ in OCC}
R["occ_unknown"] = int(oc.get("unknown", 0)); R["occ_names"] = OCC_NAME; R["occ_cols"] = OCC_COL
R["occ_by_cont"] = {c: {k: int(((K.continent == c) & (K.occ == k)).sum()) for k, *_ in OCC} for c in ["Europe", "North America", "Oceania", "Asia", "South America", "Antarctica"]}
# women
S = K[K.sex.isin(["female", "male"])]
W = K[K.sex == "female"]
R["women"] = {"n": len(W), "known": len(S), "pct": pc(len(W), len(S)), "people": int(P[P.sex == "female"].pid.nunique()),
              "royal": int((W.occ == "royal").sum()), "royal_pct": pc((W.occ == "royal").sum(), len(W)),
              "men_royal_pct": pc(((S.sex == "male") & (S.occ == "royal")).sum(), (S.sex == "male").sum()),
              "by_cont": {c: {"n": int((W.continent == c).sum()), "pct": pc((W.continent == c).sum(), (S.continent == c).sum())} for c in ["Europe", "North America", "Oceania", "Antarctica"]},
              "after1900_pct": pc(((W.born >= 1900)).sum(), (S.born >= 1900).sum()), "before1900_pct": pc(((W.born < 1900)).sum(), (S.born < 1900).sum())}
# the tallest
T = K[K.elev_m.notna()].sort_values("elev_m", ascending=False).drop_duplicates("mid")
R["tallest"] = [{"name": r.name, "elev": int(round(r.elev_m)), "person": r.person, "country": "Nepal and China" if r.name == "Mount Everest" else r.country, "born": r.bctry if isinstance(r.bctry, str) else "",
                 "feet": r.elev_note == "feet"} for r in T.head(15).itertuples()]
# distances
R["dist"] = {"median_km": int(L.dist_km.median()), "median_outside_km": int(NA.dist_km.median()),
             "over5000_pct": pc((NA.dist_km > 5000).sum(), len(NA)), "longest": [{"name": r.name, "person": r.person, "km": int(r.dist_km), "country": r.country, "bctry": r.bctry}
                                                                             for r in NA.sort_values("dist_km", ascending=False).head(5).itertuples()]}
# centuries of birth
cen = (K.born // 100 + 1).value_counts().sort_index()
R["born_median"] = int(K.born.median()); R["born_19c_pct"] = pc(K.born.between(1800, 1899).sum(), K.born.notna().sum())
R["cent"] = {int(k): int(v) for k, v in cen.items() if k >= 15}
# the most honoured people
PP = K.groupby(["pid", "person"]).mid.nunique().sort_values(ascending=False)
R["top_people"] = [{"name": n, "n": int(v)} for (p, n), v in PP.head(12).items()]
# renamings and dual names
R["dual"] = K[K.dual == 1].drop_duplicates("mid").name.tolist()
R["renamed"] = RNM.to_dict(orient="records")
R["renamed_away"] = int((RNM.direction == "away from a person").sum()); R["renamed_to"] = int((RNM.direction == "to a person").sum())
RW = pd.read_csv(REN, sep="\t", dtype=str, quoting=3); RW.columns = [c.lstrip("?") for c in RW.columns]
RW["type"] = RW.type.str.extract(r"(Q\d+)>$", expand=False)
MT = {"Q8502", "Q46831", "Q207326", "Q54050", "Q8072", "Q1595289", "Q133056", "Q39816", "Q1437459"}
# review fix: count each item once, mountains, summits, hills and ranges only (not valleys or passes), US, name ended in 2022
MT2 = {"Q8502", "Q46831", "Q207326", "Q54050", "Q8072", "Q1595289"}
sq = RW[RW.type.isin(MT2) & RW.name.str.contains("Squaw", na=False) & RW.end.str.startswith("2022", na=False) & RW.country.str.endswith("/Q30>", na=False)]
R["slur_renamed"] = int(sq.item.nunique()); R["slur_year"] = "2022"
R["checks"] = {"links_removed": CM["links_removed"], "bp_unmapped": R["source"]["bp_unmapped"]}
jsave(R, f"{DATA}/results.json", indent=1)

# ---------- page data
occ_k = [k for k, *_ in OCC] + ["unknown"]
conts = CONT_ORDER + ["Ocean islands"]
pidx = {p: i for i, p in enumerate(P.pid)}
r3 = lambda v: None if pd.isna(v) else round(float(v), 3)
people = [[r.pid, r.name, None if pd.isna(r.born) else int(r.born), r.sex, (r.birthplace if r.birthplace else (("near " + r.near_town) if isinstance(r.near_town, str) else "")),
           r3(r.blon), r3(r.blat), r.country if isinstance(r.country, str) else "", conts.index(r.continent) if isinstance(r.continent, str) and r.continent in conts else -1,
           occ_k.index(r.occ), r.occupations] for r in P.itertuples()]
peaks = [[r.mid, r.name, r3(r.lon), r3(r.lat), None if pd.isna(r.elev_m) else int(round(r.elev_m)), r.country if isinstance(r.country, str) else "",
          conts.index(r.continent), pidx[r.pid], None if pd.isna(r.dist_km) else int(r.dist_km), r.types, int(r.dual)] for r in K.itertuples()]
jsave({"pcols": ["pid", "name", "born", "sex", "bp", "lon", "lat", "country", "cont", "occ", "occs"],
       "kcols": ["mid", "name", "lon", "lat", "elev", "country", "cont", "p", "dist", "types", "dual"],
       "people": people, "peaks": peaks, "conts": conts, "ccol": [CCOL.get(c, "#9C9284") for c in conts],
       "occ": [[k, OCC_NAME.get(k, "Occupation not recorded"), OCC_COL[k]] for k in occ_k]}, f"{DATA}/site.json")
print("site", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")
print(R["source"]); print(R["cont"]); print(R["outside"]); print(R["occ"]); print(R["women"]); print(R["tallest"][:10]); print(R["countries"]); print(R["top_people"])
