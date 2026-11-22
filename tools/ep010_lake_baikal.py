"""Episode 010: Tree rings show Lake Baikal's rivers making their strongest recovery in 343 years (GRL, Nov 2026)."""
import math, random
from PIL import Image, ImageDraw
from toon import *
from epkit import run, REPO

LINES = [
    "The world's oldest lake is getting its water back!",
    "Lake Baikal in Siberia is about twenty-five million years old, and holds about a fifth of all the unfrozen fresh water on Earth.",
    "For about two decades, the rivers flowing into and out of the lake carried less and less water.",
    "To read the lake's history, scientists took tiny cores from pine trees nearby. Their growth rings record wet and dry years.",
    "Their tree-ring record stretches back three hundred forty-three years.",
    "And it shows that since around 2017, the lake's rivers have made their strongest recovery in that whole record.",
    "Scientists led by Yunnan University in China published the study in Geophysical Research Letters.",
    "The team links it to shifting weather patterns bringing more moisture. They don't know yet if it will last.",
    "But that water matters for farms and hydropower across the region, so it's a big splash of good news.",
    "Follow for a little good news every day.",
]
STARTS = [0, 3.9459, 13.2469, 20.0663, 28.8971, 34.1231, 41.5955, 48.3365, 54.9208, 62.8635]
DURS = [3.3959, 8.751, 6.2694, 8.2808, 4.6759, 6.9224, 6.191, 6.0343, 7.3927, 2.5861]
TOTAL = 66.05

LAKE0 = make_lake_bg(level=0.0)
FOREST = vgrad(SW, SH, (150, 210, 255), (230, 246, 255)).convert("RGBA")
_d = ImageDraw.Draw(FOREST)
wavy_band(_d, 1250, 20, 500, 0.4, (110, 180, 100))
LAB = vgrad(SW, SH, (240, 236, 220), (220, 214, 196)).convert("RGBA")


def lake(level, t=0.0):
    """lake backdrop with a smoothly moving water line and drifting ripples"""
    img = LAKE0.copy(); d = ImageDraw.Draw(img)
    wl = 1180 - 60 * clamp(level)
    d.rectangle([0, S(wl), SW, SH], fill=(50, 130, 210))
    d.rectangle([0, S(wl), SW, S(wl + 18)], fill=(130, 200, 250))
    rnd = random.Random(12)
    for i in range(14):
        y = wl + 60 + rnd.uniform(0, 520); w = rnd.uniform(50, 120); sp = rnd.uniform(15, 35)
        x = (rnd.uniform(0, W + 200) + t * sp) % (W + 200) - 100
        d.rounded_rectangle([S(x - w / 2), S(y - 4), S(x + w / 2), S(y + 4)], radius=S(4), fill=(110, 180, 240))
    return img


def splash(d, t, x, y, n=6):
    for i in range(n):
        p = (t * 1.2 + i / n) % 1
        a = math.pi * (0.2 + 0.6 * i / max(1, n - 1))
        dx, dy = math.cos(a) * 160 * p, -math.sin(a) * 260 * p + 300 * p * p
        draw_drop(d, x + dx * (1 if i % 2 else -1), y + dy, 18 * (1 - p * 0.5))


def mascot(d, x, y, s, t):
    """happy water-drop buddy"""
    b = abs(math.sin(t * 3)) * 30
    draw_drop(d, x, y - b, s)
    for ex in (-0.35, 0.35):
        E2(d, x + ex * s - s * 0.12, y - b - s * 0.15, x + ex * s + s * 0.12, y - b + s * 0.12, fill=C["ink"])
    d.arc([S(x - s * 0.35), S(y - b), S(x + s * 0.35), S(y - b + s * 0.5)], 20, 160, fill=C["ink"], width=int(S(s * 0.08)))
    E2(d, x - s * 0.7, y - b + s * 0.1, x - s * 0.45, y - b + s * 0.28, fill=(255, 150, 170))
    E2(d, x + s * 0.45, y - b + s * 0.1, x + s * 0.7, y - b + s * 0.28, fill=(255, 150, 170))


