"""Episode 001: coyotes are first to use the Wallis Annenberg Wildlife Crossing."""
import sys, math, subprocess, os
from PIL import Image, ImageDraw
from toon import *

LINES = [
    "A coyote just crossed a ten-lane freeway. Safely.",
    "Meet the Wallis Annenberg Wildlife Crossing in Agoura Hills, California. It's the largest wildlife bridge of its kind in the world.",
    "It stretches over the 101 Freeway, where more than three hundred thousand cars zoom by every single day.",
    "In late October, trail cameras caught the very first big animal using it. A coyote! A few days later, another one strolled across.",
    "And here's the best part. It doesn't even officially open until December second.",
    "The bridge was built to help mountain lions, who got trapped by the freeway and couldn't find new mates. Now bobcats, deer, and foxes get a safe path too.",
    "Follow for a little good news every day.",
]
STARTS = [0, 4.205714, 12.643265, 19.565714, 28.813061, 33.959184, 43.52]
DURS = [4.205714, 8.437551, 6.922449, 9.247347, 5.146122, 9.560816, 2.586122]
TOTAL = 46.2
ENDS = STARTS[1:] + [TOTAL]
CHUNKS = caption_chunks(LINES, STARTS, DURS)

DAY = make_day_bg()
NIGHT = make_night_bg()
CARS = make_cars(26, seed=2)
CARS_BUSY = make_cars(60, seed=9, speed=(0.3, 0.5))

def walker(kind, t, t0, dur, x0=-150, x1=1230, facing=1, stick=False, scale=1.0):
    def fn(d):
        p = (t - t0) / dur
        if p < -0.05 or p > 1.05: return
        x = x0 + (x1 - x0) * p
        draw_animal(d, x, bridge_y(x), kind, phase=t * 9, scale=scale, facing=facing, mouth_stick=stick)
    return fn

