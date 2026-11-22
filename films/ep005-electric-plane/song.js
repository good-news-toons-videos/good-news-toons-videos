// THE SONG: the vidIQ voiceover on top of an original, synthesized music bed + sound effects, all from score.js.
//   node song.js          (STEMS=1 also writes out/stem-*.wav; LUFS=-14 masters to YouTube/TikTok loudness)
const path = require('path');
const { SR, Bus, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { BEAT, DURATION, m, ev, clock, cut } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), bass = bus(), pad = bus(), keys = bus(), fx = bus(), gim = bus();
const verb = bus(), dly = bus();

// ---------- the voice (the spine of the film) ----------
const voice = MIX.loadAudio(path.join(__dirname, 'assets/vo.wav'), { length: DURATION });

const outroT = cut(9);
const groove = (t) => t < outroT - 0.05;

// ---------- drums: a light, bouncy explainer groove ----------
const K = I.kick({ punch: 0.8, tail: 0.5 }), CL = I.clap({ spread: 1.1 }), SH = [I.shaker(1, 15), I.shaker(0.6, 16)], HO = I.hat(true, 14);
const kicks = [];
clock.eachStep(0, 30, 8, (t, b, s) => {
  if (!groove(t) || t > DURATION) return;
  if (s === 0 || s === 4) { drums.addMono(K, t, 0.7); kicks.push(t); }
  if (s === 2 || s === 6) { drums.addMono(CL, t, 0.32); verb.addMono(CL, t, 0.12); }
  drums.addMono(SH[s % 2], t, s % 2 ? 0.1 : 0.16, 0.3);
  if (s === 7) drums.addMono(HO, t, 0.06, -0.3);
});

// ---------- bass: short root-fifth plucks ----------
clock.eachStep(0, 30, 8, (t, b, s) => {
  if (t > DURATION - 0.3) return;
  const c = sc.chordAt(t); if (!c) return;
  const R = c.bass + 12;
  if (!groove(t)) { if (s === 0) bass.addMono(I.bass(R, BEAT * 3.5, { sub: 1, bright: 0.2 }), t, 0.45); return; }
  if (s === 0) bass.addMono(I.bass(R, BEAT * 0.9), t, 0.5);
  if (s === 3) bass.addMono(I.bass(R, BEAT * 0.4), t, 0.35);
  if (s === 4) bass.addMono(I.bass(R + 7, BEAT * 0.8), t, 0.42);
});

// ---------- pads + offbeat plucks ----------
for (const c of sc.chords) {
  if (c.t0 >= DURATION) continue;
  const len = Math.min(c.t1, DURATION) - c.t0;
  for (const n of c.notes) { const { L, R } = I.padNote(n, len, { cutoff: c.name === 'Fmaj9' ? 1800 : 1300, attack: 0.3, release: 1.2 }); pad.addStereo(L, R, c.t0, 0.07); }
}
clock.eachStep(0, 30, 8, (t, b, s) => {
  if (!groove(t) || s % 2 === 0) return;
  const c = sc.chordAt(t); if (!c) return;
  c.notes.forEach((n, k) => keys.addMono(I.pluck(n + 12, { decay: 0.16, cutoff: 2600 }), t, 0.07, k - 1));
});

// ---------- outro: the music box sings the hook ----------
for (const n of sc.musicbox) { const mb = I.musicBox(n.midi); keys.addMono(mb, n.t, 0.22); verb.addMono(mb, n.t, 0.2); dly.addMono(mb, n.t, 0.08); }

// ---------- gimmicks: the picture plays these notes ----------
for (const f of sc.fans) { const x = I.marimba(f.midi, { thock: 0 }); gim.addMono(x, f.t, 0.42, f.i < 5 ? -0.35 : 0.35); verb.addMono(x, f.t, 0.15); }
for (const b of sc.blocks) { const x = I.marimba(b.midi, { thock: 0.8 }); gim.addMono(x, b.t, 0.5); gim.addMono(I.woodTick(1 + b.i * 0.05), b.t, 0.15); }
for (const p of sc.tests) { const x = I.pluck(p.midi, { decay: 0.12, cutoff: 3400 }); gim.addMono(x, p.t, 0.32, (p.i % 5 - 2) * 0.2); gim.addMono(I.pop(1 + p.i * 0.03), p.t, 0.12); }
for (const t of ev.ticks) { gim.addMono(I.ting(m('C6')), t, 0.3); verb.addMono(I.ting(m('C6')), t, 0.12); }

