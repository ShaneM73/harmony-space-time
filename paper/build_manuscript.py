"""Assemble the manuscript and Supplementary Information from the exported doc, the data tables and the figures.
Outputs: paper/manuscript.md, paper/supplementary.md, and (via pandoc) paper/Manuscript_EN.docx, paper/Supplementary_Information_EN.docx
"""
import json, os, re, subprocess
import numpy as np, pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PAP = f"{REPO}/paper"; D = f"{REPO}/data"
src = open(f"{PAP}/manuscript_export.md").read()

# ------------------------------------------------------------ 1. main text
sec = re.split(r"^## ", src, flags=re.M)
parts = {s.split("\n", 1)[0].strip(): s.split("\n", 1)[1] for s in sec[1:]}
title = sec[0].split("\n")[0].lstrip("# ").strip()
def clean(t):
    t = t.replace("\\[", "(").replace("\\]", ")")
    t = re.sub(r"\(Fig\. (\d)([a-f]?)\)", r"(Fig. \1\2)", t)
    return t.strip()

front = f"""---
title: "{title}"
---

**Xin (Shane) Miao**

Department of Geography, Geology and Planning, Missouri State University, Springfield, MO 65897, USA. Correspondence: xinmiao@missouristate.edu

**Short title:** Harmony across four centuries

**Keywords:** corpus musicology; harmonic syntax; cultural evolution; computational music analysis; music geography; cadence; chromaticism

**Manuscript for** *Humanities and Social Sciences Communications* (Article). Main text about 6,500 words; 5 figures; 3 tables; Supplementary Information with 9 tables, 2 figures and 1 data file.
"""

# ------------------------------------------------------------ 2. tables
S = json.load(open(f"{D}/summary.json")); ORDER = S["era_order"]
srcs = pd.read_csv(f"{D}/sources.csv")
T1 = ["| Corpus | Annotation | Pieces | Chord events | Years | Dating |", "| --- | --- | --- | --- | --- | --- |"]
INFO = {"DCML": ("Distant Listening Corpus (DCML, EPFL)", "Roman numerals, DCML standard", "composition date from corpus metadata"),
        "WiR": ("When in Rome meta-corpus", "Roman numerals, several analytical traditions", "per opus or collection, ±5 years"),
        "WeimarJazz": ("Weimar Jazz Database", "lead-sheet chord symbols under transcribed solos", "recording year"),
        "Billboard": ("McGill Billboard", "Harte chord symbols with tonic", "chart entry year"),
        "RockCorpus": ("Rock Corpus (RS200)", "Roman numerals", "release year")}
for r in S["totals"]["by_source"]:
    nm, ann, dat = INFO[r["source"]]; T1.append(f"| {nm} | {ann} | {r['pieces']:,} | {r['chords']:,} | {r['ymin']}–{r['ymax']} | {dat} |")
T1.append(f"| **Total** | | **{S['totals']['pieces']:,}** | **{S['totals']['chords']:,}** | 1565–2007 | |")
T1 = "**Table 1. Corpora.** Pieces are those with at least eight chord events after merging repeated chords; years are the range of piece dates.\n\n" + "\n".join(T1)

EB = pd.read_csv(f"{D}/eras_clusterboot.csv").set_index("group").loc[ORDER]
E0 = pd.DataFrame([{k: (v[0] if isinstance(v, list) else v) for k, v in e.items()} for e in S["eras"]]).set_index("group").loc[ORDER]
cols = [("seventh_rate", "Sevenths"), ("extended_rate", "9ths+"), ("nondiatonic_rate", "Non-diatonic"), ("chromatic_root_rate", "Chromatic roots"), ("V_to_I_share", "V→I"), ("IV_to_I_share", "IV→I"), ("bVII_to_I_share", "bVII→I"), ("dom_resolution", "V→I resolves"), ("down5th_share", "Desc. 5ths"), ("step_share", "Steps"), ("third_share", "Thirds")]
def fmt(e, m):
    v, lo, hi = EB.loc[e, m], EB.loc[e, m + "_lo"], EB.loc[e, m + "_hi"]
    return "–" if pd.isna(v) else f"{v*100:.0f} ({lo*100:.0f}–{hi*100:.0f})"
