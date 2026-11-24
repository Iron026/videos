"""Rodada 10: quanto serrilhado SOBRA com o MSAA 4× aprovado em 1080, medido contra uma referência supersamplada.
Para trechos curtos e CONTÍNUOS (bordas finas: arames, capilar, porta, personagem), renderiza a mesma cena em escala 2,0
(2160 × 3840, MSAA 4×, mesma configuração) e reduz para 1080 com média de 2 × 2 em luz linear = referência ~16 amostras/px.
Compara com os quadros de 1080 do teste contínuo (quadros_final_r10/<plano>):
 · erro ESPACIAL nas bordas: |1080 − referência| médio onde há borda (Sobel da referência acima do p90);
 · CINTILAÇÃO de borda: |Δt(1080) − Δt(referência)| médio nas bordas (o que pisca no 1080 e não na referência);
 · candidato local: escala 1,5 reduzida para 1080 (custo 2,25×), só se o ganho for perceptível.
Uso: python3 teste_aa_r10.py [render|medir]"""
import os, sys, json, subprocess, time
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motor')
C = json.load(open(os.path.join(A, '..', 'config', 'producao.json'))); CFG = C['perfis']['final']
TRECHOS = {'F1': (60, 67), 'A2': (30, 37), 'G3': (70, 77), 'H1': (100, 107), 'E1': (55, 62)}   # E1: tubos finos com câmera lenta (540: bordas alternando)
OUT = os.path.join(A, 'quadros_aa_r10'); LOG = os.path.join(OUT, '_teste.log'); os.makedirs(OUT, exist_ok=True)
lin = lambda a: np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
srgb = lambda a: np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.clip(a, 0, 1), 1 / 2.4) - 0.055)
def reduzir(f, fator):
    a = lin(np.asarray(Image.open(f).convert('RGB'), np.float32) / 255.0)
    if fator == 2: a = a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, 3).mean((1, 3))
    else: a = lin(np.asarray(Image.open(f).convert('RGB').resize((1080, 1920), Image.LANCZOS), np.float32) / 255.0)
    return srgb(a) * 255
if 'render' in sys.argv[1:] or len(sys.argv) == 1:
    for esc, nome in ((1.0, 'ss1'), (2.0, 'ss2'), (1.5, 'ss15')):
        for pid, (i0, i1) in TRECHOS.items():
            d = os.path.join(OUT, f'{pid}_{nome}')
            if nome == 'ss1' and os.path.isdir(os.path.join(A, 'quadros_final_r10', pid)): continue   # já há 1080 do teste contínuo
            if all(os.path.exists(os.path.join(d, f'q{i:04d}.jpg')) for i in range(i0, i1 + 1)): continue
            q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={esc}&{CFG['consulta']}{C['por_plano'].get(pid, '')}"
            t = time.time(); r = subprocess.run(['node', 'render_anim.mjs', q, d, '1', str(i0), str(i1)], cwd=MOTOR, capture_output=True, text=True)
            open(LOG, 'a').write(f"{time.strftime('%H:%M:%S')} {pid} {nome} q{i0}–q{i1}: {'ok' if r.returncode == 0 else 'ERRO ' + r.stderr[-200:]} em {time.time() - t:.0f} s\n")
if 'medir' in sys.argv[1:] or len(sys.argv) == 1:
    from scipy.ndimage import sobel
    res = {}
    for pid, (i0, i1) in TRECHOS.items():
        R = [reduzir(os.path.join(OUT, f'{pid}_ss2', f'q{i:04d}.jpg'), 2) for i in range(i0, i1 + 1)]
        d1 = os.path.join(A, 'quadros_final_r10', pid) if os.path.isdir(os.path.join(A, 'quadros_final_r10', pid)) else os.path.join(OUT, f'{pid}_ss1')
        T = [np.asarray(Image.open(os.path.join(d1, f'q{i:04d}.jpg')).convert('RGB'), np.float32) for i in range(i0, i1 + 1)]
        S = [reduzir(os.path.join(OUT, f'{pid}_ss15', f'q{i:04d}.jpg'), 1.5) for i in range(i0, i1 + 1)] if all(os.path.exists(os.path.join(OUT, f'{pid}_ss15', f'q{i:04d}.jpg')) for i in range(i0, i1 + 1)) else None
        g = lambda x: x.mean(2)
        bordas = [np.hypot(sobel(g(r), 0), sobel(g(r), 1)) for r in R]; mask = [b > np.percentile(b, 90) for b in bordas]
        esp = lambda X: float(np.mean([np.abs(g(x) - g(r))[m].mean() for x, r, m in zip(X, R, mask)]))
        tmp = lambda X: float(np.mean([np.abs((g(X[k]) - g(X[k - 1])) - (g(R[k]) - g(R[k - 1])))[mask[k]].mean() for k in range(1, len(R))]))
        ruido = float(np.mean([np.abs(g(R[k]) - g(R[k - 1]))[mask[k]].mean() for k in range(1, len(R))]))
        res[pid] = dict(quadros=[i0, i1], erro_espacial_bordas_msaa4=round(esp(T), 2), cintilacao_bordas_msaa4=round(tmp(T), 2), movimento_bordas_ref=round(ruido, 2),
                        **({'erro_espacial_bordas_ss15': round(esp(S), 2), 'cintilacao_bordas_ss15': round(tmp(S), 2)} if S else {}))
        print(pid, res[pid], flush=True)
        # mapa: onde o 1080 difere da referência (quadro do meio)
        k = len(R) // 2; dmap = np.clip(np.abs(g(T[k]) - g(R[k])) * 4, 0, 255).astype(np.uint8)
        Image.fromarray(np.concatenate([T[k].astype(np.uint8), R[k].clip(0, 255).astype(np.uint8), np.stack([dmap] * 3, 2)], 1)).resize((1620, 960)).save(os.path.join(OUT, f'{pid}_mapa.jpg'), quality=90)
    json.dump(res, open(os.path.join(A, '..', 'relatorios', 'testes_r10', 'antisserrilhado_1080.json'), 'w'), ensure_ascii=False, indent=1)
