"""Encenação do personagem no Ep. 02 (abertura A1–A4 e porta aberta I1–I4). Tempos = instantes VERIFICADOS das palavras
(roteiro/palavras.json, Whisper oficial + ataque acústico), nunca segundos redondos. Atuação contida: olhar, cabeça,
sobrancelhas, postura e mãos com propósito (puxar a porta, apoiar no batente, mão no queixo ao pensar). Sem fala.
A porta e a mão usam a MESMA curva de ângulo: a mão acompanha o puxador enquanto puxa e solta quando a porta segue sozinha."""
import math
from mathutils import Vector, Matrix
import geladeira as G, personagem as PE, ep_base as B

W = {}
def _palavras():
    if not W:
        import json, os
        p = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'roteiro', 'palavras.json')))
        for i, w in enumerate(p): W.setdefault(w['palavra'].strip('.,:;?!').lower(), []).append(w['inicio'])
    return W
def T(palavra, n=0):
    """Instante de início da n-ésima ocorrência de uma palavra (verificada)."""
    return _palavras()[palavra.lower()][n]


def porta_ang(t_inicio, dur=1.1):
    return lambda g: 100.0 * B.suave((g - t_inicio) / dur)


def alca(a):
    """Ponto de pega do puxador (face de fora) com a porta aberta a graus."""
    r = math.radians(a); lx, ly = -2 * G.GX + 0.045, -0.072 - 0.045
    return Vector((G.GX + lx * math.cos(r) - ly * math.sin(r), G.GY0 + lx * math.sin(r) + ly * math.cos(r), 1.0))


def corpo(pos, yaw, v):
    return Vector((pos[0], pos[1], 0.0)) + Matrix.Rotation(math.radians(yaw), 3, 'Z') @ Vector(v)


def repouso(lado, pos, yaw, balanco=0.0):
    sx = 1 if lado == 'd' else -1
    return tuple(corpo(pos, yaw, (sx * 0.215, 0.03 + balanco, 0.80)))


def olhar(pos, yaw, ponto, giro=0.0, incl=0.0):
    H = corpo(pos, yaw, (0, 0, 1.52)); v = Matrix.Rotation(math.radians(-yaw), 3, 'Z') @ (Vector(ponto) - H)
    y = math.degrees(math.atan2(-v.x, v.y)) - giro; p = math.degrees(math.atan2(v.z, math.hypot(v.x, v.y))) - incl
    return (max(-70, min(70, y)), max(-35, min(35, p)))


def _caminhada(g, t0, t1, A, Bp, passo=0.62):
    """Posição e fase entre A e Bp de t0 a t1 (aceleração e desaceleração suaves); None fora do trecho."""
    if g <= t0: return tuple(A), None
    if g >= t1: return tuple(Bp), None
    k = B.suave((g - t0) / (t1 - t0)); P = Vector(A).lerp(Vector(Bp), k); d = (Vector(Bp) - Vector(A)).length * k
    amp = min(1.0, (g - t0) / 0.25, (t1 - g) / 0.25)
    return tuple(P), (d / passo, max(0.0, amp))


PA = (-0.60, -0.86); YA = -47.0          # diante do puxador
PB = (-0.84, -1.20); YB = -38.0          # um passo atrás, olhando a geladeira inteira
INTERIOR = (0.0, -0.05, 1.00); TOPO_TRAS = (0.0, 0.38, 1.80); BATENTE_E = (-0.31, -0.37, 1.22)


def _mao_puxando(lado_d_estado, g, t_alcance, t_puxa, ang, pos, yaw):
    """Mão direita: repouso → puxador (antes de puxar) → acompanha o puxador até 38° → volta ao repouso."""
    a = ang(g); t_solta = t_puxa + 0.46 * 1.1          # porta a ~38° (smoothstep = 0,38)
    rest = repouso('d', pos, yaw)
    if g < t_alcance: return rest
    if g < t_puxa: return PE.trilha([(t_alcance, rest), (t_puxa - 0.04, tuple(alca(0)))], g)
    if g < t_solta: return tuple(alca(a))
    return PE.trilha([(t_solta, tuple(alca(ang(t_solta)))), (t_solta + 0.45, rest)], g)


