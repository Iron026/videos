"""Detector ABSOLUTO de cintilação (mesmo critério de detectar_cintilacao.py: pixels que "vão e voltam", |Δ| > 30 com sinais
opostos em quadros seguidos; bloco 16×16 piscante se ≥ 25 % alternam) aplicado à SEQUÊNCIA DE QUADROS EXISTENTE de cada plano
(o perfil econômico renderiza 1 a cada 2 quadros). Uso: python3 detectar_cintilacao_todos.py <pasta_quadros> <largura> → JSON por plano"""
import os, sys, json, numpy as np
from PIL import Image
d = sys.argv[1]; Wd = int(sys.argv[2]); out = {}
for seg in sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))):
    fs = sorted(f for f in os.listdir(os.path.join(d, seg)) if f.endswith('.jpg'))
    L = lambda f: np.asarray(Image.open(os.path.join(d, seg, f)).convert('L').resize((Wd, Wd * 16 // 9))).astype(np.float32)
    res = []; a, b = L(fs[0]), L(fs[1])
    for k in range(1, len(fs) - 1):
        c = L(fs[k + 1]); d1, d2 = b - a, c - b
        alt = (np.abs(d1) > 30) & (np.abs(d2) > 30) & (np.sign(d1) != np.sign(d2))
        H, W = alt.shape; h, w = H // 16 * 16, W // 16 * 16
        bl = int((alt[:h, :w].reshape(h // 16, 16, w // 16, 16).mean((1, 3)) >= 0.25).sum()); res.append((bl, fs[k], int(alt.sum()))); a, b = b, c
    res.sort(reverse=True)
    out[seg] = dict(quadros=len(res), com_blocos=sum(1 for r in res if r[0] > 0), piores=[dict(quadro=q, blocos=bl, pixels=px) for bl, q, px in res[:3]])
    print(seg, out[seg]['com_blocos'], out[seg]['piores'][0], flush=True)
json.dump(out, open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios', 'cintilacao_v5.json'), 'w'), ensure_ascii=False, indent=1)
