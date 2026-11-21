"""Episode 009: Wild-born native oysters found in Scotland's Dornoch Firth for the first time in 100+ years (DEEP, Nov 16, 2026)."""
import math, random
from PIL import Image, ImageDraw
from toon import *
from epkit import run, REPO

LINES = [
    "Baby oysters are back in Scotland, for the first time in over a hundred years!",
    "Wild oysters once filled the Dornoch Firth in the Scottish Highlands, but they were likely fished out in the eighteen hundreds.",
    "So scientists from Heriot-Watt University, the Marine Conservation Society and a local distillery teamed up to bring them back.",
    "Starting in 2017, they placed oysters on the seabed. By October, more than one hundred forty thousand young oysters had been released.",
    "Then, during routine checks, the team found baby oysters that were born right there in the wild.",
    "Some have grown as big as a fifty pence coin. Now that's a reason to shell-ebrate!",
    "Each oyster can filter up to two hundred liters of water a day, and oyster reefs make homes for other sea life.",
    "The team says the oysters are now reproducing, and they'll keep adding young ones until the reef reaches critical mass.",
    "The goal: four million oysters by 2031.",
    "Follow for a little good news every day.",
]
STARTS = [0, 5.9573, 13.5082, 21.9471, 31.4833, 38.1459, 44.4167, 52.1243, 59.5184, 64.1957]
DURS = [5.4073, 7.0008, 7.889, 8.9861, 6.1127, 5.7208, 7.1576, 6.8441, 4.1273, 2.6906]
TOTAL = 67.486

SEA = make_sea_bg(seed=3)
SEPIA = Image.blend(make_sea_bg(seed=5), Image.new("RGBA", (SW, SH), (190, 150, 100, 255)), 0.45)
FLOOR = 1340


def baby_bed(d, lt, n=7, seed=2, start=0.0, scale=1.3):
    rnd = random.Random(seed)
    for i in range(n):
        x = 110 + i * (760 / max(1, n - 1)) + rnd.uniform(-30, 30); y = FLOOR + rnd.uniform(-10, 60)
        sc = pop(prog(lt, start + i * 0.25, 0.4))
        if sc > 0.02:
            draw_oyster(d, x, y, scale * sc * rnd.uniform(0.8, 1.15), open_=0.25 + 0.25 * math.sin(lt * 3 + i), blink=(int(lt * 2 + i) % 7 == 0))


