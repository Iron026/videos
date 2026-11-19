"""Gráfico do loudness momentâneo (400 ms) de cada stem ao longo do episódio, com as sequências marcadas."""
import os, sys, numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A)
from som_ep01 import lufs, DUR
E = os.path.join(A, '..', 'stems'); F = os.path.join(A, '..', '..', 'fontes')
f1 = ImageFont.truetype(os.path.join(F, 'Montserrat-800.ttf'), 26); f2 = ImageFont.truetype(os.path.join(F, 'Montserrat-700.ttf'), 18)
CORES = {'narracao': (246, 244, 236), 'efeitos': (243, 181, 68), 'ambiencias': (90, 190, 220), 'musica': (190, 120, 230)}
NOMES = {'narracao': 'Narração', 'efeitos': 'Efeitos', 'ambiencias': 'Ambiências', 'musica': 'Música'}
SEQ = [(0, 4.4, 'Bloco'), (4.4, 15.1, 'Navio'), (15.1, 30.3, 'Estaleiro · solda'), (30.3, 41.55, 'Corte'), (41.55, 48, 'Dique'), (48, 74.85, 'Pressão e empuxo'),
       (74.85, 83.85, 'Bloco'), (83.85, 94.55, 'Experimento'), (94.55, 123.65, 'Carregamento'), (123.65, 134, 'Marcas'), (134, 154.6, 'Avaria'), (154.6, DUR, 'Conclusão')]
W, H, x0, x1, y0, y1 = 2400, 760, 90, 2370, 120, 680
im = Image.new('RGB', (W, H), (32, 43, 87)); d = ImageDraw.Draw(im)
X = lambda t: x0 + (x1 - x0) * t / DUR; Y = lambda l: y1 - (y1 - y0) * (np.clip(l, -60, -5) + 60) / 55
for i, (a, b, n) in enumerate(SEQ):
    d.rectangle([X(a), y0, X(b), y1], fill=(38, 51, 101) if i % 2 else (32, 43, 87)); d.text((X(a) + 4, y0 - 26), n, font=f2, fill=(200, 205, 220))
for l in (-50, -40, -30, -20, -10):
    d.line([x0, Y(l), x1, Y(l)], fill=(70, 82, 130)); d.text((10, Y(l) - 10), f'{l} LUFS', font=f2, fill=(170, 175, 200))
for t in range(0, int(DUR) + 1, 10): d.text((X(t) - 10, y1 + 8), f'{t}s', font=f2, fill=(170, 175, 200))
for k in ('musica', 'ambiencias', 'efeitos', 'narracao'):
    x, sr = sf.read(os.path.join(E, f'ep01_{k}.wav')); l = lufs(x, curto=True); t = np.arange(len(l)) * 0.1 + 0.2
    pts = [(X(a), Y(b)) for a, b in zip(t[::3], l[::3])]; d.line(pts, fill=CORES[k], width=3 if k != 'narracao' else 2)
d.text((x0, 20), 'Ep. 01 · loudness momentâneo por stem (após ducking e masterização)', font=f1, fill=(246, 244, 236))
xl = 1300
for k in ('narracao', 'efeitos', 'ambiencias', 'musica'):
    d.rectangle([xl, 30, xl + 26, 46], fill=CORES[k]); d.text((xl + 34, 24), NOMES[k], font=f2, fill=(246, 244, 236)); xl += 190
im.save(os.path.join(A, '..', 'som_loudness_ep01.png')); print('ok')
