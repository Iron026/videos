"""Mapa objetivo de uma gravação (não substitui a escuta): envelope RMS, transientes mais fortes,
trechos estáveis (para camas) e centroide espectral por trecho. Uso: python3 mapa_amostra.py <id> [<id> ...]"""
import sys, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import amostras as AM

def mapa(i, jan=0.05):
    a = AM.carregar(i).mean(1); sr = AM.SR; w = int(jan * sr); n = len(a) // w
    q = a[:n * w].reshape(n, w); rms = 20 * np.log10(np.sqrt((q ** 2).mean(1)) + 1e-9)
    X = np.abs(np.fft.rfft(q * np.hanning(w), axis=1)); f = np.fft.rfftfreq(w, 1 / sr)
    cen = (X * f).sum(1) / (X.sum(1) + 1e-9); grave = 20 * np.log10((X[:, f < 150] ** 2).sum(1) ** 0.5 / ((X ** 2).sum(1) ** 0.5 + 1e-9) + 1e-9)
    on = np.maximum(0, np.diff(rms, prepend=rms[0]))
    picos = [k for k in np.argsort(-on) if rms[k] > rms.max() - 18][:40]; sel = []
    for k in picos:
        if all(abs(k - j) > int(0.6 / jan) for j in sel): sel.append(k)
    sel = sorted(sel[:8])
    blocos = []
    L = int(3.0 / jan)
    for k in range(0, n - L, L // 2):
        r = rms[k:k + L]; blocos.append((np.std(r), k * jan, r.mean(), np.median(cen[k:k + L])))
    blocos.sort()
    print(f'== {i} · {AM.FONTES.get(i, {}).get("titulo", "")} · {len(a) / sr:.1f} s · pico {rms.max():.1f} dB · mediana {np.median(rms):.1f} dB')
    print('   transientes (t s, salto dB, nível, centroide Hz, grave<150 dB):', [(round(k * jan, 2), round(on[k], 1), round(rms[k], 1), int(cen[k]), round(grave[k], 1)) for k in sel])
    print('   trechos estáveis 3 s (início, desvio dB, nível, centroide):', [(round(t, 1), round(s, 1), round(m, 1), int(c)) for s, t, m, c in blocos[:5]])
    perfil = [(round(k * jan, 0), round(rms[k:k + int(2 / jan)].mean(), 0), int(np.median(cen[k:k + int(2 / jan)]))) for k in range(0, n, int(2 / jan))]
    print('   perfil a cada 2 s (t, dB, centroide):', perfil[:40])

if __name__ == '__main__':
    for x in sys.argv[1:]: mapa(int(x) if x.isdigit() else x)
