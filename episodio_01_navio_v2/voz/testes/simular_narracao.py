"""Narração 'nova' simulada a partir da atual (para testar a ferramenta, sem gerar voz): cada bloco de fala com ritmo
diferente (0,92–1,10, sem mudar a altura), pausas ×0,7–1,5, outro timbre e outro volume. Grava a VERDADE: para cada
palavra e frase, o tempo exato na narração simulada."""
import sys, os, json, numpy as np, soundfile as sf
from scipy.signal import lfilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); import comparar_narracao as CN
T = CN.TRAB; x, sr = sf.read(os.path.join(T, 'narracao_48k.wav')); x = x.mean(1) if x.ndim == 2 else x
fr = json.load(open(os.path.join(T, 'frases.json'))); pal = json.load(open(os.path.join(T, 'palavras.json')))
bl = [[0]]
for k in range(1, len(fr)): (bl[-1].append(k) if fr[k]['inicio'] - fr[k - 1]['fim'] < 0.12 else bl.append([k]))
cort = [0.0] + [(fr[b[-1]]['fim'] + fr[c[0]]['inicio']) / 2 for b, c in zip(bl, bl[1:])] + [len(x) / sr]
r = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 7); partes = []; pos = 0.30; vp, vf = {}, {}
for q, b in enumerate(bl):
    w0, w1 = cort[q], cort[q + 1]; tempo = r.uniform(0.92, 1.10)
    g = r.uniform(0.7, 1.5)                                   # pausas: o silêncio antes e depois do bloco também muda
    y = CN.esticar(x[int(w0 * sr):int(w1 * sr)], sr, tempo)
    m = lambda t: pos + (t - w0) / tempo
    for k in b: vf[k] = m(fr[k]['inicio'])
    for i, p in enumerate(pal):
        if w0 <= p['inicio'] < w1: vp[i] = m(p['inicio'])
    partes.append((pos, y)); pos += len(y) / sr + (g - 1) * 0.3
y = np.zeros(int((pos + 1) * sr))
for p0, s in partes: i = int(p0 * sr); y[i:i + len(s)] += s[:len(y) - i]
y = 0.7 * lfilter([1, -0.6], [1], y)
sf.write(sys.argv[1], y / np.abs(y).max() * 0.8, sr, subtype='PCM_24')
json.dump(dict(palavras=vp, frases=vf), open(sys.argv[1] + '.verdade.json', 'w'))
print('simulada', round(len(y) / sr, 2), 's ·', len(bl), 'blocos')
