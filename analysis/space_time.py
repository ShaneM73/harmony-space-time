"""Space-time framework: place every located piece at (x km, y km, year), cluster into scenes,
profile scenes and composers harmonically, and test whether harmonic distance follows time, space or both."""
import os as _os
REPO = _os.environ.get("HARMONY_ROOT", _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import json, math
import numpy as np, pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA

OUT = f"{REPO}/data"
rng = np.random.default_rng(11)
P = pd.read_csv(f"{OUT}/pieces_located.csv")
P = P[P.city.notna()].copy()
print("located pieces:", len(P))

FEATS = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share",
         "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy",
         "tonic_share", "minor_quality_share"]
F = P[FEATS].copy()
F = F.fillna(F.median())
Z = (F - F.mean()) / F.std()

# ---- space-time coordinates: equirectangular km, 1 century == KM_PER_CENTURY km
KM_PER_CENTURY = 1000.0
P["x_km"] = P.lon * 111.32 * np.cos(np.radians(P.lat))
P["y_km"] = P.lat * 110.57
P["t_km"] = P.year * KM_PER_CENTURY / 100.0
ST = P[["x_km", "y_km", "t_km"]].values

# ---- scenes: Ward clustering in space-time, cut at a distance threshold (~ 60 yrs / 600 km scale)
L = linkage(ST, method="ward")
P["scene_id"] = fcluster(L, t=26, criterion="maxclust")
# a scene with < 8 pieces joins its nearest big scene only if that centroid is within 1500 km-equivalents;
# otherwise it stays an isolated point set (scene_id 0) that is plotted but not profiled
cent = P.groupby("scene_id")[["x_km", "y_km", "t_km"]].mean()
sizes = P.scene_id.value_counts()
small = sizes[sizes < 8].index
for s in small:
    others = cent.drop(index=small)
    d = np.sqrt(((others - cent.loc[s]) ** 2).sum(axis=1))
    P.loc[P.scene_id == s, "scene_id"] = d.idxmin() if d.min() < 1500 else 0
# split any scene whose cities are more than 2500 km apart (Ward can chain isolated cities)
nxt = P.scene_id.max() + 1
for sid, g in list(P.groupby("scene_id")):
    if sid == 0: continue
    cc = g.groupby("city")[["x_km", "y_km"]].mean()
    if len(cc) > 1 and np.sqrt(((cc - cc.iloc[0]) ** 2).sum(axis=1)).max() > 2500:
        main = g.city.value_counts().index[0]
        far = [c for c in cc.index if np.sqrt(((cc.loc[c] - cc.loc[main]) ** 2).sum()) > 2500]
        P.loc[(P.scene_id == sid) & P.city.isin(far), "scene_id"] = 0


def scene_label(g):
    cities = g.city.value_counts()
    top = [c for c in cities.index[:2] if cities[c] >= 0.15 * len(g)] or [cities.index[0]]
    y0, y1 = int(g.year.quantile(0.05)), int(g.year.quantile(0.95))
    return f"{' / '.join(top)} {y0}–{y1}"


scenes = []
for sid, g in P.groupby("scene_id"):
    if sid == 0 or len(g) < 8:
        P.loc[g.index, "scene_id"] = 0
        continue
    comps = g.composer.value_counts()
    scenes.append(dict(scene_id=int(sid), label=scene_label(g), n_pieces=len(g), year_min=int(g.year.min()), year_max=int(g.year.max()),
                       year_mid=float(g.year.median()), lat=float(g.lat.mean()), lon=float(g.lon.mean()),
                       genre=g.genre.mode().iloc[0], cities=", ".join(f"{c} ({n})" for c, n in g.city.value_counts().head(4).items()),
                       top_composers=", ".join(f"{c} ({n})" for c, n in comps.head(5).items()),
                       **{f: float(g[f].mean()) for f in FEATS}))
