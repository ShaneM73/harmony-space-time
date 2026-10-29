"""Paper figures (Figs 1-5, Supplementary Figs S1-S2) from the data tables. Output: paper/figures/*.png and *.pdf"""
import json, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image
import matplotlib.patheffects as pe
HALO = [pe.withStroke(linewidth=2, foreground="white")]

REPO = os.environ.get("HARMONY_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = f"{REPO}/paper/figures"; os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "legend.fontsize": 7.5,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#c3c2b7", "axes.linewidth": 0.6,
                     "xtick.color": "#52514e", "ytick.color": "#52514e", "grid.color": "#e1e0d9", "grid.linewidth": 0.5, "figure.dpi": 150})
GEN = {"classical": "#2a78d6", "jazz": "#eb6834", "rock_pop": "#1baf7a"}; GLAB = {"classical": "Classical", "jazz": "Jazz", "rock_pop": "Popular"}
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
INK, MUTED = "#0b0b0b", "#898781"
def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=300, bbox_inches="tight", facecolor="white"); fig.savefig(f"{OUT}/{name}.pdf", bbox_inches="tight"); plt.close(fig); print("saved", name)

S = json.load(open(f"{REPO}/data/summary.json")); ORDER = S["era_order"]
E = pd.read_csv(f"{REPO}/data/eras_clusterboot.csv").set_index("group").loc[ORDER]
E0 = pd.DataFrame([{k: (v[0] if isinstance(v, list) else v) for k, v in e.items()} for e in S["eras"]]).set_index("group").loc[ORDER]
E["genre"] = E0.genre; E["mid"] = (E0.year_min + E0.year_max) / 2
MID = {"Renaissance (<1600)": 1580, "Early Baroque (1600-99)": 1650, "Late Baroque (1700-49)": 1725, "Classical (1750-99)": 1775, "Early Romantic (1800-49)": 1825,
       "Late Romantic (1850-99)": 1875, "Early 20th c. (1900-49)": 1920, "Jazz: Swing era (<1945)": 1935, "Jazz: Bebop/Hard bop (1945-59)": 1952, "Jazz: Modal/Post-bop (1960-74)": 1967,
       "Jazz: 1975+": 1988, "Rock/Pop 1950-64": 1957, "Rock/Pop 1965-74": 1970, "Rock/Pop 1975-84": 1980, "Rock/Pop 1985+": 1992}
E["mid"] = [MID[g] for g in E.index]

def band(ax, m, label=None, ls="-", marker="o"):
    for g in ["classical", "jazz", "rock_pop"]:
        d = E[E.genre == g]
        if d[m].isna().all(): continue
        ax.fill_between(d.mid, d[m + "_lo"], d[m + "_hi"], color=GEN[g], alpha=0.15, lw=0)
        ax.plot(d.mid, d[m], ls, color=GEN[g], lw=1.6, marker=marker, ms=3.5, mec="white", mew=0.6, label=(GLAB[g] if label is None else f"{GLAB[g]} {label}"))
def pct(ax): ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
def era_axis(ax): ax.set_xlim(1560, 2005); ax.set_xticks([1600, 1700, 1800, 1900, 2000]); ax.grid(axis="y"); ax.set_axisbelow(True)

# ------------------------------------------------------------------ Fig 1
fig, axs = plt.subplots(2, 3, figsize=(10.5, 6)); axs = axs.ravel()
ax = axs[0]; band(ax, "seventh_rate"); band(ax, "extended_rate", label="9ths+", ls="--", marker="s"); pct(ax); era_axis(ax); ax.set_title("a  Sevenths (solid), 9ths+ (dashed)", loc="left")
ax = axs[1]; band(ax, "V_to_I_share"); band(ax, "IV_to_I_share", ls="--", marker="s"); band(ax, "bVII_to_I_share", ls=":", marker="^"); pct(ax); era_axis(ax); ax.set_title("b  Tonic from V (solid), IV (dashed), bVII (dotted)", loc="left")
ax = axs[2]; band(ax, "dom_resolution"); pct(ax); era_axis(ax); ax.set_title("c  Probability that V proceeds to I", loc="left")
ax = axs[3]; band(ax, "nondiatonic_rate"); band(ax, "chromatic_root_rate", ls="--", marker="s"); pct(ax); era_axis(ax); ax.set_title("d  Non-diatonic (solid), chromatic roots (dashed)", loc="left")
ax = axs[4]; band(ax, "vocab40"); era_axis(ax); ax.set_title("e  Distinct chord types per 40 chords", loc="left")
ax = axs[5]
for g in ["classical", "jazz", "rock_pop"]:
    d = E0[E0.genre == g]; ax.plot([MID[i] for i in d.index], d.transition_entropy, "-", color=GEN[g], lw=1.6, marker="o", ms=3.5, mec="white", mew=0.6)
