// Ch.eplane: a 19-seat battery-electric commuter plane (high wing, 10 ducted fans) built from G.* primitives,
// so it boils and hatches like the rest of the film. Generic design: no airline or maker livery.
//   Ch.eplane(ctx, { x, y, s, rot, sx, sy, t, lit: [0..1 x5], gear: 0..1, crew: bool, seed })   side view, nose right
//   Ch.eplaneFront(ctx, { x, y, s, t, lit: [0..1 x10], seed })                                   front view
(function () {
  const G = globalThis.G, Ch = globalThis.Ch, U = globalThis.U;
  const BODY = '#FBF8F0', TEAL = '#2FA79A', GLOW = '#7CF2E2', SLATE = '#47506A', GREY = '#D9DCE4', GLASS = '#A9D8F5', BOLT = '#F2B84B';
  const H = (c) => ({ color: G.tint ? G.tint(c, -0.25) + '55' : 'rgba(0,0,0,0.15)', gap: 8 });

  function fan(ctx, cx, cy, r, t, lit, seed) {
    if (lit > 0.01) { // a soft cyan glow behind a powered fan
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r * 2.6);
      g.addColorStop(0, `rgba(124,242,226,${0.65 * lit})`); g.addColorStop(1, 'rgba(124,242,226,0)');
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(cx - r * 2.6, cy - r * 2.6, r * 5.2, r * 5.2); ctx.restore();
    }
    G.ellipse(ctx, cx, cy, r, r, { fill: SLATE, lw: 5, seed });
    G.ellipse(ctx, cx, cy, r * 0.72, r * 0.72, { fill: lit > 0.5 ? '#2C3550' : '#39415A', lw: 3, seed: seed + 1 });
    const spin = t * (2 + 5 * lit); // spins up when lit, never fast enough to strobe
    for (let b = 0; b < 4; b++) {
      const a = spin + (b * Math.PI) / 2;
      G.line(ctx, [[cx, cy], [cx + Math.cos(a) * r * 0.66, cy + Math.sin(a) * r * 0.66]], { color: lit > 0.5 ? GLOW : '#9AA3BC', lw: 6, seed: seed + 2 + b });
    }
    G.ellipse(ctx, cx, cy, r * 0.14, r * 0.14, { fill: BOLT, lw: 2, seed: seed + 9 });
  }

  Ch.eplane = function (ctx, o) {
    const { x = 0, y = 0, s = 1, rot = 0, sx = 1, sy = 1, t = 0, gear = 1, crew = false, seed = 40 } = o;
    const lit = o.lit || [1, 1, 1, 1, 1];
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * sx, s * sy);
    // tail
    G.poly(ctx, [[-395, -20], [-455, -205], [-372, -205], [-300, -28]], { fill: TEAL, lw: 6, seed: seed + 1, hatch: H(TEAL) });
    G.poly(ctx, [[-440, -2], [-485, 30], [-330, 30], [-318, 0]], { fill: GREY, lw: 5, seed: seed + 2 });
    // fuselage + nose
    G.poly(ctx, [[392, -40], [478, 12], [392, 62]], { fill: BODY, lw: 6, seed: seed + 3 });
    G.rrect(ctx, -430, -40, 840, 102, 50, { fill: BODY, lw: 6, seed: seed + 4, hatch: { color: 'rgba(120,110,90,0.12)', gap: 9 } });
    G.rrect(ctx, -410, 26, 860, 14, 7, { fill: TEAL, lw: 0, seed: seed + 5 });
    // cockpit + cabin windows (the first three show the crew when `crew` is on)
    G.poly(ctx, [[388, -26], [446, 6], [392, 12]], { fill: GLASS, lw: 4, seed: seed + 6 });
    for (let i = 0; i < 9; i++) {
      const wx = -300 + i * 70;
      G.rrect(ctx, wx, -12, 36, 30, 12, { fill: GLASS, lw: 4, seed: seed + 10 + i });
      if (crew && i >= 6) {
        G.ellipse(ctx, wx + 18, 6, 11, 11, { fill: '#E9B48C', lw: 2, seed: seed + 30 + i });
        G.line(ctx, [[wx + 12, 9], [wx + 18, 13], [wx + 24, 9]], { color: '#2A2320', lw: 2, seed: seed + 40 + i });
      }
    }
    // the lightning bolt: it runs on batteries
    G.poly(ctx, [[-60, 44], [-30, 44], [-46, 54], [-22, 54], [-70, 80], [-54, 62], [-76, 62]], { fill: BOLT, lw: 3, seed: seed + 7 });
    // gear
    if (gear > 0.02) {
      for (const gx of [-90, 300]) {
        const L = 46 * gear;
        G.line(ctx, [[gx, 60], [gx, 60 + L]], { color: '#2A2320', lw: 9, seed: seed + 50 + gx });
        G.ellipse(ctx, gx, 64 + L, 20 * gear, 20 * gear, { fill: '#2A2320', lw: 3, seed: seed + 60 + gx });
      }
    }
    // high wing (edge-on) with five ducted fans on top
    G.rrect(ctx, -175, -70, 350, 28, 13, { fill: GREY, lw: 5, seed: seed + 8 });
    for (let i = 0; i < 5; i++) fan(ctx, -140 + i * 70, -100, 30, t + i * 0.13, lit[i] || 0, seed + 70 + i * 10);
    ctx.restore();
  };

  Ch.eplaneFront = function (ctx, o) {
    const { x = 0, y = 0, s = 1, t = 0, seed = 140, rot = 0 } = o;
    const lit = o.lit || Array(10).fill(1);
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    G.poly(ctx, [[-14, -60], [-6, -250], [6, -250], [14, -60]], { fill: TEAL, lw: 5, seed: seed + 1 });                 // fin
    G.poly(ctx, [[-170, -40], [170, -40], [150, -26], [-150, -26]], { fill: GREY, lw: 4, seed: seed + 2 });               // tailplane
    for (const gx of [-110, 110]) { G.line(ctx, [[gx, 70], [gx, 130]], { color: '#2A2320', lw: 10, seed: seed + 3 + gx }); G.rrect(ctx, gx - 14, 120, 28, 44, 10, { fill: '#2A2320', lw: 3, seed: seed + 5 + gx }); }
    G.ellipse(ctx, 0, 20, 92, 96, { fill: BODY, lw: 6, seed: seed + 6, hatch: { color: 'rgba(120,110,90,0.12)', gap: 9 } }); // fuselage
    G.rrect(ctx, -40, -20, 80, 30, 12, { fill: GLASS, lw: 4, seed: seed + 7 });                                          // windscreen
    G.ellipse(ctx, 0, 60, 26, 26, { fill: '#EFE6D2', lw: 3, seed: seed + 8 });                                           // nose
    G.rrect(ctx, -480, -92, 960, 30, 14, { fill: GREY, lw: 5, seed: seed + 9 });                                         // the high wing
    G.poly(ctx, [[-60, -64], [60, -64], [80, -10], [-80, -10]], { fill: GREY, lw: 4, seed: seed + 10 });                // wing root
    for (let i = 0; i < 10; i++) {
      const side = i < 5 ? -1 : 1, k = i < 5 ? 4 - i : i - 5;                                                           // 0..4 from the root outwards
      fan(ctx, side * (130 + k * 78), -125, 34, t + i * 0.11, lit[i] || 0, seed + 20 + i * 10);
    }
    ctx.restore();
  };
})();
