"""Step 1: parse the Wikidata extract, deduplicate, apply documented corrections and write the clean tables.

Outputs
  data/peaks.csv    one row per mountain feature and person it is named after: Wikidata ids, name, types, coordinates, elevation,
                    modern country and continent (Natural Earth; Antarctica south of 60 S), the person.
  data/people.csv   one row per person: name, sex, birth year, birthplace (item, label, coordinates), modern country and continent,
                    occupations and occupation group.
Mountain passes are left out (a pass is a gap, not a mountain) unless also typed as a mountain. Corrections are in
data/overrides.csv (field link: a wrong 'named after' link removed; birthplace_unknown: a birthplace that is only a country or
region; birthplace: a corrected birthplace; label: a missing name).
"""
import pandas as pd, numpy as np, geopandas as gpd
from shapely.geometry import Point
from common import *

LB = pd.read_csv(f"{DATA}/wikidata_labels.csv").set_index("qid").label.to_dict()
q = lambda s: re.sub(r".*/(Q\d+)>$", r"\1", s) if isinstance(s, str) else s
d = pd.read_csv(MTN, sep="\t", dtype=str, quoting=3); d.columns = [c.lstrip("?") for c in d.columns]
n_rows = len(d)
for c in ("m", "mtype", "mcountry", "p", "bplace", "bcountry", "sex", "occ"): d[c] = d[c].map(q)
for c in ("mLabel", "pLabel"): d[c] = d[c].str.extract(r'^"(.*)"', expand=False)
xy = d.mcoord.str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)").astype(float); d["lon"], d["lat"] = xy[0], xy[1]
bxy = d.bcoord.str.extract(r"POINT\(([-\d.eE]+) ([-\d.eE]+)\)").astype(float); d["blon"], d["blat"] = bxy[0], bxy[1]
d["elev"] = pd.to_numeric(d.elev, errors="coerce")
OV = pd.read_csv(f"{DATA}/overrides.csv")

# ---------- features
TYPE = {"Q8502": "mountain", "Q46831": "range", "Q207326": "summit", "Q54050": "hill", "Q133056": "pass", "Q8072": "volcano", "Q1595289": "sacred mountain"}
rows = []
for m, g in d.groupby("m", sort=True):
    types = sorted(set(TYPE.get(t, t) for t in g.mtype.dropna()))
    c = g.drop_duplicates(["lon", "lat"])
    spread = gc_km(c.lon.min(), c.lat.min(), c.lon.max(), c.lat.max()) if len(c) > 1 else 0.0
    lon, lat = float(c.lon.median()), float(c.lat.median())
    el = g.elev.dropna()
    for p, gp in g.groupby("p"):
        rows.append(dict(mid=m, name=g.mLabel.dropna().iloc[0] if g.mLabel.notna().any() else m, types="; ".join(types),
                         lon=lon, lat=lat, coord_spread_km=round(float(spread), 1), n_coords=len(c),
                         elev=float(el.max()) if len(el) else np.nan, n_elev=el.nunique(), wd_country=LB.get(g.mcountry.dropna().iloc[0], "") if g.mcountry.notna().any() else "",
                         pid=p, person=gp.pLabel.dropna().iloc[0] if gp.pLabel.notna().any() else p))
K = pd.DataFrame(rows)
n_pass = int(K[K.types == "pass"].mid.nunique())
K = K[K.types != "pass"].copy()
n_drop = int(K[K.mid.isin(OV[OV.field == "drop"].wikidata_value)].mid.nunique())
assert n_drop == (OV.field == "drop").sum()
K = K[~K.mid.isin(OV[OV.field == "drop"].wikidata_value)].copy()   # features that are not mountains (ravines, a road)
for o in OV[OV.field == "link"].itertuples():
    m = (K.mid == o.wikidata_value) & (K.pid == o.pid); assert m.sum() == 1, o
    K = K[~m]