era_axis(ax); ax.set_ylabel("bits"); ax.set_title("f  Entropy of the next chord (pooled per era)", loc="left")
h = [Line2D([], [], color=GEN[g], lw=2, label=GLAB[g]) for g in GEN]
fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.005))
fig.text(0.5, -0.035, "Era means of per-piece values; bands are 95% composer-cluster bootstrap intervals. Popular seventh/extension rates from Billboard only.", ha="center", fontsize=7, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 1)); save(fig, "fig1_trajectories")

# ------------------------------------------------------------------ Fig 2 root motion + top chords
M = pd.read_csv(f"{REPO}/data/motion.csv"); TC = pd.read_csv(f"{REPO}/data/top_chords.csv")
CL = {"down5th": "Descending fifth", "up5th": "Ascending fifth", "stepUp": "Step", "stepDown": "Step", "thirdUp": "Third", "thirdDown": "Third", "tritone": "Other", "same": "Other"}
M["cls"] = M.motion_key.map(CL); MM = M.groupby(["era", "cls"]).share.sum().unstack().loc[ORDER][["Descending fifth", "Ascending fifth", "Step", "Third", "Other"]]
fig = plt.figure(figsize=(10.5, 6.2)); gs = fig.add_gridspec(2, 1, height_ratios=[1.15, 1], hspace=0.55)
ax = fig.add_subplot(gs[0]); left = np.zeros(len(MM)); cols = [SLOTS[0], "#86b6ef", SLOTS[1], SLOTS[2], "#c3c2b7"]
for c, col in zip(MM.columns, cols):
    ax.barh(range(len(MM)), MM[c], left=left, color=col, edgecolor="white", linewidth=1, label=c)
    for i, (v, l) in enumerate(zip(MM[c], left)):
        if v > 0.09: ax.text(l + v / 2, i, f"{v:.0%}", ha="center", va="center", fontsize=6.5, color="white" if col not in ("#c3c2b7", "#86b6ef") else INK)
    left += MM[c].values
ax.set_yticks(range(len(MM))); ax.set_yticklabels([g.replace("Jazz: ", "Jazz · ").replace("Rock/Pop", "Popular") for g in MM.index]); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
for i, g in enumerate(MM.index): ax.get_yticklabels()[i].set_color(GEN[E0.genre[g]])
ax.legend(ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.08)); ax.set_title("a  Root motion by era (share of all root moves)", loc="left"); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
sel = ["Late Baroque (1700-49)", "Classical (1750-99)", "Early 20th c. (1900-49)", "Jazz: Bebop/Hard bop (1945-59)", "Rock/Pop 1950-64", "Rock/Pop 1985+"]
gs2 = gs[1].subgridspec(1, 6, wspace=0.6)
for j, e in enumerate(sel):
    ax = fig.add_subplot(gs2[j]); d = TC[TC.era == e].head(6)
    ax.barh(range(6), d.share, color=GEN[E0.genre[e]], height=0.65); ax.set_yticks(range(6)); ax.set_yticklabels(d.chord); ax.invert_yaxis(); ax.set_xlim(0, 0.27)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0)); ax.set_xticks([0, 0.1, 0.2]); ax.set_title(e.replace("Jazz: ", "").replace("Rock/Pop", "Popular"), fontsize=7.5)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
fig.text(0.085, 0.43, "b  The six most frequent chords (share of chord events)", fontsize=9, ha="left")
save(fig, "fig2_root_motion")

# ------------------------------------------------------------------ Fig 3 composer map
CS = json.load(open(f"{REPO}/data/composer_space.json")); C = pd.DataFrame(CS["composers"]); C["pc1"] = [p[0] for p in C.pca]; C["pc2"] = [p[1] for p in C.pca]
NAMES = {1: "Bebop to contemporary jazz", 2: "Chromatic and extended", 3: "Triadic, diatonic, plagal", 4: "bVII- and step-driven rock", 5: "Dominant-seventh diatonic", 6: "Common practice"}
MK = {"classical": "o", "jazz": "s", "rock_pop": "^"}
fig, ax = plt.subplots(figsize=(8.5, 6.5))
for _, r in C.iterrows():
    ax.scatter(r.pc1, r.pc2, s=18 + 22 * np.log10(r.n), c=SLOTS[r.cluster - 1], marker=MK[r.genre], alpha=0.45 if r.conf < 0.5 else 0.9, edgecolor="white", linewidth=0.6, zorder=3)