SHORT = {"Renaissance (<1600)": "Renaissance <1600", "Early Baroque (1600-99)": "Early Baroque 1600–99", "Late Baroque (1700-49)": "Late Baroque 1700–49", "Classical (1750-99)": "Classical 1750–99", "Early Romantic (1800-49)": "Early Romantic 1800–49", "Late Romantic (1850-99)": "Late Romantic 1850–99", "Early 20th c. (1900-49)": "Early 20th c. 1900–49", "Jazz: Swing era (<1945)": "Jazz: swing <1945", "Jazz: Bebop/Hard bop (1945-59)": "Jazz: bebop 1945–59", "Jazz: Modal/Post-bop (1960-74)": "Jazz: post-bop 1960–74", "Jazz: 1975+": "Jazz 1975+", "Rock/Pop 1950-64": "Popular 1950–64", "Rock/Pop 1965-74": "Popular 1965–74", "Rock/Pop 1975-84": "Popular 1975–84", "Rock/Pop 1985+": "Popular 1985+"}
ca = [("seventh_rate", "Sevenths"), ("extended_rate", "9ths+"), ("nondiatonic_rate", "Non-diatonic"), ("chromatic_root_rate", "Chromatic roots")]
cb = [("V_to_I_share", "V→I"), ("IV_to_I_share", "IV→I"), ("bVII_to_I_share", "bVII→I"), ("dom_resolution", "V→I resolves"), ("down5th_share", "Desc. 5ths"), ("step_share", "Steps"), ("third_share", "Thirds")]
T2a = ["| Era | Pieces | Composers | Minor % | " + " | ".join(c[1] for c in ca) + " | Vocab/40 | Entropy (bits) |", "| --- | --- | --- | --- | " + " | ".join("---" for _ in ca) + " | --- | --- |"]
T2b = ["| Era | " + " | ".join(c[1] for c in cb) + " |", "| --- | " + " | ".join("---" for _ in cb) + " |"]
for e in ORDER:
    vv = "–" if pd.isna(EB.loc[e, "vocab40"]) else f"{EB.loc[e, 'vocab40']:.1f} ({EB.loc[e, 'vocab40_lo']:.1f}–{EB.loc[e, 'vocab40_hi']:.1f})"
    T2a.append(f"| {SHORT[e]} | {int(EB.loc[e, 'n_pieces'])} | {int(EB.loc[e, 'n_composers'])} | {E0.loc[e, 'minor_mode_share'] * 100:.0f} | " + " | ".join(fmt(e, m) for m, _ in ca) + f" | {vv} | {E0.loc[e, 'transition_entropy']:.2f} |")
    T2b.append(f"| {SHORT[e]} | " + " | ".join(fmt(e, m) for m, _ in cb) + " |")
T2 = ("**Table 2. Era summary.** (a) Chord quality, vocabulary and predictability; (b) cadential syntax and root motion. Values are means of per-piece values in per cent, with 95% composer-cluster bootstrap intervals in parentheses; Vocab/40 is the expected number of distinct chord types in 40 chords; entropy is the pooled entropy of the next chord given the current chord. Popular seventh and extension rates are from Billboard only. Minor % is the share of minor-mode pieces.\n\n**(a)**\n\n" + "\n".join(T2a) + "\n\n**(b)**\n\n" + "\n".join(T2b))
M = pd.read_csv(f"{D}/mantel.csv"); RC = json.load(open(f"{D}/revision_checks.json")); MB = pd.DataFrame(RC["mantel_bh"])
f = lambda r, p, pb: f"{r:.2f} ({p:.3f}; {pb:.3f})".replace("-", "−")
T3 = ["| Subset | n | Harmony ~ time | Harmony ~ geography | Geography given time | Time given geography |", "| --- | --- | --- | --- | --- | --- |"]
for i, r in MB.iterrows():
    T3.append(f"| {r.subset} | {int(r.n_units)} | {f(r.r_harmony_time, r.p_time, r.p_time_bh)} | {f(r.r_harmony_geo, r.p_geo, r.p_geo_bh)} | {f(r.r_geo_given_time, r.p_geo_given_time, r.p_geo_given_time_bh)} | {f(r.r_time_given_geo, r.p_time_given_geo, r.p_time_given_geo_bh)} |")
