# ep005: electric plane (Animation Studio build)

Rebuilt with the **animation-studio** skill (canvas film + synthesized score from one timeline) instead of `tools/toon.py`.

- `score.js`: the single source of truth: voice-line starts, every shot cut (placed in the pauses of the voiceover), comic hits, gimmick notes, captions (`subs.json`), sync markers.
- `song.js`: the soundtrack is the vidIQ voiceover only (`assets/vo.wav`), mastered to -14 LUFS, at the owner's request (no music or SFX). `MUSIC=1 node song.js` restores the original 100 BPM bed + SFX + gimmick notes.
- `plane.js`: `Ch.eplane` / `Ch.eplaneFront`, a generic 19-seat high-wing plane with 10 ducted fans, built from `G.*` primitives.
- `film.js`: 14 shots via `Shots.film` (whip/push/paper/zoom transitions in the voice pauses), `Subs.draw` pop captions inside the 9:16 safe area.

Sync gimmicks: the 10 fans light up one per 8th note and each plays a marimba note climbing the scale; the ten 1-tonne blocks each land on a note; the 19 test-flight planes pop in on 16th-note plucks; the fuel-pump X, the charging-cable BOING and the APPLICATION ACCEPTED stamp are sync-verified hits (sound ±20 ms, picture ±1 frame).

## Rebuild
```bash
node <animation-studio skill dir>/scripts/new-project.js /tmp/ep005 --format 9:16   # to get engine/
cp -r films/ep005-electric-plane/* /tmp/ep005/ && cd /tmp/ep005
node song.js && node engine/render.js video && node engine/render.js mux && node engine/render.js verify
```
