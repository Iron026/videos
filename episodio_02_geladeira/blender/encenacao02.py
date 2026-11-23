"""Encenação do personagem no Ep. 02 (abertura A1–A4 e porta aberta I1–I4). Tempos = instantes VERIFICADOS das palavras
(roteiro/palavras.json, Whisper oficial + ataque acústico), nunca segundos redondos. Atuação contida: olhar, cabeça,
sobrancelhas, postura e mãos com propósito (puxar a porta, apoiar no batente, mão no queixo ao pensar). Sem fala.
A porta e a mão usam a MESMA curva de ângulo: a mão acompanha o puxador enquanto puxa e solta quando a porta segue sozinha."""
import math, os
from mathutils import Vector, Matrix
import geladeira as G, personagem as PE, ep_base as B

W = {}
def _palavras():
    if not W:
        import json, os
        p = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'roteiro', 'palavras.json')))
        for i, w in enumerate(p): W.setdefault(w['palavra'].strip('.,:;?!').lower(), []).append(w['inicio'])
    return W
def T(palavra, n=0, apos=None):
    """Instante de início da n-ésima ocorrência de uma palavra (verificada); com apos, a primeira depois desse instante."""
    oc = _palavras()[palavra.lower()]
    return next(t for t in oc if t >= apos) if apos is not None else oc[n]


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


def passada(g, t0, t1, A, Bp, yaw0, yaw1, fracs=(0.45, 0.90, 1.0), largura=0.10):
    """Polimento: caminhada com pés PLANTADOS. Passos alternados (direito, esquerdo, direito…) pousam em frações do
    trajeto; o pé no ar sobe (6 cm) e rola do calcanhar para a ponta; o quadril sobe no apoio simples.
    Devolve (pos, yaw, bob, pes, balanço dos braços) ou None fora do trecho."""
    A, Bp = Vector((A[0], A[1], 0)), Vector((Bp[0], Bp[1], 0)); d = Bp - A
    yaw = PE.trilha([(t0, yaw0), (t1, yaw1)], g)
    lat = lambda yw: Vector((math.cos(math.radians(yw)), math.sin(math.radians(yw)), 0))        # +X local (lado direito)
    n = len(fracs); Ts = (t1 - t0) / n
    pos_pe = {'d': A + lat(yaw0) * largura, 'e': A - lat(yaw0) * largura}; yaw_pe = {'d': yaw0, 'e': yaw0}
    incl = {'d': 0.0, 'e': 0.0}; bob = 0.0; bal = 0.0
    for k, f in enumerate(fracs):
        lado = 'd' if k % 2 == 0 else 'e'; sg = 1 if lado == 'd' else -1
        ta, tb = t0 + k * Ts, t0 + (k + 1) * Ts; yw = PE.trilha([(t0, yaw0), (t1, yaw1)], tb)
        destino = A + d * f + lat(yw) * largura * sg
        if g >= tb: pos_pe[lado] = destino; yaw_pe[lado] = yw; continue
        if g > ta:
            u = (g - ta) / Ts; e_ = u * u * (3 - 2 * u)
            pos_pe[lado] = pos_pe[lado].lerp(destino, e_) + Vector((0, 0, 0.06 * math.sin(math.pi * u)))
            yaw_pe[lado] = yaw_pe[lado] + (yw - yaw_pe[lado]) * e_
            incl[lado] = -16 * math.sin(math.pi * min(1, u * 1.6)) * (1 - u) + 10 * math.sin(math.pi * u) * u
            bob = 0.012 * math.sin(math.pi * u) - 0.006; bal = sg * math.sin(math.pi * u)
        break
    pos = A + d * B.suave((g - t0) / (t1 - t0))
    pes = {l: ((pos_pe[l].x, pos_pe[l].y, ALT + pos_pe[l].z), yaw_pe[l], incl[l]) for l in ('d', 'e')}
    return (pos.x, pos.y), yaw, bob, pes, bal


