"""Rodada 8: z-fighting de peças do gabinete ENCOSTADAS face a face (sobras do relatorios/coplanares_folga0.0005.json) vistas
pelo corte em x = 0. Para cada junta e cada plano em corte: projeta o retângulo coincidente (parte x ≤ 0) em cada quadro e
conta os pixels que vão e voltam (|Δ| > 30 e, sensível, > 12) DENTRO dele nos quadros de revisão (540 × 960).
Uso: python3 verificar_juntas.py <pasta_quadros> <saida.json> [planos...]"""
import os, sys, json, math
import numpy as np
from PIL import Image, ImageDraw
GX, GY0, GY1, GZ = 0.300, -0.340, 0.310, 1.500; ESP = 0.045; IX, IY1, IZ1 = GX - ESP, GY1 - ESP, GZ - ESP; NZ1 = 0.30; e = 0.0005
JUNTAS = {   # nome: 4 cantos do retângulo coincidente (lado mantido pelo corte, x ≤ 0)
    'degrau×fundo_tras (y = IY1)': [(-IX + e, IY1, NZ1), (0, IY1, NZ1), (0, IY1, NZ1 + 0.032), (-IX + e, IY1, NZ1 + 0.032)],
    'fundo_tras×topo (z = IZ1)': [(-IX + e, IY1, IZ1), (0, IY1, IZ1), (0, GY1, IZ1), (-IX + e, GY1, IZ1)]}
base, saida = sys.argv[1], sys.argv[2]; A = os.path.dirname(os.path.abspath(__file__)); CEN = os.path.join(A, os.environ.get('CENAS_DIR', 'cenas'))
IDS = sys.argv[3:] or sorted(p for p in os.listdir(CEN) if os.path.exists(os.path.join(CEN, p, 'cena.json')) and json.load(open(os.path.join(CEN, p, 'cena.json'))).get('ao_corte'))
def proj(cam, P, W=540, H=960):
    pos = np.array(cam['pos']); f = np.array(cam['dir']); f /= np.linalg.norm(f); r = np.cross(f, cam['up']); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = np.array(P) - pos; z = d @ f; t = math.tan(math.radians(cam['fov'] / 2))
    return ((d @ r / z) / (t * W / H) + 1) / 2 * W, (1 - (d @ u / z) / t) / 2 * H, z
res = {}
for pid in IDS:
    qs = json.load(open(os.path.join(CEN, pid, 'cena.json')))['animacao']['quadros']; d = os.path.join(base, pid)
    if not os.path.isdir(d): continue
    fs = sorted(x for x in os.listdir(d) if x.startswith('q') and x.endswith('.jpg'))
    L = [np.asarray(Image.open(os.path.join(d, x)).convert('L'), np.float32) for x in fs]
    res[pid] = {}
    for nome, cs in JUNTAS.items():
        a30, a12, vis, piores = 0, 0, 0, []
        for k in range(1, min(len(L), len(qs)) - 1):
            pr = [proj(qs[k]['camera'], c) for c in cs]
            if any(p[2] <= 0.01 for p in pr): continue
            m = Image.new('L', (540, 960)); ImageDraw.Draw(m).polygon([(p[0], p[1]) for p in pr], fill=1); m = np.asarray(m) > 0
            if m.sum() < 20: continue
            vis += 1; d1, d2 = L[k] - L[k - 1], L[k + 1] - L[k]; op = np.sign(d1) != np.sign(d2)
            n30 = int(((np.abs(d1) > 30) & (np.abs(d2) > 30) & op & m).sum()); n12 = int(((np.abs(d1) > 12) & (np.abs(d2) > 12) & op & m).sum())
            a30 += n30; a12 += n12; piores.append((n12, fs[k]))
        res[pid][nome] = dict(quadros_com_junta_no_quadro=vis, px_alternando_30=a30, px_alternando_12=a12, pior=max(piores) if piores else None)
    print(pid, res[pid], flush=True)
json.dump(res, open(saida, 'w'), ensure_ascii=False, indent=1)
