# Literature review: corpus studies of harmonic change across classical, jazz and popular music

Prepared 2026-10-29 for the related-work and theory sections of the *Humanities and Social Sciences Communications* paper. Every entry below was confirmed on a page fetched during this session (publisher page, journal site, arXiv, PMC/DOAJ record, repository record, or a review published in a journal). Bibliographic fields that the fetched page did not display are marked "(not shown on page)". Works that could not be confirmed are listed at the end. Search budget used: 110 of 150 WebSearch calls.

Tags: [classical-corpus] [jazz-corpus] [pop-corpus] [cross-genre] [theory] [geography] [dataset] [method]

---

## Part 1. Annotated bibliography

### A. Seed list (verified)

### Mauch, M., MacCallum, R. M., Levy, M., & Leroi, A. M. (2015). The evolution of popular music: USA 1960–2010. *Royal Society Open Science*, 2(5), 150081. https://doi.org/10.1098/rsos.150081
[pop-corpus] Corpus: 17,094 Billboard Hot 100 recordings (1960–2010, ~86% of the chart), 30-s audio segments. Method: 12 chroma-derived harmonic and 14 timbre descriptors quantised into "words", LDA with 16 topics (8 harmonic, 8 timbral), 13 styles, Foote-novelty change-point detection. Findings: three "revolutions" c. 1964, 1983 and 1991 (the last the largest); diversity dipped to a minimum c. 1986 then recovered; dominant-seventh topic (jazz/blues) fell ~75% 1960–2009; minor-seventh topic (funk/soul/disco) more than doubled 1967–77; "no identifiable chord" topic peaked 1993 with hip-hop. Relation: the closest precedent for our pop trajectory, but audio-based and chord-type only; our symbolic Roman-numeral measures (cadence shares, root motion, entropy) extend it, and its 1991 rap break is a prediction we can test with McGill Billboard (ends 1991) and the Rock Corpus.

### Serrà, J., Corral, Á., Boguñá, M., Haro, M., & Arcos, J. L. (2012). Measuring the evolution of contemporary western popular music. *Scientific Reports*, 2, 521. https://doi.org/10.1038/srep00521
[pop-corpus] Corpus: Million Song Dataset audio descriptors, 1955–2010 (size not stated on the arXiv abstract page fetched). Method: pitch, timbre and loudness codewords; network/distribution statistics over time. Findings: most descriptors stable for 50+ years ("conventionalism"); pitch transitions became more restricted, timbral palette more homogeneous, loudness rose. Relation: the "harmonic restriction/homogenisation" claim is one of two contested pop narratives (see Mauch 2015, Parmer & Ahn 2019); our chord-entropy series speaks to it directly.

### Weiß, C., Mauch, M., Dixon, S., & Müller, M. (2018, online first; print 2019). Investigating style evolution of Western classical music: A computational approach. *Musicae Scientiae*, 1–22 (volume/issue not shown on page). https://doi.org/10.1177/1029864918757595
[classical-corpus] Corpus: 2,000 audio recordings (1,000 piano, 1,000 orchestral) by 70 composers, 1660–1975. Method: Chordino chord estimates; 65 tonal features (interval categories, tonal complexity, 55 chord-root transition features) projected onto composer lifetimes as "evolution curves"; PCA and k-means over years, pieces, composers. Findings: plagal/authentic ratio stayed <0.5 (0.3–0.5), rose c. 1750, dipped 1820–50, approached 0.5 in the 20th c.; tonal complexity rises overall, dips after 1750, rises strongly in 20th c.; stable period boundaries c. 1750, 1820, 1900; composer clustering mostly follows lifetimes. Relation: the main audio-side precedent for Q1 (long-run classical change) and Q3 (composer clustering); our symbolic annotations remove chord-estimation noise and add cadence/root-motion measures they could not compute.

### Moss, F. C., Neuwirth, M., Harasim, D., & Rohrmeier, M. (2019). Statistical characteristics of tonal harmony: A corpus study of Beethoven's string quartets. *PLOS ONE*, 14(6), e0217242. https://doi.org/10.1371/journal.pone.0217242
[classical-corpus] Corpus: ABC (all Beethoven quartets, ~28k chord labels). Method: resampling statistics on chord unigrams/bigrams. Findings: chord rank-frequency is power-law-like; transitions are asymmetric (directed in time); predictability depends on chord features; chord-level and key-level organisation differ. Relation: establishes the chord-token statistics (Zipf, asymmetry) that our entropy and root-motion classes assume; single composer only, so we extend across 450 years and three repertoires.

### Harasim, D., Moss, F. C., Ramirez, M., & Rohrmeier, M. (2021). Exploring the foundations of tonality: Statistical cognitive modeling of modes in the history of Western classical music. *Humanities and Social Sciences Communications*, 8, 1–11. https://doi.org/10.1057/s41599-020-00678-6
[classical-corpus] Corpus: ~13,000 MIDI pieces across five epochs. Method: geometric clustering of pitch-class distributions in non-Euclidean space plus a Bayesian (Dirichlet) mode model. Findings: Renaissance best described by four modes, Baroque/Classical by two (major/minor), no clear mode separation in the 19th c. Relation: same journal, same long-run framing; it works at the pitch-class level, we work at the chord level, so we test whether the "dissolution of mode" in the 19th c. has a chord-syntax counterpart (non-diatonic rate, cadence shares).

### Moss, F. C., Neuwirth, M., & Rohrmeier, M. (2022). The line of fifths and the co-evolution of tonal pitch-classes. *Journal of Mathematics and Music* (volume/pages not shown on page). https://doi.org/10.1080/17459737.2022.2044927
[classical-corpus] Corpus: pitch-class counts for >2,000 pieces by 75 composers, c. 1360–1940 (size from the DCML project page). Method: dimensionality reduction on pitch-class co-occurrence; "fifths range" over time. Findings: the line of fifths emerges unsupervised; the fifths range widens over history; pitch-class usage separates periods. Relation: provides the tonal-space backdrop; our non-diatonic chord rate is the chord-level analogue of the widening fifths range.

### Neuwirth, M., Harasim, D., Moss, F. C., & Rohrmeier, M. (2018). The Annotated Beethoven Corpus (ABC): A dataset of harmonic analyses of all Beethoven string quartets. *Frontiers in Digital Humanities*, 5, 16. https://doi.org/10.3389/fdigh.2018.00016
[dataset] 70 movements, 15,806 bars, 240,462 notes, 27,962 chord labels (1,753 unique). Defines the DCML Roman-numeral standard (regular-expression grammar: key, degree, figured bass, pedal, suspensions, added notes, applied roots, phrase ends; "@none" for unanalysable spans). Relation: this is the annotation standard behind our DCML Distant Listening data; cite for label semantics and for how seventh/extension and applied chords are encoded.

