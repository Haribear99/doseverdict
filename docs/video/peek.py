"""peek.py shot y0 y1 [x0 x1] -> out/peek.png (CSS px 좌표로 잘라 보기)"""
import sys
from PIL import Image
im = Image.open(f"shots/{sys.argv[1]}.png"); k = im.size[0] / 1920
y0, y1 = int(sys.argv[2]), int(sys.argv[3])
x0, x1 = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 1920)
c = im.crop((int(x0*k), int(y0*k), int(x1*k), int(y1*k)))
c.thumbnail((1600, 1600)); c.save("out/peek.png")
