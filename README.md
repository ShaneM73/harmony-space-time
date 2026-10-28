# Harmony in Space and Time

How chords evolved from Goudimel (1565) to bebop and 1980s pop, and whether harmony is organised by time, by place, or both.
3,539 expert-annotated pieces from five open corpora are reduced to one chord-feature table, placed in a 3D space-time frame
(longitude × latitude × year), clustered into scenes, and tested with Mantel statistics.

**Live app:** `docs/index.html` (served with GitHub Pages) — an interactive 3D frame of all located pieces plus every finding as a chart.

## Findings in one paragraph

Seventh chords grow from 2% of chords in the Renaissance to 54% in early-20th-century classical music and 91% in bebop, while rock stays near 25%.
The authentic cadence is a plateau: V prepares 62–67% of tonic arrivals from 1700 to 1850, then 43% after 1900; rock repeats the decline in thirty years
(47% → 34%) as IV→I and bVII→I take over. Chromaticism is flat (20–24%) from Corelli to Schubert, then 29% after 1850 and 40% after 1900.
Vocabulary is constant (about 14 chord types per 40 chords) from 1600 to 1900 while transition entropy rises by a full bit. Classical and jazz run on
descending fifths; 20th-century classical music and post-1965 rock both switch to steps and thirds. In the space-time frame, harmony tracks time in
every genre (Mantel r = 0.29 classical, 0.22 jazz, 0.17 rock, all p < 0.02) and tracks geography only weakly in rock (r = 0.15, p ≈ 0.06), not at all in
classical music or jazz once time is controlled.

## Repository layout

| Path | Contents |
| --- | --- |
| `docs/` | The web app (self-contained; `vendor/` holds three.js r128 and d3 v7). Enable GitHub Pages on `docs/` to publish it. |
| `src/app_template.html`, `src/build_site.py` | Template and build script for the app (inlines `data/harmony_data.json`). |
| `analysis/` | The pipeline: corpus loaders, feature extraction, metrics, location assignment, space-time clustering, Mantel tests. |
| `data/` | Every output table: per-piece metrics (`pieces.csv`, `pieces_located.csv`), era/period/composer summaries, scenes, composer clusters, Mantel results, and the bundled `harmony_data.json` the app reads. |

## Reproduce

```bash
pip install music21 pandas numpy scipy scikit-learn
mkdir corpora && cd corpora
git clone --depth 1 https://github.com/MarkGotham/When-in-Rome.git wir
git clone --depth 1 https://github.com/DCMLab/distant_listening_corpus.git dlc && (cd dlc && git submodule update --init --depth 1)
git clone --depth 1 https://github.com/smashub/choco.git choco      # ~2 GB, carries Billboard, Rock Corpus and Weimar
cd ../analysis
python load_dcml.py && python load_wir.py && python load_modern.py   # unified chord-event tables (load_wir takes ~8 min)
python analyze.py && python export_dash.py                            # metrics by era, period, composer
python locations.py && python space_time.py                           # locations, scenes, composer clusters, Mantel tests
cd .. && python src/build_site.py                                     # rebuilds docs/index.html
```

`HARMONY_ROOT` can point the scripts at another repository root.

## Method

1. **Features.** Every chord label (Roman numeral or chord symbol) becomes: root as scale degree above the local tonic; quality; extension (triad, seventh, ninth and above);
   a non-diatonic flag (root outside the key, or quality not supplied by the key); applied-chord flag and inversion where annotated; duration in beats. Consecutive identical chords are merged.
2. **Metrics** are computed per piece and averaged over pieces; 95% intervals are 400 bootstrap resamples of pieces. Vocabulary is rarefied to 40 chords; transition entropy is H(next | current) pooled per era.
3. **Locations** are assigned from biography (`analysis/locations.py`): residence timelines for the 59 classical composers (high confidence), recording base for jazz performers (medium), home city for pop artists (medium/low).
   100% of classical, jazz and Rock Corpus pieces and 75% of Billboard singles are located.
4. **Space-time.** Points at (longitude, latitude, year) with one century scaled to 1,000 km; Ward clustering into scenes; composers clustered on z-scored mean profiles; Mantel and partial Mantel tests with 5,000 permutations.

## Data sources

- [DCML Distant Listening Corpus](https://github.com/DCMLab/distant_listening_corpus) (CC BY-NC-SA 4.0) and [When in Rome](https://github.com/MarkGotham/When-in-Rome) (CC BY-SA 4.0): expert Roman-numeral analyses, 1565–1931.
- [Rock Corpus RS200](https://rockcorpus.midside.com/) (de Clercq & Temperley), [McGill Billboard](https://ddmal.music.mcgill.ca/research/The_McGill_Billboard_Project_(Chord_Analysis_Dataset)/) (Burgoyne et al.), [Weimar Jazz Database](https://jazzomat.hfm-weimar.de/dbformat/dboverview.html) (Pfleiderer et al.), all via [ChoCo](https://github.com/smashub/choco).

## Caveats

Classical and Rock Corpus labels are expert Roman numerals; Billboard and Weimar are chord symbols, so cross-genre levels are partly notation and within-genre trends are the safer finding.
Sampling is uneven (1700–49 is largely Bach chorales; 1900–49 is small). Locations are residences, not composition sites. See the app's Method section and the accompanying report for the full list.

## Related work

White 2013/2017 · Weiß, Mauch, Dixon & Müller 2018 · Moss, Neuwirth & Rohrmeier 2022 · Harasim et al. 2021 · González-Espinoza & Plotkin 2023 · Park et al. 2020 ·
Broze & Shanahan 2013 · Mauch et al. 2015 · Gauvin 2015 · de Clercq & Temperley 2011 · Schich et al. 2014 · Georges & Nguyen 2019 · Gleiser & Danon 2003.

## Licence

Code: MIT. Derived data tables: under the licences of the source corpora (see `LICENSE`).
