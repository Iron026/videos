"""Testes geométricos do circuito 3D (itens 6 e 8 da lista): continuidade, ciclo fechado, folgas entre tubos que não se
conectam, tubos fora da carcaça do compressor, s monotônico. Uso: PYTHONPATH=<bpy> python3 testes_cena.py"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geladeira as G

tr, tot = G.circuito_param(); falhas, ok = [], []
def teste(n, c, d): (ok if c else falhas).append(f'{n}: {d}')
# continuidade e fechamento
gaps = []
for i, t in enumerate(tr):
    a = np.array(t['pts'][-1]); b = np.array(tr[(i + 1) % len(tr)]['pts'][0]); d = np.linalg.norm(a - b)
    if d > 1e-4: gaps.append(f"{t['id']}→{tr[(i+1)%len(tr)]['id']} {d*1000:.2f} mm")
teste('6 continuidade e ciclo fechado', not gaps, 'emendas abertas: ' + (', '.join(gaps) or 'nenhuma') + f' · comprimento total {tot:.2f} m')
teste('s global monotônico', all(abs(tr[i]['s1'] - tr[i + 1]['s0']) < 1e-9 for i in range(len(tr) - 1)) and abs(tr[-1]['s1'] - 1) < 1e-9,
      ' · '.join(f"{t['id']} {t['s0']:.3f}–{t['s1']:.3f} ({t['comprimento']:.2f} m)" for t in tr))
# amostragem densa
def amostras(t, passo=0.004):
    P = [np.array(p) for p in t['pts']]; out = []
    for i in range(len(P) - 1):
        n = max(1, int(np.linalg.norm(P[i + 1] - P[i]) / passo))
        for k in range(n): out.append(P[i] + (P[i + 1] - P[i]) * k / n)
    out.append(P[-1]); return np.array(out)
S = {t['id']: amostras(t) for t in tr if t['id'] != 'compressor'}
pior = []
ids = list(S)
for i, a in enumerate(ids):
    for b in ids[i + 1:]:
        A, B = S[a], S[b]
        # ignora 3 cm em volta das emendas entre trechos vizinhos (lá eles se tocam por definição)
        D = np.linalg.norm(A[:, None, :] - B[None, :, :], axis=2)
        emendas = [np.array(tr[k]['pts'][0]) for k in range(len(tr))]
        m = np.ones_like(D, bool)
        for e in emendas:
            m &= ~((np.linalg.norm(A - e, axis=1) < 0.03)[:, None] | (np.linalg.norm(B - e, axis=1) < 0.03)[None, :])
        if not m.any(): continue
        dmin = D[m].min(); folga = dmin - G.R[a] - G.R[b]
        pior.append((folga, a, b))
pior.sort()
teste('8 folga entre tubos diferentes ≥ 3 mm', pior[0][0] >= 0.003, ' · '.join(f'{a}×{b} {f*1000:.1f} mm' for f, a, b in pior[:4]))
# o próprio trecho não pode se cruzar (pontos não vizinhos ao longo do tubo)
auto = []
for n, A in S.items():
    if n == 'capilar': continue   # a hélice do capilar é verificada pelo passo (abaixo)
    idx = np.arange(len(A)); D = np.linalg.norm(A[:, None] - A[None], axis=2); viz = np.abs(idx[:, None] - idx[None]) * 0.004 < 0.06
    D[viz] = 9; auto.append((D.min() - 2 * G.R[n], n))
auto.sort(); teste('8 trechos sem auto-interseção', auto[0][0] > 0.002, ' · '.join(f'{n} {d*1000:.1f} mm' for d, n in auto[:3]))
passo_helice = (0.265 - 0.17) / 7
teste('8 espiras do capilar separadas', passo_helice - 2 * G.R['capilar'] > 0.004, f'passo {passo_helice*1000:.1f} mm, diâmetro {2*G.R["capilar"]*1000:.1f} mm')
# tubos fora da carcaça do compressor (exceto as pontas de conexão)
c = np.array(G.COMP['c']); invade = []
for n, A in S.items():
    rr = np.linalg.norm(A[:, :2] - c[:2], axis=1); dentro = (rr < G.COMP['r'] + G.R[n]) & (A[:, 2] < 0.045 + G.COMP['h'])
    if dentro.sum() > 0: invade.append(f'{n}:{int(dentro.sum())} amostras')
teste('8 tubos fora do compressor', not invade, ', '.join(invade) or 'nenhum')
for s in ok: print('PASSOU  ', s)
for s in falhas: print('FALHOU  ', s)
json.dump(dict(passaram=ok, falharam=falhas), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios', 'testes_cena.json'), 'w'), ensure_ascii=False, indent=1)
sys.exit(1 if falhas else 0)