g = RC["mantel_modern_genre"]
T3.append(f"| modern artists, geography given time and genre | {g['n']} | | | {g['r_geo_given_time_genre']:.2f} ({g['p_given_genre']:.3f}) | {g['r_time_given_geo_genre']:.2f} ({g['p_time_given_genre']:.3f}) |".replace("-", "−"))
T3 = "**Table 3. Mantel and partial Mantel tests.** Pearson correlations between distance matrices (harmonic: Euclidean in the standardised 14-measure space; temporal: difference of median years; geographic: great-circle distance between cities), with permutation p-values (5,000 permutations) and, after the semicolon, Benjamini–Hochberg-adjusted p-values over the twenty tests. The last row adds a same-genre indicator matrix as a second covariate.\n\n" + "\n".join(T3)

LEG = {
1: "**Figure 1. Harmonic trajectories, 1565–2000.** Era means of per-piece values for classical (blue), jazz (orange) and popular music (green), with 95% composer-cluster bootstrap bands. (a) Share of chord events carrying a seventh (solid) or a ninth or higher extension (dashed); popular values from Billboard only. (b) Share of arrivals on the tonic prepared by V (solid), IV (dashed) and bVII (dotted). (c) Probability that a chord on scale degree 5 is followed by one on degree 1. (d) Non-diatonic chords (solid) and chords on chromatic roots (dashed). (e) Expected number of distinct chord types in a random sample of 40 chords. (f) Entropy of the next chord given the current chord, pooled per era.",
2: "**Figure 2. Three grammars of root motion.** (a) Share of all root moves by class per era: descending fifth, ascending fifth, step (one or two semitones), third, other (tritone, repetition). Era labels are coloured by repertoire. (b) The six most frequent chord labels, as a share of chord events, in six representative eras.",
3: "**Figure 3. Composers and artists on one harmonic map.** The 136 composers and artists with at least five located pieces on the first two principal components of the standardised 14-measure harmonic profile. Colour gives the Ward group, shape the repertoire, marker size the logarithm of the number of pieces; faded markers have a bootstrap membership confidence below 0.5. Selected names are shown.",
4: "**Figure 4. The space-time frame.** (a) The 3,318 located pieces at the city where they were made, coloured by year, with the largest scenes labelled (points jittered by 0.25°). (b) The same pieces at (longitude, latitude, year), coloured by the harmonic group of their scene, with scenes of more than 120 pieces labelled. The interactive version at shanem73.github.io/harmony-space-time can be rotated and filtered by year.",
5: "**Figure 5. Robustness.** (a–c) Single-break least-squares fits to piece-level classical values of the V→I share, the descending-fifth share and the chromatic-root rate; grey dots are 20-year bin means sized by the number of pieces, the dashed line the fitted break year and the shaded band its 95% bootstrap interval. (d) The notation check: for twelve recordings transcribed in both the Rock Corpus (Roman numerals) and McGill Billboard (chord symbols), the mean of each measure in each corpus, the paired correlation r, and the Wilcoxon p-value where below 0.05."}

figs = "\n\n".join(f"![]({PAP}/figures/fig{k}_{n}.png){{ width=100% }}\n\n{LEG[k]}" for k, n in [(1, "trajectories"), (2, "root_motion"), (3, "composer_map"), (4, "space_time"), (5, "robustness")])

