"""Checks added at revision (reviewer round 1).
1. Mode-adjusted mixed models (key_mode as a fixed effect) for the classical measures.
2. Mantel tests with a genre partial for the modern subset; Benjamini-Hochberg FDR over all Mantel p-values.
3. Permutation null for the piece-level nearest-neighbour statistics (classical).
4. Paired-difference CIs for the notation check, against the size of between-era differences.
5. DCML vs When in Rome: composers present in both corpora, per-corpus means.
6. Composer-cluster bootstrap intervals for the era table.
Output: data/revision_checks.json and data/eras_clusterboot.csv
"""
import json, os, warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from scipy.spatial.distance import pdist, squareform

warnings.filterwarnings("ignore")
REPO = os.environ.get("HARMONY_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = pd.read_csv(f"{REPO}/data/pieces.csv")
rng = np.random.default_rng(7)
out = {}

# 1 ---------------------------------------------------------------- mode-adjusted mixed models
CL = P[P.genre == "classical"].copy(); CL["yc"] = (CL.year - 1750) / 100; CL["hinge"] = np.clip(CL.year - 1850, 0, None) / 100; CL["corpus"] = CL.source; CL["minor"] = (CL.key_mode == "minor").astype(float)
mm = {}
for m in ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share", "dom_resolution", "down5th_share", "step_share", "chord_entropy"]:
    d = CL.dropna(subset=[m])
    r = smf.mixedlm(f"{m} ~ yc + hinge + corpus + minor", d, groups=d.composer).fit(reml=True, method="powell", maxiter=3000)
    ci = r.conf_int()
    mm[m] = dict(slope=float(r.params["yc"]), slope_ci=[float(ci.loc["yc", 0]), float(ci.loc["yc", 1])], hinge=float(r.params["hinge"]), hinge_ci=[float(ci.loc["hinge", 0]), float(ci.loc["hinge", 1])],
                 minor=float(r.params["minor"]), minor_ci=[float(ci.loc["minor", 0]), float(ci.loc["minor", 1])], n=int(r.nobs))
out["mixed_mode_adjusted"] = mm
print("mode-adjusted:"); print(pd.DataFrame(mm).T[["slope", "hinge", "hinge_ci", "minor"]].round(3).to_string())

# 2 ---------------------------------------------------------------- Mantel with genre partial + FDR
comp = pd.read_csv(f"{REPO}/data/composer_clusters.csv"); PL = pd.read_csv(f"{REPO}/data/pieces_located.csv"); PL = PL[PL.city.notna()]
F = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy", "tonic_share", "minor_quality_share"]
PF = PL[F].fillna(PL[F].median()); Z = ((comp[F] - PF.mean()) / PF.std()).fillna(0).values
def geo_km(df):
    lat = np.radians(df.lat.values)[:, None]; lon = np.radians(df.lon.values)[:, None]
    a = np.sin((lat - lat.T) / 2) ** 2 + np.cos(lat) * np.cos(lat.T) * np.sin((lon - lon.T) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
def mantel_partial(A, B, covs, n=5000):
    """correlation of A and B after regressing both on the covariate matrices (upper triangles)."""
    m = A.shape[0]; iu = np.triu_indices(m, 1)
    X = np.column_stack([np.ones(len(iu[0]))] + [c[iu] for c in covs])
    def resid(v): beta, *_ = np.linalg.lstsq(X, v, rcond=None); return v - X @ beta
    ra = resid(A[iu]); r = np.corrcoef(ra, resid(B[iu]))[0, 1]; null = []
    for _ in range(n):
        p = rng.permutation(m); null.append(np.corrcoef(ra, resid(B[np.ix_(p, p)][iu]))[0, 1])
    return float(r), float((np.sum(np.array(null) >= r) + 1) / (n + 1))
mod = comp.genre != "classical"; idx = np.where(mod)[0]
H = squareform(pdist(Z[idx])); T = np.abs(comp.year.values[idx][:, None] - comp.year.values[idx][None, :]); G = geo_km(comp.iloc[idx])
gv = np.array(comp.genre.values[idx], dtype=object); gen = (gv[:, None] != gv[None, :]).astype(float)
r1, p1 = mantel_partial(H, G, [T]); r2, p2 = mantel_partial(H, G, [T, gen]); r3, p3 = mantel_partial(H, T, [G, gen])
out["mantel_modern_genre"] = dict(n=int(len(idx)), r_geo_given_time=r1, p=p1, r_geo_given_time_genre=r2, p_given_genre=p2, r_time_given_geo_genre=r3, p_time_given_genre=p3)
print("modern: geo|time", round(r1, 3), p1, " geo|time,genre", round(r2, 3), p2, " time|geo,genre", round(r3, 3), p3)
M = pd.read_csv(f"{REPO}/data/mantel.csv")
pv = M[["p_time", "p_geo", "p_geo_given_time", "p_time_given_geo"]].values.ravel()
from statsmodels.stats.multitest import multipletests
rej, padj, *_ = multipletests(pv, alpha=0.05, method="fdr_bh")
M2 = M.copy()
for i, c in enumerate(["p_time", "p_geo", "p_geo_given_time", "p_time_given_geo"]):
    M2[c + "_bh"] = padj[i::4]
out["mantel_bh"] = M2.round(4).to_dict("records")
print(M2[["subset", "p_time", "p_time_bh", "p_geo", "p_geo_bh", "p_geo_given_time", "p_geo_given_time_bh"]].round(3).to_string())

# 3 ---------------------------------------------------------------- nearest-neighbour permutation null (classical pieces)
cl = PL[PL.genre == "classical"].reset_index(drop=True)
zc = ((cl[F].fillna(PF.median()) - PF.mean()) / PF.std()).values
cv = np.array(cl.composer.values, dtype=object); D = squareform(pdist(zc)); same = cv[:, None] == cv[None, :]; D[same] = np.inf
cityv = np.array(cl.city.values, dtype=object); nn = D.argmin(1); obs_city = float((cityv == cityv[nn]).mean()); obs_gap = float(np.median(np.abs(cl.year.values - cl.year.values[nn])))
null_city, null_gap = [], []
for _ in range(1000):
    # random partner by a different composer
    p = rng.integers(0, len(cl), len(cl)); bad = cv[p] == cv
    while bad.any(): p[bad] = rng.integers(0, len(cl), bad.sum()); bad = cv[p] == cv
    null_city.append((cityv == cityv[p]).mean()); null_gap.append(np.median(np.abs(cl.year.values - cl.year.values[p])))
null_city, null_gap = np.array(null_city), np.array(null_gap)
out["nn"] = dict(n=int(len(cl)), same_city=obs_city, same_city_null_mean=float(null_city.mean()), same_city_null_95=[float(np.percentile(null_city, 2.5)), float(np.percentile(null_city, 97.5))],
                 p_city_less=float((np.sum(null_city <= obs_city) + 1) / 1001), year_gap=obs_gap, year_gap_null_mean=float(null_gap.mean()), year_gap_null_95=[float(np.percentile(null_gap, 2.5)), float(np.percentile(null_gap, 97.5))],
                 p_gap_less=float((np.sum(null_gap <= obs_gap) + 1) / 1001))

# time-matched null: a random partner by a different composer no further away in time than the observed nearest neighbour
yr = cl.year.values; gaps = np.abs(yr - yr[nn]); tm = []
for _ in range(300):
    p = np.empty(len(cl), int)
    for i in range(len(cl)):
        cand = np.where((cv != cv[i]) & (np.abs(yr - yr[i]) <= max(gaps[i], 1)))[0]; p[i] = rng.choice(cand) if len(cand) else i
    tm.append((cityv == cityv[p]).mean())
tm = np.array(tm)
out["nn"].update(same_city_timematched_null_mean=float(tm.mean()), same_city_timematched_null_95=[float(np.percentile(tm, 2.5)), float(np.percentile(tm, 97.5))], p_city_timematched=float((np.sum(tm >= obs_city) + 1) / 301))
print("nn:", out["nn"])

# 4 ---------------------------------------------------------------- notation paired CIs vs between-era differences
R = json.load(open(f"{REPO}/data/robustness.json"))["notation"]["metrics"]
E = {e["group"]: e for e in json.load(open(f"{REPO}/data/summary.json"))["eras"]}
pop = ["Rock/Pop 1950-64", "Rock/Pop 1965-74", "Rock/Pop 1975-84", "Rock/Pop 1985+"]
nt = {}
for m, v in R.items():
    se = v["sd_diff"] / np.sqrt(v["n"]); t = stats.t.ppf(0.975, v["n"] - 1)
    span = max(E[e][m][0] for e in pop) - min(E[e][m][0] for e in pop)
    nt[m] = dict(mean_diff=v["mean_diff"], ci95=[v["mean_diff"] - t * se, v["mean_diff"] + t * se], pop_era_range=float(span))
out["notation_ci"] = nt
print(pd.DataFrame(nt).T.round(3).to_string())

# 5 ---------------------------------------------------------------- DCML vs When in Rome shared composers
both = P[P.genre == "classical"].groupby("composer").source.nunique(); shared = both[both > 1].index
sc = P[P.composer.isin(shared)].groupby(["composer", "source"])[["seventh_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "down5th_share", "chord_entropy"]].agg(["mean", "size"])
out["dcml_vs_wir"] = {c: {s: {m: float(sc.loc[(c, s), (m, "mean")]) for m in ["seventh_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "down5th_share", "chord_entropy"]} | {"n": int(sc.loc[(c, s), ("seventh_rate", "size")])} for s in sc.loc[c].index} for c in shared}
print(sc.round(3).to_string())

# 6 ---------------------------------------------------------------- composer-cluster bootstrap for the era table
MEAS = ["seventh_rate", "extended_rate", "chromatic_root_rate", "nondiatonic_rate", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy", "vocab40"]
rows = []
for era, g in P.groupby("era"):
    comps = g.composer.unique(); by = {c: g[g.composer == c] for c in comps}
    draws = []
    for _ in range(400):
        pick = rng.choice(comps, len(comps), replace=True)
        s = pd.concat([by[c] for c in pick]); draws.append(s[MEAS].mean())
    Dd = pd.DataFrame(draws); row = dict(group=era, n_pieces=len(g), n_composers=len(comps))
    for m in MEAS: row[m] = float(g[m].mean()); row[m + "_lo"] = float(Dd[m].quantile(0.025)); row[m + "_hi"] = float(Dd[m].quantile(0.975))
    rows.append(row)
order = json.load(open(f"{REPO}/data/summary.json"))["era_order"]
EB = pd.DataFrame(rows); EB["k"] = EB.group.map({e: i for i, e in enumerate(order)}); EB = EB.sort_values("k").drop(columns="k")
EB.to_csv(f"{REPO}/data/eras_clusterboot.csv", index=False)
print(EB[["group", "n_composers", "V_to_I_share", "V_to_I_share_lo", "V_to_I_share_hi", "seventh_rate", "seventh_rate_lo", "seventh_rate_hi"]].round(3).to_string())
json.dump(out, open(f"{REPO}/data/revision_checks.json", "w"), indent=1)
