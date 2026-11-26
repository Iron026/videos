"""Folha de inspeção dos manômetros: quadros compostos em 1080 (fundo da prévia ampliado), versão atual × proposta.
Uso: python3 ver_manometros.py <saida.jpg> PLANO:t [PLANO:t ...]"""
import os, sys
saida, specs = sys.argv[1], sys.argv[2:]; sys.argv = [sys.argv[0], 'final']
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A)
import montar_ep02 as M
from PIL import Image, ImageDraw, ImageFont
M.pasta = lambda pid: os.path.join(A, 'quadros_animatic', pid)
f = ImageFont.truetype(os.path.join(A, '..', 'fontes', 'Montserrat-800.ttf'), 30); col = []
for sp in specs:
    pid, t = sp.split(':'); g = float(t)
    for modo in (False, True):
        M.MAN_LEG = modo; im = M.compor(g).resize((540, 960), Image.LANCZOS); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 540, 40], fill=(0, 0, 0)); d.text((8, 4), f"{pid} {g:.2f}s · {'nova' if modo else 'atual'}", font=f, fill=(255, 230, 0)); col.append(im)
F = Image.new('RGB', (len(col) * 544, 960), (255, 0, 0))
for i, im in enumerate(col): F.paste(im, (i * 544, 0))
F.save(saida, quality=88); print(saida, F.size)
