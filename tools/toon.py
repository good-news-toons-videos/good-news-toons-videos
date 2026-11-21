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

CAPTION_Y = 1640   # legacy default (ep001-003)
CAPTION_X = 540
CAPTION_MAXW = 1000

def set_safe_captions():
    """Monetization safe zone (from ep004): keep captions above the apps' bottom UI and clear of the right-side buttons."""
    global CAPTION_Y, CAPTION_X, CAPTION_MAXW
    CAPTION_Y, CAPTION_X, CAPTION_MAXW = 1470, 510, 840

def draw_caption(img, chunks, t, y=None):
    if y is None: y = CAPTION_Y
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
    if w > S(CAPTION_MAXW):
        size *= S(CAPTION_MAXW) / w
    text_center(d, CAPTION_X, y, s.upper(), size, fill=C["white"], stroke=9, stroke_fill=C["ink"])

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


# =====================================================================
# Batch 2 (ep004-ep010) props and scenery
# =====================================================================
def E2(d, x0, y0, x1, y1, **kw):
    """ellipse in design coords, any corner order"""
    d.ellipse([S(min(x0, x1)), S(min(y0, y1)), S(max(x0, x1)), S(max(y0, y1))], **kw)

def wavy_band(d, y, amp, per, ph, col, bottom=None):
    pts = [(0, S(bottom if bottom is not None else H))]
    for x in range(0, W + 20, 20):
        pts.append((S(x), S(y + amp * math.sin(x / per * 2 * math.pi + ph))))
    pts.append((SW, S(bottom if bottom is not None else H)))
    d.polygon(pts, fill=col)

# ---------- beach / sea turtles ----------
def make_beach_bg(night=False, dawn=False):
    if night:
        img = vgrad(SW, SH, (24, 30, 78), (70, 70, 150)).convert("RGBA")
    elif dawn:
        img = vgrad(SW, SH, (90, 100, 200), (255, 170, 140)).convert("RGBA")
    else:
        img = vgrad(SW, SH, (110, 200, 255), (220, 246, 255)).convert("RGBA")
    d = ImageDraw.Draw(img)
    if night:
        rnd = random.Random(2)
        for _ in range(70):
            x, y, r = rnd.uniform(0, W), rnd.uniform(0, 700), rnd.uniform(2, 4)
            d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=(255, 255, 230))
        d.ellipse([S(780), S(200), S(920), S(340)], fill=(255, 246, 200))
    elif dawn:
        d.ellipse([S(440), S(760), S(640), S(960)], fill=(255, 220, 120))
    else:
        d.ellipse([S(800), S(170), S(980), S(350)], fill=C["sun"])
    sea = (40, 110, 190) if night else ((90, 120, 200) if dawn else (40, 150, 230))
    d.rectangle([0, S(860), SW, S(1180)], fill=sea)
    sand = (150, 130, 120) if night else (246, 214, 150)
    wavy_band(d, 1180, 16, 400, 0.4, sand)
    return img

def draw_surf(d, t, y=1170, night=False):
    col = (200, 220, 255) if night else C["white"]
    for k in range(3):
        ph = t * 1.6 + k * 2.1
        yy = y - 40 * k + 10 * math.sin(ph)
        pts = []
        for x in range(-20, W + 40, 30):
            pts.append((S(x), S(yy + 8 * math.sin(x / 90 + ph))))
        d.line(pts, fill=col, width=int(S(7 - k * 2)))

def draw_turtle(d, x, y, scale=1.0, phase=0.0, facing=1, adult=False, col=None, ang=0.0):
    """Top-down cartoon sea turtle (head points in +x if facing=1, rotated by ang radians; -pi/2 = heading up). (x,y)=shell centre."""
    k = 60 * scale; f = facing; ink = C["ink"]; lw = max(2, int(S(k * 0.07)))
    shell = col or ((120, 150, 90) if adult else (110, 120, 110))
    skin = (150, 180, 130) if adult else (140, 150, 140)
    ca, sa = math.cos(ang), math.sin(ang)
    def P(px, py):
        qx, qy = f * px * k, py * k
        return (S(x + qx * ca - qy * sa), S(y + qx * sa + qy * ca))
    fl = math.sin(phase) * 0.35
    for sy in (-1, 1):  # front flippers
        d.polygon([P(0.35, sy * 0.35), P(0.2 - fl * 0.2, sy * (0.95 + fl * 0.6)), P(-0.4 - fl * 0.3, sy * (1.3 + fl)), P(-0.2, sy * (0.85 + fl * 0.4)), P(-0.15, sy * 0.5)], fill=skin, outline=ink, width=lw)
    for sy in (-1, 1):  # back flippers
        d.polygon([P(-0.55, sy * 0.3), P(-0.95, sy * (0.65 - fl * 0.4)), P(-0.8, sy * 0.25)], fill=skin, outline=ink, width=lw)
    def OV(cx_, cy_, rx, ry, **kw):
        d.polygon([P(cx_ + rx * math.cos(a_), cy_ + ry * math.sin(a_)) for a_ in [i_ * math.pi / 14 for i_ in range(28)]], **kw)
    OV(0.85, 0, 0.3, 0.3, fill=skin, outline=ink, width=lw)
    OV(0.95, -0.14, 0.08, 0.08, fill=ink)
    OV(0.95, 0.14, 0.08, 0.08, fill=ink)
    OV(-0.075, 0, 0.675, 0.6, fill=shell, outline=ink, width=lw)
    dk = tuple(int(c * 0.78) for c in shell)
    for (px, py, rr) in [(-0.07, 0, 0.22), (-0.45, 0, 0.14), (0.3, 0, 0.14), (-0.1, -0.36, 0.13), (-0.1, 0.36, 0.13)]:
        OV(px, py, rr, rr, fill=dk)

