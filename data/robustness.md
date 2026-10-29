# Robustness checks

## 1. Notation effect: Rock Corpus (Roman numerals) vs Billboard (chord symbols), same recordings

12 songs: Be My Baby, Born To Be Wild, Eight Miles High, Help, Honky Tonk Women, I Saw Her Standing There, In The Midnight Hour, Maggie May, Sunshine Of Your Love, The Sounds Of Silence, Will You Love Me Tomorrow, With Or Without You.

| Metric | n | Rock Corpus | Billboard | Mean diff (BB − RC) | r | Wilcoxon p |
| --- | --- | --- | --- | --- | --- | --- |
| seventh_rate | 12 | 0.046 | 0.235 | +0.189 ± 0.254 | 0.55 | 0.010 |
| extended_rate | 12 | 0.000 | 0.067 | +0.067 ± 0.120 | nan | 0.125 |
| nondiatonic_rate | 12 | 0.139 | 0.134 | -0.006 ± 0.038 | 0.95 | 0.945 |
| chromatic_root_rate | 12 | 0.087 | 0.074 | -0.013 ± 0.026 | 0.98 | 0.125 |
| V_to_I_share | 12 | 0.360 | 0.388 | +0.029 ± 0.152 | 0.91 | 1.000 |
| IV_to_I_share | 12 | 0.413 | 0.329 | -0.085 ± 0.167 | 0.89 | 0.188 |
| bVII_to_I_share | 12 | 0.090 | 0.060 | -0.030 ± 0.061 | 0.96 | 0.250 |
| dom_resolution | 9 | 0.691 | 0.611 | -0.080 ± 0.168 | 0.85 | 0.125 |
| down5th_share | 12 | 0.285 | 0.253 | -0.032 ± 0.070 | 0.95 | 0.156 |
| step_share | 12 | 0.250 | 0.260 | +0.010 ± 0.049 | 0.97 | 1.000 |
| third_share | 12 | 0.187 | 0.189 | +0.002 ± 0.044 | 0.93 | 0.844 |
| chord_entropy | 12 | 2.230 | 2.378 | +0.147 ± 0.349 | 0.69 | 0.147 |
| vocab40 | 11 | 5.324 | 6.094 | +0.770 ± 1.537 | 0.62 | 0.094 |
| beats_per_chord | 12 | 6.476 | 5.774 | -0.702 ± 1.088 | 0.83 | 0.129 |

## 2. Mixed-effects models (classical, composer random intercept, corpus fixed effect)

metric ~ year (per century, centred 1750) + hinge(year − 1850) + corpus, random intercept per composer. Hinge = change in slope after 1850.

| Metric | slope / century | 95% CI | hinge after 1850 | 95% CI | composer SD | residual SD | n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| seventh_rate | +0.123 | [+0.091, +0.155] | +0.145 | [+0.032, +0.258] | 0.087 | 0.090 | 2058 |
| extended_rate | +0.003 | [-0.019, +0.026] | +0.200 | [+0.126, +0.275] | 0.080 | 0.042 | 2058 |
| nondiatonic_rate | +0.030 | [-0.000, +0.061] | +0.140 | [+0.024, +0.255] | 0.076 | 0.108 | 2058 |
| chromatic_root_rate | +0.007 | [-0.009, +0.023] | +0.131 | [+0.075, +0.187] | 0.047 | 0.039 | 2058 |
| V_to_I_share | +0.030 | [-0.008, +0.069] | -0.311 | [-0.456, -0.166] | 0.091 | 0.160 | 2058 |
| dom_resolution | -0.019 | [-0.055, +0.017] | -0.222 | [-0.360, -0.083] | 0.082 | 0.163 | 2051 |
| down5th_share | -0.000 | [-0.022, +0.021] | -0.149 | [-0.229, -0.069] | 0.054 | 0.079 | 2058 |
| step_share | -0.028 | [-0.047, -0.008] | +0.140 | [+0.067, +0.213] | 0.045 | 0.089 | 2058 |
| chord_entropy | +0.068 | [-0.081, +0.218] | +0.932 | [+0.389, +1.475] | 0.407 | 0.445 | 2058 |
| vocab40 | +0.541 | [-0.420, +1.503] | +7.182 | [+3.679, +10.686] | 2.630 | 2.719 | 1830 |

### All genres: metric ~ year × genre, composer/artist random intercept (year per century, centred 1900)

| Metric | classical slope | jazz slope | rock/pop slope | genre SD (composer) |
| --- | --- | --- | --- | --- |
| seventh_rate | +0.146 | +0.121 | +0.162 | 0.197 |
| nondiatonic_rate | +0.056 | +0.017 | +0.040 | 0.105 |
| V_to_I_share | -0.023 | -0.225 | -0.327 | 0.205 |
| dom_resolution | -0.067 | +0.055 | -0.666 | 0.213 |
| down5th_share | -0.026 | -0.137 | -0.437 | 0.108 |
| step_share | -0.003 | +0.104 | +0.371 | 0.119 |