S = pd.DataFrame(scenes).sort_values("year_mid").reset_index(drop=True)
# relabel scene ids in chronological order
remap = {old: i + 1 for i, old in enumerate(S.scene_id)}; remap[0] = 0
S["scene_id"] = S.scene_id.map(remap); P["scene_id"] = P.scene_id.map(remap)
print("isolated pieces (no scene):", int((P.scene_id == 0).sum()))
S["scene"] = S.scene_id.astype(str) + ". " + S.label
print(S[["scene", "n_pieces", "genre", "top_composers"]].to_string())

# ---- harmonic clustering of scenes (Ward on z-scored scene means) + dendrogram
SZ = (S[FEATS] - F.mean()) / F.std()
Ls = linkage(SZ.values, method="ward")
S["harmonic_group"] = fcluster(Ls, t=4, criterion="maxclust")
dn = dendrogram(Ls, no_plot=True, labels=S.scene.tolist())
S["dendro_order"] = [dn["ivl"].index(s) for s in S.scene]

# ---- composers / artists with >= 5 pieces: profile, PCA map, clusters
def canon(n):
    k = str(n).lower().strip()
    return k[4:] if k.startswith("the ") else k
P["ukey"] = P.composer.map(canon)
best = P.groupby("ukey").composer.agg(lambda s: s.value_counts().index[0])
P["unit"] = P.ukey.map(best)
C = P.groupby("unit").filter(lambda g: len(g) >= 5)
comp = C.groupby("unit").agg(n_pieces=("piece_id", "size"), year=("year", "median"), lat=("lat", "mean"), lon=("lon", "mean"),
                             genre=("genre", lambda s: s.mode().iloc[0]), city=("city", lambda s: s.mode().iloc[0]),
                             **{f: (f, "mean") for f in FEATS}).reset_index()
# artists represented only in the Rock Corpus have no measured seventh/extension rate: impute the rock/pop unit median
for f in ["seventh_rate", "extended_rate"]:
    med = comp.loc[(comp.genre == "rock_pop") & comp[f].notna(), f].median()
    comp.loc[comp[f].isna(), f] = med
CZ = (comp[FEATS] - F.mean()) / F.std()
pca = PCA(n_components=2).fit(CZ.values)
xy = pca.transform(CZ.values)
comp["pc1"], comp["pc2"] = xy[:, 0], xy[:, 1]
load = pd.DataFrame(pca.components_, columns=FEATS, index=["pc1", "pc2"]).T
print("explained variance:", pca.explained_variance_ratio_.round(3))
print(load.round(2).to_string())
Lc = linkage(CZ.values, method="ward")
comp["harmonic_cluster"] = fcluster(Lc, t=6, criterion="maxclust")
dc = dendrogram(Lc, no_plot=True, labels=comp.unit.tolist())
comp["dendro_order"] = [dc["ivl"].index(u) for u in comp.unit]
# dendrogram merge list for drawing: scipy linkage rows -> (a, b, height); leaves 0..n-1
merges = [dict(a=int(a), b=int(b), height=float(h), size=int(s)) for a, b, h, s in Lc]
for k, g in comp.groupby("harmonic_cluster"):
    print(f"cluster {k}:", ", ".join(g.sort_values("year").unit))


# ---- Mantel tests: does harmonic distance follow temporal or geographic distance?
def mantel(a, b, n=5000):
    """Pearson correlation between two condensed distance vectors with a permutation test."""
    A = squareform(a); B = squareform(b); m = A.shape[0]
    iu = np.triu_indices(m, 1)
    r = np.corrcoef(A[iu], B[iu])[0, 1]
    null = []
    for _ in range(n):
        p = rng.permutation(m); null.append(np.corrcoef(A[iu], B[np.ix_(p, p)][iu])[0, 1])
    null = np.array(null)
    return float(r), float((np.sum(null >= r) + 1) / (n + 1))


def partial_mantel(a, b, c, n=5000):
    """correlation of a and b after removing the linear effect of c from both (residual Mantel)."""
    A, B, Cc = squareform(a), squareform(b), squareform(c); m = A.shape[0]; iu = np.triu_indices(m, 1)
    def resid(X):
        x = X[iu]; z = Cc[iu]; beta = np.polyfit(z, x, 1); return x - np.polyval(beta, z)
    ra, rb = resid(A), resid(B)
    r = np.corrcoef(ra, rb)[0, 1]
    null = []
    for _ in range(n):
        p = rng.permutation(m); Bp = B[np.ix_(p, p)]; xb = Bp[iu]; z = Cc[iu]; beta = np.polyfit(z, xb, 1)
        null.append(np.corrcoef(ra, xb - np.polyval(beta, z))[0, 1])
    null = np.array(null)
    return float(r), float((np.sum(null >= r) + 1) / (n + 1))