def s0(t, lt):
    img = lake(ease_out(prog(lt, 0.3, 2.8)), t); d = ImageDraw.Draw(img)
    draw_clouds(d, t)
    splash(d, lt, 480, 1240)
    mascot(d, 480, 1050, 110 * pop(prog(lt, 0.4, 0.4)) + 1, t)
    sticker(img, 480, 330, "OLDEST LAKE", 120, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 480, 530, "WATER'S BACK!", 100, C["teal"], fg=C["white"], scale=pop(prog(lt, 1.4, 0.35)), rot=2)
    return img


def s1(t, lt):
    return xcut(t, lt, 3.6, _s1_a, _s1_b)


def _s1_a(t, lt):
    img = lake(0.6, t); d = ImageDraw.Draw(img)
    draw_clouds(d, t)
    mascot(d, 480, 1060, 90, t)
    sticker(img, 480, 330, "LAKE BAIKAL, SIBERIA", 74, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 530, "~25 MILLION YEARS OLD", 66, C["yellow"], scale=pop(prog(lt, 1.6, 0.35)), rot=2)
    return img


def _s1_b(t, l2):
    lt = l2 + 3.6
    img = lake(0.6, t); d = ImageDraw.Draw(img)
    draw_clouds(d, t)
    l2 = lt - 3.6
    cx, cy, r = 480, 820, 190
    d.ellipse([S(cx - r + 10), S(cy - r + 14), S(cx + r + 10), S(cy + r + 14)], fill=C["ink"])
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=(200, 230, 255), outline=C["ink"], width=S(7))
    ang = 72 * ease_out(prog(l2, 0.2, 1.2))
    if ang > 1:
        d.pieslice([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], -90, -90 + ang, fill=(50, 130, 210), outline=C["ink"], width=S(7))
    sticker(img, 480, 330, "ABOUT 1/5", 120, C["yellow"], scale=pop(prog(l2, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 1100, "OF EARTH'S UNFROZEN FRESH WATER", 44, C["white"], scale=pop(prog(l2, 0.8, 0.35)), rot=1)
    return img

def s2(t, lt):
    p = ease_in_out(prog(lt, 0.3, 4.5))
    img = lake(0.6 - 0.6 * p, t); d = ImageDraw.Draw(img)
    w = 60 - 44 * p
    draw_river(d, [(100, 1060), (180, 1100), (260, 1140), (330, 1180)], w=w)
    draw_river(d, [(640, 1180), (720, 1130), (820, 1090), (960, 1060)], w=w)
    mascot(d, 480, 1100 + 60 * p, 90 - 30 * p, t * (1 - p))
    sticker(img, 480, 330, "~2 DECADES", 110, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 530, "LESS & LESS WATER", 76, C["orange"], fg=C["white"], scale=pop(prog(lt, 2.2, 0.35)), rot=2)
    return img


def s3(t, lt):
    return xcut(t, lt, 4.0, _s3_a, _s3_b)


def _s3_a(t, lt):
    img = FOREST.copy(); d = ImageDraw.Draw(img)
    for x, h in [(120, 420), (330, 520), (880, 480)]:
        draw_pine(d, x, 1290, h)
    draw_pine(d, 640, 1300, 600)
    draw_person(d, 470, 1300, scale=1.5, body=(80, 160, 255), hat=(255, 140, 50), facing=1)
    # corer
    push = 30 * abs(math.sin(lt * 3))
    d.line([(S(560), S(1080)), (S(625 - push * 0.3), S(1080))], fill=(160, 160, 170), width=S(14))
    d.line([(S(560), S(1050)), (S(560), S(1110))], fill=C["ink"], width=S(12))
    sticker(img, 480, 330, "TINY TREE CORES", 92, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    return img


def _s3_b(t, l2):
    lt = l2 + 4.0
    l2 = lt - 4.0
    img = LAB.copy(); d = ImageDraw.Draw(img)
    hl = None
    if l2 > 1.5:
        hl = {1, 4, 7} if int(l2 * 2) % 2 == 0 else {2, 5, 9}
    draw_tree_rings(d, 480, 1000, 330, n=14, highlight=hl)
    sticker(img, 480, 330, "GROWTH RINGS =", 92, C["yellow"], scale=pop(prog(l2, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "WET & DRY YEARS", 80, C["teal"], fg=C["white"], scale=pop(prog(l2, 1.4, 0.35)), rot=2)
    return img

def s4(t, lt):
    img = LAB.copy(); d = ImageDraw.Draw(img)
    zoom = 1 + 0.15 * lt
    draw_tree_rings(d, 480, 1000, 300 * min(zoom, 1.5), n=22)
    n = int(343 * ease_out(prog(lt, 0.3, 2.6)))
    sticker(img, 480, 380, f"{n} YEARS", 140, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 590, "OF RECORDS", 80, C["white"], scale=pop(prog(lt, 1.2, 0.35)), rot=2)
    return img


def s5(t, lt):
    img = vgrad(SW, SH, (210, 236, 255), (170, 214, 250)).convert("RGBA"); d = ImageDraw.Draw(img)
    x0, x1, base, top = 110, 900, 1300, 760
    d.line([(S(x0), S(top - 40)), (S(x0), S(base)), (S(x1 + 20), S(base))], fill=C["ink"], width=S(8))
    rnd = random.Random(5)
    vals = [0.5 + 0.18 * math.sin(i * 0.7) + rnd.uniform(-0.08, 0.08) for i in range(30)]
    vals[22:27] = [0.35, 0.3, 0.28, 0.25, 0.27]
    vals[27:] = [0.6, 0.85, 1.0]
    p = ease_in_out(prog(lt, 0.3, 4.0))
    pos = (len(vals) - 1) * p                     # draw up to a fractional point so the line grows smoothly
    m = int(pos); fr = pos - m
    P_ = lambda i, v: (S(x0 + (x1 - x0) * i / (len(vals) - 1)), S(base - (base - top) * v))
    pts = [P_(i, v) for i, v in enumerate(vals[:m + 1])]
    if m + 1 < len(vals):
        pts.append(P_(m + fr, vals[m] + (vals[m + 1] - vals[m]) * fr))
    if len(pts) > 1:
        d.line(pts, fill=(50, 130, 210), width=S(12), joint="curve")
        hx, hy = pts[-1]
        d.ellipse([hx - S(14), hy - S(14), hx + S(14), hy + S(14)], fill=(50, 130, 210), outline=C["ink"], width=S(4))
    xs = x0 + (x1 - x0) * 27 / 29
    if p > 0.9:
        d.line([(S(xs), S(top - 40)), (S(xs), S(base))], fill=C["pink"], width=S(6))
        text_center(d, xs - 10, base + 40, "2017", 40)
        draw_drop(d, x1, top - 60 + 10 * math.sin(lt * 4), 30)
    sticker(img, 480, 330, "SINCE ~2017", 100, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "STRONGEST RECOVERY", 70, C["teal"], fg=C["white"], scale=pop(prog(lt, 3.6, 0.35)), rot=2)
    return img


def s6(t, lt):
    img = LAB.copy(); d = ImageDraw.Draw(img)
    cp = ease_out(prog(lt, 0.2, 0.6)); sc = 0.88 + 0.12 * cp
    if cp > 0.02:
        lay = Image.new("RGBA", (S(600), S(760)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([S(16), S(22), S(596), S(756)], radius=S(24), fill=C["ink"])
        ld.rounded_rectangle([0, 0, S(580), S(734)], radius=S(24), fill=C["white"], outline=C["ink"], width=S(8))
        text_center(ld, 290, 90, "GEOPHYSICAL", 54); text_center(ld, 290, 150, "RESEARCH LETTERS", 46)
        for y in range(230, 700, 50):
            ld.line([(S(60), S(y)), (S(520 if y % 100 else 380), S(y))], fill=(200, 200, 210), width=S(8))
        paste_scaled(img, lay, 480, 960 + 90 * (1 - cp) + 10 * math.sin(lt * 1.8), sc, rot=-3 + 1.2 * math.sin(lt * 1.3), alpha=cp)
    sticker(img, 480, 330, "THE STUDY", 110, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-2)
    sticker(img, 480, 1300 - 40, "LED BY YUNNAN UNIVERSITY", 50, C["teal"], fg=C["white"], scale=pop(prog(lt, 1.6, 0.35)), rot=2)
    return img


def s7(t, lt):
    img = lake(0.7, t); d = ImageDraw.Draw(img)
    # moist air rolling in
    for i in range(3):
        x = -300 + ((lt * 120 + i * 420) % (W + 600))
        y = 650 + i * 70
        for dx, dy, r in [(0, 0, 90), (90, -40, 110), (190, 0, 85)]:
            E2(d, x + dx - r, y + dy - r * 0.7, x + dx + r, y + dy + r * 0.7, fill=(170, 180, 210), outline=C["ink"], width=S(5))
        for k in range(5):
            ry = y + 80 + ((lt * 400 + k * 60) % 300)
            d.line([(S(x + 30 + k * 40), S(ry)), (S(x + 22 + k * 40), S(ry + 30))], fill=(80, 150, 240), width=S(6))
    sticker(img, 480, 330, "MORE MOISTURE", 96, C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 520, "WILL IT LAST? TBD", 72, C["yellow"], scale=pop(prog(lt, 3.2, 0.35)), rot=2)
    return img


def s8(t, lt):
    img = lake(0.8, t); d = ImageDraw.Draw(img)
    # farm field rows on the left shore, dam on the right
    for i in range(5):
        y = 1080 + i * 22
        d.line([(S(40), S(y)), (S(420), S(y))], fill=(90, 160, 70) if i % 2 else (200, 180, 90), width=S(14))
    d.rectangle([S(640), S(1000), S(960), S(1200)], fill=(200, 200, 210), outline=C["ink"], width=S(7))
    for k in range(3):
        wx = 700 + k * 100
        d.rectangle([S(wx), S(1200), S(wx + 40), S(1200 + 60 + 10 * math.sin(lt * 8 + k))], fill=(130, 200, 255))
    ang = lt * 4
    for k in range(4):
        a = ang + k * math.pi / 2
        d.line([(S(800), S(940)), (S(800 + math.cos(a) * 60), S(940 + math.sin(a) * 60))], fill=C["ink"], width=S(10))
    d.ellipse([S(785), S(925), S(815), S(955)], fill=C["yellow"], outline=C["ink"], width=S(4))
    sticker(img, 250, 900, "FARMS", 70, C["white"], scale=pop(prog(lt, 0.3, 0.35)), rot=-3)
    sticker(img, 800, 800, "HYDROPOWER", 56, C["white"], scale=pop(prog(lt, 1.6, 0.35)), rot=3)
    if lt > 4.2:
        splash(d, lt, 480, 1250)
    sticker(img, 480, 330, "A BIG SPLASH", 100, C["teal"], fg=C["white"], scale=pop(prog(lt, 4.4, 0.35)), rot=-2)
    sticker(img, 480, 520, "OF GOOD NEWS!", 90, C["yellow"], scale=pop(prog(lt, 5.0, 0.35)), rot=2)
    return img


def s9(t, lt):
    img = lake(1.0, t); d = ImageDraw.Draw(img)  # mirrors the hook for the loop
    draw_clouds(d, t)
    splash(d, lt, 480, 1240)
    mascot(d, 480, 1050, 110, t)
    sticker(img, 480, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
    sticker(img, 480, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    return img


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
if __name__ == "__main__":
    run("ep010", "lake_baikal_water_recovery", LINES, STARTS, DURS, TOTAL, SCENES, f"{REPO}/out/ep010/vo.wav")
