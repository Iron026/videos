"""Rodada 7: comparativo CONTROLADO do AO (mesmos quadros, câmeras e luz) — variantes 'atual', 'corte' (AO com corte),
'tampa' (AO com corte + tampas sem AO) e 'plana' (G-buffer com tampas planas no plano de corte). Regiões definidas no quadro
ATUAL e usadas em todas: tampas (amarelo do corte), faixa de 8 px vizinha às tampas, resto. Medidas (luma 0–255):
 · granulado = média de |img − gauss(img, σ 1,2)| (alta frequência) por região;
 · sombreamento = brilho médio da região − o do atual (negativo = mais oclusão);
 · estabilidade = detector absoluto nos 12 quadros seguidos (blocos 16×16 que vão e voltam).
Uso: python3 medir_ao.py <pasta_seq>  → relatorios/comparativo_ao.json"""
import os, sys, json
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import binary_dilation
base = sys.argv[1]; VARS = [v for v in ['atual', 'corte', 'tampa', 'plana', 'tampa_s', 'plana_m'] if os.path.isdir(os.path.join(base, v))]; res = {}
def L(f): return np.asarray(Image.open(f).convert('L'), np.float32)
def hf(f): im = Image.open(f).convert('L'); return np.abs(np.asarray(im, np.float32) - np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)), np.float32))
def mascara_tampa(f):
    a = np.asarray(Image.open(f).convert('HSV'), np.float32); h, s, v = a[..., 0] * 360 / 255, a[..., 1] / 255, a[..., 2] / 255
    return (h > 30) & (h < 60) & (s > 0.40) & (v > 0.45)
def piscantes(fs):
    n = 0
    for k in range(1, len(fs) - 1):
        a, b, c = L(fs[k - 1]), L(fs[k]), L(fs[k + 1]); d1, d2 = b - a, c - b
        alt = (np.abs(d1) > 30) & (np.abs(d2) > 30) & (np.sign(d1) != np.sign(d2)); H, W = alt.shape; h, w = H // 16 * 16, W // 16 * 16
        n += int((alt[:h, :w].reshape(h // 16, 16, w // 16, 16).mean((1, 3)) >= 0.25).sum())
    return n
for p in sorted(os.listdir(os.path.join(base, 'atual'))):
    VV = [v for v in VARS if os.path.isdir(os.path.join(base, v, p))]
    fs = {v: sorted(os.path.join(base, v, p, f) for f in os.listdir(os.path.join(base, v, p)) if f.endswith('.jpg')) for v in VV}
    mt = [mascara_tampa(f) for f in fs['atual']]; mb = [binary_dilation(m, iterations=8) & ~m for m in mt]; mr = [~(binary_dilation(m, iterations=8)) for m in mt]
    R = res[p] = {}
    for v in VV:
        g = {'tampas': [], 'faixa': [], 'resto': []}; s = {'tampas': [], 'faixa': [], 'resto': []}
        for k, f in enumerate(fs[v]):
            H_ = hf(f); im = L(f); im0 = L(fs['atual'][k])
            for nome, m in (('tampas', mt[k]), ('faixa', mb[k]), ('resto', mr[k])):
                if m.sum(): g[nome].append(float(H_[m].mean())); s[nome].append(float((im - im0)[m].mean()))
        R[v] = dict(granulado={k_: round(float(np.mean(x)), 2) for k_, x in g.items() if x}, sombreamento={k_: round(float(np.mean(x)), 2) for k_, x in s.items() if x},
                    blocos_piscantes_12q=piscantes(fs[v]), quadros=len(fs[v]))
    R['area_tampas_pct'] = round(float(np.mean([m.mean() for m in mt])) * 100, 1)
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios', 'comparativo_ao.json'), 'w'), ensure_ascii=False, indent=1)
for p, R in res.items():
    print(p, 'tampas', R['area_tampas_pct'], '%')
    for v in [x for x in VARS if x in R]: print('  ', v.ljust(8), 'granulado', R[v]['granulado'], '| sombra', R[v]['sombreamento'], '| piscantes', R[v]['blocos_piscantes_12q'])
