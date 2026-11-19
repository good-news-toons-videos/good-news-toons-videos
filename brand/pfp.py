import math
from PIL import Image, ImageDraw, ImageFont

N = 2160  # draw at 2x, save 1080
img = Image.new("RGB", (N, N), (255, 214, 90))
d = ImageDraw.Draw(img)
INK = (34, 34, 52)
c = N / 2

# sunburst
for i in range(20):
    a = i * math.pi / 10
    d.polygon([(c, c), (c + 2000 * math.cos(a), c + 2000 * math.sin(a)),
               (c + 2000 * math.cos(a + 0.16), c + 2000 * math.sin(a + 0.16))], fill=(255, 236, 150))

def ell(cx, cy, rx, ry, fill, w=22):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=INK, width=w)

FUR, LIGHT, INNER = (176, 150, 120), (240, 226, 204), (255, 160, 170)
hx, hy = c, c + 60
# ears
for s in (-1, 1):
    d.polygon([(hx + s * 150, hy - 330), (hx + s * 470, hy - 830), (hx + s * 520, hy - 210)], fill=FUR, outline=INK, width=22)
    d.polygon([(hx + s * 230, hy - 340), (hx + s * 450, hy - 690), (hx + s * 470, hy - 280)], fill=INNER)
# head
ell(hx, hy, 560, 500, FUR)
# cheek fluff
for s in (-1, 1):
    d.polygon([(hx + s * 420, hy + 80), (hx + s * 640, hy + 230), (hx + s * 400, hy + 330)], fill=FUR, outline=INK, width=22)
ell(hx, hy + 120, 560, 380, FUR, w=0)
d.arc([hx - 560, hy - 500, hx + 560, hy + 500], 0, 180, fill=INK, width=22)
# muzzle
ell(hx, hy + 210, 300, 230, LIGHT)
# eyes
for s in (-1, 1):
    ex, ey = hx + s * 220, hy - 70
    ell(ex, ey, 70, 90, INK, w=0)
    d.ellipse([ex - 30 + s * 10, ey - 55, ex + 15 + s * 10, ey - 10], fill=(255, 255, 255))
    ell(hx + s * 330, hy + 90, 70, 40, (255, 150, 150), w=0)  # blush
# nose + smile
d.rounded_rectangle([hx - 80, hy + 90, hx + 80, hy + 180], radius=45, fill=INK)
d.line([(hx, hy + 180), (hx, hy + 250)], fill=INK, width=20)
d.arc([hx - 170, hy + 130, hx, hy + 330], 20, 160, fill=INK, width=20)
d.arc([hx, hy + 130, hx + 170, hy + 330], 20, 160, fill=INK, width=20)
# tongue
d.chord([hx - 70, hy + 250, hx + 70, hy + 380], 0, 180, fill=(255, 110, 130), outline=INK, width=14)

# "GOOD NEWS" banner, inside the circle-safe zone
f = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 230)
txt = "GOOD NEWS"
bb = d.textbbox((0, 0), txt, font=f)
tw, th = bb[2] - bb[0], bb[3] - bb[1]
by = 1700
pad = 70
d.rounded_rectangle([c - tw / 2 - pad + 24, by - th / 2 - 40 + 30, c + tw / 2 + pad + 24, by + th / 2 + 40 + 30], radius=60, fill=INK)
d.rounded_rectangle([c - tw / 2 - pad, by - th / 2 - 40, c + tw / 2 + pad, by + th / 2 + 40], radius=60, fill=(255, 110, 150), outline=INK, width=22)
d.text((c - tw / 2 - bb[0], by - th / 2 - bb[1]), txt, font=f, fill=(255, 255, 255))

out = img.resize((1080, 1080), Image.LANCZOS)
out.save("../out/pfp_good_news_toons.png")
# circular preview, the way the apps crop it
m = Image.new("L", (1080, 1080), 0); ImageDraw.Draw(m).ellipse([0, 0, 1080, 1080], fill=255)
prev = Image.new("RGB", (1080, 1080), (255, 255, 255)); prev.paste(out, (0, 0), m)
prev.resize((360, 360), Image.LANCZOS).save("../out/pfp_preview.png")
