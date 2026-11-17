"""Folha de comparação v1 (rejeitada) × v2 (proposta) dos quadros equivalentes.
Uso: python3 etapa_b/comparar.py  → etapa_b/comparacao_v1_v2.jpg e etapa_b/comparacao_quadroN.jpg"""
import os
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
F = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TIT = ['1 · Bloco de aço afundando', '2 · Estaleiro / casco em construção', '3 · Corte interno do navio',
       '4 · Empuxo visto debaixo d\'água', '5 · Guindaste carregando contêineres']
AZUL, BRANCO, AMARELO = (32, 43, 87), (246, 244, 236), (243, 181, 68)


def par(n, w=540):
    h = int(w * 16 / 9)
    v1 = Image.open(os.path.join(AQUI, 'v1', f'v1_quadro{n}.jpg')).convert('RGB').resize((w, h), Image.LANCZOS)
    p2 = os.path.join(AQUI, 'quadros', f'quadro{n}.png')
    v2 = Image.open(p2).convert('RGB').resize((w, h), Image.LANCZOS)
    cab = 86; c = Image.new('RGB', (2 * w + 30, h + cab + 20), AZUL)
    d = ImageDraw.Draw(c); f1 = ImageFont.truetype(F, 30); f2 = ImageFont.truetype(F, 22)
    d.text((14, 12), TIT[n - 1], font=f1, fill=BRANCO)
    d.text((14, 52), 'v1 rejeitada (Three.js)', font=f2, fill=(200, 200, 205))
    d.text((w + 30 + 4, 52), 'v2 proposta (Blender · Cycles)', font=f2, fill=AMARELO)
    c.paste(v1, (10, cab)); c.paste(v2, (w + 20, cab))
    return c


if __name__ == '__main__':
    pares = []
    for n in range(1, 6):
        if not os.path.exists(os.path.join(AQUI, 'quadros', f'quadro{n}.png')): continue
        p = par(n); p.save(os.path.join(AQUI, f'comparacao_quadro{n}.jpg'), quality=90); pares.append(p)
    if pares:
        W = pares[0].width; H = sum(p.height for p in pares)
        folha = Image.new('RGB', (W, H), AZUL); y = 0
        for p in pares: folha.paste(p, (0, y)); y += p.height
        folha.save(os.path.join(AQUI, 'comparacao_v1_v2.jpg'), quality=88)
        print('ok', len(pares), folha.size)
