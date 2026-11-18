"""Áudio do Episódio 01 (versão de revisão): narração real Will - Deep + efeitos sonoros sintetizados aqui
(originais, sincronizados com os eventos das cenas) + trilha ORIGINAL (pads e arpejo gerados por código, sem
amostras de terceiros). A trilha e os efeitos abaixam sob a voz (ducking). Saída: episodio/audio_ep01.wav (48 kHz estéreo)
e audio_ep01.json (eventos). A loudness final (−14 LUFS / −1,5 dBTP) é aplicada na montagem."""
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000; DUR = 169.5; N = int(DUR * SR); A = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(23)
def bp(x, lo, hi, o=4): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=4): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=4): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / r)
def db(v): return 10 ** (v / 20)
L = np.zeros(N); R = np.zeros(N); MUS = np.zeros((N, 2))
def por(t, x, g=1.0, pan=0.5):
    i = int(t * SR); j = min(N, i + len(x));
    if j <= i: return
    L[i:j] += x[:j - i] * g * (1 - pan) * 2 ** 0.5; R[i:j] += x[:j - i] * g * pan * 2 ** 0.5
def janela(a, b, sub=0.3, desce=0.3):
    t = np.arange(N) / SR; return np.clip((t - a) / sub, 0, 1) * np.clip((b - t) / desce, 0, 1)
def ruido(n): return rng.standard_normal(n)
def clank(f0=523, dur=1.4, brilho=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    c = sum(a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-t * d) for a, m, d in ((1, 1, 3.2), (0.7, 2.27, 4.5), (0.5, 4.23, 6), (0.3, 6.5, 8)))
    return (c + 0.6 * brilho * hp(ruido(n), 2000) * env(n, 0.001, 0.02)) * env(n, 0.002, 0.9 * dur / 1.4)
def whoosh(dur=0.55):
    n = int(dur * SR); return bp(ruido(n), 300, 5000) * np.sin(np.linspace(0, np.pi, n)) ** 2
def thud(f=48, dur=0.6):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2.3 * f * t)) * env(n, 0.004, 0.16) + 0.3 * lp(ruido(n), 300) * env(n, 0.01, 0.2)
def splash(dur=0.9, k=1.0):
    n = int(dur * k * SR); t = np.arange(n) / SR
    return hp(ruido(n), 900 / k) * env(n, 0.004, 0.18 * k) + 0.6 * bp(ruido(n), 300 / k, 2500 / k) * env(n, 0.03, 0.35 * k) + np.sin(2 * np.pi * (70 / k - 25 * t) * t) * env(n, 0.003, 0.22 * k)
def brilho(dur=1.2, f=1318.5):
    n = int(dur * SR); t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * m * t) for a, m in ((1, 1), (0.5, 1.5), (0.35, 2))) * env(n, 0.02, dur / 3)
def mais(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o
def tique(f=2200, dur=0.08):
    n = int(dur * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.015)
def motor(a, b, f=96, g=-31):
    t = np.arange(N) / SR; ff = f + 4 * np.sin(2 * np.pi * 0.7 * t)
    m = lp(np.sign(np.sin(2 * np.pi * np.cumsum(ff) / SR)) * 0.5 + 0.3 * np.sin(4 * np.pi * np.cumsum(ff) / SR), 900)
    return m * janela(a, b, 0.3, 0.3) * db(g)
def amb_mar(a, b, g=-34, corte=700):
    m = lp(ruido(N), corte) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * np.arange(N) / SR)) * janela(a, b, 0.4, 0.4) * db(g); return m
def sub(a, b, g=-26):
    return lp(ruido(N), 320) * janela(a, b, 0.2, 0.3) * db(g)

