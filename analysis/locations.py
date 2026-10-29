"""Where each piece was made: composer residence timelines, performer/artist base cities.

Sources: standard biographical reference (Grove / composer biographies), typed from knowledge.
confidence: 'high' = composer's documented residence in that year; 'medium' = artist's base city /
recording city in that period; 'low' = artist's home town as a proxy.
Nothing in the corpora records composition place, so this is an assignment, not a field."""
import os as _os
REPO = _os.environ.get("HARMONY_ROOT", _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

import pandas as pd

CITY = {  # city: (lat, lon, country)
    "Metz": (49.12, 6.18, "France"), "Cremona": (45.13, 10.02, "Italy"), "Mantua": (45.16, 10.79, "Italy"),
    "Venice": (45.44, 12.33, "Italy"), "Florence": (43.77, 11.26, "Italy"), "Amsterdam": (52.37, 4.90, "Netherlands"),
    "Rome": (41.90, 12.50, "Italy"), "Dresden": (51.05, 13.74, "Germany"), "London": (51.51, -0.13, "UK"),
    "Paris": (48.86, 2.35, "France"), "Weimar": (50.98, 11.33, "Germany"), "Köthen": (51.75, 11.97, "Germany"),
    "Leipzig": (51.34, 12.37, "Germany"), "Naples": (40.85, 14.27, "Italy"), "Madrid": (40.42, -3.70, "Spain"),
    "Halle": (51.48, 11.97, "Germany"), "Berlin": (52.52, 13.41, "Germany"), "Hamburg": (53.55, 9.99, "Germany"),
    "Salzburg": (47.80, 13.04, "Austria"), "Vienna": (48.21, 16.37, "Austria"), "The Hague": (52.08, 4.31, "Netherlands"),
    "Eszterháza": (47.63, 16.88, "Hungary"), "Bonn": (50.74, 7.10, "Germany"), "Strasbourg": (48.57, 7.75, "France"),
    "Warsaw": (52.23, 21.01, "Poland"), "Düsseldorf": (51.23, 6.78, "Germany"), "Munich": (48.14, 11.58, "Germany"),
    "Tübingen": (48.52, 9.06, "Germany"), "Stuttgart": (48.78, 9.18, "Germany"), "Lucerne": (47.05, 8.31, "Switzerland"),
    "Oslo": (59.91, 10.75, "Norway"), "Bergen": (60.39, 5.32, "Norway"), "Moscow": (55.76, 37.62, "Russia"),
    "Prague": (50.08, 14.44, "Czechia"), "Budapest": (47.50, 19.04, "Hungary"), "New York": (40.71, -74.01, "USA"),
    "Chicago": (41.88, -87.63, "USA"), "Los Angeles": (34.05, -118.24, "USA"), "San Francisco": (37.77, -122.42, "USA"),
    "Philadelphia": (39.95, -75.17, "USA"), "Detroit": (42.33, -83.05, "USA"), "Memphis": (35.15, -90.05, "USA"),
    "Nashville": (36.16, -86.78, "USA"), "New Orleans": (29.95, -90.07, "USA"), "Kansas City": (39.10, -94.58, "USA"),
    "Copenhagen": (55.68, 12.57, "Denmark"), "Atlanta": (33.75, -84.39, "USA"), "Boston": (42.36, -71.06, "USA"),
    "Seattle": (47.61, -122.33, "USA"), "Minneapolis": (44.98, -93.27, "USA"), "Macon": (32.84, -83.63, "USA"),
    "St. Louis": (38.63, -90.20, "USA"), "Houston": (29.76, -95.37, "USA"), "Dallas": (32.78, -96.80, "USA"),
    "Lubbock": (33.58, -101.86, "USA"), "Austin": (30.27, -97.74, "USA"), "Muscle Shoals": (34.74, -87.67, "USA"),
    "Kingston": (17.97, -76.79, "Jamaica"), "Dublin": (53.35, -6.26, "Ireland"), "Manchester": (53.48, -2.24, "UK"),
    "Liverpool": (53.41, -2.98, "UK"), "Birmingham": (52.49, -1.89, "UK"), "Newcastle": (54.98, -1.61, "UK"),
    "Oxford": (51.75, -1.26, "UK"), "Glasgow": (55.86, -4.25, "UK"), "Belfast": (54.60, -5.93, "UK"),
    "Sydney": (-33.87, 151.21, "Australia"), "Melbourne": (-33.87 + -3.95, 144.96, "Australia"),
    "Stockholm": (59.33, 18.07, "Sweden"), "Toronto": (43.65, -79.38, "Canada"), "Montreal": (45.50, -73.57, "Canada"),
    "Athens GA": (33.96, -83.38, "USA"), "Stockton": (37.96, -121.29, "USA"), "Cleveland": (41.50, -81.69, "USA"),
    "Pittsburgh": (40.44, -79.99, "USA"), "Miami": (25.76, -80.19, "USA"), "Denver": (39.74, -104.98, "USA"),
    "Portland": (45.52, -122.68, "USA"), "Rockford": (42.27, -89.09, "USA"), "Milwaukee": (43.04, -87.91, "USA"),
    "Cincinnati": (39.10, -84.51, "USA"), "Jacksonville": (30.33, -81.66, "USA"), "Louisville": (38.25, -85.76, "USA"),
    "Richmond": (37.54, -77.44, "USA"), "Winnipeg": (49.90, -97.14, "Canada"), "Frankfurt": (50.11, 8.68, "Germany"),
    "Munich DE": (48.14, 11.58, "Germany"), "Rotterdam": (51.92, 4.48, "Netherlands"), "Tokyo": (35.68, 139.69, "Japan"),
    "Hilversum": (52.22, 5.17, "Netherlands"), "Rome IT": (41.90, 12.50, "Italy"), "Basildon": (51.57, 0.46, "UK"),
    "Hawthorne": (33.92, -118.35, "USA"), "Greenville": (34.85, -82.40, "USA"), "Clarksdale": (34.20, -90.57, "USA"),
    "Gary": (41.59, -87.35, "USA"), "Fort Worth": (32.75, -97.33, "USA"), "Norfolk": (36.85, -76.29, "USA"),
    "Shreveport": (32.52, -93.75, "USA"), "Clairefontaine": (48.62, 1.91, "France"),
}
CITY["Melbourne"] = (-37.81, 144.96, "Australia")

# Classical: list of (from_year, city); the last entry whose from_year <= piece year applies.
COMPOSER_TIMELINE = {
    "Claude Goudimel": [(0, "Metz")],
    "Claudio Monteverdi": [(0, "Cremona"), (1591, "Mantua"), (1613, "Venice")],
    "Jacopo Peri": [(0, "Florence")],
    "Jan Pieterszoon Sweelinck": [(0, "Amsterdam")],
    "Girolamo Frescobaldi": [(0, "Rome"), (1628, "Florence"), (1634, "Rome")],
    "Heinrich Schütz": [(0, "Dresden")],
    "Henry Purcell": [(0, "London")],
    "Arcangelo Corelli": [(0, "Rome")],
    "François Couperin": [(0, "Paris")],
    "Johann Sebastian Bach": [(0, "Weimar"), (1717, "Köthen"), (1723, "Leipzig")],
    "Georg Friedrich Händel": [(0, "London")],
    "Giovanni Battista Pergolesi": [(0, "Naples")],
    "Domenico Scarlatti": [(0, "Madrid")],
    "Wilhelm Friedemann Bach": [(0, "Dresden"), (1746, "Halle"), (1774, "Berlin")],
    "Carl Philipp Emanuel Bach": [(0, "Berlin"), (1768, "Hamburg")],
    "Johann Christian Bach": [(0, "London")],
    "Wolfgang Amadeus Mozart": [(0, "Salzburg"), (1766, "The Hague"), (1767, "Salzburg"), (1778, "Paris"), (1779, "Salzburg"), (1781, "Vienna")],
    "Franz Joseph Haydn": [(0, "Eszterháza"), (1791, "London"), (1793, "Vienna"), (1795, "London"), (1796, "Vienna")],
    "Ludwig van Beethoven": [(0, "Bonn"), (1793, "Vienna")],
    "Ignaz Pleyel": [(0, "Strasbourg")],
    "Leopold Koželuch": [(0, "Vienna")],
    "Maria Theresia von Paradis": [(0, "Vienna")],
    "Louise Reichardt": [(0, "Hamburg")],
    "Franz Schubert": [(0, "Vienna")],
    "Frédéric Chopin": [(0, "Warsaw"), (1831, "Paris")],
    "Felix Mendelssohn": [(0, "Berlin"), (1833, "Düsseldorf"), (1835, "Leipzig")],
    "Josephine Lang": [(0, "Munich"), (1842, "Tübingen")],
    "Fanny Hensel": [(0, "Berlin")],
    "Robert Schumann": [(0, "Leipzig"), (1845, "Dresden"), (1850, "Düsseldorf")],
    "Emilie Zumsteeg": [(0, "Stuttgart")],
    "Johanna Kinkel": [(0, "Bonn")],
    "Clara Schumann": [(0, "Leipzig"), (1845, "Dresden"), (1850, "Düsseldorf")],
    "Robert Franz": [(0, "Halle")],
    "Emilie Mayer": [(0, "Berlin")],
    "Johannes Brahms": [(0, "Hamburg"), (1863, "Vienna")],
    "Franz Liszt": [(0, "Weimar")],
    "Richard Wagner": [(0, "Lucerne")],
    "Edvard Grieg": [(0, "Oslo"), (1875, "Bergen")],
    "Pyotr Ilyich Tchaikovsky": [(0, "Moscow")],
    "Antonín Dvořák": [(0, "Prague")],
    "Pauline Viardot": [(0, "Paris")],
    "Marie Jaëll": [(0, "Paris")],
    "Ernest Chausson": [(0, "Paris")],
    "Maude Valérie White": [(0, "London")],
    "Hugo Wolf": [(0, "Vienna")],
    "Mathilde Kralik": [(0, "Vienna")],
    "Cécile Chaminade": [(0, "Paris")],
    "Augusta Mary Anne Holmès": [(0, "Paris")],
    "Mel Bonis": [(0, "Paris")],
    "Maurice Ravel": [(0, "Paris")],
    "Samuel Coleridge-Taylor": [(0, "London")],
    "Gustav Mahler": [(0, "Vienna")],
    "Claude Debussy": [(0, "Paris")],
    "Nikolai Medtner": [(0, "Moscow"), (1922, "Berlin"), (1925, "Paris"), (1936, "London")],
    "Béla Bartók": [(0, "Budapest")],
    "Harry Thacker Burleigh": [(0, "New York")],
    "Francis Poulenc": [(0, "Paris")],
    "Erwin Schulhoff": [(0, "Prague")],
    "Sergei Rachmaninoff": [(0, "Moscow"), (1918, "New York")],
}

# Jazz performers: base / recording city, with period overrides
JAZZ = {
    "Louis Armstrong": [(0, "Chicago"), (1929, "New York")], "Johnny Dodds": [(0, "Chicago")], "Kid Ory": [(0, "Chicago"), (1931, "Los Angeles")],
    "Bix Beiderbecke": [(0, "Chicago"), (1927, "New York")], "Sidney Bechet": [(0, "New York"), (1950, "Paris")],
    "Don Byas": [(0, "New York"), (1947, "Paris")], "Lester Young": [(0, "Kansas City"), (1937, "New York")],
    "Benny Carter": [(0, "New York"), (1943, "Los Angeles")], "Lionel Hampton": [(0, "Los Angeles"), (1937, "New York")],
    "Ben Webster": [(0, "New York"), (1952, "Los Angeles"), (1957, "New York"), (1965, "Copenhagen")],
    "Dexter Gordon": [(0, "Los Angeles"), (1944, "New York"), (1947, "Los Angeles"), (1960, "New York"), (1963, "Copenhagen"), (1976, "New York")],
    "Gerry Mulligan": [(0, "New York"), (1952, "Los Angeles"), (1955, "New York")], "Chet Baker": [(0, "Los Angeles"), (1960, "Paris"), (1975, "New York")],
    "Art Pepper": [(0, "Los Angeles")], "Paul Desmond": [(0, "San Francisco"), (1960, "New York")], "Warne Marsh": [(0, "New York"), (1966, "Los Angeles"), (1976, "New York")],
    "Harry Edison": [(0, "New York"), (1950, "Los Angeles")], "Don Ellis": [(0, "New York"), (1965, "Los Angeles")],
    "Steve Lacy": [(0, "New York"), (1970, "Paris")], "Kenny Wheeler": [(0, "London")], "Pat Martino": [(0, "Philadelphia")],
    "Von Freeman": [(0, "Chicago")], "Pat Metheny": [(0, "New York")],
}
JAZZ_DEFAULT = "New York"

# Rock / pop artists: home or base city (lowercase keys, 'the ' stripped)
POP = {
    "beatles": "Liverpool", "elvis presley": "Memphis", "rolling stones": "London", "bob dylan": "New York", "beach boys": "Los Angeles",
    "james brown": "Macon", "chuck berry": "St. Louis", "prince": "Minneapolis", "prince and the revolution": "Minneapolis",
    "jimi hendrix experience": "London", "jimi hendrix": "London", "simon and garfunkel": "New York", "simon & garfunkel": "New York", "paul simon": "New York",
    "nirvana": "Seattle", "johnny cash": "Memphis", "ray charles": "Los Angeles", "little richard": "Macon", "marvin gaye": "Detroit", "marvin gaye & tammy terrell": "Detroit",
    "u2": "Dublin", "led zeppelin": "London", "al green": "Memphis", "sam cooke": "Chicago", "everly brothers": "Nashville", "ramones": "New York",
    "bruce springsteen": "New York", "david bowie": "London", "byrds": "Los Angeles", "sly and the family stone": "San Francisco", "radiohead": "Oxford",
    "creedence clearwater revival": "San Francisco", "jerry lee lewis": "Memphis", "otis redding": "Macon", "stevie wonder": "Detroit", "clash": "London",
    "who": "London", "bob marley & the wailers": "Kingston", "buddy holly and the crickets": "Lubbock", "buddy holly": "Lubbock", "kinks": "London",
    "procol harum": "London", "sex pistols": "London", "ac/dc": "Sydney", "gene vincent": "Norfolk", "ronettes": "New York", "michael jackson": "Los Angeles",
    "verve": "Manchester", "new order": "Manchester", "fats domino": "New Orleans", "bo diddley": "Chicago", "queen": "London", "steppenwolf": "Los Angeles",
    "joni mitchell": "Los Angeles", "van morrison": "Belfast", "mamas & the papas": "Los Angeles", "patsy cline": "Nashville", "roy orbison": "Nashville",
    "crystals": "New York", "martha and the vandellas": "Detroit", "abba": "Stockholm", "aerosmith": "Boston", "penguins": "Los Angeles", "metallica": "San Francisco",
    "police": "London", "tracy chapman": "Boston", "buffalo springfield": "Los Angeles", "tom petty": "Los Angeles", "fleetwood mac": "Los Angeles",
    "jeff buckley": "New York", "donna summer": "Munich", "eagles": "Los Angeles", "animals": "Newcastle", "r. kelly": "Chicago", "bonnie raitt": "Los Angeles",
    "bobby fuller four": "Los Angeles", "flamingos": "Chicago", "jackson 5": "Detroit", "jacksons": "Los Angeles", "hank williams": "Nashville", "velvet underground": "New York",
    "john lennon": "New York", "wilson pickett": "Muscle Shoals", "five satins": "New York", "derek and the dominos": "Miami", "doors": "Los Angeles", "eminem": "Detroit",
    "r.e.m.": "Athens GA", "kingsmen": "Portland", "joy division": "Manchester", "iggy pop": "Detroit", "rod stewart": "London", "janis joplin": "San Francisco",
    "temptations": "Detroit", "sinead o'connor": "Dublin", "dr. dre": "Los Angeles", "impressions": "Chicago", "aretha franklin": "Muscle Shoals", "ike & tina turner": "Los Angeles",
    "bill haley and his comets": "Philadelphia", "b-52's": "Athens GA", "neil young": "Los Angeles", "big star": "Memphis", "big joe turner": "Kansas City", "isley brothers": "New York",
    "ben e. king": "New York", "pavement": "Stockton", "eddie cochran": "Los Angeles", "cream": "London", "guns n' roses": "Los Angeles", "eric clapton": "London",
    "miracles": "Detroit", "band": "New York", "drifters": "New York", "dionne warwick": "New York", "percy sledge": "Muscle Shoals", "shirelles": "New York",
    "elton john": "London", "righteous brothers": "Los Angeles",
    # Billboard extras (2+ songs)
    "dion": "New York", "chicago": "Chicago", "brenda lee": "Nashville", "cyndi lauper": "New York", "kenny rogers": "Los Angeles", "tina turner": "Los Angeles",
    "bob seger": "Detroit", "heart": "Seattle", "john denver": "Denver", "dr. hook": "New York", "cheap trick": "Rockford", "little river band": "Melbourne",
    "johnny tillotson": "Nashville", "pat benatar": "New York", "cliff richard": "London", "gladys knight & the pips": "Detroit", "billy idol": "London",
    "george harrison": "London", "billy joel": "New York", "glen campbell": "Los Angeles", "jackson browne": "Los Angeles", "pet shop boys": "London",
    "j. geils band": "Boston", "charlie rich": "Memphis", "genesis": "London", "5th dimension": "Los Angeles", "commodores": "Detroit", "lavern baker": "New York",
    "etta james": "Chicago", "anne murray": "Toronto", "rita coolidge": "Los Angeles", "anita baker": "Detroit", "milli vanilli": "Munich", "billy squier": "New York",
    "marty robbins": "Nashville", "wind & fire earth": "Los Angeles", "bread": "Los Angeles", "dinah washington": "New York", "stray cats": "New York",
    "nat king cole": "Los Angeles", "smokey robinson": "Detroit", "sonny & cher": "Los Angeles", "25 or 6 to 4": "Chicago", "steve miller band": "San Francisco",
    "jan & dean": "Los Angeles", "johnny horton": "Shreveport", "ub40": "Birmingham", "string-a-longs": "Lubbock", "paul mccartney": "London", "rick springfield": "Los Angeles",
    "roberta flack": "New York", "talking heads": "New York", "j. frank wilson & the cavaliers": "Dallas", "patrick hernandez": "Paris", "clarence carter": "Muscle Shoals",
    "contours": "Detroit", "wilson phillips": "Los Angeles", "stills & nash crosby": "Los Angeles", "dolly parton": "Nashville", "sting": "London", "trammps": "Philadelphia",
    "ray price": "Nashville", "jimmy reed": "Chicago", "duran duran": "Birmingham", "pink floyd": "London", "bill withers": "Los Angeles", "robert john": "New York",
    "gino vanelli": "Montreal", "gino vannelli": "Montreal", "gloria gaynor": "New York", "todd rundgren": "New York", "billy swan": "Nashville", "chubby checker": "Philadelphia",
    "youngbloods": "San Francisco", "waylon jennings": "Nashville", "madonna": "New York", "buck owens": "Los Angeles", "jesus jones": "London", "four tops": "Detroit",
    "blondie": "New York", "culture club": "London", "roberta flack and donny hathaway": "New York", "bing crosby": "Los Angeles", "boston": "Boston", "level 42": "London",
    "bette midler": "New York", "looking glass": "New York", "cornelius brothers & sister rose": "Miami", "peter gabriel": "London", "santo & johnny": "New York",
    "solomon burke": "Philadelphia", "jimmy clanton": "New Orleans", "andy gibb": "Miami", "alice cooper": "Detroit", "paul anka": "New York", "steve winwood": "Birmingham",
    "tom jones": "London", "isaac hayes": "Memphis", "stevie b": "Miami", "ten years after": "London", "brownsville station": "Detroit", "firehouse": "Richmond",
    "reo speedwagon": "Chicago", "robert palmer": "London", "hollies": "Manchester", "bobby womack": "Los Angeles", "juice newton": "Los Angeles", "roger miller": "Nashville",
    "supremes": "Detroit", "linda ronstadt": "Los Angeles", "robert cray band": "Portland", "rockwell": "Detroit", "freddy fender": "Houston", "bachman-turner overdrive": "Winnipeg",
    "marky mark & the funky bunch": "Boston", "sammy hagar": "San Francisco", "donna fargo": "Nashville", "flatt & scruggs": "Nashville", "neneh cherry": "London", "focus": "Amsterdam",
    "candi staton": "Muscle Shoals", "peggy lee": "Los Angeles", "snap": "Frankfurt", "pointer sisters": "Los Angeles", "staple singers": "Memphis", "corey hart": "Montreal",
    "cowsills": "New York", "rick james": "Detroit", "engelbert humperdinck": "London", "b.b. king": "Memphis", "tommy james": "New York", "roxy": "Los Angeles", "baltimora": "Milan",
    "canned heat": "Los Angeles", "yardbirds": "London", "quarterflash": "Portland", "nick gilder": "Los Angeles", "dean martin": "Los Angeles", "daryl hall & john oates": "Philadelphia",
    "eric carmen": "Cleveland", "queensryche": "Seattle", "foghat": "London", "leslie gore": "New York", "cher": "Los Angeles", "nitty gritty dirt band": "Los Angeles", "bananarama": "London",
    "depeche mode": "London", "wednesday": "Toronto", "r dean tayloy": "Detroit", "doobie brothers": "San Francisco",
}
CITY["Milan"] = (45.46, 9.19, "Italy")


# ---- verified overrides: data/locations_sources.csv is the authority (one row per musician, with a cited source).
# Rows with status confirmed/corrected supply the timeline; new cities carry Country|lat|lon.
def _parse_timeline(txt):
    out = []
    for part in str(txt).split(";"):
        k, _, city = part.strip().partition(":")
        out.append((0 if k.strip() == "start" else int(k.strip().replace("from", "")), city.strip()))
    return out

def _load_verified():
    path = f"{REPO}/data/locations_sources.csv"
    if not _os.path.exists(path):
        return {}
    V = pd.read_csv(path)
    for r in V[V.new_city_latlon.notna()].itertuples():
        country, lat, lon = str(r.new_city_latlon).split("|")
        for _, c in _parse_timeline(r.timeline):
            if c not in CITY:
                CITY[c] = (round(float(lat), 2), round(float(lon), 2), country)
    STATUS.update({(r.genre, r.name): r.status for r in V.itertuples()})
    return {(r.genre, r.name): _parse_timeline(r.timeline) for r in V.itertuples() if r.status in ("confirmed", "corrected")}

STATUS = {}
VERIFIED = _load_verified()
# confidence: classical high (medium if the source left it uncertain); jazz/pop medium when verified, low otherwise
def _conf(genre, name, base):
    st = STATUS.get((genre, name))
    return {"confirmed": base, "corrected": base}.get(st, "medium" if base == "high" else "low")


def _timeline(tl, year):
    city = tl[0][1]
    for y, c in tl:
        if year >= y:
            city = c
    return city


def locate(row):
    """row has composer, year, source, genre -> (city, country, lat, lon, confidence)"""
    src = row["source"]; name = row["composer"]; year = int(row["year"])
    if src in ("DCML", "WiR"):
        tl = VERIFIED.get(("classical", name)) or COMPOSER_TIMELINE.get(name)
        if tl is None:
            return (None, None, None, None, None)
        city, conf = _timeline(tl, year), _conf("classical", name, "high")
    elif src == "WeimarJazz":
        tl = VERIFIED.get(("jazz", name)) or JAZZ.get(name)
        city, conf = (_timeline(tl, year) if tl else JAZZ_DEFAULT), _conf("jazz", name, "medium")
    else:
        key = str(name).lower().strip()
        if key.startswith("the "):
            key = key[4:]
        tl = VERIFIED.get(("rock_pop", name))
        city = _timeline(tl, year) if tl else POP.get(key)
        if city is None:
            return (None, None, None, None, None)
        conf = _conf("rock_pop", name, "medium")
    lat, lon, country = CITY[city]
    return (city, country, lat, lon, conf)


if __name__ == "__main__":
    P = pd.read_csv(f"{REPO}/data/pieces.csv")
    loc = P.apply(locate, axis=1, result_type="expand")
    loc.columns = ["city", "country", "lat", "lon", "loc_confidence"]
    P = pd.concat([P, loc], axis=1)
    P.to_csv(f"{REPO}/data/pieces_located.csv", index=False)
    print(P.groupby("source").apply(lambda g: f"{g.city.notna().mean():.0%} of {len(g)} pieces located"))
    print(P[P.city.notna()].groupby("genre").city.value_counts().groupby(level=0).head(12))
