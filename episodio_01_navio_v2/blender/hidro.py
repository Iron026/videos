"""Hidrostática do casco do episódio (mesma forma meia_boca do navio.py), por integração numérica.
Coordenadas do navio: x ao longo do comprimento, z a partir da quilha. Água salgada ρ = 1,025 t/m³.
Funções: volume/centro de carena com calado T e trim θ (proa para baixo > 0), área de flutuação,
equilíbrio após inundação de um compartimento (método da perda de flutuabilidade)."""
import math
import numpy as np
import navio

RHO = 1.025
NX, NZ = 200, 50
XS = np.linspace(navio.POPA, navio.PROA, NX + 1); XC = 0.5 * (XS[1:] + XS[:-1]); DX = XS[1] - XS[0]


def secao(x, zw):
    """Área e momento vertical (∫z dA) da seção x abaixo de zw (coordenadas do navio)."""
    k = navio.quilha(x); top = min(zw, navio.PONTAL)
    if top <= k: return 0.0, 0.0
    zs = np.linspace(k, top, NZ + 1); zm = 0.5 * (zs[1:] + zs[:-1]); dz = zs[1] - zs[0]
    b = np.array([2 * navio.meia_boca(x, z) for z in zm])
    return float((b * dz).sum()), float((b * zm * dz).sum())


def carena(T, theta=0.0, perdido=None, mu=0.9):
    """Volume deslocado, LCB (x) e KB (z) para linha d'água z = T + x·tanθ (θ>0: proa afunda).
    perdido=(xa, xb): compartimento inundado (perde μ do volume da seção abaixo da linha d'água)."""
    V = Mx = Mz = 0.0; tg = math.tan(theta)
    for x in XC:
        a, mz = secao(x, T + x * tg)
        if perdido and perdido[0] <= x <= perdido[1]: a *= (1 - mu); mz *= (1 - mu)
        V += a * DX; Mx += a * x * DX; Mz += mz * DX
    return V, (Mx / V if V else 0.0), (Mz / V if V else 0.0)


def area_flutuacao(T):
    return float(sum(2 * navio.meia_boca(x, T) * DX for x in XC))


def calado_para(V_alvo, theta=0.0, perdido=None, lo=1.0, hi=None):
    hi = hi or navio.PONTAL - 0.01
    for _ in range(40):
        m = 0.5 * (lo + hi)
        if carena(m, theta, perdido)[0] < V_alvo: lo = m
        else: hi = m
    return 0.5 * (lo + hi)


def equilibrio_inundado(T0, perdido, mu=0.9):
    """Novo calado (a meia-nau) e trim após perder o compartimento: V igual ao inicial e LCB = LCG (= LCB inicial)."""
    V0, lcg, _ = carena(T0)
    th = 0.0
    for _ in range(12):
        T = calado_para(V0, th, perdido)
        _, lcb, _ = carena(T, th, perdido)
        # derivada numérica de LCB em θ (com volume mantido)
        d = 2e-4; T2 = calado_para(V0, th + d, perdido); _, lcb2, _ = carena(T2, th + d, perdido)
        g = (lcb2 - lcb) / d
        if abs(g) < 1e-9: break
        th -= (lcb - lcg) / g
        if abs(lcb - lcg) < 0.01: break
    T = calado_para(V0, th, perdido)
    return T, th


if __name__ == '__main__':
    for T in (8.0, 9.0, 10.6):
        V, lcb, kb = carena(T); print(f'T={T}: V={V:.0f} m³ Δ={RHO*V:.0f} t LCB={lcb:.2f} KB={kb:.2f} Awp={area_flutuacao(T):.0f} m²')