def draw_egg(d, x, y, s, crack=0.0, wob=0.0):
    ink = C["ink"]
    xx = x + wob
    E2(d, xx - s * 0.8, y - s, xx + s * 0.8, y + s * 0.9, fill=(252, 248, 236), outline=ink, width=S(4))
    if crack > 0:
        pts = [(S(xx - s * 0.6), S(y - s * 0.1))]
        for i in range(1, 6):
            pts.append((S(xx - s * 0.6 + i * s * 0.24), S(y - s * 0.1 + (s * 0.18 if i % 2 else -s * 0.12))))
        d.line(pts[:1 + int(5 * clamp(crack))], fill=ink, width=S(4))

def draw_bin(d, cx, cy, w, h):
    ink = C["ink"]
    d.rounded_rectangle([S(cx - w / 2), S(cy - h / 2), S(cx + w / 2), S(cy + h / 2)], radius=S(24), fill=(120, 190, 230), outline=ink, width=S(7))
    d.rectangle([S(cx - w / 2 + 16), S(cy - h / 2 + 30), S(cx + w / 2 - 16), S(cy + h / 2 - 16)], fill=(246, 214, 150))

def draw_thermometer(d, cx, cy, h, frac, col=(255, 90, 80)):
    ink = C["ink"]
    d.rounded_rectangle([S(cx - 28), S(cy - h / 2), S(cx + 28), S(cy + h / 2)], radius=S(28), fill=C["white"], outline=ink, width=S(7))
    E2(d, cx - 52, cy + h / 2 - 40, cx + 52, cy + h / 2 + 64, fill=col, outline=ink, width=S(7))
    top = cy + h / 2 - (h - 30) * clamp(frac)
    d.rectangle([S(cx - 14), S(top), S(cx + 14), S(cy + h / 2 + 10)], fill=col)

