"""Rodada 8: validação do AO com corte (aocorte + aotampa + FOLGA_GAB) nos planos com corte ilustrativo, em quadros
CONSECUTIVOS (perfil revisão, 540 × 960). Para cada plano:
 · detector padrão (|Δ| > 30, blocos 16×16 com ≥ 25 % dos pixels indo e voltando) no quadro todo;
 · detector SENSÍVEL (|Δ| > 12) só na região onde o AO e as faces coplanares atuam: tampas amarelas do corte + faixa de
   8 px em volta (é onde apareceram o z-fighting do topo do J3 e o granulado das tampas);
 · os piores trios de quadros, com mapa (magenta = pixel que vai e volta) salvo para inspeção.
Uso: python3 validar_ao_cortes.py <pasta_quadros> <saida.json> [planos...]"""
import os, sys, json
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
base, saida = sys.argv[1], sys.argv[2]
PLANOS = sys.argv[3:] or ['C2', 'C3', 'C4', 'D1', 'D2', 'D3', 'D5', 'E1', 'E2', 'E3', 'E4', 'G1', 'G2', 'G3', 'H1', 'H2', 'J3']
MAPAS = os.path.join(os.path.dirname(os.path.abspath(saida)), 'mapas_ao'); os.makedirs(MAPAS, exist_ok=True)
def tampas(rgb):
    a = np.asarray(rgb.convert('HSV'), np.float32); h, s, v = a[..., 0] * 360 / 255, a[..., 1] / 255, a[..., 2] / 255
    return (h > 30) & (h < 60) & (s > 0.40) & (v > 0.45)
def blocos(m):
    H, W = m.shape; h, w = H // 16 * 16, W // 16 * 16
    return int((m[:h, :w].reshape(h // 16, 16, w // 16, 16).mean((1, 3)) >= 0.25).sum())
res = {}
for p in PLANOS:
    d = os.path.join(base, p)
    if not os.path.isdir(d): continue
    fs = sorted(f for f in os.listdir(d) if f.endswith('.jpg') and f.startswith('q'))
    ims = [Image.open(os.path.join(d, f)).convert('RGB') for f in fs]
    L = [np.asarray(im.convert('L'), np.float32) for im in ims]
    pad_tot, sens_tot, sens_reg_pix, piores = 0, 0, 0, []
    for k in range(1, len(fs) - 1):
        a, b, c = L[k - 1], L[k], L[k + 1]; d1, d2 = b - a, c - b; opos = np.sign(d1) != np.sign(d2)
        alt30 = (np.abs(d1) > 30) & (np.abs(d2) > 30) & opos; alt12 = (np.abs(d1) > 12) & (np.abs(d2) > 12) & opos
        reg = binary_dilation(tampas(ims[k]), iterations=8)
        b30 = blocos(alt30); s = alt12 & reg; b12 = blocos(s)
        pad_tot += int(b30 > 0); sens_tot += int(b12 > 0); sens_reg_pix += int(s.sum())
        piores.append((b12, int(s.sum()), fs[k], b30))
        if b12 > 0:
            m = np.asarray(ims[k]).copy(); m[s] = [255, 0, 255]; Image.fromarray(m).save(os.path.join(MAPAS, f'{p}_{fs[k][:-4]}.jpg'), quality=85)
    piores.sort(reverse=True)
    res[p] = dict(quadros=len(fs), trios=len(fs) - 2, trios_com_blocos_padrao=pad_tot, trios_com_blocos_sensivel_nos_cortes=sens_tot,
                  pixels_sensivel_nos_cortes=sens_reg_pix, area_tampas_pct=round(100 * float(np.mean([tampas(im).mean() for im in ims[::10]])), 1),
                  piores=[dict(quadro=f, blocos_sensivel=b, pixels_sensivel=px, blocos_padrao=b3) for b, px, f, b3 in piores[:4]])
    print(p, res[p]['trios'], 'padrão', pad_tot, '| sensível nos cortes', sens_tot, sens_reg_pix, res[p]['piores'][0], flush=True)
json.dump(res, open(saida, 'w'), ensure_ascii=False, indent=1)
