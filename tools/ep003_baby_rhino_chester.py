"""Episode 003: a rare greater one-horned rhino calf is born at Chester Zoo."""
import sys, math, subprocess, os
from PIL import Image, ImageDraw
from toon import *

LINES = [
    "Say hello to a brand-new baby rhino!",
    "Cameras at Chester Zoo in England caught the moment a rare greater one-horned rhino was born.",
    "Mom Asha carried her calf for about fifteen months. Within an hour, the little one was up on its wobbly feet.",
    "Newborns weigh about a hundred pounds, but grown-ups can top two tons. That's as heavy as a car!",
    "Only about four thousand of these rhinos live in the wild, in India and Nepal.",
    "That's why every birth counts. The calf is part of a Europe-wide breeding program that keeps the species healthy and genetically diverse.",
    "Its dad, Beni, passed away earlier this year, so this little one carries on his legacy.",
    "Follow for a little good news every day.",
]
STARTS = [0, 3.317551, 9.430204, 16.74449, 23.588571, 28.734694, 37.01551, 43.128163]
DURS = [3.317551, 6.112653, 7.314286, 6.844082, 5.146122, 8.280816, 6.112653, 2.586122]
TOTAL = 45.9
ENDS = STARTS[1:] + [TOTAL]
CHUNKS = caption_chunks(LINES, STARTS, DURS)

DAY = make_zoo_bg()
NIGHT = make_zoo_bg(night=True)
GROUND = 1420


def floating_hearts(d, t, seed=4, n=12, col=C["pink"]):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(80, W - 80); sp = rnd.uniform(90, 160); s = rnd.uniform(18, 34); off = rnd.uniform(0, 20)
        y = H + 60 - ((t * sp + off * 60) % (H + 200))
        x = x0 + 30 * math.sin(t * 1.5 + i)
        draw_heart(d, x, y, s, col)


def cctv_overlay(img, t):
    d = ImageDraw.Draw(img)
    # green tint + scanlines
    img.alpha_composite(Image.new("RGBA", img.size, (40, 90, 60, 70)))
    for y in range(0, H, 8):
        d.line([(0, S(y)), (SW, S(y))], fill=(0, 0, 0, 40), width=S(2))
    # corner brackets
    for (x, y, sx, sy) in [(60, 760, 1, 1), (1020, 760, -1, 1), (60, 1560, 1, -1), (1020, 1560, -1, -1)]:
        d.line([(S(x), S(y)), (S(x + sx * 90), S(y))], fill=C["white"], width=S(8))
        d.line([(S(x), S(y)), (S(x), S(y + sy * 90))], fill=C["white"], width=S(8))
    if int(t * 2) % 2 == 0:
        d.ellipse([S(90), S(800), S(122), S(832)], fill=(255, 60, 60))
    text_center(d, 190, 816, "REC", 44, fill=C["white"])
    text_center(d, 900, 816, "CAM 2", 40, fill=C["white"], path=FONT_XB)