def est_abertura(g):
    """A1–A4 (g de −0,25 a 10,4 s). A1 abre a porta; A2 olha o interior apoiando a mão no batente; A3 recua um passo
    olhando o alto da traseira (fora de quadro); A4 reage à pergunta: estranhamento contido e mão no queixo."""
    ang = porta_ang(0.20)
    t_pens = T('ao')          # "ao mesmo tempo?"
    pos, fase = _caminhada(g, 3.05, 4.20, PA, PB)
    yaw = PE.trilha([(3.05, YA), (4.20, YB)], g)
    e = dict(pos=pos, yaw=yaw, passo=(-fase[0], fase[1]) if fase else None)      # recua de costas: fase negativa
    # mão direita: puxa a porta; no fim de A4, ao queixo
    md = _mao_puxando(None, g, -0.25, 0.20, ang, pos, yaw)
    if g > 3.0: md = repouso('d', pos, yaw, 0.06 * math.sin(2 * math.pi * fase[0]) * fase[1] if fase else 0.0)
    e['braco_d'] = ('ik', md, tuple(corpo(pos, yaw, (0.7, -0.4, -1.0))), (0, 0, -1))
    if g > t_pens - 0.15:   # v4: a mão APOIA sob o queixo (alvo calculado da cabeça já posicionada, não de um ponto fixo)
        e['braco_d'] = ('queixo', PE.trilha([(t_pens - 0.15, 0.0), (t_pens + 0.50, 1.0)], g), repouso('d', PB, YB),
                        tuple(corpo(PB, YB, (0.65, 0.25, -1.0))))
    # mão esquerda: apoia no batente esquerdo enquanto olha o interior (A2), solta antes de recuar
    me = PE.trilha([(1.45, repouso('e', PA, YA)), (1.85, BATENTE_E), (2.85, BATENTE_E), (3.15, repouso('e', PA, YA))], g)
    if g > 3.15: me = repouso('e', pos, yaw, -0.06 * math.sin(2 * math.pi * fase[0]) * fase[1] if fase else 0.0)
    e['braco_e'] = ('ik', me, tuple(corpo(pos, yaw, (-0.7, -0.4, -1.0))), (0, 0, -1))
    # postura
    e['incl'] = PE.trilha([(0.15, 0.0), (0.35, -3.0), (0.70, 0.0), (1.5, 0.0), (1.9, 7.0), (2.85, 7.0), (3.2, 0.0)], g)
    # olhar: puxador → interior (fria por dentro) → alto da traseira (quente por fora) → reação
    alvo = PE.trilha([(-0.25, tuple(alca(0))), (0.45, tuple(alca(20))), (0.95, INTERIOR), (T('fria'), INTERIOR), (2.6, (0.05, -0.05, 0.9)),
                      (T('quente') - 0.35, TOPO_TRAS), (T('parece'), TOPO_TRAS), (T('parece') + 0.7, INTERIOR),
                      (T('mesma') + 0.2, INTERIOR), (T('duas') - 0.1, TOPO_TRAS), (T('coisas') + 0.2, INTERIOR), (t_pens + 0.1, (0.15, 0.30, 1.72))], g)
    cy, cp = olhar(pos, yaw, alvo, incl=e['incl'])
    rol = PE.trilha([(T('parece'), 0.0), (T('parece') + 0.4, -7.0), (T('mesma'), -3.0), (t_pens, -3.0), (t_pens + 0.5, -9.0)], g)
    e['cab'] = (cy * 0.85, cp * 0.85, rol); e['olhar'] = (cy * 0.15, cp * 0.2)
    sob = PE.trilha([(1.4, 0.0), (T('fria'), 0.25), (2.6, 0.1), (T('quente'), 0.5), (T('parece'), 0.65), (6.0, 0.35),
                     (t_pens, 0.35), (t_pens + 0.4, 0.55)], g)
    inc = PE.trilha([(T('parece'), 0.0), (T('parece') + 0.4, 0.45), (6.0, 0.2), (t_pens + 0.4, 0.35)], g)
    ass = PE.trilha([(t_pens, 0.0), (t_pens + 0.45, 0.30)], g)     # v4: uma sobrancelha um pouco mais alta ao pensar
    e['sobr'] = (sob, inc, ass); e['piscar'] = PE.piscadas(g, [1.15, 3.55, 6.9, 8.85])
    return e


