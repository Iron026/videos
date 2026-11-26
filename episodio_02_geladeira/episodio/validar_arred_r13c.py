"""Rodada 13C — validação da correção dos quadros repetidos (ARRED_QUADROS=1) nos 4 planos com g0 a meio quadro.
Para cada plano: (1) índice do quadro renderizado por quadro do vídeo (mesma fórmula da montagem) — antes × depois:
repetições (congelamento), saltos (> 1 quadro) e retrocessos; (2) imagem composta (PNG da montagem real): pares idênticos
(congelamento) e saltos de movimento (|Δ| > 2,5 × mediana dos vizinhos); (3) duração: nº de quadros do episódio e da janela.
Uso: python3 validar_arred_r13c.py <pasta_png_raiz> → relatorios/testes_r13c/validacao_quadros_repetidos.json"""
import os, sys, json, math, glob, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'decupagem')); import planos as PL
A = os.path.dirname(os.path.abspath(__file__)); raiz = sys.argv[1]; FPS = 30
R = PL.resolvidos(); P = {p['id']: p for p in R['planos']}; n_ep = int(round(R['duracao'] * FPS))
G0 = {pid: json.load(open(os.path.join(A, 'cenas', pid, 'cena.json')))['g0'] for pid in ('A1', 'B7', 'H1', 'I1')}
velho = lambda x: int(round(x)); novo = lambda x: int(math.floor(x + 0.5 + 1e-6))
res = dict(quadros_do_episodio=dict(antes=n_ep, depois=n_ep, duracao_s=round(n_ep / FPS, 4)), planos={})
for pid, g0 in G0.items():
    t0, t1 = P[pid]['t0'], P[pid]['t1']; qs = range(int(math.ceil(t0 * FPS)), int(math.ceil(t1 * FPS)))   # quadros em que o plano é o ÚNICO ativo (fora das fusões)
    iv = [velho((q / FPS - g0) * FPS) for q in qs]; inn = [novo((q / FPS - g0) * FPS) for q in qs]
    dv, dn = np.diff(iv), np.diff(inn)
    r = dict(trecho_s=[round(t0, 3), round(t1, 3)], quadros_no_trecho=len(qs),
             indice_antes=dict(repeticoes=int((dv == 0).sum()), saltos_2=int((dv == 2).sum()), outros=int(((dv != 0) & (dv != 1) & (dv != 2)).sum())),
             indice_depois=dict(repeticoes=int((dn == 0).sum()), saltos=int((dn > 1).sum()), retrocessos=int((dn < 0).sum()), passo_unico=bool(np.all(dn == 1))),
             deslocamento_temporal_max_ms=round(max(abs(i - (q / FPS - g0) * FPS) for i, q in zip(inn, qs)) / FPS * 1000, 2))
    for lado, sub in (('antes', 'A'), ('depois', 'B')):
        fs = sorted(glob.glob(os.path.join(raiz, f'{pid}_{sub}', 'c*.png'))); fs = [f for f in fs if int(os.path.basename(f)[1:6]) in qs]
        im = [np.asarray(Image.open(f).convert('L').resize((270, 480)), np.float32) for f in fs]
        d = np.array([np.abs(im[k + 1] - im[k]).mean() for k in range(len(im) - 1)])
        hs = [hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in fs]
        med = np.array([np.median(d[max(0, k - 3):k + 4]) for k in range(len(d))])
        r[f'imagem_{lado}'] = dict(pares_identicos=int(sum(hs[k] == hs[k + 1] for k in range(len(hs) - 1))), pares_quase_parados=int((d < 0.15).sum()),
                                  saltos=int(((d > 2.5 * med) & (d > 1.0)).sum()), dif_media=round(float(d.mean()), 3), dif_max=round(float(d.max()), 3))
    r['aprovado'] = bool(r['indice_depois']['passo_unico'] and r['imagem_depois']['pares_identicos'] == 0 and r['imagem_depois']['saltos'] == 0)
    res['planos'][pid] = r
res['aprovado'] = all(r['aprovado'] for r in res['planos'].values())
os.makedirs(os.path.join(A, '..', 'relatorios', 'testes_r13c'), exist_ok=True)
json.dump(res, open(os.path.join(A, '..', 'relatorios', 'testes_r13c', 'validacao_quadros_repetidos.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
