"""Episode 004: California's first-ever sea turtle nests hatch (olive ridleys, Seal Beach)."""
import math, random
from PIL import Image, ImageDraw
from toon import *
from epkit import run, REPO

LINES = [
    "Baby sea turtles just hatched in California, for the first time ever!",
    "In September, olive ridley sea turtles dug two nests on Orange County beaches, in Seal Beach and Huntington Beach.",
    "Experts say no sea turtle had ever been recorded nesting on a California beach before.",
    "When a tropical storm threatened the nests, teams carefully dug up about two hundred eggs and moved them to the Aquarium of the Pacific in Long Beach.",
    "There, the eggs rested in warm, sand-filled containers. After fifty-eight days, the sand started to wiggle.",
    "The aquarium's vet said it looked like an eruption of baby sea turtles! Fifty-four hatched from the Seal Beach nest.",
    "Before sunrise, the hatchlings were released on the same beach where their nest was found, and scrambled into the waves.",
    "Newborn hatchlings swim nonstop for up to two days, powered by their yolk.",
    "Scientists say warm ocean water likely helped draw their moms this far north.",
    "Follow for a little good news every day.",
]
STARTS = [0, 5.2259, 13.0902, 19.2043, 28.9233, 37.4406, 45.4616, 52.699, 58.578, 64.2741]
DURS = [4.6759, 7.3143, 5.5641, 9.169, 7.9673, 7.471, 6.6873, 5.329, 5.1461, 2.5861]
TOTAL = 67.46

DAY = make_beach_bg()
NIGHT = make_beach_bg(night=True)
DAWN = make_beach_bg(dawn=True)
SEA = make_sea_bg(seed=8)
LAB = vgrad(SW, SH, (200, 236, 255), (150, 210, 240)).convert("RGBA")
GROUND = 1330


def crawlers(d, t, n=6, y0=1300, seed=3, to_sea=True, spd=60):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(140, 900); yy = y0 + rnd.uniform(-60, 120)
        prog_ = (t * spd * rnd.uniform(0.7, 1.2) + rnd.uniform(0, 200)) % 260
        draw_turtle(d, x + 12 * math.sin(t * 4 + i), yy - prog_ * 0.6, scale=1.05, phase=t * 9 + i, ang=-math.pi / 2 + 0.15 * math.sin(t * 4 + i))


def s0(t, lt):
    img = DAY.copy(); d = ImageDraw.Draw(img)
    draw_clouds(d, t); draw_surf(d, t)
    crawlers(d, t, n=6)
    sticker(img, 500, 330, "BABY SEA TURTLES!", 92, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 500, 540, "CALIFORNIA FIRST", 84, C["teal"], fg=C["white"], scale=pop(prog(lt, 1.6, 0.35)), rot=2)
    return img


def s1(t, lt):
    img = NIGHT.copy(); d = ImageDraw.Draw(img)
    draw_surf(d, t, night=True)
    # mom digs: sand flicks
    dig = math.sin(lt * 6)
    for i in range(6):
        p = (lt * 1.4 + i / 6) % 1
        x = 420 - 160 * p; y = 1290 - 180 * p + 260 * p * p
        E2(d, x - 10, y - 10, x + 10, y + 10, fill=(246, 214, 150))
    draw_turtle(d, 520, 1230, scale=2.8, phase=lt * 5, facing=1, adult=True)
    for (x, lab, tt) in [(270, "SEAL BEACH", 1.6), (720, "HUNTINGTON BEACH", 3.4)]:
        sc = pop(prog(lt, tt, 0.4))
        if sc > 0.02:
            d.ellipse([S(x - 26 * sc), S(1040 - 26 * sc), S(x + 26 * sc), S(1040 + 26 * sc)], fill=C["pink"], outline=C["ink"], width=S(5))
            sticker(img, min(max(x, 250), 740), 880 if x < 500 else 960, lab, 44, C["white"], scale=sc, rot=-2 if x < 500 else 2)
    sticker(img, 500, 330, "SEPTEMBER", 96, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 500, 520, "2 NESTS", 110, C["white"], scale=pop(prog(lt, 0.8, 0.35)), rot=2)
    return img


