"""Episode 008: Stephanie Case becomes the first woman to finish the 100-mile Antarctic Ice Ultra (Nov 2026)."""
import math, random
from PIL import Image, ImageDraw
from toon import *
from epkit import run, REPO

LINES = [
    "One hundred miles. Nonstop. In Antarctica!",
    "Canadian ultrarunner Stephanie Case just became the first woman to finish the hundred-mile Antarctic Ice Ultra.",
    "The race runs from a camp in Queen Maud Land, in East Antarctica, at about seventy degrees south, under twenty-four hours of daylight.",
    "Temperatures were around minus thirty degrees Celsius, and runners got checked for frostbite on their fingers, noses and ears.",
    "Stephanie finished in seventeen hours and thirty-one minutes. That's second overall, less than half an hour behind the winner!",
    "Her time was more than five hours faster than the previous overall record.",
    "Only four of the eight runners who started the hundred-mile race made it to the finish.",
    "She's a human rights lawyer, a mom to a young daughter, and the founder of Free to Run, a charity that helps women in conflict areas through running.",
    "Her message to other moms? Motherhood isn't the finish line.",
    "Follow for a little good news every day.",
]
STARTS = [0, 5.1476, 12.9335, 21.7643, 30.2033, 38.799, 44.1033, 49.7994, 59.1788, 63.9345]
DURS = [4.5976, 7.2359, 8.2808, 7.889, 8.0457, 4.7543, 5.1461, 8.8294, 4.2057, 2.5861]
TOTAL = 67.121

ICE = make_ice_bg()
GROUND = 1330
JACKET = (255, 90, 120)
HAT = (80, 160, 255)


def runner(d, x, lt, scale=1.5, facing=1, arms_up=0.0, run_=1.0):
    draw_person(d, x, GROUND, scale=scale, phase=lt * 11, facing=facing, body=JACKET, hat=HAT, run=run_, arms_up=arms_up)


def footprints(d, lt, speed=300):
    for i in range(14):
        x = (i * 90 - lt * speed) % (W + 100) - 50
        E2(d, x - 14, GROUND + 14 + (i % 2) * 18, x + 14, GROUND + 26 + (i % 2) * 18, fill=(205, 220, 240))


def s0(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)
    footprints(d, lt)
    runner(d, 480, lt, scale=1.7)
    draw_snow(d, t, wind=-120)
    sticker(img, 480, 330, "100 MILES", 130, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 480, 530, "NONSTOP", 100, C["white"], scale=pop(prog(lt, 1.4, 0.35)), rot=2)
    sticker(img, 480, 700, "IN ANTARCTICA!", 80, C["teal"], fg=C["white"], scale=pop(prog(lt, 2.6, 0.35)), rot=-1)
    return img


def s1(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)
    # finish arch
    for x in (180, 800):
        d.rectangle([S(x - 18), S(850), S(x + 18), S(GROUND)], fill=(80, 90, 110), outline=C["ink"], width=S(5))
    d.rounded_rectangle([S(140), S(820), S(840), S(930)], radius=S(20), fill=C["pink"], outline=C["ink"], width=S(6))
    text_center(d, 490, 875, "FINISH", 70, fill=C["white"])
    p = ease_out(prog(lt, 0.2, 3.0))
    runner(d, -100 + 640 * p, lt, scale=1.4, arms_up=prog(lt, 3.0, 0.4), run_=1 - prog(lt, 3.0, 0.4))
    draw_confetti(d, lt, 3.1)
    sticker(img, 480, 330, "FIRST WOMAN!", 110, C["yellow"], scale=pop(prog(lt, 3.2, 0.35)), rot=-3)
    sticker(img, 480, 520, "100-MILE ANTARCTIC ICE ULTRA", 46, C["white"], scale=pop(prog(lt, 4.4, 0.35)), rot=2)
    return img


def s2(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)
    draw_tent(d, 260, GROUND, 1.0); draw_tent(d, 520, GROUND, 0.8, col=(255, 206, 60)); draw_tent(d, 760, GROUND, 1.1, col=(80, 160, 255))
    draw_flag(d, 900, GROUND, t)
    # the sun circles but never sets
    a = lt * 0.9
    sx, sy = 480 + 330 * math.cos(a), 800 + 90 * math.sin(a)
    for i in range(12):
        aa = i * math.pi / 6 + lt
        d.line([(S(sx + math.cos(aa) * 70), S(sy + math.sin(aa) * 70)), (S(sx + math.cos(aa) * 100), S(sy + math.sin(aa) * 100))], fill=(255, 200, 60), width=S(8))
    d.ellipse([S(sx - 55), S(sy - 55), S(sx + 55), S(sy + 55)], fill=C["sun"], outline=C["ink"], width=S(5))
    sticker(img, 480, 330, "QUEEN MAUD LAND", 84, C["white"], scale=pop(prog(lt, 0.3, 0.35)), rot=-2)
    sticker(img, 480, 510, "~70° SOUTH", 90, C["teal"], fg=C["white"], scale=pop(prog(lt, 2.6, 0.35)), rot=2)
    sticker(img, 480, 1060, "24-HOUR DAYLIGHT", 70, C["yellow"], scale=pop(prog(lt, 5.0, 0.35)), rot=-1)
    return img


