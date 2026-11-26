"""Personagem ORIGINAL do Ep. 02 — "o morador": uma pessoa comum na própria cozinha (o "você" da narração).
Recurso narrativo de identificação, NÃO mascote nem assinatura do canal. Deliberadamente diferente do mascote oficial
(episodio_01_navio_v2/referencias/mascote_oficial.png: menino explorador, óculos, casaco azul-marinho, lenço amarelo),
que não foi usado nem redesenhado.

Desenho: proporções de adulto levemente estilizadas (cabeça um pouco maior), formas arredondadas e materiais foscos,
como o resto do episódio. Cores neutras que NÃO usam a linguagem didática (azul = frio, laranja/vermelho = quente,
âmbar = calor, violeta = trabalho, amarelo = corte): suéter cinza-mescla quente, calça grafite, tênis claro.
Expressão sem fala e sem exagero: direção do olhar, piscada, sobrancelhas, inclinação da cabeça e postura.
Na visão térmica o corpo aparece morno (pele 33 °C, roupa 30 °C) — é física real, não enfeite.

Construção: partes RÍGIDAS (sem deformação), cada uma é um objeto 'anim' que recebe a sua matriz por quadro no
exportador existente. Braços com cinemática inversa de dois ossos (a mão segue o puxador de verdade).
Uso: p = montar(); posar(p, estado) a cada quadro.  estado: ver ESTADO_PADRAO."""
import math
import bpy
from mathutils import Vector, Matrix
import lib, mats02 as M

ALT_TORNOZELO = 0.095                               # polimento: pés sobre o porcelanato (5 mm)
COXA, CANELA = 0.385, 0.38
BRACO, ANTEBRACO = 0.27, 0.25
QUADRIL_Z = ALT_TORNOZELO + COXA + CANELA + 0.02   # polimento: o quadril real fica 3 cm abaixo do pivô — joelhos só levemente flexionados
OMBRO_LOCAL = (0.168, 0.0, 0.455)                  # no espaço do tronco
QUADRIL_LOCAL = (0.09, 0.0, -0.03)
PESCOCO_LOCAL = (0.0, 0.0, 0.535)


# ------------------------------------------------------------------ geometria (malhas com origem na articulação)
def _superelipsoide(c, r, p=2.0, nu=24, nv=14, th0=-math.pi / 2):
    v, f = [], []
    sg = lambda x, e: math.copysign(abs(x) ** e, x)
    for j in range(nv + 1):
        th = th0 + (math.pi / 2 - th0) * j / nv
        for i in range(nu):
            ph = 2 * math.pi * i / nu
            e = 2.0 / p
            x = r[0] * sg(math.cos(th), e) * sg(math.cos(ph), e); y = r[1] * sg(math.cos(th), e) * sg(math.sin(ph), e); z = r[2] * sg(math.sin(th), e)
            v.append((c[0] + x, c[1] + y, c[2] + z))
    for j in range(nv):
        for i in range(nu):
            a, b = j * nu + i, j * nu + (i + 1) % nu
            f.append((a, b, b + nu, a + nu))
    return v, f


def _tronco_torneado(n=28):
    """Tronco único: seção superelíptica (p 2,6) com largura/profundidade variando suavemente da cintura ao peito."""
    perfil = [(0.00, 0.150, 0.098), (0.08, 0.152, 0.100), (0.18, 0.160, 0.104), (0.28, 0.176, 0.112), (0.38, 0.188, 0.116),
              (0.45, 0.186, 0.112), (0.49, 0.172, 0.102), (0.515, 0.140, 0.085), (0.528, 0.095, 0.060), (0.533, 0.0, 0.0)]
    sg = lambda x, e: math.copysign(abs(x) ** e, x); e = 2 / 2.6
    v = [(0.0, 0.0, -0.012)]; f = []
    for (z, w, d) in perfil:
        for i in range(n):
            ph = 2 * math.pi * i / n; v.append((max(w, 1e-4) * sg(math.cos(ph), e), max(d, 1e-4) * sg(math.sin(ph), e), z))
    for i in range(n): f.append((0, 1 + (i + 1) % n, 1 + i))
    for j in range(len(perfil) - 1):
        for i in range(n):
            a, b = 1 + j * n + i, 1 + j * n + (i + 1) % n; f.append((a, b, b + n, a + n))
    return v, f


