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


# ---------------------------------------------------------------- avaria (porão) — hipóteses documentadas
# Estrutura adotada na região de carga: duplo fundo de 2,2 m (estanque), tanques laterais de 2,0 m de largura do
# fundo interno até z = 6,0 m (estanques) e costado simples acima disso. O rombo fica no costado simples, abaixo da
# linha d'água (z ≈ 7–8,5 m), e alaga SÓ o porão: duplo fundo e tanques laterais permanecem secos.
# Método da perda de flutuabilidade: o porão aberto ao mar deixa de contribuir com volume e com área/inércia de
# flutuação (isso é o efeito de superfície livre de um compartimento em comunicação com o mar). KG não muda.
Z_DB, L_TANQUE, Z_TANQUE, CASCO, MU_PORAO = 2.2, 2.0, 6.0, 0.3, 0.95


def meia_boca_porao(x, z):
    b = navio.meia_boca(x, z)
    return max(b - (L_TANQUE if z < Z_TANQUE else CASCO), 0.0)


def carena_avaria(T, theta, comp, mu=MU_PORAO):
    V = Mx = Mz = 0.0; tg = math.tan(theta)
    for x in XC:
        zw = T + x * tg; a, mz = secao(x, zw)
        if comp[0] <= x <= comp[1]:
            k = navio.quilha(x); z0 = k + Z_DB; top = min(zw, navio.PONTAL)
            if top > z0:
                zs = np.linspace(z0, top, NZ + 1); zm = 0.5 * (zs[1:] + zs[:-1]); dz = zs[1] - zs[0]
                hb = np.array([2 * meia_boca_porao(x, z) for z in zm])
                a -= mu * float((hb * dz).sum()); mz -= mu * float((hb * zm * dz).sum())
        V += a * DX; Mx += a * x * DX; Mz += mz * DX
    return V, Mx / V, Mz / V


def equilibrio_avaria(T0, comp, mu=MU_PORAO):
    V0, lcg, _ = carena(T0)
    def T_para(th):
        lo, hi = 1.0, navio.PONTAL - 0.01
        for _ in range(40):
            m = 0.5 * (lo + hi)
            if carena_avaria(m, th, comp, mu)[0] < V0: lo = m
            else: hi = m
        return 0.5 * (lo + hi)
    th = 0.0
    for _ in range(15):
        T = T_para(th); lcb = carena_avaria(T, th, comp, mu)[1]
        d = 2e-4; lcb2 = carena_avaria(T_para(th + d), th + d, comp, mu)[1]
        th -= (lcb - lcg) / ((lcb2 - lcb) / d)
        if abs(lcb - lcg) < 0.005: break
    return T_para(th), th


def inercia_transversal(T, theta=0.0, comp=None, mu=MU_PORAO):
    """I_T da área de flutuação (m⁴); o porão alagado aberto ao mar remove μ da sua faixa de flutuação."""
    I = 0.0; tg = math.tan(theta)
    for x in XC:
        zw = T + x * tg; b = navio.meia_boca(x, zw); i = (2 * b) ** 3 / 12.0
        if comp and comp[0] <= x <= comp[1]: i -= mu * (2 * meia_boca_porao(x, zw)) ** 3 / 12.0
        I += i * DX
    return I


def estabilidade_avaria(T0, comp, GM0=1.5, mu=MU_PORAO):
    """GM antes e depois (KG fixo, adotado de modo que o GM intacto carregado seja GM0)."""
    V0, _, KB0 = carena(T0); KM0 = KB0 + inercia_transversal(T0) / V0; KG = KM0 - GM0
    T1, th1 = equilibrio_avaria(T0, comp, mu)
    _, _, KB1 = carena_avaria(T1, th1, comp, mu); KM1 = KB1 + inercia_transversal(T1, th1, comp, mu) / V0
    return dict(T0=T0, T1=T1, trim_graus=math.degrees(th1), KG=KG, KM0=KM0, GM0=GM0, KM1=KM1, GM1=KM1 - KG,
                proa=T1 + navio.PROA * math.tan(th1), popa=T1 + navio.POPA * math.tan(th1),
                borda_livre_proa=navio.PONTAL - (T1 + navio.PROA * math.tan(th1)))