ev = {}
# 0–4,40 · plano 1 aprovado (r2): efeitos já sincronizados com a queda (raspagem, impacto em câmera lenta, bolhas, leito)
r2, sr2 = sf.read(os.path.join(A, '..', 'animatic', 'audio_animatic_r2.wav')); assert sr2 == SR
n1 = int(4.40 * SR); fade = np.clip((4.40 - np.arange(n1) / SR) / 0.25, 0, 1)
L[:n1] += r2[:n1, 0] * fade * 0.85; R[:n1] += r2[:n1, 1] * fade * 0.85
# 4,40–15,10 · o gigante: mar aberto, vento, apito grave do navio
m = amb_mar(4.3, 15.2, -33); L += m; R += np.roll(m, 700)
n = int(2.2 * SR); t = np.arange(n) / SR
apito = sum(a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 5 * t)) for a, f in ((1, 73.4), (0.6, 146.8), (0.35, 220.2), (0.2, 293.6)))
por(5.0, lp(apito, 1200) * np.minimum(1, t / 0.25) * np.clip((2.2 - t) / 0.5, 0, 1), db(-24)); ev['apito'] = 5.0
mo = motor(4.4, 15.1, f=38, g=-35); L += mo; R += mo                                  # máquinas do navio navegando
proa = bp(ruido(N), 250, 3500) * janela(11.0, 13.5, 0.3, 0.4) * db(-25); L += proa; R += proa * 0.8  # onda de proa
por(13.4, whoosh(1.4), db(-27))
por(4.40, whoosh(), db(-28))
# 15,10–30,30 · estaleiro: ambiente, motor do pórtico, encaixe (23,60), solda, chapas chegando ao casco
a_ = lp(ruido(N), 1200) * janela(15.1, 30.4, 0.3, 0.4) * db(-36); L += a_; R += np.roll(a_, 1500)
mo = motor(15.1, 21.7, g=-32) + motor(21.7, 23.6, g=-29) + motor(17.2, 19.0, f=150, g=-27); L += mo; R += mo
por(15.10, whoosh(), db(-28)); por(23.60, clank(), db(-13)); ev['encaixe'] = 23.60
# solda (refinamento): arco elétrico = zumbido de 100/200 Hz modulado + crepitar denso nos cordões; faíscas chiando
for (ta, tb, g_) in ((23.75, 24.55, -25), (24.68, 25.25, -25), (24.0, 24.7, -31), (24.85, 25.4, -31), (24.9, 26.4, -34), (25.1, 26.4, -35)):
    n = int((tb - ta) * SR); t = np.arange(n) / SR
    zum = (np.sign(np.sin(2 * np.pi * 100 * t)) * 0.4 + np.sin(2 * np.pi * 200 * t) * 0.3) * (0.6 + 0.4 * rng.random(n).round(0))
    crep = hp(ruido(n), 1800) * (rng.random(n) < 0.012).astype(float).cumsum() % 2
    arco = (bp(zum, 120, 2500) * 0.5 + crep * 0.8) * np.minimum(1, t / 0.03) * np.clip((tb - ta - t) / 0.08, 0, 1)
    por(ta, arco, db(g_), pan=0.6)
for t0 in np.arange(23.75, 26.4, 0.05):
    if rng.random() < 0.45: por(float(t0), hp(ruido(int(0.09 * SR)), 3200) * env(int(0.09 * SR), 0.001, 0.05), db(-31), pan=0.4 + 0.4 * rng.random())
