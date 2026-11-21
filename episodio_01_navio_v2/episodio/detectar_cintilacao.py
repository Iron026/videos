"""Detector ABSOLUTO de cintilação tipo z-fighting (não depende de uma referência aprovada): conta, em cada quadro, pixels que
"vão e voltam" (q−1 → q → q+1 com variações grandes e de sinais opostos, |d| > 30 nas duas), agrupados em blocos de 16 × 16:
um bloco é "piscante" se ≥ 25 % dos pixels alternam. Movimento normal de câmera desloca bordas (não alterna); z-fighting alterna.
Uso: python3 episodio/detectar_cintilacao.py <pasta_quadros> <seg> [q0 q1] [largura]   → imprime os quadros com mais blocos piscantes"""
import os, sys, json, numpy as np
from PIL import Image
d, seg = sys.argv[1], sys.argv[2]; fs = sorted(int(f[1:5]) for f in os.listdir(os.path.join(d, seg)) if f.endswith('.jpg'))
q0, q1 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (fs[0], fs[-1]); Wd = int(sys.argv[5]) if len(sys.argv) > 5 else 540
L = lambda q: np.asarray(Image.open(os.path.join(d, seg, f'q{q:04d}.jpg')).convert('L').resize((Wd, Wd * 16 // 9))).astype(np.float32)
res = []; a, b = L(q0), L(q0 + 1)
for q in range(q0 + 1, q1):
    c = L(q + 1); d1, d2 = b - a, c - b
    alt = (np.abs(d1) > 30) & (np.abs(d2) > 30) & (np.sign(d1) != np.sign(d2))
    H, W = alt.shape; h, w = H // 16 * 16, W // 16 * 16
    blocos = int((alt[:h, :w].reshape(h // 16, 16, w // 16, 16).mean((1, 3)) >= 0.25).sum())
    res.append((blocos, q, int(alt.sum()))); a, b = b, c
res.sort(reverse=True)
out = dict(segmento=seg, quadros=len(res), quadros_com_blocos_piscantes=sum(1 for r in res if r[0] > 0), piores=[dict(quadro=q, blocos=bl, pixels=px) for bl, q, px in res[:8]])
print(json.dumps(out, ensure_ascii=False))
