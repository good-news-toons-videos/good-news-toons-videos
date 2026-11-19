"""Episode 002: Voyager 1 becomes the first human-made object one light-day from Earth."""
import sys, math, subprocess, os
from PIL import Image, ImageDraw
from toon import *

LINES = [
    "A spacecraft from 1977 just broke a cosmic record.",
    "On November 18, NASA's Voyager 1 became the first human-made object ever to reach one light-day from Earth.",
    "A light-day is how far light travels in twenty-four hours. That's more than sixteen billion miles!",
    "So a message from Earth now takes a whole day to reach Voyager, and another day for its answer to come back.",
    "Voyager 1 launched in 1977, flew past Jupiter and Saturn, and became the first spacecraft to enter interstellar space.",
    "Nearly fifty years later, it's still cruising at about thirty-eight thousand miles per hour, and still sending science home.",
    "Follow for a little good news every day.",
]
STARTS = [0, 4.91102, 12.721633, 19.565714, 26.566531, 35.239184, 42.788571]
DURS = [4.91102, 7.810612, 6.844082, 7.000816, 8.672653, 7.549388, 2.586122]
TOTAL = 45.6
ENDS = STARTS[1:] + [TOTAL]
CHUNKS = caption_chunks(LINES, STARTS, DURS)

SPACE = make_space_bg(seed=7)
SPACE2 = make_space_bg(seed=21, top=(14, 10, 46), bot=(30, 50, 110))

JUP = dict(col=(230, 180, 120), bands=[(-0.4, 0.16, (200, 140, 90)), (0.05, 0.2, (210, 150, 100)), (0.45, 0.14, (196, 136, 92))])
SAT = dict(col=(240, 212, 150), bands=[(-0.2, 0.14, (220, 186, 120)), (0.3, 0.12, (220, 186, 120))], rings=(214, 196, 150))


