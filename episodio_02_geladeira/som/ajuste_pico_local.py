"""Rodada 11: correção MÍNIMA de pico verdadeiro no AAC — só nos instantes indicados, sem mexer no resto da mixagem.
Para cada instante t: numa janela de ±0,2 s, o ganho cai o necessário para o pico (sobreamostrado 4×) ficar ≤ TETO (dBFS),
com rampas de 30 ms (cosseno); fora das janelas, a saída é IDÊNTICA à entrada (provado). O MP3 da narração não muda.
Uso: python3 ajuste_pico_local.py entrada.wav saida.wav teto_db t1 [t2 ...]  → imprime a redução por janela e a prova"""
import sys, json
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
ent, sai, teto = sys.argv[1], sys.argv[2], float(sys.argv[3]); ts = [float(x) for x in sys.argv[4:]]
x, SR = sf.read(ent); y = x.copy(); g = np.ones(len(x)); r = int(0.03 * SR); rel = []
for t in ts:
    a, b = int((t - 0.2) * SR), int((t + 0.2) * SR)
    pk = np.abs(resample_poly(x[a:b], 4, 1, axis=0)).max(); alvo = 10 ** (teto / 20)
    if pk <= alvo: rel.append(dict(t=t, reducao_db=0.0)); continue
    k = alvo / pk; w = np.ones(b - a) * k
    w[:r] = 1 - (1 - k) * (1 - np.cos(np.linspace(0, np.pi, r))) / 2; w[-r:] = w[:r][::-1]
    g[a:b] = np.minimum(g[a:b], w); rel.append(dict(t=t, pico_antes_dbfs=round(20 * np.log10(pk), 2), reducao_db=round(20 * np.log10(k), 2)))
y = x * g[:, None]; sf.write(sai, y.astype(np.float32), SR, subtype='PCM_24')
fora = np.ones(len(x), bool)
for t in ts: fora[int((t - 0.2) * SR):int((t + 0.2) * SR)] = False
z = sf.read(sai)[0]
print(json.dumps(dict(janelas=rel, amostras_alteradas_pct=round(float((g < 1).mean() * 100), 4), fora_das_janelas_identico=bool(np.array_equal(sf.read(ent, dtype='int32')[0][fora], sf.read(sai, dtype='int32')[0][fora]))), ensure_ascii=False))