for o in OV[OV.field == "name"].itertuples():
    m = K.mid == o.wikidata_value; assert m.sum() >= 1, o
    K.loc[m, "name"] = o.corrected_value
# features with no coordinates on Earth (on the Moon or Mars) and undersea ridges and rises are left out
n_off = int(K[K.lat.isna()].mid.nunique())
K = K[K.lat.notna()].copy()
for o in OV[OV.field == "elev"].itertuples():
    m = K.mid == o.wikidata_value; assert m.sum() >= 1, o
    K.loc[m, "elev"] = float(o.corrected_value)

# ---------- people
P = []
for p, g in d[d.p.isin(K.pid)].groupby("p"):
    b = g[g.blat.notna()].iloc[0] if g.blat.notna().any() else g.iloc[0]
    by = re.match(r"^(-?)0*(\d+)-", str(g.born.dropna().iloc[0])) if g.born.notna().any() else None
    occs = [LB.get(o, "") for o in g.occ.dropna().unique()]
    occs = [o for o in occs if o]
    grp = occ_group(occs)
    P.append(dict(pid=p, name=g.pLabel.dropna().iloc[0] if g.pLabel.notna().any() else p,
                  born=(-int(by.group(2)) if by.group(1) else int(by.group(2))) if by else None,
                  sex={"Q6581072": "female", "Q6581097": "male"}.get(g.sex.dropna().iloc[0], "") if g.sex.notna().any() else "",
                  bpid=b.bplace if isinstance(b.bplace, str) else "", birthplace=LB.get(b.bplace, "") if isinstance(b.bplace, str) else "",
                  blon=b.blon, blat=b.blat, wd_bcountry=LB.get(b.bcountry, "") if isinstance(b.bcountry, str) else "",
                  bcountry_qid=b.bcountry if isinstance(b.bcountry, str) else "",
                  n_bp=g.bplace.nunique(), occupations="; ".join(occs[:8]), occ=grp))
P = pd.DataFrame(P)
for o in OV[OV.field == "label"].itertuples():
    P.loc[P.pid == o.pid, "name"] = o.corrected_value
    K.loc[K.pid == o.pid, "person"] = o.corrected_value
for o in OV[OV.field == "birthplace"].itertuples():
    m = P.pid == o.pid; assert m.sum() == 1, o
    P.loc[m, ["birthplace", "blon", "blat", "bpid"]] = [o.corrected_value, o.blon, o.blat, "override"]
for o in OV[OV.field == "birthplace_unknown"].itertuples():
    m = P.pid == o.pid; assert m.sum() == 1, o
    P.loc[m, ["blon", "blat"]] = [np.nan, np.nan]
    P.loc[m, "birthplace"] = (P.loc[m, "birthplace"] + " (not mapped)").str.strip()
for o in OV[OV.field == "born"].itertuples():
    m = P.pid == o.pid; assert m.sum() == 1, o
    P.loc[m, "born"] = int(o.corrected_value)
for o in OV[OV.field == "occ"].itertuples():
    P.loc[P.pid == o.pid, "occ"] = o.corrected_value
for o in OV[OV.field == "sex"].itertuples():
    P.loc[P.pid == o.pid, "sex"] = o.corrected_value

# ---------- modern country and continent (Natural Earth), for peaks and birthplaces
ne = gpd.read_file(f"{GEO}/ne_10m_admin_0_countries.geojson")[["ADM0_A3", "ADMIN", "CONTINENT", "geometry"]]
REN_C = {"United States of America": "United States", "Republic of Serbia": "Serbia", "Czechia": "Czech Republic", "United Republic of Tanzania": "Tanzania", "The Bahamas": "Bahamas"}