def s2(t, lt):
    img = DAY.copy(); d = ImageDraw.Draw(img)
    sunburst(d, 500, 1150, lt, (255, 236, 160, ), speed=0.25)
    draw_surf(d, t)
    draw_turtle(d, 500, 1230, scale=2.8, phase=lt * 3, adult=True)
    # record book
    b = pop(prog(lt, 1.2, 0.4))
    if b > 0.02:
        lay = Image.new("RGBA", (S(520), S(360)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([S(14), S(20), S(510), S(350)], radius=S(24), fill=C["ink"])
        ld.rounded_rectangle([0, 0, S(496), S(330)], radius=S(24), fill=C["white"], outline=C["ink"], width=S(7))
        ld.line([(S(248), S(10)), (S(248), S(320))], fill=C["ink"], width=S(5))
        for y in range(70, 300, 50):
            ld.line([(S(30), S(y)), (S(220), S(y))], fill=(200, 200, 210), width=S(5))
        text_center(ld, 372, 165, "0", 170, fill=C["pink"])
        paste_scaled(img, lay, 500, 820, b, rot=-4)
    sticker(img, 500, 330, "NEVER RECORDED", 92, C["pink"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 500, 520, "IN CALIFORNIA!", 84, C["yellow"], scale=pop(prog(lt, 0.7, 0.35)), rot=2)
    return img


def s3(t, lt):
    img = vgrad(SW, SH, (70, 80, 120), (150, 160, 190)).convert("RGBA"); d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate([(200, 300), (650, 220), (900, 380)]):
        x2 = x + 30 * math.sin(t + i)
        for dx, dy, r in [(0, 0, 90), (80, -30, 100), (170, 0, 80)]:
            E2(d, x2 + dx - r, y + dy - r * 0.7, x2 + dx + r, y + dy + r * 0.7, fill=(110, 110, 140))
    d.rectangle([0, S(860), SW, S(1180)], fill=(40, 90, 150))
    wavy_band(d, 1180, 16, 400, 0.4, (220, 190, 130))
    for k in range(4):
        ph = t * 3 + k
        yy = 1120 - 60 * k + 20 * math.sin(ph)
        pts = [(S(x), S(yy + 22 * math.sin(x / 70 + ph))) for x in range(-20, W + 40, 30)]
        d.line(pts, fill=C["white"], width=S(10 - k * 2))
    # rain
    rnd = random.Random(1)
    for i in range(50):
        x = (rnd.uniform(0, W) + t * 120) % W; y = (rnd.uniform(0, H) + t * 900) % 1300
        d.line([(S(x), S(y)), (S(x - 14), S(y + 40))], fill=(200, 210, 240), width=S(4))
    # bucket of eggs carried right
    p = ease_in_out(prog(lt, 1.0, 5.0))
    bx = 160 + 660 * p; by = 1290 + 10 * math.sin(lt * 8)
    d.polygon([(S(bx - 120), S(by - 120)), (S(bx + 120), S(by - 120)), (S(bx + 95), S(by + 40)), (S(bx - 95), S(by + 40))], fill=(255, 150, 60), outline=C["ink"], width=S(7))
    for i, (ex, ey) in enumerate([(-60, -130), (0, -150), (60, -130), (-30, -170), (30, -172)]):
        draw_egg(d, bx + ex, by + ey + 20, 30)
    d.arc([S(bx - 120), S(by - 260), S(bx + 120), S(by - 20)], 180, 360, fill=C["ink"], width=S(8))
    sticker(img, 500, 330, "STORM COMING!", 90, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 500, 520, "~200 EGGS", 104, C["white"], scale=pop(prog(lt, 1.6, 0.35)), rot=2)
    sticker(img, 500, 700, "AQUARIUM OF THE PACIFIC", 50, C["teal"], fg=C["white"], scale=pop(prog(lt, 4.5, 0.35)), rot=-1)
    return img


def s4(t, lt):
    img = LAB.copy(); d = ImageDraw.Draw(img)
    d.rectangle([0, S(1250), SW, SH], fill=(120, 150, 180))
    draw_bin(d, 470, 1120, 620, 300)
    wig = prog(lt, 6.0, 1.0)
    for i in range(7):
        bx = 230 + i * 80
        dy = -8 * math.sin(lt * 20 + i) * wig
        E2(d, bx - 34, 1010 + dy, bx + 34, 1040 + dy, fill=(236, 200, 136))
    draw_thermometer(d, 880, 980, 300, 0.7 + 0.05 * math.sin(lt * 2))
    days = 1 + int(57 * ease_in_out(prog(lt, 0.8, 4.5)))
    sticker(img, 470, 760, f"DAY {days}", 120, C["white"], scale=pop(prog(lt, 0.5, 0.35)), rot=-2)
    sticker(img, 470, 330, "WARM & COZY", 92, C["orange"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=2)
    if wig > 0:
        sticker(img, 470, 540, "WIGGLE!", 100, C["yellow"], scale=pop(prog(lt, 6.0, 0.3)), rot=-4)
    return img


def s5(t, lt):
    img = LAB.copy(); d = ImageDraw.Draw(img)
    sunburst(d, 470, 1050, lt, (220, 244, 255), speed=0.5)
    d.rectangle([0, S(1250), SW, SH], fill=(120, 150, 180))
    rnd = random.Random(7)
    for i in range(14):
        delay = rnd.uniform(0, 2.5); x = rnd.uniform(220, 720)
        p = prog(lt, delay, 0.6)
        if p <= 0: continue
        y = 1010 - 260 * math.sin(min(1, p) * math.pi * 0.5) * (1 - 0.5 * prog(lt, delay + 0.6, 2)) + 30 * math.sin(lt * 4 + i)
        draw_turtle(d, x + 40 * math.sin(lt * 2 + i), y, scale=0.85, ang=-math.pi / 2, phase=lt * 10 + i)
    draw_bin(d, 470, 1120, 620, 300)
    draw_confetti(d, lt, 0.2)
    sticker(img, 470, 330, "ERUPTION!", 120, C["pink"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    n = int(54 * ease_out(prog(lt, 3.6, 1.8)))
    if lt > 3.4:
        sticker(img, 470, 540, f"{n} HATCHLINGS", 88, C["yellow"], scale=pop(prog(lt, 3.4, 0.35)), rot=2)
    return img


def s6(t, lt):
    img = DAWN.copy(); d = ImageDraw.Draw(img)
    draw_surf(d, t)
    crawlers(d, t, n=9, y0=1340, seed=11, spd=90)
    sticker(img, 500, 330, "BEFORE SUNRISE", 92, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 500, 520, "BACK HOME!", 96, C["white"], scale=pop(prog(lt, 2.6, 0.35)), rot=2)
    return img


def s7(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    draw_bubbles(d, t)
    for i in range(3):
        x = (-200 + (lt * 160 + i * 380)) % (W + 400) - 200
        draw_turtle(d, x, 900 + i * 170 + 30 * math.sin(lt * 2 + i), scale=1.3, phase=lt * 8 + i)
    draw_clock(d, 820, 1180, 110, prog(lt, 0.5, 4.5))
    sticker(img, 480, 330, "SWIM, SWIM, SWIM!", 84, C["teal"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "UP TO 2 DAYS", 100, C["yellow"], scale=pop(prog(lt, 1.2, 0.35)), rot=2)
    return img


def s8(t, lt):
    img = SEA.copy(); d = ImageDraw.Draw(img)
    # warm water glow + north arrow
    warm = Image.new("RGBA", img.size, (255, 140, 60, int(70 * prog(lt, 0.3, 1.5))))
    img.alpha_composite(warm); d = ImageDraw.Draw(img)
    draw_bubbles(d, t, seed=9)
    for i in range(2):
        y = 1250 - (lt * 70 + i * 260) % 700
        draw_turtle(d, 380 + i * 260, y, scale=1.8, phase=lt * 5 + i, adult=True, ang=-math.pi / 2)
    draw_thermometer(d, 860, 930, 320, 0.45 + 0.4 * ease_out(prog(lt, 0.5, 2.0)))
    ax = 160
    d.polygon([(S(ax), S(700)), (S(ax + 60), S(800)), (S(ax + 22), S(800)), (S(ax + 22), S(1000)), (S(ax - 22), S(1000)), (S(ax - 22), S(800)), (S(ax - 60), S(800))], fill=C["yellow"], outline=C["ink"], width=S(6))
    text_center(d, ax, 1040, "N", 50, fill=C["white"])
    sticker(img, 480, 330, "WARM WATER", 100, C["orange"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 520, "LIKELY HELPED", 80, C["white"], scale=pop(prog(lt, 1.4, 0.35)), rot=2)
    return img


def s9(t, lt):
    img = DAY.copy(); d = ImageDraw.Draw(img)  # same look as the hook so the loop is seamless; d = ImageDraw.Draw(img)
    draw_clouds(d, t); draw_surf(d, t)
    crawlers(d, t, n=6)
    sticker(img, 500, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
    sticker(img, 500, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    return img


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
if __name__ == "__main__":
    run("ep004", "sea_turtles_california", LINES, STARTS, DURS, TOTAL, SCENES, f"{REPO}/out/ep004/vo.wav")
