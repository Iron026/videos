"""Verificação preventiva (antes do render): pares de faces COPLANARES entre peças diferentes de uma cena exportada.
Peças que se encostam face a face brigam por profundidade (z-fighting), sobretudo dentro de cortes ilustrativos.
Lê cena.json + malhas .bin (12 floats/vértice: posição, normal, aLocal, aGen); objetos animados na pose do quadro 0.
Considera faces alinhadas aos eixos (caso de caixas e cilindros). Saída: pares com sobreposição > 0,1 mm × 0,1 mm,
marcando quando alguma das peças é cortada (prioridade). Uso: python3 varrer_faces_coplanares.py <pasta_cena> [prefixo_nome ...]"""
import json, sys, os, itertools
import numpy as np
d = sys.argv[1]; pref = tuple(sys.argv[2:]); c = json.load(open(os.path.join(d, 'cena.json')))
Q0 = c.get('animacao', {}).get('quadros', [{}])[0].get('objetos', {})
faces = []
for i, m in enumerate(c['materiais']):
    nm = m.get('nome') or f'mat{i}'
    if pref and not nm.startswith(pref): continue
    if not m.get('arquivo'): continue
    t = np.fromfile(os.path.join(d, m['arquivo']), np.float32).reshape(-1, 3, 12).astype(float); P = t[:, :, :3]
    if m.get('objeto') and m['objeto'] in Q0:
        M = np.array(Q0[m['objeto']]).reshape(4, 4).T; P = (np.concatenate([P, np.ones(P.shape[:2] + (1,))], 2) @ M.T)[:, :, :3]
    for ax in range(3):
        same = np.ptp(P[:, :, ax], axis=1) < 1e-6
        if not same.any(): continue
        vals = np.round(P[same][:, 0, ax], 6)
        for v in np.unique(vals):
            s = P[same][vals == v]; o = [a for a in range(3) if a != ax]
            faces.append((i, nm, m.get('corte'), ax, float(v), (s[:, :, o[0]].min(), s[:, :, o[0]].max(), s[:, :, o[1]].min(), s[:, :, o[1]].max())))
res = set()
for f, g in itertools.combinations(faces, 2):
    if f[0] == g[0] or f[3] != g[3] or abs(f[4] - g[4]) > 1e-7: continue
    a, b = f[5], g[5]; ov = min(a[1], b[1]) - max(a[0], b[0]); ov2 = min(a[3], b[3]) - max(a[2], b[2])
    if ov > 1e-4 and ov2 > 1e-4:
        res.add((bool(f[2] or g[2]), f[1], g[1], 'xyz'[f[3]], round(f[4], 5), round(ov * 1000, 1), round(ov2 * 1000, 1)))
for r in sorted(res, reverse=True):
    print(('CORTADA  ' if r[0] else '         ') + f'{r[1]} × {r[2]}  plano {r[3]} = {r[4]} m  sobreposição {r[5]} × {r[6]} mm')
print(f'{len(res)} pares coplanares ({sum(r[0] for r in res)} com peça cortada)')
