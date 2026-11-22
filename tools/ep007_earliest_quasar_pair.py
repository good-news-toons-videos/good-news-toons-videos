"""Episode 007: JWST + Gemini North find the earliest close quasar pair, Napowawaenakaulua (NOIRLab, Nov 10, 2026)."""
import math, random
from PIL import Image, ImageDraw
from toon import *
from epkit import run, REPO

LINES = [
    "Astronomers just spotted two monster black holes, side by side, near the dawn of time!",
    "Using the James Webb Space Telescope and the Gemini North telescope in Hawaii, they found what looks like the earliest close pair of quasars ever seen.",
    "A quasar is a giant black hole feeding so fast that it outshines all the stars in its galaxy.",
    "We're seeing this pair as it was just nine hundred million years after the Big Bang, when the universe was a thirteenth of its age.",
    "The two are about eighteen thousand light-years apart. The bigger one is about one and a half billion times the mass of our Sun!",
    "The team gathered Gemini's data in just two nights, because the sky over Mauna Kea was so clean and sharp.",
    "The pair got a Hawaiian name about two powerful dark bodies sending energy into the universe.",
    "Scientists still need to rule out a trick of the light, but if it's real, it's a cosmic lab for how the first giant galaxies grew.",
    "Follow for a little good news every day.",
]
STARTS = [0, 7.159, 17.1914, 24.7422, 33.2596, 41.9337, 49.7196, 56.539, 65.84]
DURS = [6.609, 9.4824, 7.0008, 7.9673, 8.1241, 7.2359, 6.2694, 8.751, 2.5861]
TOTAL = 69.026

SPACE = make_space_bg(seed=7)
SPACE2 = make_space_bg(seed=40, top=(12, 8, 40), bot=(70, 30, 90))
MK = make_mountain_night_bg()
NAME = "NĀPŌWAWĀʻENAKAULUA"


def pair(img, t, cx=480, cy=1000, sep=220, r=70, orbit=True):
    a = t * 0.6 if orbit else 0
    dx, dy = math.cos(a) * sep, math.sin(a) * sep * 0.35
    draw_quasar(img, cx - dx, cy - dy, r, t)
    draw_quasar(img, cx + dx, cy + dy, r * 0.7, t + 1, col=(255, 170, 120), jet=(200, 160, 255))


def s0(t, lt):
    img = SPACE.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t)
    sc = ease_out(prog(lt, 0.0, 1.2))
    pair(img, t, cy=1050, sep=60 + 190 * sc, r=50 + 60 * sc)
    sticker(img, 480, 330, "2 MONSTER", 120, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 480, 520, "BLACK HOLES!", 100, C["pink"], fg=C["white"], scale=pop(prog(lt, 1.0, 0.35)), rot=2)
    return img


def s1(t, lt):
    img = MK.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t, seed=3)
    draw_webb(img, 330 + 20 * math.sin(lt), 800 + 15 * math.sin(lt * 1.3), 0.75 * pop(prog(lt, 0.3, 0.5)), rot=-8)
    d = ImageDraw.Draw(img)
    draw_telescope_dome(d, 700, 1150, 0.9)
    # beams to a tiny pair in the corner
    if lt > 3.5:
        draw_quasar(img, 840, 620, 28, t); draw_quasar(img, 900, 650, 20, t + 1)
    sticker(img, 300, 1010, "JAMES WEBB", 58, C["yellow"], scale=pop(prog(lt, 0.6, 0.35)), rot=-3)
    sticker(img, 690, 1280, "GEMINI NORTH", 54, C["white"], scale=pop(prog(lt, 2.2, 0.35)), rot=3)
    sticker(img, 480, 330, "EARLIEST CLOSE PAIR", 74, C["pink"], fg=C["white"], scale=pop(prog(lt, 5.0, 0.35)), rot=-2)
    sticker(img, 480, 500, "OF QUASARS", 84, C["white"], scale=pop(prog(lt, 6.2, 0.35)), rot=2)
    return img


