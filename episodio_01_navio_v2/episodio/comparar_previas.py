"""Comparativo visual entre prévias.  Uso: python3 episodio/comparar_previas.py [v1_v2|v2_v3]"""
import os, subprocess, io, sys
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
MODO = sys.argv[1] if len(sys.argv) > 1 else 'v1_v2'
if MODO == 'v2_v3':   # trechos mais estáticos da v2 (mesmos instantes na v3)
    PONTOS = [('Gigante: escala', 5.5), ('Gigante: carga', 9.5), ('Gigante: linha d\'água', 12.5), ('Estaleiro: carro', 18.0),
              ('Solda', 24.6), ('Proa', 27.8), ('Compartimentos', 36.5), ('Porão', 38.3), ('Dique: água sobe', 43.8),
              ('Dique: flutua', 46.6), ('Mergulho', 49.4), ('Pressão no casco', 52.2), ('Componentes verticais', 59.0),
              ('Volume se enche', 64.4), ('Empuxo = peso da água', 68.5), ('Bloco: leito', 82.6), ('Experimento: soltos', 86.6),
              ('1º contêiner: pouso', 101.2), ('Convés enchendo', 111.0), ('Cota do calado', 120.0), ('Avaria: exterior', 136.2),
              ('Avaria: interior', 138.2), ('Nível subindo', 140.6), ('Recap: bloco afunda', 157.0)]
    VA, VB, TITULO, SAIDA = 'ep01_previa_v2.mp4', 'ep01_previa.mp4', 'Ep. 01 · prévia v2 (acima) × prévia v3 (abaixo): trechos mais estáticos da v2', 'comparativo_previa_v2_v3.jpg'
else:
    VA, VB, TITULO, SAIDA = 'ep01_previa_v1.mp4', 'ep01_previa.mp4', 'Ep. 01 · prévia v1 (acima) × prévia v2 (abaixo) — trechos corrigidos', 'comparativo_previa_v1_v2.jpg'


def quadro(v, t):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', os.path.join(A, v), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert('RGB').resize((W, H))


cols = 12 if MODO == 'v2_v3' else 9; linhas = (len(PONTOS) + cols - 1) // cols
img = Image.new('RGB', (40 + cols * (W + 10), 90 + linhas * (2 * H + 70)), AZUL); d = ImageDraw.Draw(img)
d.text((40, 28), TITULO, font=ft, fill=CREME)
for i, (rot, t) in enumerate(PONTOS):
    x = 40 + (i % cols) * (W + 10); y = 90 + (i // cols) * (2 * H + 70)
    d.text((x, y), f'{rot}', font=fs, fill=AMAR); d.text((x, y + 22), f'{t:.1f} s', font=fs, fill=CINZA)
    img.paste(quadro(VA, t), (x, y + 46)); img.paste(quadro(VB, t), (x, y + 46 + H + 4))
img.save(os.path.join(A, SAIDA), quality=86); print('ok', img.size)
