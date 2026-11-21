"""Episode 005: COMAC's 19-seat battery-electric CE-25A makes its first crewed flight (Nov 14, 2026)."""
import math, random
from PIL import Image, ImageDraw
from toon import *
from epkit import run, REPO

LINES = [
    "This nineteen-seat airplane flies on batteries. No jet fuel at all!",
    "It's called the CE-25A, from Chinese planemaker COMAC. On November fourteenth, it made its first flight with people on board.",
    "Two pilots and a flight test engineer took off from Binzhou, in Shandong province.",
    "They stayed in the air for about seventeen minutes and covered about sixty kilometers.",
    "Instead of jet engines, it has ten electric fans, five on each wing. Somebody's gonna need a really long charging cable!",
    "Its cruising speed is about three hundred kilometers per hour.",
    "It's about ten tonnes, and it's designed to fly up to four hundred kilometers, around two hundred fifty miles, between cities.",
    "Before this, it had already made nineteen test flights with nobody aboard. Next up: earning its safety certificate, and China's aviation regulator has accepted its application.",
    "COMAC says the plane behaved normally, and all the results met expectations.",
    "Follow for a little good news every day.",
]
STARTS = [0, 5.9573, 15.3367, 20.8761, 26.4939, 35.4814, 39.7408, 47.9969, 60.0147, 65.6324]
DURS = [5.4073, 8.8294, 4.9894, 5.0678, 8.4376, 3.7094, 7.7061, 11.4678, 5.0678, 2.5861]
TOTAL = 68.819

SKY = vgrad(SW, SH, (90, 170, 255), (210, 238, 255)).convert("RGBA")
RUNWAY = make_runway_bg()
SUNSET = vgrad(SW, SH, (255, 170, 120), (255, 230, 170)).convert("RGBA")


def clouds_fast(d, t, speed=200, seed=2, col=C["white"]):
    rnd = random.Random(seed)
    for i in range(7):
        y = rnd.uniform(250, 1400); s = rnd.uniform(0.6, 1.3)
        x = W + 300 - ((t * speed * s + rnd.uniform(0, 1600)) % (W + 600))
        for dx, dy, r in [(0, 0, 60), (60, -25, 70), (130, 0, 55)]:
            E2(d, x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s, fill=col)


def check(d, x, y, s, col=(60, 190, 100)):
    d.line([(S(x - s), S(y)), (S(x - s * 0.3), S(y + s * 0.7)), (S(x + s), S(y - s * 0.8))], fill=C["ink"], width=max(1, int(S(s * 0.55))), joint="curve")
    d.line([(S(x - s), S(y)), (S(x - s * 0.3), S(y + s * 0.7)), (S(x + s), S(y - s * 0.8))], fill=col, width=max(1, int(S(s * 0.3))), joint="curve")


def skyline(d, x0, base, s=1.0, col=(120, 130, 170)):
    for i, (w, h) in enumerate([(60, 160), (80, 230), (50, 120), (70, 190), (60, 140)]):
        x = x0 + sum(ww for ww, _ in [(60, 0), (80, 0), (50, 0), (70, 0), (60, 0)][:i]) * s
        d.rectangle([S(x), S(base - h * s), S(x + w * s - 6), S(base)], fill=col, outline=C["ink"], width=S(4))
        for wy in range(int(base - h * s + 20), int(base - 10), 34):
            d.rectangle([S(x + 12 * s), S(wy), S(x + 24 * s), S(wy + 12)], fill=(255, 230, 140))


def s0(t, lt):
    img = SKY.copy(); d = ImageDraw.Draw(img)
    clouds_fast(d, t)
    x = -400 + 940 * ease_out(prog(lt, 0.0, 2.2))
    draw_eplane(img, x, 1060 + 20 * math.sin(lt * 2), 0.95, rot=3 * math.sin(lt), t=t)
    draw_battery(ImageDraw.Draw(img), 760, 760, 200, 0.4 + 0.6 * prog(lt, 1.5, 2.0))
    sticker(img, 480, 330, "BATTERY PLANE!", 100, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 400, 540, "NO JET FUEL", 84, C["teal"], fg=C["white"], scale=pop(prog(lt, 2.6, 0.35)), rot=2)
    return img


