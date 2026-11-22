"""Episode 006: Two new howler monkey species identified in Brazil's Amazon; one already uses rope bridges over roads."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
from toon import *
from epkit import run, REPO

LINES = [
    "Scientists just found two new kinds of monkey, hiding in plain sight!",
    "They're howler monkeys, famous for loud calls that carry for kilometers through the Amazon rainforest.",
    "Meet the Pantepui red howler and the Mato Grosso red howler, both found in Brazil.",
    "Researchers compared the DNA of eighty-six howler monkeys, plus skulls, fur and maps, and found these two are species of their own.",
    "Big rivers kept monkey groups apart for hundreds of thousands of years, so they slowly became different.",
    "And here's the fun part: one of them was already caught on camera, using a rope bridge built so animals can safely cross roads in Alta Floresta, Brazil.",
    "Thousands of camera-trap photos show capuchins, marmosets and titi monkeys crossing too.",
    "The bridge builders were amazed they'd been helping a brand-new species all along. Now that's a monkey with good road safety!",
    "Scientists say these monkeys are likely endangered, so knowing they exist can help protect them.",
    "Follow for a little good news every day.",
]
STARTS = [0, 5.461, 12.6984, 18.6557, 28.6098, 35.9255, 45.958, 52.1504, 60.9812, 67.5655]
DURS = [4.911, 6.6873, 5.4073, 9.4041, 6.7657, 9.4824, 5.6424, 8.2808, 6.0343, 2.5861]
TOTAL = 70.752

JUNGLE = make_jungle_bg(seed=4)
JUNGLE2 = make_jungle_bg(seed=9)
RED = (200, 70, 40)
GOLD = (214, 150, 60)
LAB = vgrad(SW, SH, (210, 240, 230), (160, 220, 200)).convert("RGBA")


def branch(d, y, x0=-20, x1=W + 20, tilt=0):
    d.line([(S(x0), S(y)), (S(x1), S(y + tilt))], fill=C["ink"], width=S(44))
    d.line([(S(x0), S(y)), (S(x1), S(y + tilt))], fill=(130, 88, 50), width=S(30))
    for x in range(int(x0) + 80, int(x1), 260):
        yy = y + tilt * (x - x0) / (x1 - x0)
        E2(d, x - 60, yy - 70, x + 60, yy - 10, fill=(70, 160, 80), outline=C["ink"], width=S(4))


def road_scene(d, t):
    d.rectangle([0, S(1180), SW, S(1420)], fill=(86, 90, 104))
    for x in range(0, W, 180):
        xx = (x - t * 120) % (W + 180) - 90
        d.rectangle([S(xx), S(1290), S(xx + 90), S(1306)], fill=C["yellow"])
    d.rectangle([0, S(1420), SW, SH], fill=(60, 130, 70))
    for x in (60, 1020):
        d.rectangle([S(x - 20), S(700), S(x + 20), S(1200)], fill=(110, 72, 44), outline=C["ink"], width=S(5))


def s0(t, lt):
    img = JUNGLE.copy(); d = ImageDraw.Draw(img)
    peek = ease_out(prog(lt, 0.3, 1.0))
    draw_monkey(d, 330 + 120 * peek, 1260, scale=2.6, phase=lt * 2, fur=RED)
    E2(d, -80, 980, 420, 1450, fill=(40, 120, 70), outline=C["ink"], width=S(6))
    E2(d, 600, 1050, 1160, 1500, fill=(30, 100, 60), outline=C["ink"], width=S(6))
    draw_magnifier(d, 690 - 60 * math.sin(lt * 2), 960, 120)
    sticker(img, 480, 330, "2 NEW MONKEYS!", 100, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 480, 540, "HIDING IN PLAIN SIGHT", 62, C["white"], scale=pop(prog(lt, 1.8, 0.35)), rot=2)
    return img


def s1(t, lt):
    img = JUNGLE2.copy(); d = ImageDraw.Draw(img)
    branch(d, 1260)
    howl = max(0, math.sin(lt * 3))
    draw_monkey(d, 380, 1240, scale=2.4, phase=lt, fur=RED, howl=howl)
    draw_sound_rings(d, 560, 1100, lt)
    sticker(img, 480, 330, "HOWLER MONKEYS", 96, C["orange"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 540, "HEARD FOR KILOMETERS", 66, C["white"], scale=pop(prog(lt, 2.4, 0.35)), rot=2)
    return img


def s2(t, lt):
    img = JUNGLE.copy(); d = ImageDraw.Draw(img)
    branch(d, 1260, tilt=0)
    a = pop(prog(lt, 0.3, 0.4)); b = pop(prog(lt, 2.0, 0.4))
    if a > 0.02: draw_monkey(d, 250, 1240, scale=1.8 * a, phase=lt * 2, fur=GOLD, facing=1)
    if b > 0.02: draw_monkey(d, 740, 1240, scale=1.8 * b, phase=lt * 2 + 1, fur=RED, facing=-1)
    sticker(img, 260, 760, "PANTEPUI", 60, GOLD, scale=a, rot=-3)
    sticker(img, 260, 860, "RED HOWLER", 44, C["white"], scale=a, rot=-3)
    sticker(img, 700, 760, "MATO GROSSO", 56, RED, fg=C["white"], scale=b, rot=3)
    sticker(img, 700, 860, "RED HOWLER", 44, C["white"], scale=b, rot=3)
    sticker(img, 480, 330, "MEET THE NEW KIDS", 84, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-2)
    sticker(img, 480, 520, "BRAZIL", 90, C["teal"], fg=C["white"], scale=pop(prog(lt, 4.0, 0.35)), rot=2)
    return img


def s3(t, lt):
    img = LAB.copy(); d = ImageDraw.Draw(img)
    draw_dna(d, 260, 1000, 640, lt)
    n = int(86 * ease_out(prog(lt, 0.3, 3.0)))
    # little monkey faces grid filling up
    for i in range(min(n, 30)):
        x = 520 + (i % 5) * 86; y = 760 + (i // 5) * 86
        E2(d, x - 32, y - 32, x + 32, y + 32, fill=RED if i % 3 else GOLD, outline=C["ink"], width=S(4))
        E2(d, x - 16, y - 12, x + 22, y + 22, fill=(90, 50, 40))
    for i, (lab, tt) in enumerate([("SKULLS", 4.6), ("FUR", 5.6), ("MAPS", 6.4)]):
        sticker(img, 300 + i * 220, 1360 - 40, lab, 52, C["white"], scale=pop(prog(lt, tt, 0.3)), rot=-3 + 3 * i)
    sticker(img, 480, 330, f"{n} MONKEYS' DNA", 92, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 540, "2 NEW SPECIES!", 84, C["pink"], fg=C["white"], scale=pop(prog(lt, 7.6, 0.35)), rot=2)
    return img


def s4(t, lt):
    img = vgrad(SW, SH, (110, 190, 110), (70, 150, 80)).convert("RGBA"); d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for i in range(40):
        x, y, r = rnd.uniform(0, W), rnd.uniform(650, 1450), rnd.uniform(30, 60)
        E2(d, x - r, y - r, x + r, y + r, fill=(50, 130, 70))
    wid = 40 + 90 * ease_out(prog(lt, 0.3, 2.0))
    pts = [(500 + 80 * math.sin(y / 160), y) for y in range(600, 1560, 40)]
    draw_river(d, pts, w=wid)
    # groups drift apart & change colour
    p = prog(lt, 1.5, 4.5)
    for side, base in ((-1, RED), (1, RED)):
        col = tuple(int(base[k] + ((GOLD[k] - base[k]) * p if side < 0 else 0)) for k in range(3))
        for j in range(3):
            draw_monkey(d, 500 + side * (190 + 40 * p + j * 70), 900 + j * 180, scale=0.8, phase=lt * 3 + j, fur=col, facing=-side)
    yrs = int(100 + 600 * ease_out(prog(lt, 1.0, 4.0)))
    sticker(img, 480, 330, "BIG RIVERS", 110, C["teal"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "KEPT THEM APART", 76, C["white"], scale=pop(prog(lt, 1.2, 0.35)), rot=2)
    return img


def s5(t, lt):
    img = JUNGLE2.copy(); d = ImageDraw.Draw(img)
    road_scene(d, t)
    draw_rope_bridge(d, 40, 1040, 820, t)
    p = ease_in_out(prog(lt, 0.3, 9.4))
    x = 60 + 920 * p; y = 820 + 40 * math.sin(p * math.pi)
    draw_monkey(d, x, y - 6, scale=1.1, phase=lt * 8, fur=RED)
    draw_camtrap(d, 920, 1060, lt, 0.9)
    for ft in (2.2, 5.6):
        fl = lt - ft
        if 0 <= fl < 0.35:
            k = 1 - fl / 0.35
            glow = Image.new("RGBA", img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
            r = 90 + 160 * (fl / 0.35)
            gd.ellipse([S(920 - r), S(1060 - r), S(920 + r), S(1060 + r)], fill=(255, 255, 230, int(170 * k)))
            img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(S(30))))
    sticker(img, 480, 330, "CAUGHT ON CAMERA!", 86, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "ROPE BRIDGE", 90, C["white"], scale=pop(prog(lt, 3.0, 0.35)), rot=2)
    sticker(img, 480, 1360 - 30, "ALTA FLORESTA, BRAZIL", 52, C["teal"], fg=C["white"], scale=pop(prog(lt, 6.8, 0.35)), rot=-1)
    return img


def polaroid(img, cx, cy, kind, sc, rot, t):
    if sc <= 0.02: return
    k = sc; sc = 0.85 + 0.15 * k; cy = cy + 120 * (1 - k)
    lay = Image.new("RGBA", (S(330), S(380)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rectangle([S(10), S(14), S(326), S(376)], fill=C["ink"])
    ld.rectangle([0, 0, S(316), S(366)], fill=C["white"], outline=C["ink"], width=S(5))
    ld.rectangle([S(20), S(20), S(296), S(280)], fill=(60, 110, 80))
    ld.line([(S(20), S(200)), (S(296), S(214))], fill=(190, 150, 90), width=S(10))
    col, sz, lab = {"capuchin": ((120, 80, 50), 0.9, "CAPUCHIN"), "marmoset": ((150, 140, 120), 0.6, "MARMOSET"), "titi": ((140, 110, 90), 0.8, "TITI")}[kind]
    draw_monkey(ld, 130, 200, scale=sz, phase=t * 3, fur=col, beard=False)
    text_center(ld, 158, 322, lab, 34)
    paste_scaled(img, lay, cx, cy, sc, rot + 8 * (1 - k), alpha=k)


def s6(t, lt):
    img = vgrad(SW, SH, (60, 60, 90), (40, 40, 60)).convert("RGBA"); d = ImageDraw.Draw(img)
    polaroid(img, 280, 840, "capuchin", ease_out(prog(lt, 0.3, 0.5)), 6, t)
    polaroid(img, 690, 900, "marmoset", ease_out(prog(lt, 1.6, 0.5)), -5, t)
    polaroid(img, 470, 1180, "titi", ease_out(prog(lt, 2.8, 0.5)), 3, t)
    sticker(img, 480, 330, "THOUSANDS OF PHOTOS", 74, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-2)
    return img


def s7(t, lt):
    img = JUNGLE2.copy(); d = ImageDraw.Draw(img)
    road_scene(d, t)
    draw_rope_bridge(d, 40, 1040, 820, t)
    # gag: the monkey looks left, looks right, then crosses like a pro
    if lt < 3.0:
        look = 1 if int(lt / 0.75) % 2 == 0 else -1
        draw_monkey(d, 140, 826, scale=1.4, phase=0, fur=RED, facing=look)
    else:
        p = ease_in_out(prog(lt, 3.0, 4.5))
        draw_monkey(d, 140 + 760 * p, 826 + 40 * math.sin(p * math.pi), scale=1.4, phase=lt * 8, fur=RED)
    # crossing sign
    d.rectangle([S(880), S(1000), S(900), S(1180)], fill=(150, 150, 160), outline=C["ink"], width=S(4))
    d.polygon([(S(890), S(870)), (S(990), S(970)), (S(890), S(1070)), (S(790), S(970))], fill=C["yellow"], outline=C["ink"], width=S(6))
    draw_monkey(d, 870, 1000, scale=0.45, fur=C["ink"], beard=False)
    sticker(img, 480, 330, "THEY WERE AMAZED", 84, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "ROAD SAFETY PRO!", 84, C["pink"], fg=C["white"], scale=pop(prog(lt, 5.4, 0.35)), rot=3)
    return img


def s8(t, lt):
    img = JUNGLE.copy(); d = ImageDraw.Draw(img)
    sunburst(d, 480, 1080, lt, (120, 200, 130), speed=0.3)
    branch(d, 1260)
    draw_monkey(d, 300, 1240, scale=1.7, phase=lt * 2, fur=GOLD)
    draw_monkey(d, 660, 1240, scale=1.7, phase=lt * 2 + 1, fur=RED, facing=-1)
    for i in range(5):
        draw_heart(d, 200 + i * 150, 860 + 30 * math.sin(lt * 3 + i), 30 * pop(prog(lt, 1.5 + i * 0.2, 0.3)))
    sticker(img, 480, 330, "LIKELY ENDANGERED", 84, C["orange"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 540, "NOW WE CAN HELP", 80, C["white"], scale=pop(prog(lt, 3.0, 0.35)), rot=2)
    return img


def s9(t, lt):
    img = JUNGLE.copy(); d = ImageDraw.Draw(img)  # mirrors the hook for the loop
    draw_monkey(d, 450, 1260, scale=2.6, phase=lt * 2, fur=RED)
    E2(d, -80, 980, 420, 1450, fill=(40, 120, 70), outline=C["ink"], width=S(6))
    E2(d, 600, 1050, 1160, 1500, fill=(30, 100, 60), outline=C["ink"], width=S(6))
    sticker(img, 480, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
    sticker(img, 480, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    return img


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
if __name__ == "__main__":
    run("ep006", "new_howler_monkeys", LINES, STARTS, DURS, TOTAL, SCENES, f"{REPO}/out/ep006/vo.wav")