ALT = PE.ALT_TORNOZELO
PA = (-0.60, -0.86); YA = -47.0          # diante do puxador
PB = (-0.84, -1.20); YB = -38.0          # um passo atrás, olhando a geladeira inteira
INTERIOR = (0.0, -0.05, 1.00); TOPO_TRAS = (0.0, 0.38, 1.80); BATENTE_E = (-0.31, -0.37, 1.22)


def _mao_puxando(lado_d_estado, g, t_alcance, t_puxa, ang, pos, yaw):
    """Mão direita: repouso → puxador (antes de puxar) → acompanha o puxador até 38° → volta ao repouso."""
    a = ang(g); t_solta = t_puxa + (SOLTA_R9 if R9 else 0.46) * 1.1          # porta a ~38° (smoothstep = 0,38); R9: ~20° (o antebraço não cruza o painel)
    rest = repouso('d', pos, yaw)
    if g < t_alcance: return rest
    if g < t_puxa: return PE.trilha([(t_alcance, rest), (t_puxa - 0.04, tuple(alca(0)))], g)
    if g < t_solta: return tuple(alca(a))
    if R9:   # rodada 9: recua primeiro para a ESQUERDA e para trás (fora do arco que a borda da porta ainda varre), depois desce
        p0 = alca(ang(t_solta)); return PE.trilha([(t_solta, tuple(p0)), (t_solta + 0.14, tuple(p0 + Vector((-0.17, -0.12, -0.04)))), (t_solta + 0.50, rest)], g)
    return PE.trilha([(t_solta, tuple(alca(ang(t_solta)))), (t_solta + 0.45, rest)], g)


def est_abertura(g):
    """A1–A4 (g de −0,25 a 10,4 s). A1 abre a porta; A2 olha o interior apoiando a mão no batente; A3 recua um passo
    olhando o alto da traseira (fora de quadro); A4 reage à pergunta: estranhamento contido e mão no queixo."""
    ang = porta_ang(0.20)
    t_pens = T('ao')          # "ao mesmo tempo?"
    pos, fase = _caminhada(g, 3.05, 4.20, PA, PB)
    yaw = PE.trilha([(3.05, YA), (4.20, YB)], g)
    e = dict(pos=pos, yaw=yaw, passo=(-fase[0], fase[1]) if fase else None, t=g)      # recua de costas: fase negativa (fora de quadro)
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
    e['incl'] = PE.trilha([(0.15, 0.0), (0.35, -3.0), (0.70, 0.0), (1.5, 0.0), (1.9, 7.0), (2.85, 7.0), (3.2, 0.0),
                           (4.30, -3.5), (4.95, -3.5), (5.70, 0.0)], g)      # rodada 8: inclinado para trás olhando o alto da traseira
    e['giro'] = PE.trilha([(4.85, 6.0), (5.05, 6.0), (5.75, 0.0)], g)       # rodada 8: o tronco acompanha a cabeça com atraso (overlap)
    # olhar: puxador → interior (fria por dentro) → alto da traseira (quente por fora) → reação
    alvo = PE.trilha([(-0.25, tuple(alca(0))), (0.45, tuple(alca(20))), (0.95, INTERIOR), (T('fria'), INTERIOR), (2.6, (0.05, -0.05, 0.9)),
                      (T('quente') - 0.35, TOPO_TRAS), (4.80, TOPO_TRAS), (5.50, INTERIOR),     # rodada 8: A4 começa com ele AINDA olhando o que A3 mostrou
                      (T('mesma') + 0.2, INTERIOR), (T('duas') - 0.1, TOPO_TRAS), (T('coisas') + 0.2, INTERIOR), (t_pens + 0.1, (0.15, 0.30, 1.72))], g)
    cy, cp = olhar(pos, yaw, alvo, incl=e['incl'])
    rol = PE.trilha([(T('parece'), 0.0), (T('parece') + 0.4, -7.0), (T('mesma'), -3.0), (t_pens, -3.0), (t_pens + 0.5, -9.0)], g)
    e['cab'] = (cy * 0.85, cp * 0.85, rol); e['olhar'] = (cy * 0.15, cp * 0.2)
    sob = PE.trilha([(1.4, 0.0), (T('fria'), 0.25), (2.6, 0.1), (T('quente'), 0.5), (T('parece'), 0.65), (6.0, 0.35),
                     (t_pens, 0.35), (t_pens + 0.4, 0.55)], g)
    inc = PE.trilha([(T('parece'), 0.0), (T('parece') + 0.4, 0.45), (6.0, 0.2), (t_pens + 0.4, 0.35)], g)
    ass = PE.trilha([(t_pens, 0.0), (t_pens + 0.45, 0.30)], g)     # v4: uma sobrancelha um pouco mais alta ao pensar
    e['sobr'] = (sob, inc, ass); e['piscar'] = PE.piscadas(g, [1.15, 3.55, 5.25, 6.9, 8.85])   # rodada 8: piscada na virada do olhar
    return e


