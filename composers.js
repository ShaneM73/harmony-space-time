/* Harmonic Map of Composers — 3D scatter of composers/artists in factor (or PCA) space. */
(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const CL = ['', 'Bebop to contemporary jazz', 'Chromatic, extended', 'Triadic, plagal', 'bVII and step-driven rock', 'Dominant-seventh diatonic', 'Common practice'];
  const CL_LONG = ['', 'Bebop to contemporary jazz', 'Chromatic, extended (Bartók, Schulhoff, post-bop)', 'Triadic, plagal (pre-tonal polyphony and 1960s–80s pop)', 'bVII and step-driven rock', 'Dominant-seventh diatonic (early jazz, rock and roll, R&B)', 'Common practice (Corelli to Rachmaninoff)'];
  const GL = { classical: 'Classical', jazz: 'Jazz', rock_pop: 'Rock & pop' };
  const THEMES = {
    light: { bg: '#f3f2ee', grid: '#d6d3ca', axis: '#9aa0a6', cl: ['#9aa0a6', '#b7791f', '#7c3aed', '#0f766e', '#c2410c', '#d97706', '#2f5fd0'], genre: { classical: '#2f5fd0', jazz: '#b7791f', rock_pop: '#c2410c' }, lo: '#c9ccd1', hi: '#d9480f' },
    dark: { bg: '#14171a', grid: '#2b3036', axis: '#5c6570', cl: ['#5c6579', '#f2b134', '#c38fe6', '#79c99e', '#e8737a', '#f08a4b', '#7fb3e6'], genre: { classical: '#7aa2ff', jazz: '#f2b134', rock_pop: '#ff8a5c' }, lo: '#3a4663', hi: '#ff7a45' },
  };
  const S = 5; // half-size of the box in world units
  const state = { theme: 'dark', axes: 'fa', colorBy: 'cluster', on: new Set([1, 2, 3, 4, 5, 6]), allNames: false, drops: true, centres: true, sel: null, hover: null };
  try { const t = localStorage.getItem('hst-theme'); if (t === 'light' || t === 'dark') state.theme = t; } catch (e) { /* ignore */ }

  let D, comps, renderer, scene, camera, controls, meshes = [], drops, frame3, centreEls = [], nameEls = [], axisEls = [], scale = {};
  let tween = null;

  fetch('data/composer_space.json').then((r) => r.json()).then((d) => {
    D = d; comps = d.composers;
    for (const k of ['fa', 'pca']) { scale[k] = [0, 1, 2].map((j) => d3.max(comps, (c) => Math.abs(c[k][j])) * 1.05); }
    try { build(); } catch (e) { console.error(e); $('loading').hidden = true; const n = document.createElement('div'); n.className = 'nowebgl'; n.textContent = 'This map needs WebGL, which this browser or view does not provide.'; document.body.append(n); return; }
    panel(); applyTheme(state.theme); setAxes('fa', true); $('loading').hidden = true; loop();
  }).catch((e) => { console.error(e); $('loading').textContent = 'Could not load data/composer_space.json. Serve the page over HTTP.'; });

  const posOf = (c, k) => new THREE.Vector3(c[k][0] / scale[k][0] * S, c[k][2] / scale[k][2] * S, -c[k][1] / scale[k][1] * S); // x = axis 1, up = axis 3, depth = axis 2

  function build() {
    renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(innerWidth, innerHeight); $('scene').append(renderer.domElement);
    scene = new THREE.Scene(); camera = new THREE.PerspectiveCamera(38, innerWidth / innerHeight, 0.1, 300);
    const wide = innerWidth > 760; camera.position.set(wide ? 10 : 12, 8, 19);
    controls = new THREE.OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.dampingFactor = 0.08; controls.minDistance = 4; controls.maxDistance = 60;
    controls.target.set(wide ? -2.2 : 0, 0, 0);
    scene.add(new THREE.HemisphereLight(0xffffff, 0x666a70, 0.9)); const sun = new THREE.DirectionalLight(0xffffff, 0.7); sun.position.set(6, 10, 8); scene.add(sun);
    // frame: floor grid, box edges, three axes through the origin
    const gp = []; for (let i = -S; i <= S + 1e-6; i += S / 4) { gp.push(-S, -S, i, S, -S, i, i, -S, -S, i, -S, S); }
    const box = []; for (const y of [-S, S]) box.push(-S, y, -S, S, y, -S, S, y, -S, S, y, S, S, y, S, -S, y, S, -S, y, S, -S, y, -S); for (const [x, z] of [[-S, -S], [S, -S], [S, S], [-S, S]]) box.push(x, -S, z, x, S, z);
    frame3 = { grid: new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(gp, 3)), new THREE.LineBasicMaterial({ transparent: true, opacity: 0.6 })),
      box: new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(box, 3)), new THREE.LineBasicMaterial({ transparent: true, opacity: 0.5 })),
      axes: new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute([-S, 0, 0, S, 0, 0, 0, -S, 0, 0, S, 0, 0, 0, -S, 0, 0, S], 3)), new THREE.LineBasicMaterial({ transparent: true, opacity: 0.9 })) };
    scene.add(frame3.grid, frame3.box, frame3.axes);
    // composers
    const geo = { classical: new THREE.SphereGeometry(1, 20, 14), jazz: new THREE.BoxGeometry(1.6, 1.6, 1.6), rock_pop: new THREE.ConeGeometry(1.05, 1.9, 4) };
    comps.forEach((c, i) => {
      const m = new THREE.Mesh(geo[c.genre], new THREE.MeshLambertMaterial({ transparent: true }));
      const r = 0.08 + 0.04 * Math.log2(c.n); m.scale.setScalar(r); m.userData = { i, r }; scene.add(m); meshes.push(m);
    });
    drops = new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(comps.length * 6), 3)).setAttribute('color', new THREE.Float32BufferAttribute(new Float32Array(comps.length * 6), 3)), new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.45 }));
    scene.add(drops);
    // labels
    const L = $('labels');
    for (let k = 1; k <= 6; k++) { const el = document.createElement('div'); el.className = 'clabel'; el.textContent = `${k} · ${CL[k]}`; L.append(el); centreEls.push(el); }
    comps.forEach((c) => { const el = document.createElement('div'); el.className = 'nlabel'; el.textContent = c.unit.replace(/^The /, ''); L.append(el); nameEls.push(el); });
    for (let j = 0; j < 6; j++) { const el = document.createElement('div'); el.className = 'axlabel'; L.append(el); axisEls.push(el); }
    // interaction
    const ray = new THREE.Raycaster(), mouse = new THREE.Vector2(), tip = $('tooltip'); let down = null;
    const pick = () => { ray.setFromCamera(mouse, camera); const h = ray.intersectObjects(meshes.filter((m) => m.visible)); return h.length ? h[0].object.userData.i : -1; };
    renderer.domElement.addEventListener('pointerdown', (e) => { down = [e.clientX, e.clientY]; });
    renderer.domElement.addEventListener('pointermove', (e) => {
      mouse.x = e.clientX / innerWidth * 2 - 1; mouse.y = -(e.clientY / innerHeight) * 2 + 1; const i = pick(); state.hover = i >= 0 ? i : null;
      if (i < 0) { tip.hidden = true; renderer.domElement.style.cursor = ''; return; }
      const c = comps[i]; renderer.domElement.style.cursor = 'pointer'; tip.replaceChildren(); const b = document.createElement('b'); b.textContent = c.unit; const s = document.createElement('span'); s.textContent = `${GL[c.genre]} · ${c.city}, c. ${c.year} · ${c.n} pieces · cluster ${c.cluster}`; tip.append(b, s); tip.hidden = false;
      let x = e.clientX + 14, y = e.clientY + 14; if (x + tip.offsetWidth > innerWidth - 8) x = e.clientX - tip.offsetWidth - 14; if (y + tip.offsetHeight > innerHeight - 8) y = e.clientY - tip.offsetHeight - 14; tip.style.transform = `translate(${x}px, ${y}px)`;
    });
    renderer.domElement.addEventListener('pointerleave', () => { tip.hidden = true; state.hover = null; });
    renderer.domElement.addEventListener('pointerup', (e) => { if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 4) return; const i = pick(); if (i >= 0) select(i); });
    addEventListener('resize', () => { renderer.setSize(innerWidth, innerHeight); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); });
    addEventListener('keydown', (e) => { if (e.key === 'Escape') clearSel(); });
  }

  function colorOf(c) {
    const t = THEMES[state.theme], ramp = d3.interpolateRgb(t.lo, t.hi);
    if (state.colorBy === 'genre') return t.genre[c.genre];
    if (state.colorBy === 'year') return d3.interpolateRgb(t.lo, t.hi)((c.year - 1560) / 440);
    if (state.colorBy === 'conf') return ramp(c.conf);
    return t.cl[c.cluster];
  }
  function restyle() {
    const t = THEMES[state.theme], col = drops.geometry.attributes.color.array, cc = new THREE.Color();
    comps.forEach((c, i) => {
      const m = meshes[i]; const on = state.on.has(c.cluster); m.visible = on;
      m.material.color.set(colorOf(c)); m.material.opacity = c.conf < 0.5 && state.colorBy === 'cluster' ? 0.45 : 0.95;
      m.material.emissive = new THREE.Color(state.sel === i ? t.hi : '#000000'); m.material.emissiveIntensity = state.sel === i ? 0.5 : 0;
      cc.set(on ? colorOf(c) : t.bg); for (let k = 0; k < 2; k++) { col[i * 6 + k * 3] = cc.r; col[i * 6 + k * 3 + 1] = cc.g; col[i * 6 + k * 3 + 2] = cc.b; }
    });
    drops.geometry.attributes.color.needsUpdate = true; drops.visible = state.drops;
    document.querySelectorAll('#clist button').forEach((b) => { const k = +b.dataset.k; b.classList.toggle('off', !state.on.has(k)); b.querySelector('i').style.background = t.cl[k]; });
    centreEls.forEach((el, k) => el.style.setProperty('--c', t.cl[k + 1]));
  }
  function placeAll(k, f) { // f in [0,1] for tweening from the other axes system
    const other = k === 'fa' ? 'pca' : 'fa'; const pa = drops.geometry.attributes.position.array;
    comps.forEach((c, i) => { const p = f < 1 ? posOf(c, other).lerp(posOf(c, k), f) : posOf(c, k); meshes[i].position.copy(p); pa.set([p.x, p.y, p.z, p.x, -S, p.z], i * 6); });
    drops.geometry.attributes.position.needsUpdate = true; drops.geometry.computeBoundingSphere();
  }
  function setAxes(k, instant) {
    state.axes = k; document.querySelectorAll('#axes button').forEach((b) => b.classList.toggle('on', b.dataset.axes === k));
    if (instant) placeAll(k, 1); else tween = { k, start: performance.now() };
    const A = D[k]; const names = k === 'fa' ? A.axes : A.axes.map((a, j) => `${a} (${Math.round(A.explained[j] * 100)}%)`);
    const poles = k === 'fa' ? A.poles : [['−', '+'], ['−', '+'], ['−', '+']];
    axisEls.forEach((el, j) => { const ax = Math.floor(j / 2), pos = j % 2; el.replaceChildren(); if (pos) { const b = document.createElement('b'); b.textContent = '+ ' + names[ax]; el.append(b); el.title = poles[ax][1]; } else el.append(document.createTextNode('− ' + poles[ax][0])); el.dataset.ax = ax; el.dataset.pos = pos; });
    // loadings table
    const tb = $('loadings'); tb.replaceChildren(); const L = A.loadings; const t = THEMES[state.theme];
    const hdr = document.createElement('tr'); for (const h of ['', ...(k === 'fa' ? ['F1', 'F2', 'F3'] : ['PC1', 'PC2', 'PC3'])]) { const td = document.createElement('td'); td.textContent = h; td.style.fontWeight = '600'; hdr.append(td); } tb.append(hdr);
    D.features.forEach((f, r) => { const tr = document.createElement('tr'); const n = document.createElement('td'); n.textContent = f; tr.append(n); for (let j = 0; j < 3; j++) { const v = L[r][j]; const td = document.createElement('td'); const bar = document.createElement('span'); bar.className = 'bar'; bar.style.width = `${Math.abs(v) * 34}px`; bar.style.background = v >= 0 ? t.hi : t.axis; bar.style.opacity = Math.abs(v) >= 0.4 ? 1 : 0.45; td.append(bar, document.createTextNode(' ' + (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(2))); tr.append(td); } tb.append(tr); });
    $('loadTitle').textContent = k === 'fa' ? 'Factor loadings (varimax)' : 'PCA loadings';
  }
  function select(i) {
    state.sel = i; const c = comps[i], t = THEMES[state.theme]; $('selection').hidden = false; $('selSwatch').style.background = t.cl[c.cluster];
    $('selName').textContent = c.unit; $('selMeta').textContent = `${GL[c.genre]} · ${c.city}, c. ${c.year} · ${c.n} pieces`;
    const v = c.vals, p = (x) => x == null ? '—' : `${Math.round(x * 100)}%`;
    $('selText').textContent = `Cluster ${c.cluster}: ${CL_LONG[c.cluster]}. Stays with this group in ${Math.round(c.conf * 100)}% of bootstrap re-runs. Sevenths ${p(v['sevenths'])}, non-diatonic ${p(v['non-diatonic'])}, V → I ${p(v['V → I'])}, IV → I ${p(v['IV → I'])}, descending fifths ${p(v['descending fifths'])}, steps ${p(v['step motion'])}.`;
    const nb = $('selNear'); nb.replaceChildren(); for (const u of c.near) { const j = comps.findIndex((x) => x.unit === u); const b = document.createElement('button'); b.type = 'button'; b.textContent = `${u} (${comps[j].cluster})`; b.addEventListener('click', () => select(j)); nb.append(b); }
    restyle();
  }
  function clearSel() { state.sel = null; $('selection').hidden = true; restyle(); }
  function applyTheme(th) {
    state.theme = th; const t = THEMES[th]; document.documentElement.dataset.theme = th; document.querySelectorAll('#theme button').forEach((b) => b.classList.toggle('on', b.dataset.theme === th));
    scene.background = new THREE.Color(t.bg); frame3.grid.material.color.set(t.grid); frame3.box.material.color.set(t.grid); frame3.axes.material.color.set(t.axis);
    try { localStorage.setItem('hst-theme', th); } catch (e) { /* ignore */ }
    restyle(); if (D) setAxes(state.axes, true); if (state.sel != null) select(state.sel);
  }
  function panel() {
    const s = D.stats; $('method').textContent = `Groups: Ward clustering on all 14 standardised harmonic features. Axes: varimax factor analysis (or PCA) of the same features, for display only. Silhouette ${s.silhouette['6'].toFixed(2)}; bootstrap agreement ${s.bootstrap_ari_mean.toFixed(2)} — overlapping regions of a continuum, not islands.`;
    const cl = $('clist'); for (let k = 1; k <= 6; k++) { const b = document.createElement('button'); b.type = 'button'; b.dataset.k = k; const n = comps.filter((c) => c.cluster === k); const conf = d3.mean(n, (c) => c.conf); b.title = CL_LONG[k];
      b.append(Object.assign(document.createElement('i')), document.createTextNode(`${k}. ${CL[k]}`), Object.assign(document.createElement('em'), { textContent: `${n.length} · ${Math.round(conf * 100)}%` }));
      let timer = null; b.addEventListener('click', () => { clearTimeout(timer); timer = setTimeout(() => { state.on.has(k) ? state.on.delete(k) : state.on.add(k); if (!state.on.size) state.on = new Set([1, 2, 3, 4, 5, 6]); restyle(); }, 220); });
      b.addEventListener('dblclick', () => { clearTimeout(timer); state.on = state.on.size === 1 && state.on.has(k) ? new Set([1, 2, 3, 4, 5, 6]) : new Set([k]); restyle(); });
      cl.append(b); }
    $('foot').textContent = 'The number after each cluster is its size and the mean share of bootstrap re-runs in which its members stay together. Faded markers are border members (below 50%). Marker size grows with the logarithm of the number of analysed pieces.';
    document.querySelectorAll('#axes button').forEach((b) => b.addEventListener('click', () => setAxes(b.dataset.axes)));
    document.querySelectorAll('#theme button').forEach((b) => b.addEventListener('click', () => applyTheme(b.dataset.theme)));
    $('colorBy').addEventListener('change', (e) => { state.colorBy = e.target.value; restyle(); });
    $('allNames').addEventListener('change', (e) => { state.allNames = e.target.checked; });
    $('drops').addEventListener('change', (e) => { state.drops = e.target.checked; restyle(); });
    $('centres').addEventListener('change', (e) => { state.centres = e.target.checked; });
    $('selClose').addEventListener('click', clearSel);
    $('panelToggle').addEventListener('click', () => { const p = $('panel'); p.classList.toggle('collapsed'); $('panelToggle').setAttribute('aria-expanded', String(!p.classList.contains('collapsed'))); });
    if (innerWidth <= 760) { $('panel').classList.add('collapsed'); $('panelToggle').setAttribute('aria-expanded', 'false'); }
  }

  const v3 = new THREE.Vector3();
  function project(p) { v3.copy(p).project(camera); if (v3.z > 1 || Math.abs(v3.x) > 1.2 || Math.abs(v3.y) > 1.2) return null; return [(v3.x + 1) / 2 * innerWidth, (1 - v3.y) / 2 * innerHeight]; }
  function put(el, p, dx, dy, show) { const q = show ? project(p) : null; if (!q) { el.style.display = 'none'; return; } el.style.display = ''; el.style.transform = `translate(${q[0] + dx}px, ${q[1] + dy}px)`; }
  function loop() {
    requestAnimationFrame(loop);
    if (tween) { const f = Math.min(1, (performance.now() - tween.start) / 650); placeAll(tween.k, 1 - Math.pow(1 - f, 3)); if (f >= 1) tween = null; }
    controls.update(); renderer.render(scene, camera);
    // axis ends: x = axis 1, depth = axis 2 (negative z), up = axis 3
    const ends = [[new THREE.Vector3(-S, 0, 0), new THREE.Vector3(S, 0, 0)], [new THREE.Vector3(0, 0, S), new THREE.Vector3(0, 0, -S)], [new THREE.Vector3(0, -S, 0), new THREE.Vector3(0, S, 0)]];
    axisEls.forEach((el) => { const ax = +el.dataset.ax, pos = +el.dataset.pos; put(el, ends[ax][pos].clone().multiplyScalar(1.06), 6, -8, true); });
    for (let k = 1; k <= 6; k++) { const n = comps.map((c, i) => [c, i]).filter(([c]) => c.cluster === k); const m = new THREE.Vector3(); n.forEach(([, i]) => m.add(meshes[i].position)); m.divideScalar(n.length); put(centreEls[k - 1], m, -10, -26, state.centres && state.on.has(k)); }
    comps.forEach((c, i) => { const show = state.on.has(c.cluster) && (state.allNames || c.n >= 15 || state.sel === i || state.hover === i); const el = nameEls[i]; el.classList.toggle('sel', state.sel === i); put(el, meshes[i].position, 8, -6, show); });
  }
})();
