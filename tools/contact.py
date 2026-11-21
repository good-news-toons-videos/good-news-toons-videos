"""Make a contact sheet of stills: python3 tools/contact.py out/ep004 -> out/ep004/sheet.jpg"""
import sys, glob
from PIL import Image
d = sys.argv[1]
fs = sorted(glob.glob(f"{d}/still_*.jpg"))
tw, th = 270, 480
cols = 5
rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * th), "white")
for i, f in enumerate(fs):
    sheet.paste(Image.open(f).resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
sheet.save(f"{d}/sheet.jpg", quality=85)