PI = (-1.38, -1.48)                       # entrada pela esquerda em I1
PC = (-1.45, -0.95); YC = -62.7           # recuo: de lado, olhando a geladeira aberta (fora do caminho do calor)
PG = (-0.45, -0.55); YG = -35.0          # rodada 8: um passo à frente, diante da abertura (a porta já passou de 60°)
PX = (-1.32, -1.30)                       # saída pela esquerda (fora de quadro logo depois)
LEITE_I1 = Vector((-0.19, -0.22, 0.84 + 0.098))   # leite na frente esquerda da prateleira de cima (só no I1)
T_PASSO = (118.05, 118.40); T_PEGA = 118.66; T_SAI = (118.80, 119.70)
# ---- rodada 9 (CENA_R9=1; desligado = V8): leite numa posição ÚNICA em todos os planos, ao alcance da mão (testar_leite.py
# achou no I1 da V8: braço 3 cm dentro do painel da porta, mão 13 cm longe da caixa na pega, caixa 2,4 mm dentro do vidro)
R9 = os.environ.get('CENA_R9', '0') == '1'
SOLTA_R9 = 0.30                                   # solta o puxador a ~20°: a porta segue pelo embalo (o antebraço não cruza o painel)
LEITE_R9 = Vector((-0.12, -0.22, 0.84 + 0.098))   # frente da prateleira de cima, um pouco à esquerda (iogurtes 2,5 cm à direita)
if R9:
    LEITE_I1 = LEITE_R9; PG = (-0.40, -0.50); YG = -30.0
    T_PASSO = (117.92, 118.22); T_PEGA = 118.44; T_SAI = (118.62, 119.55)   # pega 0,22 s antes; saída visível ~0,55 s
PEGA_R9 = (0.0, -0.083, 0.015)                    # pulso diante da face da frente da caixa: a mão fechada encosta nela
PA_I1 = (-0.42, -0.70)                            # rodada 9: diante do puxador e ao alcance do braço (fora do arco da porta)
def tempos_passos_i1():
    """Pousos dos pés no I1 (para o som): entrada (3), passo à frente (1), saída (2)."""
    return [115.55 + (116.95 - 115.55) * k / 3 for k in (1, 2, 3)] + [T_PASSO[1]] + [T_SAI[0] + (T_SAI[1] - T_SAI[0]) * k / 2 for k in (1, 2)]