def s3(t, lt):
    img = vgrad(SW, SH, (120, 170, 230), (220, 236, 255)).convert("RGBA"); d = ImageDraw.Draw(img)
    draw_snow(d, t, n=90, wind=-200)
    draw_thermometer(d, 220, 950, 420, 0.15, col=(80, 160, 255))
    # frostbite check badges
    for i, (lab, tt) in enumerate([("FINGERS", 3.6), ("NOSE", 4.6), ("EARS", 5.5)]):
        sc = pop(prog(lt, tt, 0.35))
        if sc > 0.02:
            cx, cy = 640, 760 + i * 190
            d.ellipse([S(cx - 70 * sc), S(cy - 70 * sc), S(cx + 70 * sc), S(cy + 70 * sc)], fill=C["white"], outline=C["ink"], width=S(6))
            if sc > 0.9:
                d.line([(S(cx - 30), S(cy)), (S(cx - 8), S(cy + 24)), (S(cx + 32), S(cy - 26))], fill=(60, 190, 100), width=S(14))
            sticker(img, cx + 190, cy, lab, 46, C["yellow"], scale=sc, rot=-2)
    sticker(img, 480, 330, "-30°C", 150, C["white"], fg=(40, 110, 220), scale=pop(prog(lt, 0.2, 0.35)), rot=-3)
    sticker(img, 480, 540, "FROSTBITE CHECKS", 72, C["pink"], fg=C["white"], scale=pop(prog(lt, 3.0, 0.35)), rot=2)
    return img


