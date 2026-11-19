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

# ---------- shared backdrops ----------
def sunburst(d, cx, cy, t, col, n=16, speed=0.3, width=0.18):
    for i in range(n):
        a0 = i * 2 * math.pi / n + t * speed
        d.polygon([(S(cx), S(cy)), (S(cx + 1800 * math.cos(a0)), S(cy + 1800 * math.sin(a0))),
                   (S(cx + 1800 * math.cos(a0 + width)), S(cy + 1800 * math.sin(a0 + width)))], fill=col)

def paste_scaled(img, lay, cx, cy, scale=1.0, rot=0):
    if scale <= 0.01: return
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    if scale != 1.0:
        lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.BICUBIC)
    img.alpha_composite(lay, (int(S(cx) - lay.width / 2), int(S(cy) - lay.height / 2)))

# ---------- space ----------
def make_space_bg(seed=7, top=(10, 12, 40), bot=(52, 30, 100)):
    img = vgrad(SW, SH, top, bot).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(220):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice([1.5, 2, 2.5, 3, 4])
        a = rnd.randint(150, 255)
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=(a, a, min(255, a + 20)))
    # soft nebula blobs
    neb = Image.new("RGBA", (SW, SH), (0, 0, 0, 0)); nd = ImageDraw.Draw(neb)
    for (x, y, r, col) in [(200, 500, 320, (120, 60, 200, 60)), (900, 1300, 380, (40, 120, 220, 55)), (600, 1800, 300, (220, 80, 160, 45))]:
        nd.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=col)
    neb = neb.filter(ImageFilter.GaussianBlur(S(90)))
    img.alpha_composite(neb)
    return img

def draw_twinkles(d, t, seed=11, n=26):
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.uniform(40, W - 40), rnd.uniform(40, H - 40)
        s = 6 + 8 * (0.5 + 0.5 * math.sin(t * 3 + i * 1.7))
        col = (255, 250, 210)
        d.polygon([(S(x), S(y - s)), (S(x + s * 0.25), S(y)), (S(x), S(y + s)), (S(x - s * 0.25), S(y))], fill=col)
        d.polygon([(S(x - s), S(y)), (S(x), S(y + s * 0.25)), (S(x + s), S(y)), (S(x), S(y - s * 0.25))], fill=col)

def draw_planet(d, cx, cy, r, col, bands=(), rings=None, outline=True):
    ink = C["ink"]
    if rings:
        rc = rings
        d.ellipse([S(cx - r * 2.1), S(cy - r * 0.55), S(cx + r * 2.1), S(cy + r * 0.55)], outline=ink, width=int(S(max(4, r * 0.22))))
        d.ellipse([S(cx - r * 2.1), S(cy - r * 0.55), S(cx + r * 2.1), S(cy + r * 0.55)], outline=rc, width=int(S(max(2, r * 0.14))))
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=col, outline=ink if outline else None, width=S(6))
    for (dy, h, bc) in bands:
        y0, y1 = cy + dy * r - h * r / 2, cy + dy * r + h * r / 2
        hw0 = math.sqrt(max(0, r * r - (min(abs(y0 - cy), abs(y1 - cy))) ** 2)) * 0.94
        d.rounded_rectangle([S(cx - hw0), S(y0), S(cx + hw0), S(y1)], radius=S(h * r / 2), fill=bc)
    if rings:
        # front half of the ring
        d.arc([S(cx - r * 2.1), S(cy - r * 0.55), S(cx + r * 2.1), S(cy + r * 0.55)], 0, 180, fill=ink, width=int(S(max(4, r * 0.22))))
        d.arc([S(cx - r * 2.1), S(cy - r * 0.55), S(cx + r * 2.1), S(cy + r * 0.55)], 0, 180, fill=rings, width=int(S(max(2, r * 0.14))))

def draw_earth(d, cx, cy, r):
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=(60, 140, 255), outline=C["ink"], width=S(6))
    for (dx, dy, rx, ry) in [(-0.35, -0.3, 0.32, 0.22), (0.25, 0.1, 0.3, 0.35), (-0.2, 0.45, 0.22, 0.14), (0.45, -0.45, 0.16, 0.12)]:
        d.ellipse([S(cx + (dx - rx) * r), S(cy + (dy - ry) * r), S(cx + (dx + rx) * r), S(cy + (dy + ry) * r)], fill=(110, 210, 110))
    d.arc([S(cx - r * 0.75), S(cy - r * 0.75), S(cx + r * 0.75), S(cy + r * 0.75)], 200, 250, fill=(220, 240, 255), width=int(S(max(3, r * 0.08))))