def est_porta_aberta(g):
    """I1–I4. I1: entra, abre a porta, solta e recua um passo — a porta FICA aberta; I2: sai de quadro pela esquerda;
    I3: acompanha com o olhar o calor que volta à cozinha; I4: ergue o olhar para o calor liberado atrás da geladeira."""
    t_puxa = T('deixa') - 0.13                 # a porta começa a abrir em "deixa a porta aberta"
    ang = porta_ang(t_puxa)
    # rodada 8: entra, abre, dá um passo à frente, PEGA o leite e sai com ele pela esquerda — a porta fica aberta
    YX = 123.0                                   # de frente para a saída (vira ~170° andando)
    pa = PA_I1 if R9 else PA   # rodada 9: para ao alcance do puxador (da V8 o puxador ficava 15 cm além do braço)
    if g < T_PASSO[0]: pos, yaw, bob_, pes, bl = passada(g, 115.55, 116.95, PI, pa, -52.0, YA)
    elif g < T_SAI[0]: pos, yaw, bob_, pes, bl = passada(g, T_PASSO[0], T_PASSO[1], pa, PG, YA, YG, fracs=(1.0,), largura=0.10)
    else: pos, yaw, bob_, pes, bl = passada(g, T_SAI[0], T_SAI[1], PG, PX, YG, YX, fracs=(0.5, 1.0), largura=0.10)
    e = dict(pos=pos, yaw=yaw, bob=bob_, pes=pes, t=g)
    bal = lambda sgn: -sgn * 0.07 * bl
    md = _mao_puxando(None, g, t_puxa - 0.45, t_puxa, ang, pos, yaw)
    if g < 117.0: md = repouso('d', pos, yaw, bal(1))
    pega = tuple(LEITE_I1 + Vector((0.0, 0.0, 0.02)))                        # pulso tal que a mão fechada encoste na frente da caixa
    junto = tuple(corpo(PG, YG, (0.20, 0.16, 0.92)))                          # leite recolhido junto ao corpo
    if R9 and g >= T_PEGA - 0.28:   # rodada 9: alcança → pega → ERGUE 2 cm (passa sobre a borda) → puxa para fora → recolhe → desce
        pega = tuple(LEITE_I1 + Vector(PEGA_R9))
        sobe = tuple(Vector(pega) + Vector((0.0, -0.010, 0.032))); fora = tuple(Vector(pega) + Vector((0.0, -0.17, 0.030)))
        md = PE.trilha([(T_PEGA - 0.28, tuple(md)), (T_PEGA, pega), (T_PEGA + 0.03, pega), (T_PEGA + 0.11, sobe), (T_PEGA + 0.25, fora),
                        (T_PEGA + 0.42, junto), (T_SAI[0] + 0.55, repouso('d', pos, yaw, 0.04))], g) if g < T_SAI[0] + 0.55 else repouso('d', pos, yaw, bal(1) * 0.4)
    elif not R9 and g >= 118.20:   # alcança → pega → recolhe → desce ao lado do corpo (andando)
        md = PE.trilha([(118.20, tuple(md)), (T_PEGA, pega), (T_PEGA + 0.08, pega), (T_PEGA + 0.35, junto),
                        (T_SAI[0] + 0.45, repouso('d', pos, yaw, 0.04))], g) if g < T_SAI[0] + 0.45 else repouso('d', pos, yaw, bal(1) * 0.4)
    e['braco_d'] = ('ik', md, tuple(corpo(pos, yaw, (0.7, -0.4, -1.0))), (0, 0, -1))
    e['fecha_d'] = g >= T_PEGA - 0.04                                       # mão fechada segurando a caixa
    e['braco_e'] = ('ik', repouso('e', pos, yaw, bal(-1)), tuple(corpo(pos, yaw, (-0.7, -0.4, -1.0))), (0, 0, -1))
    e['incl'] = PE.trilha([(t_puxa, 0.0), (t_puxa + 0.2, -3.0), (t_puxa + 0.55, 0.0), (118.30, 0.0), (T_PEGA, 11.0),
                           (T_PEGA + 0.3, 3.0), (T_SAI[0] + 0.3, 0.0)], g)
    t_volta = T('cômodo'); t_lib = T('libera')
    alvo = PE.trilha([(115.55, (-0.2, -0.3, 1.2)), (116.9, tuple(alca(0))), (t_puxa + 0.4, tuple(alca(30))), (118.15, tuple(LEITE_I1)),
                      (T_PEGA + 0.1, tuple(LEITE_I1)), (T_SAI[0] + 0.25, (-2.6, -1.9, 1.45)), (T_SAI[1], (-2.6, -1.9, 1.45)),
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
