"""Contraste ação × calma: pico momentâneo dos efeitos+ambiências nas ações e média nos trechos calmos, anterior × refinado
(refinado corrigido pela diferença de master, narração no mesmo nível). Uso: python3 som/acao_calma.py"""
import numpy as np, soundfile as sf, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from som_ep01 import lufs, db
A = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(A, '..', 'stems'); SR = 48000
mh, mr = (json.load(open(os.path.join(A, f'mix_{v}.json')))['master_db'] for v in ('hibrido', 'refinado'))
st = {v: sf.read(f'{E}/ep01_efeitos_{v}.wav')[0] + sf.read(f'{E}/ep01_ambiencias_{v}.wav')[0] for v in ('hibrido', 'refinado')}; st['refinado'] *= db(mh - mr)
res = []
for a, b, nome, calmo in ((2.4, 3.8, 'impacto abertura', 0), (23.4, 24.2, 'encaixe da chapa', 0), (41.6, 42.8, 'comporta + jatos', 0), (76.0, 77.0, 'impacto retomada', 0), (86.0, 87.0, 'experimento', 0),
                          (101.4, 102.2, 'pouso contêiner 1', 0), (134.7, 135.6, 'ruptura', 0), (137.0, 140.0, 'jato da avaria', 0), (155.6, 156.8, 'impacto conclusão', 0),
                          (8.0, 14.0, 'navegação', 1), (66.0, 74.0, 'empuxo subaquático', 1), (120.0, 133.0, 'calado/marcas', 1), (164.4, 167.5, 'plano final', 1)):
    f = (lambda x: float(np.max(lufs(x, curto=True)))) if not calmo else (lambda x: float(lufs(x)))
    r = [f(st[v][int(a * SR):int(b * SR)]) for v in ('hibrido', 'refinado')]
    res.append(dict(trecho=nome, tipo='calmo (média)' if calmo else 'ação (pico momentâneo)', anterior=round(r[0], 1), refinado=round(r[1], 1), dif_db=round(r[1] - r[0], 1)))
    print(f"{res[-1]['tipo']:24s} {nome:20s} {r[0]:6.1f} → {r[1]:6.1f}  ({r[1] - r[0]:+.1f} dB)")
json.dump(res, open(os.path.join(A, 'contraste_acao_calma.json'), 'w'), ensure_ascii=False, indent=1)
