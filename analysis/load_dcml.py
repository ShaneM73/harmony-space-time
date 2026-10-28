"""Load DCML Distant Listening Corpus harmony TSVs into the unified schema."""
import os as _os
REPO = _os.environ.get("HARMONY_ROOT", _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import glob, os, sys
import pandas as pd
from common import COLUMNS, is_diatonic

ROOT = sys.argv[1] if len(sys.argv) > 1 else f"{REPO}/corpora/dlc"
OUT = sys.argv[2] if len(sys.argv) > 2 else f"{REPO}/data/chords_dcml.csv"

QUAL = {  # chord_type -> (quality, seventh_type)
    "M": ("maj", ""), "m": ("min", ""), "o": ("dim", ""), "+": ("aug", ""),
    "Mm7": ("maj", "dom7"), "mm7": ("min", "min7"), "MM7": ("maj", "maj7"),
    "mM7": ("min", "minmaj7"), "o7": ("dim", "dim7"), "%7": ("dim", "hdim7"),
    "+7": ("aug", "aug7"), "+M7": ("aug", "augmaj7"),
    "Ger": ("aug6", "aug6"), "It": ("aug6", "aug6"), "Fr": ("aug6", "aug6"),
}
INV = {"": 0, "6": 1, "64": 2, "7": 0, "65": 1, "43": 2, "2": 3, "42": 3, "9": 0}

meta = pd.read_csv(os.path.join(ROOT, "distant_listening_corpus.metadata.tsv"),
                   sep="\t", dtype=str, keep_default_na=False)
meta["year"] = pd.to_numeric(meta["composed_end"], errors="coerce")
meta = meta.set_index(["corpus", "piece"])

rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "*/harmonies/*.harmonies.tsv"))):
    corpus = f.split(os.sep)[-3]
    piece = os.path.basename(f).replace(".harmonies.tsv", "")
    try:
        m = meta.loc[(corpus, piece)]
    except KeyError:
        continue
    d = pd.read_csv(f, sep="\t", dtype=str, keep_default_na=False)
    if "chord_type" not in d.columns:
        continue
    year = m["year"]
    composer = m["composer"].strip()
    title = (m["workTitle"] or m["title_text"] or piece).strip()
    gmode = "minor" if m.get("annotated_key", "") and m["annotated_key"][:1].islower() else "major"
    i = 0
    for r in d.itertuples(index=False):
        ct = r.chord_type
        if ct == "" or r.numeral == "" or r.chord in ("@none", ""):
            continue
        q, s7 = QUAL.get(ct, ("other", ""))
        try:
            root_pc = (int(r.root) * 7) % 12
        except ValueError:
            continue
        lmode = "minor" if r.localkey_is_minor == "1" else "major"
        ch = r.changes
        has9 = any(x in ch for x in ("9", "11", "13"))
        if has9:
            ext = "9+"
        elif s7:
            ext = "7"
        elif "6" in r.changes and r.figbass == "" and "+6" in ch:
            ext = "add6"
        else:
            ext = "triad"
        rows.append(dict(
            source="DCML", genre="classical", piece_id=f"dcml:{corpus}/{piece}",
            composer=composer, title=title, year=year, key_mode=gmode,
            idx=i, root_pc=root_pc, quality=q, ext=ext, seventh_type=s7,
            chromatic_root=not is_diatonic(root_pc, lmode),
            applied=r.relativeroot != "",
            inversion=INV.get(r.figbass, 0),
            dur=float(r.duration_qb) if r.duration_qb else None,
            cadence=r.cadence, label=r.chord,
        ))
        i += 1

df = pd.DataFrame(rows, columns=COLUMNS)
df.to_csv(OUT, index=False)
print(df.shape, df.piece_id.nunique(), "pieces", df.composer.nunique(), "composers")
print(df.year.describe())
