"""Rodada 8: z-fighting porta × vedação visto pelo corte ilustrativo (defeito antigo da rodada 5).
A face de trás do painel da porta (y = GY0 − 0,001) coincide com a face da frente da vedação. Com a porta FECHADA e o corte em
x = 0, a câmera do lado +x e à frente da porta (y < GY0) enxerga pelo corte o interior do painel: a tampa amarela (face de trás
do painel, vista por dentro) e a vedação escura ficam na MESMA profundidade → a faixa alterna amarelo/escuro entre quadros.
1. Geometria: para cada plano em corte, em quais quadros a faixa do painel (x = 0, y ∈ [GY0 − 0,056; GY0 − 0,001], z da vedação)
   aparece no quadro, e com que largura em pixels (540 × 960). Sem câmera do lado certo, o defeito não pode aparecer.
2. Imagem: pixels que vão e voltam (|Δ| > 30) DENTRO da faixa projetada, numa pasta de quadros (renders) ou num vídeo.
Uso: python3 verificar_porta_vedacao.py <saida.json> [--video arq.mp4 --passo 2] [--quadros pasta] [planos...]"""
import os, sys, json, math, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(A, '..', 'decupagem')); import planos as PL
GY0 = -0.340; Z0, Z1 = 0.07, 1.47
args = sys.argv[1:]; saida = args.pop(0)
def opt(k, d=None):
    if k in args: i = args.index(k); v = args[i + 1]; del args[i:i + 2]; return v
    return d
VIDEO, PASSO, QUADROS = opt('--video'), int(opt('--passo', '1')), opt('--quadros')
T = {p['id']: (p['t0'], p['t1']) for p in PL.resolvidos()['planos']}
CEN = os.path.join(A, 'cenas')
IDS = args or sorted(p for p in os.listdir(CEN) if os.path.exists(os.path.join(CEN, p, 'cena.json')) and json.load(open(os.path.join(CEN, p, 'cena.json'))).get('ao_corte'))
def proj(cam, P, W=540, H=960):
    pos = np.array(cam['pos']); f = np.array(cam['dir']); f /= np.linalg.norm(f); r = np.cross(f, cam['up']); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = P - pos; z = d @ f; t = math.tan(math.radians(cam['fov'] / 2))
    return ((d @ r / z) / (t * W / H) + 1) / 2 * W, (1 - (d @ u / z) / t) / 2 * H, z
def faixa(cam):
    if not (cam['pos'][0] > 0 and cam['pos'][1] < GY0): return None, 0.0
    zs = np.linspace(Z0, Z1, 40)
    ua, va, za = proj(cam, np.stack([np.zeros_like(zs), np.full_like(zs, GY0 - 0.056), zs], 1))
    ub, vb, zb = proj(cam, np.stack([np.zeros_like(zs), np.full_like(zs, GY0 - 0.001), zs], 1))
    ok = (za > 0) & (zb > 0) & (ub >= 0) & (ub < 540) & (vb >= 0) & (vb < 960)
    if not ok.any(): return None, 0.0
    m = Image.new('L', (540, 960)); ImageDraw.Draw(m).polygon(list(zip(ua, va)) + list(zip(ub[::-1], vb[::-1])), fill=1)
    return np.asarray(m) > 0, float(np.hypot(ua - ub, va - vb)[ok].max())
res = {}
for pid in IDS:
    qs = json.load(open(os.path.join(CEN, pid, 'cena.json')))['animacao']['quadros']
    fx = [faixa(q['camera']) for q in qs]
    r = dict(quadros=len(qs), quadros_com_faixa_a_vista=sum(1 for m, _ in fx if m is not None), largura_max_px_540=round(max(w for _, w in fx), 1))
    L = None
    if VIDEO and r['quadros_com_faixa_a_vista']:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(T[pid[:2]][0]), '-t', str(T[pid[:2]][1] - T[pid[:2]][0]), '-i', VIDEO, '-vf', 'scale=540:960', f'{d}/%04d.png'], check=True)
            L = [np.asarray(Image.open(os.path.join(d, x)).convert('L'), np.float32) for x in sorted(os.listdir(d))]
    elif QUADROS and r['quadros_com_faixa_a_vista']:
        d = os.path.join(QUADROS, pid); fs = sorted(x for x in os.listdir(d) if x.startswith('q') and x.endswith('.jpg'))
        L = [np.asarray(Image.open(os.path.join(d, x)).convert('L').resize((540, 960)), np.float32) for x in fs]
    if L is not None:
        alts = []
        for k in range(PASSO, min(len(L), len(qs)) - PASSO, PASSO):
            m = fx[k][0]
            if m is None or m.sum() < 50: continue
            d1, d2 = L[k] - L[k - PASSO], L[k + PASSO] - L[k]
            alts.append(int(((np.abs(d1) > 30) & (np.abs(d2) > 30) & (np.sign(d1) != np.sign(d2)) & m).sum()))
        r.update(trios_avaliados=len(alts), pixels_alternando_total=sum(alts), pixels_alternando_max_quadro=max(alts) if alts else 0,
                 trios_com_mais_de_50_px=sum(1 for x in alts if x > 50), fonte=VIDEO or QUADROS)
    res[pid] = r; print(pid, r, flush=True)
json.dump(res, open(saida, 'w'), ensure_ascii=False, indent=1)