def s1(t, lt):
    img = RUNWAY.copy(); d = ImageDraw.Draw(img)
    draw_clouds(d, t)
    p = prog(lt, 4.5, 4.0)
    x = 480 + 700 * p ** 2
    draw_eplane(img, x, 1210 - 300 * p ** 2, 0.9, rot=8 * p, t=t)
    sticker(img, 480, 330, "CE-25A", 140, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
    sticker(img, 480, 540, "NOV 14", 96, C["yellow"], scale=pop(prog(lt, 3.6, 0.35)), rot=2)
    sticker(img, 480, 700, "FIRST CREWED FLIGHT", 60, C["pink"], fg=C["white"], scale=pop(prog(lt, 5.0, 0.35)), rot=-1)
    return img


def s2(t, lt):
    img = RUNWAY.copy(); d = ImageDraw.Draw(img)
    draw_clouds(d, t)
    draw_eplane(img, 560, 1060, 0.8, t=0)
    d = ImageDraw.Draw(img)
    for i, (x, col, hat) in enumerate([(230, (60, 90, 160), (60, 90, 160)), (450, (60, 90, 160), (60, 90, 160)), (680, (255, 140, 50), (255, 206, 60))]):
        sc = pop(prog(lt, 0.3 + i * 0.4, 0.35))
        if sc > 0.02:
            draw_person(d, x, 1360, scale=1.05 * sc, body=col, hat=hat, arms_up=0.6 + 0.4 * math.sin(lt * 5 + i), facing=1 if i < 2 else -1)
    sticker(img, 480, 330, "2 PILOTS + 1 ENGINEER", 64, C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 510, "BINZHOU, SHANDONG", 66, C["yellow"], scale=pop(prog(lt, 2.4, 0.35)), rot=2)
    return img


def s3(t, lt):
    img = SKY.copy(); d = ImageDraw.Draw(img)
    clouds_fast(d, t, speed=320)
    draw_eplane(img, 480, 1150 + 30 * math.sin(lt * 1.5), 0.85, rot=-2, t=t)
    d = ImageDraw.Draw(img)
    draw_stopwatch(d, 250, 760, 110, prog(lt, 0.3, 3.0))
    m = int(17 * ease_out(prog(lt, 0.3, 3.0)))
    km = int(60 * ease_out(prog(lt, 2.2, 2.4)))
    sticker(img, 640, 730, f"~{m} MIN", 96, C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    sticker(img, 480, 330, f"~{km} KM", 130, C["yellow"], scale=pop(prog(lt, 2.0, 0.35)), rot=2)
    return img


def s4(t, lt):
    img = SKY.copy(); d = ImageDraw.Draw(img)
    clouds_fast(d, t, speed=120)
    if lt < 4.6:
        # close-up of the wing fans
        draw_eplane(img, 520, 1150, 2.0, t=t)
        sticker(img, 480, 330, "10 ELECTRIC FANS", 86, C["teal"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
        sticker(img, 480, 520, "5 PER WING", 90, C["white"], scale=pop(prog(lt, 1.8, 0.35)), rot=2)
    else:
        l2 = lt - 4.6
        # gag: plane flying off trailing an absurdly long charging cable from a wall plug
        d.rectangle([0, S(1330), SW, SH], fill=(110, 180, 100))
        d.rounded_rectangle([S(80), S(1180), S(200), S(1330)], radius=S(16), fill=C["white"], outline=C["ink"], width=S(6))
        for yy in (1225, 1275):
            d.rectangle([S(120), S(yy), S(160), S(yy + 22)], fill=C["ink"])
        px = 520 + 380 * ease_in_out(prog(l2, 0.2, 3.0)); py = 760 - 120 * prog(l2, 0.2, 3.0)
        pts = [(140, 1250), (220, 1300), (320, 1120)]
        for i in range(1, 12):
            u = i / 11
            pts.append((320 + (px - 420 - 320) * u, 1120 + (py + 60 - 1120) * u + 150 * math.sin(u * math.pi * 3 + l2 * 3) * (1 - u)))
        d.line([(S(x), S(y)) for x, y in pts], fill=C["ink"], width=S(16), joint="curve")
        d.line([(S(x), S(y)) for x, y in pts], fill=(255, 206, 60), width=S(8), joint="curve")
        draw_eplane(img, px, py, 0.7, rot=6, t=t)
        sticker(img, 480, 330, "UH... LONG CABLE?", 84, C["pink"], fg=C["white"], scale=pop(prog(l2, 0.6, 0.35)), rot=-3)
    return img


def s5(t, lt):
    img = SKY.copy(); d = ImageDraw.Draw(img)
    clouds_fast(d, t, speed=700)
    for i in range(10):
        y = 900 + i * 40; x = (W - ((t * 1400 + i * 260) % (W + 400)))
        d.line([(S(x), S(y)), (S(x + 160), S(y))], fill=C["white"], width=S(8))
    draw_eplane(img, 520, 1130, 0.9, rot=-3, t=t)
    v = int(300 * ease_out(prog(lt, 0.2, 2.0)))
    sticker(img, 480, 380, f"{v} KM/H", 140, C["yellow"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
    sticker(img, 480, 600, "CRUISING SPEED", 66, C["white"], scale=pop(prog(lt, 0.9, 0.35)), rot=2)
    return img


def s6(t, lt):
    img = SKY.copy(); d = ImageDraw.Draw(img)
    clouds_fast(d, t, speed=100)
    if lt < 3.2:
        # giant balance scale
        d.rectangle([S(0), S(1340), SW, SH], fill=(110, 180, 100))
        d.polygon([(S(420), S(1340)), (S(600), S(1340)), (S(510), S(1220))], fill=C["ink"])
        tilt = 0.12 * math.sin(lt * 3) * (1 - prog(lt, 0.0, 2.5))
        d.line([(S(150), S(1220 + 300 * tilt)), (S(870), S(1220 - 300 * tilt))], fill=C["ink"], width=S(16))
        draw_eplane(img, 510, 1110, 0.62, rot=0, t=0)
        sticker(img, 480, 380, "~10 TONNES", 130, C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
    else:
        l2 = lt - 3.2
        d.rectangle([0, S(1300), SW, SH], fill=(110, 180, 100))
        skyline(d, 60, 1300, 0.9); skyline(d, 700, 1300, 0.9, col=(150, 120, 170))
        p = ease_in_out(prog(l2, 0.2, 3.8))
        pts = [(S(180 + 640 * u), S(1100 - 380 * math.sin(u * math.pi))) for u in [i / 30 for i in range(int(30 * p) + 1)]]
        if len(pts) > 1:
            d.line(pts, fill=C["pink"], width=S(10))
        ux = 180 + 640 * p; uy = 1100 - 380 * math.sin(p * math.pi)
        draw_eplane(img, ux, uy, 0.35, rot=-30 * math.cos(p * math.pi), t=t)
        sticker(img, 480, 330, "UP TO 400 KM", 110, C["yellow"], scale=pop(prog(l2, 0.1, 0.35)), rot=-2)
        sticker(img, 480, 520, "~250 MILES", 84, C["white"], scale=pop(prog(l2, 1.4, 0.35)), rot=2)
    return img


def s7(t, lt):
    img = RUNWAY.copy(); d = ImageDraw.Draw(img)
    draw_clouds(d, t)
    if lt < 5.0:
        n = 1 + int(18 * ease_out(prog(lt, 0.4, 3.6)))
        for i in range(n):
            x = 140 + (i % 5) * 180; y = 760 + (i // 5) * 150
            draw_eplane(img, x, y + 8 * math.sin(lt * 3 + i), 0.16, t=t)
        sticker(img, 480, 330, f"{n} TEST FLIGHTS", 92, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
        sticker(img, 480, 1380 - 160, "NOBODY ABOARD", 70, C["yellow"], scale=pop(prog(lt, 1.6, 0.35)), rot=2)
    else:
        l2 = lt - 5.0
        sc = pop(prog(l2, 0.1, 0.4))
        if sc > 0.02:
            lay = Image.new("RGBA", (S(620), S(760)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle([S(16), S(22), S(610), S(750)], radius=S(30), fill=C["ink"])
            ld.rounded_rectangle([0, 0, S(594), S(728)], radius=S(30), fill=(255, 250, 235), outline=C["ink"], width=S(8))
            text_center(ld, 297, 110, "SAFETY", 70); text_center(ld, 297, 190, "CERTIFICATE", 62)
            for y in range(280, 520, 56):
                ld.line([(S(80), S(y)), (S(514), S(y))], fill=(210, 200, 180), width=S(8))
            paste_scaled(img, lay, 480, 960, sc, rot=-3)
        st = pop(prog(l2, 2.6, 0.3))
        if st > 0.02:
            sticker(img, 520, 1110, "APPLICATION ACCEPTED", 54, C["pink"], fg=C["white"], scale=st, rot=-12)
        sticker(img, 480, 330, "NEXT UP", 110, C["yellow"], scale=pop(prog(l2, 0.0, 0.35)), rot=2)
    return img


def s8(t, lt):
    img = SKY.copy(); d = ImageDraw.Draw(img)
    clouds_fast(d, t, speed=80)
    lay = Image.new("RGBA", (S(820), S(560)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([S(16), S(22), S(810), S(550)], radius=S(30), fill=C["ink"])
    ld.rounded_rectangle([0, 0, S(794), S(528)], radius=S(30), fill=C["white"], outline=C["ink"], width=S(8))
    for i, txt in enumerate(["BEHAVED NORMALLY", "RESULTS MET", "EXPECTATIONS"]):
        text_center(ld, 450, 120 + i * 140, txt, 60)
    paste_scaled(img, lay, 480, 900, pop(prog(lt, 0.2, 0.4)), rot=-1)
    d = ImageDraw.Draw(img)
    for i, tt in enumerate([1.0, 2.6]):
        if lt > tt:
            check(d, 150, 745 + i * 205, 46 * pop(prog(lt, tt, 0.3)))
    draw_eplane(img, 480, 1300 + 10 * math.sin(lt * 2), 0.55, t=t)
    sticker(img, 480, 330, "COMAC SAYS", 100, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-2)
    return img


def s9(t, lt):
    img = SKY.copy(); d = ImageDraw.Draw(img)  # mirrors the hook for a clean loop
    clouds_fast(d, t)
    draw_eplane(img, 540 + 30 * math.sin(lt), 1060 + 20 * math.sin(lt * 2), 0.95, t=t)
    sticker(img, 480, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
    sticker(img, 480, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    return img


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]
if __name__ == "__main__":
    run("ep005", "electric_plane_first_crewed_flight", LINES, STARTS, DURS, TOTAL, SCENES, f"{REPO}/out/ep005/vo.wav")
