"""timeline.json의 비트마다 지정 비율 지점 프레임을 뽑아 접촉 시트로 만든다. sheet.py [frac] [from] [to]"""
import json, subprocess, sys
from PIL import Image, ImageDraw
frac = float(sys.argv[1]) if len(sys.argv) > 1 else 0.75
a, b = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 999)
tl = json.load(open("out/timeline.json", encoding="utf-8"))[a:b]
tw, th = 640, 360
cols = 3
sheet = Image.new("RGB", (tw * cols, th * ((len(tl) + cols - 1) // cols)), "white")
for i, e in enumerate(tl):
    t = e["start"] + e["dur"] * frac
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", "out/doseverdict_demo.mp4", "-frames:v", "1", "-vf", f"scale={tw}:{th}", "out/_f.png"], check=True)
    im = Image.open("out/_f.png").convert("RGB")
    ImageDraw.Draw(im).text((6, 6), f"{e['beat']} {t:.1f}s", fill=(255, 0, 0))
    sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
sheet.save("out/sheet.png")
print(len(tl))