PRI = ["Erwin Schulhoff", "Béla Bartók", "Wayne Shorter", "Stevie Wonder", "Claude Goudimel", "Chicago", "Led Zeppelin", "Louis Armstrong", "Elvis Presley", "The Beatles", "Charlie Parker",
       "Johann Sebastian Bach", "Wolfgang Amadeus Mozart", "Ludwig van Beethoven", "Frédéric Chopin", "Edvard Grieg", "Sergei Rachmaninoff", "Claudio Monteverdi", "François Couperin",
       "John Coltrane", "Miles Davis", "Bob Dylan", "David Bowie", "Chuck Berry", "The Rolling Stones", "Arcangelo Corelli", "Franz Schubert", "Louise Reichardt", "Kenny Rogers", "Michael Jackson"]
placed = []
for name in PRI:
    r = C[C.unit == name]
    if not len(r): continue
    r = r.iloc[0]
    if any(abs(r.pc1 - x) < 0.55 and abs(r.pc2 - y) < 0.22 for x, y in placed): continue
    placed.append((r.pc1, r.pc2))
    short = r.unit.replace("Johann Sebastian ", "J. S. ").replace("Wolfgang Amadeus ", "W. A. ").replace("Ludwig van ", "").replace("Frédéric ", "").replace("Sergei ", "").replace("Claudio ", "").replace("François ", "").replace("Arcangelo ", "").replace("Erwin ", "").replace("Béla ", "")
    ax.annotate(short, (r.pc1, r.pc2), xytext=(4, 3), textcoords="offset points", fontsize=6.5, color=INK)
ex = CS["pca"]["explained"]; ax.set_xlabel(f"PC1 ({ex[0]:.0%} of variance): triadic, plagal  →  seventh-chord, fifth-driven"); ax.set_ylabel(f"PC2 ({ex[1]:.0%}): cadential  →  extended, chromatic, step-driven")
ax.axhline(0, color="#e1e0d9", lw=0.5, zorder=1); ax.axvline(0, color="#e1e0d9", lw=0.5, zorder=1)
h1 = [Patch(color=SLOTS[k - 1], label=f"{k}. {NAMES[k]}") for k in range(1, 7)]; h2 = [Line2D([], [], marker=MK[g], color="#52514e", ls="", label=GLAB[g]) for g in MK]
l1 = ax.legend(handles=h1, loc="upper left", frameon=False, title="Ward group (colour)"); ax.add_artist(l1); ax.legend(handles=h2, loc="lower right", frameon=False, title="Genre (shape)")
ax.text(0.01, 0.01, "marker size ∝ log pieces; faded = membership confidence < 0.5", transform=ax.transAxes, ha="left", va="bottom", fontsize=6.5, color=MUTED)
save(fig, "fig3_composer_map")

# ------------------------------------------------------------------ Fig 4 space-time
P = pd.read_csv(f"{REPO}/data/pieces_spacetime.csv"); SC = pd.read_csv(f"{REPO}/data/scenes.csv"); meta = json.load(open(f"{REPO}/data/basemap_meta.json"))
ter = np.array(Image.open(f"{REPO}/data/terrain.png")); land = ter[:, :, 2] > 127
lon0, lon1 = meta["lon"]; lat0, lat1 = meta["lat"]
sg = SC.set_index("scene_id").harmonic_group; P["hg"] = P.scene_id.map(sg).fillna(0).astype(int)
HG = {1: "#eb6834", 2: "#2a78d6", 3: "#1baf7a", 4: "#eda100"}; HGN = {1: "Late Romantic / 20th c. classical", 2: "Common-practice classical", 3: "Jazz and popular", 4: "Popular, step-driven"}
fig = plt.figure(figsize=(11, 5.2)); ax = fig.add_subplot(1, 2, 1)
ax.imshow(np.where(land, 1.0, np.nan), extent=[lon0, lon1, lat0, lat1], cmap=matplotlib.colors.ListedColormap(["#e8e6df"]), origin="upper", aspect="auto", zorder=0)
sc = ax.scatter(P.lon + np.random.default_rng(0).normal(0, 0.25, len(P)), P.lat + np.random.default_rng(1).normal(0, 0.25, len(P)), c=P.year, cmap="viridis", s=5, alpha=0.6, linewidth=0, zorder=2)
import re
city = lambda l: re.sub(r" \d{4}.*", "", l).split(" / ")[0]
seen = set()
for _, r in SC.sort_values("n_pieces", ascending=False).iterrows():
    c = city(r.label)
    if r.n_pieces > 90 and c not in seen:
        seen.add(c); ax.annotate(c, (r.lon, r.lat), fontsize=6.5, color=INK, xytext=(4, 2), textcoords="offset points", path_effects=HALO)
