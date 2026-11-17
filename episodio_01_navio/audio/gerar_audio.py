"""Trilha do Episódio 01: efeitos sonoros e música 100% sintetizados aqui (sem material de terceiros),
sincronizados aos eventos de projeto/src/roteiro.js, mixados com a narração.
Saída: audio/mix_bruto.wav (48 kHz estéreo). A normalização de loudness é feita no FFmpeg (montar.sh)."""
import os, json, math
import numpy as np, soundfile as sf

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
SR = 48000; DUR = 75.0; N = int(SR * DUR)
rng = np.random.default_rng(2026)

def env_adsr(n, a, r, curva=3.0):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) * curva / max(r, 1e-4)); return e
def passa_baixa(x, fc):
    # filtro de 1 polo aplicado duas vezes (suave)
    from scipy.signal import lfilter
    a = math.exp(-2 * math.pi * fc / SR); y = x
    for _ in range(2): y = lfilter([1 - a], [1, -a], y)
    return y
def passa_alta(x, fc): return x - passa_baixa(x, fc)
def ruido(n): return rng.standard_normal(n).astype(np.float64)
def por(buf, ini, sinal, ganho=1.0, pan=0.0):
    i0 = int(ini * SR); i1 = min(N, i0 + len(sinal))
    if i1 <= i0 or i0 < 0: return
    l = math.cos((pan + 1) * math.pi / 4); r = math.sin((pan + 1) * math.pi / 4)
    buf[i0:i1, 0] += sinal[:i1 - i0] * ganho * l * 1.414; buf[i0:i1, 1] += sinal[:i1 - i0] * ganho * r * 1.414

# ---------- sons básicos ----------
def whoosh(d, f0=300, f1=2400, sobe=True):
    n = int(d * SR); t = np.arange(n) / SR; x = ruido(n)
    # varredura de filtro passa-banda aproximada por diferença de passa-baixas variando em blocos
    out = np.zeros(n); bl = 1024
    for i in range(0, n, bl):
        f = f0 + (f1 - f0) * ((i / n) if sobe else (1 - i / n))
        seg = x[max(0, i - 4096):i + bl]
        y = passa_baixa(seg, f * 1.6) - passa_baixa(seg, f * 0.5)
        out[i:i + bl] = y[-len(out[i:i + bl]):]
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    return out * e / (np.abs(out).max() + 1e-9)
def respingo(d=1.6):
    n = int(d * SR); x = ruido(n); e = env_adsr(n, 0.008, d, 4.5)
    y = passa_alta(x, 600) * e + 0.6 * passa_baixa(x, 300) * env_adsr(n, 0.01, 0.5, 5)
    # gotas
    for _ in range(40):
        i = int(rng.uniform(0.05, d * 0.8) * SR); m = int(0.03 * SR)
        if i + m < n: y[i:i + m] += np.sin(2 * np.pi * rng.uniform(900, 2600) * np.arange(m) / SR) * np.exp(-np.arange(m) / (0.006 * SR)) * 0.35
    return y / np.abs(y).max()
def baque(f=55, d=1.2):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t * (1 + 0.6 * np.exp(-t * 8))) * np.exp(-t * 4.5) + 0.4 * passa_baixa(ruido(n), 200) * np.exp(-t * 7)
    return y / np.abs(y).max()
def clank(f=180):
    n = int(0.5 * SR); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (14 + 6 * k)) for k, a in [(1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)])
    y += 0.5 * passa_alta(ruido(n), 2000) * np.exp(-t * 60)
    return y / np.abs(y).max()
def tom(f0, f1, d, tipo='sobe'):
    n = int(d * SR); t = np.arange(n) / SR; f = f0 + (f1 - f0) * (t / d) ** 0.7
    fase = 2 * np.pi * np.cumsum(f) / SR
    y = (np.sin(fase) + 0.3 * np.sin(2 * fase)) * env_adsr(n, 0.03, d, 2.5)
    return y / np.abs(y).max()
def clique():
    n = int(0.12 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 1450 * t) * np.exp(-t * 55) + 0.5 * np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 80)
    return y / np.abs(y).max()
def sino(f):
    n = int(2.6 * SR); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.2 + k)) for k, a in [(1, 1), (2, 0.35), (3.01, 0.2), (4.2, 0.08)])
    return y * env_adsr(n, 0.005, 2.6, 0.5) / 1.6
