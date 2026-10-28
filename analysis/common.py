"""Shared vocabulary for the unified chord-event table.

Every loader emits rows with these columns:
  source, genre, piece_id, composer, title, year, key_mode,
  idx, root_pc, quality, ext, seventh_type, chromatic_root, applied,
  inversion, dur, cadence, label
"""
import re

COLUMNS = ["source", "genre", "piece_id", "composer", "title", "year", "key_mode",
           "idx", "root_pc", "quality", "ext", "seventh_type", "chromatic_root",
           "applied", "inversion", "dur", "cadence", "label"]

MAJOR_DIATONIC = {0, 2, 4, 5, 7, 9, 11}
# natural minor plus the raised leading tone (harmonic minor), the usual
# common-practice notion of "diatonic in minor"
MINOR_DIATONIC = {0, 2, 3, 5, 7, 8, 10, 11}

PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pitch_class(name: str):
    """'Bb' -> 10, 'F#' -> 6, 'Cb' -> 11. Returns None if unparseable."""
    if not name:
        return None
    m = re.match(r"^([A-Ga-g])([#b]*)", name.strip())
    if not m:
        return None
    pc = PC[m.group(1).upper()]
    for a in m.group(2):
        pc += 1 if a == "#" else -1
    return pc % 12


def is_diatonic(root_pc, key_mode):
    if root_pc is None:
        return None
    s = MINOR_DIATONIC if key_mode == "minor" else MAJOR_DIATONIC
    return root_pc in s


def era_for(year, genre):
    if year is None or year != year:  # NaN
        return "unknown"
    y = int(year)
    if genre == "classical":
        if y < 1600: return "Renaissance (<1600)"
        if y < 1700: return "Early Baroque (1600-99)"
        if y < 1750: return "Late Baroque (1700-49)"
        if y < 1800: return "Classical (1750-99)"
        if y < 1850: return "Early Romantic (1800-49)"
        if y < 1900: return "Late Romantic (1850-99)"
        return "Early 20th c. (1900-49)"
    if genre == "jazz":
        if y < 1945: return "Jazz: Swing era (<1945)"
        if y < 1960: return "Jazz: Bebop/Hard bop (1945-59)"
        if y < 1975: return "Jazz: Modal/Post-bop (1960-74)"
        return "Jazz: 1975+"
    # rock / pop
    if y < 1965: return "Rock/Pop 1950-64"
    if y < 1975: return "Rock/Pop 1965-74"
    if y < 1985: return "Rock/Pop 1975-84"
    return "Rock/Pop 1985+"


ERA_ORDER = [
    "Renaissance (<1600)", "Early Baroque (1600-99)", "Late Baroque (1700-49)",
    "Classical (1750-99)", "Early Romantic (1800-49)", "Late Romantic (1850-99)",
    "Early 20th c. (1900-49)",
    "Jazz: Swing era (<1945)", "Jazz: Bebop/Hard bop (1945-59)",
    "Jazz: Modal/Post-bop (1960-74)", "Jazz: 1975+",
    "Rock/Pop 1950-64", "Rock/Pop 1965-74", "Rock/Pop 1975-84", "Rock/Pop 1985+",
]