ax.set_xlim(lon0, lon1); ax.set_ylim(lat0, lat1); ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.set_title("a  Where the pieces were made (colour = year)", loc="left")
cb = fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.02); cb.set_label("Year")
ax3 = fig.add_subplot(1, 2, 2, projection="3d")
for k in [2, 1, 3, 4]:
    d = P[P.hg == k]; ax3.scatter(d.lon, d.lat, d.year, s=3, c=HG[k], alpha=0.5, linewidth=0, label=HGN[k])
for _, r in SC.iterrows():
    if r.n_pieces > 120: ax3.text(r.lon + 1, r.lat, r.year_mid, f"{city(r.label)} {re.search(r'\d{4}', r.label).group()}s", fontsize=5.5, color=INK, path_effects=HALO)
ax3.set_xlabel("Longitude", labelpad=-4); ax3.set_ylabel("Latitude", labelpad=-4); ax3.set_zlabel("Year", labelpad=-2); ax3.tick_params(labelsize=6, pad=-2)
ax3.view_init(elev=22, azim=-60); ax3.set_title("b  The space-time frame (colour = harmonic group of the scene)", loc="left")
ax3.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, 0.95), fontsize=6.5, markerscale=3)
fig.tight_layout(); save(fig, "fig4_space_time")

# ------------------------------------------------------------------ Fig 5 robustness
R = json.load(open(f"{REPO}/data/robustness.json")); PC = pd.read_csv(f"{REPO}/data/pieces.csv"); PC = PC[PC.genre == "classical"]
fig = plt.figure(figsize=(10.5, 6.6)); gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.15], hspace=0.5, wspace=0.35)
for j, (m, lab) in enumerate([("V_to_I_share", "Tonic from V"), ("down5th_share", "Descending fifths"), ("chromatic_root_rate", "Chromatic roots")]):
    ax = fig.add_subplot(gs[0, j]); d = PC.dropna(subset=[m]); x = d.year.values; y = d[m].values
    bins = np.arange(1560, 1960, 20); idx = np.digitize(x, bins); bm = [(bins[i - 1] + 10, y[idx == i].mean(), (idx == i).sum()) for i in range(1, len(bins)) if (idx == i).sum() >= 5]
    ax.scatter([b[0] for b in bm], [b[1] for b in bm], s=[8 + b[2] / 6 for b in bm], color="#c3c2b7", zorder=2, label="20-year bin mean (size = pieces)")
    cp = R["changepoints"][m]; b = cp["break1"]; X = np.column_stack([np.ones_like(x), x, np.clip(x - b, 0, None)]); beta = np.linalg.lstsq(X, y, rcond=None)[0]
    xx = np.linspace(1565, 1935, 200); ax.plot(xx, beta[0] + beta[1] * xx + beta[2] * np.clip(xx - b, 0, None), color=SLOTS[0], lw=1.8, zorder=3, label="single-break fit")
    ax.axvspan(cp["ci"][0], cp["ci"][1], color=SLOTS[0], alpha=0.12, lw=0); ax.axvline(b, color=SLOTS[0], lw=0.8, ls="--")
    ax.set_title(f"{'abc'[j]}  {lab}\nbreak {b:.0f} (CI {cp['ci'][0]:.0f}–{cp['ci'][1]:.0f})", loc="left", fontsize=8.5); pct(ax); ax.set_xlim(1560, 1940); ax.grid(axis="y"); ax.set_axisbelow(True)
    if j == 0: ax.legend(frameon=False, loc="lower right")
