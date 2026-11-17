"""Áudio do animatic (19,5 s, 48 kHz estéreo). Narração: SOMENTE a amostra real Will - Deep na assinatura
(plano 4); nos planos 1–3 a narração definitiva está pendente (só legendas). Efeitos sonoros originais,
sintetizados aqui, sincronizados com os eventos da animação. Saída: animatic/audio_animatic.wav
"""
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000; DUR = 19.5; N = int(DUR * SR); AQUI = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(11)
T_AGUA, T_FUNDO, T_ENCAIXE, T_VOZ = 3.13, 3.76, 14.40, 15.20     # eventos (s, tempo global)


def bp(x, lo, hi, o=4): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=4): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=4): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / r); return e
def db(v): return 10 ** (v / 20)
def por(buf, t, x, g=1.0):
    i = int(t * SR); j = min(N, i + len(x)); buf[i:j] += x[:j - i] * g
def janela(a, b, sub=0.3, desce=0.3):
    t = np.arange(N) / SR; return np.clip((t - a) / sub, 0, 1) * np.clip((b - t) / desce, 0, 1)

L = np.zeros(N); R = np.zeros(N)
ruido = rng.standard_normal(N)
# ambiente do cais (marulho) no plano 1, abafado após o mergulho da câmera
mar = lp(ruido, 700) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * np.arange(N) / SR)) * janela(0, 5.6, 0.4, 0.4)
L += mar * db(-34); R += np.roll(mar, 900) * db(-34)
# bloco raspando no concreto (1,40–2,30 s)
n = int(0.9 * SR); rasp = bp(rng.standard_normal(n), 700, 3200) * np.sin(np.linspace(0, np.pi, n)) ** 0.6 * (1 + 0.5 * rng.standard_normal(n) * 0.2)
por(L, 1.40, rasp, db(-22)); por(R, 1.40, rasp, db(-25))
# impacto na água: estalo + jato de respingos + baque grave
n = int(0.9 * SR); t = np.arange(n) / SR
spl = hp(rng.standard_normal(n), 900) * env(n, 0.004, 0.18) + 0.6 * bp(rng.standard_normal(n), 300, 2500) * env(n, 0.03, 0.35)
baque = np.sin(2 * np.pi * (70 - 25 * t) * t) * env(n, 0.003, 0.22)
por(L, T_AGUA, spl * 0.9 + baque, db(-9)); por(R, T_AGUA, spl * 0.9 + baque, db(-10))
# subaquático: ronco abafado + bolhas (chirps ascendentes)
sub = lp(rng.standard_normal(N), 350) * janela(T_AGUA, 5.6, 0.1, 0.4)
L += sub * db(-24); R += sub * db(-24)
for k in range(28):
    tb = T_AGUA + rng.uniform(0.05, 2.2) ** 1.2; n = int(rng.uniform(0.03, 0.07) * SR); tt = np.arange(n) / SR
    f0 = rng.uniform(380, 900); bl = np.sin(2 * np.pi * (f0 * tt + 0.5 * f0 * 6 * tt * tt)) * env(n, 0.002, 0.02)
    pan = rng.uniform(0.3, 0.7); por(L, tb, bl, db(-26) * (1 - pan)); por(R, tb, bl, db(-26) * pan)
# bloco toca o leito: baque surdo
n = int(0.6 * SR); t = np.arange(n) / SR
th = (np.sin(2 * np.pi * 48 * t) + 0.5 * np.sin(2 * np.pi * 110 * t)) * env(n, 0.004, 0.16) + 0.3 * lp(rng.standard_normal(n), 300) * env(n, 0.01, 0.2)
por(L, T_FUNDO, th, db(-12)); por(R, T_FUNDO, th, db(-12))
# transições (whoosh) em 5,25 e 14,80
for tw in (5.25, 14.80):
    n = int(0.55 * SR); w = bp(rng.standard_normal(n), 300, 5000) * np.sin(np.linspace(0, np.pi, n)) ** 2
    por(L, tw - 0.2, w, db(-28)); por(R, tw - 0.15, w, db(-28))