def _girar_x(vf, graus, centro):
    c = math.cos(math.radians(graus)); s_ = math.sin(math.radians(graus)); out = []
    for (x, y, z) in vf[0]:
        yy, zz = y - centro[1], z - centro[2]; out.append((x, centro[1] + yy * c - zz * s_, centro[2] + yy * s_ + zz * c))
    return out, vf[1]


def _mover(vf, d):
    return [(x + d[0], y + d[1], z + d[2]) for (x, y, z) in vf[0]], vf[1]


def _mao(sx):
    """Mão (polimento): palma, quatro dedos levemente curvados para a frente e polegar — no lugar da luva única."""
    partes = [_superelipsoide((0, 0.002, -0.036), (0.036, 0.019, 0.04), 2.3, 16, 10)]
    for k, (dx, L) in enumerate(((-0.024, 0.040), (-0.008, 0.046), (0.008, 0.044), (0.024, 0.036))):
        dedo = _girar_x(_capsula(L, 0.0088, 0.0078, 10, 4), 14, (0, 0, 0))
        partes.append(_mover(dedo, (sx * dx, 0.004, -0.068)))
    partes.append(_mover(_girar_x(_capsula(0.034, 0.0105, 0.009, 10, 4), 35, (0, 0, 0)), (sx * -0.034, 0.014, -0.022)))
    return _juntar(*partes)


def _ao_longo_x(vf, sx):
    """Cápsula feita ao longo de −Z passa a apontar para ±X (sx)."""
    return [(-z * sx, y, x) for (x, y, z) in vf[0]], vf[1]


def _mao_fechada(sx):
    """Rodada 5 (pedido do usuário): mão FECHADA e relaxada para o apoio sob o queixo — mesma palma e mesmo comprimento da
    mão aberta (≈ 0,10 m, então o ponto de contato e o braço não mudam); dedos dobrados formam a fileira dos nós na ponta
    (a parte que encosta no queixo), as pontas e o polegar ficam do lado do pescoço; para fora (câmera) fica o dorso dos dedos dobrados."""
    partes = [_superelipsoide((0, 0.002, -0.040), (0.036, 0.020, 0.044), 2.3, 16, 10)]
    for dx, r in ((-0.024, 0.0092), (-0.008, 0.0102), (0.008, 0.0100), (0.024, 0.0090)):
        partes.append(_mover(_girar_x(_capsula(0.038, r, r * 0.95, 10, 4), 90, (0, 0, 0)), (sx * dx, -0.024, -0.0885)))   # dedos dobrados: fileira dos nós
        partes.append(_mover(_capsula(0.016, r * 0.95, r * 0.9, 10, 4), (sx * dx, -0.026, -0.072)))                      # pontas recolhidas (lado do pescoço)
    partes.append(_mover(_ao_longo_x(_capsula(0.030, 0.0100, 0.0088, 10, 4), sx), (sx * -0.032, -0.034, -0.064)))       # polegar (lado do pescoço)
    return _juntar(*partes)


