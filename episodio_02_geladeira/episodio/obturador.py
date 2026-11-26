"""Rodada 7: desfoque de movimento FISICAMENTE coerente (obturador de 180°, como uma câmera real): o quadro k é a média, em
luz LINEAR, dos sub-quadros 8k−2 … 8k+2 de uma exportação com 8 sub-quadros por quadro (cenas/<plano>_sub8, mesma câmera,
mesmo pulso e mesmo corte: o sub-quadro 8k é idêntico ao quadro k aprovado). Só suaviza o que se move durante o meio
intervalo de exposição. Uso: python3 obturador.py <pasta_subquadros> <saida> <k0> <k1> [180|270]"""
import os, sys
import numpy as np
from PIL import Image
src, out, k0, k1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); os.makedirs(out, exist_ok=True)
GRAUS = int(sys.argv[5]) if len(sys.argv) > 5 else 180   # 180° (padrão de cinema) ou 270°: meia-largura = graus/360 × 4 sub-quadros
M = {180: 2, 270: 3}[GRAUS]
lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
for k in range(k0, k1 + 1):
    acc = None
    for j in range(8 * k - M, 8 * k + M + 1):
        a = lin(np.asarray(Image.open(os.path.join(src, f'q{j:04d}.jpg')).convert('RGB'), np.float32) / 255.0)
        acc = a if acc is None else acc + a
    Image.fromarray(np.clip(srgb(acc / (2 * M + 1)) * 255 + 0.5, 0, 255).astype(np.uint8)).save(os.path.join(out, f'q{k:04d}.jpg'), quality=95)
print('ok', k1 - k0 + 1, 'quadros')