def frame(t):
    img = None
    # ---------------- scene 0: hook ----------------
    if t < ENDS[0]:
        lt = t
        img = vgrad(SW, SH, (255, 226, 110), (255, 170, 120)).convert("RGBA")
        d = ImageDraw.Draw(img)
        sunburst(d, 540, 1150, lt, (255, 238, 160))
        floating_hearts(d, lt)
        hop = 60 * abs(math.sin(lt * 4.5))
        draw_rhino(d, 540, 1450 - hop, scale=2.3, facing=1, phase=lt * 6, baby=True, walking=False)
        sticker(img, 540, 330, "SAY HELLO!", 120, C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-3)
        sticker(img, 540, 540, "BABY RHINO!", 110, C["pink"], fg=C["white"], scale=pop(prog(lt, 1.2, 0.35)), rot=2)
    # ---------------- scene 1: caught on CCTV ----------------
    elif t < ENDS[1]:
        lt = t - STARTS[1]
        img = NIGHT.copy()
        d = ImageDraw.Draw(img)
        # straw floor inside the barn
        d.rectangle([0, S(1270), SW, SH], fill=(120, 104, 60))
        for i in range(40):
            rx = (i * 97) % W; ry = 1300 + (i * 53) % 300
            d.line([(S(rx), S(ry)), (S(rx + 40), S(ry - 10))], fill=(170, 150, 90), width=S(5))
        draw_rhino(d, 470, 1480, scale=1.9, facing=1, phase=0.4, walking=False)
        b = pop(prog(lt, 2.6, 0.5))
        if b > 0.02:
            draw_rhino(d, 820, 1480, scale=1.0 * b, facing=-1, phase=0.0, baby=True, walking=False)
        cctv_overlay(img, lt)
        sticker(img, 540, 300, "CHESTER ZOO, ENGLAND", 64, C["white"], scale=pop(prog(lt, 0.4, 0.35)), rot=-2)
        sticker(img, 540, 470, "RARE!", 90, C["yellow"], scale=pop(prog(lt, 3.0, 0.3)), rot=3)
        sticker(img, 540, 620, "GREATER ONE-HORNED RHINO", 52, C["teal"], fg=C["white"], scale=pop(prog(lt, 3.6, 0.35)), rot=-1)
    # ---------------- scene 2: 15 months, up in an hour ----------------
    elif t < ENDS[2]:
        lt = t - STARTS[2]
        if lt < 3.4:
            img = vgrad(SW, SH, (190, 230, 255), (255, 210, 230)).convert("RGBA")
            d = ImageDraw.Draw(img)
            sunburst(d, 540, 950, lt, (210, 238, 255))
            m = 1 + int(14 * ease_in_out(prog(lt, 0.4, 2.4)))
            ca = pop(prog(lt, 0.1, 0.4))
            cal = Image.new("RGBA", (S(560), S(600)), (0, 0, 0, 0))
            cd = ImageDraw.Draw(cal)
            cd.rounded_rectangle([S(10), S(24), S(550), S(590)], radius=S(40), fill=C["ink"])
            cd.rounded_rectangle([0, 0, S(540), S(570)], radius=S(40), fill=C["white"], outline=C["ink"], width=S(8))
            cd.rounded_rectangle([0, 0, S(540), S(170)], radius=S(40), fill=(140, 100, 240), outline=C["ink"], width=S(8))
            cd.rectangle([S(4), S(120), S(536), S(170)], fill=(140, 100, 240))
            text_center(cd, 270, 92, "MONTHS", 76, fill=C["white"])
            text_center(cd, 270, 370, str(m), 280)
            for rx in (130, 410):
                cd.rounded_rectangle([S(rx - 16), S(-30), S(rx + 16), S(40)], radius=S(14), fill=(120, 120, 140), outline=C["ink"], width=S(5))
            flip = 1 + 0.05 * math.sin(lt * 14) * (1 - prog(lt, 2.8, 0.2))
            paste_scaled(img, cal, 540, 960, ca * flip, rot=3 * math.sin(lt * 3))
            sticker(img, 540, 330, "MOM ASHA", 100, C["pink"], fg=C["white"], scale=pop(prog(lt, 0.0, 0.35)), rot=-2)
            sticker(img, 540, 1400, "~15 MONTHS!", 90, C["yellow"], scale=pop(prog(lt, 2.7, 0.3)), rot=2)
        else:
            l2 = lt - 3.4
            img = DAY.copy()
            d = ImageDraw.Draw(img)
            draw_rhino(d, 300, GROUND + 60, scale=2.2, facing=1, phase=0.3, walking=False, head_up=0.2)
            # the calf wobbles to its feet
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            rise = ease_out(prog(l2, 0.0, 1.4))
            bx, by = 810, GROUND + 60 + 80 * (1 - rise)
            draw_rhino(ld, bx, by, scale=1.45, facing=-1, phase=l2 * 3, baby=True, walking=False)
            wob = 9 * math.sin(l2 * 7) * (1 - 0.6 * prog(l2, 1.5, 2.0))
            lay = lay.rotate(wob, resample=Image.BICUBIC, center=(S(bx), S(GROUND + 60)))
            img.alpha_composite(lay)
            d = ImageDraw.Draw(img)
            sticker(img, 540, 330, "UP IN 1 HOUR!", 100, C["teal"], fg=C["white"], scale=pop(prog(l2, 0.3, 0.35)), rot=-2)
            sticker(img, 540, 520, "WOBBLE WOBBLE", 64, C["white"], scale=pop(prog(l2, 1.6, 0.35)), rot=3)
    # ---------------- scene 3: 100 lbs vs 2 tons ----------------
    elif t < ENDS[3]:
        lt = t - STARTS[3]
        img = DAY.copy()
        d = ImageDraw.Draw(img)
        swap = ease_in_out(prog(lt, 4.3, 0.9))
        # newborn on the left slides out, car slides in
        draw_rhino(d, 230 - 700 * swap, GROUND, scale=0.95, facing=1, phase=lt * 6, baby=True)
        if swap > 0:
            draw_side_car(d, 230 + 700 * (1 - swap) - 0, GROUND, 330, col=(255, 92, 92))
        draw_rhino(d, 700, GROUND, scale=1.55, facing=-1, phase=0.5, walking=False)
        a = pop(prog(lt, 0.3, 0.35)) * (1 - swap)
        sticker(img, 300, 820, "NEWBORN", 60, C["white"], scale=a, rot=-3)
        sticker(img, 300, 960, "~100 LBS", 80, C["yellow"], scale=a, rot=2)
        b = pop(prog(lt, 2.4, 0.35))
        sticker(img, 760, 620, "GROWN-UP", 60, C["white"], scale=b, rot=3)
        sticker(img, 760, 760, "2+ TONS", 96, C["pink"], fg=C["white"], scale=b, rot=-2)
        c = pop(prog(lt, 4.9, 0.35))
        sticker(img, 300, 960, "= A CAR!", 84, C["teal"], fg=C["white"], scale=c, rot=-3)
    # ---------------- scene 4: ~4,000 in the wild ----------------
    elif t < ENDS[4]:
        lt = t - STARTS[4]
        img = vgrad(SW, SH, (150, 214, 255), (230, 246, 230)).convert("RGBA")
        d = ImageDraw.Draw(img)
        # tall grass + wetland
        pts = [(0, SH)]
        for x in range(0, W + 20, 20):
            pts.append((S(x), S(1000 - 40 * (0.5 + 0.5 * math.sin(x / 400 + 1.0)))))
        pts.append((SW, SH)); d.polygon(pts, fill=(140, 196, 110))
        d.ellipse([S(80), S(1500), S(900), S(1760)], fill=(90, 170, 220), outline=C["ink"], width=S(6))
        for i in range(30):
            gx = (i * 73) % W; gy = 1060 + (i * 41) % 380
            sway = 8 * math.sin(lt * 2 + i)
            d.polygon([(S(gx - 8), S(gy)), (S(gx + 8), S(gy)), (S(gx + sway), S(gy - 70))], fill=(90, 160, 80))
        herd = [(180, 1240, 0.75), (520, 1300, 0.9), (860, 1220, 0.7), (360, 1440, 1.05)]
        for i, (hx, hy, sc) in enumerate(herd):
            x = (hx + lt * 40 + 300) % (W + 600) - 300
            draw_rhino(d, x, hy, scale=sc, facing=1, phase=lt * 5 + i, baby=(i == 3))
        n = int(4000 * ease_out(prog(lt, 0.3, 1.6)))
        sticker(img, 540, 340, f"~{n:,}", 150, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-3)
        sticker(img, 540, 540, "IN THE WILD", 76, C["white"], scale=pop(prog(lt, 1.0, 0.3)), rot=2)
        sticker(img, 540, 720, "INDIA & NEPAL", 76, C["orange"], fg=C["white"], scale=pop(prog(lt, 2.8, 0.35)), rot=-2)
    # ---------------- scene 5: every birth counts ----------------
    elif t < ENDS[5]:
        lt = t - STARTS[5]
        img = vgrad(SW, SH, (255, 200, 220), (255, 236, 200)).convert("RGBA")
        d = ImageDraw.Draw(img)
        sunburst(d, 540, 1100, lt * 0.6, (255, 222, 230))
        floating_hearts(d, lt, seed=9, n=14)
        d.rectangle([0, S(1380), SW, SH], fill=(126, 204, 120))
        x = -100 + 60 * lt
        draw_rhino(d, x + 260, 1460, scale=1.55, facing=1, phase=lt * 5)
        draw_rhino(d, x + 620, 1470, scale=0.95, facing=1, phase=lt * 7 + 1, baby=True)
        sticker(img, 540, 300, "EVERY BIRTH COUNTS", 76, C["pink"], fg=C["white"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
        sticker(img, 540, 480, "EUROPE-WIDE", 80, C["white"], scale=pop(prog(lt, 2.3, 0.3)), rot=2)
        sticker(img, 540, 630, "BREEDING PROGRAM", 72, C["purple"], fg=C["white"], scale=pop(prog(lt, 2.8, 0.3)), rot=-2)
        sticker(img, 540, 820, "HEALTHY + DIVERSE", 70, C["teal"], fg=C["white"], scale=pop(prog(lt, 5.4, 0.35)), rot=2)
    # ---------------- scene 6: dad Beni's legacy ----------------
    elif t < ENDS[6]:
        lt = t - STARTS[6]
        img = vgrad(SW, SH, (60, 50, 130), (255, 150, 110)).convert("RGBA")
        d = ImageDraw.Draw(img)
        draw_twinkles(d, lt, seed=6, n=16)
        sx, sy = 760, 700
        g = 0.6 + 0.4 * math.sin(lt * 2.5)
        draw_glow(img, sx, sy, 26 + 6 * g, col=(255, 230, 150))
        d = ImageDraw.Draw(img)
        pts = []
        for i in range(10):
            r = 70 if i % 2 == 0 else 30
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((S(sx + r * math.cos(a)), S(sy + r * math.sin(a))))
        d.polygon(pts, fill=(255, 220, 90), outline=C["ink"], width=S(5))
        sticker(img, sx, sy + 130, "BENI", 60, C["yellow"], scale=pop(prog(lt, 0.8, 0.4)))
        pts = [(0, SH)]
        for x in range(0, W + 20, 20):
            pts.append((S(x), S(1320 - 40 * (0.5 + 0.5 * math.sin(x / 300)))))
        pts.append((SW, SH)); d.polygon(pts, fill=(70, 120, 90))
        draw_rhino(d, 330, 1430, scale=1.6, facing=1, phase=0.2, walking=False, head_up=0.6)
        draw_rhino(d, 640, 1440, scale=1.0, facing=1, phase=0.4, baby=True, walking=False, head_up=1.0)
        sticker(img, 540, 300, "DAD, BENI", 96, C["white"], scale=pop(prog(lt, 0.3, 0.35)), rot=-2)
        sticker(img, 540, 1120, "HIS LEGACY LIVES ON", 64, C["pink"], fg=C["white"], scale=pop(prog(lt, 3.4, 0.4)), rot=1)
    # ---------------- scene 7: outro ----------------
    else:
        lt = t - STARTS[7]
        img = vgrad(SW, SH, (130, 110, 250), (255, 120, 170)).convert("RGBA")
        d = ImageDraw.Draw(img)
        sunburst(d, 540, 820, -lt, (160, 140, 255), speed=0.4)
        draw_rhino(d, 540, 1350 - 40 * abs(math.sin(lt * 5)), scale=2.1, facing=1, phase=lt * 4, baby=True, walking=False)
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
    os.makedirs("out/ep003", exist_ok=True)
    if sys.argv[1] == "stills":
        for t in map(float, sys.argv[2:]):
            frame(t).save(f"out/ep003/still_{t:05.2f}.jpg", quality=88)
    elif sys.argv[1] == "scene":
        for i in map(int, sys.argv[2:]):
            render_scene(i, f"out/ep003/scene{i}.mp4")
