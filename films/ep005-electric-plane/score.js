// THE SCORE: Good News Toons ep005, "This 19-seat plane flies on batteries" (COMAC CE-25A first crewed flight).
// The voiceover (assets/vo.wav, vidIQ "Jessica", already timed with 0.55 s pauses between lines) is the spine:
// every shot change and comic hit sits inside a measured pause, so nothing ever lands on top of a word.
// Music and picture both read the events below.
(function () {
  const node = typeof require !== 'undefined';
  const U = node ? require('./engine/util') : globalThis.U;
  const MU = node ? require('./engine/music') : globalThis.MUSIC;
  const { m, makeClock, placeBar, makeChords } = MU;
  const SUBS = node ? require('./subs.json') : globalThis.SUBS_JSON;

  const FPS = 30;
  const FORMAT = U.pickFormat('9:16');
  const [W, H] = U.formatSize(FORMAT);
  const SAFE = U.safeArea(W, H);
  const WIDE = W / H > 1.2;
  const STYLE = 'paper';
  const clock = makeClock({ bpm: 100, offset: 0 }); // 1 beat = 0.6 s, 1 bar = 2.4 s, 8th = 0.3 s
  const { T, BEAT } = clock;
  const DURATION = 68.82; // = the voiceover

  // Start of each spoken line; each shot cut sits in the pause just before its line.
  const LINES = [0, 5.96, 15.34, 20.96, 26.56, 35.58, 39.84, 48.07, 60.11, 65.74];
  const cut = (i) => LINES[i] - 0.3;
  const snap8 = (t) => Math.round(t / (BEAT / 2)) * (BEAT / 2);

  const ev = {
    planeIn: 0.0,            // the hook: the plane swoops in on frame 1
    noFuel: 3.42,            // pause before "No jet fuel at all!": the fuel pump gets a big X (thunk)
    nameStamp: 7.15,         // "CE-25A" nameplate stamps as it's said
    calFlip: 10.72,          // pause before "On November fourteenth": the calendar flips to NOV 14
    takeoff: 12.6,           // wheels leave the runway
    mapCut: 18.0,            // crew → map of Shandong
    mapPin: 18.45,           // "...from Binzhou": the pin drops
    fanFirst: snap8(27.0),   // fans light up one per 8th: 10 notes climbing the scale
    gag: 31.5,               // "Somebody's gonna need a really long charging cable!"
    yank: 34.95,             // pause after "cable!": the cable snaps taut, BOING
    route: 42.6,             // "...fly up to four hundred kilometers"
    blocks: snap8(40.2),     // ten 1-tonne blocks stack, one per 16th (done by the end of "ten tonnes")
    testFirst: snap8(48.6),  // 19 tiny uncrewed test flights pop in, one per 16th
    nextUp: 52.66,           // pause before "Next up:"
    certStamp: 59.48,        // pause after "...accepted its application": the APPLICATION ACCEPTED stamp
    checksCut: 60.9,         // cut to the checklist (leaves the stamp up for a beat and a half)
    ticks: [61.95, 64.25],   // "behaved normally" / "met expectations"
    end: DURATION,
  };

  // Every shot change (film.js builds its shot list from these; song.js puts a page-turn whoosh on each)
  const shotAt = { hook: 0, intro: cut(1), crew: cut(2), map: ev.mapCut, flight: cut(3), fans: cut(4), gag: ev.gag, speed: cut(5),
    weight: cut(6), route: 42.3, tests: cut(7), cert: ev.nextUp, checks: ev.checksCut, outro: cut(9) };

  // Gimmick notes: F major pentatonic, climbing
  const PENTA = ['F4', 'G4', 'A4', 'C5', 'D5', 'F5', 'G5', 'A5', 'C6', 'D6', 'F6'];
  const fans = Array.from({ length: 10 }, (_, i) => ({ i, t: ev.fanFirst + i * BEAT / 2, midi: m(PENTA[i]) }));
  const blocks = Array.from({ length: 10 }, (_, i) => ({ i, t: ev.blocks + i * BEAT / 4, midi: m(PENTA[i]) - 12 }));
  const tests = Array.from({ length: 19 }, (_, i) => ({ i, t: ev.testFirst + i * BEAT / 4, midi: m(PENTA[i % 11]) + (i >= 11 ? 12 : 0) }));

  // Sections (levels.js reads these)
  const S = {
    hook: [0, cut(1)], intro: [cut(1), cut(2)], crew: [cut(2), cut(3)], flight: [cut(3), cut(4)], fans: [cut(4), cut(5)],
    speed: [cut(5), cut(6)], weight: [cut(6), cut(7)], tests: [cut(7), 60.9], checks: [60.9, cut(9)], outro: [cut(9), DURATION],
  };

  // Harmony: a light F-major loop under the voice (I V vi IV), resolving to Fmaj9 for the outro
  const prog = ['F', 'C', 'Dm', 'Bb'];
  const outroBar = Math.floor(cut(9) / (4 * BEAT)) + 1; // first full bar after the outro cut
  const rows = [];
  for (let b = 0; b < outroBar; b++) rows.push([b, 0, 4, prog[b % 4]]);
  for (let b = outroBar; b < 30; b++) rows.push([b, 0, 4, 'Fmaj9']);
  const { chords, chordAt } = makeChords(clock, {
    F: { notes: ['A3', 'C4', 'F4'], bass: 'F2' },
    C: { notes: ['G3', 'C4', 'E4'], bass: 'C2' },
    Dm: { notes: ['A3', 'D4', 'F4'], bass: 'D2' },
    Bb: { notes: ['Bb3', 'D4', 'F4'], bass: 'Bb1' },
    Fmaj9: { notes: ['A3', 'C4', 'E4', 'G4'], bass: 'F1' },
  }, rows);

  // Music-box hook: a soft reprise on the outro, under "Follow for a little good news every day."
  const HOOK = [['C5', 0, 2], ['A4', 2, 1], ['C5', 3, 1], ['F5', 4, 2], ['E5', 6, 1], ['D5', 7, 1]];
  const musicbox = placeBar(clock, HOOK, outroBar - 1, 12).filter((n) => n.t >= cut(9));

  const markers = {
    hook: 0.4,
    noFuel: { t: ev.noFuel, sync: 'av' },
    nameplate: ev.nameStamp + 0.3,
    calFlip: ev.calFlip + 0.2,
    takeoff: ev.takeoff + 0.6,
    crew: cut(2) + 1.2,
    mapPin: ev.mapPin + 0.4,
    flight: cut(3) + 2,
    fans: ev.fanFirst + 2,
    gag: ev.gag + 1.5,
    yank: { t: ev.yank, sync: 'av' },
    speed: cut(5) + 2,
    blocks: ev.blocks + 2,
    route: ev.route + 2.5,
    tests: ev.testFirst + 2.5,
    cert: { t: ev.certStamp, sync: 'av' },
    checks: ev.ticks[1] + 0.3,
    outro: cut(9) + 1.2,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, STYLE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, LINES, cut, fans, blocks, tests, musicbox, markers, shotAt, subtitles: SUBS };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
