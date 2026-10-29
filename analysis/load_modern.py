"""Load modern corpora into the unified schema:
  * Rock Corpus (de Clercq & Temperley, RS200): expert Roman numerals, years from Rolling Stone list
  * McGill Billboard (Burgoyne et al.): Harte chord symbols + tonic, years from chart dates
  * Weimar Jazz Database: chord symbols per beat + key, recording years
"""
import os as _os
REPO = _os.environ.get("HARMONY_ROOT", _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import csv, glob, json, os, re, sqlite3
STRICT_NC = os.environ.get("STRICT_NC") == "1"
import pandas as pd
from common import COLUMNS, is_diatonic, pitch_class

P = f"{REPO}/corpora/choco/partitions"
OUT = f"{REPO}/data/" + os.environ.get("HARMONY_OUT_SUFFIX", "") + "chords_modern.csv"
rows = []


def emit(**kw):
    rows.append({c: kw.get(c) for c in COLUMNS})


def infer_mode(events):
    """major/minor from the quality of chords built on the tonic."""
    events = [e for e in events if e["quality"] != "nc"]
    maj = sum(1 for e in events if e["root_pc"] == 0 and e["quality"] == "maj")
    mn = sum(1 for e in events if e["root_pc"] == 0 and e["quality"] == "min")
    return "minor" if mn > maj else "major"


def finalize(events, **meta):
    mode = infer_mode(events)
    for i, e in enumerate(events):
        e["chromatic_root"] = False if e["quality"] == "nc" else not is_diatonic(e["root_pc"], mode)
        emit(idx=i, key_mode=mode, **e, **meta)


# ---------------------------------------------------------------- Rock Corpus
def rock_quality(sym):
    """RS200 numeral like 'IVd7', 'iih7', 'V11', 'bVIs4', 'viix7/V' -> features"""
    applied = "/" in sym
    base = sym.split("/")[0]
    m = re.match(r"^([b#]*)([ivIV]+)(.*)$", base)
    if not m:
        return None
    acc, num, suf = m.groups()
    upper = num.isupper()
    q = "maj" if upper else "min"
    if "x" in suf: q = "dim"
    elif "h" in suf: q = "dim"
    elif "o" in suf: q = "dim"
    elif "+" in suf or "a" in suf: q = "aug"
    if "s4" in suf or "s2" in suf: q = "sus"
    if "b5" in suf and q == "maj": q = "other"
    has9 = bool(re.search(r"(9|11|13)", suf))
    seventh_figs = re.search(r"(d7|h7|x7|7|65|43|42)", suf)
    has7 = bool(seventh_figs) or has9
    s7 = ""
    if has7:
        if "x7" in suf: s7 = "dim7"
        elif "h" in suf: s7 = "hdim7"
        elif "d7" in suf: s7 = "dom7"
        elif q == "min": s7 = "min7"
        elif q == "maj": s7 = "dom7" if num.upper() in ("V", "VII") or acc else "maj7"
        elif q == "dim": s7 = "hdim7"
        else: s7 = "other7"
        if has9 and q == "maj" and s7 == "maj7" and num.upper() == "V": s7 = "dom7"
    ext = "9+" if has9 else ("7" if has7 else ("add6" if re.search(r"(?<!\d)6(?!\d)", suf) and "64" not in suf and "65" not in suf and False else "triad"))
    inv = 0
    if re.search(r"(?<!\d)6(?!\d)", suf) or "65" in suf: inv = 1
    if "64" in suf or "43" in suf: inv = 2
    if "42" in suf: inv = 3
    return dict(quality=q, ext=ext, seventh_type=s7, applied=applied, inversion=inv)


def load_rock():
    years = {}
    for line in open(f"{P}/rock-corpus/raw/rs500.txt", encoding="utf-8", errors="ignore"):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 4 and parts[3].strip().isdigit():
            years[parts[1].strip().lower()] = (int(parts[3]), parts[2].strip())
    files = json.load(open(f"{P}/rock-corpus/raw/files.json"))
    manual = {  # titles that differ between the corpus and the Rolling Stone list
        "Brown-Eyed Girl": "brown eyed girl", "Dont Worry Baby": "don't worry baby",
        "Good Golly Miss Molly": '"good golly, miss molly"', "Help": "help!",
        "I'm So Lonesome": "i'm so lonesome i could cry", "In My Life (1965)": "in my life",
        "It's A Man's, Man's, Man's World": "it's a man's man's man's world",
        "I've Been Loving You": "i've been loving you too long (to stop now)",
        "No Woman No Cry": '"no woman, no cry"', "Norwegian Wood": "norwegian wood (this bird has flown)",
        "Nuthin' But A G Thang": "nuthin' but a 'g' thang", "Paint It Black": '"paint it, black"',
        "Please, Please, Please": '"please, please, please"', "Rock And Roll Music": "rock & roll music",
        "Rock Around The Clock": "(we're gonna) rock around the clock",
        "Shake Rattle And Roll": '"shake, rattle and roll"',
        "Should I Stay Or Should I Go?": "should i stay or should i go", "Shout": "shout (parts 1 and 2)",
        "Dock Of The Bay": "(sittin' on) the dock of the bay", "Voodoo Child": "voodoo child (slight return)",
        "Whole Lotta Shakin' Goin' On": "whole lotta shakin' goin on", "Yesterday (1965)": "yesterday",
    }
    years["mr. tambourine man (byrds)"] = (1965, "The Byrds")
    years["mr. tambourine man (dylan)"] = (1965, "Bob Dylan")
    n = 0
    for title, stem in files.items():
        yr = years.get(manual.get(title, title).lower())
        if not yr:
            continue
        path = f"{P}/rock-corpus/raw/rs200_harmony_clt/{stem}_dt.clt"
        if not os.path.exists(path):
            path = f"{P}/rock-corpus/raw/rs200_harmony_clt/{stem}_tdc.clt"
        if not os.path.exists(path):
            continue
        events = []
        prev_t = None
        meter = json.load(open(f"{P}/rock-corpus/raw/songs.json")).get(title, {}).get("meter", "4/4")
        bpb = int(meter.split("/")[0]) if meter and meter[0].isdigit() else 4
        if bpb == 12: bpb = 4
        for line in open(path):
            c = line.rstrip("\n").split("\t")
            if len(c) < 7 or c[2] == "End":
                continue
            f = rock_quality(c[2])
            if f is None:
                continue
            t = float(c[1])  # metric position in bars
            if events and prev_t is not None:
                events[-1]["dur"] = (t - prev_t) * bpb
            prev_t = t
            events.append(dict(root_pc=int(c[3]) % 12, dur=None, cadence="", label=c[2], **f))
        if events:
            finalize(events, source="RockCorpus", genre="rock_pop", piece_id=f"rs200:{stem}",
                     composer=yr[1], title=title, year=yr[0])
            n += 1
    print("rock corpus songs:", n)


# ---------------------------------------------------------------- Billboard
SHORT = {  # harte shorthand -> (quality, seventh_type, ext)
    "maj": ("maj", "", "triad"), "min": ("min", "", "triad"), "dim": ("dim", "", "triad"),
    "aug": ("aug", "", "triad"), "7": ("maj", "dom7", "7"), "min7": ("min", "min7", "7"),
    "maj7": ("maj", "maj7", "7"), "dim7": ("dim", "dim7", "7"), "hdim7": ("dim", "hdim7", "7"),
    "minmaj7": ("min", "minmaj7", "7"), "maj6": ("maj", "", "add6"), "min6": ("min", "", "add6"),
    "9": ("maj", "dom7", "9+"), "maj9": ("maj", "maj7", "9+"), "min9": ("min", "min7", "9+"),
    "11": ("maj", "dom7", "9+"), "min11": ("min", "min7", "9+"), "13": ("maj", "dom7", "9+"),
    "maj13": ("maj", "maj7", "9+"), "min13": ("min", "min7", "9+"),
    "sus4": ("sus", "", "triad"), "sus2": ("sus", "", "triad"), "1": ("power", "", "triad"),
    "5": ("power", "", "triad"), "": ("maj", "", "triad"),
}


def harte(sym):
    m = re.match(r"^([A-G][#b]*)(?::([a-z0-9]*))?(?:\(([^)]*)\))?(?:/(\S+))?$", sym)
    if not m:
        return None
    root, short, adds, bass = m.groups()
    short = short or ""
    if short not in SHORT:
        return None
    q, s7, ext = SHORT[short]
    adds = adds or ""
    if "7" in adds or "b7" in adds:
        if ext == "triad": ext = "7"
        if not s7: s7 = "maj7" if "7" in adds and "b7" not in adds and q == "maj" else ("dom7" if q in ("maj", "sus", "power") else "min7")
    if re.search(r"(9|11|13)", adds):
        ext = "9+"
    inv = 0
    if bass:
        inv = {"3": 1, "b3": 1, "5": 2, "b7": 3, "7": 3}.get(bass, 0)
    return dict(root=pitch_class(root), quality=q, seventh_type=s7, ext=ext, inversion=inv)


def load_billboard():
    idx = {}
    with open(f"{P}/billboard/raw/billboard-2.0-index.csv") as fh:
        for r in csv.DictReader(fh):
            idx[int(r["id"])] = r["chart_date"][:4]
    n = 0
    for d in sorted(glob.glob(f"{P}/billboard/raw/original/*/salami_chords.txt")):
        bid = int(os.path.basename(os.path.dirname(d)))
        year = idx.get(bid)
        if not year:
            continue
        title = artist = ""
        tonic = None
        beats_per_bar = 4
        events = []
        for line in open(d, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith("# title:"): title = line[8:].strip()
            elif line.startswith("# artist:"): artist = line[9:].strip()
            elif line.startswith("# tonic:"): tonic = pitch_class(line[8:].strip())
            elif line.startswith("# metre:"):
                try: beats_per_bar = int(line[8:].strip().split("/")[0])
                except ValueError: pass
            elif "|" in line and tonic is not None:
                body = line.split("\t", 1)[1] if "\t" in line else line
                bars = [b.strip() for b in body.split("|")]
                bars = [b for b in bars if b and not b.startswith(",") and (":" in b or (STRICT_NC and "N" in b.split())) or b == "." or (b and b[0] in "ABCDEFG")]
                for bar in bars:
                    toks = bar.split()
                    toks = [t for t in toks if t != "" and not t.startswith("(")]
                    if not toks:
                        continue
                    k = len(toks)
                    for t in toks:
                        if t == ".":
                            if events: events[-1]["dur"] += beats_per_bar / k
                            continue
                        if STRICT_NC and t == "N":
                            events.append(dict(root_pc=-1, quality="nc", ext="triad", seventh_type="", applied=False, inversion=0, dur=beats_per_bar / k, cadence="", label="N"))
                            continue
                        f = harte(t)
                        if f is None or f["root"] is None:
                            continue
                        events.append(dict(root_pc=(f["root"] - tonic) % 12, quality=f["quality"],
                                           ext=f["ext"], seventh_type=f["seventh_type"],
                                           applied=False, inversion=f["inversion"],
                                           dur=beats_per_bar / k, cadence="", label=t))
        if len(events) >= 8:
            finalize(events, source="Billboard", genre="rock_pop", piece_id=f"billboard:{bid}",
                     composer=artist, title=title, year=int(year))
            n += 1
    print("billboard songs:", n)


# ---------------------------------------------------------------- Weimar jazz
def jazz_chord(sym):
    """Weimar notation: 'Bb7', 'C-7', 'Ebj7', 'Am7b5', 'Eo7', 'G+7', 'D79b', 'Fsus7', 'C69', 'C-/Bb'"""
    sym = sym.split("/")[0]
    m = re.match(r"^([A-G][#b]*)(.*)$", sym)
    if not m:
        return None
    root, suf = m.groups()
    q = "maj"
    if suf.startswith("-"): q = "min"
    elif suf.startswith("o"): q = "dim"
    elif suf.startswith("+"): q = "aug"
    elif suf.startswith("sus"): q = "sus"
    elif "m7b5" in suf: q = "dim"
    s7 = ""; ext = "triad"
    if "j7" in suf: s7 = "maj7" if q != "min" else "minmaj7"
    elif "m7b5" in suf: s7 = "hdim7"
    elif suf.startswith("o7"): s7 = "dim7"
    elif "7" in suf or "9" in suf or "11" in suf or "13" in suf or "alt" in suf:
        s7 = {"maj": "dom7", "min": "min7", "dim": "hdim7", "aug": "aug7", "sus": "dom7"}[q]
    if s7: ext = "7"
    if re.search(r"(9|11|13|alt)", suf): ext = "9+"
    if ext == "triad" and re.search(r"(?<!\d)6", suf): ext = "add6"
    if "69" in suf: ext = "9+"
    return dict(root=pitch_class(root), quality=q, seventh_type=s7, ext=ext)


def load_weimar():
    c = sqlite3.connect(f"{P}/weimar/raw/wjazzd.db")
    q = """select s.melid, s.title, s.performer, s.key, s.style, t.recordingdate
           from solo_info s join track_info t on s.trackid=t.trackid"""
    n = 0
    for melid, title, performer, key, style, rd in c.execute(q).fetchall():
        m = re.search(r"(19\d\d|20\d\d)", rd or "")
        if not m or not key:
            continue
        year = int(m.group(1))
        tonic = pitch_class(key.split("-")[0])
        if tonic is None:
            continue
        beats = c.execute("select onset, bar, beat, chord, signature from beats where melid=? order by onset", (melid,)).fetchall()
        events = []
        prev = None
        for onset, bar, beat, chord, sig in beats:
            if not chord or (chord == "NC" and not STRICT_NC):
                continue
            try: bpb = int(str(sig).split("/")[0]) if sig else 4
            except ValueError: bpb = 4
            onset = bar * bpb + beat  # position in beats
            if chord == prev:
                continue
            if chord == "NC":
                if events: events[-1]["dur"] = onset - events[-1]["_t"]
                events.append(dict(root_pc=-1, quality="nc", ext="triad", seventh_type="", applied=False, inversion=0, dur=None, cadence="", label="NC", _t=onset)); prev = chord
                continue
            f = jazz_chord(chord)
            if f is None or f["root"] is None:
                continue
            if events:
                events[-1]["dur"] = onset - events[-1]["_t"]
            events.append(dict(root_pc=(f["root"] - tonic) % 12, quality=f["quality"], ext=f["ext"],
                               seventh_type=f["seventh_type"], applied=False, inversion=0,
                               dur=None, cadence="", label=chord, _t=onset))
            prev = chord
        for e in events:
            e.pop("_t")
        if len(events) >= 8:
            finalize(events, source="WeimarJazz", genre="jazz", piece_id=f"wjd:{melid}",
                     composer=performer, title=f"{title} [{style}]", year=year)
            n += 1
    print("weimar solos:", n)


if __name__ == "__main__":
    load_rock(); load_billboard(); load_weimar()
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(OUT, index=False)
    print(df.shape)
    print(df.groupby("source").agg(pieces=("piece_id", "nunique"), ymin=("year", "min"), ymax=("year", "max"), n=("idx", "size")))
    print(df.groupby("source").quality.value_counts(normalize=True).round(3).unstack())
    print(df.groupby("source").ext.value_counts(normalize=True).round(3).unstack())