def s4(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)
    frac = ease_out(prog(lt, 0.2, 3.2))
    hh = int(17 * frac); mm = int(31 * frac)
    if lt < 3.8:
        draw_stopwatch(d, 250, 900, 120, frac)
        sticker(img, 640, 890, f"{hh}H {mm:02d}M", 90, C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    else:
        sticker(img, 480, 720, "17H 31M", 90, C["white"], scale=1.0, rot=-2)
    # podium
    pa = pop(prog(lt, 3.8, 0.4))
    if pa > 0.02:
        for (x, h, lab, col) in [(300, 200, "2", (200, 210, 225)), (500, 280, "1", C["yellow"]), (700, 150, "3", (220, 160, 110))]:
            d.rectangle([S(x - 90), S(GROUND - h * pa), S(x + 90), S(GROUND)], fill=col, outline=C["ink"], width=S(6))
            text_center(d, x, GROUND - h * pa + 50, lab, 70 * pa)
        draw_person(d, 300, GROUND - 200 * pa, scale=1.0 * pa, body=JACKET, hat=HAT, arms_up=0.7)
    sticker(img, 480, 330, "2ND OVERALL", 100, C["yellow"], scale=pop(prog(lt, 4.0, 0.35)), rot=2)
    sticker(img, 480, 520, "< 30 MIN BEHIND", 76, C["teal"], fg=C["white"], scale=pop(prog(lt, 5.4, 0.35)), rot=-2)
    return img


def s5(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)
    g = ease_out(prog(lt, 0.3, 1.6))
    draw_bar(d, 330, GROUND, 200, 520 * g, (180, 190, 210), "OLD RECORD")
    draw_bar(d, 650, GROUND, 200, 400 * g, JACKET, "STEPHANIE")
    if lt > 2.0:
        d.line([(S(330), S(GROUND - 520)), (S(650), S(GROUND - 520))], fill=C["ink"], width=S(6))
        d.line([(S(650), S(GROUND - 520)), (S(650), S(GROUND - 410))], fill=C["ink"], width=S(6))
    sticker(img, 480, 330, "5+ HOURS", 120, C["yellow"], scale=pop(prog(lt, 1.4, 0.35)), rot=-2)
    sticker(img, 480, 520, "FASTER THAN THE RECORD", 56, C["white"], scale=pop(prog(lt, 2.0, 0.35)), rot=2)
    return img


def s6(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)
    draw_snow(d, t, n=40)
    for i in range(8):
        x = 140 + (i % 4) * 230; y = 980 + (i // 4) * 330
        fin = i in (0, 2, 5, 7)
        lit = fin and lt > 1.5 + 0.4 * [0, 2, 5, 7].index(i) if fin else False
        draw_person(d, x, y, scale=0.85, body=JACKET if lit else (170, 175, 190), hat=HAT if lit else (150, 155, 170), arms_up=0.8 if lit else 0.0)
    sticker(img, 480, 330, "4 OF 8", 140, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 530, "FINISHED", 90, C["white"], scale=pop(prog(lt, 1.0, 0.35)), rot=2)
    return img


def badge(img, cx, cy, sc, kind, col):
    if sc <= 0.02: return
    lay = Image.new("RGBA", (S(240), S(240)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.ellipse([S(10), S(16), S(236), S(240)], fill=C["ink"])
    ld.ellipse([S(4), S(4), S(226), S(226)], fill=col, outline=C["ink"], width=S(7))
    ink = C["ink"]
    if kind == "scales":
        ld.line([(S(115), S(60)), (S(115), S(170))], fill=ink, width=S(10))
        ld.line([(S(55), S(80)), (S(175), S(80))], fill=ink, width=S(10))
        for x in (55, 175):
            ld.chord([S(x - 32), S(100), S(x + 32), S(150)], 0, 180, fill=C["white"], outline=ink, width=S(5))
            ld.line([(S(x), S(80)), (S(x - 28), S(122))], fill=ink, width=S(4)); ld.line([(S(x), S(80)), (S(x + 28), S(122))], fill=ink, width=S(4))
        ld.rectangle([S(80), S(165), S(150), S(182)], fill=ink)
    elif kind == "heart":
        draw_heart(ld, 115, 120, 62, C["pink"])
    else:  # shoe
        ld.polygon([(S(45), S(150)), (S(60), S(85)), (S(110), S(90)), (S(130), S(120)), (S(190), S(135)), (S(190), S(160)), (S(45), S(165))], fill=C["white"], outline=ink, width=S(6))
        ld.line([(S(70), S(110)), (S(105), S(108))], fill=ink, width=S(5))
    paste_scaled(img, lay, cx, cy, sc)


def s7(t, lt):
    img = vgrad(SW, SH, (255, 214, 200), (255, 240, 220)).convert("RGBA"); d = ImageDraw.Draw(img)
    sunburst(d, 480, 1000, lt, (255, 226, 214), speed=0.2)
    items = [("scales", 0.2, "HUMAN RIGHTS LAWYER", (200, 220, 255)), ("heart", 2.6, "MOM", (255, 230, 240)), ("shoe", 4.6, "FOUNDED FREE TO RUN", (210, 250, 230))]
    for i, (kind, tt, lab, col) in enumerate(items):
        y = 720 + i * 250
        sc = pop(prog(lt, tt, 0.4))
        badge(img, 230, y, sc, kind, col)
        sticker(img, 620, y, lab, 50 if len(lab) > 10 else 70, C["white"], scale=sc, rot=-2 + 2 * i)
    sticker(img, 480, 330, "MEET STEPHANIE", 90, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-2)
    return img


def s8(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)
    sunburst(d, 480, 1100, lt, (226, 240, 255), speed=0.3)
    draw_person(d, 480, GROUND, scale=1.8, body=JACKET, hat=HAT, arms_up=0.8 + 0.2 * math.sin(lt * 5))
    for i in range(6):
        draw_heart(d, 150 + i * 140, 1000 + 40 * math.sin(lt * 3 + i), 26 * pop(prog(lt, 0.8 + i * 0.15, 0.3)))
    sticker(img, 480, 330, "MOTHERHOOD ISN'T", 84, C["white"], scale=pop(prog(lt, 1.0, 0.35)), rot=-2)
    sticker(img, 480, 520, "THE FINISH LINE", 90, C["pink"], fg=C["white"], scale=pop(prog(lt, 2.2, 0.35)), rot=2)
    return img


def s9(t, lt):
    img = ICE.copy(); d = ImageDraw.Draw(img)  # mirrors the hook for the loop
    footprints(d, lt)
    runner(d, 480, lt, scale=1.7)
    draw_snow(d, t, wind=-120)
    sticker(img, 480, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
    sticker(img, 480, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    return img


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
if __name__ == "__main__":
    run("ep008", "first_woman_antarctic_100_miler", LINES, STARTS, DURS, TOTAL, SCENES, f"{REPO}/out/ep008/vo.wav")
