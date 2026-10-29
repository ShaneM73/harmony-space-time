"""Robustness checks for the harmony-evolution findings.

1. Notation effect: songs present in both the Rock Corpus (Roman numerals) and McGill Billboard (chord symbols)
   as the same recording — paired differences in every metric.
2. Mixed-effects models: metric ~ year (+ a post-1850 hinge) with composer random intercepts and a corpus
   fixed effect, classical only; and metric ~ year × genre across all genres.
3. Change-point tests on piece-level data: best single breakpoint by least squares with a bootstrap CI,
   one-break vs two-break vs linear by BIC (the "plateau" claim).
4. No-chord handling: default vs strict (no-chord stretches break transitions) era summaries.
5. Cluster sensitivity: leave-one-feature-out, feature families removed, k-means and average linkage,
   compared with the published 6-cluster Ward solution by adjusted Rand index.
Output: data/robustness.json and data/robustness.md
"""
import json, os, re, warnings
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy.cluster.hierarchy import linkage, fcluster
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

warnings.filterwarnings("ignore")
REPO = os.environ.get("HARMONY_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = pd.read_csv(f"{REPO}/data/pieces.csv"); PS = pd.read_csv(f"{REPO}/data/strict_pieces.csv")
out = {}; md = []
METRICS = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share",
           "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy", "vocab40", "beats_per_chord"]

# ---------------------------------------------------------------- 1. notation effect
PAIRS = ["be_my_baby", "born_to_be_wild", "eight_miles_high", "help", "honky_tonk_women", "i_saw_her_standing_there", "in_the_midnight_hour",
         "maggie_may", "sunshine_of_your_love", "the_sounds_of_silence", "will_you_love_me_tomorrow", "with_or_without_you"]
BB = P[P.source == "Billboard"].copy(); norm = lambda s: re.sub(r"[^a-z0-9 ]", "", str(s).lower().replace("&", "and"))
BB["tkey"] = BB.title.map(norm); BB["akey"] = BB.composer.map(norm)
# seventh/extension rates are "not measured" for Rock Corpus pieces in pieces.csv (see analyze.py); recompute them here from the events
ev = pd.read_csv(f"{REPO}/data/chords_modern.csv", usecols=["piece_id", "source", "root_pc", "quality", "ext", "applied"]) if os.path.exists(f"{REPO}/data/chords_modern.csv") else None
if ev is not None:
    ev = ev[ev.source == "RockCorpus"].copy()
    key = ev.piece_id.astype(str) + "|" + ev.root_pc.astype(str) + "|" + ev.quality.astype(str) + "|" + ev.ext.astype(str) + "|" + ev.applied.astype(str)
    ev = ev[key != key.shift()]  # merge consecutive repeats as analyze.py does
    ev["seventh"] = ev.ext.isin(["7", "9+"]); ev["extended"] = ev.ext == "9+"
    rs = ev.groupby("piece_id")[["seventh", "extended"]].mean()
    for col, src in [("seventh_rate", "seventh"), ("extended_rate", "extended")]:
        P.loc[P.piece_id.isin(rs.index), col] = P.loc[P.piece_id.isin(rs.index), "piece_id"].map(rs[src])
rows = []
for stem in PAIRS:
    a = P[P.piece_id == f"rs200:{stem}"].iloc[0]
    b = BB[(BB.tkey == norm(a.title)) & (BB.akey == norm(a.composer))]
    if len(b) == 0: b = BB[(BB.tkey.str.startswith(norm(a.title))) & (BB.akey.str.startswith(norm(a.composer)[:8]))]
    if len(b) == 0: print("no match", stem); continue
    b = b.iloc[0]  # duplicate chart entries use the same transcription; take the first
    rows.append(dict(song=stem, rs_title=a.title, bb_id=b.piece_id, **{m: a[m] for m in METRICS}, **{m + "_bb": b[m] for m in METRICS}))