# estaleiro: zumbido distante, ventilação e batidas metálicas longe
amb = lp(rng.standard_normal(N), 1200) * janela(5.25, 15.0, 0.4, 0.5); hum = np.sin(2 * np.pi * 60 * np.arange(N) / SR) * janela(5.25, 15.0, 0.4, 0.5)
L += amb * db(-36) + hum * db(-44); R += np.roll(amb, 2000) * db(-36) + hum * db(-44)
for tc in (6.4, 8.9, 10.6):
    n = int(0.5 * SR); t = np.arange(n) / SR; c = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((930, 9), (2140, 12), (3350, 16)))
    por(L, tc, lp(c, 4000) * env(n, 0.002, 0.3), db(-40)); por(R, tc + 0.01, lp(c, 4000) * env(n, 0.002, 0.3), db(-42))
# motor do pórtico: descida (5,6–12,5) e translação do carro (12,5–14,4)
t = np.arange(N) / SR; f = 96 + 4 * np.sin(2 * np.pi * 0.7 * t)
mot = lp(np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR), 900)
mot = mot * (janela(5.6, 12.5, 0.5, 0.3) * db(-31) + janela(12.5, 14.4, 0.2, 0.2) * db(-28))
L += mot; R += mot
# encaixe da chapa: impacto metálico ressonante (14,40 s)
n = int(1.6 * SR); t = np.arange(n) / SR
clk = sum(a * np.sin(2 * np.pi * fr * t) * np.exp(-t * d) for a, fr, d in ((1, 523, 3.2), (0.7, 1187, 4.5), (0.5, 2211, 6), (0.3, 3400, 8))) + 0.6 * hp(rng.standard_normal(n), 2000) * env(n, 0.001, 0.02)
por(L, T_ENCAIXE, clk * env(n, 0.002, 0.9), db(-12)); por(R, T_ENCAIXE + 0.004, clk * env(n, 0.002, 0.9), db(-13))
# assinatura: carrilhão suave da marca (sob a voz)
n = int(2.5 * SR); t = np.arange(n) / SR
sino = sum(a * np.sin(2 * np.pi * fr * t) * np.exp(-t * d) for a, fr, d in ((1, 587.3, 1.6), (0.6, 880.0, 2.0), (0.4, 1174.7, 2.6)))
por(L, 14.95, sino, db(-30)); por(R, 14.97, sino, db(-30))

# narração: amostra real (normalizada a −16 LUFS pelo pipeline da voz) e ducking dos efeitos sob a fala
voz, sr = sf.read(os.path.join(AQUI, '..', 'voz', 'amostra_assinatura', 'narracao_48k.wav'))
assert sr == SR
duck = 1 - 0.6 * janela(T_VOZ - 0.1, T_VOZ + len(voz) / SR + 0.1, 0.15, 0.3)
L *= duck; R *= duck
por(L, T_VOZ, voz); por(R, T_VOZ, voz)
mix = np.stack([L, R], 1)
pico = np.abs(mix).max(); alvo = db(-1.5)
if pico > alvo: mix *= alvo / pico
sf.write(os.path.join(AQUI, 'audio_animatic.wav'), mix, SR, subtype='PCM_24')
json.dump(dict(eventos=dict(t_agua=T_AGUA, t_fundo=T_FUNDO, t_encaixe=T_ENCAIXE, t_voz=T_VOZ, dur_voz=round(len(voz) / SR, 3)), pico_dbfs=round(20 * np.log10(np.abs(mix).max()), 2)),
          open(os.path.join(AQUI, 'audio_animatic.json'), 'w'), indent=1)
print('ok', round(20 * np.log10(np.abs(mix).max()), 2), 'dBFS')