def agua_corrente(d):
    n = int(d * SR); x = ruido(n); t = np.arange(n) / SR
    y = passa_baixa(passa_alta(x, 250), 2500) * (0.7 + 0.3 * np.sin(2 * np.pi * 3.3 * t + np.sin(t * 7)))
    e = np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.8)
    return y * e / np.abs(y).max()
def rangido(d):
    n = int(d * SR); t = np.arange(n) / SR; f = 70 + 25 * np.sin(2 * np.pi * 0.7 * t) + 10 * np.sin(2 * np.pi * 2.3 * t)
    fase = 2 * np.pi * np.cumsum(f) / SR; y = np.sign(np.sin(fase)) * 0.3 + np.sin(fase * 3.02) * 0.4
    y = passa_baixa(y, 900) * np.sin(np.pi * t / d) ** 2
    return y / np.abs(y).max()

# ---------- instantes (mesmas fórmulas de projeto/src) ----------
T = dict(quedaBloco=3.25, fatiaInicio=4.25, corteNavio0=8.25, transicoes=[19.75, 27.75, 55.75, 62.75], entradaDescida=28.45, cartaoFinal=70.3)
g = 9.81 * 2.2; v0 = 14; y0 = 26
tImp = T['quedaBloco'] + (-v0 + math.sqrt(v0 * v0 + 2 * g * y0)) / g
vI = v0 + g * (tImp - T['quedaBloco']); fundo = -34 + 1.3
tP = next(tImp + d for d in np.arange(0, 15, 0.002) if -(9.5 * d + (vI - 9.5) * 0.35 * (1 - math.exp(-d / 0.35))) <= fundo)

def mulberry32(seed):
    s = seed & 0xFFFFFFFF
    def imul(a, b): return (a * b) & 0xFFFFFFFF
    def r():
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF; t = s
        t = imul(t ^ (t >> 15), t | 1)
        t = (t ^ ((t + imul(t ^ (t >> 7), t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return r
r = mulberry32(7); pousos = []
extras = {2: 47.7, 3: 49.6, 4: 51.5}
for camada in range(5):
    for bi in range(9):
        for f in range(12):
            r()  # cor
            if camada in extras:
                ordem = (bi * 12 + f) / (9 * 12); pousos.append((extras[camada] + 0.55 + ordem * 1.5 + r() * 0.12, bi))

# ---------- montagem ----------
sfx = np.zeros((N, 2)); amb = np.zeros((N, 2)); mus = np.zeros((N, 2))
t = np.arange(N) / SR
# ambiente de oceano (ondas lentas), mais abafado nas cenas técnicas
base = ruido(N)
mar = passa_baixa(base, 700) * (0.55 + 0.45 * np.sin(2 * np.pi * t / 7.3) ** 2) + 0.25 * passa_baixa(passa_alta(ruido(N), 1500), 5000) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 5.1 + 1) ** 4)
mar /= np.abs(mar).max()
abert = np.interp(t, [0, 4.2, 5.4, 62.6, 63.2, 70.3, 75], [1, 1, 0.45, 0.45, 0.8, 0.8, 0.25])
amb[:, 0] = mar * abert * 0.22; amb[:, 1] = np.roll(mar, 900) * abert * 0.22

por(sfx, 0.0, whoosh(2.4, 250, 1800), 0.28, -0.2)
por(sfx, T['quedaBloco'] + 0.2, whoosh(0.9, 900, 3000), 0.18, 0.3)
por(sfx, tImp - 0.01, respingo(1.8), 0.55, 0.25)
por(sfx, T['fatiaInicio'], whoosh(1.4, 400, 3500), 0.32, 0.0)
por(sfx, tP, baque(48, 1.4), 0.5, 0.2)
por(sfx, T['corteNavio0'], whoosh(1.8, 300, 2800), 0.3, -0.1)
por(sfx, T['corteNavio0'] + 1.2, clank(120), 0.18, 0.0)
for tc in T['transicoes']: por(sfx, tc - 0.3, whoosh(0.75, 600, 2600, sobe=False), 0.22, 0.0)
por(sfx, T['entradaDescida'] + 0.25, baque(40, 1.8), 0.35, 0.0)
por(sfx, T['entradaDescida'] + 0.35, respingo(2.2) * 0.6 + 0, 0.35, 0.0)
por(sfx, 32.1, tom(400, 700, 0.6), 0.10, 0.0)
por(sfx, 33.8, tom(180, 360, 1.1), 0.26, 0.15)     # empuxo (sobe)
por(sfx, 41.6, tom(360, 170, 1.1), 0.26, -0.15)    # peso (desce)
for tc in [36.7, 42.0, 47.6, 59.2, 63.5, 66.17]: por(sfx, tc, clique(), 0.16, 0.0)
for tp, bi in pousos:
    por(sfx, tp, clank(rng.uniform(140, 260)), 0.07, (bi - 4) / 6)
for (t0, t1, pan) in [(56.6, 58.6, -0.3), (59.0, 61.3, 0.2), (59.2, 61.5, -0.1), (59.6, 62.0, 0.35), (59.8, 62.2, -0.35)]:
    por(sfx, t0 - 0.1, agua_corrente(t1 - t0 + 0.6), 0.16, pan)
por(sfx, 60.2, rangido(2.6), 0.16, 0.0)
por(sfx, T['cartaoFinal'] + 0.35, sino(659.25), 0.22, -0.1)
por(sfx, 72.65, sino(987.77), 0.18, 0.1)

# música: pad original (Ré maior), acordes a cada 6 s, timbre suave
acordes = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 69]]
def hz(m): return 440 * 2 ** ((m - 69) / 12)
dur_ac = 6.0
for k in range(int(DUR / dur_ac) + 1):
    ac = acordes[k % 4]; n = int((dur_ac + 2.0) * SR); tt = np.arange(n) / SR
    env = np.minimum(1, tt / 1.6) * np.minimum(1, np.maximum(0, (dur_ac + 2.0 - tt)) / 2.0)
    sig = np.zeros(n)
    for m in ac:
        for det in (-0.07, 0.07):
            sig += np.sin(2 * np.pi * hz(m - 12) * (1 + det / 100) * tt) * 0.5 + 0.18 * np.sin(2 * np.pi * hz(m) * (1 + det / 100) * tt)
    baixo = np.sin(2 * np.pi * hz(ac[0] - 24) * tt) * 0.8
    sig = (sig + baixo) * env
    por(mus, k * dur_ac - 1.0, sig / 9.0, 1.0, 0.0)