### Hentschel, J., Neuwirth, M., & Rohrmeier, M. (2021). The Annotated Mozart Sonatas: Score, harmony, and cadence. *Transactions of the International Society for Music Information Retrieval*, 4(1), 67–80. https://doi.org/10.5334/tismir.63
[dataset] All Mozart piano sonatas with harmony, phrase and cadence labels in the DCML standard; "data triangulation" review procedure; preliminary experiments on terminal cadence harmonies and harmonic density. Relation: supplies the cadence-label conventions we use for V→I vs IV→I shares; the inter-annotator procedure is what we should cite when defending annotation reliability.

### Hentschel, J., Rammos, Y., Moss, F. C., Neuwirth, M., & Rohrmeier, M. A. (2023). An annotated corpus of tonal piano music from the long 19th century. *Empirical Musicology Review*, 18(1), 84–95. https://doi.org/10.18061/emr.v18i1.8903
[dataset] 264 annotated piano pieces by nine composers (Beethoven to Medtner), DCML standard, GitHub-based review to consensus; descriptive statistics on pitch-class content, phrase length, modulation and cadence types. Relation: the published data paper for the 19th-century slice of the Distant Listening Corpus; cite together with the ABC and Mozart papers as the DCML corpus trilogy. (The SNSF project page "Distant Listening: The Development of Harmony over Three Centuries (1700–2000)", EPFL DCML, 2019–2023, was fetched and lists these outputs; no single "Distant Listening Corpus" data paper could be found.)

### Gotham, M., Micchi, G., Nápoles López, N., & Sailor, M. (2023). When in Rome: A meta-corpus of functional harmony. *Transactions of the International Society for Music Information Retrieval*, 6(1), 150–166. https://doi.org/10.5334/tismir.165
[dataset] >2,000 human Roman-numeral analyses of ~1,500 works, unified format, conversion and feature-extraction code. Relation: our second classical source; note that it mixes analytical traditions and annotators, which we must treat as a covariate (see Gotham 2023, Chromatic chords).

### de Berardinis, J., Meroño-Peñuela, A., Poltronieri, A., & Presutti, V. (2023). ChoCo: A chord corpus and a data transformation workflow for musical harmony knowledge graphs. *Scientific Data*, 10, 1–25. https://doi.org/10.1038/s41597-023-02410-w
[dataset] Integrates 18 chord datasets (Harte, lead-sheet, Roman numeral, ABC) into JAMS and a 30M-triple knowledge graph. Relation: the only prior attempt to put classical, jazz and pop chord annotations into one frame; it is an infrastructure paper with no diachronic analysis, which is exactly the gap we fill.

### Pfleiderer, M., Frieler, K., Abeßer, J., Zaddach, W.-G., & Burkhart, B. (Eds.) (2017). *Inside the Jazzomat: New perspectives for jazz research*. Mainz: Schott Campus. ISBN 978-3-95983-124-6. urn:nbn:de:101:1-201711151872
[dataset] Edited volume presenting the Jazzomat project, MeloSpyGUI and the Weimar Jazz Database. Relation: canonical citation for the WJD. For the database's size see Frieler (2019) below: 456 solos, 78 performers, 1925–2009, ~200k tone events, with style labels (postbop 147, hardbop 76, swing 66, bebop 56, cool 54, traditional 32, free 5).

### Frieler, K. (2019). Constructing jazz lines: Taxonomy, vocabulary, grammar. In M. Pfleiderer & W.-G. Zaddach (Eds.), *Jazzforschung heute* (pp. 104–131). Berlin: Edition EMVAS. Volume DOI 10.25643/bauhaus-universitaet.3868
[jazz-corpus] Corpus: the 456 WJD solos. Method: "Weimar Bebop Alphabet" parsing of lines into atoms; Markov analysis. Findings: atom sequences near zero-order; arpeggios 62% triads, 33% four-note (minor-seventh most common). Relation: documents WJD composition and shows it is a solo-melody corpus whose chord track is the lead sheet, a limitation we must state explicitly.

### Burgoyne, J. A., Wild, J., & Fujinaga, I. (2011). An expert ground-truth set for audio chord recognition and music analysis. *Proceedings of ISMIR 2011*, 633–638. (no DOI on page)
[dataset] >1,000 Billboard Hot 100 songs 1958–1991, stratified by era × chart-rank quintile; Harte syntax with inversions/extensions; 638 distinct chords in 99 classes; major chords >50% of tokens; mean 11.8 unique chords per song; late-1970s songs most varied. Relation: the McGill Billboard sampling design gives us a defensible chart-weighted pop sample; the 1970s variety peak is a finding we can replicate with entropy.

