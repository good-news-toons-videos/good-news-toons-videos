"""Bright flat-cartoon 2D animation toolkit for vertical (1080x1920) news explainers.
Frames are drawn at 2x and downsampled for smooth edges."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SS = 2                      # supersample factor
SW, SH = W * SS, H * SS

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
_fc = {}
def font(size, path=FONT_BLACK):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(size * SS))
    return _fc[k]

def S(v):                   # scale design coords (1080 space) to canvas
    return v * SS

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in_out(t): t = clamp(t); return 3 * t * t - 2 * t * t * t
def pop(t):                 # overshoot pop 0->1
    t = clamp(t)
    if t >= 1: return 1.0
    c = 1.70158 * 1.5
    t -= 1
    return 1 + (c + 1) * t ** 3 + c * t ** 2
def prog(t, start, dur): return clamp((t - start) / dur)

# ---------- palette ----------
C = dict(
    sky1=(120, 200, 255), sky2=(214, 242, 255), sun=(255, 214, 90),
    hill1=(126, 204, 120), hill2=(86, 172, 98), hill3=(60, 140, 82),
    road=(86, 90, 104), roadedge=(70, 72, 84), dash=(255, 255, 255),
    concrete=(238, 222, 190), concrete_d=(206, 186, 150), grass=(98, 196, 96), grass_d=(64, 160, 76),
    ink=(34, 34, 52), white=(255, 255, 255), yellow=(255, 206, 60), pink=(255, 110, 150),
    teal=(40, 200, 180), orange=(255, 140, 50), purple=(140, 100, 240),
    night1=(24, 30, 78), night2=(60, 64, 140),
)
CAR_COLORS = [(255, 92, 92), (255, 196, 60), (80, 160, 255), (120, 220, 130), (255, 140, 200), (170, 120, 255), (255, 255, 255), (255, 150, 70)]

def vgrad(w, h, top, bot):
    g = Image.new("RGB", (1, 256))
    for i in range(256):
        f = i / 255
        g.putpixel((0, i), tuple(int(top[k] + (bot[k] - top[k]) * f) for k in range(3)))
    return g.resize((w, h), Image.BILINEAR)

# ---------- text helpers ----------
def text_center(d, cx, cy, s, size, fill=C["ink"], path=FONT_BLACK, stroke=0, stroke_fill=None):
    f = font(size, path)
    bb = d.textbbox((0, 0), s, font=f, stroke_width=S(stroke))
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text((S(cx) - w / 2 - bb[0], S(cy) - h / 2 - bb[1]), s, font=f, fill=fill,
           stroke_width=S(stroke), stroke_fill=stroke_fill)
    return w / SS, h / SS

def text_w(s, size, path=FONT_BLACK):
    f = font(size, path); bb = f.getbbox(s); return (bb[2] - bb[0]) / SS

def pill(d, cx, cy, w, h, fill, outline=None, ow=0):
    d.rounded_rectangle([S(cx - w / 2), S(cy - h / 2), S(cx + w / 2), S(cy + h / 2)], radius=S(h / 2),
                        fill=fill, outline=outline, width=S(ow))

def sticker(img, cx, cy, s, size, bg, fg=C["ink"], scale=1.0, rot=0, pad=(44, 26)):
    """Text in a rounded card with a dark offset shadow, popped by `scale`."""
    if scale <= 0.01: return
    tw = text_w(s, size); f = font(size)
    bb = f.getbbox(s); th = (bb[3] - bb[1]) / SS
    w, h = tw + pad[0] * 2, th + pad[1] * 2
    lay = Image.new("RGBA", (int(S(w + 20)), int(S(h + 20))), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle([S(10), S(16), S(w + 10), S(h + 16)], radius=S(26), fill=C["ink"])
    ld.rounded_rectangle([S(4), S(4), S(w + 4), S(h + 4)], radius=S(26), fill=bg, outline=C["ink"], width=S(6))
    ld.text((S(4 + pad[0]) - bb[0], S(4 + pad[1]) - bb[1]), s, font=f, fill=fg)
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    if scale != 1.0:
        lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.BICUBIC)
    img.alpha_composite(lay, (int(S(cx) - lay.width / 2), int(S(cy) - lay.height / 2)))

# ---------- captions ----------
def caption_chunks(lines, starts, durs, max_words=4):
    out = []
    for text, st, du in zip(lines, starts, durs):
        words = text.split()
        chunks, cur = [], []
        for w_ in words:
            cur.append(w_)
            if len(cur) >= max_words or w_.endswith((".", ",", "!", "?")):
                chunks.append(" ".join(cur)); cur = []
        if cur: chunks.append(" ".join(cur))
        total = sum(len(c) + 2 for c in chunks)
        t = st + 0.05
        speak = du - 0.35
        for c in chunks:
            d_ = speak * (len(c) + 2) / total
            out.append((t, t + d_, c)); t += d_
    return out

def draw_caption(img, chunks, t, y=1640):
    cur = None
    for a, b, s in chunks:
        if a <= t < b + 0.12: cur = (a, s)
    if not cur: return
    a, s = cur
    sc = 0.85 + 0.15 * pop(prog(t, a, 0.18))
    d = ImageDraw.Draw(img)
    size = 76 * sc
    f = font(size)
    bb = d.textbbox((0, 0), s.upper(), font=f, stroke_width=S(9))
    w = bb[2] - bb[0]
    if w > S(1000):
        size *= S(1000) / w
    text_center(d, 540, y, s.upper(), size, fill=C["white"], stroke=9, stroke_fill=C["ink"])

# ---------- scenery ----------
HORIZON = 820
VPX = 540

def road_halfw(y):
    return 30 + (y - HORIZON) / (H - HORIZON) * 900

def make_day_bg():
    img = vgrad(SW, SH, C["sky1"], C["sky2"]).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.ellipse([S(780), S(150), S(980), S(350)], fill=C["sun"])
    # clouds drawn per-frame (they drift). hills:
    for col, base, amp, ph, per in [(C["hill1"], 760, 90, 0.3, 700), (C["hill2"], 810, 70, 1.7, 520)]:
        pts = [(0, SH)]
        for x in range(0, W + 20, 20):
            pts.append((S(x), S(base - amp * (0.5 + 0.5 * math.sin(x / per * 2 * math.pi + ph)))))
        pts.append((SW, SH))
        d.polygon(pts, fill=col)
    d.rectangle([0, S(HORIZON), SW, SH], fill=C["hill3"])
    # road trapezoid
    d.polygon([(S(VPX - road_halfw(HORIZON)), S(HORIZON)), (S(VPX + road_halfw(HORIZON)), S(HORIZON)),
               (S(VPX + road_halfw(H)), SH), (S(VPX - road_halfw(H)), SH)], fill=C["road"])
    # median
    d.polygon([(S(VPX - 3), S(HORIZON)), (S(VPX + 3), S(HORIZON)), (S(VPX + 18), SH), (S(VPX - 18), SH)], fill=C["yellow"])
    return img

def make_night_bg(seed=3):
    img = vgrad(SW, SH, C["night1"], C["night2"]).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(90):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 1000), rnd.uniform(2, 5)
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=(255, 255, 230))
    d.ellipse([S(140), S(180), S(320), S(360)], fill=(255, 246, 200))
    d.ellipse([S(190), S(160), S(360), S(330)], fill=C["night1"])
    pts = [(0, SH)]
    for x in range(0, W + 20, 20):
        pts.append((S(x), S(1180 - 80 * (0.5 + 0.5 * math.sin(x / 600 * 2 * math.pi + 0.8)))))
    pts.append((SW, SH))
    d.polygon(pts, fill=(36, 70, 70))
    d.rectangle([0, S(1300), SW, SH], fill=(28, 54, 58))
    return img

def draw_clouds(d, t, night=False):
    col = (255, 255, 255) if not night else (90, 96, 170)
    for i, (x0, y, s) in enumerate([(100, 300, 1.0), (600, 200, 0.8), (380, 480, 0.7)]):
        x = (x0 + t * (14 + 6 * i)) % (W + 400) - 200
        for dx, dy, r in [(0, 0, 60), (60, -25, 70), (130, 0, 55), (65, 20, 60)]:
            rr = r * s
            d.ellipse([S(x + dx * s - rr), S(y + dy * s - rr), S(x + dx * s + rr), S(y + dy * s + rr)], fill=col)

# ---------- cars ----------
def car_state(t, lane, speed, offset):
    """lane in -5..-1 (oncoming, toward viewer) / 1..5 (away). returns (u in 0..1 depth)."""
    u = ((t * speed + offset) % 1.0)
    return u if lane < 0 else 1 - u

def draw_car(d, u, lane, color):
    y = HORIZON + (H - HORIZON) * (u ** 1.8)
    hw = road_halfw(y)
    x = VPX + (lane + (0.5 if lane < 0 else -0.5)) / 5.0 * hw
    w = hw / 5.0 * 0.78
    h = w * 0.62
    d.rounded_rectangle([S(x - w / 2), S(y - h), S(x + w / 2), S(y)], radius=S(w * 0.18), fill=color, outline=C["ink"], width=max(1, int(S(w * 0.05))))
    # windshield
    d.rounded_rectangle([S(x - w * 0.36), S(y - h * 0.92), S(x + w * 0.36), S(y - h * 0.52)], radius=S(w * 0.08), fill=(190, 230, 255))
    # lights
    lc = (255, 250, 200) if lane < 0 else (255, 70, 70)
    for sx in (-1, 1):
        cx = x + sx * w * 0.32
        d.ellipse([S(cx - w * 0.08), S(y - h * 0.36), S(cx + w * 0.08), S(y - h * 0.2)], fill=lc)
    # wheels
    for sx in (-1, 1):
        cx = x + sx * w * 0.36
        d.rectangle([S(cx - w * 0.09), S(y - h * 0.05), S(cx + w * 0.09), S(y + h * 0.1)], fill=C["ink"])
    return y

def make_cars(n, seed=1, speed=(0.18, 0.32)):
    rnd = random.Random(seed)
    cars = []
    for i in range(n):
        lane = rnd.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        cars.append((lane, rnd.uniform(*speed), rnd.random(), rnd.choice(CAR_COLORS)))
    return cars

def draw_lane_dashes(d, t):
    for lane in range(-4, 5):
        if lane == 0: continue
        for k in range(14):
            u0 = ((k / 14) + t * 0.5 * (1 if lane < 0 else -1)) % 1.0
            u1 = u0 + 0.025
            if u1 > 1: continue
            y0 = HORIZON + (H - HORIZON) * u0 ** 1.8; y1 = HORIZON + (H - HORIZON) * u1 ** 1.8
            x0 = VPX + lane / 5 * road_halfw(y0); x1 = VPX + lane / 5 * road_halfw(y1)
            wd = max(1.0, road_halfw(y1) / 5 * 0.06)
            d.polygon([(S(x0 - wd * 0.6), S(y0)), (S(x0 + wd * 0.6), S(y0)), (S(x1 + wd), S(y1)), (S(x1 - wd), S(y1))], fill=C["dash"])

# ---------- the wildlife bridge ----------
BRIDGE_TOP = 1010      # top of grass
BRIDGE_FACE = (1060, 1170)

def draw_bridge(d, t, sign=None, sign_a=1.0):
    # grass hump
    pts = [(0, S(BRIDGE_FACE[0]))]
    for x in range(0, W + 10, 10):
        pts.append((S(x), S(BRIDGE_TOP + 30 - 30 * math.sin(x / W * math.pi))))
    pts.append((SW, S(BRIDGE_FACE[0])))
    d.polygon(pts, fill=C["grass"])
    # bushes
    for x, r in [(60, 50), (170, 38), (880, 46), (990, 56), (300, 30), (760, 32)]:
        yb = BRIDGE_TOP + 30 - 30 * math.sin(x / W * math.pi) + 6
        d.ellipse([S(x - r), S(yb - r * 1.3), S(x + r), S(yb + r * 0.3)], fill=C["grass_d"])
    # concrete face
    d.rectangle([0, S(BRIDGE_FACE[0]), SW, S(BRIDGE_FACE[1])], fill=C["concrete"])
    d.rectangle([0, S(BRIDGE_FACE[1] - 16), SW, S(BRIDGE_FACE[1])], fill=C["concrete_d"])
    d.line([(0, S(BRIDGE_FACE[0])), (SW, S(BRIDGE_FACE[0]))], fill=C["ink"], width=S(6))
    d.line([(0, S(BRIDGE_FACE[1])), (SW, S(BRIDGE_FACE[1]))], fill=C["ink"], width=S(6))
    if sign and sign_a > 0:
        sc = pop(sign_a)
        w, h = 900 * sc, 84 * sc
        cy = (BRIDGE_FACE[0] + BRIDGE_FACE[1]) / 2
        d.rounded_rectangle([S(540 - w / 2), S(cy - h / 2), S(540 + w / 2), S(cy + h / 2)], radius=S(14), fill=(40, 130, 80), outline=C["white"], width=S(5))
        if sc > 0.5:
            text_center(d, 540, cy, sign, 40 * sc, fill=C["white"])

def bridge_y(x):
    return BRIDGE_TOP + 30 - 30 * math.sin(x / W * math.pi) + 8

def draw_road_scene(img, t, cars, bridge=True, sign=None, sign_a=0.0, walkers=()):
    d = ImageDraw.Draw(img)
    draw_clouds(d, t)
    draw_lane_dashes(d, t)
    # far cars first, near cars after the bridge
    near = []
    order = sorted(cars, key=lambda c: car_state(t, c[0], c[1], c[2]))
    for lane, sp, off, col in order:
        u = car_state(t, lane, sp, off)
        y = HORIZON + (H - HORIZON) * (u ** 1.8)
        if y < BRIDGE_FACE[1] + 30: draw_car(d, u, lane, col)
        else: near.append((u, lane, col))
    if bridge:
        draw_bridge(d, t, sign, sign_a)
        for fn in walkers: fn(d)
    for u, lane, col in near:
        draw_car(d, u, lane, col)

# ---------- animals (side view) ----------
SPECIES = {
    "coyote":   dict(body=(176, 150, 120), belly=(236, 220, 196), ear="point", tail="bushy", size=1.0, snout=0.5),
    "lion":     dict(body=(222, 170, 100), belly=(250, 226, 180), ear="round", tail="long", size=1.35, snout=0.14),
    "bobcat":   dict(body=(200, 150, 100), belly=(246, 228, 200), ear="tuft", tail="stub", size=0.9, snout=0.3, spots=True),
    "deer":     dict(body=(190, 130, 80), belly=(246, 226, 196), ear="long", tail="stub", size=1.25, snout=0.45, antler=True, legs=1.5),
    "fox":      dict(body=(255, 130, 50), belly=(255, 246, 236), ear="point", tail="fox", size=0.8, snout=0.55),
}

def draw_animal(d, x, y, kind, phase=0.0, scale=1.0, facing=1, mouth_stick=False):
    """(x,y) = point between the feet on the ground, in design coords."""
    sp = SPECIES[kind]
    k = 60 * sp["size"] * scale
    L = sp.get("legs", 1.0)
    f = facing
    def P(px, py): return (S(x + f * px * k), S(y - py * k))
    ink = C["ink"]; lw = max(2, int(S(k * 0.07)))
    leg_h = 0.72 * L
    by = leg_h + 0.45
    body = sp["body"]; belly = sp["belly"]
    # tail
    tt = sp["tail"]; wag = math.sin(phase * 2) * 0.12
    if tt == "bushy":
        d.polygon([P(-0.95, by + 0.15), P(-1.65, by - 0.25 + wag), P(-1.55, by - 0.55 + wag), P(-0.9, by - 0.15)], fill=body, outline=ink, width=lw)
    elif tt == "fox":
        d.polygon([P(-0.9, by + 0.15), P(-1.7, by + 0.1 + wag), P(-1.9, by - 0.3 + wag), P(-0.9, by - 0.2)], fill=body, outline=ink, width=lw)
        d.polygon([P(-1.6, by + 0.08 + wag), P(-1.9, by - 0.3 + wag), P(-1.62, by - 0.22 + wag)], fill=C["white"], outline=ink, width=lw)
    elif tt == "long":
        pts = [P(-0.95, by + 0.1)]
        for i in range(1, 9):
            s_ = i / 8
            pts.append(P(-0.95 - 1.2 * s_, by + 0.1 - 0.7 * math.sin(s_ * 2.2) + 0.5 * s_ ** 3 + wag * s_))
        d.line(pts, fill=ink, width=int(lw * 3.2), joint="curve")
        d.line(pts, fill=body, width=int(lw * 1.6), joint="curve")
    else:
        d.ellipse([P(-1.1, by + 0.35)[0] if f > 0 else P(-0.8, by + 0.35)[0], P(-1, by + 0.35)[1],
                   P(-0.8, by)[0] if f > 0 else P(-1.1, by)[0], P(-1, by)[1]], fill=belly, outline=ink, width=lw)
    # legs (back pair darker)
    for i, (lx, ph) in enumerate([(-0.6, 0), (0.55, math.pi), (-0.5, math.pi), (0.65, 0)]):
        sw = math.sin(phase + ph) * 0.28
        col = tuple(int(c * 0.82) for c in body) if i < 2 else body
        top = P(lx, leg_h + 0.15); foot = P(lx + sw, 0.02)
        d.line([top, foot], fill=ink, width=int(S(k * 0.34)))
        d.line([top, foot], fill=col, width=int(S(k * 0.2)))
        r_ = S(k * 0.17); d.ellipse([foot[0] - r_, foot[1] - r_, foot[0] + r_, foot[1] + r_], fill=ink)
    # body
    bx0, bx1 = -1.05, 1.0
    a, b = P(bx0, by + 0.45), P(bx1, by - 0.45)
    d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=body, outline=ink, width=lw)
    a, b = P(-0.6, by - 0.05), P(0.7, by - 0.43)
    d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=belly)
    if sp.get("spots"):
        for sx, sy in [(-0.5, by + 0.2), (0.0, by + 0.25), (0.45, by + 0.15), (-0.2, by + 0.02), (0.3, by - 0.05)]:
            a, b = P(sx - 0.07, sy + 0.07), P(sx + 0.07, sy - 0.07)
            d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=(120, 80, 50))
    # head
    bob = math.sin(phase * 2) * 0.04
    hx, hy = 1.15, by + 0.5 + bob
    # ears
    et = sp["ear"]
    if et in ("point", "tuft", "long"):
        eh = 0.55 if et != "long" else 0.5
        for ex in (-0.05, 0.22):
            d.polygon([P(hx + ex - 0.16, hy + 0.2), P(hx + ex + 0.02, hy + 0.2 + eh), P(hx + ex + 0.18, hy + 0.2)], fill=body, outline=ink, width=lw)
            if et == "tuft":
                d.line([P(hx + ex + 0.02, hy + 0.2 + eh), P(hx + ex + 0.05, hy + 0.32 + eh)], fill=ink, width=lw)
    else:
        for ex in (-0.05, 0.2):
            a, b = P(hx + ex - 0.14, hy + 0.5), P(hx + ex + 0.14, hy + 0.22)
            d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=body, outline=ink, width=lw)
    if sp.get("antler"):
        for ex in (-0.02, 0.18):
            base = P(hx + ex, hy + 0.38)
            d.line([base, P(hx + ex - 0.05, hy + 1.0)], fill=(120, 80, 40), width=int(lw * 1.6))
            d.line([P(hx + ex - 0.03, hy + 0.75), P(hx + ex + 0.25, hy + 0.95)], fill=(120, 80, 40), width=int(lw * 1.4))
            d.line([P(hx + ex - 0.04, hy + 0.9), P(hx + ex - 0.3, hy + 1.1)], fill=(120, 80, 40), width=int(lw * 1.4))
    a, b = P(hx - 0.38, hy + 0.38), P(hx + 0.38, hy - 0.34)
    d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=body, outline=ink, width=lw)
    sn = sp["snout"]
    d.polygon([P(hx + 0.2, hy + 0.12), P(hx + 0.3 + sn, hy - 0.08), P(hx + 0.25 + sn * 0.9, hy - 0.22), P(hx + 0.15, hy - 0.28)], fill=belly, outline=ink, width=lw)
    nx, ny = P(hx + 0.3 + sn, hy - 0.1)
    r = S(k * 0.08)
    d.ellipse([nx - r, ny - r, nx + r, ny + r], fill=ink)
    ex_, ey_ = P(hx + 0.12, hy + 0.1)
    r = S(k * 0.075)
    d.ellipse([ex_ - r, ey_ - r, ex_ + r, ey_ + r], fill=ink)
    d.ellipse([ex_ - r * 0.35 + f * r * 0.3, ey_ - r * 0.7, ex_ + r * 0.25 + f * r * 0.3, ey_ - r * 0.1], fill=C["white"])
    if mouth_stick:
        d.line([P(hx + 0.05, hy - 0.3), P(hx + 0.75 + sn, hy - 0.18)], fill=(130, 84, 44), width=int(lw * 2.2))

# ---------- confetti ----------
def draw_confetti(d, t, t0, n=70, seed=5):
    if t < t0: return
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W); vy = rnd.uniform(380, 700); vx = rnd.uniform(-80, 80)
        delay = rnd.uniform(0, 0.8); col = rnd.choice(CAR_COLORS[:6] + [C["teal"]])
        tt = t - t0 - delay
        if tt < 0: continue
        x = x0 + vx * tt + 30 * math.sin(tt * 4 + i)
        y = -40 + vy * tt
        if y > H: continue
        a = tt * 6 + i
        s = 14
        pts = [(S(x + math.cos(a + q) * s), S(y + math.sin(a + q) * s * 0.5)) for q in (0, 1.6, 3.14, 4.7)]
        d.polygon(pts, fill=col)

def finish(img):
    return img.convert("RGB").resize((W, H), Image.LANCZOS)
