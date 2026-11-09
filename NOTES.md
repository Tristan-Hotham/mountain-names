# mountain-names: working notes
- Brief: /home/claude/work/new9/BRIEFS.md item 7 (+ shared rules new8/BRIEFS.md top, newdata/BRIEF.md). Sibling: moon-names (ink map assets copied from it).
- Raw: /home/claude/newdata/raw_new9/mountains.tsv.gz (Wikidata via QLever), renamed.tsv.gz for renamings.
- QID labels: the extract has no labels for occupations/types/birthplaces/countries; data/wikidata_labels.csv built from other local Wikidata
  extracts (header-matched item/label columns), CoDEx English entity labels (github tsafavi/codex) and occupation lists on GitHub
  (Datawheel/johnny5, mjsuhonos/wikicore-beta, Danysan1/osm-wikidata-map-framework, tig12/g5). ~93% of person-occupation pairs labelled.
- Pipeline: 01_clean -> 02_analysis -> 03_build_site -> 04_figures -> 05_paper -> reddit/collage.py -> 07_readme -> 06_release; qa.js (22/22 ok).
- Checks done on the whole set: all 237 name/namesake mismatches read (27 wrong links removed + 3 label fixes); multi-namesake features read;
  all birthplaces that are a country item, round-coordinate region centres or kingdoms/empires unmapped (59); Lyon Playfair birthplace fixed;
  no same-name duplicates within 5 km; elevations above the country's highest point read as feet (Alaska >4000 m only for named giants);
  top-15 elevations read by eye. Moon/Mars 'mountains' and undersea ridges dropped; passes dropped.
- Renamings: data/renamings.csv hand-curated from renamed.tsv (dated P1448) and P138 links to former names; years only where in the data
  (Denali 2015/2025, Black Elk 2016, Doso Doyabi 2019, Blue Sky 2023, Kuwohi 2024, Wunaamin-Miliwundi 2020 from knowledge: VERIFY).
- References to verify: Vrandecic & Kroetzsch 2014 CACM; Bast & Buchhold 2017 CIKM. Facts from general knowledge to verify: Everest
  name proposed by the Survey of India in the 1850s; Svalbard sovereignty 1925; Mount Peck formerly Mount Stalin; Lenin Hills -> Sparrow
  Hills; King Leopold Ranges renamed 2020; Lyon Playfair born at Chunar; California Geological Survey naming of Whitney/Brewer/Hoffmann/Dana.
- Independent review (2026): occupation grouping changed to tiers (code/common.py OCC_TIERS); 21 saint/religious dedication links,
  Mount Pétain (rescinded 2022) removed; 3 non-mountains dropped (2 ravines, a road); Kata Tjuta/Mount Olga person fixed (Queen Olga
  of Württemberg, b. 1822, St Petersburg); 11 more feet values and Mount Rogers fixed (state high points, ETOPO5 screen, by eye);
  AU+NZ share now computed on Australia and New Zealand only (results 'anz'); slur count = 96 US hills/peaks ended 2022 in Wikidata
  (federal total nearly 650, DOI press release 8 Sep 2022); map triangles fixed (the Ink fonts have no ▲ glyph; now icons);
  collage labels moved off the data. Verified: Everest 1856 Waugh / RGS 1865; Svalbard Treaty in force 14 Aug 1925; Playfair born
  Chunar; Whitney Survey named Dana 1863, Whitney 1864; Denali 2015, McKinley EO 2025 (Alaska Denali since 1975); Black Elk 2016;
  Doso Doyabi 2019 (not 2022); Blue Sky 2023; Kuwohi 2024; Mount Peck 1987; Wunaamin-Miliwundi 2020.
  Unresolved: Mount Ronald Adair -> Helen Adair McMaster and Mount Stanley (NZ) -> Bishop Edward Stanley look doubtful, unverified;
  31 people have only a QID as label (Wikidata not reachable); low feet values below any regional high point cannot be detected.
