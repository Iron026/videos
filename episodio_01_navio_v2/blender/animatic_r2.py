"""Animatic do Episódio 01 · revisão r2 (direção de câmera). Reaproveita as cenas, a física e o movimento do pórtico
da v1 (animatic.py): só mudam câmeras e o mapeamento do tempo.  Uso: python3 animatic_r2.py <1|23> <pasta_saida>

Linha do tempo GLOBAL r2 (s, 30 fps) — legendas provisórias (~145 pal/min, ritmo medido da amostra):
  Plano 1   0,00–4,80   cais, câmera próxima na linha d'água; câmera lenta (0,35×) no impacto
  Plano 2   4,60–7,00   aérea curta (fusão 4,60–4,80), corte em movimento para o close
  Plano 3a  7,00–10,25  a chapa desce para o quadro (câmera acompanha)
  Plano 3b 10,25–13,75  close aprovado: descida final, deslize e encaixe (13,15 s)
  Assinatura 13,75–16,85 (separada; voz entra 0,40 s antes, sobre o encaixe já feito)
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: F401 (carrega mathutils)
import numpy as np
from mathutils import Vector
import animatic as A
from animatic import camera_em, suave, suave5, lerp, lerpv

FPS = 30
P1 = dict(fim=4.80, ts0=0.90, lento=(2.95, 3.45), v_lento=0.35)          # tempo de cena inicial, trecho em câmera lenta
P23 = dict(ini=4.60, corte=7.00, corte_b=10.25, fim=13.75)


# ---------- plano 1: tempo global -> tempo de cena (rampa de velocidade suave) ----------
def mapa_lento():
    a, b = P1['lento']; v0 = P1['v_lento']; ts = np.linspace(P1['ts0'], 9.0, 40001)
    sobe = np.clip((ts - (a - 0.12)) / 0.12, 0, 1); desce = np.clip(((b + 0.20) - ts) / 0.20, 0, 1)
    k = np.minimum(sobe, desce); k = k * k * (3 - 2 * k)
    v = 1 - (1 - v0) * k                                          # velocidade da cena (1 = tempo real)
    g = np.concatenate([[0], np.cumsum(0.5 * (1 / v[1:] + 1 / v[:-1]) * np.diff(ts))])
    return lambda tg: float(np.interp(tg, g, ts)), lambda tc: float(np.interp(tc, ts, g))


def plano1(pasta):
    cena, glob = mapa_lento()
    n = int(round(P1['fim'] * FPS)) + 1

    def camera(cam, t, f, info):
        tg = f / FPS; ta, tf = info['t_agua'], info['t_fundo']; b = info['bloco']
        # 1) no cais, perto: o bloco ocupa ~1/3 da largura; 2) desce até a linha d'água no impacto (meio a meio);
        # 3) mergulha e inclina acompanhando o bloco até o leito. Leve empurrão para dentro durante a câmera lenta.
        kz = suave((t - 2.45) / (ta + 0.10 - 2.45)); ks = suave((t - ta) / (tf + 0.25 - ta))
        z = lerp(1.65, 0.12, kz) + lerp(0.0, -1.45, ks)
        y = lerp(-1.6, -0.5, suave((t - 2.4) / 1.6))
        x = lerp(1.15, 1.45, suave((t - 1.0) / 3.0))
        alvo = Vector((lerp(5.5, 3.6, suave((t - 1.2) / 1.7)), 6.5, lerp(2.7, 0.0, kz)))
        alvo.z += lerp(0.0, max(b.z, -4.2) + 0.3 - alvo.z, suave((t - ta - 0.05) / 0.55))   # depois do mergulho, segue o bloco
        # 4) bloco no leito: recua e revela o bloco inteiro no fundo, com a superfície no alto do quadro
        kr = suave((t - tf + 0.15) / 0.95)
        pos = Vector((x, y, z)).lerp(Vector((2.3, -8.0, -1.0)), kr); alvo = alvo.lerp(Vector((3.3, 6.5, -3.6)), kr)
        x, y, z = pos
        # tranco de câmera no impacto (decai em 0,4 s de cena)
        dt = t - ta; tr = 0.05 * math.exp(-dt / 0.13) * math.sin(dt * 55) if dt > 0 else 0.0
        camera_em(cam, Vector((x, y, z + tr)), alvo, lerp(30, 34, suave((t - 2.5) / 1.4)))
    A.plano1(pasta, n=n, tempo=lambda f: cena(f / FPS), camera=camera)
    print('R2_P1', dict(t_agua_global=round(glob(3.13), 3), t_fundo_global=round(glob(3.76), 3)))


# ---------- planos 2/3: tempo global -> tempo do pórtico (mesmo movimento da v1) ----------
def t_guindaste(tg):
    """Descida (5,6→11,5) levemente comprimida; descida final (11,5→12,5) e deslize (12,5→14,4) em tempo real,
    para o balanço do pêndulo (calculado da aceleração) e o limite de folga continuarem idênticos."""
    pts_g = [P23['ini'], 10.25, 11.25, 13.15, 13.75]
    pts_c = [5.60, 11.50, 12.50, 14.40, 15.00]
    return float(np.interp(tg, pts_g, pts_c))


def plano23(pasta):
    n = int(round((P23['fim'] - P23['ini']) * FPS)) + 1

    def camera(cam, tg, tc):
        if tg < P23['corte']:          # plano 2: aérea curta, acelera até o enquadramento aprovado e corta em movimento
            k = suave(min(max((tg - P23['ini']) / (P23['corte'] - P23['ini'] + 0.35), 0), 1))
            camera_em(cam, lerpv((200, 98, 58), (154, 32, 12), k), lerpv((52, 0, 8), (86, 6, 17), k), 24)
        elif tg < P23['corte_b']:      # plano 3a: chapa entra pelo alto do quadro; a câmera inclina com ela
            k = suave((tg - P23['corte']) / (P23['corte_b'] - P23['corte']))
            zc = 16.5 + 3.0 + max(0.0, painel_z(tc) - 3.0) * 0.30
            camera_em(cam, lerpv((101, 39, 15), (98, 36, 19), k), Vector((73.5, 14.5, zc)), 26)
        else:                          # plano 3b: close aprovado da v1 (descida final, deslize, encaixe)
            k = suave((tg - P23['corte_b']) / (P23['fim'] - P23['corte_b']))
            camera_em(cam, lerpv((97, 35, 25), (93, 32.5, 23), k), lerpv((73, 14.5, 16.5), (73.5, 14.5, 15.5), k), 30)

    def painel_z(tc):                  # altura da chapa acima da posição final (mesma lei de A.plano23)
        if tc < 11.5: return lerp(13.0, 1.2, suave((tc - 5.6) / 5.9))
        if tc < 12.5: return lerp(1.2, 0.0, suave5((tc - 11.5) / 1.0))
        return 0.0
    A.plano23(pasta, n=n, tempo=lambda f: (P23['ini'] + f / FPS, t_guindaste(P23['ini'] + f / FPS)), camera=camera)


if __name__ == '__main__':
    p, pasta = int(sys.argv[1]), sys.argv[2]
    {1: plano1, 23: plano23}[p](pasta)