PR = pd.DataFrame(rows)
notation = {}
for m in METRICS:
    x, y = PR[m].astype(float), PR[m + "_bb"].astype(float); ok = x.notna() & y.notna()
    if ok.sum() < 5: continue
    d = (y - x)[ok]; r = stats.pearsonr(x[ok], y[ok])[0] if ok.sum() > 2 else np.nan
    w = stats.wilcoxon(d).pvalue if (d != 0).any() else 1.0
    notation[m] = dict(n=int(ok.sum()), rock_mean=float(x[ok].mean()), billboard_mean=float(y[ok].mean()), mean_diff=float(d.mean()), sd_diff=float(d.std()), r=float(r), p_wilcoxon=float(w))
out["notation"] = dict(pairs=PR[["song","bb_id"]].values.tolist(), metrics=notation)
md.append("## 1. Notation effect: Rock Corpus (Roman numerals) vs Billboard (chord symbols), same recordings\n")
md.append(f"{len(PR)} songs: " + ", ".join(PR.rs_title) + ".\n")
md.append("| Metric | n | Rock Corpus | Billboard | Mean diff (BB − RC) | r | Wilcoxon p |\n| --- | --- | --- | --- | --- | --- | --- |")
for m, v in notation.items():
    md.append(f"| {m} | {v['n']} | {v['rock_mean']:.3f} | {v['billboard_mean']:.3f} | {v['mean_diff']:+.3f} ± {v['sd_diff']:.3f} | {v['r']:.2f} | {v['p_wilcoxon']:.3f} |")

# ---------------------------------------------------------------- 2. mixed models
C = P[P.genre == "classical"].copy(); C["yc"] = (C.year - 1750) / 100; C["hinge"] = np.clip(C.year - 1850, 0, None) / 100
C["corpus"] = C.source
mixed = {}
md.append("\n## 2. Mixed-effects models (classical, composer random intercept, corpus fixed effect)\n")
md.append("metric ~ year (per century, centred 1750) + hinge(year − 1850) + corpus, random intercept per composer. Hinge = change in slope after 1850.\n")
md.append("| Metric | slope / century | 95% CI | hinge after 1850 | 95% CI | composer SD | residual SD | n |\n| --- | --- | --- | --- | --- | --- | --- | --- |")
for m in ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "dom_resolution", "down5th_share", "step_share", "chord_entropy", "vocab40"]:
    d = C.dropna(subset=[m])
    try:
        r = smf.mixedlm(f"{m} ~ yc + hinge + corpus", d, groups=d.composer).fit(reml=True, method="powell", maxiter=3000)
        ci = r.conf_int()
        mixed[m] = dict(slope=float(r.params["yc"]), slope_ci=[float(ci.loc["yc", 0]), float(ci.loc["yc", 1])], hinge=float(r.params["hinge"]), hinge_ci=[float(ci.loc["hinge", 0]), float(ci.loc["hinge", 1])],
                        composer_sd=float(np.sqrt(r.cov_re.iloc[0, 0])), resid_sd=float(np.sqrt(r.scale)), n=int(r.nobs), p_slope=float(r.pvalues["yc"]), p_hinge=float(r.pvalues["hinge"]))
        v = mixed[m]
        md.append(f"| {m} | {v['slope']:+.3f} | [{v['slope_ci'][0]:+.3f}, {v['slope_ci'][1]:+.3f}] | {v['hinge']:+.3f} | [{v['hinge_ci'][0]:+.3f}, {v['hinge_ci'][1]:+.3f}] | {v['composer_sd']:.3f} | {v['resid_sd']:.3f} | {v['n']} |")
    except Exception as e:
        mixed[m] = dict(error=str(e))