# ---------- electric plane ----------
def draw_eplane(img, cx, cy, scale=1.0, rot=0, t=0.0, col=(250, 250, 255), stripe=(40, 200, 180)):
    """Side view high-wing commuter plane with ducted fans along the wing. Nose to the right."""
    w, h = 1000, 460
    lay = Image.new("RGBA", (S(w), S(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ink = C["ink"]; ox, oy = 500, 250
    def P(x, y): return (S(ox + x), S(oy + y))
    lw = S(7)
    # tail fin
    d.polygon([P(-390, -10), P(-440, -190), P(-360, -190), P(-280, -20)], fill=col, outline=ink, width=lw)
    d.polygon([P(-430, -150), P(-372, -150), P(-345, -95), P(-415, -95)], fill=stripe)
    d.polygon([P(-430, -10), P(-470, 25), P(-330, 25), P(-310, -5)], fill=(225, 230, 240), outline=ink, width=lw)
    # fuselage
    d.rounded_rectangle([P(-420, -30)[0], P(-420, -30)[1], P(400, 70)[0], P(400, 70)[1]], radius=S(50), fill=col, outline=ink, width=lw)
    d.polygon([P(360, -30), P(470, 20), P(360, 70)], fill=col, outline=ink, width=lw)
    d.rectangle([P(-400, 30)[0], P(-400, 30)[1], P(420, 44)[0], P(420, 44)[1]], fill=stripe)
    # cockpit window + cabin windows
    d.polygon([P(370, -18), P(430, 12), P(380, 14)], fill=(150, 210, 255), outline=ink, width=S(4))
    for i in range(9):
        x = -300 + i * 70
        d.rounded_rectangle([P(x, -8)[0], P(x, -8)[1], P(x + 34, 18)[0], P(x + 34, 18)[1]], radius=S(10), fill=(150, 210, 255), outline=ink, width=S(4))
    # high wing (thin, seen edge-on) + fans on top
    d.rounded_rectangle([P(-170, -62)[0], P(-170, -62)[1], P(170, -36)[0], P(170, -36)[1]], radius=S(12), fill=(225, 230, 240), outline=ink, width=lw)
    for i in range(5):
        fx = -140 + i * 70
        d.rounded_rectangle([P(fx - 26, -108)[0], P(fx - 26, -108)[1], P(fx + 26, -60)[0], P(fx + 26, -60)[1]], radius=S(14), fill=(80, 90, 110), outline=ink, width=S(5))
        sp = (t * 40 + i) % 1.0
        d.line([P(fx + 18, -104 + 44 * sp), P(fx + 18, -64)], fill=stripe, width=S(5))
    # bolt badge
    d.polygon([P(-40, 52), P(-12, 52), P(-26, 60), P(-6, 60), P(-46, 82), P(-32, 66), P(-50, 66)], fill=C["yellow"])
    # landing gear
    for gx in (-80, 300):
        d.line([P(gx, 70), P(gx, 100)], fill=ink, width=S(8))
        d.ellipse([P(gx - 18, 92)[0], P(gx - 18, 92)[1], P(gx + 18, 128)[0], P(gx + 18, 128)[1]], fill=ink)
    paste_scaled(img, lay, cx, cy, scale, rot)

def draw_battery(d, cx, cy, w, frac, col=(90, 220, 120)):
    ink = C["ink"]; h = w * 0.5
    d.rounded_rectangle([S(cx - w / 2 + 8), S(cy - h / 2 + 12), S(cx + w / 2 + 8), S(cy + h / 2 + 12)], radius=S(18), fill=ink)
    d.rounded_rectangle([S(cx - w / 2), S(cy - h / 2), S(cx + w / 2), S(cy + h / 2)], radius=S(18), fill=C["white"], outline=ink, width=S(7))
    d.rounded_rectangle([S(cx + w / 2), S(cy - h * 0.2), S(cx + w / 2 + 22), S(cy + h * 0.2)], radius=S(6), fill=ink)
    iw = (w - 36) * clamp(frac)
    if iw > 4:
        d.rounded_rectangle([S(cx - w / 2 + 18), S(cy - h / 2 + 18), S(cx - w / 2 + 18 + iw), S(cy + h / 2 - 18)], radius=S(10), fill=col)
    d.polygon([(S(cx + 10), S(cy - h * 0.34)), (S(cx - 26), S(cy + 6)), (S(cx - 2), S(cy + 6)), (S(cx - 12), S(cy + h * 0.34)), (S(cx + 26), S(cy - 6)), (S(cx + 2), S(cy - 6))], fill=C["yellow"], outline=ink, width=S(3))

def draw_person(d, x, y, scale=1.0, phase=0.0, facing=1, body=(255, 120, 80), skin=(240, 190, 150), hat=None, run=0.0, arms_up=0.0, hair=(60, 40, 30), pants=(60, 70, 110)):
    """Simple cartoon person, (x,y)=feet. run 0..1 = running stride amount, arms_up 0..1 = cheering."""
    k = 100 * scale; f = facing; ink = C["ink"]
    def P(px, py): return (S(x + f * px * k), S(y - py * k))
    lw = max(2, int(S(k * 0.17))); ow = lw + max(2, int(S(k * 0.06)))
    hip = (0.0, 0.95)
    sh = (0.05 + 0.1 * run, 1.62)
    def limb(a, b, c, col):
        pts = [P(*a), P(*b), P(*c)]
        d.line(pts, fill=ink, width=ow, joint="curve")
        d.line(pts, fill=col, width=lw, joint="curve")
        r = ow / 2
        for q in pts[1:]:
            d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=ink)
            d.ellipse([q[0] - lw / 2, q[1] - lw / 2, q[0] + lw / 2, q[1] + lw / 2], fill=col)
    def leg(s_):
        ph = phase + (0 if s_ > 0 else math.pi)
        sw = math.sin(ph) * 0.42 * run
        lift = max(0.0, math.cos(ph)) * 0.25 * run
        knee = (hip[0] + sw * 0.6 + 0.12 * run * max(0, math.cos(ph)), 0.5 + lift)
        foot = (sw, 0.04 + lift * 0.9)
        limb(hip, knee, foot, pants if s_ > 0 else tuple(int(c * 0.8) for c in pants))
    def arm(s_):
        col = body if s_ > 0 else tuple(int(c * 0.82) for c in body)
        if arms_up > 0:
            elbow = (sh[0] + 0.32 * s_, sh[1] + 0.3 * arms_up)
            hand = (sh[0] + 0.42 * s_, sh[1] + 0.75 * arms_up)
        else:
            ph = phase + (math.pi if s_ > 0 else 0)
            sw = math.sin(ph) * 0.38 * run
            elbow = (sh[0] + sw * 0.7, sh[1] - 0.32)
            hand = (sh[0] + sw + 0.18 * run, sh[1] - 0.55 + 0.25 * run)
        limb(sh, elbow, hand, col)
    leg(-1); arm(-1)
    a, b = P(-0.26, 1.8), P(0.32, 0.86)
    d.rounded_rectangle([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], radius=S(k * 0.2), fill=body, outline=ink, width=max(2, int(S(k * 0.05))))
    leg(1); arm(1)
    hc = P(0.06 + 0.08 * run, 2.12); r = S(k * 0.32)
    d.ellipse([hc[0] - r, hc[1] - r, hc[0] + r, hc[1] + r], fill=skin, outline=ink, width=max(2, int(S(k * 0.05))))
    if hat:
        d.chord([hc[0] - r * 1.05, hc[1] - r * 1.15, hc[0] + r * 1.05, hc[1] + r * 0.6], 180, 360, fill=hat, outline=ink, width=max(2, int(S(k * 0.05))))
        d.ellipse([hc[0] - r * 0.3, hc[1] - r * 1.5, hc[0] + r * 0.3, hc[1] - r * 0.95], fill=C["white"], outline=ink, width=max(2, int(S(k * 0.04))))
    else:
        d.chord([hc[0] - r, hc[1] - r, hc[0] + r, hc[1] + r * 0.2], 180, 360, fill=hair)
    ex = hc[0] + f * r * 0.42; ey = hc[1] + r * 0.05; er = r * 0.13
    d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=ink)
    mx = hc[0] + f * r * 0.35
    d.arc([mx - r * 0.3, hc[1] + r * 0.1, mx + r * 0.3, hc[1] + r * 0.6], 20, 160, fill=ink, width=max(2, int(S(k * 0.04))))
    d.ellipse([hc[0] + f * r * 0.05 - r * 0.14, hc[1] + r * 0.28, hc[0] + f * r * 0.05 + r * 0.14, hc[1] + r * 0.48], fill=(255, 150, 160))

def make_runway_bg():
    img = vgrad(SW, SH, (120, 196, 255), (230, 246, 255)).convert("RGBA")
    d = ImageDraw.Draw(img)
    wavy_band(d, 1130, 30, 600, 0.2, (130, 200, 120))
    d.rectangle([0, S(1250), SW, SH], fill=(110, 180, 100))
    d.rectangle([0, S(1270), SW, S(1380)], fill=(90, 94, 108))
    for x in range(0, W, 160):
        d.rectangle([S(x + 30), S(1318), S(x + 110), S(1332)], fill=C["white"])
    # control tower
    d.rectangle([S(880), S(960), S(930), S(1250)], fill=(220, 220, 230), outline=C["ink"], width=S(5))
    d.polygon([(S(850), S(960)), (S(960), S(960)), (S(940), S(900)), (S(870), S(900))], fill=(120, 200, 240), outline=C["ink"], width=S(5))
    return img

# ---------- rainforest / monkeys ----------
def make_jungle_bg(seed=4, dark=False):
    img = vgrad(SW, SH, (150, 220, 170) if not dark else (40, 70, 60), (60, 150, 100) if not dark else (20, 50, 40)).convert("RGBA")
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    cols = [(40, 120, 70), (30, 100, 60), (60, 150, 80), (20, 90, 55)]
    if dark: cols = [tuple(int(c * 0.5) for c in cc) for cc in cols]
    for layer in range(3):
        col = cols[layer]
        for i in range(9):
            x = rnd.uniform(-100, W + 100); y = rnd.uniform(200, 1600); r = rnd.uniform(120, 260)
            d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=col)
    for i in range(6):  # trunks
        x = rnd.uniform(40, W - 40)
        d.rectangle([S(x - 18), S(rnd.uniform(300, 900)), S(x + 18), SH], fill=(90, 60, 40) if not dark else (50, 36, 28))
    return img