// ---------- fx, each one tied to an event in the score ----------
fx.addMono(I.noiseSweep(1.1, 300, 4200, { q: 0.8, pink: true }), ev.planeIn, 0.35, -0.4);   // the plane swooshes in
fx.addMono(I.thwack(), ev.noFuel, 0.6);                                                      // big X on the fuel pump
fx.addMono(I.thud(90, 0.08), ev.noFuel, 0.5);
fx.addMono(I.thwack(), ev.nameStamp, 0.4);                                                   // CE-25A nameplate stamp
fx.addMono(I.paperFwip(1.0, 11), ev.calFlip - 0.03, 0.45);                                   // calendar flips to NOV 14
fx.addMono(I.noiseSweep(1.6, 200, 6000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.takeoff - 1.2, 0.3); // takeoff rush
fx.addMono(I.pop(0.8), ev.mapPin, 0.45);                                                     // pin drops on Binzhou
fx.addMono(I.thud(140, 0.05), ev.mapPin + 0.12, 0.25);
for (let i = 0; i < 8; i++) fx.addMono(I.woodTick(1.6 + 0.04 * i), ev.gag + 0.45 + i * 0.32, 0.12); // cable reel clicking out
fx.addMono(I.noiseSweep(0.4, 2400, 600, { q: 2 }), ev.yank - 0.36, 0.16);                    // ...zzzip...
fx.addMono(I.boing(), ev.yank, 0.65);                                                        // BOING: the cable runs out
fx.addMono(I.thud(70, 0.1), ev.yank, 0.55);
fx.addMono(I.noiseSweep(0.9, 500, 5000, { q: 1, pink: true }), cut(5) + 0.2, 0.3);           // speed-lines whoosh
fx.addMono(I.noiseSweep(1.4, 400, 2400, { q: 1.2, pink: true }), ev.route, 0.18);            // the route arc draws
fx.addMono(I.tvClick(), ev.nextUp, 0.3);                                                     // "Next up:"
fx.addMono(I.thwack(), ev.certStamp, 0.7);                                                   // APPLICATION ACCEPTED stamp
fx.addMono(I.thud(80, 0.09), ev.certStamp, 0.6);
fx.addMono(I.crash(18), ev.certStamp, 0.12, 0.2);
Object.values(sc.shotAt).filter((t) => t > 0).forEach((t, i) => fx.addMono(I.noiseSweep(0.32, 900, 3800, { q: 1.1, pink: true }), t - 0.16, 0.12, i % 2 ? -0.3 : 0.3)); // a soft whoosh on every shot change

// ---------- mix ----------
MIX.sidechain([pad, bass], kicks, { depth: 0.25 });
const wet = { verb: reverb(verb, { room: 0.8, damp: 0.35 }), dly: pingpong(dly, BEAT * 0.75, 0.35, 3500) };
MIX.duck([drums, bass, pad, keys, wet.verb, wet.dly], voice, { depth: 0.55, release: 0.35 }); // music dips under the voice
MIX.duck([gim, fx], voice, { depth: 0.25, release: 0.3 });
// Owner request (Nov 21 2026): voice only, no music or sound effects. MUSIC=1 node song.js brings the bed back.
const stems = process.env.MUSIC === '1' ? { voice, drums, bass, pad, keys, gim, fx, ...wet } : { voice };
const GAIN = { voice: 2.6, drums: 0.24, bass: 0.4, pad: 1.8, keys: 0.8, gim: 0.6, fx: 0.75, verb: 0.8, dly: 0.8 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 30);
MIX.fadeOut(mix, DURATION - 0.6, DURATION);
const M = MIX.master(mix, 0.8, undefined, { lufs: parseFloat(process.env.LUFS || '-14') });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s, ${M.lufs !== undefined ? M.lufs.toFixed(1) + ' LUFS' : ''} at drive ${M.drive ? M.drive.toFixed(2) : '?'})`);