ax = fig.add_subplot(gs[1, :]); nt = R["notation"]["metrics"]
ms = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share"]
LAB = {"seventh_rate": "Sevenths", "extended_rate": "9ths+", "nondiatonic_rate": "Non-diatonic", "chromatic_root_rate": "Chromatic roots", "V_to_I_share": "V→I share", "IV_to_I_share": "IV→I share", "bVII_to_I_share": "bVII→I share", "dom_resolution": "V proceeds to I", "down5th_share": "Desc. fifths", "step_share": "Steps", "third_share": "Thirds"}
for i, m in enumerate(ms):
    v = nt[m]; ax.plot([i - 0.18, i + 0.18], [v["rock_mean"], v["billboard_mean"]], color="#c3c2b7", lw=1.2, zorder=1)
    ax.scatter(i - 0.18, v["rock_mean"], color=SLOTS[6], s=28, zorder=3, label="Rock Corpus (Roman numerals)" if i == 0 else None)
    ax.scatter(i + 0.18, v["billboard_mean"], color=SLOTS[2], s=28, zorder=3, label="McGill Billboard (chord symbols)" if i == 0 else None)
    ax.text(i, max(v["rock_mean"], v["billboard_mean"]) + 0.04, f"r = {v['r']:.2f}" if not np.isnan(v["r"]) else "", ha="center", fontsize=6.5, color=MUTED)
    if v["p_wilcoxon"] < 0.05: ax.text(i, -0.06, f"p = {v['p_wilcoxon']:.2f}", ha="center", fontsize=6.5, color=SLOTS[7])
ax.set_xticks(range(len(ms))); ax.set_xticklabels([LAB[m] for m in ms], rotation=0, fontsize=7); pct(ax); ax.set_ylim(-0.08, 0.85); ax.grid(axis="y"); ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper right", ncol=2); ax.set_title("d  Notation check: twelve recordings in both corpora (means; r = paired correlation; p shown where Wilcoxon p < 0.05)", loc="left", fontsize=8.5)
save(fig, "fig5_robustness")

# ------------------------------------------------------------------ S1 fine-grained series
SR = pd.read_csv(f"{REPO}/data/series.csv"); SR = SR[SR.n_pieces >= 5]
MS = ["seventh_rate", "extended_rate", "nondiatonic_rate", "chromatic_root_rate", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "step_share", "third_share", "chord_entropy"]
fig, axs = plt.subplots(3, 4, figsize=(12, 7.5)); axs = axs.ravel()
for ax, m in zip(axs, MS):
    for g in GEN:
        d = SR[SR.genre == g]
        if m + "_lo" in d: ax.fill_between(d.bin_mid, d[m + "_lo"], d[m + "_hi"], color=GEN[g], alpha=0.15, lw=0)
        ax.plot(d.bin_mid, d[m], color=GEN[g], lw=1.3, marker="o", ms=2.5)
    ax.set_title(LAB.get(m, m.replace("_", " ")), loc="left"); ax.set_xlim(1560, 2010); ax.grid(axis="y"); ax.set_axisbelow(True)
    if m != "chord_entropy": pct(ax)
fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.01)); fig.tight_layout(rect=(0, 0.03, 1, 1)); save(fig, "figS1_series")

# ------------------------------------------------------------------ S2 balanced resampling
B = pd.read_csv(f"{REPO}/data/balanced_eras.csv").set_index("era").loc[ORDER]
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.4))
for ax, m in zip(axs, ["seventh_rate", "V_to_I_share", "nondiatonic_rate"]):
    x = np.arange(len(B)); ax.errorbar(x, B[m], yerr=[np.clip(B[m] - B[m + "_lo"], 0, None), np.clip(B[m + "_hi"] - B[m], 0, None)], fmt="o", color=SLOTS[0], ms=4, capsize=2, lw=1, label="capped at 30 pieces per composer (95% over draws)")
    ax.scatter(x + 0.25, B[m + "_full"], color=SLOTS[1], marker="s", s=18, label="all pieces", zorder=3)
    ax.set_xticks(x); ax.set_xticklabels([g.replace("Jazz: ", "").replace("Rock/Pop", "Pop").split(" (")[0] for g in B.index], rotation=70, fontsize=6); pct(ax); ax.set_title(LAB.get(m, m), loc="left"); ax.grid(axis="y"); ax.set_axisbelow(True)
axs[0].legend(frameon=False, fontsize=6.5, loc="upper left"); fig.tight_layout(); save(fig, "figS2_balanced")