PI = (-1.38, -1.48)                       # entrada pela esquerda em I1
PC = (-1.45, -0.95); YC = -62.7           # recuo: de lado, olhando a geladeira aberta (fora do caminho do calor)
def est_porta_aberta(g):
    """I1–I4. I1: entra, abre a porta, solta e recua um passo — a porta FICA aberta; I2: sai de quadro pela esquerda;
    I3: acompanha com o olhar o calor que volta à cozinha; I4: ergue o olhar para o calor liberado atrás da geladeira."""
    t_puxa = T('deixa') - 0.13                 # a porta começa a abrir em "deixa a porta aberta"
    ang = porta_ang(t_puxa)
    t_recua = t_puxa + 0.95
    if g < t_recua: pos, fase = _caminhada(g, 115.55, 116.95, PI, PA); fase_s = fase
    else: pos, fase = _caminhada(g, t_recua, t_recua + 0.95, PA, PC); fase_s = (-fase[0], fase[1]) if fase else None
    yaw = PE.trilha([(115.55, -52.0), (116.95, YA), (t_recua, YA), (t_recua + 0.95, YC)], g)
    e = dict(pos=pos, yaw=yaw, passo=fase_s)
    bal = lambda sgn: sgn * 0.06 * math.sin(2 * math.pi * fase[0]) * fase[1] if fase else 0.0
    md = _mao_puxando(None, g, t_puxa - 0.45, t_puxa, ang, pos, yaw)
    if g < 117.0 or g > t_puxa + 1.0: md = repouso('d', pos, yaw, bal(1))
    e['braco_d'] = ('ik', md, tuple(corpo(pos, yaw, (0.7, -0.4, -1.0))), (0, 0, -1))
    e['braco_e'] = ('ik', repouso('e', pos, yaw, bal(-1)), tuple(corpo(pos, yaw, (-0.7, -0.4, -1.0))), (0, 0, -1))
    e['incl'] = PE.trilha([(t_puxa, 0.0), (t_puxa + 0.2, -3.0), (t_puxa + 0.55, 0.0)], g)
    t_volta = T('cômodo'); t_lib = T('libera')
    alvo = PE.trilha([(115.55, (-0.2, -0.3, 1.2)), (116.9, tuple(alca(0))), (t_puxa + 0.5, tuple(alca(30))), (t_puxa + 0.9, INTERIOR),
                      (T('mesma', 1) - 0.2, INTERIOR), (T('mesma', 1) + 0.5, (-0.05, -1.3, 1.5)), (t_volta - 0.4, (0.0, 0.2, 1.95)),
                      (t_volta + 0.6, INTERIOR), (t_lib - 0.2, INTERIOR), (t_lib + 0.6, TOPO_TRAS), (T('energia', -1), TOPO_TRAS),
                      (T('funcionar'), (0.0, 0.0, 1.3))], g)
    cy, cp = olhar(pos, yaw, alvo, incl=e['incl'])
    e['cab'] = (cy * 0.85, cp * 0.85, PE.trilha([(t_volta - 0.4, 0.0), (t_volta, -5.0), (t_lib, -2.0)], g))
    e['olhar'] = (cy * 0.15, cp * 0.2)
    e['sobr'] = (PE.trilha([(118.5, 0.0), (119.4, 0.15), (t_volta - 0.5, 0.15), (t_volta, 0.55), (t_lib, 0.3), (t_lib + 0.6, 0.6)], g),
                 PE.trilha([(t_volta - 0.5, 0.0), (t_volta, 0.4), (t_lib + 0.6, 0.3)], g))
    e['piscar'] = PE.piscadas(g, [116.2, 119.0, 121.6, 124.1, 126.4, 128.9, 131.9, 134.6])
    return e
