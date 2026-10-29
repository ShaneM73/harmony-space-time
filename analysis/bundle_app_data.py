"""Bundle the tables the web app reads into data/harmony_data.json.
Run after space_time.py (and export_dash.py); composer_space.py writes its own composer_space.json.
"""
import json, os, re
import numpy as np, pandas as pd

REPO = os.environ.get("HARMONY_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = f"{REPO}/data"
rd = lambda f: pd.read_csv(f"{D}/{f}.csv")
norm = lambda s: re.sub(r"^the ", "", str(s).strip().lower())

def recs(df, nd=3):
    df = df.copy()
    for c in df.select_dtypes("float").columns: df[c] = df[c].round(nd)
    return [{k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in r.items()} for r in df.to_dict("records")]

comp = rd("composer_clusters"); cmap = {norm(u): int(c) for u, c in zip(comp.unit, comp.harmonic_cluster)}
pieces = rd("pieces_spacetime")
pieces["cluster"] = pieces.composer.map(lambda s: cmap.get(norm(s), 0))
pieces = pieces.drop(columns=["source", "chord_entropy"])
series = rd("series"); series = series[series.n_pieces >= 5].dropna(subset=["seventh_rate"])
series = series[["genre", "bin_mid", "period", "n_pieces", "seventh_rate", "seventh_rate_lo", "seventh_rate_hi", "extended_rate", "nondiatonic_rate",
                 "V_to_I_share", "V_to_I_share_lo", "V_to_I_share_hi", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share"]]
out = dict(pieces=recs(pieces), scenes=recs(rd("scenes")), composers=recs(comp), mantel=recs(rd("mantel")), eras=recs(rd("eras")),
           series=recs(series), top_chords=recs(rd("top_chords")), transitions=recs(rd("transitions")))
json.dump(out, open(f"{D}/harmony_data.json", "w"), ensure_ascii=False, separators=(",", ":"))
print({k: len(v) for k, v in out.items()})
