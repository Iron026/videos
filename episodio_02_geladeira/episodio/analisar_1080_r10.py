"""Rodada 10: análise dos testes CONTÍNUOS em 1080 (quadros_final_r10/<plano>).
Para cada trecho: detector absoluto (pixels que vão e voltam |Δ| > 30, blocos 16×16 com ≥ 25 %) em 1080 e nos MESMOS
quadros da revisão 540 (pixels × 4 = mesma área na tela) — um conflito de profundidade muda com a resolução, animação e
movimento não mudam; quando existe, o mesmo trecho de uma rodada aprovada em 1080 (r8/r9v/quadros_final); mapa do pior
quadro em relatorios/comparativos_r10/1080_<plano>_mapa.jpg.
Uso: python3 analisar_1080_r10.py → relatorios/testes_r10/testes_1080_r10.json"""
import os, json, ast
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); D10 = os.path.join(A, 'quadros_final_r10'); OUTC = os.path.join(A, '..', 'relatorios', 'comparativos_r10')
TRECHOS = ast.literal_eval(open(os.path.join(A, 'teste_1080_r10.py')).read().split('TRECHOS = ', 1)[1].split('\n}', 1)[0] + '\n}')
def L(d, k, w): return np.asarray(Image.open(os.path.join(d, f'q{k:04d}.jpg')).convert('L').resize((w, w * 16 // 9)), np.float32)
def detector(d, k0, k1, w):
    res = []; a, b = L(d, k0, w), L(d, k0 + 1, w)
    for k in range(k0 + 1, k1):
        c = L(d, k + 1, w); d1, d2 = b - a, c - b; m = (np.abs(d1) > 30) & (np.abs(d2) > 30) & (np.sign(d1) != np.sign(d2))
        H, W = m.shape; bl = int((m[:H // 16 * 16, :W // 16 * 16].reshape(H // 16, 16, W // 16, 16).mean((1, 3)) >= 0.25).sum())
        res.append((k, bl, int(m.sum()))); a, b = b, c
    return res
out = {}
for pid, (i0, i1) in TRECHOS.items():
    d = os.path.join(D10, pid)
    if not all(os.path.exists(os.path.join(d, f'q{k:04d}.jpg')) for k in range(i0, i1 + 1)): continue
    r1 = detector(d, i0, i1, 1080); r5 = detector(os.path.join(A, 'quadros_revisao', pid), i0, i1, 540)
    o = dict(quadros=[i0, i1], px_1080=sum(x[2] for x in r1), px_540_x4=4 * sum(x[2] for x in r5), quadros_com_blocos_1080=sum(1 for x in r1 if x[1]), pior_1080=max(r1, key=lambda x: x[1]))
    o['razao_1080_sobre_540'] = round(o['px_1080'] / max(1, o['px_540_x4']), 2)
    for nome, dd in (('r8', 'quadros_final_r8'), ('r9v', 'quadros_final_r9v'), ('aprovada_r6r7', 'quadros_final')):
        p = os.path.join(A, dd, pid)
        if os.path.isdir(p) and all(os.path.exists(os.path.join(p, f'q{k:04d}.jpg')) for k in range(i0, i1 + 1)):
            rr = detector(p, i0, i1, 1080); o[f'px_1080_{nome}'] = sum(x[2] for x in rr)
    k = o['pior_1080'][0]; a, b, c = L(d, k - 1, 1080), L(d, k, 1080), L(d, k + 1, 1080); d1, d2 = b - a, c - b
    m = (np.abs(d1) > 30) & (np.abs(d2) > 30) & (np.sign(d1) != np.sign(d2)); im = np.asarray(Image.open(os.path.join(d, f'q{k:04d}.jpg')).convert('RGB')).copy(); im[m] = [255, 0, 255]
    Image.fromarray(im).resize((540, 960)).save(os.path.join(OUTC, f'1080_{pid}_mapa_q{k}.jpg'), quality=88)
    out[pid] = o; print(pid, {kk: v for kk, v in o.items()}, flush=True)
json.dump(out, open(os.path.join(A, '..', 'relatorios', 'testes_r10', 'testes_1080_r10.json'), 'w'), ensure_ascii=False, indent=1)
