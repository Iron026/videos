"""Movimento e PERSPECTIVA para o som: lê das cenas exportadas (cenas/sXX/cena.json) a câmera e os objetos quadro a
quadro, no tempo global do episódio. Dá curvas de velocidade e de distância câmera→ponto, e aplica a perspectiva
(câmera longe: mais baixo e menos agudo; perto: presente e definido)."""
import os, json, numpy as np
from sintese import SR, lpz, tt

A = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(A, '..', 'cenas'); _cache = {}


def _cena(s):
    if s not in _cache: _cache[s] = json.load(open(os.path.join(C, s, 'cena.json')))
    return _cache[s]


def _mat(M): return np.array(M, float).reshape(4, 4).T          # matriz coluna-major do exportador → 4×4


def trajetoria(s, objeto, local=(0.0, 0.0, 0.0)):
    """(t, P): posição no mundo de um ponto do objeto (coordenadas locais), quadro a quadro."""
    c = _cena(s); q = c['animacao']['quadros']; fps = c['animacao']['fps']; g0 = c['g0']; p = np.array([*local, 1.0])
    t = np.array([g0 + i / fps for i in range(len(q))]); P = np.array([(_mat(x['objetos'][objeto]) @ p)[:3] for x in q])
    return t, P


def camera(s):
    c = _cena(s); q = c['animacao']['quadros']; fps = c['animacao']['fps']; g0 = c['g0']
    return np.array([g0 + i / fps for i in range(len(q))]), np.array([x['camera']['pos'] for x in q], float)


def velocidade(s, objeto, suav=5):
    t, P = trajetoria(s, objeto); fps = 1 / (t[1] - t[0])
    v = np.r_[0, np.linalg.norm(np.diff(P, axis=0), axis=1) * fps]; v[v > 50] = 0     # saltos de corte não são movimento
    return t, np.convolve(v, np.ones(suav) / suav, 'same')


def distancia(s, objeto=None, local=(0.0, 0.0, 0.0), mundo=None):
    tc, Pc = camera(s)
    if mundo is not None: Po = np.array(mundo, float)[None, :]
    else: _, Po = trajetoria(s, objeto, local)
    return tc, np.linalg.norm(Pc - Po, axis=1)


def amostrar(t, y, a, n):
    """Curva (t, y) amostrada por amostra de áudio a partir do instante global a."""
    return np.interp(a + tt(n), t, y)


def perspectiva(x, a, t, d, d_ref, k=0.6, piso=-15.0, teto=2.0, lp=2500.0):
    """Aplica a perspectiva a x (estéreo) que começa em a: ganho −20·k·log10(d/d_ref) dB (limitado) e, com a distância,
    mistura gradual para uma versão sem agudos (até 100% a 8× d_ref)."""
    n = len(x); fps = 1 / (t[1] - t[0]); w = max(1, int(0.3 * fps))           # nos cortes a perspectiva muda em ~0,3 s, sem degrau seco
    dl = np.convolve(np.pad(np.log(np.maximum(d, 0.5)), (w, w), mode='edge'), np.ones(w) / w, 'same')[w:-w]
    dd = np.exp(amostrar(t, dl, a, n))
    g_db = np.clip(-20 * k * np.log10(dd / d_ref), piso, teto); w = np.clip(np.log2(dd / d_ref) / 3.0, 0, 1)
    return ((1 - w)[:, None] * x + w[:, None] * lpz(x, lp, 2)) * (10 ** (g_db / 20))[:, None]
