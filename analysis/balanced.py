"""Period-balanced resampling check: cap each composer at CAP pieces per era (random draw, 200 repeats)
so that Bach's 561 pieces or the 1960s-heavy Rock Corpus cannot dominate an era mean.
Output: data/balanced_eras.csv (mean and 2.5/97.5 percentiles over draws) and a comparison printout.
"""
import json, os
import numpy as np, pandas as pd

REPO = os.environ.get("HARMONY_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = pd.read_csv(f"{REPO}/data/pieces.csv")
M = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share",
     "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy", "vocab40"]
CAP, REPS = 30, 200
rng = np.random.default_rng(1)
rows = []
for era, g in P.groupby("era"):
    draws = []
    for _ in range(REPS):
        samp = g.groupby("composer", group_keys=False).apply(lambda c: c.sample(min(len(c), CAP), random_state=rng.integers(1e9)))
        draws.append(samp[M].mean())
    D = pd.DataFrame(draws)
    full = g[M].mean()
    row = dict(era=era, n_pieces=len(g), n_composers=g.composer.nunique())
    for m in M:
        row[m] = D[m].mean(); row[m + "_lo"] = D[m].quantile(0.025); row[m + "_hi"] = D[m].quantile(0.975); row[m + "_full"] = full[m]
    rows.append(row)
B = pd.DataFrame(rows)
order = json.load(open(f"{REPO}/data/summary.json"))["era_order"]
B["k"] = B.era.map({e: i for i, e in enumerate(order)}); B = B.sort_values("k").drop(columns="k")
B.to_csv(f"{REPO}/data/balanced_eras.csv", index=False)
diff = pd.DataFrame({m: (B[m] - B[m + "_full"]).abs().values for m in M}, index=B.era)
print("largest |balanced - full| per measure:"); print(diff.max().round(3).to_string())
print(B[["era", "n_pieces", "n_composers", "V_to_I_share", "V_to_I_share_full", "seventh_rate", "seventh_rate_full"]].round(3).to_string())
