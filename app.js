/* Harmony in Space and Time — space-time cube. Design and interaction model follow
   github.com/ShaneM73/European_spatiotemporal_geography (panel, timeline, views, themes, projected labels). */
(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);

  // ---------------------------------------------------------------- world
  const LON = [-130, 45], LAT = [12, 70], YEAR = [1550, 2010];
  const SX = 24, SZ = SX * (LAT[1] - LAT[0]) / ((LON[1] - LON[0]) * Math.cos(41 * Math.PI / 180)), TIME_H = 11;
  const BASE = 0.8, SEA_Y = -0.02, SLAB_H = 0.6;
  const KM_PER_UNIT = (LON[1] - LON[0]) * 111.32 * Math.cos(41 * Math.PI / 180) / SX;
  const px = (lon) => (lon - LON[0]) / (LON[1] - LON[0]) * SX - SX / 2;
  const pz = (lat) => -((lat - LAT[0]) / (LAT[1] - LAT[0]) * SZ - SZ / 2);
  const py = (yr) => BASE + (yr - YEAR[0]) / (YEAR[1] - YEAR[0]) * TIME_H;
  const yearOfY = (y) => YEAR[0] + (y - BASE) / TIME_H * (YEAR[1] - YEAR[0]);

  const THEMES = {
    light: { bg: '#f3f2ee', slabTop: '#e3e1da', slabSide: '#d6d3ca', frame: '#b4babf', dim: 0.55, hemi: 0.55, sun: 0.6, column: '#6b7177', slice: '#d9480f',
             genre: { classical: '#2f5fd0', jazz: '#b7791f', rock_pop: '#c2410c' }, cluster: ['#9aa0a6', '#b7791f', '#7c3aed', '#0f766e', '#c2410c', '#d97706', '#2f5fd0'], rampLo: '#c9ccd1', rampHi: '#d9480f' },
    dark: { bg: '#14171a', slabTop: '#24282c', slabSide: '#1d2125', frame: '#3b4248', dim: 0.3, hemi: 1.0, sun: 0.55, column: '#8fa0c4', slice: '#ff7a45',
            genre: { classical: '#7aa2ff', jazz: '#f2b134', rock_pop: '#ff8a5c' }, cluster: ['#5c6579', '#f2b134', '#c38fe6', '#79c99e', '#e8737a', '#f08a4b', '#7fb3e6'], rampLo: '#3a4663', rampHi: '#ff7a45' },
  };
  const GL = { classical: 'Classical', jazz: 'Jazz', rock_pop: 'Rock & pop' };
  const CL = ['', 'Bebop to contemporary jazz', 'Chromatic, extended (Bartók, post-bop)', 'Triadic, plagal (pre-tonal and 1960s–80s pop)', 'bVII and step-driven rock', 'Dominant-seventh diatonic (early jazz, rock and roll, R&B)', 'Common practice (Corelli to Rachmaninoff)'];
  const ERA = (y, g) => {
    if (g === 'classical') return y < 1600 ? 'Renaissance' : y < 1700 ? 'Early Baroque' : y < 1750 ? 'Late Baroque' : y < 1800 ? 'Classical' : y < 1850 ? 'Early Romantic' : y < 1900 ? 'Late Romantic' : 'Early 20th century';
    if (g === 'jazz') return y < 1945 ? 'Swing era' : y < 1960 ? 'Bebop / hard bop' : y < 1975 ? 'Modal / post-bop' : 'Contemporary jazz';
    return y < 1965 ? 'Rock and roll, soul' : y < 1975 ? 'Rock, pop' : y < 1985 ? 'Rock, disco, new wave' : 'Pop, rock';
  };
  const pct = d3.format('.0%'), pct1 = d3.format('.1%'), fmt = d3.format(',');

  const state = { theme: 'dark', view: 'cube', colorBy: 'genre', genres: new Set(['classical', 'jazz', 'rock_pop']), reliefK: 0.12, focus: false, columns: true, sceneLabels: true, cityLabels: true, year: 1725, selected: null, trace: null, playing: false };

  // ---------------------------------------------------------------- data
  let DATA, pieces, scenes, composers, inFrame, BM;
  let renderer, scene, camera, controls, hemi, sun, slab, terrain, tex, texImgs = {}, elev = null, land = null, gridW, gridH, tpos, tg, nv;
  let points, pos, col, basePos, hl, slicePlane, frameLines, cityG, sceneColors;
  let labelEls = { years: [], now: null, cities: [], scenes: [] };
  let cameraTween = null, playTimer = null, spinIdle = true;

  Promise.all([fetch('data/harmony_data.json').then((r) => r.json()), fetch('data/basemap_meta.json').then((r) => r.json())]).then(([d, m]) => {
    DATA = d; BM = m; pieces = d.pieces; scenes = d.scenes; composers = d.composers;
    const cl = new Map(composers.map((r) => [canon(r.unit), r]));
    for (const p of pieces) { const c = cl.get(canon(p.composer)); p.cluster = c ? c.harmonic_cluster : 0; p.unit = c ? c.unit : p.composer; }
    inFrame = pieces.filter((p) => p.lon >= LON[0] && p.lon <= LON[1] && p.lat >= LAT[0] && p.lat <= LAT[1]);
    sceneColors = scenes.map((s, i) => d3.hsl((i * 137.508) % 360, 0.62, state.theme === 'dark' ? 0.62 : 0.45).formatHex());
    if (location.hash.startsWith('#year=')) { const y = +location.hash.slice(6); if (y >= YEAR[0] && y <= YEAR[1]) state.year = y; }
    try { build(); } catch (e) { console.error(e); $('loading').hidden = true; const n = document.createElement('div'); n.className = 'nowebgl'; n.textContent = 'The cube needs WebGL, which this browser or view does not provide. The findings page does not depend on it.'; document.body.append(n); return; }
    buildTimeline(); bindUI(); applyTheme(state.theme); setYear(state.year, true); setView('cube', true); recolor(); refilter(); drawLegend();
    $('loading').hidden = true; frame()
  }).catch((e) => { console.error(e); $('loading').textContent = 'Could not load the data files. If you opened this page as a file, serve it over HTTP (python -m http.server).'; });

  function canon(n) { const k = String(n).toLowerCase().trim(); return k.startsWith('the ') ? k.slice(4) : k; }

  // ---------------------------------------------------------------- scene
  function build() {
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(innerWidth, innerHeight);
    $('scene').appendChild(renderer.domElement);
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(38, innerWidth / innerHeight, 0.2, 500);
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; controls.dampingFactor = 0.08; controls.minDistance = 6; controls.maxDistance = 90;
    controls.addEventListener('start', () => { cameraTween = null; spinIdle = false; });
    hemi = new THREE.HemisphereLight(0xffffff, 0x8a8f94, 1.0); sun = new THREE.DirectionalLight(0xffffff, 0.55); sun.position.set(-8, 14, 6); scene.add(hemi, sun);

    // terrain + plinth
    [gridW, gridH] = BM.elevSize; nv = gridW * gridH;
    const tw = px(LON[1]) - px(LON[0]), th = pz(LAT[0]) - pz(LAT[1]);
    slab = new THREE.Mesh(new THREE.BoxGeometry(tw, SLAB_H, th), [0, 1, 2, 3, 4, 5].map(() => new THREE.MeshLambertMaterial()));
    slab.position.set(0, SEA_Y - SLAB_H / 2 - 0.004, 0); scene.add(slab);
    tg = new THREE.BufferGeometry(); tpos = new Float32Array(nv * 3); const tuv = new Float32Array(nv * 2);
    for (let j = 0; j < gridH; j++) for (let i = 0; i < gridW; i++) { const v = j * gridW + i; tpos[v * 3] = px(LON[0] + i / (gridW - 1) * (LON[1] - LON[0])); tpos[v * 3 + 1] = SEA_Y; tpos[v * 3 + 2] = pz(LAT[1] - j / (gridH - 1) * (LAT[1] - LAT[0])); tuv[v * 2] = i / (gridW - 1); tuv[v * 2 + 1] = 1 - j / (gridH - 1); }
    const tidx = new Uint32Array((gridW - 1) * (gridH - 1) * 6); let k = 0;
    for (let j = 0; j < gridH - 1; j++) for (let i = 0; i < gridW - 1; i++) { const a = j * gridW + i, b = a + 1, c = a + gridW, d = c + 1; tidx.set([a, c, b, b, c, d], k); k += 6; }
    tg.setAttribute('position', new THREE.BufferAttribute(tpos, 3)); tg.setAttribute('uv', new THREE.BufferAttribute(tuv, 2)); tg.setIndex(new THREE.BufferAttribute(tidx, 1));
    const blank = document.createElement('canvas'); blank.width = blank.height = 2; blank.getContext('2d').fillStyle = '#1b252c'; blank.getContext('2d').fillRect(0, 0, 2, 2);
    tex = new THREE.CanvasTexture(blank); tex.minFilter = THREE.LinearMipMapLinearFilter; tex.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
    terrain = new THREE.Mesh(tg, new THREE.MeshLambertMaterial({ map: tex })); scene.add(terrain);
    for (const t of ['dark', 'light']) { const im = new Image(); im.onload = () => { if (state.theme === t) { tex.image = im; tex.needsUpdate = true; } }; im.src = `data/map_texture_${t}.jpg`; texImgs[t] = im; }
    const terr = new Image(); terr.onload = () => { decodeTerrain(terr); updateRelief(); buildCities(); refilter(); }; terr.src = 'data/terrain.png';

    // cube frame + time slice
    const fp = [], x0 = px(LON[0]), x1 = px(LON[1]), z0 = pz(LAT[1]), z1 = pz(LAT[0]), yT = py(YEAR[1]);
    for (const y of [BASE, yT]) fp.push(x0, y, z0, x1, y, z0, x1, y, z0, x1, y, z1, x1, y, z1, x0, y, z1, x0, y, z1, x0, y, z0);
    for (const [x, z] of [[x0, z0], [x1, z0], [x1, z1], [x0, z1]]) fp.push(x, BASE, z, x, yT, z);
    for (let yr = 1600; yr <= 2000; yr += 50) fp.push(x0 - 0.15, py(yr), z1, x0, py(yr), z1);
    frameLines = new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(fp, 3)), new THREE.LineBasicMaterial({ transparent: true, opacity: 0.7 }));
    scene.add(frameLines);
    slicePlane = new THREE.Group();
    const sp = new THREE.Mesh(new THREE.PlaneGeometry(tw, th), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.08, side: THREE.DoubleSide, depthWrite: false }));
    sp.rotateX(-Math.PI / 2); slicePlane.add(sp);
    const so = new THREE.LineLoop(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute([x0, 0, z0, x1, 0, z0, x1, 0, z1, x0, 0, z1], 3)), new THREE.LineBasicMaterial({ transparent: true, opacity: 0.9 }));
    slicePlane.add(so); scene.add(slicePlane);

    // pieces
    const n = inFrame.length; pos = new Float32Array(n * 3); col = new Float32Array(n * 3); basePos = new Float32Array(n * 3);
    const hash = (s) => { let h = 0; for (const ch of String(s)) h = (h * 31 + ch.charCodeAt(0)) >>> 0; return h; };
    inFrame.forEach((p, i) => { const h = hash(p.piece_id); basePos[i * 3] = px(p.lon) + ((h % 1000) / 1000 - 0.5) * 0.5; basePos[i * 3 + 1] = py(p.year) + (((h >> 20) % 1000) / 1000 - 0.5) * 0.08; basePos[i * 3 + 2] = pz(p.lat) + (((h >> 10) % 1000) / 1000 - 0.5) * 0.35; });
    pos.set(basePos);
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const dot = document.createElement('canvas'); dot.width = dot.height = 64; { const cx = dot.getContext('2d'); cx.beginPath(); cx.arc(32, 32, 28, 0, Math.PI * 2); cx.fillStyle = '#fff'; cx.fill(); }
    points = new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.24, map: new THREE.CanvasTexture(dot), alphaTest: 0.5, vertexColors: true, sizeAttenuation: true, transparent: true, opacity: 0.95 }));
    scene.add(points);
    hl = new THREE.Mesh(new THREE.SphereGeometry(0.2, 12, 12), new THREE.MeshBasicMaterial()); hl.visible = false; scene.add(hl);
    cityG = new THREE.Group(); scene.add(cityG);

    // labels (HTML, projected each frame)
    const L = $('labels');
    for (let yr = 1600; yr <= 2000; yr += 50) { const el = document.createElement('div'); el.className = 'axis-label'; el.textContent = yr; el.dataset.y = py(yr); L.append(el); labelEls.years.push(el); }
    labelEls.now = document.createElement('div'); labelEls.now.className = 'axis-label now'; L.append(labelEls.now);
    scenes.forEach((s, i) => { const el = document.createElement('div'); el.className = 'scene-label'; el.style.setProperty('--c', sceneColors[i]); const b = document.createElement('b'); b.textContent = s.scene_id; el.append(b, document.createTextNode(s.label)); L.append(el); labelEls.scenes.push(el); });

    // interaction
    const ray = new THREE.Raycaster(); ray.params.Points.threshold = 0.17; const mouse = new THREE.Vector2(); const tip = $('tooltip');
    let downAt = null;
    renderer.domElement.addEventListener('pointerdown', (e) => { downAt = [e.clientX, e.clientY]; });
    renderer.domElement.addEventListener('pointermove', (e) => {
      mouse.x = (e.clientX / innerWidth) * 2 - 1; mouse.y = -(e.clientY / innerHeight) * 2 + 1;
      const i = pick(); if (i < 0) { tip.hidden = true; hl.visible = false; renderer.domElement.style.cursor = ''; return; }
      const p = inFrame[i]; renderer.domElement.style.cursor = 'pointer';
      hl.position.set(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]); hl.visible = true;
      tip.replaceChildren(); const b = document.createElement('b'); b.textContent = `${p.composer} — ${p.title}`; const s = document.createElement('span'); s.textContent = `${p.city}, ${p.year} · ${GL[p.genre]} · sevenths ${pct(p.seventh_rate)} · V→I ${p.V_to_I_share == null ? '—' : pct(p.V_to_I_share)}`; tip.append(b, s); tip.hidden = false;
      let x = e.clientX + 14, y = e.clientY + 14; if (x + tip.offsetWidth > innerWidth - 8) x = e.clientX - tip.offsetWidth - 14; if (y + tip.offsetHeight > innerHeight - 8) y = e.clientY - tip.offsetHeight - 14; tip.style.transform = `translate(${x}px, ${y}px)`;
    });
    renderer.domElement.addEventListener('pointerleave', () => { tip.hidden = true; hl.visible = false; });
    renderer.domElement.addEventListener('pointerup', (e) => { if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 4) return; const i = pick(); if (i >= 0) select(inFrame[i]); });
    function pick() { ray.setFromCamera(mouse, camera); const hits = ray.intersectObject(points).filter((h) => pos[h.index * 3 + 1] > -100).sort((a, b) => a.distanceToRay - b.distanceToRay); return hits.length ? hits[0].index : -1; }
    addEventListener('resize', () => { renderer.setSize(innerWidth, innerHeight); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); });
  }

  function decodeTerrain(img) {
    const c = document.createElement('canvas'); c.width = gridW; c.height = gridH; const cx = c.getContext('2d', { willReadFrequently: true }); cx.drawImage(img, 0, 0);
    const d = cx.getImageData(0, 0, gridW, gridH).data; elev = new Float32Array(nv); land = new Uint8Array(nv);
    for (let i = 0; i < nv; i++) { land[i] = d[i * 4 + 2] > 127 ? 1 : 0; elev[i] = land[i] ? Math.max(0, d[i * 4] * 256 + d[i * 4 + 1] - BM.elevationOffset) : 0; }
  }
  const yOf = (m) => m > 0 ? m / 1000 * state.reliefK : SEA_Y;
  function sample(lon, lat) {
    if (!elev) return 0;
    const gx = Math.max(0, Math.min(gridW - 1.001, (lon - LON[0]) / (LON[1] - LON[0]) * (gridW - 1))), gy = Math.max(0, Math.min(gridH - 1.001, (LAT[1] - lat) / (LAT[1] - LAT[0]) * (gridH - 1)));
    const x0 = Math.floor(gx), y0 = Math.floor(gy), fx = gx - x0, fy = gy - y0, i = y0 * gridW + x0;
    if (!land[Math.round(gy) * gridW + Math.round(gx)]) return 0;
    return elev[i] * (1 - fx) * (1 - fy) + elev[i + 1] * fx * (1 - fy) + elev[i + gridW] * (1 - fx) * fy + elev[i + gridW + 1] * fx * fy;
  }
  function updateRelief() { if (!elev) return; for (let v = 0; v < nv; v++) tpos[v * 3 + 1] = land[v] ? yOf(elev[v]) : SEA_Y; tg.attributes.position.needsUpdate = true; tg.computeVertexNormals(); tg.computeBoundingSphere(); }

  function buildCities() {
    cityG.clear(); labelEls.cities.forEach((el) => el.remove()); labelEls.cities = [];
    const t = THEMES[state.theme]; const byCity = d3.group(inFrame, (p) => p.city); const colPts = [];
    for (const [city, ps] of byCity) { const lon = ps[0].lon, lat = ps[0].lat; const ys = d3.extent(ps, (p) => p.year); colPts.push(px(lon), yOf(sample(lon, lat)) + 0.02, pz(lat), px(lon), py(ys[1]), pz(lat)); }
    cityG.add(new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(colPts, 3)), new THREE.LineBasicMaterial({ color: t.column, transparent: true, opacity: 0.5 })));
    cityG.visible = state.columns && state.view !== 'map';
    for (const [city, ps] of byCity) { if (ps.length < 25) continue; const el = document.createElement('div'); el.className = 'city-label'; el.textContent = city; el.dataset.x = px(ps[0].lon); el.dataset.y = yOf(sample(ps[0].lon, ps[0].lat)) + 0.05; el.dataset.z = pz(ps[0].lat); $('labels').append(el); labelEls.cities.push(el); }
  }

  // ---------------------------------------------------------------- colour, filter, selection
  function colorOf(p) {
    const t = THEMES[state.theme], ramp = d3.interpolateRgb(t.rampLo, t.rampHi);
    switch (state.colorBy) {
      case 'scene': return p.scene_id ? sceneColors[p.scene_id - 1] : t.cluster[0];
      case 'cluster': return t.cluster[p.cluster] || t.cluster[0];
      case 'seventh': return ramp(Math.min(1, p.seventh_rate));
      case 'vtoi': return p.V_to_I_share == null ? t.rampLo : ramp(Math.min(1, p.V_to_I_share / 0.9));
      case 'nondia': return ramp(Math.min(1, p.nondiatonic_rate / 0.6));
      default: return t.genre[p.genre];
    }
  }
  function recolor() {
    const t = THEMES[state.theme], c = new THREE.Color(), bg = new THREE.Color(t.bg);
    inFrame.forEach((p, i) => {
      c.set(colorOf(p));
      let w = 1;
      if (state.trace && p.unit !== state.trace) w = Math.min(w, t.dim * 0.6);
      if (state.focus && Math.abs(p.year - state.year) > 10) w = Math.min(w, t.dim);
      if (w < 1) c.lerp(bg, 1 - w);
      col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
    });
    points.geometry.attributes.color.needsUpdate = true;
  }
  function refilter() {
    inFrame.forEach((p, i) => { const on = state.genres.has(p.genre) && (state.view !== 'map' || Math.abs(p.year - state.year) <= 10); pos[i * 3] = basePos[i * 3]; pos[i * 3 + 1] = on ? (state.view === 'map' ? yOf(sample(p.lon, p.lat)) + 0.3 : basePos[i * 3 + 1]) : -999; pos[i * 3 + 2] = basePos[i * 3 + 2]; });
    points.geometry.attributes.position.needsUpdate = true; points.geometry.computeBoundingSphere();
  }
  function drawLegend() {
    const t = THEMES[state.theme], el = $('legend'); el.replaceChildren();
    const item = (color, label) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = color; s.append(i, document.createTextNode(label)); el.append(s); };
    if (state.colorBy === 'genre') for (const g of ['classical', 'jazz', 'rock_pop']) item(t.genre[g], GL[g]);
    else if (state.colorBy === 'cluster') for (let k = 1; k <= 6; k++) item(t.cluster[k], `${k}. ${CL[k]}`);
    else if (state.colorBy === 'scene') scenes.forEach((s, i) => item(sceneColors[i], `${s.scene_id}. ${s.label}`));
    else { const lab = { seventh: ['Seventh-chord share', '0%', '100%'], vtoi: ['V → I share of tonic arrivals', '0%', '90%'], nondia: ['Non-diatonic share', '0%', '60%'] }[state.colorBy]; const s = document.createElement('span'); s.textContent = lab[0]; const r = document.createElement('div'); r.className = 'ramp'; r.style.background = `linear-gradient(90deg, ${t.rampLo}, ${t.rampHi})`; const e = document.createElement('span'); e.textContent = `${lab[1]} → ${lab[2]}`; el.append(s, r, e); }
  }

  function select(p) {
    state.selected = p; const t = THEMES[state.theme]; const c = composers.find((r) => canon(r.unit) === canon(p.composer));
    $('selection').hidden = false; $('selSwatch').style.background = t.cluster[p.cluster] || t.cluster[0];
    $('selName').textContent = `${p.composer} — ${p.title}`;
    $('selMeta').textContent = `${p.city}, ${p.year} · ${GL[p.genre]} · ${ERA(p.year, p.genre)}`;
    $('selText').textContent = `Sevenths ${pct(p.seventh_rate)} · non-diatonic ${pct(p.nondiatonic_rate)} · V→I ${p.V_to_I_share == null ? '—' : pct(p.V_to_I_share)} of tonic arrivals · chord entropy ${d3.format('.2f')(p.chord_entropy)} bits.` + (c ? ` ${c.unit}: ${c.n_pieces} pieces, cluster ${c.harmonic_cluster} (${CL[c.harmonic_cluster]}).` : '') + (p.scene_id ? ` Scene ${p.scene_id}: ${scenes[p.scene_id - 1].label}.` : '') + ` Location confidence: ${p.loc_confidence}.`;
    const mine = inFrame.filter((q) => q.unit === p.unit).sort((a, b) => a.year - b.year);
    $('selChipsLabel').textContent = `${p.unit}: ${mine.length} located pieces`;
    const ch = $('selChips'); ch.replaceChildren();
    const cities = d3.rollups(mine, (v) => [d3.min(v, (q) => q.year), d3.max(v, (q) => q.year), v.length], (q) => q.city);
    for (const [city, [y0, y1, n]] of cities) { const b = document.createElement('button'); b.type = 'button'; b.textContent = `${city} ${y0 === y1 ? y0 : y0 + '–' + y1} (${n})`; b.addEventListener('click', () => setYear(y0)); ch.append(b); }
    $('selTrace').textContent = state.trace === p.unit ? 'Stop tracing' : 'Trace composer';
  }
  function clearSelection() { state.selected = null; state.trace = null; $('selection').hidden = true; recolor(); }

  // ---------------------------------------------------------------- year, timeline
  function setYear(y, instant) {
    state.year = Math.round(Math.max(YEAR[0], Math.min(YEAR[1], y)));
    $('year').textContent = state.year;
    const eras = []; if (state.year <= 1935) eras.push(ERA(state.year, 'classical')); if (state.year >= 1920) eras.push('Jazz: ' + ERA(state.year, 'jazz')); if (state.year >= 1948) eras.push(ERA(state.year, 'rock_pop'));
    $('period').textContent = eras.join(' · ');
    const win = inFrame.filter((p) => Math.abs(p.year - state.year) <= 10 && state.genres.has(p.genre));
    const comps = d3.rollups(win, (v) => v.length, (p) => p.unit).sort((a, b) => b[1] - a[1]).slice(0, 4).map((d) => d[0]);
    $('span').textContent = win.length ? `Most pieces: ${comps.join(', ')}` : 'No located pieces in this window';
    $('stPieces').textContent = fmt(win.length);
    $('stSeventh').textContent = win.length ? pct(d3.mean(win, (p) => p.seventh_rate)) : '—';
    const vi = win.filter((p) => p.V_to_I_share != null); $('stVI').textContent = vi.length ? pct(d3.mean(vi, (p) => p.V_to_I_share)) : '—';
    $('thumb').style.left = `${(state.year - YEAR[0]) / (YEAR[1] - YEAR[0]) * 100}%`; $('thumbLabel').textContent = state.year; $('track').setAttribute('aria-valuenow', state.year);
    if (slicePlane) slicePlane.position.y = py(state.year);
    if (state.focus || state.view === 'map') { recolor(); if (state.view === 'map') refilter(); }
    history.replaceState(null, '', `#year=${state.year}`);
  }
  function buildTimeline() {
    const tk = $('ticks'), hist = $('hist'); const X = (y) => `${(y - YEAR[0]) / (YEAR[1] - YEAR[0]) * 100}%`;
    for (let y = 1550; y <= 2000; y += 50) { const t = document.createElement('div'); t.className = 'tick'; t.style.left = X(y); tk.append(t); if (y % 100 === 0) { const l = document.createElement('div'); l.className = 'tick-label'; l.style.left = X(y); l.textContent = y; tk.append(l); } }
    const dec = d3.rollups(inFrame, (v) => v.length, (p) => Math.floor(p.year / 10) * 10, (p) => p.genre); const max = d3.max(dec, (d) => d3.sum(d[1], (g) => g[1]));
    for (const [y, gs] of dec) { let acc = 0; for (const [g, n] of gs) { const b = document.createElement('div'); b.className = `bar ${g}`; b.style.left = X(y + 5); b.style.height = `${n / max * 100}%`; b.style.bottom = `${acc / max * 100}%`; hist.append(b); acc += n; } }
    const track = $('track'); const fromEvent = (e) => { const r = track.getBoundingClientRect(); return YEAR[0] + Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * (YEAR[1] - YEAR[0]); };
    let drag = false; track.addEventListener('pointerdown', (e) => { drag = true; track.setPointerCapture(e.pointerId); setYear(fromEvent(e)); stopPlay(); });
    track.addEventListener('pointermove', (e) => { if (drag) setYear(fromEvent(e)); }); track.addEventListener('pointerup', () => { drag = false; }); track.addEventListener('pointercancel', () => { drag = false; });
    track.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') setYear(state.year - 10); if (e.key === 'ArrowRight') setYear(state.year + 10); });
    $('play').addEventListener('click', () => (state.playing ? stopPlay() : startPlay()));
  }
  function startPlay() { state.playing = true; $('playIcon').innerHTML = '<path d="M7 5h4v14H7zM13 5h4v14h-4z" fill="currentColor"/>'; if (state.year >= YEAR[1]) setYear(YEAR[0]); playTimer = setInterval(() => { if (state.year >= YEAR[1]) return stopPlay(); setYear(state.year + 5); }, 180); }
  function stopPlay() { state.playing = false; $('playIcon').innerHTML = '<path d="M8 5v14l11-7z" fill="currentColor"/>'; clearInterval(playTimer); playTimer = null; }

  // ---------------------------------------------------------------- views, theme, UI
  function setView(view, instant) {
    state.view = view; document.querySelectorAll('#views button').forEach((b) => b.classList.toggle('on', b.dataset.view === view));
    const wide = innerWidth > 760; const tx = wide ? -3 : 0; // the panel covers the left edge on wide screens, so the cube sits right of centre
    const target = new THREE.Vector3(tx, view === 'map' ? 0.5 : BASE + TIME_H * 0.4, 0);
    let pos3;
    if (view === 'map') pos3 = new THREE.Vector3(tx, 30, 7);
    else if (view === 'profile') pos3 = new THREE.Vector3(tx, BASE + TIME_H * 0.4, 36);
    else pos3 = new THREE.Vector3(tx - 13, 17, 33);
    controls.enableRotate = view !== 'map'; spinIdle = view === 'cube' && instant;
    if (instant) { camera.position.copy(pos3); controls.target.copy(target); controls.update(); } else cameraTween = { t: 0, start: performance.now(), p0: camera.position.clone(), t0: controls.target.clone(), p1: pos3, t1: target };
    slicePlane.visible = view !== 'map'; frameLines.visible = view !== 'map'; cityG.visible = state.columns && view !== 'map'; refilter(); recolor();
  }
  function applyTheme(theme) {
    state.theme = theme; const t = THEMES[theme]; document.documentElement.dataset.theme = theme;
    document.querySelectorAll('#theme button').forEach((b) => b.classList.toggle('on', b.dataset.theme === theme));
    sceneColors = scenes.map((s, i) => d3.hsl((i * 137.508) % 360, 0.62, theme === 'dark' ? 0.62 : 0.42).formatHex());
    labelEls.scenes.forEach((el, i) => el.style.setProperty('--c', sceneColors[i]));
    scene.background = new THREE.Color(t.bg);
    slab.material.forEach((m, i) => m.color.set(i === 2 ? t.slabTop : t.slabSide));
    if (texImgs[theme] && texImgs[theme].complete) { tex.image = texImgs[theme]; tex.needsUpdate = true; }
    frameLines.material.color.set(t.frame); slicePlane.children[0].material.color.set(t.slice); slicePlane.children[1].material.color.set(t.slice);
    hl.material.color.set(t.slice); hemi.intensity = t.hemi; sun.intensity = t.sun;
    buildCities(); recolor(); drawLegend(); if (state.selected) select(state.selected);
    try { localStorage.setItem('hst-theme', theme); } catch (e) { /* storage may be unavailable */ }
  }
  function bindUI() {
    document.querySelectorAll('#views button').forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));
    document.querySelectorAll('#theme button').forEach((b) => b.addEventListener('click', () => applyTheme(b.dataset.theme)));
    document.querySelectorAll('#genres button').forEach((b) => b.addEventListener('click', () => { b.classList.toggle('on'); state.genres = new Set([...document.querySelectorAll('#genres button.on')].map((x) => x.dataset.genre)); refilter(); setYear(state.year); }));
    $('colorBy').addEventListener('change', (e) => { state.colorBy = e.target.value; recolor(); drawLegend(); });
    $('relief').addEventListener('input', (e) => { state.reliefK = e.target.value / 100; $('reliefVal').textContent = `×${Math.round(state.reliefK * KM_PER_UNIT)}`; updateRelief(); buildCities(); if (state.view === 'map') refilter(); });
    $('reliefVal').textContent = `×${Math.round(state.reliefK * KM_PER_UNIT)}`;
    $('focus').addEventListener('change', (e) => { state.focus = e.target.checked; recolor(); });
    $('columns').addEventListener('change', (e) => { state.columns = e.target.checked; cityG.visible = state.columns && state.view !== 'map'; });
    $('sceneLabels').addEventListener('change', (e) => { state.sceneLabels = e.target.checked; });
    $('cityLabels').addEventListener('change', (e) => { state.cityLabels = e.target.checked; });
    $('selClose').addEventListener('click', clearSelection);
    $('selJump').addEventListener('click', () => { if (state.selected) setYear(state.selected.year); });
    $('selTrace').addEventListener('click', () => { if (!state.selected) return; state.trace = state.trace === state.selected.unit ? null : state.selected.unit; $('selTrace').textContent = state.trace ? 'Stop tracing' : 'Trace composer'; recolor(); });
    $('panelToggle').addEventListener('click', () => { const p = $('panel'); p.classList.toggle('collapsed'); $('panelToggle').setAttribute('aria-expanded', String(!p.classList.contains('collapsed'))); });
    addEventListener('keydown', (e) => { if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return; if (e.key === 'ArrowLeft') setYear(state.year - 10); else if (e.key === 'ArrowRight') setYear(state.year + 10); else if (e.key === ' ') { e.preventDefault(); state.playing ? stopPlay() : startPlay(); } else if (e.key === 'Escape') clearSelection(); });
    try { const saved = localStorage.getItem('hst-theme'); if (saved === 'light' || saved === 'dark') state.theme = saved; } catch (e) { /* ignore */ }
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) spinIdle = false;
    if (innerWidth <= 760) { $('panel').classList.add('collapsed'); $('panelToggle').setAttribute('aria-expanded', 'false'); }
  }

  // ---------------------------------------------------------------- frame loop
  const v3 = new THREE.Vector3();
  function project(x, y, z) { v3.set(x, y, z).project(camera); if (v3.z > 1) return null; return [(v3.x + 1) / 2 * innerWidth, (1 - v3.y) / 2 * innerHeight]; }
  function place(el, x, y, z, hidden) { const p = hidden ? null : project(x, y, z); if (!p) { el.style.display = 'none'; return; } el.style.display = ''; el.style.transform = `translate(${p[0]}px, ${p[1]}px) ${el.classList.contains('axis-label') ? 'translate(-100%, -50%)' : el.classList.contains('scene-label') ? 'translate(-4px, -50%)' : 'translate(0, -50%)'}`; }
  function frame() {
    requestAnimationFrame(frame);
    if (cameraTween) { cameraTween.t = Math.min(1, (performance.now() - cameraTween.start) / 700); const k = 1 - Math.pow(1 - cameraTween.t, 3); camera.position.lerpVectors(cameraTween.p0, cameraTween.p1, k); controls.target.lerpVectors(cameraTween.t0, cameraTween.t1, k); if (cameraTween.t >= 1) cameraTween = null; }
    else if (spinIdle && state.view === 'cube') { const o = camera.position.clone().sub(controls.target); const a = 0.0012 * Math.min(3, (performance.now() - (frame.last || performance.now())) / 16.7); const x = o.x * Math.cos(a) - o.z * Math.sin(a), z = o.x * Math.sin(a) + o.z * Math.cos(a); o.x = x; o.z = z; camera.position.copy(controls.target).add(o); }
    frame.last = performance.now();
    controls.update();
    renderer.render(scene, camera);
    // labels
    const x0 = px(LON[0]), z1 = pz(LAT[0]); const isMap = state.view === 'map';
    labelEls.years.forEach((el) => place(el, x0 - 0.2, +el.dataset.y, z1, isMap));
    place(labelEls.now, x0 - 0.2, py(state.year), z1, isMap); labelEls.now.textContent = state.year;
    labelEls.cities.forEach((el) => place(el, +el.dataset.x, +el.dataset.y, +el.dataset.z, !state.cityLabels));
    scenes.forEach((s, i) => place(labelEls.scenes[i], px(s.lon), isMap ? yOf(sample(s.lon, s.lat)) + 0.4 : py(s.year_mid), pz(s.lat), !state.sceneLabels || Math.abs(s.year_mid - state.year) > (isMap ? 40 : 45)));
  }
})();
