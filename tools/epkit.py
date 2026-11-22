"""Tiny episode runner shared by ep004+ : scenes are functions scene(t, lt) -> RGBA canvas.

Usage from an episode file:
    run("ep004", "sea_turtles_california", LINES, STARTS, DURS, TOTAL, SCENES, audio_path)
CLI:  python3 epNNN.py stills 1.0 5.2 ...   -> out/epNNN/still_*.jpg
      python3 epNNN.py scene 0 1 2          -> out/epNNN/sceneN.mp4
      python3 epNNN.py all                  -> renders every scene (2 workers), concats, muxes into videos/
"""
import sys, os, subprocess, multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from toon import *

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CTX = {}


XFADE = 0.3      # seconds of crossfade into each scene
PUSH = 0.035     # slow camera push-in per scene (3.5%), anchored on the caption line


def _bounds(i):
    c = _CTX
    a = c["starts"][i]
    b = c["starts"][i + 1] if i + 1 < len(c["starts"]) else c["total"]
    return a, b


def _shot(i, t):
    """render scene i at time t (2x canvas), then apply the camera push and downsample to 1x (captions are added later)"""
    c = _CTX
    a, b = _bounds(i)
    img = c["scenes"][i](t, t - a)
    z = 1 + PUSH * ease_in_out((t - a) / max(0.01, b - a))
    ax, ay = S(CAPTION_X), S(CAPTION_Y)
    box = (ax - ax / z, ay - ay / z, ax + (SW - ax) / z, ay + (SH - ay) / z)
    return img.convert("RGB").resize((W, H), Image.LANCZOS, box=box)


def _frame(t):
    c = _CTX
    i = 0
    while i + 1 < len(c["starts"]) and t >= c["starts"][i + 1]:
        i += 1
    cur = _shot(i, t)
    lt = t - c["starts"][i]
    if i > 0 and lt < XFADE:
        prev = _shot(i - 1, t)
        cur = Image.blend(prev, cur, ease_in_out(lt / XFADE))
    draw_caption_1x(cur, c["chunks"], t)
    return cur


def _render_scene(i):
    c = _CTX
    a = c["starts"][i]
    b = c["starts"][i + 1] if i + 1 < len(c["starts"]) else c["total"]
    f0, f1 = int(round(a * FPS)), int(round(b * FPS))
    out = f"{c['out']}/scene{i}.mp4"; tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for k in range(f0, f1):
        p.stdin.write(_frame(k / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out)
    return out


def run(ep, slug, lines, starts, durs, total, scenes, audio):
    set_safe_captions()
    assert len(lines) == len(starts) == len(durs) == len(scenes)
    out = os.path.join(REPO, "out", ep)
    os.makedirs(out, exist_ok=True)
    _CTX.update(starts=starts, total=total, scenes=scenes, chunks=caption_chunks(lines, starts, durs), out=out)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "stills":
        for t in map(float, sys.argv[2:]):
            _frame(t).save(f"{out}/still_{t:05.2f}.jpg", quality=85)
    elif cmd == "scene":
        for i in map(int, sys.argv[2:]):
            _render_scene(i)
    elif cmd in ("all", "join"):
        idx = list(range(len(scenes)))
        if cmd == "all":
            with ProcessPoolExecutor(2, mp_context=mp.get_context('fork')) as ex:
                files = list(ex.map(_render_scene, idx))
        else:
            files = [f"{out}/scene{i}.mp4" for i in idx]
        with open(f"{out}/list.txt", "w") as fh:
            for fpath in files:
                fh.write(f"file '{fpath}'\n")
        silent = f"{out}/silent.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-c", "copy", silent], check=True)
        final = os.path.join(REPO, "videos", f"good_news_toons_{ep}_{slug}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-af", "apad,loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", final], check=True)
        print(final)
