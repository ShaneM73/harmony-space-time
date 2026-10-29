"""Composer/artist harmonic space for the 3D map.

Grouping and display are separate steps:
  * grouping  = Ward clustering on all 14 z-scored harmonic features (6 clusters, as in space_time.py);
  * display   = 3 axes, either varimax-rotated factor analysis (default; interpretable) or PCA (max variance).
Also reports cluster separation (silhouette), Ward vs k-means agreement, bootstrap stability, and for each
composer a membership confidence: the mean share of bootstrap replicates in which they are clustered with
their original cluster-mates.
Output: data/composer_space.json
"""
import json, os
import numpy as np, pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.cluster import KMeans

REPO = os.environ.get("HARMONY_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
C = pd.read_csv(f"{REPO}/data/composer_clusters.csv")
F = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share",
     "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy",
     "tonic_share", "minor_quality_share"]
LABEL = {"seventh_rate": "sevenths", "extended_rate": "9ths and above", "nondiatonic_rate": "non-diatonic",
         "chromatic_root_rate": "chromatic roots", "V_to_I_share": "V → I", "IV_to_I_share": "IV → I",
         "bVII_to_I_share": "bVII → I", "dom_resolution": "V resolves to I", "down5th_share": "descending fifths",
         "step_share": "step motion", "third_share": "third motion", "chord_entropy": "chord entropy",
         "tonic_share": "tonic share", "minor_quality_share": "minor chords"}
# standardise with the piece-level means and SDs of the located pieces, exactly as space_time.py does
PL = pd.read_csv(f"{REPO}/data/pieces_located.csv"); PL = PL[PL.city.notna()]
PF = PL[F].fillna(PL[F].median())
Z = ((C[F] - PF.mean()) / PF.std()).fillna(0).values
rng = np.random.default_rng(0)

# grouping (same as space_time.py)
Lw = linkage(Z, "ward"); cl = fcluster(Lw, 6, "maxclust")
assert (cl == C.harmonic_cluster.values).all(), "cluster labels differ from composer_clusters.csv"

# display axes
pca = PCA(n_components=3).fit(Z); P = pca.transform(Z)
fa = FactorAnalysis(n_components=3, rotation="varimax", random_state=0).fit(Z); FS = fa.transform(Z)
Lfa = fa.components_.T.copy()
# orient factors so the named pole is positive: F1 = fifth-driven, F2 = chromatic, F3 = plagal
sign = np.array([-1 if Lfa[F.index("down5th_share"), 0] < 0 else 1,
                 1 if Lfa[F.index("nondiatonic_rate"), 1] > 0 else -1,
                 1 if Lfa[F.index("IV_to_I_share"), 2] > 0 else -1])
Lfa *= sign; FS *= sign
Lp = pca.components_.T

# separation and stability
sil = {k: float(silhouette_score(Z, fcluster(Lw, k, "maxclust"))) for k in range(2, 11)}
ari_km = float(adjusted_rand_score(cl, KMeans(6, n_init=20, random_state=0).fit_predict(Z)))
n = len(Z); co = np.zeros((n, n)); cnt = np.zeros((n, n)); aris = []
for _ in range(300):
    idx = rng.choice(n, n); lab = fcluster(linkage(Z[idx], "ward"), 6, "maxclust")
    aris.append(adjusted_rand_score(cl[idx], lab))
    u, first = np.unique(idx, return_index=True); lu = lab[first]
    same = (lu[:, None] == lu[None, :]).astype(float)
    co[np.ix_(u, u)] += same; cnt[np.ix_(u, u)] += 1
cop = np.divide(co, cnt, out=np.full_like(co, np.nan), where=cnt > 0)
conf = []
for i in range(n):
    mates = [j for j in range(n) if cl[j] == cl[i] and j != i]
    conf.append(float(np.nanmean(cop[i, mates])) if mates else 1.0)
D = squareform(pdist(Z))
out = dict(
    features=[LABEL[f] for f in F],
    fa=dict(axes=["Fifth-driven, cadential", "Chromatic, extended", "Plagal, tonic-centred"],
            poles=[["steps and thirds", "descending fifths, V → I"], ["diatonic triads", "sevenths, chromatic chords"], ["varied, V → I", "IV → I, predictable"]],
            loadings=np.round(Lfa, 3).tolist(), communality=float(np.round((Lfa ** 2).sum(1).mean(), 3))),
    pca=dict(axes=["PC1", "PC2", "PC3"], explained=np.round(pca.explained_variance_ratio_, 3).tolist(), loadings=np.round(Lp, 3).tolist()),
    stats=dict(silhouette=sil, ari_ward_kmeans=ari_km, bootstrap_ari_mean=float(np.mean(aris)), bootstrap_ari_90=[float(np.percentile(aris, 5)), float(np.percentile(aris, 95))]),
    composers=[dict(unit=r.unit, genre=r.genre, city=r.city, year=int(round(r.year)), n=int(r.n_pieces), cluster=int(cl[i]),
                    fa=np.round(FS[i], 3).tolist(), pca=np.round(P[i], 3).tolist(), conf=round(conf[i], 3),
                    vals={LABEL[f]: (None if pd.isna(getattr(r, f)) else round(float(getattr(r, f)), 3)) for f in F},
                    near=[C.unit.iloc[j] for j in np.argsort(D[i])[1:4]]) for i, r in enumerate(C.itertuples())],
)
json.dump(out, open(f"{REPO}/data/composer_space.json", "w"), ensure_ascii=False)
C["conf"] = np.round(conf, 3); C.to_csv(f"{REPO}/data/composer_clusters.csv", index=False)  # deposit membership confidence
print("silhouette", {k: round(v, 3) for k, v in sil.items()}, "ARI ward-kmeans", round(ari_km, 3), "bootstrap ARI", round(np.mean(aris), 3))
print("low-confidence members:", sorted([(round(c, 2), C.unit.iloc[i], int(cl[i])) for i, c in enumerate(conf)])[:10])