def draw_vine(d, x0, y0, x1, y1, sag=80, col=(70, 130, 60), width=10):
    pts = []
    for i in range(21):
        u = i / 20
        pts.append((S(x0 + (x1 - x0) * u), S(y0 + (y1 - y0) * u + sag * math.sin(u * math.pi))))
    d.line(pts, fill=C["ink"], width=int(S(width + 6)), joint="curve")
    d.line(pts, fill=col, width=int(S(width)), joint="curve")
    return pts

def draw_monkey(d, x, y, scale=1.0, phase=0.0, facing=1, fur=(200, 70, 40), howl=0.0, beard=True, hang=False):
    """Cartoon howler monkey sitting/walking on a branch. (x,y)=branch contact point."""
    k = 60 * scale; f = facing; ink = C["ink"]; lw = max(2, int(S(k * 0.07)))
    dark = tuple(int(c * 0.75) for c in fur)
    face = (90, 50, 40)
    def P(px, py): return (S(x + f * px * k), S(y - py * k))
    # prehensile tail curling
    pts = []
    for i in range(14):
        u = i / 13
        pts.append(P(-0.7 - 1.0 * u, 0.6 - 1.4 * u + 0.25 * math.sin(phase + u * 3)))
    pts.append(P(-1.75, -0.95)); pts.append(P(-1.55, -1.05))
    d.line(pts, fill=ink, width=int(S(k * 0.3)), joint="curve")
    d.line(pts, fill=fur, width=int(S(k * 0.18)), joint="curve")
    # legs
    st = math.sin(phase) * 0.25
    for i, lx in enumerate((-0.45, 0.45)):
        a = P(lx, 0.6); b = P(lx + (st if i else -st), 0.0)
        d.line([a, b], fill=ink, width=int(S(k * 0.34))); d.line([a, b], fill=dark if i == 0 else fur, width=int(S(k * 0.22)))
    # body
    a, b = P(-0.9, 1.4), P(0.8, 0.35)
    d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=fur, outline=ink, width=lw)
    # arm
    a = P(0.45, 1.05); b = P(0.75 + st, 0.0)
    d.line([a, b], fill=ink, width=int(S(k * 0.32))); d.line([a, b], fill=fur, width=int(S(k * 0.2)))
    # head
    hx, hy = 0.85, 1.55
    a, b = P(hx - 0.5, hy + 0.5), P(hx + 0.5, hy - 0.5)
    d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=fur, outline=ink, width=lw)
    if beard:
        d.polygon([P(hx - 0.25, hy - 0.25), P(hx + 0.45, hy - 0.25), P(hx + 0.15, hy - 0.85)], fill=dark, outline=ink, width=lw)
    a, b = P(hx - 0.05, hy + 0.3), P(hx + 0.55, hy - 0.35)
    d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=face, outline=ink, width=lw)
    ex, ey = P(hx + 0.3, hy + 0.08); r = S(k * 0.08)
    d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=C["white"])
    d.ellipse([ex - r * 0.5, ey - r * 0.5, ex + r * 0.5, ey + r * 0.5], fill=ink)
    mo = 0.05 + 0.22 * howl
    a, b = P(hx + 0.2, hy - 0.1), P(hx + 0.45, hy - 0.1 - mo)
    d.ellipse([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], fill=ink)

