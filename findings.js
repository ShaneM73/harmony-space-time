(function () {
  'use strict';
  try { const s = localStorage.getItem('hst-theme'); if (s === 'light' || s === 'dark') document.documentElement.dataset.theme = s; } catch (e) {}
  if (!document.documentElement.dataset.theme) document.documentElement.dataset.theme = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  const themeBtn = document.getElementById('themeBtn');
  const labelTheme = () => { themeBtn.textContent = document.documentElement.dataset.theme === 'dark' ? 'Light theme' : 'Dark theme'; };
  themeBtn.addEventListener('click', () => { document.documentElement.dataset.theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; try { localStorage.setItem('hst-theme', document.documentElement.dataset.theme); } catch (e) {} labelTheme(); dispatchEvent(new Event('resize')); });
  labelTheme();
  fetch('data/harmony_data.json').then((r) => r.json()).then((DATA) => {
  const pieces = DATA.pieces, scenes = DATA.scenes, composers = DATA.composers;
  const GC = { classical: 'var(--classical)', jazz: 'var(--jazz)', rock_pop: 'var(--rock)' };
  const GL = { classical: 'Classical', jazz: 'Jazz', rock_pop: 'Rock & pop' };
  const CL = ['', 'Bebop to contemporary jazz', 'Chromatic, extended (Bartók, post-bop)', 'Triadic, plagal (pre-tonal and 1960s–80s pop)', 'bVII and step-driven rock', 'Dominant-seventh diatonic (early jazz, rock and roll, R&B)', 'Common practice (Corelli to Rachmaninoff)'];
  const CLC = ['#9aa0a6', '#b7791f', '#7c3aed', '#0f766e', '#c2410c', '#d97706', '#2f5fd0'];
  const SCENE_COL = scenes.map((s, i) => d3.hsl((i * 137.508) % 360, 0.62, 0.5).formatHex());
  const pct = d3.format('.0%'), pct1 = d3.format('.1%'), fmt = d3.format(',');
  const txt = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  txt('t-pieces', fmt(DATA.eras.reduce((s, e) => s + e.n_pieces, 0)));
  txt('t-chords', fmt(DATA.eras.reduce((s, e) => s + e.n_chords, 0)));
  txt('t-located', fmt(pieces.length)); txt('t-scenes', scenes.length); txt('t-units', composers.length);
  /* ------------------------------------------------------------------ 2D charts (d3) */
  const tipFor = (host) => { let t = host.querySelector('.tip'); if (!t) { t = document.createElement('div'); t.className = 'tip'; t.hidden = true; host.append(t); } return { show(ev, html) { t.textContent = html; t.hidden = false; const r = host.getBoundingClientRect(); let x = ev.clientX - r.left + 12, y = ev.clientY - r.top + 12; if (x + t.offsetWidth > r.width) x = Math.max(0, ev.clientX - r.left - t.offsetWidth - 12); t.style.left = x + 'px'; t.style.top = y + 'px'; }, hide() { t.hidden = true; } }; };
  const axisStyle = (a) => { a.select('.domain').remove(); a.selectAll('line').attr('stroke', 'var(--line)'); a.attr('font-size', null).attr('font-family', null); };
  function timeSeries(id, specs, opts = {}) {
    const el = document.getElementById(id); if (!el) return;
    const draw = () => {
      const W = Math.max(280, el.clientWidth), H = opts.height || 250, ml = 42, mr = 10, mt = 8, mb = 24;
      const all = specs.map((s) => ({ ...s, pts: DATA.series.filter((r) => r.genre === s.genre && r[s.metric] != null).map((r) => ({ x: r.bin_mid, y: r[s.metric], lo: r[s.metric + '_lo'], hi: r[s.metric + '_hi'], period: r.period, n: r.n_pieces })) })).filter((s) => s.pts.length);
      el.replaceChildren();
      const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`);
      const ymax = opts.ymax ?? Math.min(1, d3.max(all, (s) => d3.max(s.pts, (p) => p.hi ?? p.y)) * 1.1);
      const x = d3.scaleLinear([opts.xmin ?? 1560, opts.xmax ?? 2010], [ml, W - mr]), y = d3.scaleLinear([0, ymax], [H - mb, mt]);
      svg.append('g').attr('transform', `translate(${ml},0)`).call(d3.axisLeft(y).ticks(4).tickFormat(pct).tickSize(-(W - ml - mr))).call(axisStyle).selectAll('text').attr('x', -6);
      svg.append('g').attr('transform', `translate(0,${H - mb})`).call(d3.axisBottom(x).ticks(Math.max(3, Math.floor(W / 90))).tickFormat(d3.format('d')).tickSize(0)).call((a) => { a.select('.domain').attr('stroke', 'var(--muted)'); a.attr('font-size', null).attr('font-family', null); a.selectAll('text').attr('dy', '1.1em'); });
      const area = d3.area().x((p) => x(p.x)).y0((p) => y(p.lo)).y1((p) => y(p.hi)); const ln = d3.line().x((p) => x(p.x)).y((p) => y(p.y));
      const T = tipFor(el);
      for (const s of all) {
        if (s.pts.every((p) => p.lo != null)) svg.append('path').attr('d', area(s.pts)).attr('fill', s.color).attr('fill-opacity', 0.14);
        svg.append('path').attr('d', ln(s.pts)).attr('fill', 'none').attr('stroke', s.color).attr('stroke-width', 2).attr('stroke-linecap', 'round').attr('stroke-linejoin', 'round');
        svg.append('g').selectAll('circle').data(s.pts).join('circle').attr('cx', (p) => x(p.x)).attr('cy', (p) => y(p.y)).attr('r', 3).attr('fill', s.color)
          .on('pointermove', (ev, p) => T.show(ev, `${s.label} ${p.period}: ${pct1(p.y)} (${p.n} pieces)`)).on('pointerleave', () => T.hide());
      }
    };
    draw(); new ResizeObserver(draw).observe(el); addEventListener('resize', draw);
  }
  const byGenre = (metric) => Object.keys(GC).map((g) => ({ genre: g, metric, label: GL[g], color: GC[g] }));
  timeSeries('ch-seventh', byGenre('seventh_rate'), { ymax: 1 });
  timeSeries('ch-extended', byGenre('extended_rate'));
  timeSeries('ch-nondiatonic', byGenre('nondiatonic_rate'));
  timeSeries('ch-vtoi-genre', byGenre('V_to_I_share'), { ymax: 1 });
  timeSeries('ch-resolution', byGenre('dom_resolution'), { ymax: 1 });
  const cad = (genre, c0) => [['V_to_I_share', 'V → I', c0], ['IV_to_I_share', 'IV → I', 'var(--iv)'], ['bVII_to_I_share', 'bVII → I', 'var(--bvii)']].map(([m, l, c]) => ({ genre, metric: m, label: l, color: c }));
  timeSeries('ch-cad-classical', cad('classical', GC.classical), { ymax: 0.8, xmin: 1560, xmax: 1940 });
  timeSeries('ch-cad-rock', cad('rock_pop', GC.rock_pop), { ymax: 0.8, xmin: 1945, xmax: 2005 });

  function eraBars(id, metric, f, opts = {}) {
    const el = document.getElementById(id); if (!el) return;
    const draw = () => {
      const rows = DATA.eras.filter((r) => r[metric] != null).sort((a, b) => a.order - b.order);
      const W = Math.max(280, el.clientWidth), rh = 22, mt = 4, mb = 22, H = mt + rows.length * rh + mb;
      el.replaceChildren(); const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`);
      const ml = Math.min(W * 0.45, 170);
      const x = d3.scaleLinear([0, d3.max(rows, (r) => r[metric]) * 1.12], [ml, W - 36]); const y = d3.scaleBand(rows.map((r) => r.era), [mt, H - mb]).padding(0.25);
      svg.append('g').attr('transform', `translate(0,${H - mb})`).call(d3.axisBottom(x).ticks(4).tickFormat(f).tickSize(-(H - mb - mt))).call(axisStyle).selectAll('text').attr('dy', '1.1em');
      const row = svg.append('g').selectAll('g').data(rows).join('g').attr('transform', (r) => `translate(0,${y(r.era)})`);
      row.append('text').attr('x', ml - 8).attr('y', y.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text((r) => r.era.length > 26 ? r.era.slice(0, 24) + '…' : r.era);
      row.append('rect').attr('x', x(0)).attr('width', (r) => x(r[metric]) - x(0)).attr('height', y.bandwidth()).attr('rx', 2).attr('fill', (r) => GC[r.genre]);
      row.append('text').attr('class', 'lbl').attr('x', (r) => x(r[metric]) + 6).attr('y', y.bandwidth() / 2).attr('dy', '0.35em').text((r) => f(r[metric]));
    };
    draw(); new ResizeObserver(draw).observe(el); addEventListener('resize', draw);
  }
  eraBars('ch-vocab', 'vocab40', d3.format('.1f')); eraBars('ch-entropy', 'transition_entropy', d3.format('.2f'));

  // root motion stacked bars
  (function () {
    const el = document.getElementById('ch-motion'); const key = document.getElementById('key-motion'); if (!el || !key) return;
    const M = [['down5th_share', 'Descending fifth', 'var(--classical)'], ['step_share', 'Step', 'var(--rock)'], ['third_share', 'Third', 'var(--iv)']];
    key.replaceChildren(...M.map(([k, l, c]) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = c; s.append(i, document.createTextNode(l)); return s; }));
    const draw = () => {
      const rows = DATA.eras.slice().sort((a, b) => a.order - b.order);
      const W = Math.max(280, el.clientWidth), rh = 22, mt = 4, mb = 22, H = mt + rows.length * rh + mb;
      el.replaceChildren(); const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`);
      const ml = Math.min(W * 0.45, 170); const x = d3.scaleLinear([0, 1], [ml, W - 8]); const y = d3.scaleBand(rows.map((r) => r.era), [mt, H - mb]).padding(0.2);
      svg.append('g').attr('transform', `translate(0,${H - mb})`).call(d3.axisBottom(x).ticks(5).tickFormat(pct).tickSize(0)).call((a) => { a.select('.domain').attr('stroke', 'var(--muted)'); a.attr('font-size', null).attr('font-family', null); a.selectAll('text').attr('dy', '1.1em'); });
      const T = tipFor(el);
      for (const r of rows) { const g = svg.append('g').attr('transform', `translate(0,${y(r.era)})`); g.append('text').attr('x', ml - 8).attr('y', y.bandwidth() / 2).attr('dy', '0.35em').attr('text-anchor', 'end').text(r.era.length > 26 ? r.era.slice(0, 24) + '…' : r.era); let acc = 0; for (const [k, l, c] of M) { const v = r[k] || 0; g.append('rect').attr('x', x(acc)).attr('width', Math.max(0, x(acc + v) - x(acc))).attr('height', y.bandwidth()).attr('fill', c).on('pointermove', (ev) => T.show(ev, `${r.era}: ${l} ${pct1(v)}`)).on('pointerleave', () => T.hide()); acc += v; } g.append('text').attr('class', 'lbl').attr('x', x(0) + 4).attr('y', y.bandwidth() / 2).attr('dy', '0.35em').attr('fill', 'var(--bg)').text(pct(r.down5th_share)); }
    };
    draw(); new ResizeObserver(draw).observe(el); addEventListener('resize', draw);
  })();

  // top chords / progressions table
  (function () {
    const tb = document.querySelector('#tbl-top tbody'); if (!tb) return;
    const eras = DATA.eras.slice().sort((a, b) => a.order - b.order);
    for (const e of eras) { const tr = document.createElement('tr'); const td = (t) => { const d = document.createElement('td'); d.textContent = t; tr.append(d); }; td(e.era); td(DATA.top_chords.filter((r) => r.era === e.era && r.rank <= 6).map((r) => `${r.chord} ${pct(r.share)}`).join(', ')); td(DATA.transitions.filter((r) => r.era === e.era && r.rank <= 4).map((r) => `${r.progression} ${pct1(r.share)}`).join(', ')); tb.append(tr); }
  })();

  // composer map
  (function () {
    const el = document.getElementById('ch-map'); const key = document.getElementById('key-clusters'); if (!el || !key) return;
    key.replaceChildren(...[1, 2, 3, 4, 5, 6].map((k) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = CLC[k]; s.append(i, document.createTextNode(`${k}. ${CL[k]}`)); return s; }));
    const draw = () => {
      const W = Math.max(300, el.clientWidth), H = 460, m = 18; el.replaceChildren();
      const svg = d3.select(el).append('svg').attr('viewBox', `0 0 ${W} ${H}`);
      const x = d3.scaleLinear(d3.extent(composers, (r) => r.pc1), [m + 10, W - m - 10]).nice(), y = d3.scaleLinear(d3.extent(composers, (r) => r.pc2), [H - m - 10, m + 10]).nice();
      svg.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', m).attr('y2', H - m).attr('stroke', 'var(--line)'); svg.append('line').attr('y1', y(0)).attr('y2', y(0)).attr('x1', m).attr('x2', W - m).attr('stroke', 'var(--line)');
      svg.append('text').attr('x', W - m).attr('y', y(0) - 6).attr('text-anchor', 'end').text('sevenths, descending fifths →'); svg.append('text').attr('x', x(0) + 6).attr('y', m + 10).text('↑ extensions, chromaticism, steps');
      const T = tipFor(el);
      const g = svg.append('g').selectAll('g').data(composers).join('g').attr('transform', (r) => `translate(${x(r.pc1)},${y(r.pc2)})`);
      g.each(function (r) { const s = d3.select(this), c = CLC[r.harmonic_cluster]; if (r.genre === 'classical') s.append('circle').attr('r', 4.5).attr('fill', c); else if (r.genre === 'jazz') s.append('rect').attr('x', -4).attr('y', -4).attr('width', 8).attr('height', 8).attr('fill', c); else s.append('path').attr('d', 'M0,-5.5 L5,3.5 L-5,3.5 Z').attr('fill', c); });
      g.on('pointermove', (ev, r) => T.show(ev, `${r.unit} (${r.city}, c. ${Math.round(r.year)}, ${r.n_pieces} pieces) — sevenths ${pct(r.seventh_rate)}, non-diatonic ${pct(r.nondiatonic_rate)}, V→I ${pct(r.V_to_I_share)}`)).on('pointerleave', () => T.hide());
      const labs = svg.append('g').selectAll('text').data(composers.filter((r) => r.n_pieces >= 15)).join('text').attr('class', 'lbl').attr('font-size', 11).attr('x', (r) => x(r.pc1) + 6).attr('y', (r) => y(r.pc2) + 3).text((r) => r.unit.replace(/^The /, ''));
      const nodes = labs.nodes(); for (let pass = 0; pass < 12; pass++) { let moved = false; for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) { const a = nodes[i].getBBox(), b = nodes[j].getBBox(); if (a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height) { const lower = a.y > b.y ? nodes[i] : nodes[j]; lower.setAttribute('y', +lower.getAttribute('y') + 11); moved = true; } } if (!moved) break; }
    };
    draw(); new ResizeObserver(draw).observe(el); addEventListener('resize', draw);
    const lists = document.getElementById('cluster-lists'); if (!lists) return;
    for (let k = 1; k <= 6; k++) { const d = document.createElement('div'); d.className = 'c'; d.style.borderColor = CLC[k]; const b = document.createElement('b'); b.textContent = `${k}. ${CL[k]}`; d.append(b, document.createTextNode(composers.filter((r) => r.harmonic_cluster === k).sort((a, b) => a.year - b.year).map((r) => `${r.unit} (${Math.round(r.year)})`).join(' · '))); lists.append(d); }
  })();

  // scenes + mantel tables
  (function () {
    const tb = document.querySelector('#tbl-scenes tbody'); if (!tb) return;
    for (const s of scenes) { const tr = document.createElement('tr'); const td = (t, cls) => { const d = document.createElement('td'); if (cls) d.className = cls; d.textContent = t; tr.append(d); return d; }; const c = td(s.scene); c.style.borderLeft = `4px solid ${SCENE_COL[s.scene_id - 1]}`; td(s.n_pieces, 'num'); td(GL[s.genre]); td(s.top_composers); td(pct(s.seventh_rate), 'num'); td(pct(s.nondiatonic_rate), 'num'); td(pct(s.V_to_I_share), 'num'); td(pct(s.down5th_share), 'num'); td(s.harmonic_group, 'num'); tb.append(tr); }
    const mb = document.querySelector('#tbl-mantel tbody'); const f2 = d3.format('.2f'), fp = (v) => v < 0.001 ? '<0.001' : d3.format('.3f')(v);
    for (const r of DATA.mantel) { const tr = document.createElement('tr'); const td = (t, cls, strong) => { const d = document.createElement('td'); if (cls) d.className = cls; d.textContent = t; if (strong) d.style.fontWeight = '600'; tr.append(d); }; td(r.subset); td(r.n_units, 'num'); td(f2(r.r_harmony_time), 'num', r.p_time < 0.05); td(fp(r.p_time), 'num'); td(f2(r.r_harmony_geo), 'num', r.p_geo < 0.05); td(fp(r.p_geo), 'num'); td(f2(r.r_geo_given_time), 'num', r.p_geo_given_time < 0.05); td(fp(r.p_geo_given_time), 'num'); td(f2(r.r_time_given_geo), 'num', r.p_time_given_geo < 0.05); td(fp(r.p_time_given_geo), 'num'); mb.append(tr); }
  })();
  });
})();