def frame(t):
    img = None
    # ---------------- scene 0: hook ----------------
    if t < ENDS[0]:
        lt = t
        img = SPACE.copy()
        d = ImageDraw.Draw(img)
        draw_twinkles(d, t)
        draw_earth(d, 160, 1500, 70)
        x = -200 + 760 * ease_out(prog(lt, 0.0, 2.6)) + 30 * lt
        draw_voyager(img, x, 1080 + 14 * math.sin(lt * 2), 0.95, rot=6 * math.sin(lt))
        sticker(img, 540, 330, "1977", 160, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-3)
        sticker(img, 540, 560, "COSMIC RECORD!", 90, C["pink"], fg=C["white"], scale=pop(prog(lt, 2.0, 0.35)), rot=2)
    # ---------------- scene 1: first to one light-day ----------------
    elif t < ENDS[1]:
        lt = t - STARTS[1]
        img = SPACE.copy()
        d = ImageDraw.Draw(img)
        draw_twinkles(d, t)
        # Earth left, Voyager right, a measuring tape between them
        draw_earth(d, 170, 1150, 95)
        p = ease_in_out(prog(lt, 0.4, 2.4))
        vx = 400 + 470 * p
        x1 = 270 + (vx - 330) * 1.0
        if p > 0:
            d.line([(S(270), S(1150)), (S(max(270, vx - 160)), S(1150))], fill=C["yellow"], width=S(10))
            for k in range(0, 20):
                xx = 290 + k * 40
                if xx < vx - 170:
                    d.line([(S(xx), S(1138)), (S(xx), S(1162))], fill=C["ink"], width=S(4))
        draw_voyager(img, vx, 1150 + 10 * math.sin(lt * 2), 0.62, rot=0)
        sticker(img, 540, 300, "NOV 18, 2026", 74, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
        sticker(img, 540, 500, "1 LIGHT-DAY", 120, C["yellow"], scale=pop(prog(lt, 3.0, 0.35)), rot=2)
        b = pop(prog(lt, 4.6, 0.35))
        sticker(img, 540, 1380, "★ FIRST EVER ★", 74, C["pink"], fg=C["white"], scale=b, rot=-2)
        if lt > 4.6:
            draw_confetti(ImageDraw.Draw(img), lt, 4.6, n=50)
    # ---------------- scene 2: what a light-day is ----------------
    elif t < ENDS[2]:
        lt = t - STARTS[2]
        img = SPACE2.copy()
        d = ImageDraw.Draw(img)
        draw_twinkles(d, t, seed=4)
        draw_earth(d, 140, 1100, 70)
        # a beam of light races out with a 24h clock
        p = prog(lt, 0.3, 3.6)
        bx = 210 + 780 * p
        for k in range(12):
            tx = bx - k * 26
            if tx > 210:
                rr = 12 - k * 0.8
                d.ellipse([S(tx - rr), S(1100 - rr), S(tx + rr), S(1100 + rr)], fill=(255, 236, 140))
        draw_glow(img, bx, 1100, 22)
        d = ImageDraw.Draw(img)
        draw_clock(d, 540, 740, 170, prog(lt, 0.3, 3.6))
        sticker(img, 540, 330, "24 HOURS", 110, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
        a = pop(prog(lt, 3.6, 0.35))
        n = 16 * ease_out(prog(lt, 3.6, 1.6))
        sticker(img, 540, 1300, f"{n:.1f} BILLION" if n < 15.95 else "16 BILLION+", 96, C["pink"], fg=C["white"], scale=a, rot=2)
        sticker(img, 540, 1450, "MILES", 64, C["white"], scale=pop(prog(lt, 4.0, 0.3)))
    # ---------------- scene 3: one day there, one day back ----------------
    elif t < ENDS[3]:
        lt = t - STARTS[3]
        img = SPACE.copy()
        d = ImageDraw.Draw(img)
        draw_twinkles(d, t, seed=8)
        draw_earth(d, 170, 1180, 95)
        draw_voyager(img, 880, 1180 + 10 * math.sin(lt * 2), 0.5)
        d = ImageDraw.Draw(img)
        # dotted path
        for xx in range(290, 760, 30):
            d.ellipse([S(xx - 4), S(1180 - 4), S(xx + 4), S(1180 + 4)], fill=(200, 200, 230))
        go = prog(lt, 0.4, 2.6)
        back = prog(lt, 3.7, 2.6)
        if 0 < go < 1:
            ex = 290 + 470 * ease_in_out(go)
            draw_envelope(d, ex, 1110 + 20 * math.sin(lt * 6), 110)
        if 0 < back < 1:
            ex = 760 - 470 * ease_in_out(back)
            draw_envelope(d, ex, 1250 + 20 * math.sin(lt * 6), 110, col=C["yellow"])
        sticker(img, 330, 420, "TO VOYAGER:", 58, C["white"], scale=pop(prog(lt, 0.3, 0.3)), rot=-2)
        sticker(img, 760, 420, "1 DAY", 80, C["yellow"], scale=pop(prog(lt, 0.7, 0.3)), rot=3)
        sticker(img, 330, 620, "REPLY:", 58, C["white"], scale=pop(prog(lt, 3.6, 0.3)), rot=-2)
        sticker(img, 760, 620, "1 MORE DAY", 70, C["pink"], fg=C["white"], scale=pop(prog(lt, 4.0, 0.3)), rot=3)
    # ---------------- scene 4: the journey ----------------
    elif t < ENDS[4]:
        lt = t - STARTS[4]
        img = SPACE2.copy()
        d = ImageDraw.Draw(img)
        draw_twinkles(d, t, seed=13)
        # the camera pans right past Jupiter and Saturn; Voyager stays centered-ish
        le = min(lt, 6.0)
        jx = 540 + 600 * (2.4 - le)
        draw_planet(d, jx, 1050, 190, JUP["col"], bands=JUP["bands"])
        draw_planet(d, jx + 720, 1050, 130, SAT["col"], bands=SAT["bands"], rings=SAT["rings"])
        # edge of the Sun's bubble (heliopause)
        hx = jx + 720 + 1300 + 1400
        if hx - 1400 < W + 50:
            d.arc([S(hx - 1400), S(-300), S(hx + 1400), S(2200)], 130, 230, fill=(120, 220, 255), width=S(14))
        draw_voyager(img, 380 + 480 * ease_in_out(prog(lt, 5.2, 2.6)), 1460 + 12 * math.sin(lt * 2), 0.55, rot=4)
        labels = [("1977: LAUNCH", 0.0, C["white"]), ("JUPITER", 2.2, C["orange"]), ("SATURN", 3.3, C["yellow"]), ("INTERSTELLAR SPACE!", 5.4, C["teal"])]
        cur = None
        for s_, t0, col in labels:
            if lt >= t0: cur = (s_, t0, col)
        if cur:
            s_, t0, col = cur
            fg = C["white"] if col in (C["orange"], C["teal"]) else C["ink"]
            sticker(img, 540, 380, s_, 84 if len(s_) < 14 else 70, col, fg=fg, scale=pop(prog(lt, t0, 0.3)), rot=-2)
        if lt > 5.4:
            sticker(img, 540, 560, "FIRST SPACECRAFT THERE", 56, C["white"], scale=pop(prog(lt, 6.0, 0.3)), rot=2)
    # ---------------- scene 5: still cruising ----------------
    elif t < ENDS[5]:
        lt = t - STARTS[5]
        img = SPACE.copy()
        d = ImageDraw.Draw(img)
        # speed streaks
        rnd = random.Random(3)
        for i in range(40):
            y = rnd.uniform(200, 1800); spd = rnd.uniform(900, 1600); ln = rnd.uniform(60, 180)
            x = W + 200 - ((lt * spd + rnd.uniform(0, 2000)) % (W + 400))
            d.line([(S(x), S(y)), (S(x + ln), S(y))], fill=(200, 210, 255), width=S(4))
        draw_voyager(img, 600, 1080 + 16 * math.sin(lt * 2.5), 0.9, rot=3 * math.sin(lt * 1.5))
        d = ImageDraw.Draw(img)
        draw_waves(d, 390, 1090, lt)
        n = int(38000 * ease_out(prog(lt, 0.3, 2.4)))
        sticker(img, 540, 330, f"~{n:,} MPH", 104, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
        sticker(img, 540, 1440, "STILL SENDING SCIENCE", 68, C["teal"], fg=C["white"], scale=pop(prog(lt, 4.0, 0.35)), rot=2)
    # ---------------- scene 6: outro ----------------
    else:
        lt = t - STARTS[6]
        img = vgrad(SW, SH, (60, 50, 160), (255, 120, 170)).convert("RGBA")
        d = ImageDraw.Draw(img)
        sunburst(d, 540, 900, -lt, (100, 90, 210), speed=0.4)
        draw_twinkles(d, t, seed=2, n=18)
        draw_voyager(img, 540, 1080 - 30 * abs(math.sin(lt * 4)), 0.95, rot=10 * math.sin(lt * 3))
        sticker(img, 540, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
        sticker(img, 540, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    draw_caption(img, CHUNKS, t)
    return finish(img)


def render_scene(i, out):
    a, b = STARTS[i], ENDS[i]
    n = int(round((b - a) * FPS))
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(frame(a + k / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)


if __name__ == "__main__":
    os.makedirs("out/ep002", exist_ok=True)
    if sys.argv[1] == "stills":
        for t in map(float, sys.argv[2:]):
            frame(t).save(f"out/ep002/still_{t:05.2f}.jpg", quality=88)
    elif sys.argv[1] == "scene":
        for i in map(int, sys.argv[2:]):
            render_scene(i, f"out/ep002/scene{i}.mp4")