for i, t0 in enumerate(np.linspace(25.95, 28.4, 9)): por(float(t0), clank(380 + 40 * (i % 3), 0.7, 0.5), db(-27), pan=0.35 + 0.3 * (i % 2))
# 30,30–41,55 · corte ilustrativo: deslize da proa, brilho na revelação
sl = lp(ruido(int(1.8 * SR)), 260) * np.sin(np.linspace(0, np.pi, int(1.8 * SR))); por(33.15, sl, db(-24)); por(33.6, brilho(1.6), db(-30))
por(37.0, brilho(0.9, 1567.98), db(-33)); por(39.2, brilho(0.9, 1174.66), db(-33))
a_ = lp(ruido(N), 900) * janela(30.3, 41.6, 0.3, 0.3) * db(-40); L += a_; R += a_
# 41,55–48,00 · dique seco: água entrando pela comporta (forte no início), enchimento contínuo; casco deixa os picadeiros (46,10)
jorro_d = bp(ruido(N), 180, 2600) * (janela(41.6, 44.0, 0.15, 0.6) * db(-22) + janela(43.6, 48.0, 0.4, 0.4) * db(-31)); L += jorro_d; R += jorro_d * 0.9
m = amb_mar(41.5, 48.2, -36, 900); L += m; R += np.roll(m, 500)
n = int(0.8 * SR); t = np.arange(n) / SR
range_ = (lp(ruido(n), 900) * np.exp(-t / 0.25) + 0.6 * np.sin(2 * np.pi * (140 - 60 * t) * t) * env(n, 0.01, 0.3))
por(46.10, range_, db(-24)); por(46.15, thud(42, 0.8), db(-27)); ev['flutua'] = 46.10
# 48,00–74,85 · seção submersa: ambiente abafado, setas, empuxo, volume deslocado, peso
s_ = sub(48.0, 74.9); L += s_; R += s_
n = int(1.2 * SR); mergulho = bp(ruido(n), 200, 2500) * np.sin(np.linspace(0, np.pi, n)) ** 2; por(49.0, mergulho, db(-22))   # câmera mergulha
n = int(2.5 * SR); t = np.arange(n) / SR; mapa = np.sin(2 * np.pi * 110 * t) * np.sin(np.pi * t / 2.5) ** 2; por(50.75, mapa, db(-30))
for i, t0 in enumerate(np.linspace(50.9, 53.2, 10)): por(float(t0), tique(1700 + 90 * i), db(-31), pan=0.3 + 0.4 * (i % 2))
por(57.35, thud(70, 0.35), db(-31), pan=0.2); por(57.35, thud(70, 0.35), db(-31), pan=0.8)          # os dois lados empurram juntos
por(58.35, whoosh(0.9), db(-31)); por(58.6, tique(1200, 0.12), db(-31)); por(59.8, whoosh(1.6), db(-29)); por(61.6, mais(brilho(1.4, 880.0), 0.5 * thud(60, 0.8)), db(-24)); ev['empuxo'] = 61.6
n = int(2.3 * SR); t = np.arange(n) / SR; enche = np.sin(2 * np.pi * (330 * t + 60 * t * t)) * np.sin(np.pi * t / 2.3) ** 2; por(63.2, enche, db(-32))
por(65.6, brilho(1.6, 1046.5), db(-28)); por(67.2, tique(900, 0.15), db(-28)); por(71.15, mais(brilho(1.2, 698.46), 0.5 * thud(52, 0.8)), db(-25))
# 74,85–83,85 · o bloco em câmera lenta e o leito (82,12)
s_ = sub(76.1, 83.9, -24); L += s_; R += s_
# retomada (refinamento): o mesmo bloco é arrastado no cais e cai; impacto em 76,13; a câmera lenta começa logo depois
n = int(0.42 * SR); por(74.88, bp(ruido(n), 300, 2400) * env(n, 0.02, 0.15), db(-24), pan=0.6)        # arrasto aço × concreto
por(75.3, whoosh(0.8), db(-30)); t_imp = 76.13
por(t_imp, splash(1.6, 1.3), db(-15), pan=0.55); por(t_imp + 0.05, thud(46, 0.9), db(-22)); ev['retomada_agua'] = t_imp
lento = lp(ruido(int(6.0 * SR)), 140) * np.linspace(0.4, 1, int(6.0 * SR)); por(76.15, lento, db(-26))
for k in range(10): por(t_imp + 0.3 + 0.16 * k, bp(ruido(int(0.06 * SR)), 500, 1600) * env(int(0.06 * SR), 0.004, 0.04), db(-33), pan=0.4 + 0.05 * k)   # bolhas
por(82.12, thud(40, 0.9), db(-12)); ev['bloco_leito'] = 82.12
por(82.15, lp(ruido(int(1.2 * SR)), 900) * env(int(1.2 * SR), 0.02, 0.4), db(-24))   # sedimento
# 83,85–94,55 · cubo de aço maciço afunda; volume deslocado do casco; forças
s_ = sub(83.85, 94.6, -27); L += s_; R += s_
por(84.2, tique(1500, 0.1), db(-30)); t_ag = 85.6 + (2 * 2.0 / 9.81) ** 0.5
por(t_ag, splash(1.4, 1.7), db(-15), pan=0.35); por(t_ag + 0.02, splash(1.2, 1.4), db(-17), pan=0.65); ev['experimento_agua'] = round(t_ag, 2)
por(t_ag + 0.2, lp(ruido(int(2.6 * SR)), 180) * np.linspace(1, 0, int(2.6 * SR)), db(-22)); por(t_ag + 1.2, thud(38, 1.0), db(-28))
por(84.6, brilho(1.4, 1318.5), db(-31)); por(90.0, brilho(1.6, 1046.5), db(-28))
# 94,55–117,20 · porto: ambiente, portêineres, três pousos (101,60 · 102,95 · 104,45), lotes do time-lapse
a_ = lp(ruido(N), 1500) * janela(94.5, 134.1, 0.4, 0.4) * db(-37); L += a_; R += np.roll(a_, 1800)
m = amb_mar(94.5, 134.1, -36, 600); L += m; R += np.roll(m, 900)
for (tl, pan) in ((101.60, 0.5), (102.95, 0.3), (104.45, 0.7)):
    mo = motor(tl - 4.0, tl, f=110, g=-33); L += mo * (1 - pan); R += mo * pan
    por(tl, clank(392, 1.2), db(-15), pan=pan)