out["mixed_classical"] = mixed
# all genres: metric ~ year × genre with composer random intercepts (modern artists as "composers")
A = P.copy(); A["yc"] = (A.year - 1900) / 100; A["g"] = pd.Categorical(A.genre, ["classical", "jazz", "rock_pop"])
mixed_all = {}
md.append("\n### All genres: metric ~ year × genre, composer/artist random intercept (year per century, centred 1900)\n")
md.append("| Metric | classical slope | jazz slope | rock/pop slope | genre SD (composer) |\n| --- | --- | --- | --- | --- |")
for m in ["seventh_rate", "nondiatonic_rate", "V_to_I_share", "dom_resolution", "down5th_share", "step_share"]:
    d = A.dropna(subset=[m])
    try:
        r = smf.mixedlm(f"{m} ~ yc * g", d, groups=d.composer).fit(reml=True, method="powell", maxiter=3000)
        p = r.params; sl = dict(classical=float(p["yc"]), jazz=float(p["yc"] + p.get("yc:g[T.jazz]", 0)), rock_pop=float(p["yc"] + p.get("yc:g[T.rock_pop]", 0)))
        mixed_all[m] = dict(slopes=sl, composer_sd=float(np.sqrt(r.cov_re.iloc[0, 0])))
        md.append(f"| {m} | {sl['classical']:+.3f} | {sl['jazz']:+.3f} | {sl['rock_pop']:+.3f} | {mixed_all[m]['composer_sd']:.3f} |")
    except Exception as e:
        mixed_all[m] = dict(error=str(e))
out["mixed_all"] = mixed_all

# ---------------------------------------------------------------- 3. change points (classical, piece level)
rng = np.random.default_rng(3)
def fit_breaks(x, y, breaks):
    X = np.column_stack([np.ones_like(x), x] + [np.clip(x - b, 0, None) for b in breaks])
    beta, res, *_ = np.linalg.lstsq(X, y, rcond=None); sse = float(((X @ beta - y) ** 2).sum()); return beta, sse
def best_break(x, y, grid):
    best = None
    for b in grid:
        _, sse = fit_breaks(x, y, [b])
        if best is None or sse < best[1]: best = (b, sse)
    return best
def best_two(x, y, grid):
    best = None
    for i, b1 in enumerate(grid):
        for b2 in grid[i + 2:]:
            _, sse = fit_breaks(x, y, [b1, b2])
            if best is None or sse < best[2]: best = (b1, b2, sse)
    return best
cp = {}
md.append("\n## 3. Change points (classical, piece level, least-squares hinge regression)\n")
md.append("| Metric | n | best single break | 95% bootstrap CI | ΔBIC 1-break vs linear | best two breaks | ΔBIC 2-break vs 1-break |\n| --- | --- | --- | --- | --- | --- | --- |")
grid = np.arange(1600, 1911, 5)
for m in ["seventh_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "dom_resolution", "down5th_share", "chord_entropy"]:
    d = C.dropna(subset=[m]); x = d.year.values.astype(float); y = d[m].values.astype(float); n = len(x)
    _, sse0 = fit_breaks(x, y, []); b1, sse1 = best_break(x, y, grid); b21, b22, sse2 = best_two(x, y, grid[::2])
    bic = lambda sse, k: n * np.log(sse / n) + k * np.log(n)
    boots = []
    for _ in range(200):
        idx = rng.integers(0, n, n); boots.append(best_break(x[idx], y[idx], grid[::2])[0])
    cp[m] = dict(n=n, break1=float(b1), ci=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))], dbic_1_vs_0=float(bic(sse0, 2) - bic(sse1, 3)),
                 breaks2=[float(b21), float(b22)], dbic_2_vs_1=float(bic(sse1, 3) - bic(sse2, 4)))
    v = cp[m]; md.append(f"| {m} | {n} | {v['break1']:.0f} | [{v['ci'][0]:.0f}, {v['ci'][1]:.0f}] | {v['dbic_1_vs_0']:+.1f} | {v['breaks2'][0]:.0f}, {v['breaks2'][1]:.0f} | {v['dbic_2_vs_1']:+.1f} |")
out["changepoints"] = cp

