"""YouTube banner 2560x1440. Safe area for all devices: centered 1546x423 (x 507-2053, y 508-931)."""
import math
from PIL import Image, ImageDraw
import toon
from toon import *

BW, BH = 2560, 1440
img = vgrad(BW * SS, BH * SS, (120, 200, 255), (214, 242, 255)).convert("RGBA")
d = ImageDraw.Draw(img)

# soft sunburst behind the centre
for i in range(24):
    a = i * math.pi / 12
    d.polygon([(S(1280), S(720)), (S(1280 + 2400 * math.cos(a)), S(720 + 2400 * math.sin(a))),
               (S(1280 + 2400 * math.cos(a + 0.12)), S(720 + 2400 * math.sin(a + 0.12)))], fill=(170, 222, 255))
d.ellipse([S(2150), S(120), S(2410), S(380)], fill=C["sun"])
for x, y, s in [(250, 200, 1.3), (1700, 160, 1.0), (900, 260, 0.8)]:
    for dx, dy, r in [(0, 0, 60), (60, -25, 70), (130, 0, 55), (65, 20, 60)]:
        rr = r * s
        d.ellipse([S(x + dx * s - rr), S(y + dy * s - rr), S(x + dx * s + rr), S(y + dy * s + rr)], fill=(255, 255, 255))

# hills
for col, base, amp, ph, per in [(C["hill1"], 1080, 110, 0.4, 900), (C["hill2"], 1180, 80, 2.0, 700)]:
    pts = [(0, S(BH))]
    for x in range(0, BW + 20, 20):
        pts.append((S(x), S(base - amp * (0.5 + 0.5 * math.sin(x / per * 2 * math.pi + ph)))))
    pts.append((S(BW), S(BH)))
    d.polygon(pts, fill=col)
d.rectangle([0, S(1260), S(BW), S(BH)], fill=C["hill3"])

# animals on the hills (outside the text, visible on desktop/TV)
for kind, x, f, sc in [("deer", 230, 1, 2.0), ("fox", 600, 1, 2.3), ("coyote", 1280, 1, 2.3), ("bobcat", 1990, -1, 2.1), ("lion", 2330, -1, 1.9)]:
    draw_animal(d, x, 1300, kind, phase=0.9, scale=sc, facing=f)

# centre: coyote mascot + title + tagline, all inside the safe area
sticker(img, 1280, 650, "GOOD NEWS TOONS", 128, C["yellow"], rot=-2)
sticker(img, 1280, 835, "Real good news, explained in little cartoons", 54, C["white"], pad=(36, 20))
sticker(img, 1820, 545, "NEW DAILY!", 44, C["pink"], fg=C["white"], rot=8, pad=(28, 16))

img.convert("RGB").resize((BW, BH), Image.LANCZOS).save("../out/yt_banner_good_news_toons.png")

# preview with the safe areas drawn on
p = Image.open("../out/yt_banner_good_news_toons.png").copy()
pd = ImageDraw.Draw(p)
pd.rectangle([507, 508, 2053, 931], outline=(255, 0, 0), width=6)      # all devices
pd.rectangle([0, 509, 2560, 931], outline=(0, 160, 255), width=4)     # desktop max
p.resize((1280, 720)).save("../out/banner_check.png")
