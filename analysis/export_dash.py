"""Export summary.json into flat CSVs for the dashboard."""
import os as _os
REPO = _os.environ.get("HARMONY_ROOT", _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import json, csv, os
OUT = f"{REPO}/data"
os.makedirs(OUT, exist_ok=True)
S = json.load(open(f"{REPO}/data/summary.json"))
METRICS = ["seventh_rate", "extended_rate", "chromatic_root_rate", "nondiatonic_rate", "applied_rate",
           "inversion_rate", "tonic_share", "dominant_share", "subdominant_share", "bVII_share",
           "minor_quality_share", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution",
           "down5th_share", "step_share", "third_share", "chord_entropy", "vocab40", "beats_per_chord",
           "cadences_per100", "pac_per100"]


def fmt(v):
    return "" if v is None or v != v else round(v, 4)


def flat(row):
    d = {}
    for k, v in row.items():
        if isinstance(v, list) and len(v) == 3:
            d[k] = fmt(v[0]); d[k + "_lo"] = fmt(v[1]); d[k + "_hi"] = fmt(v[2])
        elif isinstance(v, float):
            d[k] = fmt(v)
        else:
            d[k] = v
    return d


def write(name, rows):
    rows = list(rows)
    keys = list(rows[0].keys())
    with open(f"{OUT}/{name}", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(name, len(rows), "rows")


GENRE_LABEL = {"classical": "Classical", "jazz": "Jazz", "rock_pop": "Rock & pop"}

eras = []
for i, r in enumerate(S["eras"]):
    d = flat(r); d["order"] = i; d["era"] = d.pop("group"); d["genre_label"] = GENRE_LABEL[d["genre"]]
    d["mid_year"] = round((d["year_min"] + d["year_max"]) / 2)
    eras.append(d)
write("eras.csv", eras)

series = []
for r in S["series"]:
    d = flat(r); g, b = d.pop("group").split(":"); d["genre"] = g; d["genre_label"] = GENRE_LABEL[g]; d["bin_start"] = int(b)
    d["bin_mid"] = int(b) + (12 if g == "classical" else 5)
    d["period"] = f"{b}–{int(b) + (24 if g == 'classical' else 9)}"
    series.append(d)
series.sort(key=lambda d: (d["genre"], d["bin_start"]))
write("series.csv", series)

comps = []
for r in S["composers"]:
    d = flat(r); d["composer"] = d.pop("group"); comps.append(d)
write("composers.csv", comps)

write("top_chords.csv", [dict(era=e, rank=i + 1, chord=c, share=round(v, 4)) for e in S["era_order"] if e in S["top_chords"] for i, (c, v) in enumerate(S["top_chords"][e])])
write("transitions.csv", [dict(era=e, rank=i + 1, progression=f"{a} → {b}", from_chord=a, to_chord=b, share=round(v, 4)) for e in S["era_order"] if e in S["top_transitions"] for i, (a, b, v) in enumerate(S["top_transitions"][e])])
MOTION_LABEL = {"down5th": "Descending fifth", "up5th": "Ascending fifth", "stepUp": "Step up", "stepDown": "Step down", "thirdUp": "Third up", "thirdDown": "Third down", "tritone": "Tritone", "same": "Same root"}
write("motion.csv", [dict(era=e, motion=MOTION_LABEL[m], motion_key=m, share=round(v, 4)) for e in S["era_order"] if e in S["motion"] for m, v in S["motion"][e].items()])
DEG = ["I", "bII", "II", "bIII", "III", "IV", "#IV", "V", "bVI", "VI", "bVII", "VII"]
write("networks.csv", [dict(genre=g, genre_label=GENRE_LABEL[g], from_pc=i, to_pc=j, from_degree=DEG[i], to_degree=DEG[j], share=M[i][j])
                       for g, M in S["networks"].items() for i in range(12) for j in range(12)])
SRC_LABEL = {"DCML": "DCML Distant Listening Corpus (expert Roman-numeral analyses)",
             "WiR": "When in Rome corpus (expert Roman-numeral analyses)",
             "Billboard": "McGill Billboard (chart singles, chord symbols)",
             "RockCorpus": "Rock Corpus RS200 (expert Roman-numeral analyses)",
             "WeimarJazz": "Weimar Jazz Database (lead-sheet changes behind recorded solos)"}
write("sources.csv", [dict(source=r["source"], label=SRC_LABEL[r["source"]], pieces=r["pieces"], chords=r["chords"], year_min=r["ymin"], year_max=r["ymax"]) for r in S["totals"]["by_source"]])