def draw_sound_rings(d, cx, cy, t, col=C["yellow"], n=3, facing=1):
    for i in range(n):
        p = (t * 1.5 + i / n) % 1.0
        r = 40 + p * 260
        a0, a1 = (-40, 40) if facing > 0 else (140, 220)
        d.arc([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], a0, a1, fill=col, width=max(2, int(S(12 * (1 - p)))))

def draw_dna(d, cx, cy, h, t, cols=((255, 110, 150), (80, 160, 255))):
    ink = C["ink"]; n = 16
    for i in range(n):
        y = cy - h / 2 + h * i / (n - 1)
        a = t * 2.5 + i * 0.55
        x1 = cx + 110 * math.sin(a); x2 = cx - 110 * math.sin(a)
        d.line([(S(x1), S(y)), (S(x2), S(y))], fill=(220, 220, 230), width=S(8))
        for xx, c in ((x1, cols[0]), (x2, cols[1])):
            d.ellipse([S(xx - 18), S(y - 18), S(xx + 18), S(y + 18)], fill=c, outline=ink, width=S(4))

def draw_rope_bridge(d, x0, x1, y, t, sag=40):
    ink = C["ink"]; rope = (190, 150, 90)
    for dy in (0, -70):
        pts = [(S(x0 + (x1 - x0) * u / 20), S(y + dy + sag * math.sin(u / 20 * math.pi))) for u in range(21)]
        d.line(pts, fill=ink, width=S(14)); d.line(pts, fill=rope, width=S(8))
    for u in range(1, 20, 2):
        xx = x0 + (x1 - x0) * u / 20; yy = y + sag * math.sin(u / 20 * math.pi)
        d.line([(S(xx), S(yy)), (S(xx), S(yy - 70))], fill=rope, width=S(5))

def draw_camtrap(d, x, y, t, s=1.0):
    ink = C["ink"]
    d.rounded_rectangle([S(x - 70 * s), S(y - 80 * s), S(x + 70 * s), S(y + 80 * s)], radius=S(20 * s), fill=(60, 110, 70), outline=ink, width=S(6))
    d.ellipse([S(x - 35 * s), S(y - 40 * s), S(x + 35 * s), S(y + 30 * s)], fill=ink)
    d.ellipse([S(x - 18 * s), S(y - 23 * s), S(x + 18 * s), S(y + 13 * s)], fill=(80, 120, 200))
    d.ellipse([S(x + 38 * s), S(y - 70 * s), S(x + 56 * s), S(y - 52 * s)], fill=(255, 60, 60) if int(t * 2) % 2 == 0 else (100, 30, 30))

def draw_magnifier(d, cx, cy, r, rot=0.0):
    ink = C["ink"]
    hx, hy = cx + math.cos(0.8 + rot) * r * 1.9, cy + math.sin(0.8 + rot) * r * 1.9
    d.line([(S(cx + math.cos(0.8 + rot) * r), S(cy + math.sin(0.8 + rot) * r)), (S(hx), S(hy))], fill=ink, width=S(40))
    d.line([(S(cx + math.cos(0.8 + rot) * r * 1.1), S(cy + math.sin(0.8 + rot) * r * 1.1)), (S(hx), S(hy))], fill=(150, 90, 50), width=S(26))
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=(220, 240, 255, 120), outline=ink, width=S(14))

