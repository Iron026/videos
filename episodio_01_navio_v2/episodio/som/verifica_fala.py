"""Lista os trechos de fala em que, no alto-falante de celular simulado (mono, 350 Hz–7 kHz), a voz fica < 10 dB acima do resto."""
import numpy as np, soundfile as sf, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from sintese import hpz, lpz, SR
E = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stems')
st = {k: sf.read(os.path.join(E, f'ep01_{k}.wav'))[0] for k in ('narracao', 'efeitos', 'ambiencias', 'musica')}
def cel(x): return hpz(lpz(x.mean(1), 7000, 4), 350, 4)
v = cel(st['narracao']); parts = {k: cel(st[k]) for k in ('efeitos', 'ambiencias', 'musica')}; r = sum(parts.values())
j = int(0.1 * SR); thr = np.mean(v ** 2) * 0.05; g = {}
for i in range(0, len(v) - j, j):
    pv = np.mean(v[i:i + j] ** 2)
    if pv > thr:
        snr = 10 * np.log10(pv / (np.mean(r[i:i + j] ** 2) + 1e-12))
        if snr < 10: g.setdefault(int(i / SR), []).append((round(snr, 1), max(parts, key=lambda k: np.mean(parts[k][i:i + j] ** 2)), round(10 * np.log10(pv + 1e-12), 1)))
for t, x in g.items(): print(t, x)
