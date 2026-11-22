# Good News Toons: weekly production pipeline

Channel: **Good News Toons**, short 2D flat-cartoon explainers of recent, real, positive, **non-political** news.
Accounts (all via vidIQ): TikTok `@goodnewstoonsdaily`, Instagram `@good_news_toons`, YouTube `@goodnewstoons-q2w`.
Posting schedule: one episode per day at **5:00 PM America/Chicago** (owner request, Nov 20 2026), made in weekly batches of 7 that the owner approves once.

## Monetization (owner request, Nov 21 2026)
YouTube Shorts and TikTok are the money platforms; every episode must qualify on both and work as an Instagram Reel.
- Length **65–75 s, never under 61 s** (TikTok Creator Rewards only pays on videos over 1 minute). Fill with real, sourced detail, never padding.
- Original/licensed visuals, voice and music only; no copyrighted characters, logos or songs; nothing shocking or graphic.
- Hook in the first 1–3 s; burned-in captions; key text kept clear of the bottom (~last 400 px) and right edge (app UI); outro scene mirrors the hook so the video loops.
- Searchable YouTube title + description (sources, keywords, a few hashtags incl. #Shorts); TikTok/Reels caption with hook line + hashtags.
- Before each weekly batch, re-check the current TikTok Creator Rewards and YouTube Partner Program thresholds (they change) and tell the owner what the channel doesn't meet yet.

## Story rules
- Published in the last ~10 days, verified against at least 2 independent reputable sources (fetch them, don't trust roundups alone).
- Positive and non-political: wildlife, conservation, science, health/medicine, space, clean-energy data, community kindness, rescues, records, culture. Skip legislation, elections, politicians, wars, culture-war topics, and anything a government action is the main subject of.
- Not already in `EPISODES.md`. Mix categories across the week; prefer stories with something visual to animate (animals, vehicles, places, numbers).
- Every number, date and place in the script must appear in a source. When sources disagree, use the vaguer wording ("late October").

## Script
- 9–10 lines, **~920–1000 characters total (stay at or under 1000 so each voiceover costs 28 credits)**, ~60–65 s of speech. Line 1 is a punchy hook (under 12 words). Last line is always: "Follow for a little good news every day."
- Jessica reads ~15.4 characters/second. After download, insert a 0.55 s pause between lines (and 0.6 s at the end) with ffmpeg, which lands the episode at 65–71 s. Shift STARTS accordingly; captions use the per-line durations.
- Humor: a light, kind joke/pun/visual gag in roughly 2–3 of 7 episodes; never about real people or undercutting a serious story; never changes facts.
- Voiceover: `vidiq_voiceover_generate` with `voiceId` `cgSgspJ2msm6clMCkdW9` (Jessica, playful/bright/warm), passing `scriptLines` (one line per scene). It returns per-line `startSeconds`/`durationSeconds` and a joined `audioUrl` (~28 credits each).
- Download with `curl -sS -o vo.mp3 <audioUrl>` (assets.vidiq.com is allowlisted).

## Animation
- **Style and sound (owner decision, Nov 21 2026):** every episode uses the flat-cartoon look of `tools/toon.py` + `tools/epkit.py` (as in ep004 and ep006–ep010). Do **not** use the hand-drawn Animation Studio engine; `films/ep005-electric-plane` was a one-off. The soundtrack is the **voiceover only: no music and no sound effects**.
- `tools/toon.py` is the toolkit (1080x1920, 30 fps, drawn at 2x): sky/road/bridge scenery, cars, side-view animals (`coyote`, `lion`, `bobcat`, `deer`, `fox`; add new species to `SPECIES` or new draw functions as needed), `sticker()` pop-in labels, `caption_chunks()`/`draw_caption()` burnt-in captions, confetti, sunbursts.
- From ep004 on, episodes use `tools/epkit.py`: define `LINES/STARTS/DURS/TOTAL` and one `sN(t, lt)` function per line, then `run(...)`. Commands: `python3 tools/epNNN_x.py stills <t...>`, `... all` (renders every scene on 2 cores, concats and muxes into `videos/`), `... join` (re-concat/mux after re-rendering single scenes with `... scene N`). `tools/contact.py out/epNNN` makes a contact sheet of the stills. `set_safe_captions()` (called by epkit) puts captions at y≈1470 and keeps them off the right edge.
- **Motion rules (owner feedback Nov 21 2026: "a bit janky")** — epkit adds a 0.3 s crossfade into every scene, a slow 3.5% camera push-in per scene, and draws captions last (they hold through the pauses between lines). In scene code:
  - No hard cuts inside a scene: use `xcut(t, lt, cut, shot_a, shot_b)` to crossfade between two shots.
  - Nothing may teleport: looping props (animals, bubbles, hearts, particles) must enter/leave off-screen or shrink/fade at the ends of their loop; one-shot moves use `ease_in_out(prog(...))`, not `% 1`.
  - Big cards/documents/photos ease in (`ease_out`, slide up 80–120 px, `paste_scaled(..., alpha=)`) instead of a full-size overshoot `pop`; reserve `pop` for stickers.
  - No full-screen flashes; no fast spinning hands/blades (keep anything rotating under ~1.5 turns/s so it doesn't strobe at 30 fps); no stepped animation (interpolate, don't index into a few pre-drawn frames).
  - Check with `python3 tools/jank.py` frame-difference scan: spikes should only be at scene crossfades and sticker pops.
- `tools/ep001_wildlife_crossing.py` is the original reference episode: copy it to `tools/epNNN_<slug>.py`, set `LINES`, `STARTS`, `DURS` from the voiceover result, and write one scene per line in `frame(t)`. Every scene needs motion, a big sticker headline for its key fact, and the caption. Keep sticker text inside x 60–960, y 250–1350 (captions sit at y≈1470); nothing important below y≈1550.
- Check before rendering: `python3 tools/epNNN.py stills <t1> <t2> ...` then look at the JPGs (legibility, overlaps, animals visible). Fix, then render: `python3 tools/epNNN.py scene 0 1 2 ...` (run two processes in parallel), concat with the ffmpeg concat demuxer and `-c copy`.
- Mux: `ffmpeg -i silent.mp4 -i vo.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "apad,loudnorm=I=-14:TP=-1.5" -shortest -movflags +faststart videos/good_news_toons_epNNN_<slug>.mp4`

## Upload and post
1. Commit the MP4 to `videos/` and push to `main`.
2. `vidiq_video_upload` with `url` = `https://github.com/good-news-toons-videos/good-news-toons-videos/raw/main/videos/<file>.mp4` → `uploadId`.
3. `vidiq_social_post_draft_create`, one draft per episode, media = that upload, `publishAt` = its day at 17:00 America/Chicago (ISO with offset, e.g. `2026-11-22T17:00:00-06:00`), destinations:
   - TIKTOK `_000Bz163-0TCukr5lR24t3h7Onesu5dxJ3J`: `privacyLevel: PUBLIC_TO_EVERYONE`, `allowComment: true`, `musicUsageConfirmed: true` (owner accepted TikTok's Music Usage Confirmation on 2026-11-19), `isAiGenerated: true`.
   - INSTAGRAM `29773976395540909`.
   - YOUTUBE `UCxV4_7zzir5qoXp3GQBqm0w`: `privacyStatus: public`, title ≤ 100 chars ending in `#shorts`, a fitting `categoryId` (15 Pets & Animals, 28 Science & Technology, 26 Howto & Style, 22 People & Blogs), 5–8 tags, and a description with the story, every source as a full link, and the line "Animated with AI."
   - Shared caption (TikTok/Instagram): 2–3 short lines + "Sources: <outlet names>" + 4–6 hashtags including #goodnews.
4. **Do not publish without the owner's approval** of the drafts. After approval, call `vidiq_social_post_publish` for each draft (with a `publishAt` this schedules it). If YouTube asks for verification, show the owner the link and wait.
5. Append each episode to `EPISODES.md` and push.