def frame(t):
    img = None
    # ---------------- scene 0: hook ----------------
    if t < ENDS[0]:
        img = DAY.copy()
        draw_road_scene(img, t, CARS, walkers=[walker("coyote", t, 0.0, 4.2, x0=-200, x1=1250, scale=1.9)])
        sticker(img, 540, 330, "10 LANES.", 120, C["yellow"], scale=pop(prog(t, 0.2, 0.35)), rot=-3)
        sticker(img, 540, 520, "1 COYOTE.", 120, C["pink"], fg=C["white"], scale=pop(prog(t, 1.5, 0.35)), rot=2)
        if t > 2.9:
            sticker(img, 540, 690, "SAFELY", 80, C["teal"], fg=C["white"], scale=pop(prog(t, 2.9, 0.3)))
    # ---------------- scene 1: meet the crossing ----------------
    elif t < ENDS[1]:
        lt = t - STARTS[1]
        img = DAY.copy()
        draw_road_scene(img, t, CARS, sign="WALLIS ANNENBERG WILDLIFE CROSSING", sign_a=prog(lt, 0.3, 0.45))
        d = ImageDraw.Draw(img)
        # map pin + location
        a = pop(prog(lt, 2.2, 0.4))
        if a > 0.02:
            cx, cy = 540, 360
            r = 70 * a
            d.ellipse([S(cx - r), S(cy - r - 40 * a), S(cx + r), S(cy + r - 40 * a)], fill=C["pink"], outline=C["ink"], width=S(6))
            d.polygon([(S(cx - r * 0.8), S(cy + r * 0.2 - 40 * a)), (S(cx + r * 0.8), S(cy + r * 0.2 - 40 * a)), (S(cx), S(cy + r * 1.6))], fill=C["pink"], outline=C["ink"])
            d.ellipse([S(cx - r * 0.38), S(cy - r * 0.38 - 40 * a), S(cx + r * 0.38), S(cy + r * 0.38 - 40 * a)], fill=C["white"])
            sticker(img, 540, 540, "AGOURA HILLS, CA", 64, C["white"], scale=a)
        b = pop(prog(lt, 5.0, 0.4))
        if b > 0.02:
            sticker(img, 540, 720, "★ WORLD'S LARGEST ★", 70, C["yellow"], scale=b, rot=-2)
    # ---------------- scene 2: 300,000 cars ----------------
    elif t < ENDS[2]:
        lt = t - STARTS[2]
        img = DAY.copy()
        draw_road_scene(img, t * 1.6, CARS_BUSY, sign="101 FREEWAY", sign_a=1.0)
        n = int(300000 * ease_out(prog(lt, 1.6, 2.6)))
        sc = pop(prog(lt, 1.4, 0.35))
        sticker(img, 540, 380, f"{n:,}+", 150, C["yellow"], scale=sc, rot=-2)
        sticker(img, 540, 590, "CARS EVERY DAY", 72, C["white"], scale=pop(prog(lt, 2.2, 0.35)))
    # ---------------- scene 3: trail cam at night ----------------
    elif t < ENDS[3]:
        lt = t - STARTS[3]
        img = NIGHT.copy()
        d = ImageDraw.Draw(img)
        draw_clouds(d, t, night=True)
        # ground + bridge deck silhouette
        d.rectangle([0, S(1290), SW, S(1330)], fill=(52, 92, 80))
        # trail camera on a post
        d.rectangle([S(110), S(1000), S(140), S(1300)], fill=(90, 60, 40), outline=C["ink"], width=S(4))
        d.rounded_rectangle([S(60), S(900), S(200), S(1060)], radius=S(20), fill=(60, 110, 70), outline=C["ink"], width=S(6))
        d.ellipse([S(95), S(940), S(165), S(1010)], fill=C["ink"])
        d.ellipse([S(112), S(957), S(148), S(993)], fill=(80, 120, 200))
        blink = (int(lt * 2) % 2 == 0)
        d.ellipse([S(170), S(915), S(188), S(933)], fill=(255, 60, 60) if blink else (100, 30, 30))
        # coyote trots in
        p = prog(lt, 0.4, 3.0)
        cx = 1200 - 650 * ease_out(p)
        draw_animal(d, cx, 1300, "coyote", phase=t * 9 * (1 - p * 0.9), scale=1.6, facing=-1)
        sticker(img, 540, 330, "LATE OCTOBER", 80, C["yellow"], scale=pop(prog(lt, 0.2, 0.35)), rot=-2)
        # flash
        fl = prog(lt, 3.3, 0.5)
        if 0 < fl < 1:
            img.alpha_composite(Image.new("RGBA", img.size, (255, 255, 255, int(255 * (1 - fl)))))
        # polaroid 1
        pa = pop(prog(lt, 3.6, 0.4))
        if pa > 0.02:
            pol = Image.new("RGBA", (S(560), S(620)), (0, 0, 0, 0))
            pd = ImageDraw.Draw(pol)
            pd.rectangle([0, 0, S(560), S(620)], fill=C["white"], outline=C["ink"], width=S(6))
            pd.rectangle([S(30), S(30), S(530), S(500)], fill=(120, 150, 120))
            draw_animal_local(pd, 280, 450, "coyote", 1.5, -1)
            text_center(pd, 280, 560, "FIRST BIG ANIMAL!", 40)
            pol = pol.rotate(-6, resample=Image.BICUBIC, expand=True)
            pol = pol.resize((max(1, int(pol.width * pa)), max(1, int(pol.height * pa))))
            img.alpha_composite(pol, (int(S(470) - pol.width / 2), int(S(720) - pol.height / 2)))
        # polaroid 2 (second coyote with a stick)
        pb = pop(prog(lt, 6.6, 0.4))
        if pb > 0.02:
            pol = Image.new("RGBA", (S(480), S(540)), (0, 0, 0, 0))
            pd = ImageDraw.Draw(pol)
            pd.rectangle([0, 0, S(480), S(540)], fill=C["white"], outline=C["ink"], width=S(6))
            pd.rectangle([S(26), S(26), S(454), S(430)], fill=(110, 140, 170))
            draw_animal_local(pd, 240, 390, "coyote", 1.3, 1, stick=True)
            text_center(pd, 240, 485, "ANOTHER ONE!", 38)
            pol = pol.rotate(7, resample=Image.BICUBIC, expand=True)
            pol = pol.resize((max(1, int(pol.width * pb)), max(1, int(pol.height * pb))))
            img.alpha_composite(pol, (int(S(680) - pol.width / 2), int(S(1180) - pol.height / 2)))
    # ---------------- scene 4: not even open yet ----------------
    elif t < ENDS[4]:
        lt = t - STARTS[4]
        img = vgrad(SW, SH, (255, 226, 110), (255, 170, 90)).convert("RGBA")
        d = ImageDraw.Draw(img)
        # sunburst
        for i in range(16):
            a0 = i * math.pi / 8 + lt * 0.3
            d.polygon([(S(540), S(860)), (S(540 + 1600 * math.cos(a0)), S(860 + 1600 * math.sin(a0))),
                       (S(540 + 1600 * math.cos(a0 + 0.18)), S(860 + 1600 * math.sin(a0 + 0.18)))], fill=(255, 236, 150))
        sticker(img, 540, 300, "NOT EVEN OPEN YET!", 76, C["pink"], fg=C["white"], scale=pop(prog(lt, 0.1, 0.35)), rot=-2)
        ca = pop(prog(lt, 1.6, 0.45))
        if ca > 0.02:
            cal = Image.new("RGBA", (S(560), S(600)), (0, 0, 0, 0))
            cd = ImageDraw.Draw(cal)
            cd.rounded_rectangle([S(10), S(24), S(550), S(590)], radius=S(40), fill=C["ink"])
            cd.rounded_rectangle([0, 0, S(540), S(570)], radius=S(40), fill=C["white"], outline=C["ink"], width=S(8))
            cd.rounded_rectangle([0, 0, S(540), S(170)], radius=S(40), fill=(240, 70, 80), outline=C["ink"], width=S(8))
            cd.rectangle([S(4), S(120), S(536), S(170)], fill=(240, 70, 80))
            text_center(cd, 270, 92, "DECEMBER", 76, fill=C["white"])
            text_center(cd, 270, 370, "2", 300)
            for rx in (130, 410):
                cd.rounded_rectangle([S(rx - 16), S(-30), S(rx + 16), S(40)], radius=S(14), fill=(120, 120, 140), outline=C["ink"], width=S(5))
            bounce = 1 + 0.04 * math.sin(lt * 6)
            cal = cal.rotate(3 * math.sin(lt * 3), resample=Image.BICUBIC, expand=True)
            s_ = ca * bounce
            cal = cal.resize((max(1, int(cal.width * s_)), max(1, int(cal.height * s_))))
            img.alpha_composite(cal, (int(S(540) - cal.width / 2), int(S(900) - cal.height / 2)))
        sticker(img, 540, 1330, "OFFICIAL OPENING", 64, C["teal"], fg=C["white"], scale=pop(prog(lt, 2.4, 0.35)))
        draw_confetti(d, lt, 1.7)
    # ---------------- scene 5: built for mountain lions ----------------
    elif t < ENDS[5]:
        lt = t - STARTS[5]
        img = DAY.copy()
        parade = [("lion", 0.2, 1.6, 6.0), ("bobcat", 5.6, 1.8, 4.2), ("deer", 6.6, 1.5, 4.2), ("fox", 7.5, 2.0, 4.2)]
        ws = [walker(k, lt, t0, du, x0=-260, x1=1340, scale=s) for k, t0, s, du in parade]
        draw_road_scene(img, t, CARS, sign="WALLIS ANNENBERG WILDLIFE CROSSING", sign_a=1.0, walkers=ws)
        sticker(img, 540, 330, "BUILT FOR", 72, C["white"], scale=pop(prog(lt, 0.1, 0.3)))
        sticker(img, 540, 480, "MOUNTAIN LIONS", 100, C["orange"], fg=C["white"], scale=pop(prog(lt, 0.5, 0.35)), rot=-2)
        tags = [("BOBCATS", 5.6, 230), ("DEER", 6.6, 540), ("FOXES", 7.5, 850)]
        for s_, t0, x in tags:
            sticker(img, x, 680, s_, 56, C["yellow"], scale=pop(prog(lt, t0, 0.3)), rot=(-4 if x < 500 else 4))
    # ---------------- scene 6: outro ----------------
    else:
        lt = t - STARTS[6]
        img = vgrad(SW, SH, (130, 110, 250), (255, 120, 170)).convert("RGBA")
        d = ImageDraw.Draw(img)
        for i in range(16):
            a0 = i * math.pi / 8 - lt * 0.4
            d.polygon([(S(540), S(820)), (S(540 + 1600 * math.cos(a0)), S(820 + 1600 * math.sin(a0))),
                       (S(540 + 1600 * math.cos(a0 + 0.18)), S(820 + 1600 * math.sin(a0 + 0.18)))], fill=(160, 140, 255))
        draw_animal(d, 540, 1200 - 30 * abs(math.sin(lt * 5)), "coyote", phase=lt * 4, scale=2.4, facing=1)
        sticker(img, 540, 330, "FOLLOW", 130, C["yellow"], scale=pop(prog(lt, 0.0, 0.35)), rot=-3)
        sticker(img, 540, 520, "FOR DAILY GOOD NEWS", 66, C["white"], scale=pop(prog(lt, 0.4, 0.35)))
    draw_caption(img, CHUNKS, t)
    return finish(img)

def draw_animal_local(d, x, y, kind, scale, facing, stick=False):
    draw_animal(d, x, y, kind, phase=0.6, scale=scale, facing=facing, mouth_stick=stick)

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
    if sys.argv[1] == "stills":
        for t in map(float, sys.argv[2:]):
            frame(t).save(f"out/still_{t:05.2f}.jpg", quality=88)
    elif sys.argv[1] == "scene":
        for i in map(int, sys.argv[2:]):
            render_scene(i, f"out/scene{i}.mp4")
