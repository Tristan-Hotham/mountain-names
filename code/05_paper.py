"""Step 5: the paper. Fills code/paper_template.tex from data/results.json, adds tables and compiles with xelatex.
Output: release/paper/Hotham_Mountain_Names.pdf and .tex. The DOI is a placeholder (https://doi.org/10.5281/zenodo.24075305) unless the environment
variable DOI is set (DOI=10.5281/zenodo.N python3 05_paper.py), as the publisher does."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Mountain_Names"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")
assert len(R["dual"]) == 9 and R["top_people"][0]["name"] == "Ferdinand von Mueller"


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "f1": return f"{float(v):.1f}"
    return tex(str(v))


rows = "".join(f"{c} & {R['cont'][c]['n']:,} & {R['cont'][c]['europe_pct']:.1f} & {R['cont'][c]['other_pct']:.1f} & {R['cont'][c]['same_country_pct']:.1f}\\\\\n"
               for c in ["Europe", "North America", "Oceania", "South America", "Asia"])
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Located namings by continent of the mountain: share honouring someone born in Europe, on another "
      "continent, and in the same modern country.}\\label{tab:cont}\\begin{tabular}{lrrrr}\\toprule Continent & Namings & Born in Europe (\\%) & Other continent (\\%) & Same country (\\%)\\\\\\midrule\n"
      + rows + f"Antarctica & {R['antarctica']['n']:,} & {R['antarctica']['europe_pct']:.1f} & 100.0 & \\\\\n\\bottomrule\\end{{tabular}}\\end{{table}}")
rows = "".join(f"{tex(t['name'])} & {t['elev']:,}{'*' if t['feet'] else ''} & {tex(t['person'])} & {tex(t['country'])} & {tex(t['born'] or 'not mapped')}\\\\\n" for t in R["tallest"])
TT = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{The fifteen highest person-named mountains in Wikidata (* converted from feet).}\\label{tab:tall}"
      "\\begin{tabular}{lrlll}\\toprule Mountain & m & Named after & Country & Born in\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = "".join(f"{tex(r['name'])} & {tex(r['old_name'])} & {tex(r['old_person'] if isinstance(r['old_person'], str) else '')} & {'' if r['year'] != r['year'] or r['year'] is None else int(r['year'])}\\\\\n" for r in R["renamed"])
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Renamed mountains recorded in Wikidata.}\\label{tab:ren}"
      "\\begin{tabular}{p{4.2cm}p{3.6cm}p{3.6cm}r}\\toprule Now & Before & Honoured before & Year\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\url{{{meta.page}}}", "\\url{%s}" % PAGE).replace("\\url{{{meta.repo}}}", "\\url{%s}" % REPO).replace("{{AI}}", AI)
for k, v in (("CONT", TC), ("TALL", TT), ("REN", TR)):
    t = t.replace("{{TABLE_%s}}" % k, v)
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
DOI = os.environ.get("DOI")
t = t.replace("https://doi.org/10.5281/zenodo.24055580", f"\\url{{https://doi.org/{DOI}}}" if DOI else "\\{\\{DOI\\_URL\\}\\}")
assert "{{" not in t and "--" not in t and "—" not in t and "–" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:10])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"), "DOI_URL shown:", "https://doi.org/10.5281/zenodo.24075305" in txt)
