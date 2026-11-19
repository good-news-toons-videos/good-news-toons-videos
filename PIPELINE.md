# Good News Toons: weekly production pipeline

Channel: **Good News Toons**, short 2D flat-cartoon explainers of recent, real, positive, **non-political** news.
Accounts (all via vidIQ): TikTok `@goodnewstoonsdaily`, Instagram `@good_news_toons`, YouTube `@goodnewstoons-q2w`.
Posting schedule: one episode per day at **6:00 PM America/Chicago**, made in weekly batches of 7 that the owner approves once.

## Story rules
- Published in the last ~10 days, verified against at least 2 independent reputable sources (fetch them, don't trust roundups alone).
- Positive and non-political: wildlife, conservation, science, health/medicine, space, clean-energy data, community kindness, rescues, records, culture. Skip legislation, elections, politicians, wars, culture-war topics, and anything a government action is the main subject of.
- Not already in `EPISODES.md`. Mix categories across the week; prefer stories with something visual to animate (animals, vehicles, places, numbers).
- Every number, date and place in the script must appear in a source. When sources disagree, use the vaguer wording ("late October").

## Script
- 6–8 lines, ~110–130 words total, ~40–50 s of audio. Line 1 is a punchy hook (under 12 words). Last line is always: "Follow for a little good news every day."
- Voiceover: `vidiq_voiceover_generate` with `voiceId` `cgSgspJ2msm6clMCkdW9` (Jessica, playful/bright/warm), passing `scriptLines` (one line per scene). It returns per-line `startSeconds`/`durationSeconds` and a joined `audioUrl` (~28 credits each).
- Download with `curl -sS -o vo.mp3 <audioUrl>` (assets.vidiq.com is allowlisted).

## Animation
- `tools/toon.py` is the toolkit (1080x1920, 30 fps, drawn at 2x): sky/road/bridge scenery, cars, side-view animals (`coyote`, `lion`, `bobcat`, `deer`, `fox`; add new species to `SPECIES` or new draw functions as needed), `sticker()` pop-in labels, `caption_chunks()`/`draw_caption()` burnt-in captions, confetti, sunbursts.
- `tools/ep001_wildlife_crossing.py` is the reference episode: copy it to `tools/epNNN_<slug>.py`, set `LINES`, `STARTS`, `DURS` from the voiceover result, and write one scene per line in `frame(t)`. Every scene needs motion, a big sticker headline for its key fact, and the caption. Keep text inside x 60–1020, y 250–1750.
- Check before rendering: `python3 tools/epNNN.py stills <t1> <t2> ...` then look at the JPGs (legibility, overlaps, animals visible). Fix, then render: `python3 tools/epNNN.py scene 0 1 2 ...` (run two processes in parallel), concat with the ffmpeg concat demuxer and `-c copy`.
- Mux: `ffmpeg -i silent.mp4 -i vo.mp3 -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -af "apad,loudnorm=I=-14:TP=-1.5" -shortest -movflags +faststart videos/good_news_toons_epNNN_<slug>.mp4`

## Upload and post
1. Commit the MP4 to `videos/` and push to `main`.
2. `vidiq_video_upload` with `url` = `https://github.com/good-news-toons-videos/good-news-toons-videos/raw/main/videos/<file>.mp4` → `uploadId`.
3. `vidiq_social_post_draft_create`, one draft per episode, media = that upload, `publishAt` = its day at 18:00 America/Chicago (ISO with offset, e.g. `2026-11-22T18:00:00-06:00`), destinations:
   - TIKTOK `_000Bz163-0TCukr5lR24t3h7Onesu5dxJ3J`: `privacyLevel: PUBLIC_TO_EVERYONE`, `allowComment: true`, `musicUsageConfirmed: true` (owner accepted TikTok's Music Usage Confirmation on 2026-11-19), `isAiGenerated: true`.
   - INSTAGRAM `29773976395540909`.
   - YOUTUBE `UCxV4_7zzir5qoXp3GQBqm0w`: `privacyStatus: public`, title ≤ 100 chars ending in `#shorts`, a fitting `categoryId` (15 Pets & Animals, 28 Science & Technology, 26 Howto & Style, 22 People & Blogs), 5–8 tags, and a description with the story, every source as a full link, and the line "Animated with AI."
   - Shared caption (TikTok/Instagram): 2–3 short lines + "Sources: <outlet names>" + 4–6 hashtags including #goodnews.
4. **Do not publish without the owner's approval** of the drafts. After approval, call `vidiq_social_post_publish` for each draft (with a `publishAt` this schedules it). If YouTube asks for verification, show the owner the link and wait.
5. Append each episode to `EPISODES.md` and push.