def geo_km(df):
    pts = np.radians(df[["lat", "lon"]].values)
    lat = pts[:, 0][:, None]; lon = pts[:, 1][:, None]
    d = 2 * 6371 * np.arcsin(np.sqrt(np.sin((lat - lat.T) / 2) ** 2 + np.cos(lat) * np.cos(lat.T) * np.sin((lon - lon.T) / 2) ** 2))
    return squareform(d, checks=False)


tests = []
for name, df, zf in [("all composers and artists (5+ pieces)", comp, CZ), ("classical composers only", comp[comp.genre == "classical"], CZ[comp.genre == "classical"]),
                     ("modern artists only (jazz, rock/pop)", comp[comp.genre != "classical"], CZ[comp.genre != "classical"]),
                     ("jazz performers only", comp[comp.genre == "jazz"], CZ[comp.genre == "jazz"]),
                     ("rock/pop artists only", comp[comp.genre == "rock_pop"], CZ[comp.genre == "rock_pop"])]:
    dh = pdist(zf.values); dt = pdist(df[["year"]].values); dg = geo_km(df)
    r_t, p_t = mantel(dh, dt); r_g, p_g = mantel(dh, dg)
    r_gt, p_gt = partial_mantel(dh, dg, dt); r_tg, p_tg = partial_mantel(dh, dt, dg)
    tests.append(dict(subset=name, n_units=len(df), r_harmony_time=r_t, p_time=p_t, r_harmony_geo=r_g, p_geo=p_g,
                      r_geo_given_time=r_gt, p_geo_given_time=p_gt, r_time_given_geo=r_tg, p_time_given_geo=p_tg))
T = pd.DataFrame(tests)
print(T.round(3).to_string())

# ---- same question at the piece level inside the classical corpus: nearest harmonic neighbour
cl = P[P.genre == "classical"].reset_index(drop=True)
zc = Z.loc[cl.index] if False else ((cl[FEATS].fillna(F.median()) - F.mean()) / F.std()).values
D = squareform(pdist(zc)); np.fill_diagonal(D, np.inf)
cc_ = cl.composer.astype(object).values
same_comp = cc_[:, None] == cc_[None, :]
D[same_comp] = np.inf  # nearest neighbour must be by a different composer
nn = D.argmin(axis=1)
same_city = (cl.city.values == cl.city.values[nn]).mean()
dyear = np.abs(cl.year.values - cl.year.values[nn])
rand = rng.integers(0, len(cl), len(cl))
same_city_rand = (cl.city.values == cl.city.values[rand]).mean()
dyear_rand = np.abs(cl.year.values - cl.year.values[rand])
nnstats = dict(n=len(cl), same_city_nn=float(same_city), same_city_random=float(same_city_rand),
               median_year_gap_nn=float(np.median(dyear)), median_year_gap_random=float(np.median(dyear_rand)))
print(nnstats)

# ---- write outputs
P[["piece_id", "source", "genre", "composer", "title", "year", "city", "country", "lat", "lon", "loc_confidence", "scene_id"] + FEATS].to_csv(f"{OUT}/pieces_spacetime.csv", index=False)
S.to_csv(f"{OUT}/scenes.csv", index=False)
comp.to_csv(f"{OUT}/composer_clusters.csv", index=False)
T.to_csv(f"{OUT}/mantel.csv", index=False)
json.dump(dict(merges=merges, leaves=comp.unit.tolist(), loadings=load.round(3).to_dict(), explained=pca.explained_variance_ratio_.round(3).tolist(), nn=nnstats,
               km_per_century=KM_PER_CENTURY), open(f"{OUT}/spacetime_extra.json", "w"), indent=1)