# ---------------------------------------------------------------- 4. no-chord handling
nc = {}
md.append("\n## 4. No-chord handling: default (transitions bridge silent stretches) vs strict (they do not)\n")
md.append("| Era | metric | default | strict | difference |\n| --- | --- | --- | --- | --- |")
E0 = pd.DataFrame([{k: (v[0] if isinstance(v, list) else v) for k, v in e.items()} for e in json.load(open(f"{REPO}/data/summary.json"))["eras"]]).set_index("group"); E1 = pd.read_csv(f"{REPO}/data/strict_era_summary.csv").set_index("group")
for e in E0.index:
    for m in ["V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "beats_per_chord"]:
        a, b = E0.loc[e, m], E1.loc[e, m]
        if pd.notna(a) and pd.notna(b):
            nc[f"{e}|{m}"] = [float(a), float(b)]
            if abs(a - b) > 0.004 or m == "V_to_I_share": md.append(f"| {e} | {m} | {a:.3f} | {b:.3f} | {b - a:+.3f} |")
out["no_chord"] = nc
maxd = max(abs(a - b) for k, (a, b) in nc.items() if not k.endswith("beats_per_chord"))
md.append(f"\nLargest change in any share across all eras: {maxd:.3f}.\n")

# ---------------------------------------------------------------- 5. cluster sensitivity
CC = pd.read_csv(f"{REPO}/data/composer_clusters.csv"); PL = pd.read_csv(f"{REPO}/data/pieces_located.csv"); PL = PL[PL.city.notna()]
F = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy", "tonic_share", "minor_quality_share"]
PF = PL[F].fillna(PL[F].median()); Z = ((CC[F] - PF.mean()) / PF.std()).fillna(0)
base = CC.harmonic_cluster.values
sens = {}
def ward6(Zs): return fcluster(linkage(Zs.values, "ward"), 6, "maxclust")
for f in F: sens[f"drop {f}"] = float(adjusted_rand_score(base, ward6(Z.drop(columns=[f]))))
families = {"no seventh/extension features": ["seventh_rate", "extended_rate"], "no chromaticism features": ["nondiatonic_rate", "chromatic_root_rate"],
            "no cadence features": ["V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution"], "no root-motion features": ["down5th_share", "step_share", "third_share"],
            "no distribution features": ["chord_entropy", "tonic_share", "minor_quality_share"]}
for k, cols in families.items(): sens[k] = float(adjusted_rand_score(base, ward6(Z.drop(columns=cols))))
sens["k-means (k=6)"] = float(adjusted_rand_score(base, KMeans(6, n_init=20, random_state=0).fit_predict(Z.values)))
sens["average linkage (k=6)"] = float(adjusted_rand_score(base, fcluster(linkage(Z.values, "average"), 6, "maxclust")))
sens["complete linkage (k=6)"] = float(adjusted_rand_score(base, fcluster(linkage(Z.values, "complete"), 6, "maxclust")))
# strict-mode composer profiles
PS2 = PS.copy(); PS2["ukey"] = PS2.composer.str.lower().str.replace(r"^the ", "", regex=True)
CC["ukey"] = CC.unit.str.lower().str.replace(r"^the ", "", regex=True)
G = PS2.groupby("ukey")[F].mean().reindex(CC.ukey)
Zs = ((G.values - PF.mean().values) / PF.std().values); Zs = pd.DataFrame(np.nan_to_num(Zs), columns=F)
sens["strict no-chord profiles"] = float(adjusted_rand_score(base, ward6(Zs)))
out["cluster_sensitivity"] = sens
md.append("\n## 5. Cluster sensitivity (adjusted Rand index vs the published 6-cluster Ward solution)\n")
md.append("| Variant | ARI |\n| --- | --- |")
for k, v in sens.items(): md.append(f"| {k} | {v:.2f} |")

json.dump(out, open(f"{REPO}/data/robustness.json", "w"), indent=1)
open(f"{REPO}/data/robustness.md", "w").write("# Robustness checks\n\n" + "\n".join(md) + "\n")
print("\n".join(md))