def locate(df, lon, lat, key):
    has = df[lat].notna()
    pts = gpd.GeoDataFrame(df[has][[key]], geometry=[Point(a, b) for a, b in zip(df[has][lon], df[has][lat])], crs=4326)
    j = gpd.sjoin(pts, ne, how="left", predicate="within").drop_duplicates(key)
    miss = j[j.ADM0_A3.isna()][[key, "geometry"]]
    if len(miss):
        jn = gpd.sjoin_nearest(miss.to_crs(3857), ne.to_crs(3857), how="left", max_distance=60000).drop_duplicates(key)
        j = j.set_index(key); jn = jn.set_index(key)
        for c in ("ADM0_A3", "ADMIN", "CONTINENT"): j.loc[jn.index, c] = jn[c]
        j = j.reset_index()
    j = j.set_index(key)
    return df[key].map(j.ADMIN).replace(REN_C), df[key].map(j.CONTINENT), df[key].map(j.ADM0_A3)


K["key"] = K.mid + ":" + K.pid
K["country"], K["continent"], K["iso3"] = locate(K, "lon", "lat", "key")
K.loc[K.lat < -60, ["country", "continent"]] = ["Antarctica", "Antarctica"]
K.loc[(K.country == "Norway") & (K.lat > 74), "country"] = "Svalbard (Norway)"
K.loc[K.continent == "Seven seas (open ocean)", "continent"] = "Ocean islands"
n_sea = int(K[K.continent.isna()].mid.nunique())
K = K[K.continent.notna()].copy()   # undersea ridges and rises
P["country"], P["continent"], P["iso3"] = locate(P, "blon", "blat", "pid")
P.loc[P.continent == "Seven seas (open ocean)", "continent"] = None
for df in (K, P):
    cri = (df.iso3 == "RUS") & (df[df.columns[df.columns.isin(["lon", "blon"])][0]].between(32.4, 36.7)) & (df[df.columns[df.columns.isin(["lat", "blat"])][0]].between(44.3, 46.25))
    df.loc[cri, ["iso3", "country"]] = ["UKR", "Ukraine"]
# nearest Natural Earth town, as a fallback label where Wikidata's label is missing in the extract
pp = gpd.read_file(f"{GEO}/ne_10m_populated_places_simple.geojson")[["name", "geometry"]].to_crs(3857)
has = P.blat.notna()
pts = gpd.GeoDataFrame(P[has][["pid"]], geometry=[Point(a, b) for a, b in zip(P[has].blon, P[has].blat)], crs=4326).to_crs(3857)
jn = gpd.sjoin_nearest(pts, pp, how="left", distance_col="dist").drop_duplicates("pid").set_index("pid")
P["near_town"] = P.pid.map(jn["name"]); P["near_km"] = (P.pid.map(jn.dist / 1000) * np.cos(np.radians(P.blat))).round(0)
P["bp_label_src"] = np.where(P.birthplace != "", "wikidata", np.where(P.blat.notna(), "nearest town", ""))
P["n_peaks"] = P.pid.map(K.groupby("pid").mid.nunique()).fillna(0).astype(int)
K = K.merge(P[["pid", "blon", "blat", "continent", "country", "born", "sex", "occ"]].rename(columns={"continent": "bcont", "country": "bctry"}), on="pid", how="left")
K["dist_km"] = gc_km(K.lon, K.lat, K.blon, K.blat).round(0)
K["other_cont"] = np.where(K.bcont.notna() & K.continent.notna(), (K.bcont != K.continent).astype(float), np.nan)
K["dual"] = K.name.str.contains(" / ").astype(int)
K.drop(columns=["key"]).to_csv(f"{DATA}/peaks.csv", index=False)
P.to_csv(f"{DATA}/people.csv", index=False)
jsave({"rows": n_rows, "passes": n_pass, "off_earth": n_off, "undersea": n_sea, "not_mountains": n_drop, "links_removed": int((OV.field == "link").sum())}, f"{WORK}/clean_meta.json")
print(n_rows, "rows;", K.mid.nunique(), "features;", len(K), "pairs;", len(P), "people;", int(P.blat.notna().sum()), "located;", n_pass, "passes dropped")
print(K.continent.value_counts().to_dict()); print(P.occ.value_counts().to_dict())