def draw_voyager(img, cx, cy, scale=1.0, rot=0):
    """Voyager-style probe: big white dish, gold bus, booms. Dish faces left."""
    k = 1.0
    w, h = 760, 520
    lay = Image.new("RGBA", (S(w), S(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ink = C["ink"]; ox, oy = 380, 260
    def P(x, y): return (S(ox + x), S(oy + y))
    lw = S(6)
    # long magnetometer boom (up-right)
    d.line([P(20, -10), P(340, -230)], fill=ink, width=S(10)); d.line([P(20, -10), P(340, -230)], fill=(230, 230, 240), width=S(4))
    # science boom (right) with instruments
    d.line([P(30, 20), P(250, 70)], fill=ink, width=S(16)); d.line([P(30, 20), P(250, 70)], fill=(200, 200, 210), width=S(8))
    d.rounded_rectangle([P(220, 40)[0], P(220, 40)[1], P(290, 105)[0], P(290, 105)[1]], radius=S(10), fill=(120, 120, 140), outline=ink, width=lw)
    d.ellipse([P(250, 55)[0], P(250, 55)[1], P(282, 87)[0], P(282, 87)[1]], fill=(80, 160, 255), outline=ink, width=S(4))
    # RTG boom (down-right) with fins
    d.line([P(20, 40), P(200, 220)], fill=ink, width=S(16)); d.line([P(20, 40), P(200, 220)], fill=(200, 200, 210), width=S(8))
    for i in range(3):
        x, y = 110 + i * 40, 130 + i * 40
        d.rounded_rectangle([P(x - 20, y - 20)[0], P(x - 20, y - 20)[1], P(x + 20, y + 20)[0], P(x + 20, y + 20)[1]], radius=S(6), fill=(110, 110, 120), outline=ink, width=S(4))
    # bus (gold foil decagon box)
    d.rounded_rectangle([P(-40, -30)[0], P(-40, -30)[1], P(60, 70)[0], P(60, 70)[1]], radius=S(10), fill=(232, 182, 70), outline=ink, width=lw)
    d.line([P(-40, 20), P(60, 20)], fill=(190, 140, 40), width=S(4))
    d.line([P(10, -30), P(10, 70)], fill=(190, 140, 40), width=S(4))
    # golden record
    d.ellipse([P(20, -20)[0], P(20, -20)[1], P(52, 12)[0], P(52, 12)[1]], fill=(255, 220, 90), outline=ink, width=S(4))
    # dish (side view, faces left)
    d.ellipse([P(-150, -180)[0], P(-150, -180)[1], P(-40, 200)[0], P(-40, 200)[1]], fill=(250, 250, 255), outline=ink, width=S(8))
    d.ellipse([P(-130, -140)[0], P(-130, -140)[1], P(-70, 160)[0], P(-70, 160)[1]], fill=(222, 230, 245))
    # feed horn struts
    for yy in (-150, 170):
        d.line([P(-95, yy), P(-210, 10)], fill=ink, width=S(5))
    d.rounded_rectangle([P(-235, -6)[0], P(-235, -6)[1], P(-200, 26)[0], P(-200, 26)[1]], radius=S(6), fill=(200, 200, 210), outline=ink, width=S(4))
    paste_scaled(img, lay, cx, cy, scale, rot)

def draw_glow(img, cx, cy, r, col=(255, 236, 120)):
    lay = Image.new("RGBA", (int(S(r * 6)), int(S(r * 6))), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = r * 3
    d.ellipse([S(c - r * 2.4), S(c - r * 2.4), S(c + r * 2.4), S(c + r * 2.4)], fill=col + (90,))
    lay = lay.filter(ImageFilter.GaussianBlur(S(r * 0.7)))
    d = ImageDraw.Draw(lay)
    d.ellipse([S(c - r), S(c - r), S(c + r), S(c + r)], fill=(255, 255, 240, 255))
    img.alpha_composite(lay, (int(S(cx - c)), int(S(cy - c))))

def draw_clock(d, cx, cy, r, frac, face=C["white"]):
    """frac 0..1 = hour hand sweep over 24h (two turns)."""
    ink = C["ink"]
    d.ellipse([S(cx - r + 8), S(cy - r + 14), S(cx + r + 8), S(cy + r + 14)], fill=ink)
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=face, outline=ink, width=S(8))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        d.line([(S(cx + math.sin(a) * r * 0.8), S(cy - math.cos(a) * r * 0.8)), (S(cx + math.sin(a) * r * 0.92), S(cy - math.cos(a) * r * 0.92))], fill=ink, width=S(6))
    ah = frac * 4 * math.pi; am = frac * 48 * math.pi
    d.line([(S(cx), S(cy)), (S(cx + math.sin(ah) * r * 0.5), S(cy - math.cos(ah) * r * 0.5))], fill=ink, width=S(12))
    d.line([(S(cx), S(cy)), (S(cx + math.sin(am) * r * 0.75), S(cy - math.cos(am) * r * 0.75))], fill=C["pink"], width=S(8))
    d.ellipse([S(cx - 12), S(cy - 12), S(cx + 12), S(cy + 12)], fill=ink)

def draw_envelope(d, cx, cy, w, col=C["white"]):
    h = w * 0.66; ink = C["ink"]
    d.rectangle([S(cx - w / 2), S(cy - h / 2), S(cx + w / 2), S(cy + h / 2)], fill=col, outline=ink, width=S(6))
    d.line([(S(cx - w / 2), S(cy - h / 2)), (S(cx), S(cy + h * 0.1)), (S(cx + w / 2), S(cy - h / 2))], fill=ink, width=S(6))

def draw_waves(d, cx, cy, t, facing=-1, n=3, col=(120, 255, 200)):
    for i in range(n):
        p = (t * 1.2 + i / n) % 1.0
        r = 40 + p * 220
        a0, a1 = (150, 210) if facing < 0 else (-30, 30)
        alpha_w = max(2, int(S(10 * (1 - p))))
        d.arc([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], a0, a1, fill=col, width=alpha_w)

def draw_side_car(d, cx, y, w, col=(255, 92, 92)):
    ink = C["ink"]; h = w * 0.32
    d.rounded_rectangle([S(cx - w / 2), S(y - h - w * 0.08), S(cx + w / 2), S(y - w * 0.08)], radius=S(h * 0.35), fill=col, outline=ink, width=S(6))
    d.rounded_rectangle([S(cx - w * 0.28), S(y - h * 1.9), S(cx + w * 0.22), S(y - h * 0.9)], radius=S(h * 0.3), fill=col, outline=ink, width=S(6))
    d.rounded_rectangle([S(cx - w * 0.22), S(y - h * 1.72), S(cx + w * 0.16), S(y - h * 1.05)], radius=S(h * 0.18), fill=(190, 230, 255))
    for sx in (-0.3, 0.3):
        r = w * 0.12
        d.ellipse([S(cx + sx * w - r), S(y - r * 1.6), S(cx + sx * w + r), S(y + r * 0.4)], fill=ink)
        d.ellipse([S(cx + sx * w - r * 0.45), S(y - r * 1.05), S(cx + sx * w + r * 0.45), S(y - r * 0.15)], fill=(200, 200, 210))

def draw_heart(d, cx, cy, s, col=C["pink"]):
    ink = C["ink"]
    d.ellipse([S(cx - s), S(cy - s * 0.8), S(cx), S(cy + s * 0.2)], fill=col)
    d.ellipse([S(cx), S(cy - s * 0.8), S(cx + s), S(cy + s * 0.2)], fill=col)
    d.polygon([(S(cx - s * 0.97), S(cy - s * 0.15)), (S(cx + s * 0.97), S(cy - s * 0.15)), (S(cx), S(cy + s * 1.0))], fill=col)

# ---------- rhino (side view) ----------
def draw_rhino(d, x, y, scale=1.0, facing=1, phase=0.0, baby=False, walking=True, head_up=0.0):
    """Greater one-horned rhino. (x,y) = ground point between the feet."""
    k = 70 * scale
    f = facing
    def P(px, py): return (S(x + f * px * k), S(y - py * k))
    def E(x0, y0, x1, y1, **kw):
        a, b = P(x0, y0), P(x1, y1)
        d.ellipse([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], **kw)
    ink = C["ink"]; lw = max(2, int(S(k * 0.06)))
    body = (196, 170, 176) if baby else (150, 142, 150)
    dark = tuple(int(c * 0.82) for c in body)
    light = tuple(min(255, int(c * 1.12)) for c in body)
    leg_h = 0.62 if baby else 0.55
    by = leg_h + 0.55
    sw_amp = 0.18 if walking else 0.0
    # tail
    d.line([P(-1.15, by + 0.15), P(-1.32, by - 0.3)], fill=ink, width=int(lw * 1.6))
    E(-1.4, by - 0.25, -1.24, by - 0.45, fill=ink)
    # legs
    for i, (lx, ph) in enumerate([(-0.75, 0), (0.6, math.pi), (-0.55, math.pi), (0.8, 0)]):
        sw = math.sin(phase + ph) * sw_amp
        col = dark if i < 2 else body
        top = P(lx, by - 0.1); foot = P(lx + sw, 0.06)
        d.line([top, foot], fill=ink, width=int(S(k * 0.42)))
        d.line([top, foot], fill=col, width=int(S(k * 0.3)))
        r_ = S(k * 0.22)
        d.rounded_rectangle([foot[0] - r_, foot[1] - r_ * 0.6, foot[0] + r_, foot[1] + r_ * 0.4], radius=r_ * 0.4, fill=ink)
    # body
    E(-1.25, by + 0.62, 1.05, by - 0.55, fill=body, outline=ink, width=lw)
    E(-0.7, by - 0.1, 0.65, by - 0.5, fill=light)
    # armor folds
    d.arc([min(P(0.1, 0)[0], P(0.8, 0)[0]), P(0, by + 0.6)[1], max(P(0.1, 0)[0], P(0.8, 0)[0]), P(0, by - 0.5)[1]],
          90 if f > 0 else 270, 270 if f > 0 else 90, fill=ink, width=lw)
    d.arc([min(P(-0.85, 0)[0], P(-0.2, 0)[0]), P(0, by + 0.6)[1], max(P(-0.85, 0)[0], P(-0.2, 0)[0]), P(0, by - 0.5)[1]],
          90 if f > 0 else 270, 270 if f > 0 else 90, fill=ink, width=lw)
    for (sx, sy) in [(-0.95, by + 0.1), (-0.8, by - 0.15), (-1.05, by - 0.2), (0.75, by - 0.05), (0.85, by + 0.2), (0.65, by - 0.3)]:
        E(sx - 0.05, sy + 0.05, sx + 0.05, sy - 0.05, fill=dark)
    # head (tilted down; head_up raises it)
    hu = head_up * 0.3 + math.sin(phase * 2) * 0.03
    hs = 1.15 if baby else 1.0
    def H(px, py): return P(0.85 + (px - 0.85) * hs, by + (py - by) * hs + hu)
    pts = [H(0.8, by + 0.4), H(1.3, by + 0.3), H(1.85, by - 0.2), H(1.85, by - 0.48), H(1.4, by - 0.55), H(0.85, by - 0.25)]
    d.polygon(pts, fill=body, outline=ink, width=lw)
    # horn
    if baby:
        d.polygon([H(1.62, by - 0.2), H(1.78, by - 0.25), H(1.7, by - 0.08)], fill=(220, 200, 180), outline=ink, width=lw)
    else:
        d.polygon([H(1.5, by - 0.16), H(1.82, by - 0.3), H(1.62, by + 0.42)], fill=(110, 96, 90), outline=ink, width=lw)
    # ears
    for ex in (0.98, 1.1):
        a, b = H(ex - 0.09, by + 0.62), H(ex + 0.09, by + 0.3)
        d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=body, outline=ink, width=lw)
    # eye
    ex_, ey_ = H(1.3, by + 0.05)
    r = S(k * (0.09 if baby else 0.065))
    d.ellipse([ex_ - r, ey_ - r, ex_ + r, ey_ + r], fill=ink)
    d.ellipse([ex_ - r * 0.3 + f * r * 0.3, ey_ - r * 0.7, ex_ + r * 0.3 + f * r * 0.3, ey_ - r * 0.1], fill=C["white"])
    # nostril + smile
    nx, ny = H(1.78, by - 0.38); r = S(k * 0.04)
    d.ellipse([nx - r, ny - r, nx + r, ny + r], fill=ink)
    d.line([H(1.45, by - 0.47), H(1.7, by - 0.43)], fill=ink, width=lw)

def make_zoo_bg(night=False):
    if night:
        img = vgrad(SW, SH, (30, 36, 80), (70, 60, 120)).convert("RGBA")
    else:
        img = vgrad(SW, SH, (130, 210, 255), (220, 246, 255)).convert("RGBA")
    d = ImageDraw.Draw(img)
    gr1 = (60, 110, 90) if night else (126, 204, 120)
    gr2 = (44, 90, 74) if night else (98, 186, 98)
    pts = [(0, SH)]
    for x in range(0, W + 20, 20):
        pts.append((S(x), S(1080 - 60 * (0.5 + 0.5 * math.sin(x / 520 * 2 * math.pi + 0.5)))))
    pts.append((SW, SH)); d.polygon(pts, fill=gr1)
    d.rectangle([0, S(1250), SW, SH], fill=gr2)
    # trees
    for tx, ts in [(110, 1.0), (980, 1.2), (820, 0.7)]:
        d.rectangle([S(tx - 16 * ts), S(1060 - 160 * ts), S(tx + 16 * ts), S(1100)], fill=(120, 80, 50) if not night else (70, 50, 40))
        for dx, dy, r in [(0, -230, 110), (-70, -170, 80), (70, -170, 80)]:
            d.ellipse([S(tx + dx * ts - r * ts), S(1060 + dy * ts - r * ts), S(tx + dx * ts + r * ts), S(1060 + dy * ts + r * ts)],
                      fill=(70, 160, 80) if not night else (40, 90, 60))
    # wooden fence
    fc = (190, 140, 90) if not night else (110, 84, 64)
    for x in range(-20, W + 40, 90):
        d.rectangle([S(x), S(1150), S(x + 22), S(1260)], fill=fc, outline=C["ink"], width=S(4))
    for yy in (1170, 1220):
        d.rectangle([0, S(yy), SW, S(yy + 18)], fill=fc, outline=C["ink"], width=S(4))
    return img
