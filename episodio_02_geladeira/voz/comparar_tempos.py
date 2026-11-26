"""Compara os tempos do alinhamento por pausas (roteiro/palavras.json, usado na v1) com os medidos pelo Whisper oficial
(roteiro/palavras_whisper.json): por palavra, por início de frase e nas ÂNCORAS dos cortes (decupagem/planos.py).
Uso: python3 comparar_tempos.py   → imprime e grava voz/comparacao_tempos.json"""
import os, sys, json
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..', 'roteiro')
sys.path.insert(0, os.path.join(A, '..', 'decupagem')); import planos as PL
v1 = json.load(open(os.path.join(R, 'palavras_v1_pausas.json'))); wh = json.load(open(os.path.join(R, 'palavras.json')))   # v1 (pausas) × final (Whisper + ataque)
assert [w['palavra'] for w in v1] == [w['palavra'] for w in wh]
d = np.array([w['inicio'] - v['inicio'] for v, w in zip(v1, wh)])
fr = PL.frases(v1); df = np.array([wh[f[0]]['inicio'] - v1[f[0]]['inicio'] for f in fr])
anc = []
for (pid, a, *_r) in PL.PLANOS:
    t_v1 = PL.resolver(a, v1, fr); t_wh = PL.resolver(a, wh, fr); anc.append(dict(plano=pid, ancora=a, v1=round(t_v1, 3), whisper=round(t_wh, 3), delta=round(t_wh - t_v1, 3)))
da = np.array([x['delta'] for x in anc[1:]])
res = dict(palavras=dict(n=len(d), media_abs=round(float(np.mean(np.abs(d))), 3), p95_abs=round(float(np.percentile(np.abs(d), 95)), 3), max_abs=round(float(np.max(np.abs(d))), 3)),
           inicios_de_frase=dict(n=len(df), media_abs=round(float(np.mean(np.abs(df))), 3), max_abs=round(float(np.max(np.abs(df))), 3)),
           ancoras_dos_cortes=dict(n=len(da), media_abs=round(float(np.mean(np.abs(da))), 3), max_abs=round(float(np.max(np.abs(da))), 3),
                                   acima_de_2_quadros=[x for x in anc[1:] if abs(x['delta']) > 2 / 30]),
           fim_da_fala=dict(v1=v1[-1]['fim'], whisper=wh[-1]['fim']), ancoras=anc)
json.dump(res, open(os.path.join(A, 'comparacao_tempos.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'ancoras'}, ensure_ascii=False, indent=1))