ev['pousos'] = [101.60, 102.95, 104.45]
for tl in (105.45, 106.95, 108.45, 110.15, 111.85, 113.55, 115.05):
    for k in range(6): por(tl + 0.15 * k, clank(330 + 30 * k, 0.5, 0.4), db(-31), pan=0.3 + 0.08 * k)
    por(tl + 0.45, thud(45, 0.5), db(-30))
# 117,20–123,65 · calado: cota sobe (tom ascendente)
n = int(2.0 * SR); t = np.arange(n) / SR; sweep = np.sin(2 * np.pi * (400 * t + 300 * t * t)) * np.sin(np.pi * t / 2.0) ** 2
por(118.9, sweep, db(-34)); por(122.55, brilho(1.0, 1318.5), db(-30))
# 123,65–134,00 · marcas: realces
por(125.9, brilho(0.8, 1567.98), db(-32)); por(127.6, whoosh(1.2), db(-27)); [por(130.5 + 0.55 * i, tique(1500 + 150 * i, 0.1), db(-29)) for i in range(5)]
# 134,00–154,60 · avaria: rasgo (136,6), água entrando, hipótese grave (tensão), divisórias (151,05)
m = amb_mar(134.0, 154.7, -34); L += m; R += np.roll(m, 600)
n = int(0.9 * SR); crunch = lp(ruido(n), 1800) * env(n, 0.002, 0.25) + 0.6 * clank(180, 0.9, 0.2)[:n]
por(134.9, crunch, db(-16)); ev['avaria'] = 134.9
gorgolejo = bp(ruido(N), 150, 1200) * janela(135.0, 137.2, 0.2, 0.3) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * np.arange(N) / SR)) * db(-24); L += gorgolejo; R += gorgolejo
jorro = bp(ruido(N), 250, 2200) * janela(136.9, 145.8, 0.3, 1.0) * db(-27); L += jorro; R += jorro * 0.8
n = int(2.8 * SR); t = np.arange(n) / SR; drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 58.3 * t)) * np.sin(np.pi * t / 2.8)
por(147.9, drone, db(-24)); [por(147.9 + 0.45 * i, tique(700 - 60 * i, 0.12), db(-30)) for i in range(5)]; por(151.05, mais(clank(523, 1.6, 0.6) * 0.6, brilho(1.2, 1046.5)), db(-24)); ev['divisorias'] = 151.05
# 154,60–166,30 · conclusão; 166,25 assinatura
m = amb_mar(154.5, DUR + 0.5, -35); L += m; R += np.roll(m, 800)
t_c = 155.2 + (4.0 / 9.81) ** 0.5; por(t_c, splash(1.4, 1.8), db(-17)); por(t_c + 0.2, lp(ruido(int(2.4 * SR)), 180) * np.linspace(1, 0, int(2.4 * SR)), db(-24))
por(159.6, brilho(2.0, 1046.5), db(-28)); por(161.4, mais(brilho(1.4, 783.99), 0.4 * thud(50, 0.8)), db(-27))
# refinamento: sem tela nem som de assinatura; o vídeo termina no último plano do navio (fim musical natural abaixo)
ev['fim'] = DUR

# ------------------------------------------------------------------ trilha original (pads + arpejo), em Ré maior
NOTAS = {'D': 146.83, 'E': 164.81, 'F#': 185.0, 'G': 196.0, 'A': 220.0, 'B': 246.94, 'C': 130.81}
def acorde(raiz, menor=False):
    f = NOTAS[raiz]; return [f, f * (2 ** ((3 if menor else 4) / 12)), f * 1.5]
SECOES = [(0.0, 15.1, [('B', 1), ('G', 0), ('D', 0), ('A', 0)]), (15.1, 48.0, [('D', 0), ('A', 0), ('B', 1), ('G', 0)]),
          (48.0, 94.55, [('E', 1), ('C', 0), ('G', 0), ('D', 0)]), (94.55, 134.0, [('D', 0), ('G', 0), ('A', 0), ('B', 1)]),
          (134.0, 154.6, [('B', 1), ('F#', 1), ('G', 0), ('E', 1)]), (154.6, 166.6, [('G', 0), ('D', 0), ('A', 0)]), (166.6, DUR, [('D', 0)])]   # resolve em Ré no fim
