// THE FILM: Good News Toons ep005. Every visual is a pure function of t, timed from score.js.
(function () {
  const U = globalThis.U, G = globalThis.G, Ch = globalThis.Ch, S = globalThis.SCORE, Studio = globalThis.Studio;
  const Shots = globalThis.Shots, Subs = globalThis.Subs, Data = globalThis.Data, UI = globalThis.UI;
  const { ev, BEAT, shotAt: A } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H, SAFE = G.SAFE;
  const CX = SAFE.x + SAFE.w / 2;            // 500: the centre of the safe column (the right edge belongs to the app buttons)
  const GROUND = 1330;                        // ground line; the bottom band stays quiet for the platform UI
  const C = { sky1: '#7EC8F4', sky2: '#DDF1FB', ink: '#2A2320', cream: '#F6F0E2', gold: '#F2B84B', teal: '#2FA79A', pink: '#E8718D', orange: '#E0703E', grass: '#8CCB6E', grass2: '#6DB45A', navy: '#27305C' };
  globalThis.GEO && (GEO.cities.Binzhou = [117.97, 37.38]);

  // ---------- helpers ----------
  const prog = (t, t0, d) => clamp((t - t0) / d);
  const pop = (t, t0, d = 0.22) => ease.outBack(prog(t, t0, d), 2.4);

  // a word stamped on a torn paper card: scales in with a little overshoot, rotates slightly
  function stamp(ctx, text, x, y, t, t0, o = {}) {
    if (t < t0) return;
    const size = o.size || 92, fam = o.fam || 'Bungee', p = pop(t, t0, o.d || 0.2);
    const out = o.out != null ? 1 - prog(t, o.out, 0.25) : 1;
    if (out <= 0) return;
    const tw = G.measure(ctx, text, size, fam, 400);
    const w = tw + size * 0.9, h = size * 1.55;
    ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot ?? -0.03); ctx.scale(p * out, p * out); ctx.globalAlpha = clamp(p * 2) * out;
    G.tornPaper(ctx, -w / 2, -h / 2, w, h, { fill: o.bg || C.cream, seed: o.seed || Math.round(t0 * 10), shadow: true });
    G.text(ctx, text, 0, size * 0.36, { size, fam, weight: 400, color: o.fg || C.ink, align: 'center' });
    ctx.restore();
  }

  function sky(ctx, t, o = {}) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, o.top || C.sky1); g.addColorStop(1, o.bot || C.sky2);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    if (o.sun !== false) G.ellipse(ctx, 840, 300, 74, 74, { fill: '#FFE08A', lw: 4, seed: 3 });
    const speed = o.speed ?? 18;
    for (let i = 0; i < 6; i++) { // paper clouds drift off one edge and come back from the other, always off-screen
      const s = 0.6 + U.hash(i, 1) * 0.7, span = W + 700;
      const x = ((U.hash(i, 2) * span - t * speed * s) % span + span) % span - 350;
      const y = 240 + U.hash(i, 3) * 900;
      for (const [dx, dy, r] of [[0, 0, 60], [62, -28, 72], [134, 0, 56], [66, 18, 62]])
        G.ellipse(ctx, x + dx * s, y + dy * s, r * s, r * s * 0.82, { fill: '#FFFFFF', lw: 3, seed: 20 + i, alpha: 0.95 });
    }
  }

  function hills(ctx, y = GROUND, seed = 4) {
    G.poly(ctx, [[-50, y - 70], [260, y - 140], [560, y - 90], [860, y - 160], [1130, y - 100], [1130, H + 50], [-50, H + 50]], { fill: C.grass, lw: 5, seed, hatch: { color: 'rgba(40,90,40,0.18)', gap: 9 } });
    G.poly(ctx, [[-50, y], [1130, y], [1130, H + 50], [-50, H + 50]], { fill: C.grass2, lw: 5, seed: seed + 1 });
  }

  function runway(ctx, t, scroll = 0) {
    hills(ctx, GROUND - 40, 7);
    G.poly(ctx, [[-50, GROUND - 60], [1130, GROUND - 60], [1130, GROUND + 40], [-50, GROUND + 40]], { fill: '#5E6273', lw: 5, seed: 9 });
    for (let k = -1; k < 8; k++) {
      const x = ((k * 190 - scroll) % 1330 + 1330) % 1330 - 120;
      G.rrect(ctx, x, GROUND - 16, 100, 14, 6, { fill: '#F6F0E2', lw: 0, seed: 10 + k });
    }
    G.rrect(ctx, 860, 930, 54, 340, 8, { fill: '#E7E3DA', lw: 5, seed: 12 });                 // control tower
    G.poly(ctx, [[826, 930], [948, 930], [930, 860], [844, 860]], { fill: '#9DD3F0', lw: 5, seed: 13 });
  }

  const allLit = [1, 1, 1, 1, 1];

  // ---------- shots ----------
  function hook(ctx, t) {
    sky(ctx, t);
    hills(ctx);
    // fuel pump that the plane doesn't need
    const px = 210, py = GROUND - 30;
    G.rrect(ctx, px - 70, py - 230, 140, 230, 18, { fill: '#D9463E', lw: 6, seed: 31, hatch: { color: 'rgba(80,0,0,0.2)', gap: 8 } });
    G.rrect(ctx, px - 46, py - 200, 92, 62, 10, { fill: '#F6F0E2', lw: 4, seed: 32 });
    G.text(ctx, 'FUEL', px, py - 158, { size: 30, fam: 'Bungee', weight: 400, color: C.ink, align: 'center' });
    G.line(ctx, [[px + 70, py - 120], [px + 120, py - 100], [px + 118, py - 40]], { color: C.ink, lw: 10, seed: 33 });
    if (t >= ev.noFuel) {
      const p = t - ev.noFuel < 1 / 30 ? 1.25 : 1 + 0.25 * Math.exp(-(t - ev.noFuel) * 14), r = 150 * p; // slams on at full size, settles
      for (const [a, b] of [[[-1, -1], [1, 1]], [[1, -1], [-1, 1]]]) G.line(ctx, [[px + a[0] * r, py - 115 + a[1] * r], [px + b[0] * r, py - 115 + b[1] * r]], { color: '#C8102E', lw: 26, seed: 34 + a[0] });
    }
    // the plane swoops in on the first frame and settles, bobbing
    const k = ease.outCubic(prog(t, 0, 1.4));
    const x = lerp(-520, 560, k), y = lerp(1180, 900, k) + 14 * Math.sin(t * 2.2);
    Ch.eplane(ctx, { x, y, s: 0.82, rot: lerp(-0.28, -0.04, k) + 0.02 * Math.sin(t * 2.2), t, gear: 0, lit: allLit });
    stamp(ctx, 'BATTERY', CX, 330, t, 0.35, { size: 120, bg: C.gold, rot: -0.04 });
    stamp(ctx, 'PLANE!', CX, 500, t, 0.75, { size: 120, rot: 0.03 });
    stamp(ctx, 'NO JET FUEL', CX + 120, 1110, t, ev.noFuel + 0.55, { size: 64, bg: C.pink, fg: '#FFFFFF', rot: -0.06 });
  }

  function intro(ctx, t) {
    sky(ctx, t);
    const roll = clamp((t - (ev.takeoff - 1.6)) / 1.6);              // takeoff run
    runway(ctx, t, 600 * roll * roll);
    const k = clamp((t - ev.takeoff) / 2.2);
    const x = lerp(470, 470 + 120 * roll, 1) + 900 * k * k, y = GROUND - 128 - 620 * k * k;
    Ch.eplane(ctx, { x, y, s: 0.78, rot: -0.22 * clamp(k * 3), t, gear: 1 - clamp(k * 2), crew: true, lit: allLit });
    const calOut = prog(t, ev.takeoff - 0.4, 0.4);
    stamp(ctx, 'CE-25A', CX, 330, t, ev.nameStamp, { size: 140, bg: C.cream, rot: -0.03 });
    stamp(ctx, 'BY COMAC', CX, 500, t, 8.75, { size: 58, bg: C.teal, fg: '#FFFFFF', rot: 0.03 });
    // calendar: 13 → flips to NOV 14 in the pause before "On November fourteenth"
    if (t > 9.6 && calOut < 1) {
      const a = pop(t, 9.6, 0.25) * (1 - calOut);
      ctx.save(); ctx.translate(CX, 760); ctx.scale(a, a); ctx.rotate(0.04);
      G.rrect(ctx, -150, -160, 300, 320, 22, { fill: '#FFFFFF', lw: 6, seed: 51 });
      G.rrect(ctx, -150, -160, 300, 80, 22, { fill: '#D9463E', lw: 6, seed: 52 });
      G.text(ctx, 'NOV', 0, -104, { size: 48, fam: 'Bungee', weight: 400, color: '#FFFFFF', align: 'center' });
      const f = prog(t, ev.calFlip, 0.22);
      if (f < 1) { // the old page (13) lifts and folds away
        ctx.save(); ctx.translate(0, -80); ctx.scale(1, 1 - f); ctx.translate(0, 80);
        G.text(ctx, '13', 0, 70, { size: 150, fam: 'Bungee', weight: 400, color: '#B8B2A6', align: 'center' });
        ctx.restore();
      }
      if (f > 0.5) G.text(ctx, '14', 0, 70, { size: 150, fam: 'Bungee', weight: 400, color: C.ink, align: 'center' });
      ctx.restore();
    }
    stamp(ctx, 'FIRST FLIGHT', CX, 700, t, ev.takeoff + 0.35, { size: 84, bg: C.gold });
    stamp(ctx, 'WITH PEOPLE ON BOARD', CX, 840, t, ev.takeoff + 0.75, { size: 50, bg: C.cream, rot: 0.02 });
  }

  const PILOT = { hairStyle: 'short', hair: '#2E2420', skin: '#E9B48C', outfit: 'suit', robe: C.navy, trim: '#F2B84B', bottoms: 'pants', shorts: C.navy, headwear: 'cap', headwearColor: C.navy };
  const PILOT2 = { ...PILOT, hairStyle: 'ponytail', hair: '#1E1A18', skin: '#D9A07A' };
  const ENGINEER = { hairStyle: 'buzz', hair: '#2A2320', skin: '#C98E66', outfit: 'hoodie', shirt: C.orange, bottoms: 'pants', shorts: '#4A5578', glasses: 'square' };

  function crew(ctx, t) {
    sky(ctx, t);
    runway(ctx, t);
    Ch.eplane(ctx, { x: 520, y: GROUND - 300, s: 0.6, t, gear: 1, lit: [0, 0, 0, 0, 0] });
    const people = [[PILOT, 220, 0], [PILOT2, 490, 0.25], [ENGINEER, 760, 0.5]];
    for (const [style, x1, d] of people) {
      const t0 = A.crew + 0.1 + d, t1 = t0 + 1.3;
      const walking = t < t1;
      const x = walking ? lerp(x1 - 420, x1, ease.outQuad(prog(t, t0, 1.3))) : x1;
      Ch.person(ctx, { x, y: GROUND + 10, s: 0.74, pose: walking ? 'walk' : 'stand', walk: (t - t0) * 2.2, style, eyes: 'happy', mouth: 'smile', gesture: walking ? undefined : 'wave', t });
    }
    stamp(ctx, '2 PILOTS', CX, 330, t, A.crew + 0.35, { size: 110, bg: C.cream });
    stamp(ctx, '+ 1 FLIGHT TEST ENGINEER', CX, 490, t, A.crew + 1.5, { size: 46, bg: C.gold, rot: 0.02 });
  }

  let MAP = null;
  function map(ctx, t) {
    ctx.fillStyle = '#BFE3F5'; ctx.fillRect(0, 0, W, H);
    MAP = MAP || Data.map({ region: [113.6, 33.6, 123.4, 40.6], x: SAFE.x, y: 470, w: SAFE.w, h: 820, pad: 0 });
    Data.drawMap(ctx, MAP, { highlight: { China: '#F3E6C4' }, land: '#E8E1CF', sea: '#BFE3F5', lw: 4, t, t0: A.map - 0.2, dur: 0.6 });
    const [bx, by] = MAP.proj(117.97, 37.38);
    Data.pin(ctx, bx, by, { t, at: ev.mapPin, color: '#D9463E', size: 70 });
    stamp(ctx, 'BINZHOU', bx + 210, by - 70, t, ev.mapPin + 0.35, { size: 64, bg: C.cream, rot: -0.04 });
    stamp(ctx, 'SHANDONG, CHINA', CX, 330, t, ev.mapPin + 0.6, { size: 70, bg: C.cream });
  }

  function flight(ctx, t) {
    sky(ctx, t, { speed: 140 });
    const off = (t - A.flight) * 160;
    // far + near hills scroll at different speeds (parallax)
    for (const [yy, sp, col, seed] of [[1180, 0.4, '#A8D88E', 61], [1290, 1, C.grass, 62]]) {
      const pts = [[-50, H + 50]];
      for (let x = -60; x <= 1140; x += 60) pts.push([x, yy - 60 - 50 * Math.sin((x + off * sp) / 170 + seed)]);
      pts.push([1140, H + 50]);
      G.poly(ctx, pts, { fill: col, lw: 5, seed, step: 40 });
    }
    // dotted trail behind the plane
    for (let i = 1; i < 14; i++) { const tx = 520 - 330 - i * 60, ty = 900 + 30 * Math.sin((t - i * 0.08) * 1.6); G.ellipse(ctx, tx, ty + 20, 8, 8, { fill: '#FFFFFF', lw: 2, seed: 70 + i, alpha: 1 - i / 14 }); }
    Ch.eplane(ctx, { x: 560, y: 900 + 30 * Math.sin(t * 1.6), s: 0.72, rot: -0.05 + 0.04 * Math.cos(t * 1.6), t, gear: 0, crew: true, lit: allLit });
    const card = (y, t0, to, unit, seed) => {
      if (t < t0) return;
      const p = pop(t, t0);
      ctx.save(); ctx.translate(CX, y); ctx.scale(p, p);
      G.tornPaper(ctx, -260, -85, 520, 170, { fill: C.cream, seed, shadow: true });
      Data.counter(ctx, { x: -30, y: 42, from: 0, to, t, t0: t0 + 0.1, t1: t0 + 1.2, size: 116, color: C.ink, align: 'right', fam: 'Bungee', weight: 400, prefix: '~' });
      G.text(ctx, unit, 10, 36, { size: 64, fam: 'Bungee', weight: 400, color: '#17675F' });
      ctx.restore();
    };
    card(340, 22.4, 17, 'MIN', 81);
    card(540, 24.1, 60, 'KM', 82);
  }

  function fans(ctx, t) {
    sky(ctx, t, { top: '#5FB6EE', bot: '#CBEAF8' });
    const lit = S.fans.map((f) => ease.outQuad(prog(t, f.t, 0.14)));
    Ch.eplaneFront(ctx, { x: CX, y: 930, s: 0.9, t, lit });
    const n = S.fans.filter((f) => t >= f.t).length;
    if (n > 0) {
      const last = S.fans[n - 1].t, b = 1 + 0.18 * Math.max(0, 1 - (t - last) / 0.15);
      ctx.save(); ctx.translate(CX, 360); ctx.scale(b, b);
      G.text(ctx, String(n), 0, 50, { size: 170, fam: 'Bungee', weight: 400, color: C.cream, align: 'center', stroke: C.ink, strokeW: 14 });
      ctx.restore();
    }
    stamp(ctx, 'ELECTRIC FANS', CX, 530, t, S.fans[9].t + 0.25, { size: 70, bg: C.teal, fg: '#FFFFFF' });
    stamp(ctx, '5', CX - 260, 1150, t, 30.1, { size: 80, bg: C.gold, rot: -0.08 });
    stamp(ctx, '5', CX + 260, 1150, t, 30.45, { size: 80, bg: C.gold, rot: 0.08 });
  }

  function gag(ctx, t) {
    sky(ctx, t);
    hills(ctx);
    const lt = t - A.gag;
    // wall socket on a post, and a cable reel
    G.rrect(ctx, 112, 1010, 26, 300, 8, { fill: '#B98B5E', lw: 5, seed: 91 });
    G.rrect(ctx, 70, 930, 110, 120, 16, { fill: '#FFFFFF', lw: 6, seed: 92 });
    G.rrect(ctx, 104, 966, 12, 30, 4, { fill: C.ink, lw: 0, seed: 93 }); G.rrect(ctx, 134, 966, 12, 30, 4, { fill: C.ink, lw: 0, seed: 94 });
    const reelA = lt * 9 * (lt < ev.yank - A.gag ? 1 : 0);
    G.ellipse(ctx, 250, 1230, 70, 70, { fill: '#F2B84B', lw: 6, seed: 95 });
    for (let k = 0; k < 4; k++) { const a = reelA + (k * Math.PI) / 2; G.line(ctx, [[250, 1230], [250 + Math.cos(a) * 58, 1230 + Math.sin(a) * 58]], { color: C.ink, lw: 6, seed: 96 + k }); }
    // the plane climbs away to the right... until the cable runs out
    const yankT = ev.yank;
    const fly = ease.inOutQuad(prog(t, A.gag + 0.25, yankT - A.gag - 0.25));
    const snap = t >= yankT ? U.springKick(t, yankT, 2.6, 5) : 0;
    const px = lerp(420, 720, fly) - 90 * snap, py = lerp(1080, 690, fly) + 20 * snap;
    const tight = t >= yankT ? 1 : 0;
    // cable: plug → reel → plane tail. Saggy while it pays out, dead straight at the yank.
    const tail = [px - 0.5 * 470, py + 10];
    const pts = [[140, 1000], [190, 1120], [250, 1170]];
    for (let i = 1; i <= 16; i++) {
      const u = i / 16, sag = (1 - tight) * 140 * Math.sin(u * Math.PI) * (1 - 0.6 * fly) + tight * 18 * Math.sin(u * Math.PI) * Math.cos((t - yankT) * 30) * Math.exp(-(t - yankT) * 6);
      pts.push([lerp(250, tail[0], u), lerp(1170, tail[1], u) + sag]);
    }
    G.line(ctx, pts, { color: '#2A2320', lw: 14, seed: 97 });
    G.line(ctx, pts, { color: C.gold, lw: 7, seed: 98 });
    Ch.eplane(ctx, { x: px, y: py, s: 0.5, rot: -0.18 * fly + 0.25 * snap, sx: 1 - 0.12 * snap, sy: 1 + 0.12 * snap, t, gear: 0, lit: allLit });
    if (t >= yankT) G.text(ctx, '!', px + 40, py - 120 - 20 * pop(t, yankT), { size: 120, fam: 'Bungee', weight: 400, color: '#D9463E', align: 'center', stroke: C.ink, strokeW: 10 });
    stamp(ctx, 'LONG CABLE...?', CX, 330, t, A.gag + 0.5, { size: 80, bg: C.cream });
    stamp(ctx, 'BOING!', CX, 520, t, yankT, { size: 130, bg: C.pink, fg: '#FFFFFF', rot: -0.08, d: 0.05 });
  }

  function speed(ctx, t) {
    sky(ctx, t, { speed: 520, sun: false, top: '#4FA8E8', bot: '#C8E8F8' });
    for (let i = 0; i < 12; i++) { // speed lines
      const y = 880 + i * 34, x = ((U.hash(i, 5) * 1500 - (t - A.speed) * 2300) % 1500 + 1500) % 1500 - 200;
      G.line(ctx, [[x, y], [x + 190, y]], { color: '#FFFFFF', lw: 7, seed: 100 + i, alpha: 0.85 });
    }
    Ch.eplane(ctx, { x: 560 + 12 * Math.sin(t * 9), y: 1080, s: 0.7, rot: -0.06, t, gear: 0, lit: allLit });
    // speedometer
    const gx = CX, gy = 640, R = 200, a0 = Math.PI * 0.8, a1 = Math.PI * 2.2;
    G.ellipse(ctx, gx, gy, R + 20, R + 20, { fill: C.cream, lw: 7, seed: 110 });
    for (let k = 0; k <= 6; k++) {
      const a = lerp(a0, a1, k / 6);
      G.line(ctx, [[gx + Math.cos(a) * (R - 26), gy + Math.sin(a) * (R - 26)], [gx + Math.cos(a) * (R - 2), gy + Math.sin(a) * (R - 2)]], { color: C.ink, lw: 7, seed: 111 + k });
    }
    const v = ease.outCubic(prog(t, A.speed + 0.6, 1.8));
    const a = lerp(a0, a1, v) + 0.015 * Math.sin(t * 40) * v;
    G.line(ctx, [[gx, gy], [gx + Math.cos(a) * (R - 40), gy + Math.sin(a) * (R - 40)]], { color: '#D9463E', lw: 12, seed: 120 });
    G.ellipse(ctx, gx, gy, 22, 22, { fill: C.ink, lw: 3, seed: 121 });
    Data.counter(ctx, { x: gx, y: gy + 130, from: 0, to: 300, t, t0: A.speed + 0.6, t1: A.speed + 2.4, size: 70, color: C.ink, align: 'center', fam: 'Bungee', weight: 400 });
    stamp(ctx, 'CRUISING SPEED', CX, 330, t, A.speed + 0.3, { size: 80, bg: C.gold });
    stamp(ctx, 'KM/H', CX, 915, t, A.speed + 2.4, { size: 56, bg: C.cream, rot: 0.04 });
  }

  function weight(ctx, t) {
    sky(ctx, t);
    hills(ctx);
    const n = S.blocks.filter((b) => t >= b.t).length;
    const target = lerp(0.2, 0, n / 10);                                     // the plane side starts down, the blocks balance it
    const ang = target + 0.03 * Math.sin((t - (S.blocks[Math.max(0, n - 1)].t)) * 14) * Math.exp(-(t - S.blocks[Math.max(0, n - 1)].t) * 5) * (n > 0 ? 1 : 0);
    const fx = CX, fy = GROUND - 90;
    G.poly(ctx, [[fx - 70, GROUND - 10], [fx + 70, GROUND - 10], [fx, fy]], { fill: '#8A6A4C', lw: 6, seed: 130 });
    ctx.save(); ctx.translate(fx, fy); ctx.rotate(-ang);
    G.rrect(ctx, -420, -18, 840, 26, 10, { fill: '#C9A27A', lw: 6, seed: 131 });
    Ch.eplane(ctx, { x: -230, y: -88, s: 0.4, t, gear: 1, lit: [0, 0, 0, 0, 0] });
    for (const b of S.blocks) {
      if (t < b.t) continue;
      const col = b.i % 2, row = Math.floor(b.i / 2), p = ease.outBounce(prog(t, b.t, 0.25));
      const bx = 200 + col * 104, by = -18 - 34 - row * 64 - (1 - p) * 220;
      G.rrect(ctx, bx - 50, by - 30, 100, 62, 8, { fill: '#7D8597', lw: 5, seed: 140 + b.i });
      G.text(ctx, '1 t', bx, by + 12, { size: 34, fam: 'Bungee', weight: 400, color: '#FFFFFF', align: 'center' });
    }
    ctx.restore();
    if (n > 0 && t < S.blocks[9].t + 0.3) G.text(ctx, String(n), CX, 470, { size: 150, fam: 'Bungee', weight: 400, color: C.cream, align: 'center', stroke: C.ink, strokeW: 14 });
    stamp(ctx, '~10 TONNES', CX, 330, t, S.blocks[9].t + 0.3, { size: 100, bg: C.gold });
  }

  function city(ctx, x, base, s, seed, tint) {
    const blocks = [[0, 150], [62, 230], [124, 120], [176, 190]];
    for (const [dx, h] of blocks) {
      G.rrect(ctx, x + dx * s, base - h * s, 54 * s, h * s, 6, { fill: tint, lw: 5, seed: seed + dx });
      for (let wy = base - h * s + 20 * s; wy < base - 20 * s; wy += 34 * s) G.rrect(ctx, x + dx * s + 14 * s, wy, 24 * s, 14 * s, 3, { fill: '#FFE08A', lw: 0, seed: seed + wy });
    }
  }

  function route(ctx, t) {
    sky(ctx, t, { top: '#8FD0F4', bot: '#EAF6FC' });
    hills(ctx, GROUND, 150);
    const P0 = [210, 1180], P1 = [790, 1180];
    city(ctx, 90, 1210, 1.0, 160, '#9BA6C8');
    city(ctx, 670, 1210, 1.0, 170, '#C59BC8');
    const u = ease.inOutQuad(prog(t, ev.route, 2.8));
    const arc = (k) => [lerp(P0[0], P1[0], k), lerp(P0[1], P1[1], k) - 560 * Math.sin(Math.PI * k)];
    const pts = []; for (let i = 0; i <= 40; i++) { const k = (i / 40) * u; pts.push(arc(k)); }
    for (let i = 0; i < pts.length - 1; i += 2) G.line(ctx, [pts[i], pts[i + 1]], { color: '#D9463E', lw: 9, seed: 180 + i });
    const [ax, ay] = arc(u), [bx, by] = arc(Math.min(1, u + 0.01));
    Ch.eplane(ctx, { x: ax, y: ay, s: 0.2, rot: Math.atan2(by - ay, bx - ax), t, gear: 0, lit: allLit });
    const card = () => {
      if (t < ev.route + 0.2) return;
      const p = pop(t, ev.route + 0.2);
      ctx.save(); ctx.translate(CX, 340); ctx.scale(p, p);
      G.tornPaper(ctx, -330, -90, 660, 180, { fill: C.cream, seed: 190, shadow: true });
      G.text(ctx, 'UP TO', -170, 40, { size: 44, fam: 'Bungee', weight: 400, color: '#17675F', align: 'center' });
      Data.counter(ctx, { x: 150, y: 46, from: 0, to: 400, t, t0: ev.route + 0.3, t1: ev.route + 2.6, size: 110, color: C.ink, align: 'right', fam: 'Bungee', weight: 400 });
      G.text(ctx, 'KM', 170, 40, { size: 64, fam: 'Bungee', weight: 400, color: '#17675F' });
      ctx.restore();
    };
    card();
    stamp(ctx, '~250 MILES', CX, 520, t, 45.2, { size: 70, bg: C.gold, rot: 0.03 });
    stamp(ctx, 'BETWEEN CITIES', CX, 1080, t, 46.4, { size: 56, bg: C.cream, rot: -0.02 });
  }

  function tests(ctx, t) {
    sky(ctx, t);
    hills(ctx);
    const n = S.tests.filter((p) => t >= p.t).length;
    for (const p of S.tests) {
      if (t < p.t) continue;
      const col = p.i % 4, row = Math.floor(p.i / 4), k = pop(t, p.t, 0.2);
      const x = 200 + col * 200 + (row % 2) * 40, y = 660 + row * 120 + 8 * Math.sin(t * 3 + p.i);
      Ch.eplane(ctx, { x, y, s: 0.17 * k, t, gear: 0, lit: allLit });
    }
    if (n > 0) G.text(ctx, String(n), CX, 470, { size: 150, fam: 'Bungee', weight: 400, color: C.cream, align: 'center', stroke: C.ink, strokeW: 14 });
    stamp(ctx, 'TEST FLIGHTS', CX, 300, t, S.tests[18].t + 0.2, { size: 80, bg: C.cream });
    stamp(ctx, 'NOBODY ABOARD', CX, 1140, t, 50.9, { size: 64, bg: C.gold, rot: 0.03 });
  }

  function cert(ctx, t) {
    sky(ctx, t, { top: '#9ED4F2', bot: '#F2F8FB' });
    stamp(ctx, 'NEXT UP:', CX, 330, t, A.cert + 0.15, { size: 100, bg: C.gold, out: 55.55 });
    stamp(ctx, "CHINA'S AVIATION", CX, 300, t, 55.9, { size: 66, bg: C.cream });
    stamp(ctx, 'REGULATOR', CX, 420, t, 56.2, { size: 66, bg: C.cream, rot: 0.03 });
    // the certificate rises in, then gets its stamp
    const k = ease.outCubic(prog(t, 53.8, 0.6));
    if (k > 0) {
      ctx.save(); ctx.translate(CX, lerp(1500, 880, k)); ctx.rotate(-0.03);
      G.tornPaper(ctx, -300, -360, 600, 720, { fill: '#FFFDF4', seed: 201, shadow: true });
      G.text(ctx, 'SAFETY', 0, -250, { size: 70, fam: 'Bungee', weight: 400, color: C.navy, align: 'center' });
      G.text(ctx, 'CERTIFICATE', 0, -170, { size: 54, fam: 'Bungee', weight: 400, color: C.navy, align: 'center' });
      for (let i = 0; i < 5; i++) G.line(ctx, [[-210, -80 + i * 56], [i === 4 ? 40 : 210, -80 + i * 56]], { color: '#D8D2C4', lw: 8, seed: 210 + i });
      G.ellipse(ctx, 170, 250, 54, 54, { fill: C.gold, lw: 5, seed: 220 });
      ctx.restore();
    }
    if (t >= ev.certStamp) {
      const p = ease.outBack(prog(t, ev.certStamp, 0.12), 2), s = lerp(2.4, 1, p);
      ctx.save(); ctx.translate(CX, 900); ctx.rotate(-0.22); ctx.scale(s, s); ctx.globalAlpha = clamp(p * 1.5);
      G.rrect(ctx, -290, -95, 580, 190, 18, { fill: 'rgba(255,255,255,0)', stroke: '#C8102E', lw: 14, seed: 230 });
      G.text(ctx, 'APPLICATION', 0, -10, { size: 66, fam: 'Bungee', weight: 400, color: '#C8102E', align: 'center' });
      G.text(ctx, 'ACCEPTED', 0, 66, { size: 66, fam: 'Bungee', weight: 400, color: '#C8102E', align: 'center' });
      ctx.restore();
    }
  }

  function checks(ctx, t) {
    sky(ctx, t);
    Ch.eplane(ctx, { x: 560 + 20 * Math.sin(t), y: 560 + 12 * Math.sin(t * 1.7), s: 0.4, t, gear: 0, lit: allLit });
    stamp(ctx, 'COMAC SAYS', CX, 330, t, A.checks + 0.15, { size: 90, bg: C.cream });
    const k = ease.outCubic(prog(t, A.checks + 0.3, 0.5));
    ctx.save(); ctx.translate(CX, lerp(1400, 960, k)); ctx.globalAlpha = k;
    G.rrect(ctx, -330, -260, 660, 520, 30, { fill: '#C9A27A', lw: 6, seed: 240 });
    G.tornPaper(ctx, -290, -220, 580, 460, { fill: '#FFFDF4', seed: 241 });
    G.rrect(ctx, -80, -290, 160, 60, 14, { fill: '#9AA3BC', lw: 5, seed: 242 });
    const rows = [['BEHAVED', 'NORMALLY', ev.ticks[0]], ['RESULTS MET', 'EXPECTATIONS', ev.ticks[1]]];
    rows.forEach(([l1, l2, tt], i) => {
      const y = -110 + i * 200;
      G.rrect(ctx, -250, y - 50, 100, 100, 14, { fill: '#FFFFFF', lw: 6, seed: 250 + i });
      if (t >= tt) UI.check(ctx, -200, y, 40, ease.outQuad(prog(t, tt, 0.25)));
      G.text(ctx, l1, -110, y - 6, { size: 44, fam: 'Bungee', weight: 400, color: C.ink });
      G.text(ctx, l2, -110, y + 46, { size: 44, fam: 'Bungee', weight: 400, color: C.ink });
    });
    ctx.restore();
  }

  function outro(ctx, t) {
    sky(ctx, t);
    hills(ctx);
    const k = ease.inQuad(prog(t, A.outro + 0.4, 2.6)); // the plane flies off; the last frame is the empty sky the film opens on
    Ch.eplane(ctx, { x: lerp(560, 1700, k), y: lerp(900, 640, k) + 14 * Math.sin(t * 2.2), s: 0.82, rot: -0.04 - 0.12 * k, t, gear: 0, lit: allLit });
    stamp(ctx, 'FOLLOW', CX, 330, t, A.outro + 0.25, { size: 130, bg: C.gold, rot: -0.04, out: S.DURATION - 0.6 });
    stamp(ctx, 'FOR DAILY GOOD NEWS', CX, 500, t, A.outro + 0.6, { size: 56, rot: 0.03, out: S.DURATION - 0.6 });
  }

  // ---------- the shot list: transitions sit in the voice pauses ----------
  const push = Shots.push(1, 1.05);
  const shots = Shots.film([
    { at: A.hook, draw: hook, cam: Shots.push(1.04, 1) },
    { at: A.intro, draw: intro, in: { type: 'whip', dur: 0.36 }, cam: push },
    { at: A.crew, draw: crew, in: { type: 'push', dur: 0.4 }, cam: push },
    { at: A.map, draw: map, in: { type: 'paper', dur: 0.5 }, cam: Shots.push(1, 1.08) },
    { at: A.flight, draw: flight, in: { type: 'whip', dur: 0.36 } },
    { at: A.fans, draw: fans, in: { type: 'zoom', dur: 0.4 }, cam: push },
    { at: A.gag, draw: gag, in: { type: 'push', dur: 0.36 }, cam: (s) => Shots.combine(push, Shots.shake(26, ev.yank, 7))(s) },
    { at: A.speed, draw: speed, in: { type: 'fade', dur: 0.4 } },
    { at: A.weight, draw: weight, in: { type: 'push', dur: 0.4 }, cam: push },
    { at: A.route, draw: route, in: { type: 'whip', dur: 0.36 }, cam: push },
    { at: A.tests, draw: tests, in: { type: 'push', dur: 0.4 }, cam: push },
    { at: A.cert, draw: cert, in: { type: 'paper', dur: 0.5 }, cam: (s) => Shots.combine(push, Shots.shake(18, ev.certStamp, 8))(s) },
    { at: A.checks, draw: checks, in: { type: 'whip', dur: 0.36 }, cam: push },
    { at: A.outro, draw: outro, in: { type: 'push', dur: 0.4 } },
  ], { end: S.DURATION });

  Studio.film({
    draw(ctx, t) {
      shots(ctx, t);
      for (const ft of [ev.noFuel, ev.yank]) if (t >= ft && t < ft + 0.2) { ctx.fillStyle = `rgba(255,250,235,${0.5 * (1 - (t - ft) / 0.2)})`; ctx.fillRect(0, 0, W, H); }
      if (t >= ev.certStamp && t < ev.certStamp + 0.25) { ctx.fillStyle = `rgba(255,250,235,${0.55 * (1 - (t - ev.certStamp) / 0.25)})`; ctx.fillRect(0, 0, W, H); }
      Subs.draw(ctx, t, S.subtitles, { style: 'pop', size: 66 });
    },
    post: { paper: 0.4, vignette: 0.22, grain: 0.045 },
    fadeOut: 0.4,
  });
})();
