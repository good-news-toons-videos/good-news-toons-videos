"""Frame-difference motion scan: flags jumps that are NOT part of a scene crossfade.
usage: python3 tools/jank.py ep004 ep005 ...   (reads STARTS from tools/epNNN_*.py)"""
import subprocess, numpy as np, glob, os, sys, re, ast
W, H = 135, 240
for ep in sys.argv[1:]:
    f = glob.glob(f"videos/good_news_toons_{ep}_*.mp4")[0]
    src = open(glob.glob(f"tools/{ep}_*.py")[0]).read()
    starts = ast.literal_eval(re.search(r"STARTS = (\[.*?\])", src).group(1))
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", f, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
    m = np.ones((H, W), bool); m[170:198, :] = False          # ignore the caption band
    d = np.array([np.abs(a[i] - a[i - 1])[m].mean() for i in range(1, len(a))])
    out = []
    for i, v in enumerate(d):
        t = (i + 1) / 30
        if any(0 <= t - s < 0.4 for s in starts[1:]): continue
        out.append((round(float(v), 1), round(t, 2)))
    out.sort(reverse=True)
    print(ep, "median", round(float(np.median(d)), 2), "| biggest non-crossfade jumps (diff, t):", out[:8])