def s0(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    draw_bubbles(d, t)
    baby_bed(d, lt, n=5)
    for i in range(5):
        draw_heart(d, 160 + i * 170, 1120 - (lt * 60 + i * 50) % 260, 22)
    sticker(img, 480, 330, "BABY OYSTERS!", 110, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 480, 530, "BACK IN SCOTLAND", 76, C["white"], scale=pop(prog(lt, 1.4, 0.35)), rot=2)
    sticker(img, 480, 700, "FIRST IN 100+ YEARS", 62, C["teal"], fg=C["white"], scale=pop(prog(lt, 2.8, 0.35)), rot=-1)
    return img


def s1(t, lt):
    vanish = prog(lt, 3.2, 2.0)
    img = SEPIA.copy() if vanish < 0.5 else SEA.copy(); d = ImageDraw.Draw(img)
    rnd = random.Random(1)
    for i in range(16):
        x = 70 + (i % 8) * 125 + rnd.uniform(-20, 20); y = FLOOR - 30 + (i // 8) * 80
        if rnd.random() > vanish:
            draw_oyster(d, x, y, 0.9, face=False)
    # little boat at the surface
    bx = -200 + 1400 * prog(lt, 2.4, 4.0)
    d.polygon([(S(bx - 120), S(170)), (S(bx + 120), S(170)), (S(bx + 90), S(230)), (S(bx - 90), S(230))], fill=(120, 80, 50), outline=C["ink"], width=S(6))
    d.line([(S(bx), S(170)), (S(bx), S(40))], fill=C["ink"], width=S(8))
    if vanish > 0 and vanish < 1:
        d.line([(S(bx + 40), S(200)), (S(bx + 40), S(FLOOR - 60))], fill=(80, 80, 80), width=S(4))
    sticker(img, 480, 400, "DORNOCH FIRTH", 96, C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 590, "FISHED OUT IN THE 1800s", 58, C["pink"], fg=C["white"], scale=pop(prog(lt, 3.6, 0.35)), rot=2)
    return img


def s2(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    draw_bubbles(d, t, seed=8)
    for i, (lab, tt, col) in enumerate([("HERIOT-WATT UNIVERSITY", 1.4, C["white"]), ("MARINE CONSERVATION SOCIETY", 2.8, C["teal"]), ("A LOCAL DISTILLERY", 5.0, C["yellow"])]):
        sticker(img, 480, 560 + i * 170, lab, 48, col, fg=C["white"] if col == C["teal"] else C["ink"], scale=pop(prog(lt, tt, 0.35)), rot=-2 + 2 * i)
    # three helping hands = three divers' bubbles converging on an oyster
    draw_oyster(d, 480, FLOOR + 20, 2.2, open_=0.3 + 0.2 * math.sin(lt * 3))
    sticker(img, 480, 360, "TEAM OYSTER!", 100, C["orange"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    return img


def s3(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    rnd = random.Random(4)
    for i in range(40):
        delay = rnd.uniform(0, 7); x = rnd.uniform(80, 900)
        p = prog(lt, delay, 1.4)
        if p <= 0: continue
        y = 200 + (FLOOR + rnd.uniform(-20, 60) - 200) * ease_out(p)
        draw_oyster(d, x, y, 0.7, face=False)
    n = int(140000 * ease_out(prog(lt, 3.6, 3.6)))
    sticker(img, 480, 380, "SINCE 2017", 100, C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    if lt > 3.4:
        sticker(img, 480, 590, f"{n:,}+ RELEASED", 70, C["yellow"], scale=pop(prog(lt, 3.4, 0.35)), rot=2)
    return img


def s4(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    for i, x in enumerate((180, 420, 760)):
        draw_oyster(d, x, FLOOR + 10, 1.4, face=False)
    mx = 960 - 300 * ease_in_out(prog(lt, 0.3, 2.2))
    found = lt > 2.6
    if found:
        draw_oyster(d, 500, FLOOR - 90, 0.7 * pop(prog(lt, 2.6, 0.4)) + 0.01, open_=0.3)
        for i in range(6):
            a = i * math.pi / 3 + lt * 2
            d.line([(S(500 + math.cos(a) * 80), S(FLOOR - 90 + math.sin(a) * 80)), (S(500 + math.cos(a) * 110), S(FLOOR - 90 + math.sin(a) * 110))], fill=C["yellow"], width=S(8))
    draw_magnifier(d, mx, FLOOR - 100, 130)
    sticker(img, 480, 380, "ROUTINE CHECK...", 84, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    if found:
        sticker(img, 480, 590, "BORN IN THE WILD!", 84, C["pink"], fg=C["white"], scale=pop(prog(lt, 2.8, 0.35)), rot=2)
    return img


def s5(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    sunburst(d, 480, 1100, lt, (90, 190, 230), speed=0.4)
    if lt < 2.4:
        draw_coin(d, 300, 1050, 150)
        draw_oyster(d, 690, 1180, 1.6, open_=0.3)
        sticker(img, 480, 380, "AS BIG AS A 50p", 90, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    else:
        l2 = lt - 2.4
        # gag: oysters in party hats
        for i, x in enumerate((240, 480, 720)):
            y = FLOOR - 20 - 40 * abs(math.sin(l2 * 5 + i))
            draw_oyster(d, x, y, 1.4, open_=0.4)
            hx, hy = x, y - 150
            d.polygon([(S(hx - 34), S(hy)), (S(hx + 34), S(hy)), (S(hx), S(hy - 100))], fill=[C["pink"], C["yellow"], C["teal"]][i], outline=C["ink"], width=S(5))
            d.ellipse([S(hx - 14), S(hy - 114), S(hx + 14), S(hy - 86)], fill=C["white"], outline=C["ink"], width=S(4))
        draw_confetti(d, l2, 0.0)
        sticker(img, 480, 380, "SHELL-EBRATE!", 110, C["yellow"], scale=pop(prog(l2, 0.1, 0.35)), rot=-4)
    return img


def s6(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    clear = prog(lt, 0.6, 3.0)
    if clear < 1:
        img.alpha_composite(Image.new("RGBA", img.size, (120, 130, 90, int(150 * (1 - clear)))))
        d = ImageDraw.Draw(img)
    draw_oyster(d, 480, FLOOR + 10, 2.6, open_=0.35 + 0.15 * math.sin(lt * 6))
    for i in range(10):  # water swirling in
        a = lt * 2 + i * 0.63
        r = 260 - (lt * 90 + i * 30) % 220
        d.ellipse([S(480 + math.cos(a) * r - 10), S(FLOOR - 120 + math.sin(a) * r * 0.5 - 10), S(480 + math.cos(a) * r + 10), S(FLOOR - 120 + math.sin(a) * r * 0.5 + 10)], fill=(200, 240, 255))
    if lt > 3.6:
        for i, (col, y) in enumerate([(C["orange"], 900), (C["yellow"], 1030), (C["pink"], 780)]):
            x = (lt * 150 * (1 if i % 2 else -1) + i * 400) % (W + 200) - 100
            draw_fish(d, x, y, 50, col, facing=1 if i % 2 else -1, t=lt)
    sticker(img, 480, 380, "200 LITERS A DAY", 86, C["teal"], fg=C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 570, "HOMES FOR SEA LIFE", 70, C["white"], scale=pop(prog(lt, 3.8, 0.35)), rot=2)
    return img


def s7(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    for i, x in enumerate((220, 480, 740)):
        draw_oyster(d, x, FLOOR + 10, 1.4, open_=0.3 + 0.2 * math.sin(lt * 3 + i))
    rnd = random.Random(6)
    for i in range(50):  # larvae drifting up
        x0 = rnd.choice((220, 480, 740)) + rnd.uniform(-40, 40)
        p = ((lt * 0.25 + rnd.random()) % 1)
        y = FLOOR - 100 - p * 600; x = x0 + 60 * math.sin(p * 6 + i)
        d.ellipse([S(x - 7), S(y - 7), S(x + 7), S(y + 7)], fill=(255, 240, 200))
    sticker(img, 480, 380, "NOW REPRODUCING", 86, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 570, "MORE ON THE WAY", 74, C["white"], scale=pop(prog(lt, 2.6, 0.35)), rot=2)
    return img


def s8(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    baby_bed(d, lt, n=7, seed=4, scale=1.1)
    n = int(4000000 * ease_out(prog(lt, 0.3, 2.6)))
    sticker(img, 480, 400, f"{n:,}", 120, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 600, "OYSTERS BY 2031", 80, C["white"], scale=pop(prog(lt, 1.6, 0.35)), rot=2)
    return img


def s9(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)  # mirrors the hook for the loop
    draw_bubbles(d, t)
    baby_bed(d, 5 + lt, n=5)
    sticker(img, 480, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
    sticker(img, 480, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    return img


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
if __name__ == "__main__":
    run("ep009", "wild_oysters_scotland", LINES, STARTS, DURS, TOTAL, SCENES, f"{REPO}/out/ep009/vo.wav")