# ---------- space: quasars ----------
def draw_quasar(img, cx, cy, r, t, col=(255, 200, 90), jet=(140, 200, 255), tilt=0.35):
    """Glowing accretion disk around a black hole with twin jets."""
    lay = Image.new("RGBA", (int(S(r * 8)), int(S(r * 8))), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    c = r * 4
    for i in range(3):
        L = r * (3.2 + 0.25 * math.sin(t * 3 + i))
        wdt = r * (0.22 - i * 0.05)
        d.polygon([(S(c - wdt), S(c)), (S(c + wdt), S(c)), (S(c), S(c - L))], fill=jet + (200,))
        d.polygon([(S(c - wdt), S(c)), (S(c + wdt), S(c)), (S(c), S(c + L))], fill=jet + (200,))
    glow = lay.filter(ImageFilter.GaussianBlur(S(r * 0.15)))
    lay = Image.new("RGBA", lay.size, (0, 0, 0, 0)); lay.alpha_composite(glow); d = ImageDraw.Draw(lay)
    halo = Image.new("RGBA", lay.size, (0, 0, 0, 0)); hd = ImageDraw.Draw(halo)
    hd.ellipse([S(c - r * 2.4), S(c - r * 2.4 * tilt * 1.6), S(c + r * 2.4), S(c + r * 2.4 * tilt * 1.6)], fill=col + (140,))
    halo = halo.filter(ImageFilter.GaussianBlur(S(r * 0.5)))
    lay.alpha_composite(halo); d = ImageDraw.Draw(lay)
    for i, (rr, cc) in enumerate([(2.0, (255, 120, 60)), (1.6, col), (1.25, (255, 250, 220))]):
        d.ellipse([S(c - r * rr), S(c - r * rr * tilt), S(c + r * rr), S(c + r * rr * tilt)], fill=cc + (255,))
    # swirl ticks
    for i in range(10):
        a = t * 2 + i * 0.63
        px, py = c + math.cos(a) * r * 1.7, c + math.sin(a) * r * 1.7 * tilt
        d.ellipse([S(px - r * 0.07), S(py - r * 0.05), S(px + r * 0.07), S(py + r * 0.05)], fill=(255, 255, 255, 230))
    d.ellipse([S(c - r * 0.75), S(c - r * 0.75), S(c + r * 0.75), S(c + r * 0.75)], fill=(5, 5, 15, 255), outline=(255, 240, 200, 255), width=int(S(max(2, r * 0.06))))
    img.alpha_composite(lay, (int(S(cx - c)), int(S(cy - c))))

def draw_telescope_dome(d, cx, base_y, s=1.0, open_=1.0, col=(235, 235, 245)):
    ink = C["ink"]
    d.rectangle([S(cx - 130 * s), S(base_y - 120 * s), S(cx + 130 * s), S(base_y)], fill=col, outline=ink, width=S(6))
    d.chord([S(cx - 140 * s), S(base_y - 260 * s), S(cx + 140 * s), S(base_y + 20 * s)], 180, 360, fill=col, outline=ink, width=S(6))
    if open_ > 0:
        d.rectangle([S(cx - 26 * s), S(base_y - 258 * s), S(cx + 26 * s), S(base_y - 130 * s)], fill=(20, 24, 60))

def make_mountain_night_bg():
    img = make_space_bg(seed=31, top=(8, 10, 40), bot=(40, 40, 110))
    d = ImageDraw.Draw(img)
    d.polygon([(0, S(1500)), (S(300), S(1180)), (S(540), S(1100)), (S(780), S(1190)), (SW, S(1420)), (SW, SH), (0, SH)], fill=(70, 50, 80))
    d.polygon([(S(380), S(1150)), (S(540), S(1100)), (S(690), S(1150)), (S(600), S(1170)), (S(480), S(1165))], fill=(200, 190, 220))
    return img

def draw_webb(img, cx, cy, scale=1.0, rot=0):
    """Gold hexagon-mirror space telescope on a sunshield."""
    lay = Image.new("RGBA", (S(700), S(600)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ink = C["ink"]; ox, oy = 350, 260
    def P(x, y): return (S(ox + x), S(oy + y))
    for i, col in enumerate([(200, 120, 220), (230, 160, 240), (190, 110, 210)]):
        yy = 210 + i * 18
        d.polygon([P(-320 + i * 20, yy), P(320 - i * 20, yy), P(260, yy + 40), P(-260, yy + 40)], fill=col, outline=ink, width=S(4))
    hexes = [(0, 0)] + [(math.cos(a) * 92, math.sin(a) * 92) for a in [i * math.pi / 3 + math.pi / 6 for i in range(6)]]
    hexes += [(math.cos(a) * 184, math.sin(a) * 184) for a in [i * math.pi / 3 + math.pi / 6 for i in range(6)]]
    for hx, hy in hexes[:13]:
        pts = [P(hx + 50 * math.cos(a), hy * 0.9 + 50 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]]
        d.polygon(pts, fill=(255, 200, 70), outline=ink, width=S(4))
    d.line([P(0, 0), P(0, -150)], fill=ink, width=S(8))
    d.ellipse([P(-16, -170)[0], P(-16, -170)[1], P(16, -138)[0], P(16, -138)[1]], fill=(200, 200, 210), outline=ink, width=S(3))
    paste_scaled(img, lay, cx, cy, scale, rot)

# ---------- Antarctica / runner ----------
def make_ice_bg(seed=5):
    img = vgrad(SW, SH, (150, 200, 255), (236, 246, 255)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.ellipse([S(780), S(200), S(940), S(360)], fill=(255, 246, 200))
    d.polygon([(0, S(1050)), (S(200), S(900)), (S(380), S(1000)), (S(600), S(860)), (S(860), S(990)), (SW, S(900)), (SW, S(1150)), (0, S(1150))], fill=(214, 232, 250))
    d.polygon([(S(560), S(900)), (S(600), S(860)), (S(650), S(890))], fill=C["white"])
    wavy_band(d, 1150, 18, 500, 0.7, (246, 250, 255))
    d.line([(0, S(1150)), (SW, S(1150))], fill=(200, 220, 240), width=S(4))
    return img

def draw_snow(d, t, seed=9, n=60, wind=60):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(0, W); sp = rnd.uniform(60, 140); r = rnd.uniform(3, 7)
        y = (rnd.uniform(0, H) + t * sp) % H
        x = (x0 + t * wind + 20 * math.sin(t + i)) % W
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=(255, 255, 255))

def draw_tent(d, cx, base, s=1.0, col=(255, 150, 60)):
    ink = C["ink"]
    d.polygon([(S(cx - 140 * s), S(base)), (S(cx), S(base - 170 * s)), (S(cx + 140 * s), S(base))], fill=col, outline=ink, width=S(6))
    d.polygon([(S(cx - 30 * s), S(base)), (S(cx), S(base - 100 * s)), (S(cx + 30 * s), S(base))], fill=ink)

def draw_flag(d, x, y, t, col=C["pink"], h=200):
    ink = C["ink"]
    d.line([(S(x), S(y)), (S(x), S(y - h))], fill=ink, width=S(8))
    pts = [(S(x), S(y - h))]
    for i in range(1, 7):
        pts.append((S(x + i * 22), S(y - h + 6 * math.sin(t * 5 + i))))
    for i in range(6, -1, -1):
        pts.append((S(x + i * 22), S(y - h + 70 + 6 * math.sin(t * 5 + i))))
    d.polygon(pts, fill=col, outline=ink, width=S(4))

def draw_stopwatch(d, cx, cy, r, frac):
    ink = C["ink"]
    d.rectangle([S(cx - 20), S(cy - r - 40), S(cx + 20), S(cy - r + 4)], fill=ink)
    d.rounded_rectangle([S(cx - 46), S(cy - r - 60), S(cx + 46), S(cy - r - 30)], radius=S(10), fill=C["pink"], outline=ink, width=S(5))
    draw_clock(d, cx, cy, r, frac / 2)

# ---------- underwater / oysters ----------
def make_sea_bg(seed=3):
    img = vgrad(SW, SH, (60, 170, 220), (10, 60, 120)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for i in range(6):  # light rays
        x = 80 + i * 190
        d.polygon([(S(x), 0), (S(x + 80), 0), (S(x + 200), S(1300)), (S(x + 120), S(1300))], fill=(120, 210, 240))
    img2 = vgrad(SW, SH, (60, 170, 220), (10, 60, 120)).convert("RGBA")
    img = Image.blend(img2, img, 0.25)
    d = ImageDraw.Draw(img)
    wavy_band(d, 1320, 20, 380, 1.0, (190, 170, 120))
    rnd = random.Random(seed)
    for i in range(30):
        x, y, r = rnd.uniform(0, W), rnd.uniform(1360, H), rnd.uniform(6, 16)
        d.ellipse([S(x - r), S(y - r * 0.6), S(x + r), S(y + r * 0.6)], fill=(170, 150, 104))
    for x in (90, 980, 860):  # seaweed
        pts = [(S(x + 20 * math.sin(i * 0.6)), S(1340 - i * 40)) for i in range(10)]
        d.line(pts, fill=(40, 140, 80), width=S(16), joint="curve")
    return img

def draw_bubbles(d, t, seed=4, n=18):
    rnd = random.Random(seed)
    for i in range(n):
        x0 = rnd.uniform(60, W - 60); sp = rnd.uniform(80, 170); r = rnd.uniform(6, 16)
        y = 1400 - ((t * sp + rnd.uniform(0, 1400)) % 1500)
        x = x0 + 14 * math.sin(t * 2 + i)
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], outline=(220, 245, 255), width=S(3))

def draw_oyster(d, x, y, scale=1.0, open_=0.0, face=True, col=(170, 160, 150), blink=False):
    """Cartoon flat oyster seen from the side; (x,y) = bottom centre."""
    k = 80 * scale; ink = C["ink"]; lw = max(2, int(S(k * 0.06)))
    dark = tuple(int(c * 0.78) for c in col)
    E2(d, x - 1.1 * k, y - 0.55 * k, x + 1.1 * k, y + 0.05 * k, fill=dark, outline=ink, width=lw)
    if open_ > 0:
        E2(d, x - 0.8 * k, y - 0.55 * k - 0.15 * k, x + 0.8 * k, y - 0.25 * k, fill=(250, 230, 220))
    lift = 0.5 * open_ * k
    top = [(x - 1.1 * k, y - 0.35 * k - lift * 0.3)]
    for i in range(1, 12):
        u = i / 11
        top.append((x - 1.1 * k + 2.2 * k * u, y - 0.35 * k - lift * (1 - u) * 0.3 - lift * u - 0.55 * k * math.sin(u * math.pi) + 0.06 * k * math.sin(u * 30)))
    top.append((x + 1.1 * k, y - 0.3 * k - lift))
    bot = [(x + 1.0 * k, y - 0.25 * k - lift), (x - 1.0 * k, y - 0.25 * k - lift * 0.3)]
    d.polygon([(S(a), S(b)) for a, b in top + bot], fill=col, outline=ink, width=lw)
    for i in range(3):
        u0 = 0.25 + i * 0.22
        d.arc([S(x - k * (1 - u0)), S(y - k * 1.0 - lift * 0.6), S(x + k * (1 - u0)), S(y - k * 0.1 - lift * 0.6)], 200, 340, fill=dark, width=S(3))
    if face:
        fy = y - 0.62 * k - lift * 0.6
        for ex in (-0.28, 0.28):
            if blink:
                d.line([(S(x + ex * k - 0.09 * k), S(fy)), (S(x + ex * k + 0.09 * k), S(fy))], fill=ink, width=S(5))
            else:
                E2(d, x + ex * k - 0.09 * k, fy - 0.12 * k, x + ex * k + 0.09 * k, fy + 0.12 * k, fill=ink)
                E2(d, x + ex * k - 0.03 * k, fy - 0.08 * k, x + ex * k + 0.03 * k, fy - 0.02 * k, fill=C["white"])
        d.arc([S(x - 0.2 * k), S(fy + 0.0 * k), S(x + 0.2 * k), S(fy + 0.3 * k)], 20, 160, fill=ink, width=S(5))
        E2(d, x - 0.55 * k, fy + 0.05 * k, x - 0.38 * k, fy + 0.18 * k, fill=(255, 150, 160))
        E2(d, x + 0.38 * k, fy + 0.05 * k, x + 0.55 * k, fy + 0.18 * k, fill=(255, 150, 160))

def draw_coin(d, cx, cy, r, label="50p"):
    ink = C["ink"]
    pts = [(S(cx + r * math.cos(a)), S(cy + r * math.sin(a))) for a in [i * 2 * math.pi / 7 - math.pi / 2 for i in range(7)]]
    d.polygon([(p[0] + S(8), p[1] + S(12)) for p in pts], fill=ink)
    d.polygon(pts, fill=(210, 214, 222), outline=ink, width=S(7))
    text_center(d, cx, cy, label, r * 0.6, fill=(110, 114, 130))

def draw_fish(d, x, y, s, col, facing=1, t=0.0):
    ink = C["ink"]; f = facing
    wag = math.sin(t * 8) * 0.15
    d.polygon([(S(x - f * s * 0.9), S(y)), (S(x - f * s * 1.5), S(y - s * (0.5 + wag))), (S(x - f * s * 1.5), S(y + s * (0.5 - wag)))], fill=col, outline=ink, width=S(4))
    E2(d, x - s, y - s * 0.55, x + s, y + s * 0.55, fill=col, outline=ink, width=S(4))
    E2(d, x + f * s * 0.45 - s * 0.12, y - s * 0.22, x + f * s * 0.45 + s * 0.12, y + s * 0.02, fill=ink)

# ---------- lake / trees ----------
def make_lake_bg(level=0.0, snowcaps=True):
    """level 0..1 raises the water line."""
    img = vgrad(SW, SH, (120, 196, 255), (226, 244, 255)).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.polygon([(0, S(1000)), (S(160), S(760)), (S(330), S(900)), (S(520), S(700)), (S(720), S(880)), (S(900), S(740)), (SW, S(900)), (SW, S(1100)), (0, S(1100))], fill=(120, 140, 170))
    if snowcaps:
        for (px, py) in [(160, 760), (520, 700), (900, 740)]:
            d.polygon([(S(px - 60), S(py + 70)), (S(px), S(py)), (S(px + 60), S(py + 70))], fill=C["white"])
    wavy_band(d, 1060, 20, 500, 0.3, (80, 150, 90))
    wl = 1180 - 60 * level
    d.rectangle([0, S(wl), SW, SH], fill=(50, 130, 210))
    d.rectangle([0, S(wl), SW, S(wl + 18)], fill=(130, 200, 250))
    return img

def draw_pine(d, x, base, h, col=(40, 120, 70), trunk=(110, 72, 44)):
    ink = C["ink"]
    d.rectangle([S(x - h * 0.05), S(base - h * 0.2), S(x + h * 0.05), S(base)], fill=trunk, outline=ink, width=S(4))
    for i in range(3):
        top = base - h + i * h * 0.22; bw = h * (0.22 + i * 0.1)
        d.polygon([(S(x), S(top)), (S(x + bw), S(top + h * 0.42)), (S(x - bw), S(top + h * 0.42))], fill=col, outline=ink, width=S(4))

def draw_tree_rings(d, cx, cy, r, n=12, t=0.0, highlight=None):
    ink = C["ink"]
    d.ellipse([S(cx - r - 8), S(cy - r * 0.62 - 6), S(cx + r + 8), S(cy + r * 0.62 + 18)], fill=(110, 72, 44), outline=ink, width=S(6))
    d.ellipse([S(cx - r), S(cy - r * 0.62), S(cx + r), S(cy + r * 0.62)], fill=(240, 206, 150), outline=ink, width=S(5))
    rnd = random.Random(3)
    rr = r
    for i in range(n):
        rr -= r / (n + 1) * rnd.uniform(0.6, 1.4)
        if rr < 8: break
        col = (190, 140, 90)
        wd = 4
        if highlight is not None and i in highlight: col = (60, 140, 240); wd = 8
        d.ellipse([S(cx - rr), S(cy - rr * 0.62), S(cx + rr), S(cy + rr * 0.62)], outline=col, width=int(S(wd)))

def draw_drop(d, cx, cy, s, col=(80, 170, 255)):
    ink = C["ink"]
    d.polygon([(S(cx), S(cy - s * 1.4)), (S(cx + s * 0.75), S(cy - s * 0.1)), (S(cx - s * 0.75), S(cy - s * 0.1))], fill=col, outline=ink, width=S(5))
    E2(d, cx - s, cy - s * 0.9, cx + s, cy + s, fill=col, outline=ink, width=S(5))
    d.polygon([(S(cx), S(cy - s * 1.3)), (S(cx + s * 0.6), S(cy - s * 0.3)), (S(cx - s * 0.6), S(cy - s * 0.3))], fill=col)
    E2(d, cx - s * 0.5, cy - s * 0.5, cx - s * 0.15, cy - s * 0.05, fill=(220, 240, 255))

def draw_river(d, pts, col=(70, 160, 240), w=40):
    d.line([(S(x), S(y)) for x, y in pts], fill=C["ink"], width=int(S(w + 10)), joint="curve")
    d.line([(S(x), S(y)) for x, y in pts], fill=col, width=int(S(w)), joint="curve")

def draw_bar(d, x, base, w, h, col, label=None):
    ink = C["ink"]
    if h > 1:
        d.rounded_rectangle([S(x - w / 2), S(base - h), S(x + w / 2), S(base)], radius=S(12), fill=col, outline=ink, width=S(5))
    if label:
        text_center(d, x, base + 40, label, 36, fill=ink)

def draw_globe_dot(d, cx, cy, r, dots=(), t=0.0):
    draw_earth(d, cx, cy, r)
    for (dx, dy) in dots:
        pr = 18 + 6 * math.sin(t * 6)
        d.ellipse([S(cx + dx * r - pr), S(cy + dy * r - pr), S(cx + dx * r + pr), S(cy + dy * r + pr)], fill=C["pink"], outline=C["ink"], width=S(4))
