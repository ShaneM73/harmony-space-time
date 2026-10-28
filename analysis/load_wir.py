"""Load the When-in-Rome RomanText analyses that are NOT already in the DCML
corpus (Bach chorales, Goudimel, Lieder, Haydn quartets, extra Beethoven, ...).
Dates are assigned from the collection / opus, see date_for()."""
import os as _os
REPO = _os.environ.get("HARMONY_ROOT", _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import glob, os, re, sys, warnings
from multiprocessing import Pool
import pandas as pd
from music21 import converter
from common import COLUMNS, is_diatonic

warnings.filterwarnings("ignore")
ROOT = f"{REPO}/corpora/wir/Corpus"
OUT = f"{REPO}/data/chords_wir.csv"
DCML_ROOT = f"{REPO}/corpora/dlc"

BEETHOVEN_SONATAS = {2: 1795, 7: 1797, 10: 1798, 13: 1798, 14: 1799, 22: 1800, 26: 1801,
                     27: 1801, 28: 1801, 31: 1802, 49: 1797, 53: 1804, 54: 1804, 57: 1805,
                     78: 1809, 79: 1809, 81: 1810, 90: 1814, 101: 1816, 106: 1818,
                     109: 1820, 110: 1821, 111: 1822}
BEETHOVEN_VARS = {"Op34": 1802, "Op76": 1809, "WoO_63": 1782, "WoO_64": 1790, "WoO_65": 1790,
                  "WoO_66": 1792, "WoO_68": 1795, "WoO_69": 1795, "WoO_70": 1795, "WoO_71": 1796,
                  "WoO_72": 1796, "WoO_73": 1799, "WoO_75": 1799, "WoO_76": 1799, "WoO_77": 1800,
                  "WoO_78": 1803, "WoO_80": 1806}
MOZART_VARS = {"K025": 1766, "K179": 1774, "K265": 1781, "K353": 1781, "K354": 1778,
               "K398": 1783, "K455": 1784, "K501": 1786, "K573": 1789, "K613": 1791}
HAYDN_QT = {20: 1772, 33: 1781, 42: 1785, 50: 1787, 54: 1788, 55: 1788, 64: 1790,
            71: 1793, 74: 1793, 76: 1797, 77: 1799}
LIEDER = {  # (composer, collection) -> year ; collection "*" = default for composer
    ("Bonis", "*"): 1895, ("Brahms", "6_Songs,_Op.3"): 1853, ("Brahms", "Marienlieder,_Op.22"): 1859,
    ("Brahms", "7_Lieder,_Op.48"): 1868, ("Brahms", "*"): 1865,
    ("Burleigh", "*"): 1915, ("Chaminade", "*"): 1890, ("Chausson", "*"): 1882,
    ("Coleridge-Taylor", "*"): 1904, ("Fauré", "*"): 1878, ("Franz", "*"): 1850,
    ("Hensel", "6_Lieder,_Op.1"): 1846, ("Hensel", "6_Lieder,_Op.7"): 1847, ("Hensel", "6_Lieder,_Op.9"): 1838,
    ("Hensel", "5_Lieder,_Op.10"): 1841, ("Hensel", "Gartenlieder,_Op.3"): 1846, ("Hensel", "*"): 1840,
    ("Holmès", "*"): 1890, ("Jaëll", "*"): 1880, ("Joplin", "*"): 1905,
    ("Kinkel", "6_Lieder,_Op.10"): 1840, ("Kinkel", "*"): 1841, ("Kralik", "*"): 1890,
    ("Lang", "3_Lieder,_Op.8"): 1838, ("Lang", "6_Lieder,_Op.10"): 1841, ("Lang", "6_Lieder,_Op.12"): 1845,
    ("Lang", "6_Lieder,_Op.13"): 1847, ("Lang", "*"): 1860,
    ("Mayer", "*"): 1850, ("Paradis", "*"): 1786, ("Reichardt", "*"): 1810,
    ("Schubert", "Die_schöne_Müllerin,_D.795"): 1823, ("Schubert", "Op.52"): 1825, ("Schubert", "Op.59"): 1826,
    ("Schubert", "4_Lieder,_Op.96"): 1826, ("Schubert", "Schwanengesang,_D.957"): 1828, ("Schubert", "*"): 1820,
    ("Schumann", "Dichterliebe,_Op.48"): 1840, ("Schumann", "Frauenliebe_und_Leben,_Op.42"): 1840,
    ("Schumann", "Myrthen,_Op.25"): 1840, ("Schumann", "5_Lieder_und_Gesänge,_Op.127"): 1850,
    ("Viardot", "*"): 1880, ("White", "*"): 1885, ("Wolf", "*"): 1888, ("Zumsteeg", "*"): 1840,
}
SKIP_COMPOSERS_IN_LIEDER = {"Mahler", "Schumann,_Clara"}  # covered by DCML
MONTEVERDI_BOOK_YEAR = {"3": 1592, "4": 1603, "5": 1605}


def dcml_monteverdi():
    s = set()
    for f in glob.glob(os.path.join(DCML_ROOT, "monteverdi_madrigals/harmonies/*.tsv")):
        m = re.match(r"(\d)-(\d+)", os.path.basename(f))
        if m:
            s.add((m.group(1), int(m.group(2))))
    return s


DCML_MONTEVERDI = dcml_monteverdi()


def date_for(parts):
    """parts = path components after Corpus/: [collection, composer, work..., analysis.txt]"""
    coll, comp = parts[0], parts[1]
    rest = parts[2:-1]
    if coll == "Early_Choral":
        if comp.startswith("Bach"): return 1725
        if comp.startswith("Goudimel"): return 1565
        if comp.startswith("Monteverdi"):
            book = rest[0].split("_")[-1]
            if (book, int(rest[1])) in DCML_MONTEVERDI:
                return None
            return MONTEVERDI_BOOK_YEAR.get(book)
    if coll == "Keyboard_Other" and comp.startswith("Bach"):
        return 1722 if rest[0].endswith("_I") else 1742
    if coll == "Variations_and_Grounds":
        if comp.startswith("Bach"): return 1749 if "mass" in rest[0] else 1720
        if comp.startswith("Beethoven"): return BEETHOVEN_VARS.get(rest[1])
        if comp.startswith("Mozart"): return MOZART_VARS.get(rest[1])
        if comp.startswith("Purcell"): return 1680
    if coll == "Piano_Sonatas" and comp.startswith("Beethoven"):
        m = re.match(r"Op(\d+)", rest[0]); return BEETHOVEN_SONATAS.get(int(m.group(1))) if m else None
    if coll == "Quartets":
        if comp.startswith("Haydn"):
            m = re.match(r"Op(\d+)", rest[0]); return HAYDN_QT.get(int(m.group(1))) if m else None
        if comp.startswith("Brahms"): return 1873
    if coll == "Orchestral":
        return 1795 if comp.startswith("Haydn") else 1868
    if coll == "OpenScore-LiederCorpus":
        if comp in SKIP_COMPOSERS_IN_LIEDER or comp.startswith("Mahler") or comp.startswith("Schumann,_Clara"):
            return None
        surname = comp.split(",")[0]
        return LIEDER.get((surname, rest[0]), LIEDER.get((surname, "*")))
    return None


def parse_one(path):
    parts = os.path.relpath(path, ROOT).split(os.sep)
    with open(path, encoding="utf-8", errors="ignore") as fh:
        head = fh.read(600)
    if "DCML" in head:
        return []
    year = date_for(parts)
    if year is None:
        return []
    composer = parts[1].replace("_", " ")
    coll = parts[0]
    title = "/".join(parts[2:-1])
    try:
        s = converter.parse(path, format="romanText")
    except Exception as e:
        return []
    rows = []
    i = 0
    gmode = None
    for rn in s.recurse().getElementsByClass("RomanNumeral"):
        k = rn.key
        if k is None:
            continue
        if gmode is None:
            gmode = k.mode
        try:
            root_pc = (rn.root().pitchClass - k.tonic.pitchClass) % 12
        except Exception:
            continue
        q = rn.quality
        fig = rn.figure
        q = {"major": "maj", "minor": "min", "diminished": "dim", "augmented": "aug"}.get(q, "other")
        if re.search(r"(It|Ger|Fr)", fig):
            q = "aug6"
        has7 = rn.containsSeventh()
        has9 = rn.isNinth() or bool(re.search(r"(?<!\d)(9|11|13)", fig))
        s7 = ""
        if has7:
            if q == "maj":
                s7 = "dom7" if rn.seventh is not None and (rn.seventh.pitchClass - rn.root().pitchClass) % 12 == 10 else "maj7"
            elif q == "min":
                s7 = "min7" if rn.seventh is not None and (rn.seventh.pitchClass - rn.root().pitchClass) % 12 == 10 else "minmaj7"
            elif q == "dim":
                s7 = "dim7" if rn.seventh is not None and (rn.seventh.pitchClass - rn.root().pitchClass) % 12 == 9 else "hdim7"
            elif q == "aug6":
                s7 = "aug6"
            else:
                s7 = "other7"
        ext = "9+" if has9 else ("7" if has7 else "triad")
        try:
            inv = rn.inversion()
        except Exception:
            inv = 0
        rows.append(dict(
            source="WiR", genre="classical", piece_id="wir:" + "/".join(parts[:-1]),
            composer=composer, title=title, year=year, key_mode=gmode,
            idx=i, root_pc=root_pc, quality=q, ext=ext, seventh_type=s7,
            chromatic_root=not is_diatonic(root_pc, k.mode),
            applied=rn.secondaryRomanNumeral is not None,
            inversion=inv, dur=float(rn.quarterLength), cadence="", label=fig,
        ))
        i += 1
    return rows


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(ROOT, "**", "analysis.txt"), recursive=True))
    with Pool(8) as p:
        res = p.map(parse_one, files, chunksize=4)
    rows = [r for rs in res for r in rs]
    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(OUT, index=False)
    print(df.shape, df.piece_id.nunique(), "pieces")
    print(df.groupby("composer").piece_id.nunique())