def _capsula(L, r0, r1, n=18, anel=8):
    """Cápsula da origem (raio r0) até z = −L (raio r1), com calotas hemisféricas."""
    v, f = [], []
    perfil = []
    for k in range(anel + 1):                     # calota de cima
        a = math.pi / 2 * (1 - k / anel); perfil.append((r0 * math.cos(a), r0 * math.sin(a)))
    for k in range(1, 6):
        t = k / 5; perfil.append((r0 + (r1 - r0) * t, -L * t))
    for k in range(1, anel + 1):                  # calota de baixo
        a = math.pi / 2 * k / anel; perfil.append((r1 * math.cos(a), -L - r1 * math.sin(a)))
    for (rr, z) in perfil:
        for i in range(n):
            ph = 2 * math.pi * i / n; v.append((rr * math.cos(ph), rr * math.sin(ph), z))
    for j in range(len(perfil) - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n; f.append((a, b, b + n, a + n))
    return v, f


def _juntar(*partes):
    V, Fc = [], []
    for (v, f) in partes:
        o = len(V); V += v; Fc += [tuple(i + o for i in q) for q in f]
    return V, Fc


def _obj(nome, vf, mat):
    o = lib.malha(nome, vf[0], vf[1], mat, suave=True, angulo=80); o['anim'] = 1; return o


def materiais():
    return dict(
        pele=M.pintura('pers_pele', '#c58a66', rug=0.55, temp=33.0),
        cabelo=M.pintura('pers_cabelo', '#33261f', rug=0.7, temp=31.0),
        sueter=M.pintura('pers_sueter', '#8c8781', rug=0.93, variacao=0.03, escala_var=14.0, temp=30.0),    # polimento: malha fosca
        punho=M.pintura('pers_punho', '#7a756f', rug=0.95, variacao=0.05, escala_var=20.0, temp=30.0),      # punhos, barra e gola canelados
        calca=M.pintura('pers_calca', '#3a3e45', rug=0.8, variacao=0.04, escala_var=8.0, temp=30.0),
        tenis=M.pintura('pers_tenis', '#e6e2da', rug=0.5, temp=27.0),
        sola=M.pintura('pers_sola', '#9a948c', rug=0.6, temp=27.0),
        olho=M.pintura('pers_olho', '#f4f1ea', rug=0.25, coat=0.6, temp=33.0),
        iris=M.pintura('pers_iris', '#2c1d16', rug=0.15, coat=0.9, temp=33.0),
        boca=M.pintura('pers_boca', '#7a4436', rug=0.6, temp=33.0))


def montar():
    m = materiais(); P = {}
    P['pelve'] = _obj('pers_pelve', _superelipsoide((0, 0, -0.02), (0.165, 0.105, 0.095), 2.6), m['calca'])
    P['tronco'] = _obj('pers_tronco', _tronco_torneado(), m['sueter'])
    P['barra'] = _obj('pers_barra', _juntar(_superelipsoide((0, 0, 0.035), (0.157, 0.104, 0.04), 2.6, 28, 8),          # barra canelada
                                            _superelipsoide((0, 0.0, 0.53), (0.068, 0.064, 0.03), 2.0)), m['punho'])   # gola
    P['cabeca'] = _obj('pers_cabeca', _juntar(_capsula(0.0, 0.045, 0.045),                                             # pescoço
                                              _superelipsoide((0, 0, 0.13), (0.112, 0.118, 0.128), 2.0, 32, 18),
                                              _superelipsoide((0.112, -0.005, 0.12), (0.016, 0.03, 0.036), 2.0, 12, 8),  # orelhas
                                              _superelipsoide((-0.112, -0.005, 0.12), (0.016, 0.03, 0.036), 2.0, 12, 8),
                                              _superelipsoide((0, 0.117, 0.118), (0.0125, 0.014, 0.017), 2.0, 12, 8)), m['pele'])  # nariz
    # cabelo curto: calota lisa só na parte de cima/trás (linha do cabelo alta e limpa, sem serrilhado)
    # calota inclinada 28° em X: linha do cabelo alta na testa (≈ 0,20) e baixa na nuca (≈ 0,08); cobre as orelhas só em cima
    P['cabelo'] = _obj('pers_cabelo', _girar_x(_superelipsoide((0, -0.012, 0.165), (0.123, 0.13, 0.125), 2.15, 36, 14, th0=-0.25), 28, (0, -0.012, 0.165)), m['cabelo'])
    P['boca'] = _obj('pers_boca', _superelipsoide((0, 0.112, 0.068), (0.026, 0.008, 0.006), 2.0, 12, 6), m['boca'])
    for lado, sx in (('d', 1), ('e', -1)):
        P[f'olho_{lado}'] = _obj(f'pers_olho_{lado}', _superelipsoide((0, 0, 0), (0.019, 0.012, 0.023), 2.0, 16, 10), m['olho'])
        P[f'iris_{lado}'] = _obj(f'pers_iris_{lado}', _superelipsoide((0, 0.009, 0), (0.0122, 0.006, 0.0145), 2.0, 14, 8), m['iris'])
        P[f'palp_{lado}'] = _obj(f'pers_palp_{lado}', _superelipsoide((0, 0.001, 0), (0.0215, 0.0145, 0.0255), 2.0, 16, 8, th0=0.0), m['pele'])  # pálpebra
        P[f'sobr_{lado}'] = _obj(f'pers_sobr_{lado}', _superelipsoide((0, 0, 0), (0.024, 0.006, 0.0065), 2.0, 12, 6), m['cabelo'])
        P[f'braco_{lado}'] = _obj(f'pers_braco_{lado}', _capsula(BRACO, 0.05, 0.043), m['sueter'])
        P[f'antebraco_{lado}'] = _obj(f'pers_antebraco_{lado}', _capsula(ANTEBRACO - 0.04, 0.043, 0.037), m['sueter'])
        P[f'punho_{lado}'] = _obj(f'pers_punho_{lado}', _superelipsoide((0, 0, -ANTEBRACO + 0.03), (0.041, 0.041, 0.03), 2.4, 16, 8), m['punho'])
        P[f'mao_{lado}'] = _obj(f'pers_mao_{lado}', _mao(sx), m['pele'])
        P[f'maof_{lado}'] = _obj(f'pers_maof_{lado}', _mao_fechada(sx), m['pele'])     # só aparece no apoio sob o queixo
        P[f'coxa_{lado}'] = _obj(f'pers_coxa_{lado}', _capsula(COXA, 0.082, 0.064), m['calca'])
        P[f'canela_{lado}'] = _obj(f'pers_canela_{lado}', _capsula(CANELA, 0.062, 0.05), m['calca'])
        P[f'pe_{lado}'] = _obj(f'pers_pe_{lado}', _juntar(_superelipsoide((0, 0.055, -0.04), (0.055, 0.125, 0.048), 2.6),
                                                        _superelipsoide((0, 0.055, -0.083), (0.058, 0.128, 0.012), 3.0)), m['tenis'])
    return P


# ------------------------------------------------------------------ poses
ESTADO_PADRAO = dict(pos=(0.0, 0.0), yaw=0.0, bob=0.0, incl=0.0, giro=0.0, cab=(0.0, 0.0, 0.0), olhar=(0.0, 0.0),
                     piscar=0.0, sobr=(0.0, 0.0), passo=None,
                     braco_d=('fk', 8.0, 6.0, 12.0), braco_e=('fk', 8.0, 6.0, 12.0))


def _rot(eixo, graus): return Matrix.Rotation(math.radians(graus), 4, eixo)


def _segmento(origem, direcao, frente):
    """Matriz com origem na articulação e −Z local apontando para a próxima articulação; frente define a torção."""
    z = (-direcao).normalized(); fr = frente - z * frente.dot(z)
    if fr.length < 1e-6: fr = Vector((0, 1, 0)) - z * z.y
    y = fr.normalized(); x = y.cross(z)
    Mx = Matrix(((x.x, y.x, z.x, origem.x), (x.y, y.y, z.y, origem.y), (x.z, y.z, z.z, origem.z), (0, 0, 0, 1)))
    return Mx


def _ik(S, T, a, b, polo):
    d = T - S; L = min(max(d.length, abs(a - b) + 1e-3), a + b - 1e-3); u = d.normalized()
    ca = (a * a + L * L - b * b) / (2 * a * L); al = math.acos(max(-1, min(1, ca)))
    v = (polo - u * polo.dot(u)); v = v.normalized() if v.length > 1e-6 else Vector((0, 0, -1))
    E = S + (u * math.cos(al) + v * math.sin(al)) * a
    return E, S + u * L


def posar(P, e):
    e = dict(ESTADO_PADRAO, **e)
    W = Matrix.Translation(Vector((e['pos'][0], e['pos'][1], 0.0))) @ _rot('Z', e['yaw'])     # frente = +Y local
    fase = e['passo']                                     # None (parado) ou (fase em ciclos, amplitude 0–1)
    bob = e['bob'] + (0.012 * abs(math.sin(2 * math.pi * fase[0])) * fase[1] if fase else 0.0)
    pelve = W @ Matrix.Translation((0, 0, QUADRIL_Z + bob)) @ _rot('Z', e['giro'] * 0.3)
    tronco = W @ Matrix.Translation((0, 0, QUADRIL_Z + bob + 0.02)) @ _rot('Z', e['giro']) @ _rot('X', e['incl'])
    if e.get('t') is not None and not fase:   # vida em repouso: respiração lenta e leve oscilação do tronco
        tt = e['t']; tronco = tronco @ _rot('X', 0.5 * math.sin(2 * math.pi * 0.24 * tt + 1.0)) @ Matrix.Diagonal((1.0, 1.0 + 0.006 * math.sin(2 * math.pi * 0.24 * tt), 1.0, 1.0))
    P['pelve'].matrix_world = pelve; P['tronco'].matrix_world = tronco; P['barra'].matrix_world = tronco
    cy, cp, cr = e['cab']
    cab = tronco @ Matrix.Translation(PESCOCO_LOCAL) @ _rot('Z', cy) @ _rot('X', cp) @ _rot('Y', cr)
    P['cabeca'].matrix_world = cab; P['cabelo'].matrix_world = cab; P['boca'].matrix_world = cab
    oy, op = e['olhar']; pisca = max(0.08, 1.0 - e['piscar']); sob, inc = e['sobr'][:2]; ass = e['sobr'][2] if len(e['sobr']) > 2 else 0.0
    for lado, sx in (('d', 1), ('e', -1)):
        base = cab @ Matrix.Translation((sx * 0.043, 0.104, 0.142)) @ _rot('Z', sx * -8)          # olhos levemente para fora
        P[f'olho_{lado}'].matrix_world = base
        P[f'iris_{lado}'].matrix_world = base @ _rot('Z', oy + sx * 8) @ _rot('X', op)
        # pálpebra superior: em repouso cobre o terço de cima (olhar calmo); desce até fechar na piscada; sobe um pouco com as sobrancelhas
        # (a calota z ≥ 0 girada em X: a borda da frente sobe com ângulo positivo; −90° = olho fechado)
        P[f'palp_{lado}'].matrix_world = base @ _rot('X', 34 + 10 * max(0.0, sob) - 124 * (1.0 - pisca))
        sl = sob + sx * ass        # assimetria: uma sobrancelha um pouco mais alta (curiosidade contida)
        P[f'sobr_{lado}'].matrix_world = cab @ Matrix.Translation((sx * 0.046, 0.106, 0.183 + 0.012 * sl)) @ _rot('Y', sx * (6 + 14 * inc))
    # braços
    frente_w = (tronco.to_3x3() @ Vector((0, 1, 0))).normalized()
    for lado, sx in (('d', 1), ('e', -1)):
        S = tronco @ Vector((sx * OMBRO_LOCAL[0], OMBRO_LOCAL[1], OMBRO_LOCAL[2]))
        b = e[f'braco_{lado}']; fechada = (b[0] == 'queixo' and b[1] > 0.15) or bool(e.get('fecha_' + lado))   # queixo ou segurando um objeto
        if b[0] == 'queixo':   # ('queixo', k, repouso, polo): a mão sai do repouso e APOIA sob o queixo da cabeça já posicionada
            k = b[1]; R3 = cab.to_3x3(); cima = (R3 @ Vector((0, 0.15, 1))).normalized()
            contato = cab @ Vector((sx * 0.012, 0.100, 0.040))                  # sob o queixo, levemente para o lado da mão
            pulso = contato - cima * 0.098                                     # a ponta da mão (0,10 m) toca o contato
            alvo = Vector(b[2]).lerp(pulso, k)
            b = ('ik', tuple(alvo), b[3], tuple((Vector((0, 0, -1)).lerp(cima, k)).normalized()))
        if b[0] == 'ik':
            T = Vector(b[1]); polo = Vector(b[2]) if len(b) > 2 else (tronco.to_3x3() @ Vector((sx * 0.6, -0.5, -1.0)))
            E, T = _ik(S, T, BRACO, ANTEBRACO, polo)
        else:   # fk: (flexão para a frente, abdução, flexão do cotovelo) em graus
            _, fl, ab, cot = b
            R = tronco.to_3x3() @ (Matrix.Rotation(math.radians(sx * ab), 3, 'Y') @ Matrix.Rotation(math.radians(-fl), 3, 'X'))
            E = S + R @ Vector((0, 0, -BRACO))
            R2 = R @ Matrix.Rotation(math.radians(-cot), 3, 'X'); T = E + R2 @ Vector((0, 0, -ANTEBRACO))
        P[f'braco_{lado}'].matrix_world = _segmento(S, (E - S).normalized(), frente_w)
        P[f'antebraco_{lado}'].matrix_world = _segmento(E, (T - E).normalized(), frente_w)
        P[f'punho_{lado}'].matrix_world = P[f'antebraco_{lado}'].matrix_world
        mao_dir = (T - E).normalized() if b[0] == 'fk' else ((T - E).normalized() * 0.7 + Vector(b[3] if len(b) > 3 else (0, 0, -1)) * 0.3).normalized()
        Mm = _segmento(T, mao_dir, frente_w); oculta = Matrix.Translation(E.lerp(T, 0.9)) @ Matrix.Scale(1e-4, 4)   # escondida dentro do punho
        if 'maof_' + lado in P:
            P[f'mao_{lado}'].matrix_world = oculta if fechada else Mm; P[f'maof_{lado}'].matrix_world = Mm if fechada else oculta
        else: P[f'mao_{lado}'].matrix_world = Mm
    # pernas: parado (leve flexão) ou caminhada simples
    for lado, sx, ph in (('d', 1, 0.0), ('e', -1, 0.5)):
        H = pelve @ Vector((sx * QUADRIL_LOCAL[0], QUADRIL_LOCAL[1], QUADRIL_LOCAL[2]))
        if fase:
            s = math.sin(2 * math.pi * (fase[0] + ph)); amp = fase[1]
            quad = 22 * s * amp; joelho = (8 + 30 * max(0.0, math.sin(2 * math.pi * (fase[0] + ph) + 1.2))) * amp + 3
        else:
            quad, joelho = 2.0, 4.0
        fr = (W.to_3x3() @ Vector((0, 1, 0)))
        if e.get('pes'):   # polimento: pé PLANTADO no chão (alvo do tornozelo) e joelho por cinemática inversa
            alvo, yaw_pe, incl_pe = e['pes'][lado]
            K, A = _ik(H, Vector(alvo), COXA, CANELA, fr * 1.0 + Vector((0, 0, -0.2)))
            P[f'coxa_{lado}'].matrix_world = _segmento(H, (K - H).normalized(), fr)
            P[f'canela_{lado}'].matrix_world = _segmento(K, (A - K).normalized(), fr)
            P[f'pe_{lado}'].matrix_world = Matrix.Translation(A) @ _rot('Z', yaw_pe) @ _rot('X', incl_pe)
            continue
        R = W.to_3x3() @ Matrix.Rotation(math.radians(e['giro'] * 0.3), 3, 'Z') @ Matrix.Rotation(math.radians(quad), 3, 'X')
        K = H + R @ Vector((0, 0, -COXA))
        R2 = R @ Matrix.Rotation(math.radians(-joelho), 3, 'X'); A = K + R2 @ Vector((0, 0, -CANELA))
        P[f'coxa_{lado}'].matrix_world = _segmento(H, (K - H).normalized(), fr)
        P[f'canela_{lado}'].matrix_world = _segmento(K, (A - K).normalized(), fr)
        pe = W.copy(); pe.translation = A
        if fase: pe = pe @ _rot('X', -10 * math.sin(2 * math.pi * (fase[0] + ph)) * fase[1])
        P[f'pe_{lado}'].matrix_world = pe


# ------------------------------------------------------------------ trilhas de animação (chaves com suavização)
def trilha(chaves, g):
    """chaves = [(t, valor)], valor escalar, tupla ou vetor; interpolação smoothstep entre chaves."""
    if g <= chaves[0][0]: return chaves[0][1]
    for (t0, v0), (t1, v1) in zip(chaves, chaves[1:]):
        if g <= t1:
            k = (g - t0) / max(t1 - t0, 1e-9); k = k * k * (3 - 2 * k)
            if isinstance(v0, (tuple, list)):
                if v0 and isinstance(v0[0], str): return v0 if k < 0.5 else v1
                return tuple(a + (b - a) * k for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * k
    return chaves[-1][1]


def piscadas(g, instantes, dur=0.13):
    for t in instantes:
        if t <= g <= t + dur: return math.sin(math.pi * (g - t) / dur)
    return 0.0
