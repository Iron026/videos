"""Gravações reais (bibliotecas licenciadas): carregar, reamostrar para 48 kHz, recortar o evento, aparar, normalizar,
mudar levemente a altura (só para câmera lenta / tamanho, nunca acelerar demais) e registrar cada uso (relatório)."""
import os, json, numpy as np, soundfile as sf
from fractions import Fraction
from scipy.signal import resample_poly

SR = 48000
A = os.path.dirname(os.path.abspath(__file__))
FONTES = {x['id']: x for x in json.load(open(os.path.join(A, 'candidatos_mixkit.json')))}
# Wikimedia Commons (Work With Sounds, CC BY 4.0): id = nome do arquivo sem 'WWS ' e sem '.ogg' (ex.: 'Shipyardcrane')
_CM = os.path.join(A, 'fontes_commons.json')
if os.path.exists(_CM):
    for x in json.load(open(_CM)): FONTES[x['id']] = x
USOS = []          # (t, id, título, ini, dur, uso)
grupo_atual = lambda: None   # definido pelo script de mixagem (grupo de substituição ativo)
# Substituições após a escuta, SEM editar o código: som/substituicoes.json = {"<id original>": {"arquivo": "bib/manual/x.wav",
# "titulo": ..., "autor": ..., "url": ..., "licenca": ..., "credito": ...}}. O arquivo novo entra nos mesmos instantes e camadas.
_SP = os.path.join(A, 'substituicoes.json')
SUBST = {k: v for k, v in json.load(open(_SP)).items() if not k.startswith('_')} if os.path.exists(_SP) else {}
_C = {}


def _titulo(i): return SUBST[str(i)].get('titulo', SUBST[str(i)]['arquivo']) if str(i) in SUBST else FONTES[i]['titulo']


def _marca(i, uso):
    r = getattr(i, 'reserva_de', '')
    return f'{uso} [RESERVA Mixkit: WWS {r} (Commons) não pôde ser baixado]' if r else uso


def carregar(i):
    if i not in _C:
        f = os.path.join(A, 'bib', 'mixkit', f'{i}.wav') if isinstance(i, int) else os.path.join(A, 'bib', 'commons', f'{i}.ogg')
        if str(i) in SUBST: f = os.path.join(A, SUBST[str(i)]['arquivo'])
        a, sr = sf.read(f, always_2d=True)
        if a.shape[1] == 1: a = np.repeat(a, 2, 1)
        if sr != SR:
            fr = Fraction(SR, sr).limit_denominator(1000); a = resample_poly(a, fr.numerator, fr.denominator, axis=0)
        _C[i] = a.astype(np.float64)
    return _C[i]


def ataque(i, limiar_db=-20, ini=0.0):
    """Instante (s) em que o evento começa: primeira janela de 5 ms a menos de |limiar| dB do máximo."""
    a = carregar(i)[int(ini * SR):].mean(1); w = int(0.005 * SR)
    e = np.sqrt(np.convolve(a ** 2, np.ones(w) / w, 'same')) + 1e-12
    return ini + float(np.argmax(20 * np.log10(e) > 20 * np.log10(e.max()) + limiar_db)) / SR


def trecho(i, ini=0.0, dur=None, fi=0.004, fo=0.08, tom=1.0, norm='pico', ref=-1.0, mono=False, t=None, uso=''):
    """Recorta [ini, ini+dur] (s) da gravação i. tom < 1 = mais grave e mais lento (câmera lenta / objeto maior)."""
    a = carregar(i); i0 = int(ini * SR); i1 = len(a) if dur is None else min(len(a), i0 + int(dur * SR / tom))
    x = a[i0:i1].copy()
    if tom != 1.0:
        fr = Fraction(1 / tom).limit_denominator(60); x = resample_poly(x, fr.numerator, fr.denominator, axis=0)
    n = len(x); k1 = min(n, int(fi * SR)); k2 = min(n, int(fo * SR))
    if k1: x[:k1] *= np.linspace(0, 1, k1)[:, None]
    if k2: x[-k2:] *= np.linspace(1, 0, k2)[:, None]
    if mono: x = np.repeat(x.mean(1, keepdims=True), 2, 1)
    if norm == 'pico': x *= 10 ** (ref / 20) / (np.abs(x).max() + 1e-12)
    elif norm == 'rms': x *= 10 ** (ref / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-12)
    if t is not None: USOS.append(dict(t=round(t, 2), id=int(i) if isinstance(i, int) else i, titulo=_titulo(i), ini=round(ini, 2), dur=round(n / SR, 2), tom=tom, uso=_marca(i, uso), grupo=grupo_atual(), substituido=str(i) in SUBST))
    return x


def laco(i, dur, ini=0.0, fim=None, xf=0.6, ref=-20.0, t=None, uso=''):
    """Cama contínua de 'dur' s a partir de um trecho da gravação, emendada com fusões de xf s (sem alterar altura)."""
    a = carregar(i); s0 = int(ini * SR); s1 = len(a) if fim is None else min(len(a), int(fim * SR))
    if s1 - s0 < int(2 * xf * SR) + SR: s0, s1 = 0, len(a)          # trecho pedido além do fim da gravação: usa a gravação inteira
    base = a[s0:s1]
    n = int(dur * SR); k = int(xf * SR); out = np.zeros((n, 2)); pos = 0; rampa = np.linspace(0, 1, k)[:, None]
    while pos < n:
        seg = base.copy(); m = min(len(seg), n - pos)
        if pos > 0: seg[:k] *= rampa
        if pos + len(seg) < n: seg[-k:] *= rampa[::-1]
        out[pos:pos + m] += seg[:m]; pos += len(seg) - k
    out *= 10 ** (ref / 20) / (np.sqrt(np.mean(out ** 2)) + 1e-12)
    if t is not None: USOS.append(dict(t=round(t, 2), id=int(i) if isinstance(i, int) else i, titulo=_titulo(i), ini=round(ini, 2), dur=round(dur, 2), tom=1.0, uso=_marca(i, uso), grupo=grupo_atual(), substituido=str(i) in SUBST))
    return out