main = (front + "\n## Abstract\n\n" + clean(parts["Abstract"]) + "\n\n## Introduction\n\n" + clean(parts["Introduction"]) + "\n\n## Results\n\n" + clean(parts["Results"]) +
        "\n\n## Discussion\n\n" + clean(parts["Discussion"]) + "\n\n## Methods\n\n" + clean(parts["Methods"]) + "\n\n" + clean(parts["Statements"]).replace("**Data availability.**", "## Data availability\n\n").replace("**Code availability.**", "\n\n## Code availability\n\n").replace("**Author contributions.**", "\n\n## Author contributions\n\n").replace("**Competing interests.**", "\n\n## Competing interests\n\n").replace("**Ethics.**", "\n\n## Ethics\n\n").replace("**Use of artificial intelligence.**", "\n\n## Use of artificial intelligence\n\n").replace("**Funding.**", "\n\n## Funding\n\n") +
        "\n\n## References\n\n" + clean(parts["References"]).split("\n", 2)[2] + "\n\n## Tables\n\n" + T1 + "\n\n" + T2 + "\n\n" + T3 + "\n\n## Figures\n\n" + figs + "\n")
main = re.sub(r"^\d+\. ", lambda m: m.group(0), main, flags=re.M)
open(f"{PAP}/manuscript.md", "w").write(main)

# ------------------------------------------------------------ 3. supplementary
def md_table(df, caption, floatfmt="{:.3f}"):
    cells = [[(floatfmt.format(v) if isinstance(v, (float, np.floating)) and not pd.isna(v) else ("" if (isinstance(v, float) and pd.isna(v)) else str(v))) for v in r.values] for _, r in df.iterrows()]
    widths = [max([len(str(c))] + [len(row[i]) for row in cells]) for i, c in enumerate(df.columns)]
    widths = [min(max(7, int(w * 0.6) + 2), 22) for w in widths]
    out = [caption, "", "| " + " | ".join(map(str, df.columns)) + " |", "| " + " | ".join("-" * w for w in widths) + " |"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join((floatfmt.format(v) if isinstance(v, (float, np.floating)) and not pd.isna(v) else ("" if (isinstance(v, float) and pd.isna(v)) else str(v))) for v in r.values) + " |")
    return "\n".join(out)
