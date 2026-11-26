"""Rodada 8: A/B CONTROLADO do AO nos planos em corte — mesma cena (a da rodada 8), mesmos quadros, mesma câmera, mesma luz;
só muda o AO: A = AO aprovado (aocorte=0: o AO "vê" a parte cortada) × B = AO com corte + máscara das tampas (o render de
revisão, quadros_revisao). Janela de N quadros SEGUIDOS em volta do pior trio do detector sensível (validacao_ao_*.json).
Medidas nos dois, nos mesmos quadros:
 · detector padrão (|Δ| > 30, blocos 16×16 ≥ 25 %) no quadro todo;
 · detector sensível (|Δ| > 12) DENTRO das tampas (máscara erodida 2 px, tampa nos 3 quadros) e na faixa de 8 px em volta;
 · granulado das tampas (desvio do laplaciano dentro das tampas) e escurecimento da faixa vizinha (B − A, luma).
Planos com obturador (config) usam a cena de sub-quadros e a MESMA integração do render.
Uso: python3 validar_ao_ab.py <validacao.json> <saida.json> [--n 12] [--so-medir] [planos...]
Renders: quadros_ao_ab/<plano>_aocorte0/ (um processo por vez; não roda junto com outro render)"""
import os, sys, json, subprocess, time
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, binary_erosion, laplace
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); MOTOR = os.path.join(RAIZ, 'motor')
CFG = json.load(open(os.path.join(RAIZ, 'config', 'producao.json'))); P = CFG['perfis']['revisao']; OBT = CFG.get('obturador', {})
args = sys.argv[1:]; VAL, SAIDA = args[0], args[1]; args = args[2:]
N = int(args[args.index('--n') + 1]) if '--n' in args else 12
if '--n' in args: i = args.index('--n'); del args[i:i + 2]
SO_MEDIR = '--so-medir' in args; args = [a for a in args if a != '--so-medir']
val = json.load(open(VAL)); IDS = args or list(val)
REV = os.path.join(A, 'quadros_revisao'); AB = os.path.join(A, 'quadros_ao_ab'); os.makedirs(AB, exist_ok=True)
def tampas(rgb):
    a = np.asarray(rgb.convert('HSV'), np.float32); h, s, v = a[..., 0] * 360 / 255, a[..., 1] / 255, a[..., 2] / 255
    return (h > 30) & (h < 60) & (s > 0.40) & (v > 0.45)
def blocos(m):
    H, W = m.shape; h, w = H // 16 * 16, W // 16 * 16
    return int((m[:h, :w].reshape(h // 16, 16, w // 16, 16).mean((1, 3)) >= 0.25).sum())
def integrar(src, dst, js):
    lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
    acc = sum(lin(np.asarray(Image.open(os.path.join(src, f'q{j:04d}.jpg')).convert('RGB'), np.float32) / 255.0) for j in js) / len(js)
    Image.fromarray(np.clip(srgb(acc) * 255 + 0.5, 0, 255).astype(np.uint8)).save(dst, quality=95)
def medir(pasta, ks):
    ims = {k: Image.open(os.path.join(pasta, f'q{k:04d}.jpg')).convert('RGB') for k in ks}
    L = {k: np.asarray(im.convert('L'), np.float32) for k, im in ims.items()}; T = {k: tampas(im) for k, im in ims.items()}
    r = dict(trios_blocos_padrao=0, px_padrao=0, px_sens_dentro=0, trios_blocos_sens_dentro=0, px_sens_borda=0)
    for k in ks[1:-1]:
        d1, d2 = L[k] - L[k - 1], L[k + 1] - L[k]; op = np.sign(d1) != np.sign(d2)
        a30 = (np.abs(d1) > 30) & (np.abs(d2) > 30) & op; a12 = (np.abs(d1) > 12) & (np.abs(d2) > 12) & op
        dentro = binary_erosion(T[k - 1] & T[k] & T[k + 1], iterations=2); borda = binary_dilation(T[k], iterations=8) & ~dentro
        r['trios_blocos_padrao'] += int(blocos(a30) > 0); r['px_padrao'] += int(a30.sum())
        r['px_sens_dentro'] += int((a12 & dentro).sum()); r['trios_blocos_sens_dentro'] += int(blocos(a12 & dentro) > 0); r['px_sens_borda'] += int((a12 & borda).sum())
    return r, L, T
res = json.load(open(SAIDA)) if os.path.exists(SAIDA) else {}
for pid in IDS:
    if pid not in val or not os.path.isdir(os.path.join(REV, pid)): continue
    nq = val[pid]['quadros']; pior = int(val[pid]['piores'][0]['quadro'][1:5])
    k0 = max(0, min(nq - N, pior - N // 2)); ks = list(range(k0, k0 + N))
    dA = os.path.join(AB, pid + '_aocorte0'); os.makedirs(dA, exist_ok=True)
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={P['escala']}&{P['consulta']}{CFG['por_plano'].get(pid, '')}&aocorte=0"
    if not SO_MEDIR and not all(os.path.exists(os.path.join(dA, f'q{k:04d}.jpg')) for k in ks):
        t = time.time()
        if pid in OBT:
            m = OBT[pid]['sub']; dsub = dA + '_sub'
            r = subprocess.run(['node', 'render_anim.mjs', q.replace(f'/cenas/{pid}/', f'/cenas/{pid}_obt/'), dsub, '1', str(ks[0] * m), str(ks[-1] * m + m - 1)], cwd=MOTOR, capture_output=True, text=True)
            for k in ks: integrar(dsub, os.path.join(dA, f'q{k:04d}.jpg'), range(k * m, k * m + m))
        else:
            r = subprocess.run(['node', 'render_anim.mjs', q, dA, '1', str(ks[0]), str(ks[-1])], cwd=MOTOR, capture_output=True, text=True)
        if r.returncode != 0: print(pid, 'ERRO', r.stderr[-300:]); sys.exit(3)
        print(pid, f'{len(ks)} quadros (aocorte=0) em {time.time() - t:.0f} s', flush=True)
    mA, LA, TA = medir(dA, ks); mB, LB, TB = medir(os.path.join(REV, pid), ks)
    # granulado (alta frequência) dentro das tampas e escurecimento da faixa vizinha, médios na janela
    gA, gB, esc, dif = [], [], [], []
    for k in ks:
        den = binary_erosion(TA[k] & TB[k], iterations=2); viz = binary_dilation(TA[k] & TB[k], iterations=10) & ~binary_dilation(TA[k] | TB[k], iterations=2)
        if den.sum() > 200: gA.append(float(np.std(laplace(LA[k])[den]))); gB.append(float(np.std(laplace(LB[k])[den])))
        if viz.sum() > 200: esc.append(float((LB[k] - LA[k])[viz].mean()))
        dif.append(float(np.abs(LB[k] - LA[k]).mean()))
    res[pid] = dict(janela=[ks[0], ks[-1]], A_aocorte0=mA, B_aocorte1_tampa=mB,
                    granulado_tampas=dict(A=round(np.mean(gA), 2) if gA else None, B=round(np.mean(gB), 2) if gB else None),
                    faixa_vizinha_B_menos_A=round(np.mean(esc), 2) if esc else None, dif_media_quadro=round(np.mean(dif), 2))
    print(pid, json.dumps(res[pid], ensure_ascii=False), flush=True)
    json.dump(res, open(SAIDA, 'w'), ensure_ascii=False, indent=1)