def s2(t, lt):
    img = SPACE2.copy(); d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    dim = prog(lt, 2.0, 3.0)
    for i in range(160):  # the host galaxy's stars
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(60, 380) ** 1.0
        x = 480 + math.cos(a + t * 0.1) * r; y = 1000 + math.sin(a + t * 0.1) * r * 0.45
        b = int(255 - 150 * dim)
        rr = rnd.uniform(3, 6)
        d.ellipse([S(x - rr), S(y - rr), S(x + rr), S(y + rr)], fill=(b, b, min(255, b + 30)))
    g = 30 + 60 * ease_out(prog(lt, 1.6, 3.0))
    draw_quasar(img, 480, 1000, g, t)
    sticker(img, 480, 330, "QUASAR =", 110, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "A FEEDING BLACK HOLE", 66, C["white"], scale=pop(prog(lt, 1.0, 0.35)), rot=2)
    sticker(img, 480, 700, "OUTSHINES THE STARS!", 62, C["pink"], fg=C["white"], scale=pop(prog(lt, 4.4, 0.35)), rot=-1)
    return img


def s3(t, lt):
    img = SPACE.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t)
    x0, x1, y = 120, 860, 1000
    d.rounded_rectangle([S(x0), S(y - 26), S(x1), S(y + 26)], radius=S(26), fill=(60, 60, 110), outline=C["white"], width=S(5))
    p = ease_out(prog(lt, 0.4, 2.0))
    xm = x0 + (x1 - x0) / 13
    d.rounded_rectangle([S(x0), S(y - 26), S(x0 + (xm - x0) * p + 1), S(y + 26)], radius=S(26), fill=C["yellow"])
    # big bang burst at the start
    for i in range(10):
        a = i * math.pi / 5 + lt
        d.line([(S(x0), S(y)), (S(x0 + math.cos(a) * 70), S(y + math.sin(a) * 70))], fill=C["orange"], width=S(8))
    text_center(d, x0 + 20, y + 90, "BIG BANG", 40, fill=C["white"])
    text_center(d, x1 - 40, y + 90, "TODAY", 40, fill=C["white"])
    if p > 0.5:
        draw_quasar(img, xm, y - 160, 38, t)
        d = ImageDraw.Draw(img)
        d.line([(S(xm), S(y - 110)), (S(xm), S(y - 30))], fill=C["white"], width=S(6))
    sticker(img, 480, 330, "900 MILLION YEARS", 80, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 500, "AFTER THE BIG BANG", 66, C["white"], scale=pop(prog(lt, 1.6, 0.35)), rot=2)
    sticker(img, 480, 1260, "1/13 OF ITS AGE", 80, C["teal"], fg=C["white"], scale=pop(prog(lt, 4.6, 0.35)), rot=-1)
    return img


def s4(t, lt):
    return xcut(t, lt, 4.0, _s4_a, _s4_b)


def _s4_a(t, lt):
    img = SPACE2.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t, seed=8)
    draw_quasar(img, 200, 1000, 90, t); draw_quasar(img, 780, 1000, 65, t + 1, col=(255, 170, 120), jet=(200, 160, 255))
    d = ImageDraw.Draw(img)
    p = ease_in_out(prog(lt, 0.4, 1.6))
    d.line([(S(300), S(1180)), (S(300 + 380 * p), S(1180))], fill=C["yellow"], width=S(12))
    for k in range(int(380 * p / 38)):
        d.line([(S(310 + k * 38), S(1166)), (S(310 + k * 38), S(1194))], fill=C["ink"], width=S(4))
    sticker(img, 480, 380, "~18,000", 130, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 580, "LIGHT-YEARS APART", 70, C["white"], scale=pop(prog(lt, 1.0, 0.35)), rot=2)
    return img


