"""Sincronia dos impactos no stem de efeitos do som híbrido: ataque medido (subida mais forte do envelope de 5 ms)
perto de cada evento da animação. Saída: som/sincronia_hibrido.json"""
import os, sys, json, numpy as np, soundfile as sf
A = os.path.dirname(os.path.abspath(__file__)); EV = json.load(open(os.path.join(A, 'eventos_som.json')))
SUF = sys.argv[1] if len(sys.argv) > 1 else 'hibrido'
x, sr = sf.read(os.path.join(A, '..', 'stems', f'ep01_efeitos_{SUF}.wav')); x = x.mean(1); w = int(0.005 * sr)
e = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(w) / w, 'same')) + 1e-9)
ev = {'abertura · borda': EV['abertura']['borda'], 'abertura · água': EV['abertura']['agua'], 'abertura · leito': EV['abertura']['leito'], 'encaixe da chapa': 23.6,
      'comporta do dique': EV['dique']['comporta'], 'retomada · água': EV['retomada']['agua'], 'experimento · água': EV['experimento']['agua'],
      **{f'pouso de contêiner {i + 1}': t for i, t in enumerate(EV['pousos'])}, 'ruptura': EV['avaria']['rasgo'], 'divisórias': EV['avaria']['divisorias'],
      'conclusão · água': EV['conclusao']['agua']}
res = {}
for k, t in ev.items():
    a, b = int((t - 0.15) * sr), int((t + 0.25) * sr); d = e[a + int(0.02 * sr):b] - e[a:b - int(0.02 * sr)]
    res[k] = dict(evento_s=round(t, 3), ataque_s=round((a + int(np.argmax(d)) + int(0.02 * sr)) / sr, 3), desvio_ms=round(((a + int(np.argmax(d)) + int(0.02 * sr)) / sr - t) * 1000))
json.dump(res, open(os.path.join(A, f'sincronia_{SUF}.json'), 'w'), ensure_ascii=False, indent=1)
for k, v in res.items(): print(f'{k:28s} {v["desvio_ms"]:+5d} ms')
