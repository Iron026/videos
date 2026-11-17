"""Comparativo visual prévia v1 × v2 nos trechos corrigidos → episodio/comparativo_previa_v1_v2.jpg
Uso: python3 episodio/comparar_previas.py"""
import os, subprocess, io
from PIL import Image, ImageDraw, ImageFont

A = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(A, '..', 'fontes')
ft = ImageFont.truetype(os.path.join(F, 'Montserrat-800.ttf'), 30); fs = ImageFont.truetype(os.path.join(F, 'Montserrat-700.ttf'), 19)
AZUL, CREME, AMAR, CINZA = (32, 43, 87), (246, 244, 236), (243, 181, 68), (160, 166, 190)
PONTOS = [('Outro navio', 8.0), ('Estaleiro', 26.5), ('Ar no porão', 40.6), ('Entrada na água', 43.8),
          ('…e para (flutua)', 47.0), ('Pressão', 55.0), ('Empuxo', 62.5), ('Arquimedes', 72.5), ('Bloco 1,6 m', 79.0),
          ('Bloco × casco', 86.5), ('Água deslocada', 92.5), ('"E mais outro"', 104.0), ('Linha d\'água', 106.0),
          ('Marcas de calado', 126.8), ('Linha de carga', 132.0), ('Avaria', 140.0), ('Calado e trim', 146.6),
          ('Divisórias', 152.5)]
W, H = 180, 320


def quadro(v, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', os.path.join(A, v), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert('RGB').resize((W, H))


cols = 9; linhas = (len(PONTOS) + cols - 1) // cols
img = Image.new('RGB', (40 + cols * (W + 10), 90 + linhas * (2 * H + 70)), AZUL); d = ImageDraw.Draw(img)
d.text((40, 28), 'Ep. 01 · prévia v1 (acima) × prévia v2 (abaixo) — trechos corrigidos', font=ft, fill=CREME)
for i, (rot, t) in enumerate(PONTOS):
    x = 40 + (i % cols) * (W + 10); y = 90 + (i // cols) * (2 * H + 70)
    d.text((x, y), f'{rot}', font=fs, fill=AMAR); d.text((x, y + 22), f'{t:.1f} s', font=fs, fill=CINZA)
    img.paste(quadro('ep01_previa_v1.mp4', t), (x, y + 46)); img.paste(quadro('ep01_previa.mp4', t), (x, y + 46 + H + 4))
img.save(os.path.join(A, 'comparativo_previa_v1_v2.jpg'), quality=86); print('ok', img.size)