P = pd.read_csv(f"{D}/pieces.csv")
S1 = P.groupby(["era", "source"]).agg(pieces=("piece_id", "size"), chords=("n_chords", "sum"), composers=("composer", "nunique"), minor=("key_mode", lambda s: (s == "minor").mean())).reset_index()
S1["k"] = S1.era.map({e: i for i, e in enumerate(ORDER)}); S1 = S1.sort_values(["k", "source"]).drop(columns="k"); S1["minor"] = (S1.minor * 100).round(0).astype(int)
S1.columns = ["Era", "Corpus", "Pieces", "Chord events", "Composers/artists", "Minor-mode %"]
S1t = md_table(S1, "**Supplementary Table S1. Pieces, chord events and composers per era and corpus.**", "{:.0f}")
C = pd.read_csv(f"{D}/composers.csv").sort_values("median_year")
C2 = C[["composer", "median_year", "n_pieces", "seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share", "dom_resolution", "down5th_share", "step_share", "chord_entropy", "vocab40"]].copy()
for c in C2.columns[3:13]: C2[c] = (C2[c] * 100).round(0)
C2["chord_entropy"] = C["chord_entropy"].round(2); C2["vocab40"] = C.vocab40.round(1); C2["median_year"] = C2.median_year.astype(int)
C2.columns = ["Composer", "Median year", "Pieces", "Sevenths %", "9ths+ %", "Non-diatonic %", "Chromatic roots %", "V→I %", "IV→I %", "V→I resolves %", "Desc. 5ths %", "Steps %", "Entropy", "Vocab/40"]
S2t = md_table(C2, "**Supplementary Table S2. Composer-by-composer harmonic profile** (classical composers with five or more pieces; means of per-piece values).", "{:.0f}")
SC = pd.read_csv(f"{D}/scenes.csv")
S3 = SC[["scene", "n_pieces", "year_min", "year_max", "cities", "top_composers", "seventh_rate", "nondiatonic_rate", "V_to_I_share", "IV_to_I_share", "down5th_share", "chord_entropy", "harmonic_group"]].copy()
for c in ["seventh_rate", "nondiatonic_rate", "V_to_I_share", "IV_to_I_share", "down5th_share"]: S3[c] = (S3[c] * 100).round(0)
S3["chord_entropy"] = S3.chord_entropy.round(2)
S3.columns = ["Scene", "Pieces", "From", "To", "Cities (pieces)", "Main composers (pieces)", "Sevenths %", "Non-diatonic %", "V→I %", "IV→I %", "Desc. 5ths %", "Entropy", "Harmonic group"]
S3t = md_table(S3, "**Supplementary Table S3. The 25 space-time scenes** (Ward clustering of located pieces in the space-time frame; harmonic group from Ward clustering of scene profiles at four groups).", "{:.0f}")
R = json.load(open(f"{D}/robustness.json")); nt = R["notation"]["metrics"]; nci = RC["notation_ci"]
S4 = pd.DataFrame([dict(Measure=m, n=v["n"], **{"Rock Corpus": round(v["rock_mean"], 3), "Billboard": round(v["billboard_mean"], 3), "Mean difference (BB − RC)": round(v["mean_diff"], 3), "95% CI of difference": f"{nci[m]['ci95'][0]:+.3f} to {nci[m]['ci95'][1]:+.3f}", "Range across popular eras": round(nci[m]["pop_era_range"], 3), "r": round(v["r"], 2), "Wilcoxon p": round(v["p_wilcoxon"], 3)}) for m, v in nt.items()])
S4t = md_table(S4, "**Supplementary Table S4. Notation check.** Twelve recordings transcribed in both the Rock Corpus and McGill Billboard (Be My Baby; Born To Be Wild; Eight Miles High; Help!; Honky Tonk Women; I Saw Her Standing There; In The Midnight Hour; Maggie May; Sunshine Of Your Love; The Sounds Of Silence; Will You Love Me Tomorrow; With Or Without You). The last column but two gives, for comparison, the range of the era means of that measure across the four popular-music periods.")
mx = R["mixed_classical"]; mm = RC["mixed_mode_adjusted"]
rows = []
for m in mm:
    a, b = mx.get(m, {}), mm[m]
    rows.append({"Measure": m, "Slope per century (no mode)": (f"{a['slope']:+.3f}" if a else ""), "Hinge after 1850 (no mode)": f"{a.get('hinge', float('nan')):+.3f} [{a.get('hinge_ci', [float('nan')]*2)[0]:+.3f}, {a.get('hinge_ci', [float('nan')]*2)[1]:+.3f}]" if a else "", "Slope (mode-adjusted)": f"{b['slope']:+.3f}", "Hinge (mode-adjusted)": f"{b['hinge']:+.3f} [{b['hinge_ci'][0]:+.3f}, {b['hinge_ci'][1]:+.3f}]", "Minor-mode effect": f"{b['minor']:+.3f} [{b['minor_ci'][0]:+.3f}, {b['minor_ci'][1]:+.3f}]", "Composer SD / residual SD": (f"{a['composer_sd']:.3f} / {a['resid_sd']:.3f}" if a else "")})