### de Clercq, T., & Temperley, D. (2011). A corpus analysis of rock harmony. *Popular Music*, 30(1), 47–70. https://doi.org/10.1017/S026114301000067X
[pop-corpus] Corpus: 100 songs (20 per decade 1950s–90s from Rolling Stone's 500). Method: dual Roman-numeral analysis (>90% agreement), recursive encoding. Findings: IV is the most common chord after I and the most common pre-tonic chord; root motion and co-occurrence patterns, with changes by decade. Relation: direct precedent for our IV→I vs V→I cadence-share measure in rock; we extend the time span and add classical/jazz comparators.

### Temperley, D., & de Clercq, T. (2013). Statistical analysis of harmony and melody in rock music. *Journal of New Music Research*, 42(3), 187–204. https://doi.org/10.1080/09298215.2013.788039
[pop-corpus] Corpus: RS200 (200 songs, 20 per decade 1950s–90s + top-ranked remainder; 93.3% harmonic agreement). Findings: root frequency order I > IV > V > bVII > VI; b7 commoner than 7 in melody; two pitch-organisation clusters resembling major and minor. Relation: establishes bVII as the fourth most common root in rock, the basis of our bVII→I cadence class; the paper explicitly does not test decade trends, which we do.

### Temperley, D. (2018). *The Musical Language of Rock*. New York: Oxford University Press. (verified via Heetderks, D., 2023, review in *Music Theory Online* 29(1))
[theory] Book-length synthesis of RS200 findings. The review notes 43% of RS200 songs are from the 1960s, a chronological imbalance we must address when the Rock Corpus is used for trend estimation. Relation: theory source for rock harmonic norms (IV-dominance, supermode, bVII).

### Broze, Y., & Shanahan, D. (2013). Diachronic changes in jazz harmony: A cognitive perspective. *Music Perception*, 31(1), 32–45. (DOI not shown on pages fetched)
[jazz-corpus] Corpus: 1,086 jazz compositions (lead sheets). Method: chord-quality distributions and root-motion transitions by decade. Findings: chord-quality distributions change slowly and incrementally; typical tonal transitions decline 1920s–1960s; ascending-fourth root motion drops suddenly in the 1950s; transitions change faster than frequencies. Relation: the single most important jazz precedent; our root-motion classes and seventh/extension rates on the WJD lead sheets replicate and extend it to solos (1925–2000), and its "transitions change faster than frequencies" claim is a hypothesis we can test across all three repertoires.

### Léveillé Gauvin, H. (2015). "The times they were a-changin'": A database-driven approach to the evolution of musical syntax in popular music from the 1960s. *Empirical Musicology Review*, 10(3), 215–238. https://doi.org/10.18061/emr.v10i3.4467
[pop-corpus] Corpus: McGill Billboard (>700 songs at the time). Findings: no change in multi-tonic songs across the 1960s; flat-side harmonies (bIII, bVI, bVII) increased significantly in the second half of the decade. Relation: replicable with our non-diatonic rate; shows the McGill corpus has already been used diachronically for one decade.

### White, C. W. (2014; page shows 2012 preprint year). Changing styles, changing corpora, changing tonal models. *Music Perception* (volume/pages not shown on page).
[classical-corpus] Corpus: 19 composer sub-corpora, three-chord progressions tallied. Method: cluster analysis; inter-corpus cross-entropy; corpus-specific key-finding on the Eroica opening. Findings: clustering matches stylistic intuition; cross-entropy between corpora correlates with the years separating them; chord norms are period-specific. Relation: the closest existing version of our Q3 (composers clustering by harmonic profile) and of the time-distance logic behind our space-time Mantel design; limited to classical.

### Albrecht, J. D., & Huron, D. (2014; page shows 2012). A statistical approach to tracing the historical development of major and minor pitch distributions, 1400–1750. *Music Perception* (volume/pages not shown on page).
[classical-corpus] Corpus: 455 works by 259 composers, 1400–1750. Method: backward-stepping cluster analysis of scale-degree distributions with a generalised key-finding method. Finding: major/minor preceded by a multi-mode system. Relation: with Harasim 2021, frames the pre-1750 end of our window; our earliest Roman-numeral data (1565) sit inside the modal-to-tonal transition they describe.

### Horn, K., & Huron, D. (2015). On the changing use of the major and minor modes 1750–1900. *Music Theory Online*, 21(1). (DOI not shown on page)
[classical-corpus] Corpus: 750 IMSLP works (50 per decade, 330 composers). Method: UPGMA clustering on mode, dynamics, tempo, articulation. Findings: 71% major, 25% minor overall; minor-mode use rises considerably over the period; "light/effervescent" cluster falls from 38% to near zero, "tender/lyrical" rises 22%→44%. Relation: mode drift is a confound for chord-level trends (minor keys carry different cadence and non-diatonic rates), so we should stratify or control by mode.

### Nakamura, E., & Kaneko, K. (2019). Statistical evolutionary laws in music styles. *Scientific Reports*, 9. https://doi.org/10.1038/s41598-019-52380-6 (arXiv:1809.05832)
[classical-corpus] [theory] Corpus: 9,727 MIDI pieces by 76 classical composers plus 761 enka songs. Method: frequencies of rare events (tritones, non-diatonic motions); "statistical creator–evaluator" model with novelty/typicality selection. Findings: mean and SD of rare-event frequency rise steadily 1500–1900 with a near-constant ratio slightly below 1; model fit RMSE 4.5e-3 / 1.5e-2 vs baseline. Relation: predicts that our non-diatonic chord rate should rise with increasing between-composer dispersion; gives a cultural-evolution mechanism to cite.

### Park, D., Bae, A., Schich, M., & Park, J. (2015). Topology and evolution of the network of western classical music composers. *EPJ Data Science*, 4, 2. https://doi.org/10.1140/epjds/s13688-015-0039-z
[geography] Data: composer co-occurrence network from CD recordings. Findings: superlinear preferential attachment; growing concentration on highly recorded composers. Relation: composer-network precedent; does not use musical content or location, so our composer-by-harmony clustering is complementary.

### Youngblood, M. (2019). Cultural transmission modes of music sampling traditions remain stable despite delocalization in the digital age. *PLOS ONE*, 14(2), e0211860. https://doi.org/10.1371/journal.pone.0211860
[geography] Method: network-based diffusion analysis of drum-break sampling through collaboration networks. Findings: strong evidence of transmission via collaboration; network no longer biased by geographic proximity after 2000. Relation: directly relevant to Q4: geography structured musical transmission before 2000 and weakened afterwards, which predicts a time-dependent geographic signal in our Mantel tests.

### Percino, G., Klimek, P., & Thurner, S. (2014). Instrumentational complexity of music genres and why simplicity sells. *PLOS ONE*, 9(12), e115255. https://doi.org/10.1371/journal.pone.0115255
[pop-corpus] Data: Discogs instrumentation by style over 50 years. Findings: style complexity falls as sales rise; complexity grows with number of contributing artists. Relation: "simplicity sells" is a candidate explanation for declining harmonic complexity in charts; not a geography paper despite the seed-list grouping.

### Savage, P. E. (2019). Cultural evolution of music. *Palgrave Communications* (now *Humanities and Social Sciences Communications*), 5, 1–12. https://doi.org/10.1057/s41599-019-0221-1
[theory] Review arguing that cultural-evolution theory is a useful framework for musical change at all scales; addresses objections about agency and reductionism. Relation: the theoretical umbrella for framing our trajectories as cultural evolution, in the same journal.

### Kantarelis, S., Liolitsas, I., Thomas, K., Lyberatos, V., Dervakos, E., & Stamou, G. (2024). Chordonomicon: A dataset of 666,000 songs and their chord progressions. arXiv:2410.22046 (v3, Dec 2024).
[dataset] >666k user-generated chord progressions with structural-part, genre and release-date metadata; next-chord-prediction baselines. Relation: a much larger but crowd-sourced, un-reviewed pop resource; cite as the scale benchmark and as future replication material for our pop trends.

### Meeùs, N. (2000). Toward a post-Schoenbergian grammar of tonal and pre-tonal harmonic progressions. *Music Theory Online*, 6(1).
[theory] Reduces Schoenberg's root-progression classes to "dominant" (5th down, 3rd down, 2nd up) vs "subdominant" (5th up, 3rd up, 2nd down) vectors. Illustrative counts: Bach chorale 92% dominant progressions; Lassus 64% dominant / 36% subdominant. Relation: the theoretical basis for our root-motion classes; it predicts tonal music is dominant-vector heavy and pre-tonal (and, by extension, rock) more balanced, which de Clercq's country/rock comparison (below) echoes.

### Tymoczko, D. (2011). *A Geometry of Music: Harmony and Counterpoint in the Extended Common Practice*. New York: Oxford University Press. ISBN 978-0-19-533667-2.
[theory] Argues for an "extended common practice" from the late Middle Ages to jazz (Bill Evans, Miles Davis), with five features underpinning tonality. Relation: the strongest theoretical argument that classical, jazz and pop share one harmonic system; our Q2 (shared trajectory?) is an empirical test of this claim.

### Biamonte, N. (2010). Triadic modal and pentatonic patterns in rock music. *Music Theory Spectrum*, 32(2), 95–110. https://doi.org/10.1525/mts.2010.32.2.95
[theory] Several hundred classic-rock songs (late 1960s–1990s); double-plagal (I–bVII–IV–I) and Aeolian (bVI–bVII–I) progressions as substitutes for IV–V–I; triad-doubled pentatonic systems. Relation: theory for bVII→I as a cadence class.

### Doll, C. (2017). *Hearing Harmony: Toward a Tonal Theory for the Rock Era*. Ann Arbor: University of Michigan Press. (verified via de Clercq, T., 2018, review in *Music Theory Online* 24(1))
[theory] Function tied to scale-degree content; "pre-tonic" and Greek-letter functional labels; catalogue of root-succession schemas regardless of chord quality. Relation: supports treating rock cadences by root succession (our V→I / IV→I / bVII→I shares) rather than by classical function.

### Nobile, D. (2020). *Form as Harmony in Rock Music*. New York: Oxford University Press. (verified via Barna, A., 2022, review in *Music Theory Online* 28(1))
[theory] Functional circuit T–PD–D–T spanning formal units; cadence only at circuit completion; repertoire 1960–1991. Relation: cautions that chord-level cadence counts in rock may not align with form-level closure; we should present cadence shares as surface statistics, not formal cadences.

### Moore, A. F. (1992). Patterns of harmony. *Popular Music* (Cambridge University Press; © 1992; volume/pages/author field not displayed on the publisher page fetched).
[theory] Opens by rejecting the Adornian view that popular harmony is a static set of formulae and argues harmony distinguishes rock, pop and soul, noting such differences had "rarely been studied systematically". Relation: earliest statement of our cross-style harmonic-difference question for popular music.

### Moore, A. F. (1995). The so-called "flattened seventh" in rock. *Popular Music* (volume/pages not shown on page).
[theory] Maps rock harmonic practice against common-practice tonality and jazz; argues Schenkerian theory does not yet transfer; analyses varieties of diatonic bVII. Relation: theory for bVII as a structural rock scale degree.

### Rohrmeier, M. (2011). Towards a generative syntax of tonal harmony. *Journal of Mathematics and Music*, 5(1), 35–53. (reference confirmed on an Edinburgh talk page; DOI not shown)
[theory] Context-free generative grammar of tonal harmony with preparation and prolongation dependencies. Relation: theoretical reason why chord bigram statistics (ours) are a surface proxy for hierarchical syntax; cite as a limitation.

### Rohrmeier, M. (2020). The syntax of jazz harmony: Diatonic tonality, phrase structure, and form. *Music Theory and Analysis*, 7(1), 1–62. https://doi.org/10.11116/MTA.7.1.1
[theory] Extends the generative grammar to jazz (modulation, borrowing, substitution; blues as plagal). Relation: shows jazz and classical harmony can be modelled with one grammar, supporting the premise of a cross-genre comparison.

### Gjerdingen, R. O. (2007). *Music in the Galant Style*. New York: Oxford University Press. https://doi.org/10.1093/oso/9780195313710.001.0001
[theory] Schema theory of 18th-century harmony. Relation: predicts strong cadential stereotypy (high V→I share, low entropy) in the galant/Classical slice of our classical corpora.

### Caplin, W. E. (1998). *Classical Form: A Theory of Formal Functions for the Instrumental Music of Haydn, Mozart, and Beethoven*. New York: Oxford University Press. https://doi.org/10.1093/oso/9780195104806.001.0001
[theory] Formal-function theory; cadence definitions used by the DCML annotation guidelines and by Nobile 2020. Relation: source for the cadence categories underlying our V→I shares.

### Harrison, D. (1994). *Harmonic Function in Chromatic Music: A Renewed Dualist Theory and an Account of Its Precedents*. Chicago: University of Chicago Press. ISBN 9780226318097.
[theory] Scale-degree-based (Riemannian) function theory with a history of German function theory. Relation: modern summary of Riemann function theory for the T/S/D framing of our cadence classes.

### Everett, W. (2004). Making sense of rock's tonal systems. *Music Theory Online*, 10(4).
[theory] Six tonal systems from major/minor tonality through modal, mixture, blues, pentatonic triad-doubling to chromatic; compares 1957–58 with 1999–2000 hits. Relation: theoretical taxonomy that predicts rock harmony is heterogeneous rather than one trajectory; Shaffer et al. 2020 (below) test it empirically.

### Bennett, A., & Peterson, R. A. (Eds.) (2004). *Music Scenes: Local, Translocal, and Virtual*. Nashville: Vanderbilt University Press. ISBN 9780826514516.
[geography] Fourteen essays on local, translocal and virtual scenes (bop New York, Merseybeat, Memphis rockabilly, London punk, Bronx hip-hop) as sites of innovation. Relation: sociological rationale for using "city where the music was made" as the geographic unit.

### Connell, J., & Gibson, C. (2003). *Sound Tracks: Popular Music, Identity and Place*. London: Routledge. ISBN 9780415170284.
[geography] First comprehensive geography of popular music; argues globalisation loosens but does not erase place–music links. Relation: predicts a weakening geographic signal over time, consistent with Youngblood 2019.

### B. Discovery (2019–2026 unless noted)

### Hamilton, M., & Pearce, M. (2024). Trajectories and revolutions in popular melody based on U.S. charts from 1950 to 2023. *Scientific Reports*, 14, 1–9. https://doi.org/10.1038/s41598-024-64571-x
[pop-corpus] Corpus: 366 chart-topping melodies 1950–2023 (Billboard Melodic Music Dataset). Method: multivariate change-point detection on pitch/rhythm features; AR/VAR era models. Findings: two major complexity drops (1975, 2000) and a smaller one (1996); complexity falls (~30% for pitch and rhythm per the QMUL summary) while note density rises. Relation: the melodic counterpart of our harmonic-complexity series; its break years (1975/1996/2000) differ from Mauch's (1964/1983/1991), so our harmonic breakpoints adjudicate.

### Chander, A., & Quinn, I. (2023). The decline of harmonic schemata in popular music chord loops. EasyChair Preprint 10295 (not peer-reviewed).
[pop-corpus] Corpora: McGill Billboard (1958–1991) vs Yale-Geerdes Billboard (2002–2021). Method: information-theoretic repetition and loop-sharing measures. Findings: 21st-century corpus is more repetitive within songs but shares fewer cross-song schemata. Relation: the only study that extends Billboard harmony past 1991; our pop window ends where theirs begins, so cite for the post-1991 extrapolation.

### Shaffer, K., Vasiete, E., Jacquez, B., Davis, A., Escalante, D., Hicks, C., McCann, J., Noufi, C., & Salminen, P. (2020). A cluster analysis of harmony in the McGill Billboard dataset. *Empirical Musicology Review*, 14(3–4), 146–162. https://doi.org/10.18061/emr.v14i3-4.5576
[pop-corpus] k-means on chord-transition profiles; optimal 5–8 clusters (supporting Everett 2004 over 15 genre tags). Relation: shows McGill Billboard contains several harmonic grammars; our composer/artist clustering (Q3) should expect multi-modality within pop.

### Parmer, T., & Ahn, Y.-Y. (2019). Evolution of the informational complexity of contemporary Western music. *Proceedings of ISMIR 2019*, 175–182.
[pop-corpus] Corpus: 905,896 Million Song Dataset tracks 1960–2010 plus 6,661 Hot 100 songs. Method: conditional entropy of pitch/timbre/loudness/rhythm codewords. Findings: pitch complexity roughly stable; loudness complexity declines; Hot 100 songs cluster near average complexity (inverted-U); popular songs not more similar in pitch than 50 years ago. Relation: contradicts the "harmonic homogenisation" reading of Serrà 2012 on the pitch dimension; our chord-entropy series is the symbolic test.

### Warrell, J., Salichos, L., Gancz, M., & Gerstein, M. B. (2024). Latent evolutionary signatures: A general framework for analysing music and cultural evolution. *Journal of the Royal Society Interface*, 21(212), 20230647. https://doi.org/10.1098/rsif.2023.0647
[pop-corpus] [method] Corpus: McGill Billboard (730 songs, 533 artists, 1958–1991, 64 genres). Method: chord-transition k-mers, VAE with evolutionary prior. Findings: evolutionary representation improves period (r 0.275 vs 0.220) and genre (r 0.243 vs 0.217) prediction; one model shows decreasing variance over time (possible homogenisation). Relation: a mutational-signature analogue on the same pop corpus we use; our explicit descriptive measures are more interpretable but should be reconciled with its variance-decline finding.

### Moss, F. C., & Nakamura, E. (2024). Modeling the evolution of harmony in popular music from different cultural contexts. *Proceedings of CHR 2024*, CEUR Workshop Proceedings, 137–152.
[cross-genre] Corpora: J-Pop (2,419 songs, 1927–2019), US-Pop/McGill Billboard (890 songs, 1958–1991), Brazilian choro (289 songs); 3,598 songs, 351,265 chord tokens. Method: content-based transmission model of chord 4-grams with substitution probabilities; three chord-distance metrics. Findings: J-Pop chord-frequency entropy rises (strongest 1970s–mid-1990s); US-Pop vocabulary stable with slight late rise; choro no trend; chord categories used increasingly while extensions stay stable. Relation: the closest existing multi-corpus diachronic harmony study; it compares popular repertoires across cultures, we compare classical/jazz/pop across 450 years, and its "US-Pop stable" finding is a direct benchmark for our McGill entropy series.

### Nakamura, E. (2023). Computational analysis of selection and mutation probabilities in the evolution of chord progressions. *Proceedings of CMMR 2023*, 462–473. https://doi.org/10.5281/zenodo.10113462
[method] J-Pop chord corpus; stochastic reference-selection/mutation model. Findings: strong recency bias, large and time-varying mutation rates. Relation: supplies a generative cultural-evolution model for chord progressions that our descriptive trends could later be fitted to.

### Nakamura, E. (2021). Conjugate distribution laws in cultural evolution via statistical learning. *Physical Review E*, 104, 034309. https://doi.org/10.1103/PhysRevE.104.034309 (arXiv:2102.01465)
[theory] Shows beta/conjugate distributions of musical parameters arise from oblique statistical learning. Relation: theoretical reason to report between-composer dispersion, not only means, in each period.

### Moss, F. C., Souza, W. F., & Rohrmeier, M. (2020). Harmony and form in Brazilian choro: A corpus-driven approach to musical style analysis. *Journal of New Music Research*. https://doi.org/10.1080/09298215.2020.1797109 (verified via EPFL news page describing the paper)
[cross-genre] ~300 choro pieces, late 1800s–2000s. Findings: chord- and key-level rules diverge more than in classical music; five/six-note chord extensions become much more common after the 1950s (jazz influence suggested). Relation: independent evidence that extension rates rise in the mid-20th century in a non-classical repertoire; a pattern to compare with our WJD seventh/extension series.

### Sears, D. R. W., & Forrest, D. (2021). Triadic patterns across classical and popular music corpora: Stylistic conventions, or characteristic idioms? *Journal of Mathematics and Music*, 15(2), 140–153. https://doi.org/10.1080/17459737.2021.1925762 (citation from TTU lab publications page; abstract not fetched; method as described by Windholz et al. 2026)
[cross-genre] Large Roman-numeral corpora of classical and Anglophone popular music; ranks conventional vs characteristic progressions at formal boundaries. Relation: the most direct cross-genre harmonic comparison to date, but synchronic; we add the time axis.

### Windholz, M. O., Sears, D. R. W., & Moss, F. C. (2026). Harmonic patterns in Brazilian choro: A data-driven comparison with Western classical and Anglophone popular music. *MusMat – Brazilian Journal of Music and Mathematics*, 10. (pages/DOI not shown)
[cross-genre] Reproduces Sears & Forrest with choro added. Findings: choro has much higher applied-dominant incidence and characteristic iv–iiø–i; vi–V7–I appears at similar rates in all three styles. Relation: supports the "shared core, distinctive periphery" hypothesis for Q2.

### Anzuoni, E., Ayhan, S., Dutto, F., McLeod, A. P., Moss, F. C., & Rohrmeier, M. A. (2021). Chord embeddings of harmonic progressions reveal historical trends. *Proceedings of SMC 2021* (postprint at https://infoscience.epfl.ch/handle/20.500.14299/179469).
[classical-corpus] Corpus: 4,045 DCML chord sequences from 24 composers, Renaissance to Modernism. Method: word2vec chord embeddings, hierarchical clustering, held-out-composer LSTM prediction. Findings: ~50% next-chord accuracy; inverted-U in predictability (Classical most predictable, Renaissance and Modernist least); IV predictable only for Baroque; I and V poorly predicted for Debussy/Ravel. Relation: replicates on part of our classical data; its inverted-U predictability is the same quantity as our chord entropy, so we should report agreement.

### Moss, F. C., Lieck, R., & Rohrmeier, M. (2024). Computational modeling of interval distributions in tonal space reveals paradigmatic stylistic changes in Western music history. *Humanities and Social Sciences Communications*, 11, 1–11. (DOI not shown on DOAJ page)
[classical-corpus] Tonal-space model of pieces as bags of tonal pitch classes. Findings: fifth dominates for centuries; major and minor thirds rise sharply in the 19th c. with extended tonality. Relation: same journal and framing; our chord-level third-related root motion is the syntactic counterpart.

### Moss, F. C., Neuwirth, M., & Rohrmeier, M. (2021). Discovering latent tonal "topics" in a large historical corpus. *Music & Science*. https://doi.org/10.1177/20592043211048827 (citation from EPFL DCML page)
[classical-corpus] LDA on pitch-class distributions over ~600 years; topics map to contiguous line-of-fifths segments; marks the common-practice to extended-tonality transition. Relation: method precedent (topic models, cf. Mauch 2015) applied to classical.

### Moss, F. C. (2019). Transitions of tonality: A model-based corpus study. PhD thesis, EPFL (record 273178; author/year inferred from the EPFL news item "Congrats to Dr. Fabian Moss" and the record's file name; thesis text fetched).
[classical-corpus] Meso level: >75,000 chord symbols from nine 19th-century composers; chord distributions follow Zipf/Heaps laws; entropy analysis finds suspensions most predictive; progressions asymmetric, mostly by fifths, with third-based progressions increasing. Macro level: ~3M notes, >2,000 pieces, 75 composers. Relation: the most detailed existing chord-level diachronic analysis of the 19th century; we must cite its "thirds increase" result when interpreting our root-motion classes.

### Henzel, B., Müller, M., & Weiß, C. (2025). Style evolution in Western choral music: A corpus-based strategy. *Computational Humanities Research*, 1, e13. https://doi.org/10.1017/chr.2025.10016
[classical-corpus] Carus Audio Corpus: 5,729 tracks, 2,401 works, 234 composers, c. 1570–2020. Method: deep-learning pitch-class activations, tonal complexity "evolution curves", Tukey-window life-date heuristic (validated: mean distance 0.046 vs 0.068). Findings: complexity rises Renaissance→Baroque then plateaus; minor-key works consistently more complex; vocal music more complex than instrumental in the 18th c., less in the 20th. Relation: the plateau after 1800 contrasts with the DCML "19th-century expansion" narrative; our chord-level series can adjudicate.

### Weiß, C., & Müller, M. (2023). Studying tonal evolution of Western choral music: A corpus-based strategy. *CEUR Workshop Proceedings*, 3558 (CHR 2023), 687–702.
[classical-corpus] 5,773 choral tracks; validates the composer-lifetime dating heuristic. Relation: method support for dating pieces by composer lifetime where composition year is missing (relevant for When in Rome).

### Almeida, F., Bernardes, G., & Weiß, C. (2022). Mid-level harmonic audio features for musical style classification. *Proceedings of ISMIR 2022*, 210–217.
[method] Cross-Era (1,600 pieces, four periods) and Cross-Composer (1,100 pieces, 11 composers). Findings: chord-transition features reach 83.2% era accuracy; composer classification only 38.25% for 11 composers. Relation: baseline for how separable composers are by harmonic features (Q3): era is easy, composer is hard.

### Sailor, M. (2025). *Deep learning for large-scale harmonic analysis: A corpus study of Western harmony from 1700–1900*. PhD dissertation, Yale University (advisor I. Quinn). https://elischolar.library.yale.edu/gsas_dissertations/1574
[classical-corpus] >12,000 movements analysed with automatic Roman-numeral models. Findings: chromatic scale-degree proportion and key dispersion rise steadily 1700–1900; I/V transition tendencies fall then rise; major-key practice converges toward minor-key practice; harmony usage more dispersed through the 19th c. Relation: the largest-scale classical harmony trend study so far, but automatic labels and 1700–1900 only; our expert-annotated 1565–1950 data test whether the same trends hold.

### Gotham, M. (2023). Chromatic chords in theory and practice. *Proceedings of ISMIR 2023*, 272–278. https://doi.org/10.5281/zenodo.10265275
[classical-corpus] Corpus: When in Rome (~2,000 analyses). Findings: German augmented sixths 653 vs Italian 63; minor-key contexts dominate; descending fifth progressions outnumber ascending; quiescenza-at-end hypothesis not supported. Relation: shows national annotation traditions differ in how chromatic chords are labelled, a confound when pooling When in Rome with DCML.

### Micchi, G., Gotham, M., & Giraud, M. (2020). Not all roads lead to Rome: Pitch representation and model architecture for automatic harmonic analysis. *Transactions of ISMIR*, 3(1), 42–54. https://doi.org/10.5334/tismir.45
[method] Automatic Roman-numeral analysis architecture. Relation: cite when discussing the human-vs-automatic annotation trade-off (Sailor 2025 vs our expert data).

### Harasim, D., Finkensiep, C., Ericson, P., O'Donnell, T. J., & Rohrmeier, M. (2020). The Jazz Harmony Treebank. *Proceedings of ISMIR 2020*, 207–215. https://doi.org/10.5281/zenodo.4245406
[jazz-corpus] [dataset] Expert syntax-tree analyses of complete jazz standards from iRealPro lead sheets. Relation: alternative jazz harmony resource (standards rather than solos); useful to argue WJD lead-sheet chords are representative.

### Raposo, A. N., & Soares, V. N. G. J. (2025). Generative jazz chord progressions: A statistical approach to harmonic creativity. *Information*, 16(6), 504. https://doi.org/10.3390/info16060504
[jazz-corpus] 1,382 jazz standards with keys, sections and chords; statistical generation. Relation: marginal; indicates a second standards corpus of comparable size to Broze & Shanahan's.

### Jacoby, N., Tishby, N., & Tymoczko, D. (2015). An information theoretic approach to chord categorization and functional harmony. *Journal of New Music Research*, 44(3), 219–244. https://doi.org/10.1080/09298215.2015.1036888
[method] Evaluates harmonic theories by accuracy and complexity across eleven corpora; recovers T/S/D categories as an optimal clustering. Relation: justifies collapsing chords into functional classes and the use of information-theoretic measures across corpora with different chord vocabularies.

### White, C. W., & Quinn, I. (2016). The Yale-Classical Archives Corpus. *Empirical Musicology Review*, 11(1), 50–58. https://doi.org/10.18061/emr.v11i1.4958
[dataset] 13,769 MIDI files, 571 composers, >14M vertical slices with composer country, date, genre, key. Relation: the main alternative classical corpus with composer-country metadata, relevant to a future geographic replication.

### Di Marco, N., Loru, E., Galeazzi, A., Cinelli, M., & Quattrociocchi, W. (2025). Decoding musical evolution through network science. arXiv:2501.07557 (year/ID from the arXiv URL).
[cross-genre] 21,480 MIDI songs (MetaMIDI) in six macro-genres over ~four centuries; note-transition networks (not chords). Findings: Classical and Jazz more complex than Pop/Rock/Electronic/Hip-Hop; Classical efficiency declines over time (Mann–Kendall τ = −0.401, p = 0.001), Jazz falls after an early rise (τ = −0.487). Relation: the only cross-genre long-run complexity study; caveats (LLM-estimated dates, heuristic genre labels) are severe, so our expert-annotated comparison is a needed check.

### Schich, M., Song, C., Ahn, Y.-Y., Mirsky, A., Martino, M., Barabási, A.-L., & Helbing, D. (2014). A network framework of cultural history. *Science*, 345(6196), 558–562.
[geography] Birth–death location network of >150,000 notable individuals over two millennia; identifies cultural centres and mobility patterns. Relation: the precedent for placing creators in geographic space and for the "space-time frame" idea; contains no musical content.

### Lee, C., & Cunningham, P. (2012). The geographic flow of music. arXiv:1204.2677.
[geography] Last.fm listening in hundreds of cities; leadership network among cities; preferences tied to nationality, language and geography; large cities lead weakly. Relation: evidence for city-level structure in consumption, which motivates city as the unit in our Mantel design.

### Dueñas, M., & Mandel, A. (2023). The structure of global cultural networks: Evidence from the diffusion of music videos. *PLOS ONE*, 18(11), e0294149. https://doi.org/10.1371/journal.pone.0294149
[geography] Independent-cascade inference of a global music-diffusion network; gravity-model tests. Findings: cultural, geographic and historical distance drive diffusion; economic factors matter less. Relation: supports a geographic-distance predictor of musical similarity at the country level; we test it at city level for production rather than consumption.

### Passmore, S., Wood, A. L. C., Barbieri, C., Shilton, D., Daikoku, H., Atkinson, Q. D., & Savage, P. E. (2024). Global musical diversity is largely independent of linguistic and genetic histories. *Nature Communications*, 15, 1–12. https://doi.org/10.1038/s41467-024-48113-7
[geography] 5,242 songs from 719 societies; matched set of 121 societies. Findings: music shows geographic/historical patterning like language and genes, but music–language and music–gene similarity are weak and inconsistent. Relation: a global-scale distance-matrix design (the methodological family of our Mantel tests) showing that geographic structure in music can exist without non-musical correlates.

### Brown, S., Savage, P. E., Ko, A. M.-S., Stoneking, M., Ko, Y.-C., Loo, J.-H., & Trejaut, J. A. (2014). Correlations in the population structure of music, genes and language. *Proceedings of the Royal Society B*, 281(1774). https://doi.org/10.1098/rspb.2013.2072
[geography] [method] Nine Taiwanese populations; music–gene correlations as strong as language–gene; music–language not correlated. Relation: the canonical Mantel/partial-Mantel style design for music; cite for the method lineage (the fetched record did not display the methods section, so confirm the partial-Mantel detail in the full text before citing it as such).

### Nishikawa, Y., & Ihara, Y. (2022). Cultural transmission of traditional songs in the Ryukyu Archipelago. *PLoS ONE*, 17(6), e0270354. https://doi.org/10.1371/journal.pone.0270354
[geography] 1,342 traditional songs (CantoCore); Neighbor-Net, delta scores, AMOVA vs lexical and mtDNA distance. Findings: horizontal transmission shapes musical diversity more than linguistic; social context of singing modulates geographic patterning. Relation: shows geographic signal in music depends on genre/context, analogous to our expectation that geography matters differently for jazz, pop and classical.

### Le Bomin, S., Lecointre, G., & Heyer, E. (2016). The evolution of musical diversity: The key role of vertical transmission. *PLoS ONE*, 11(3), e0151570. https://doi.org/10.1371/journal.pone.0151570
[geography] Phylogenetic analysis of coded Gabonese musical traits; vertical transmission strongest for metre, rhythm and melody. Relation: older but foundational for treating musical features as inheritable traits in space.

### Lee, H., Polak, R., Anglada-Tort, M., Schönwiesner, M., Park, M., & Jacoby, N. (2026). Do melody and rhythm coevolve? arXiv:2605.05982 (ID from URL; year not shown in text).
[geography] 27,628 chart songs from 59 countries (2017–2022); source-separated melody/rhythm distributions. Findings: same-region countries more similar (melody d = 0.39, rhythm d = 0.58); between-country divergence exceeds null (z = 10.0 / 14.0); melodic and rhythmic diversity uncorrelated. Relation: recent evidence that geographic proximity still predicts musical similarity in contemporary charts, the null hypothesis our Mantel tests examine for harmony.

### de Clercq, T. (2021). How should corpus studies of harmony in popular music handle the minor tonic? *Proceedings of the Future Directions of Music Cognition International Conference*, 44–48. https://doi.org/10.18061/FDMC.2021.0006
[method] RS200 (154 major-tonic, 32 minor-tonic songs) vs Kostka-Payne classical corpus; KL divergence between parallel and relative encodings. Findings: classical fits parallel encoding (divergence 0.043 vs 1.052); popular music is mixed (0.588 vs 0.630 for roots; 1.353 vs 1.575 for transitions). Relation: a concrete methodological decision we must document: how minor-tonic rock songs are encoded changes IV/V/bVII shares.

### de Clercq, T. (2017, talk transcript; SMT session). A corpus analysis of harmony in country music. Unpublished transcript at midside.com.
[pop-corpus] NN200 country corpus (200 songs). Findings: I, IV, V = ~82% of chords in country, ~79% in major-key rock, ~75% in early common-practice music (after Budge); classical root motion favours "progressive" (4th up, 3rd down, 2nd up), rock is balanced, country in between. Relation: unpublished, but the only cross-genre root-motion comparison with numbers; treat as supporting, not primary, evidence for Meeùs-style vector asymmetry differing by repertoire.

---

## Part 2. Synthesis (what is established, contested, and the gaps)

**Established.** Three results recur across independent corpora and are safe to treat as background. (1) Chord usage in every repertoire is heavy-tailed: a handful of chords account for most tokens (Moss et al. 2019; Burgoyne et al. 2011, where major triads exceed half of all chord classes; Moss 2019 thesis, Zipf/Heaps behaviour), so entropy-style measures are well-behaved summaries. (2) Within classical music, something that can be called harmonic or tonal "complexity" rises over the long run, with the 19th century as the pivot: the fifths range widens (Moss, Neuwirth & Rohrmeier 2022), thirds rise in the 19th century (Moss, Lieck & Rohrmeier 2024; Moss 2019), chromatic degrees and key dispersion rise 1700–1900 (Sailor 2025), rare-event frequencies and their dispersion rise 1500–1900 (Nakamura & Kaneko 2019), and modes dissolve after 1800 (Harasim et al. 2021). (3) Within popular music, harmonic change is real but modest and stepwise rather than monotonic: Mauch et al. (2015) find three punctuated changes with a 75% fall in dominant sevenths, Léveillé Gauvin (2015) a rise in flat-side chords within the 1960s, Broze & Shanahan (2013) a sudden 1950s drop in ascending-fourth root motion in jazz, and Moss & Nakamura (2024) a stable US-pop chord vocabulary 1958–1991.

**Contested.** Three questions remain open and our data bear on each. First, *direction of complexity in the 20th century*: Serrà et al. (2012) and Hamilton & Pearce (2024) report restriction/simplification (melodic complexity down ~30%), Di Marco et al. (2025) report declining note-network complexity even for classical and jazz, whereas Parmer & Ahn (2019) find pitch complexity flat and Warrell et al. (2024) find only weak variance decline in Billboard chords. None of these uses expert chord annotations, and the audio studies cannot separate harmony from timbre. Second, *gradual vs punctuated change*: Broze & Shanahan argue chord frequencies drift slowly while transitions jump; Mauch et al. and Hamilton & Pearce locate revolutions at different years (1964/1983/1991 vs 1975/1996/2000); Weiß et al. (2018) and Anzuoni et al. (2021) find classical period boundaries c. 1750/1820/1900 and an inverted-U in predictability. Third, *whether repertoires share one harmonic system*: Tymoczko (2011) and Rohrmeier (2011, 2020) argue for an extended common practice spanning classical and jazz; Everett (2004), Biamonte (2010), Doll (2017) and Nobile (2020) argue rock has distinct tonal systems in which IV- and bVII-based closure replaces V→I (de Clercq & Temperley 2011; Temperley & de Clercq 2013). The only quantitative cross-genre harmony comparisons are synchronic (Sears & Forrest 2021; Windholz, Sears & Moss 2026; de Clercq 2017 talk) or compare popular repertoires with each other (Moss & Nakamura 2024).

**Who has already done part of what we do.** Honest accounting: the classical long-run trajectory (Q1) has been described at the pitch-class level by the DCML group in this very journal (Harasim et al. 2021; Moss, Lieck & Rohrmeier 2024) and at the chord level for 1700–1900 by Sailor (2025, automatic labels) and for the 19th century by Moss (2019). Our contribution on Q1 is therefore not novelty of question but (a) expert chord-level measures across 1565–1950, (b) cadence-share and root-motion-class measures that none of these report, and (c) the extension to jazz and pop in one frame. Composer clustering (Q3) exists for classical (White 2014; Weiß et al. 2018; Almeida et al. 2022 show composer separation is hard, ~38% for 11 composers) and for pop songs (Shaffer et al. 2020), never across genres. The chord-level diachronic comparison of three repertoires (Q2) has not been done; ChoCo (2023) built the shared format but did no analysis, and Moss & Nakamura (2024) is the closest antecedent.

**Geography is the real gap.** No study we could find relates chord-level harmony to the city of production, and none applies Mantel or spatial-autocorrelation tests to Western art, jazz or chart repertoires. The methodological lineage comes from comparative musicology and cultural evolution (Brown et al. 2014; Le Bomin et al. 2016; Nishikawa & Ihara 2022; Passmore et al. 2024; Lee et al. 2026), where distance-matrix designs are standard but the units are societies or countries and the features are melodic/rhythmic. The production-geography literature is either network-based without musical content (Schich et al. 2014; Park et al. 2015), consumption-based (Lee & Cunningham 2012; Dueñas & Mandel 2023), or qualitative (Connell & Gibson 2003; Bennett & Peterson 2004). Youngblood (2019) gives the one quantitative result that geography structured musical transmission before 2000 and not after; our space-time Mantel design, controlling for time, is the first test of that idea on harmony itself.

**Caveats the review imposes.** (i) Annotation heterogeneity: When in Rome pools national labelling traditions (Gotham 2023) and automatic analyses differ systematically from human ones (Micchi et al. 2020); DCML and When in Rome should be modelled with a corpus covariate. (ii) Minor-tonic encoding changes IV/V/bVII shares in rock (de Clercq 2021) and mode drift is itself a historical variable (Horn & Huron 2015). (iii) The WJD chord track is a lead sheet under improvised solos (Frieler 2019), so jazz "harmony" is compositional, not performed. (iv) Chronological imbalance (43% of RS200 from the 1960s; Classical-era dominance in DCML noted by Anzuoni et al.) requires period-balanced resampling. (v) Chord bigram statistics are a surface proxy for hierarchical syntax (Rohrmeier 2011, 2020; Jacoby et al. 2015).

---

## Part 3. Must-cite lists

**Introduction (7):** Mauch et al. 2015; Serrà et al. 2012; Harasim et al. 2021; Moss, Lieck & Rohrmeier 2024; Broze & Shanahan 2013; Tymoczko 2011; Savage 2019. (Optional eighth: Youngblood 2019 for the geography hook.)

**Methods (8):** Neuwirth et al. 2018 (DCML standard); Hentschel et al. 2021 and 2023 (DCML corpora, cadence labels); Gotham et al. 2023 (When in Rome); Burgoyne et al. 2011 (McGill Billboard); Temperley & de Clercq 2013 (Rock Corpus); Pfleiderer et al. 2017 with Frieler 2019 (WJD); Meeùs 2000 (root-motion classes); Brown et al. 2014 / Passmore et al. 2024 (Mantel-type distance designs); de Clercq 2021 (minor-tonic encoding).

---

## Could not verify (left out of the bibliography)

- **White & Quinn (2018), "Chord context and harmonic function in tonal music", *Music Theory Online*.** Six searches (title in quotes, author names, "mto.18.24", MTO site, Yale faculty page) returned no page showing this article; the Yale page confirms only White's 2013 dissertation *Some Statistical Properties of Tonal Harmony, 1650–1900* (advisor Quinn). Do not cite until a page is found.
- **Hentschel, Moss, Neuwirth & Rohrmeier, "Towards a unified model of chords in Western harmony" (ISMIR 2021).** Not found in the ISMIR 2021 anthology search; the DCML standard is documented instead in Neuwirth et al. 2018 and Hentschel et al. 2021.
- **A dedicated "Distant Listening Corpus" data paper.** Only the SNSF project page and the three DCML data papers above were found; a Zenodo record (Hentschel, Rammos, Neuwirth & Rohrmeier 2022, Medtner Tales, DOI 10.5281/zenodo.8329410) refers to an "accompanying data report still under review", which is the 2023 EMR paper.
- **Moore 1992** is included above but the Cambridge page did not display the author or volume/pages; confirm 11(1), 73–106 before submission.
- **Volume/issue/pages** not displayed for Weiß et al. 2018/2019, White 2014, Albrecht & Huron 2014, Moore 1995, Moss et al. 2022, Moss et al. 2024 (HSSC) and Nakamura & Kaneko 2019 (DOI only); fill from the DOI landing pages.
- **Sears & Forrest 2021**: citation confirmed on the TTU lab page; abstract not fetched (Taylor & Francis page not reachable).
- **Percino et al. 2014** is verified but is about instrumentation, not geography; it is kept only as a "simplicity sells" explanatory reference.
