"""Comparativo v1 × r2: linhas do tempo por plano e quadros dos mesmos momentos narrativos → comparativo_r2.jpg
Uso: python3 animatic/comparar_r2.py
"""
import os, subprocess, io
from PIL import Image, ImageDraw, ImageFont

A = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(A, '..', 'fontes')
f_t = ImageFont.truetype(os.path.join(F, 'Montserrat-800.ttf'), 34); f_s = ImageFont.truetype(os.path.join(F, 'Montserrat-700.ttf'), 22)
AZUL, CREME, AMAR, CINZA = (32, 43, 87), (246, 244, 236), (243, 181, 68), (150, 156, 180)
CORES = {'Cais': (74, 140, 190), 'Aérea': (243, 181, 68), 'Içamento': (205, 110, 70), 'Encaixe': (160, 80, 60), 'Assinatura': (120, 110, 200)}
V1 = [('Cais', 0, 5.6), ('Aérea', 5.6, 11.5), ('Encaixe', 11.5, 14.8), ('Assinatura', 14.8, 19.5)]
R2 = [('Cais', 0, 4.8), ('Aérea', 4.8, 7.0), ('Içamento', 7.0, 10.25), ('Encaixe', 10.25, 13.75), ('Assinatura', 13.75, 16.85)]
MOMENTOS = [('Bloco entra na água', 3.23, 2.70), ('Bloco no fundo', 4.60, 4.55), ('Estaleiro', 8.00, 6.20),
            ('Chapa descendo', 12.00, 8.60), ('Encaixe', 14.45, 13.20), ('Assinatura', 18.00, 15.80)]


def quadro(video, t, w=300):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', os.path.join(A, video), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    im = Image.open(io.BytesIO(raw)).convert('RGB'); return im.resize((w, int(w * im.height / im.width)))


W = 40 + len(MOMENTOS) * 320; img = Image.new('RGB', (W, 1720), AZUL); d = ImageDraw.Draw(img)
d.text((40, 30), 'Animatic Ep. 01 · v1 × r2', font=f_t, fill=CREME)
esc = (W - 200) / 19.5
for k, (nome, pl, tot) in enumerate((('v1', V1, 19.5), ('r2', R2, 16.85))):
    y = 100 + k * 70; d.text((40, y + 8), nome, font=f_t, fill=AMAR if nome == 'r2' else CINZA)
    for rot, a, b in pl:
        x0, x1 = 120 + a * esc, 120 + b * esc; d.rounded_rectangle((x0 + 2, y, x1 - 2, y + 48), 8, fill=CORES[rot])
        d.text(((x0 + x1) / 2, y + 24), f'{rot} {b - a:.1f}s', font=f_s, fill=(16, 22, 46), anchor='mm')
    d.text((120 + tot * esc + 10, y + 12), f'{tot:.2f} s', font=f_s, fill=CREME)
for i, (rot, t1, t2) in enumerate(MOMENTOS):
    x = 40 + i * 320; d.text((x, 260), rot, font=f_s, fill=CREME)
    img.paste(quadro('animatic_ep01.mp4', t1), (x, 300)); d.text((x + 6, 306), f'v1 · {t1:.2f} s', font=f_s, fill=CINZA, stroke_width=3, stroke_fill=(0, 0, 0))
    img.paste(quadro('animatic_ep01_r2.mp4', t2), (x, 300 + 540)); d.text((x + 6, 846), f'r2 · {t2:.2f} s', font=f_s, fill=AMAR, stroke_width=3, stroke_fill=(0, 0, 0))
img = img.crop((0, 0, W, 300 + 540 * 2 + 20)); img.save(os.path.join(A, 'comparativo_r2.jpg'), quality=88); print('ok', img.size)