S5t = md_table(pd.DataFrame(rows), "**Supplementary Table S5. Mixed-effects models for the classical measures** (metric ~ year per century centred on 1750 + hinge after 1850 + corpus [+ mode], random intercept per composer; REML, 59 composers, 2,058 pieces). Brackets give 95% confidence intervals. The cross-repertoire model (year × genre, random intercept per artist) gives V→I share slopes of −0.02 per century (classical), −0.23 (jazz) and −0.33 (popular) over 1900–2000.")
cp = R["changepoints"]
S6 = pd.DataFrame([dict(Measure=m, n=v["n"], **{"Best single break": int(v["break1"]), "95% bootstrap CI": f"{v['ci'][0]:.0f}–{v['ci'][1]:.0f}", "ΔBIC single break vs linear": round(v["dbic_1_vs_0"], 1), "Best two breaks": f"{v['breaks2'][0]:.0f}, {v['breaks2'][1]:.0f}", "ΔBIC two breaks vs one": round(v["dbic_2_vs_1"], 1)}) for m, v in cp.items()])
S6t = md_table(S6, "**Supplementary Table S6. Change points in the classical series** (least-squares hinge regression on piece-level values, candidate years 1600–1910 in 5-year steps, 200 bootstrap resamples; positive ΔBIC favours the more complex model).", "{:.1f}")
nc = R["no_chord"]; rows = []
for k, (a, b) in nc.items():
    e, m = k.split("|")
    if m in ("V_to_I_share", "IV_to_I_share", "dom_resolution", "down5th_share"): rows.append({"Era": e, "Measure": m, "Default": round(a, 3), "Strict": round(b, 3), "Difference": round(b - a, 3)})
S7t = md_table(pd.DataFrame(rows), "**Supplementary Table S7. No-chord handling.** Era means with no-chord stretches bridged (default) and treated as breaks in the progression (strict).")
S8 = pd.DataFrame([{"Variant": k, "Adjusted Rand index vs published six groups": round(v, 2)} for k, v in R["cluster_sensitivity"].items()])
S8t = md_table(S8, "**Supplementary Table S8. Cluster sensitivity.**", "{:.2f}")
rows = []
for c, d in RC["dcml_vs_wir"].items():
    for s, v in d.items(): rows.append({"Composer": c, "Corpus": s, "Pieces": v["n"], "Sevenths": round(v["seventh_rate"], 3), "Non-diatonic": round(v["nondiatonic_rate"], 3), "Chromatic roots": round(v["chromatic_root_rate"], 3), "V→I share": round(v["V_to_I_share"], 3), "Desc. 5ths": round(v["down5th_share"], 3), "Entropy": round(v["chord_entropy"], 2)})
S9t = md_table(pd.DataFrame(rows), "**Supplementary Table S9. Composers present in both classical corpora**, per-corpus means (different pieces in each corpus).")
SI = f"""---
title: "Supplementary Information for: {title}"
---

**Xin (Shane) Miao**, Missouri State University. xinmiao@missouristate.edu

This file contains Supplementary Tables S1–S9 and Supplementary Figures S1–S2. Supplementary Data 1 (the location table with a cited source for each of the 412 musician entries) is the file `locations_sources.csv` in the repository github.com/ShaneM73/harmony-space-time.

{S1t}

{S2t}

{S3t}

{S4t}

{S5t}

{S6t}

{S7t}

{S8t}

{S9t}

## Supplementary Figures

![]({PAP}/figures/figS1_series.png){{ width=100% }}

**Supplementary Figure S1. Fine-grained series.** The twelve profile measures by quarter-century (classical) and decade (jazz, popular), bins with at least five pieces; bands are 95% piece-level bootstrap intervals.

![]({PAP}/figures/figS2_balanced.png){{ width=100% }}

**Supplementary Figure S2. Period-balanced resampling.** Era means after capping every composer at 30 pieces per era (circles, with 95% intervals over 200 random draws) against the means over all pieces (squares), for three measures.

## Supplementary Data 1

`locations_sources.csv`: one row per musician entry (412 rows: 59 classical composers, 74 jazz performers, 279 popular artists) with columns name, genre, status (confirmed / corrected / uncertain), confidence, timeline (the city or cities assigned, with from-years), basis (one-sentence evidence), source_title, source_url, new_city_latlon.
"""
open(f"{PAP}/supplementary.md", "w").write(SI)
print("markdown written", len(main), len(SI))
