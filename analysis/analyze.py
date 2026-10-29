"""Compute harmonic-evolution metrics from the unified chord table.
Outputs: out/pieces.csv (per-piece metrics) and out/summary.json (aggregates for the dashboard)."""
import os as _os
REPO = _os.environ.get("HARMONY_ROOT", _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import json, math, os
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
from common import era_for, ERA_ORDER

OUT = f"{REPO}/data"
SUF = os.environ.get("HARMONY_OUT_SUFFIX", "")
rng = np.random.default_rng(7)

df = pd.concat([pd.read_csv(f"{OUT}/{SUF if s != 'wir' else ''}chords_{s}.csv") for s in ("dcml", "wir", "modern")], ignore_index=True)
df = df[df.year.notna()].copy()
df["year"] = df.year.astype(int)


def norm_name(n):
    n = str(n)
    if ", " in n:
        sur, given = n.split(", ", 1)
        given = given.replace("(Mendelssohn)", "").strip()
        return f"{given} {sur}".strip()
    return n


df["composer"] = df.composer.map(norm_name)
df["era"] = [era_for(y, g) for y, g in zip(df.year, df.genre)]
df["seventh"] = df.ext.isin(["7", "9+"])
df["extended"] = df.ext == "9+"
df["chromatic_root"] = df.chromatic_root.astype(bool)
df["applied"] = df.applied.astype(bool)

# diatonic quality expectation
DIA_MAJ = {0: "maj", 2: "min", 4: "min", 5: "maj", 7: "maj", 9: "min", 11: "dim"}
DIA_MIN = {0: "min", 2: "dim", 3: "maj", 5: "min", 7: "maj|min", 8: "maj", 10: "maj", 11: "dim"}


def nondiatonic(root, q, mode):
    if q == "nc":
        return False
    tab = DIA_MIN if mode == "minor" else DIA_MAJ
    if root not in tab:
        return True
    if q in ("sus", "power", "other"):
        return False
    return q not in tab[root].split("|")


df["nondiatonic"] = [nondiatonic(r, q, m) for r, q, m in zip(df.root_pc, df.quality, df.key_mode)]

ROMAN_MAJ = {0: "I", 1: "bII", 2: "II", 3: "bIII", 4: "III", 5: "IV", 6: "#IV", 7: "V", 8: "bVI", 9: "VI", 10: "bVII", 11: "VII"}
ROMAN_MIN = {0: "I", 1: "bII", 2: "II", 3: "III", 4: "#III", 5: "IV", 6: "#IV", 7: "V", 8: "VI", 9: "#VI", 10: "VII", 11: "#VII"}


def roman(root, q, mode):
    if q == "nc":
        return "NC"
    r = (ROMAN_MIN if mode == "minor" else ROMAN_MAJ)[int(root)]
    if q in ("min", "dim"):
        r = r.lower()
    suf = {"dim": "°", "aug": "+", "sus": "sus", "power": "5", "aug6": "+6", "other": "?"}.get(q, "")
    return r + suf


df["roman"] = [roman(r, q, m) for r, q, m in zip(df.root_pc, df.quality, df.key_mode)]
df["chord_label"] = df.roman + np.where(df.ext == "9+", "9", np.where(df.ext == "7", "7", ""))

# merge consecutive identical chord labels within a piece (pop sources repeat bars)
df = df.sort_values(["piece_id", "idx"]).reset_index(drop=True)
same = (df.piece_id == df.piece_id.shift()) & (df.chord_label == df.chord_label.shift()) & (df.applied == df.applied.shift())
df["run"] = (~same).cumsum()
agg = {c: "first" for c in df.columns if c not in ("dur", "run")}
agg["dur"] = "sum"
m = df.groupby("run", sort=False).agg(agg).reset_index(drop=True)
m["dur"] = m.dur.where(df.groupby("run").dur.apply(lambda s: s.notna().any()).values)
df = m
print("events after merging repeats:", len(df))


def entropy(counter):
    n = sum(counter.values())
    return -sum(c / n * math.log2(c / n) for c in counter.values()) if n else float("nan")


def rarefied_vocab(labels, k=40):
    """expected number of distinct chord labels in a random sample of k chords"""
    if len(labels) < k:
        return float("nan")
    return float(np.mean([len(set(rng.choice(labels, k, replace=False))) for _ in range(30)]))


MOTION = {5: "down5th", 7: "up5th", 1: "stepUp", 2: "stepUp", 10: "stepDown", 11: "stepDown",
          3: "thirdUp", 4: "thirdUp", 8: "thirdDown", 9: "thirdDown", 6: "tritone", 0: "same"}

piece_rows = []
trans_by_era = defaultdict(Counter)       # era -> Counter((from_label,to_label))
chords_by_era = defaultdict(Counter)      # era -> Counter(label)
motion_by_era = defaultdict(Counter)
for pid, gfull in df.groupby("piece_id", sort=False):
    g = gfull[gfull.quality != "nc"]          # no-chord stretches never count as chords ...
    n = len(g)
    if n < 8:
        continue
    r0 = g.iloc[0]
    roots = g.root_pc.astype(int).values
    quals = g.quality.values
    labels = g.chord_label.values
    era = r0.era
    chords_by_era[era].update(labels)
    # transitions: ... and in strict mode they break the sequence, so no move is counted across them
    fr = gfull.root_pc.astype(int).values; fq = gfull.quality.values; fl = gfull.chord_label.values
    into_tonic = Counter(); from_dom = Counter(); motions = Counter(); trans = Counter()
    for i in range(1, len(gfull)):
        if fq[i] == "nc" or fq[i - 1] == "nc":
            continue
        a, b = fr[i - 1], fr[i]
        mv = (b - a) % 12
        motions[MOTION[mv]] += 1
        trans[(fl[i - 1], fl[i])] += 1
        if b == 0 and fq[i] in ("maj", "min", "power", "sus"):
            into_tonic[a] += 1
        if a == 7 and fq[i - 1] in ("maj",):
            from_dom[b] += 1
    trans_by_era[era].update(trans)
    motion_by_era[era].update(motions)
    nt = sum(into_tonic.values()); nd = sum(from_dom.values())
    nm = sum(motions.values())
    lab_counter = Counter(labels)
    cad = g.cadence.fillna("").astype(str)
    piece_rows.append(dict(
        piece_id=pid, source=r0.source, genre=r0.genre, composer=r0.composer, title=r0.title,
        year=int(r0.year), era=era, key_mode=r0.key_mode, n_chords=n,
        seventh_rate=g.seventh.mean(), extended_rate=g.extended.mean(),
        chromatic_root_rate=g.chromatic_root.mean(), nondiatonic_rate=g.nondiatonic.mean(),
        applied_rate=g.applied.mean() if r0.source in ("DCML", "WiR", "RockCorpus") else float("nan"),
        inversion_rate=(g.inversion.fillna(0) > 0).mean() if r0.source != "WeimarJazz" else float("nan"),
        tonic_share=(roots == 0).mean(), dominant_share=(roots == 7).mean(),
        subdominant_share=(roots == 5).mean(), bVII_share=((roots == 10) & (quals == "maj")).mean() if r0.key_mode == "major" else float("nan"),
        minor_quality_share=(quals == "min").mean(),
        V_to_I_share=into_tonic[7] / nt if nt else float("nan"),
        IV_to_I_share=into_tonic[5] / nt if nt else float("nan"),
        bVII_to_I_share=into_tonic[10] / nt if nt else float("nan"),
        dom_resolution=from_dom[0] / nd if nd else float("nan"),
        down5th_share=motions["down5th"] / nm if nm else float("nan"),
        step_share=(motions["stepUp"] + motions["stepDown"]) / nm if nm else float("nan"),
        third_share=(motions["thirdUp"] + motions["thirdDown"]) / nm if nm else float("nan"),
        chord_entropy=entropy(lab_counter), vocab40=rarefied_vocab(labels, 40),
        beats_per_chord=g.dur.mean() if g.dur.notna().mean() > 0.8 else float("nan"),
        cadences_per100=(cad.isin(["PAC", "IAC", "HC", "DC", "EC", "PC"]).sum() / n * 100) if r0.source == "DCML" else float("nan"),
        pac_per100=((cad == "PAC").sum() / n * 100) if r0.source == "DCML" else float("nan"),
    ))

P = pd.DataFrame(piece_rows)
P.to_csv(f"{OUT}/{SUF}pieces.csv", index=False)
print(P.shape)

METRICS = ["seventh_rate", "extended_rate", "chromatic_root_rate", "nondiatonic_rate", "applied_rate",
           "inversion_rate", "tonic_share", "dominant_share", "subdominant_share", "bVII_share",
           "minor_quality_share", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution",
           "down5th_share", "step_share", "third_share", "chord_entropy", "vocab40", "beats_per_chord",
           "cadences_per100", "pac_per100"]


def boot_ci(x, nb=400):
    x = x[~np.isnan(x)]
    if len(x) < 3:
        return [float("nan")] * 3
    means = [np.mean(rng.choice(x, len(x))) for _ in range(nb)]
    return [float(np.mean(x)), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def summarize(groups):
    out = []
    for key, g in groups:
        row = {"group": key, "n_pieces": int(len(g)), "n_chords": int(g.n_chords.sum()),
               "year_min": int(g.year.min()), "year_max": int(g.year.max()),
               "minor_mode_share": float((g.key_mode == "minor").mean()), "genre": g.genre.iloc[0]}
        for mname in METRICS:
            row[mname] = boot_ci(g[mname].values.astype(float))
        out.append(row)
    return out


eras = summarize([(e, P[P.era == e]) for e in ERA_ORDER if (P.era == e).any()])

# time series: 25-year bins for classical, decades for jazz & rock/pop
P["bin"] = np.where(P.genre == "classical", (P.year // 25) * 25, (P.year // 10) * 10)
series = summarize([(f"{g}:{b}", gg) for (g, b), gg in P.groupby(["genre", "bin"])])

# composer table
comp = summarize([(c, g) for c, g in P[P.genre == "classical"].groupby("composer") if len(g) >= 5])
for row in comp:
    row["median_year"] = int(P[(P.composer == row["group"]) & (P.genre == "classical")].year.median())
comp.sort(key=lambda r: r["median_year"])

# top chords and transitions per era (shares)
top_chords = {}
top_trans = {}
motion = {}
for e in ERA_ORDER:
    if e not in chords_by_era:
        continue
    c = chords_by_era[e]; tot = sum(c.values())
    top_chords[e] = [[k, v / tot] for k, v in c.most_common(15)]
    t = trans_by_era[e]; tt = sum(t.values())
    top_trans[e] = [[a, b, v / tt] for (a, b), v in t.most_common(20)]
    mo = motion_by_era[e]; mt = sum(mo.values())
    motion[e] = {k: v / mt for k, v in mo.items()}
    # pooled transition entropy H(next|cur)
    byfrom = defaultdict(Counter)
    for (a, b), v in t.items():
        byfrom[a][b] += v
    H = sum(sum(cn.values()) / tt * entropy(cn) for cn in byfrom.values())
    for row in eras:
        if row["group"] == e:
            row["transition_entropy"] = H
            row["chord_entropy_pooled"] = entropy(c)

# Classical-vs-modern "progression network": pooled 12-root matrix per genre (major-mode pieces)
networks = {}
for gname, gg in df[df.key_mode == "major"].groupby("genre"):
    M = np.zeros((12, 12))
    for pid, g in gg.groupby("piece_id", sort=False):
        r = g.root_pc.astype(int).values
        for i in range(1, len(r)):
            if r[i] != r[i - 1]:
                M[r[i - 1], r[i]] += 1
    networks[gname] = (M / M.sum()).round(5).tolist()

summary = dict(eras=eras, series=series, composers=comp, top_chords=top_chords, top_transitions=top_trans,
               motion=motion, networks=networks, era_order=ERA_ORDER,
               totals=dict(pieces=int(len(P)), chords=int(P.n_chords.sum()),
                           by_source=P.groupby("source").agg(pieces=("piece_id", "size"), chords=("n_chords", "sum"),
                                                              ymin=("year", "min"), ymax=("year", "max")).reset_index().to_dict("records")))
json.dump(summary, open(f"{OUT}/{SUF}summary.json", "w"), default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
pd.DataFrame([{k: (v[0] if isinstance(v, list) else v) for k, v in r.items()} for r in eras]).to_csv(f"{OUT}/{SUF}era_summary.csv", index=False)
print(pd.DataFrame([{k: (round(v[0], 3) if isinstance(v, list) else v) for k, v in r.items()} for r in eras])[
    ["group", "n_pieces", "seventh_rate", "extended_rate", "chromatic_root_rate", "nondiatonic_rate", "V_to_I_share", "IV_to_I_share", "bVII_to_I_share", "dom_resolution", "down5th_share", "chord_entropy", "vocab40", "beats_per_chord"]].to_string())