DUR_AC = 4.0
for (a, b, prog) in SECOES:
    t0 = a; i = 0
    while t0 < b - 0.05:
        t1 = min(b, t0 + DUR_AC); n = int((t1 - t0 + 1.2) * SR); t = np.arange(n) / SR
        r, mn = prog[i % len(prog)]; fs = acorde(r, mn)
        voz = np.zeros(n)
        for f in fs + [fs[0] / 2]:
            for det in (-0.12, 0.12):
                ph = 2 * np.pi * f * (1 + det / 100) * t; voz += 0.5 * (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.25 + np.sin(ph) * 0.35
        e = np.minimum(1, t / 0.9) * np.clip((t1 - t0 + 1.2 - t) / 1.2, 0, 1)
        pad = lp(voz, 900) * e * db(-31)
        i0 = int(t0 * SR); j0 = min(N, i0 + n); MUS[i0:j0, 0] += pad[:j0 - i0]; MUS[i0:j0, 1] += np.roll(pad, 240)[:j0 - i0]
        t0 = t1; i += 1
# arpejo suave nos trechos de ação (carregamento e conclusão), 92 bpm em colcheias
for (a, b) in ((97.6, 117.0), (154.6, 166.0)):
    passo = 60 / 92 / 2; k = 0; t0 = a
    while t0 < b:
        sec = next(s for s in SECOES if s[0] <= t0 < s[1]); r, mn = sec[2][int((t0 - sec[0]) // DUR_AC) % 4]
        f = acorde(r, mn)[k % 3] * 2; n = int(0.5 * SR); t = np.arange(n) / SR
        nota = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(n, 0.004, 0.18) * db(-33) * min(1, (t0 - a) / 2.0)
        i0 = int(t0 * SR); j0 = min(N, i0 + n); MUS[i0:j0, 0] += nota[:j0 - i0] * (0.4 + 0.2 * (k % 2)); MUS[i0:j0, 1] += nota[:j0 - i0] * (0.6 - 0.2 * (k % 2))
        t0 += passo; k += 1

# fim natural: o último acorde (Ré) soa e se apaga com o plano final; efeitos e mar descem juntos
fim = np.clip((DUR - 0.05 - np.arange(N) / SR) / 2.6, 0, 1) ** 1.6
MUS *= fim[:, None]; L *= fim; R *= fim

# ------------------------------------------------------------------ voz + ducking (trilha −7 dB e efeitos −4 dB sob a fala)
voz, sr = sf.read(os.path.join(A, '..', 'voz', 'narracao_ep01', 'trabalho', 'narracao_48k.wav')); assert sr == SR
v = np.zeros(N); v[:min(N, len(voz))] = voz[:N]
# CÓPIA DE MONTAGEM: a fala de assinatura ("De Olho no Invisível. O invisível ganha forma.", 166,56–169,86) fica de fora;
# o MP3 original e o WAV de trabalho não são alterados
corte = int(166.36 * SR); v[corte:] = 0.0; rampa = int(0.06 * SR); v[corte - rampa:corte] *= np.linspace(1, 0, rampa)
w = int(0.05 * SR); rms = np.sqrt(np.convolve(v ** 2, np.ones(w) / w, 'same'))
fala = lp((rms > db(-42)).astype(float), 3.0, o=2); fala = np.clip(fala, 0, 1)
MUS *= (1 - (1 - db(-7)) * fala)[:, None]; L *= 1 - (1 - db(-4)) * fala; R *= 1 - (1 - db(-4)) * fala
mix = np.stack([L + v + MUS[:, 0], R + v + MUS[:, 1]], 1)
mix *= min(1.0, db(-1.0) / np.abs(mix).max())
sf.write(os.path.join(A, 'audio_ep01.wav'), mix, SR, subtype='PCM_24')
json.dump(dict(eventos=ev, duracao=DUR, pico_dbfs=round(20 * np.log10(np.abs(mix).max()), 2), trilha='original (sintetizada neste script)'),
          open(os.path.join(A, 'audio_ep01.json'), 'w'), indent=1)
print('ok', round(20 * np.log10(np.abs(mix).max()), 2))
