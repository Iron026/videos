"""Gera folhas de contato a partir de um vídeo: python3 folha_contato.py video.mp4 inicio fim passo saida.jpg [colunas]"""
import sys, subprocess, io
from PIL import Image, ImageDraw
v, a, b, p, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 6
ts = []; t = a
while t <= b + 1e-6: ts.append(round(t, 2)); t += p
ims = []
for t in ts:
    d = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(t), '-i', v, '-frames:v', '1', '-f', 'image2pipe', '-c:v', 'png', '-'], capture_output=True).stdout
    im = Image.open(io.BytesIO(d)).convert('RGB'); im.thumbnail((270, 480))
    ImageDraw.Draw(im).text((6, 4), f'{t:.1f}s', fill=(255, 255, 0)); ims.append(im)
w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (w * cols, h * rows))
for i, im in enumerate(ims): S.paste(im, ((i % cols) * w, (i // cols) * h))
S.save(out, quality=85)