# pulso suave (marimba sintética) para dar ritmo nas cenas de explicação
for k, bt in enumerate(np.arange(13.0, 69.0, 60 / 92 * 2)):
    m = acordes[int(bt // dur_ac) % 4][k % 4] + 12
    n = int(0.6 * SR); tt = np.arange(n) / SR
    nota = np.sin(2 * np.pi * hz(m) * tt) * np.exp(-tt * 7) + 0.3 * np.sin(2 * np.pi * hz(m) * 4 * tt) * np.exp(-tt * 20)
    por(mus, bt, nota, 0.05, 0.3 if k % 2 else -0.3)
mus *= np.interp(t, [0, 1.0, 69.5, 70.3, 74.0, 75], [0, 1, 1, 1.25, 1.0, 0])[:, None]

# narração e ducking
narr, sr_n = sf.read(os.path.join(RAIZ, 'narracao/narracao.wav'), dtype='float64')
narr = np.interp(np.arange(N) / SR, np.arange(len(narr)) / sr_n, narr)
narr = narr / (np.abs(narr).max() + 1e-9) * 0.85
envn = np.convolve(np.abs(narr), np.ones(int(0.05 * SR)) / int(0.05 * SR), mode='same')
fala = np.clip(envn / 0.04, 0, 1)
fala = np.clip(passa_baixa(fala, 3) * 1.6, 0, 1)  # envelope suavizado da fala
duck = 1 - 0.55 * np.clip(fala, 0, 1)
mix = np.zeros((N, 2))
mix += narr[:, None] * 1.0
mix += sfx * (1 - 0.25 * np.clip(fala, 0, 1))[:, None]
mix += amb * duck[:, None]
mix += mus * 0.55 * duck[:, None]
# fade de entrada/saída
mix *= np.interp(t, [0, 0.05, 74.6, 75.0], [0, 1, 1, 0])[:, None]
pico = np.abs(mix).max(); mix = mix / pico * 0.89
sf.write(os.path.join(AQUI, 'mix_bruto.wav'), mix.astype(np.float32), SR, subtype='PCM_24')
json.dump({'impacto_bloco': tImp, 'pouso_bloco': tP, 'pousos_conteineres': len(pousos)}, open(os.path.join(AQUI, 'eventos.json'), 'w'), indent=1)
print('ok', round(tImp, 3), round(tP, 3), len(pousos))