def _s4_b(t, l2):
    lt = l2 + 4.0
    img = SPACE2.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t, seed=8)
    l2 = lt - 4.0
    draw_quasar(img, 280, 1050, 130, t)
    d = ImageDraw.Draw(img)
    n = int(20 * ease_out(prog(l2, 0.4, 2.0)))
    for i in range(n):
        x = 560 + (i % 5) * 80; y = 880 + (i // 5) * 80
        d.ellipse([S(x - 26), S(y - 26), S(x + 26), S(y + 26)], fill=C["sun"], outline=C["ink"], width=S(4))
    sticker(img, 480, 380, "1.5 BILLION", 120, C["yellow"], scale=pop(prog(l2, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 580, "TIMES OUR SUN!", 80, C["pink"], fg=C["white"], scale=pop(prog(l2, 0.9, 0.35)), rot=2)
    return img

def s5(t, lt):
    img = MK.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t, seed=2, n=40)
    draw_telescope_dome(d, 480, 1180, 1.2)
    # night counter with moon crossing twice
    k = lt / 3.6
    for i in range(2):
        p = clamp(k - i)
        if 0 < p < 1:
            mx = 100 + 800 * p; my = 760 - 200 * math.sin(p * math.pi)
            d.ellipse([S(mx - 50), S(my - 50), S(mx + 50), S(my + 50)], fill=(255, 246, 200))
    n = 1 if k < 1 else 2
    sticker(img, 480, 330, f"{n} NIGHT{'S' if n > 1 else ''}", 120, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 700, "MAUNA KEA, HAWAII", 62, C["white"], scale=pop(prog(lt, 4.0, 0.35)), rot=2)
    sticker(img, 480, 515, "CLEAN, SHARP SKY", 70, C["teal"], fg=C["white"], scale=pop(prog(lt, 4.8, 0.35)), rot=-1)
    return img


def s6(t, lt):
    img = SPACE.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t)
    pair(img, t, cy=1080, sep=220, r=85)
    sticker(img, 480, 330, "A HAWAIIAN NAME", 90, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 540, NAME, 52, C["white"], scale=pop(prog(lt, 1.2, 0.35)), rot=1)
    sticker(img, 480, 720, "TWO POWERFUL DARK BODIES", 50, C["pink"], fg=C["white"], scale=pop(prog(lt, 2.8, 0.35)), rot=-1)
    return img


def s7(t, lt):
    return xcut(t, lt, 4.0, _s7_a, _s7_b)


def _s7_a(t, lt):
    img = SPACE2.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t, seed=5)
    pair(img, t, cy=1020, sep=220, r=80)
    d = ImageDraw.Draw(img)
    draw_magnifier(d, 480 + 200 * math.sin(lt * 1.5), 1000, 150, rot=0.2 * math.sin(lt))
    sticker(img, 480, 330, "TRICK OF THE LIGHT?", 76, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "STILL CHECKING", 76, C["yellow"], scale=pop(prog(lt, 1.2, 0.35)), rot=2)
    return img


def _s7_b(t, l2):
    lt = l2 + 4.0
    img = SPACE2.copy(); d = ImageDraw.Draw(img)
    draw_twinkles(d, t, seed=5)
    pair(img, t, cy=1020, sep=220, r=80)
    d = ImageDraw.Draw(img)
    l2 = lt - 4.0
    sticker(img, 480, 330, "IF IT'S REAL...", 90, C["yellow"], scale=pop(prog(l2, 0.0, 0.35)), rot=-2)
    sticker(img, 480, 520, "A COSMIC LAB!", 100, C["teal"], fg=C["white"], scale=pop(prog(l2, 0.8, 0.35)), rot=2)
    return img

def s8(t, lt):
    img = SPACE.copy(); d = ImageDraw.Draw(img)  # mirrors the hook for the loop
    draw_twinkles(d, t)
    pair(img, t, cy=1050, sep=250, r=110)
    sticker(img, 480, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
    sticker(img, 480, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    return img


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8]
if __name__ == "__main__":
    run("ep007", "earliest_quasar_pair", LINES, STARTS, DURS, TOTAL, SCENES, f"{REPO}/out/ep007/vo.wav")