## 3. Change points (classical, piece level, least-squares hinge regression)

| Metric | n | best single break | 95% bootstrap CI | ΔBIC 1-break vs linear | best two breaks | ΔBIC 2-break vs 1-break |
| --- | --- | --- | --- | --- | --- | --- |
| seventh_rate | 2058 | 1690 | [1690, 1890] | +23.5 | 1720, 1740 | +122.6 |
| nondiatonic_rate | 2058 | 1810 | [1780, 1880] | +108.6 | 1600, 1690 | +82.6 |
| chromatic_root_rate | 2058 | 1880 | [1730, 1900] | +138.7 | 1710, 1890 | +45.3 |
| V_to_I_share | 2058 | 1805 | [1790, 1810] | +260.5 | 1630, 1800 | +2.4 |
| dom_resolution | 2051 | 1820 | [1810, 1860] | +31.7 | 1740, 1810 | +21.5 |
| down5th_share | 2058 | 1770 | [1750, 1810] | +191.7 | 1700, 1810 | +15.5 |
| chord_entropy | 2058 | 1880 | [1600, 1880] | +72.1 | 1600, 1820 | +90.0 |

## 4. No-chord handling: default (transitions bridge silent stretches) vs strict (they do not)

| Era | metric | default | strict | difference |
| --- | --- | --- | --- | --- |
| Renaissance (<1600) | V_to_I_share | 0.504 | 0.504 | +0.000 |
| Early Baroque (1600-99) | V_to_I_share | 0.541 | 0.541 | +0.000 |
| Late Baroque (1700-49) | V_to_I_share | 0.630 | 0.630 | +0.000 |
| Classical (1750-99) | V_to_I_share | 0.647 | 0.647 | -0.000 |
| Early Romantic (1800-49) | V_to_I_share | 0.641 | 0.641 | +0.000 |
| Late Romantic (1850-99) | V_to_I_share | 0.524 | 0.524 | +0.000 |
| Early 20th c. (1900-49) | V_to_I_share | 0.426 | 0.426 | +0.000 |
| Jazz: Swing era (<1945) | V_to_I_share | 0.674 | 0.674 | -0.001 |
| Jazz: Bebop/Hard bop (1945-59) | V_to_I_share | 0.645 | 0.645 | -0.000 |
| Jazz: Modal/Post-bop (1960-74) | V_to_I_share | 0.503 | 0.504 | +0.001 |
| Jazz: 1975+ | V_to_I_share | 0.543 | 0.544 | +0.000 |
| Jazz: 1975+ | beats_per_chord | 5.637 | 5.645 | +0.008 |
| Rock/Pop 1950-64 | V_to_I_share | 0.472 | 0.467 | -0.005 |
| Rock/Pop 1950-64 | IV_to_I_share | 0.338 | 0.343 | +0.005 |
| Rock/Pop 1950-64 | beats_per_chord | 7.074 | 7.054 | -0.020 |
| Rock/Pop 1965-74 | V_to_I_share | 0.358 | 0.356 | -0.002 |
| Rock/Pop 1965-74 | beats_per_chord | 5.671 | 5.704 | +0.033 |
| Rock/Pop 1975-84 | V_to_I_share | 0.339 | 0.338 | -0.000 |
| Rock/Pop 1975-84 | beats_per_chord | 4.684 | 4.679 | -0.005 |
| Rock/Pop 1985+ | V_to_I_share | 0.343 | 0.341 | -0.002 |
| Rock/Pop 1985+ | dom_resolution | 0.453 | 0.447 | -0.006 |
| Rock/Pop 1985+ | beats_per_chord | 4.432 | 4.423 | -0.010 |

Largest change in any share across all eras: 0.006.


## 5. Cluster sensitivity (adjusted Rand index vs the published 6-cluster Ward solution)

| Variant | ARI |
| --- | --- |
| drop seventh_rate | 0.70 |
| drop extended_rate | 0.93 |
| drop nondiatonic_rate | 0.78 |
| drop chromatic_root_rate | 0.82 |
| drop V_to_I_share | 0.91 |
| drop IV_to_I_share | 0.91 |
| drop bVII_to_I_share | 0.72 |
| drop dom_resolution | 0.86 |
| drop down5th_share | 0.87 |
| drop step_share | 0.90 |
| drop third_share | 0.98 |
| drop chord_entropy | 0.73 |
| drop tonic_share | 0.89 |
| drop minor_quality_share | 0.84 |
| no seventh/extension features | 0.63 |
| no chromaticism features | 0.81 |
| no cadence features | 0.77 |
| no root-motion features | 0.72 |
| no distribution features | 0.63 |
| k-means (k=6) | 0.71 |
| average linkage (k=6) | 0.09 |
| complete linkage (k=6) | 0.25 |
| strict no-chord profiles | 0.87 |
