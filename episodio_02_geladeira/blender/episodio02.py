"""Linha do tempo do Ep. 02: os 40 planos da decupagem (decupagem/planos.py) sobre UM modelo mestre (geladeira.py).
Cada plano é exportado como um segmento próprio (com margem para as fusões) → re-render só do que mudar.
Tempos: âncoras em palavras (narração aprovada quando existir; senão, tempos provisórios). Câmeras por frações do plano.
Uso: PYTHONPATH=<bpy> python3 episodio02.py [planos...]   (sem argumentos: todos)"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import lib, mats02 as M, geladeira as G, ep_base as B, cenas02 as C, compressor_mec as CM
COND_Y = G.COND_Y

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(AQUI, '..')
SAIDA = os.path.join(RAIZ, 'episodio', 'cenas')
PL = C.PLANOS
MARGEM = 0.25    # quadros extras antes/depois de cada plano (fusões na montagem)
MOD = json.load(open(os.path.join(RAIZ, 'ciencia', 'ciclo_modelo.json')))
BASE = lambda p: p[:2]
T0 = lambda p: PL[BASE(p)]['t0']; T1 = lambda p: PL[BASE(p)]['t1']
def F(p, f): return T0(p) + (T1(p) - T0(p)) * f       # instante a uma fração do plano


# ------------------------------------------------------------------ peças por plano
def feixe(nome, pts, r=0.012, curvas=None, sobre=False, onda=7.0, vel=0.7, cor='#ffb43a'):
    m = M.calor('calor_' + nome, cor=cor, onda=onda, vel=vel)
    M.ajustar(m, curvas=curvas or {}, sobre=sobre)
    return M.varrer('feixe_' + nome, M.reamostrar(M.suavizar(pts, 0.08, 6), 0.02), r, m, 0.0, 1.0, lados=10)


def calor_traseira(pid, t0, t1):
    """Calor rejeitado: feixes que sobem da serpentina traseira para o ar da cozinha (mesma linguagem de F1/J4)."""
    for i, x in enumerate([-0.18, 0.0, 0.18]):
        feixe(f'{pid}_tras{i}', [(x, 0.40, 0.75 + 0.15 * i), (x, 0.43, 1.25), (x * 1.3, 0.45, 1.85)], 0.010, cresce(t0 + 0.12 * i, t1), onda=7)


def canal_esticado(pid, trecho, p0, p1, r, fundo_y):
    """CORTE ILUSTRATIVO (esquema): o canal inteiro de um trocador (evaporador ou condensador) esticado em linha reta e
    ampliado. O fluido usa a MESMA tabela do ciclo (s global do trecho → T, título x), então a fração líquida ao longo do
    tubo é a do modelo, ponto a ponto. Só a escala muda: o comprimento real vira |p1 − p0| (a coordenada de fluxo é
    reescalada na mesma proporção, por isso o aviso "Fluxo desacelerado"). Fundo neutro atrás, para isolar o mecanismo."""
    tr = {t['id']: t for t in G.circuito_param()[0]}[trecho]; lut = G.tabela_fluido(); n = lut['n']; U = lut['u']; V = lut['u_volta']
    a, b = Vector(p0), Vector(p1); k = (b - a).length / tr['comprimento']
    def fl(s_):
        f = s_ * n - 0.5; i = int(math.floor(f)); w = f - i
        u0 = U[i % n] + (V if i >= n else 0) - (V if i < 0 else 0); u1 = U[(i + 1) % n] + (V if i + 1 >= n else 0) - (V if i + 1 < 0 else 0)
        return (u0 * (1 - w) + u1 * w) * k
    base = dict(evaporador='aluminio', condensador='preto')[trecho]
    m = M.circuito(f'circ_canal_{pid}', base)
    pts = [tuple(a + (b - a) * (i / 120)) for i in range(121)]
    M.varrer(f'tubo_canal_{pid}', pts, r, m, tr['s0'], tr['s1'], lados=32, fluxo=fl, tampa=True)
    fundo = M.pintura(f'fundo_canal_{pid}', '#262a31', rug=0.9)
    lib.caixa(f'fundo_canal_{pid}', (4.0, 0.02, 3.0), ((a.x + b.x) / 2, fundo_y, a.z), fundo)


def cresce(t0, t1, ate=1.0, some=None):
    """Curvas de um feixe que cresce de p1 = 0 até 'ate' entre t0 e t1 (e opcionalmente some depois)."""
    c = dict(p0=[[0, 0.0]], p1=[[t0, 0.0], [t1, ate]], forca=[[t0 - 0.01, 0.0], [t0, 1.0]])
    if some: c['forca'] += [[some[0], 1.0], [some[1], 0.0]]
    return c


class Manometros:
    """Manômetros 2D desenhados na montagem: âncora 3D projetada por quadro + valor 0–1 (baixa → alta pressão)."""
    def __init__(self): self.itens = []; self.quadros = []
    def add(self, nome, ancora, t0, t1, valor): self.itens.append((nome, ancora, t0, t1, valor))
    def registrar(self, g):
        from bpy_extras.object_utils import world_to_camera_view
        s = bpy.context.scene; q = []
        for (nome, anc, t0, t1, val) in self.itens:
            if not (t0 - 0.01 <= g <= t1 + 0.3): continue
            p = anc(g) if callable(anc) else Vector(anc); u, v, z = world_to_camera_view(s, s.camera, p)
            a = min(B.suave((g - t0) / 0.3), 1 - B.suave((g - t1) / 0.3))
            if z > 0: q.append([nome, round(u, 4), round(1 - v, 4), round(a, 3), round(val(g) if callable(val) else val, 4)])
        self.quadros.append(q)


PB, PA = MOD['pressoes']['baixa_bar'], MOD['pressoes']['alta_bar']
def p_rel(P): return (P - PB) / (PA - PB)            # 0 = baixa, 1 = alta


# ------------------------------------------------------------------ montagem de um plano
def plano(pid):
    p = PL[BASE(pid)]; g0, g1 = p['t0'] - MARGEM, p['t1'] + MARGEM
    seq = pid[0]
    parede = pid in ('A1', 'A2', 'A4', 'J1', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'I1', 'I2', 'I3', 'I4', 'J2', 'J4')   # v2: I3/I4 com a parede (cômodo fechado)
    s, cam = C.nova(); C.luzes_cozinha(); C.lampada_interna()
    obj = G.montar(parede_traseira=parede)
    mec = CM.montar(); tab = CM.ciclo()
    # garrafa extra sobre a bancada (B4: "Imagine uma garrafa...")
    if pid == 'B4':   # v2: na beira da bancada, ao lado da geladeira aberta; a garrafa de dentro some (é a mesma que vai entrar em B5)
        for nm in ('garrafa', 'garrafa_tampa', 'garrafa_agua_vol', 'garrafa_rot'): bpy.data.objects[nm].hide_render = True
        G.garrafa_agua(obj['mt'], (-0.50, -0.11, 0.90))
    corte_gab = seq in 'CDEGH' or pid in ('J3',)   # v2: F sem corte do gabinete (a serpentina é externa; o corte poluía o fundo)
    if corte_gab:   # gabinete, forro e porta entram no corte ilustrativo (metade x > 0 removida)
        nomes = ('gab_', 'forro', 'porta_', 'prat_', 'gaveta')
        for o in bpy.data.objects:
            if o.type == 'MESH' and o.name.startswith(nomes):
                for ms in o.material_slots: M.ajustar(ms.material, corte=True)
    if pid in ('E3',):
        M.ajustar(obj['mt']['compressor'], corte=2)
    curvas = {}; rot = B.Rotulos(); man = Manometros(); extra = {}
    porta = lambda g: 0.0
    termico = None; revela = 0.0; theta = None
    garrafa_T = None
    # ---------------- câmeras e eventos
    K = lambda *ks: [(F(pid, f), pos, alvo, lente) for (f, pos, alvo, lente) in ks]
    if pid == 'A1':
        cam_k = K((0, (0.58, -2.62, 1.16), (-0.03, -0.15, 0.86), 30), (1, (0.47, -2.10, 1.13), (-0.03, -0.15, 0.86), 30))
        porta = lambda g: 100 * B.suave((g - F('A1', 0.15)) / 1.1)
    elif pid == 'A2':
        cam_k = K((0, (0.47, -2.10, 1.13), (-0.03, -0.15, 0.86), 30), (1, (0.40, -1.80, 1.11), (-0.03, -0.15, 0.88), 30))
        porta = lambda g: 100; termico = [[F('A2', 0.0), 0], [F('A2', 0.05), 1]]; curvas['uVarre'] = [[F('A2', 0.05), 0.0], [F('A2', 0.75), 1.0]]
    elif pid == 'A3':
        # v2: 3/4 traseiro quase fixo (a órbita de 1,2 s da v1 passava rente à lateral: quadro tomado pela parede cinza)
        cam_k = K((0, (1.30, 1.95, 1.38), (0.0, 0.30, 0.88), 30), (1, (1.22, 1.85, 1.36), (0.0, 0.30, 0.88), 30))
        porta = lambda g: 100; termico = [[0, 1]]
        calor_traseira(pid, F('A3', 0.0), F('A3', 0.8))
    elif pid in ('A4', 'J1'):   # tela dividida, metade da FRENTE: interior frio
        cam_k = K((0, (0.12, -1.95, 1.18), (0.0, -0.15, 0.88), 30), (1, (0.10, -2.15, 1.20), (0.0, -0.15, 0.88), 30))
        porta = lambda g: 100; termico = [[0, 1]] if pid == 'J1' else [[F('A4', 0.0), 1], [F('A4', 0.80), 1], [F('A4', 0.95), 0]]
    elif pid in ('A4b', 'J1b'):  # tela dividida, metade de TRÁS: condensador e compressor quentes (parede em corte)
        cam_k = K((0, (0.18, 1.55, 1.02), (0.0, 0.30, 0.78), 30), (1, (0.16, 1.75, 1.05), (0.0, 0.30, 0.78), 30))
        calor_traseira(pid, F(BASE(pid), 0.0) - 0.6, F(BASE(pid), 0.4))   # v2: o calor rejeitado sobe da serpentina para a cozinha
        porta = lambda g: 100; termico = [[0, 1]] if pid == 'J1b' else [[F('A4', 0.0), 1], [F('A4', 0.80), 1], [F('A4', 0.95), 0]]
    elif pid == 'B1':
        cam_k = K((0, (0.25, -1.95, 1.22), (0.0, -0.10, 0.95), 32), (1, (0.15, -1.55, 1.20), (0.0, -0.10, 0.97), 32))
        porta = lambda g: 100
    elif pid in ('B2', 'J2'):
        cam_k = K((0, (0.16, -1.12, 1.30), (-0.02, -0.05, 1.12), 34), (1, (0.13, -1.00, 1.29), (-0.02, -0.05, 1.13), 34))
        porta = lambda g: 100
    elif pid in ('B3', 'J3'):
        if pid == 'B3':   # frente-esquerda alta: o interior pela porta aberta e o calor saindo por trás, acima da geladeira
            cam_k = K((0, (-0.95, -1.95, 1.62), (0.0, 0.0, 1.05), 28), (1, (-0.88, -1.85, 1.62), (0.0, 0.0, 1.07), 28))
        else:             # corte, rima com C2
            cam_k = K((0, (1.55, -1.25, 1.42), (0.0, 0.05, 0.78), 30), (1, (1.62, -1.15, 1.45), (0.0, 0.05, 0.78), 30))
        porta = lambda g: 100 if pid == 'B3' else 0
        pts = [(-0.12, -0.10, 0.70), (-0.06, -0.06, 0.95), (0.0, 0.0, 1.12), (0.0, 0.18, 1.32), (0.0, 0.36, 1.42), (0.0, 0.41, 1.60), (0.0, 0.43, 1.95)]
        if pid == 'J3':   # o caminho do calor pelo circuito: interior → evaporador → sucção → compressor → condensador → ar
            pts = [(-0.02, -0.12, 0.70), (0.0, -0.05, 0.95), (0.0, 0.05, 1.18), (0.12, 0.20, 1.40), (0.205, 0.287, 1.30), (0.205, 0.287, 0.40),
                   (0.10, 0.20, 0.20), (-0.10, 0.20, 0.20), (-0.28, 0.345, 0.30), (-0.20, 0.345, 0.80), (0.0, 0.40, 1.20), (0.0, 0.42, 1.65)]
            revela = 1.0
        feixe(pid, pts, 0.018, cresce(F(pid, 0.05), F(pid, 0.85)), sobre=True)
        rot.add('calor', lambda g: Vector((0.0, 0.40, 1.25)), F(pid, 0.55), T1(pid)) if pid == 'B3' else None
    elif pid == 'B4':
        # v2: a garrafa (temperatura ambiente) recortada contra o interior frio da geladeira aberta, ao fundo
        cam_k = K((0, (-0.40, -1.62, 1.14), (-0.36, -0.12, 1.00), 34), (1, (-0.40, -1.50, 1.13), (-0.36, -0.12, 1.00), 34))
        porta = lambda g: 100
        rot.add('temperatura ambiente', lambda g: Vector((-0.50, -0.11, 1.12)), F('B4', 0.50), T1('B4'), dx=-0.06)
        termico = [[F('B4', 0.25), 0], [F('B4', 0.45), 1]]
    elif pid in ('B5', 'B6', 'B7'):
        alvo0 = {'B5': (-0.12, -0.10, 0.66), 'B6': (-0.10, -0.08, 0.86), 'B7': (-0.06, -0.04, 1.08)}[pid]
        alvo1 = {'B5': (-0.12, -0.10, 0.70), 'B6': (-0.08, -0.06, 0.98), 'B7': (-0.02, -0.02, 1.18)}[pid]
        z0 = {'B5': 0.70, 'B6': 0.78, 'B7': 0.90}[pid]; z1 = {'B5': 0.72, 'B6': 0.88, 'B7': 0.98}[pid]
        cam_k = K((0, (0.10, -0.62, z0), alvo0, 28), (1, (0.08, -0.60, z1), alvo1, 28))
        if pid == 'B7':   # v2: plano mais aberto, com a caixa do congelador inteira recebendo os feixes
            cam_k = K((0, (0.16, -0.92, 0.98), (-0.04, -0.04, 1.06), 30), (1, (0.14, -0.84, 1.02), (-0.04, -0.04, 1.10), 30))
        porta = lambda g: 100; termico = [[0, 1]]
        garrafa_T = [[T0('B5'), 25.0], [T1('B7'), 9.0]]
        # feixes saem da garrafa, sobem com o ar morno e chegam ao evaporador
        for i, (dx, dy) in enumerate([(-0.03, 0.0), (0.03, 0.01), (0.0, -0.03)]):
            pts = [(-0.12 + dx, -0.10 + dy, 0.62), (-0.12 + dx * 1.6, -0.08 + dy, 0.80), (-0.06 + dx * 2, -0.04, 1.00), (-0.02 + dx * 2.5, 0.0, 1.17)]
            feixe(f'{pid}_{i}', pts, 0.006, dict(p0=[[0, 0]], p1=[[T0('B5') + 0.3 * i, 0], [T1('B7') - 0.4 + 0.2 * i, 1.0]], forca=[[0, 1]]), onda=9)
    elif pid == 'C1':
        cam_k = K((0, (0.12, -2.20, 1.25), (0.0, -0.05, 0.84), 30), (0.30, (0.45, -2.15, 1.30), (0.0, 0.0, 0.82), 30), (1, (1.55, -1.25, 1.42), (0.0, 0.05, 0.78), 30))
        porta = lambda g: 100 * (1 - B.suave((g - F('C1', 0.02)) / 1.0))
        curvas['corte'] = [[F('C1', 0.24), 99.0], [F('C1', 0.25), 0.36], [F('C1', 0.80), 0.0]]
    elif pid == 'C2':
        cam_k = K((0, (1.55, -1.25, 1.42), (0.0, 0.05, 0.78), 30), (1, (1.60, -1.20, 1.44), (0.0, 0.05, 0.78), 30))
        revela = [[F('C2', 0.0), 0], [F('C2', 0.22), 1]]
        curvas['uPulso'] = [[F('C2', 0.15), 0.0], [F('C2', 0.95), 1.0]]
    elif pid == 'C3':
        zp = 1.425 - 5 * 0.072   # 6º passe do condensador (escoa para −x): condensando, líquido embaixo e vapor em cima
        cam_k = K((0, (0.16, 0.44, zp + 0.035), (0.10, COND_Y, zp), 40), (1, (-0.06, 0.44, zp + 0.035), (-0.12, COND_Y, zp), 40))
        revela = 1.0; rot.add('fluido refrigerante', lambda g: Vector((0.0, COND_Y, zp)), F('C3', 0.25), T1('C3'))
        bpy.data.objects['pote'].hide_render = True   # v2: defeito da v1 — o pote tapava metade do quadro no início do plano
    elif pid == 'C4':
        cam_k = K((0, (1.65, -1.05, 1.50), (0.0, 0.10, 0.76), 30), (0.75, (1.75, 0.10, 1.55), (0.0, 0.15, 0.76), 30), (1, (1.25, 0.30, 1.35), (0.0, 0.22, 0.70), 32))
        revela = 1.0
        man.add('baixa', (0.205, 0.287, 0.70), F('C4', 0.18), T1('C4'), 0.0)
        man.add('alta', (-0.284, 0.345, 0.70), F('C4', 0.18), T1('C4'), 1.0)
    elif pid == 'D1':
        cam_k = K((0, (0.48, -0.60, 1.48), (0.0, 0.0, 1.29), 35), (1, (0.36, -0.42, 1.36), (0.0, 0.0, 1.29), 35))
        revela = 1.0; rot.add('Evaporador', lambda g: Vector((0.219, -0.10, 1.30)), F('D1', 0.2), T1('D1'))
    elif pid == 'D2':
        cam_k = K((0, (0.10, 0.11, 1.440), (-0.15, 0.215, 1.412), 45), (1, (0.02, 0.11, 1.436), (-0.17, 0.205, 1.408), 45))
        revela = 1.0; man.add('baixa', (-0.15, 0.235, 1.43), F('D2', 0.3), T1('D2'), 0.0)
    elif pid == 'D3':
        cam_k = K((0, (0.50, -0.30, 0.95), (0.0, -0.02, 0.95), 30), (1, (0.46, -0.25, 1.00), (0.0, -0.02, 1.00), 30))
        revela = 1.0
        for i, (x, y, z) in enumerate([(-0.10, 0.05, 0.93), (0.12, -0.08, 1.03), (-0.12, -0.10, 0.80), (0.0, -0.18, 0.18)]):
            pts = [(x, y, z), (x * 0.8, y * 0.7, (z + 1.17) / 2), (x * 0.5, y * 0.4, 1.17)]
            feixe(f'D3_{i}', pts, 0.006, dict(p0=[[0, 0]], p1=[[F('D3', 0.05 + 0.08 * i), 0], [F('D3', 0.70 + 0.05 * i), 1.0]], forca=[[0, 1]]), onda=9)
        rot.add('fluido mais frio que o ar', lambda g: Vector((0.219, -0.05, 1.21)), F('D3', 0.45), T1('D3'))
    elif pid == 'D4':   # v2: canal do evaporador esticado e ampliado (corte ilustrativo): a fração líquida diminui até só vapor
        Y, Z = -1.30, 1.25; r_c = 0.022
        canal_esticado(pid, 'evaporador', (-0.30, Y, Z), (0.30, Y, Z), r_c, -1.02)
        pc = lambda xt: (xt - 0.15, Y - 0.215, Z + 0.004)
        cam_k = K((0, pc(-0.27), (-0.27 + 0.10, Y, Z - 0.002), 35), (1, pc(0.19), (0.19 + 0.10, Y, Z - 0.002), 35))
        for i, x in enumerate([-0.24, -0.14, -0.04, 0.06, 0.16, 0.24]):   # calor do ar entrando pela parede do canal
            feixe(f'D4_{i}', [(x, Y - 0.01, Z - 0.20), (x + 0.01, Y, Z - 0.10), (x, Y, Z - r_c - 0.002)], 0.0045,
                  dict(p0=[[0, 0]], p1=[[F('D4', 0.02 + 0.07 * i) - 0.4, 0], [F('D4', 0.25 + 0.07 * i), 1.0]], forca=[[0, 1]]), onda=11)
        rot.add('entra: líquido + vapor', lambda g: Vector((-0.27, Y, Z + r_c)), F('D4', 0.05), F('D4', 0.50))
        rot.add('sai: só vapor', lambda g: Vector((0.29, Y, Z + r_c)), F('D4', 0.55), T1('D4'))
        revela = 1.0
    elif pid == 'D5':
        # v2: começa num plano médio do interior (a v1 começava no macro da v1 de D4); o calor dos alimentos já está no evaporador
        cam_k = K((0, (0.46, -0.28, 1.04), (0.0, -0.02, 1.12), 30), (1, (0.85, -0.85, 1.20), (0.0, 0.0, 1.05), 30))
        for i, (x, y, z) in enumerate([(-0.10, 0.05, 0.93), (0.12, -0.08, 1.03), (-0.12, -0.10, 0.80)]):
            feixe(f'D5_{i}', [(x, y, z), (x * 0.8, y * 0.7, (z + 1.17) / 2), (x * 0.5, y * 0.4, 1.17)], 0.006,
                  dict(p0=[[0, 0]], p1=[[0, 1.0]], forca=[[F('D5', 0.55), 1], [F('D5', 0.85), 0]]), onda=9)
        revela = 1.0
    elif pid == 'E1':
        cam_k = K((0, (0.42, 0.62, 1.30), (0.205, 0.287, 1.22), 35), (1, (0.42, 0.62, 0.45), (0.205, 0.287, 0.37), 35))
        revela = 1.0
    elif pid == 'E2':
        cam_k = K((0, (0.48, 0.80, 0.26), (0.0, 0.18, 0.14), 35), (1, (0.34, 0.62, 0.23), (0.0, 0.18, 0.14), 35))
        revela = 1.0; curvas['uTrab'] = [[F('E2', 0.30), 0], [F('E2', 0.45), 1]]
        rot.add('Compressor', lambda g: Vector((0.0, 0.22, 0.26)), F('E2', 0.15), T1('E2'))
    elif pid == 'E3':
        cam_k = K((0, (0.07, 0.42, 0.34), (-0.03, 0.18, 0.18), 40), (1, (0.05, 0.36, 0.30), (-0.035, 0.18, 0.18), 40))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]; curvas['corte2'] = [[0, 0.18]]; extra['corte2'] = dict(n=[0, -1, 0])
        theta = lambda g: 2 * math.pi * 0.8 * (g - T0('E3')) + math.radians(200)
        man.add('cilindro', (-0.045, 0.18, 0.215), F('E3', 0.1), T1('E3'), lambda g: p_rel(tab[int(((theta(g) % (2 * math.pi)) / (2 * math.pi)) * len(tab)) % len(tab)]['p']))
    elif pid == 'E4':
        cam_k = K((0, (-0.10, 0.80, 0.52), (-0.284, 0.345, 0.44), 40), (1, (-0.12, 0.76, 0.54), (-0.284, 0.345, 0.47), 40))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
        rot.add('fluido: mais quente', lambda g: Vector((-0.284, 0.345, 0.50)), F('E4', 0.2), T1('E4'))
        rot.add('ar da cozinha', lambda g: Vector((-0.55, 0.40, 0.70)), F('E4', 0.4), T1('E4'), dx=-0.06)
    elif pid == 'F1':
        cam_k = K((0, (0.95, 1.50, 0.85), (0.0, 0.345, 0.85), 30), (1, (0.95, 1.50, 1.20), (0.0, 0.345, 1.10), 30))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
        for i, z in enumerate([0.55, 0.85, 1.15]):
            for j, x in enumerate([-0.15, 0.15]):
                pts = [(x, 0.35, z), (x, 0.40, z + 0.10), (x * 1.2, 0.43, z + 0.35), (x * 1.4, 0.44, z + 0.65)]
                feixe(f'F1_{i}{j}', pts, 0.007, dict(p0=[[0, 0]], p1=[[F('F1', 0.10 + 0.1 * i), 0], [F('F1', 0.75 + 0.05 * i), 1.0]], forca=[[0, 1]]), onda=8)
        rot.add('Condensador', lambda g: Vector((0.262, 0.345, 0.70)), F('F1', 0.15), T1('F1'))
    elif pid == 'F2':
        # v2: canal do condensador esticado e ampliado (os arames tapavam os tubos na v1): vapor quente → gotas → líquido
        Y, Z = 1.30, 1.00; r_c = 0.022
        canal_esticado(pid, 'condensador', (-0.30, Y, Z), (0.30, Y, Z), r_c, Y + 0.28)
        pc = lambda xt: (xt - 0.15, Y - 0.215, Z + 0.004)
        cam_k = K((0, pc(-0.27), (-0.27 + 0.10, Y, Z - 0.002), 35), (1, pc(0.19), (0.19 + 0.10, Y, Z - 0.002), 35))
        for i, x in enumerate([-0.26, -0.16, -0.06, 0.04, 0.14, 0.24]):   # calor saindo pela parede do canal para o ar
            feixe(f'F2_{i}', [(x, Y, Z + r_c + 0.002), (x + 0.01, Y, Z + 0.10), (x, Y + 0.01, Z + 0.22)], 0.0045,
                  dict(p0=[[0, 0]], p1=[[F('F2', 0.02 + 0.07 * i) - 0.4, 0], [F('F2', 0.25 + 0.07 * i), 1.0]], forca=[[0, 1]]), onda=11)
        rot.add('entra: vapor quente', lambda g: Vector((-0.27, Y, Z - r_c)), F('F2', 0.05), F('F2', 0.50), dy=0.06)
        rot.add('sai: líquido', lambda g: Vector((0.29, Y, Z - r_c)), F('F2', 0.55), T1('F2'), dy=0.06)
        revela = 1.0
    elif pid == 'G1':
        cam_k = K((0, (0.48, 0.66, 0.36), (0.245, 0.30, 0.27), 40), (1, (0.42, 0.60, 0.31), (0.245, 0.30, 0.25), 40))
        revela = 1.0
    elif pid == 'G2':
        cam_k = K((0, (0.36, 0.58, 0.26), (0.205, 0.255, 0.22), 50), (1, (0.33, 0.55, 0.25), (0.205, 0.255, 0.22), 50))
        revela = 1.0; rot.add('Capilar', lambda g: Vector((0.235, 0.255, 0.24)), F('G2', 0.3), T1('G2'))
    elif pid == 'G3':
        z = lambda g: 0.40 + 0.92 * B.suave((g - T0('G3')) / (T1('G3') - T0('G3')))
        cam_k = [(T0('G3'), lambda g: Vector((0.172, 0.330, z(g))), lambda g: Vector((0.125, 0.283, z(g) + 0.012)), 50),
                 (T1('G3'), lambda g: Vector((0.172, 0.330, z(g))), lambda g: Vector((0.125, 0.283, z(g) + 0.012)), 50)]
        revela = 1.0
        cap = next(t for t in MOD['circuito'] if t['id'] == 'capilar')['perfil']
        tr = {t['id']: t for t in obj['tracado']}['capilar']
        def p_cap(g):   # pressão no ponto do capilar à altura da câmera (s local pelo comprimento do traçado)
            zz = z(g) + 0.03; pts = tr['pts']; L = 0; tot = M.comprimento(pts); best = None
            for i in range(len(pts) - 1):
                a, b = Vector(pts[i]), Vector(pts[i + 1])
                if abs(a.x - 0.125) < 1e-3 and abs(b.x - 0.125) < 1e-3 and min(a.z, b.z) <= zz <= max(a.z, b.z): best = L + abs(zz - a.z)
                L += (b - a).length
            sl = (best if best is not None else tot) / tot; k = min(int(sl * (len(cap) - 1)), len(cap) - 1)
            return p_rel(cap[k]['P_bar'] * 1.0)
        man.add('capilar', lambda g: Vector((0.125, 0.283, z(g) + 0.03)), F('G3', 0.05), T1('G3'), p_cap)
        bpy.data.objects['pote'].hide_render = True   # v2: tapava metade do quadro (fora do assunto do plano)
    elif pid == 'H1':
        cam_k = K((0, (0.40, -0.50, 1.42), (0.0, 0.02, 1.29), 35), (0.35, (0.70, -0.75, 1.45), (0.0, 0.05, 1.18), 33), (1, (1.70, -0.90, 1.60), (0.0, 0.10, 0.78), 30))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
    elif pid == 'H2':
        cam_k = K((0, (1.70, -0.90, 1.60), (0.0, 0.10, 0.78), 30), (1, (1.80, -0.45, 1.62), (0.0, 0.12, 0.78), 30))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
        for i, (x, y, z) in enumerate([(-0.10, 0.05, 0.93), (0.12, -0.08, 1.03)]):
            feixe(f'H2_in{i}', [(x, y, z), (x * 0.6, y * 0.5, 1.05), (x * 0.4, y * 0.3, 1.17)], 0.008, cresce(F('H2', 0.05), F('H2', 0.6)), onda=9)
        for i, z in enumerate([0.65, 1.05]):
            feixe(f'H2_out{i}', [(0.0, 0.35, z), (0.0, 0.42, z + 0.15), (0.0, 0.44, z + 0.55)], 0.010, cresce(F('H2', 0.15), F('H2', 0.7)), onda=8)
        # v2: rótulos afastados entre si (na v1 "Compressor" e "Capilar" se sobrepunham e um manômetro cobria "Condensador")
        for nome, anc, dx, dy in [('Evaporador', (0.219, -0.10, 1.30), 0.06, -0.05), ('Compressor', (-0.02, 0.20, 0.24), -0.10, 0.03),
                                  ('Condensador', (0.262, 0.345, 1.20), 0.04, -0.06), ('Capilar', (0.235, 0.255, 0.24), 0.05, 0.06)]:
            rot.add(nome, (lambda a: lambda g: Vector(a))(anc), F('H2', 0.2), T1('H2'), dx=dx, dy=dy)
        man.add('baixa', (0.205, 0.287, 0.70), F('H2', 0.1), T1('H2'), 0.0); man.add('alta', (-0.284, 0.345, 0.70), F('H2', 0.1), T1('H2'), 1.0)
    elif pid == 'I1':
        cam_k = K((0, (0.58, -2.62, 1.16), (-0.03, -0.15, 0.86), 30), (1, (0.50, -2.25, 1.14), (-0.03, -0.15, 0.86), 30))
        porta = lambda g: 100 * B.suave((g - F('I1', 0.55)) / 1.1)
    elif pid == 'I2':
        cam_k = K((0, (-1.10, -1.55, 1.15), (0.05, -0.38, 0.85), 30), (1, (-1.00, -1.45, 1.15), (0.05, -0.38, 0.85), 30))
        porta = lambda g: 100; curvas['uTrab'] = [[0, 1]]; curvas['uTrabVel'] = [[F('I2', 0.4), 1], [F('I2', 0.7), 2.2]]
        for i, z in enumerate([1.25, 1.05, 0.85]):
            feixe(f'I2_{i}', [(-0.05, -1.10, z + 0.15), (-0.03, -0.60, z + 0.05), (0.0, -0.20, z), (0.0, 0.05, 1.17)], 0.010,
                  dict(p0=[[0, 0]], p1=[[F('I2', 0.10 + 0.1 * i), 0], [F('I2', 0.80), 1.0]], forca=[[0, 1]]), onda=7)
    elif pid in ('I3', 'I4'):
        # v2: 3/4 alto com a parede da cozinha (a vista de cima da v1 não se lia). Feixes "sobre" = vistos através do gabinete.
        cam_k = K((0, (-1.80, -2.68, 2.50), (-0.02, -0.12, 1.00), 26), (1, (-1.70, -2.50, 2.42), (-0.02, -0.10, 1.00), 26)) if pid == 'I3' else \
                K((0, (-1.70, -2.50, 2.42), (-0.02, -0.10, 1.00), 26), (1, (-1.60, -2.35, 2.34), (-0.02, -0.08, 1.00), 26))
        porta = lambda g: 100; curvas['uTrab'] = [[0, 1]]; curvas['uTrabVel'] = [[0, 2.2]]
        X = -0.05
        if pid == 'I3':   # laço fechado: entra pela porta aberta, sai pela serpentina, sobe e volta para a frente do MESMO cômodo
            loop = [(X, -1.20, 1.10), (X, -0.60, 1.05), (X, -0.05, 1.00), (X, 0.38, 0.95), (X, 0.41, 1.60), (X, 0.10, 1.98),
                    (X, -0.80, 1.95), (X, -1.30, 1.55), (X, -1.20, 1.10)]
            feixe('I3', loop, 0.026, cresce(F('I3', 0.05), F('I3', 0.85)), sobre=True, onda=10)
            rot.add('o calor volta para a mesma cozinha', lambda g: Vector((X, -0.80, 1.95)), F('I3', 0.55), T1('I3'), dx=0.04, dy=-0.06)
        else:   # balanço: entrada (Q̇_abs), trabalho (Ẇ, violeta) e saída mais larga (Q̇_abs + Ẇ) — larguras proporcionais
            E_ = MOD['energia_W']; r_in = 0.026; r_out = r_in * E_['Q_rej_total'] / E_['Q_abs_total']; r_w = r_in * E_['W_eletrico'] / E_['Q_abs_total']
            feixe('I4_in', [(X, -1.25, 1.10), (X, -0.70, 1.05), (X, -0.10, 1.00)], r_in, cresce(F('I4', 0.03), F('I4', 0.30)), sobre=True, onda=10)
            feixe('I4_w', [(-0.55, 0.44, 0.32), (-0.40, 0.40, 0.12), (-0.05, 0.22, 0.12)], r_w, cresce(F('I4', 0.33), F('I4', 0.55)), sobre=True, onda=10, cor='#9a6bff')
            feixe('I4_out', [(X, 0.39, 0.95), (X, 0.41, 1.45), (X, 0.38, 2.05)], r_out, cresce(F('I4', 0.58), F('I4', 0.85)), sobre=True, onda=10)
            rot.add('calor retirado', lambda g: Vector((X, -0.95, 1.08)), F('I4', 0.12), T1('I4'), dx=0.06, dy=0.05)
            rot.add('energia elétrica', lambda g: Vector((-0.45, 0.42, 0.20)), F('I4', 0.40), T1('I4'), dx=-0.08, dy=0.05)
            rot.add('calor liberado = retirado + elétrica', lambda g: Vector((X, 0.38, 1.95)), F('I4', 0.66), T1('I4'), dx=0.03, dy=-0.05)
    elif pid == 'J1':
        cam_k = K((0, (-1.25, 1.55, 2.35), (0.05, -0.20, 0.80), 30), (1, (-1.45, 1.80, 2.50), (0.05, -0.25, 0.78), 30))
        porta = lambda g: 100; termico = [[0, 1]]
    elif pid == 'J4':
        cam_k = K((0, (0.50, -2.25, 1.14), (-0.03, -0.10, 0.86), 30), (1, (0.62, -2.75, 1.17), (-0.03, -0.10, 0.88), 30))
        for i, x in enumerate([-0.18, 0.0, 0.18]):
            feixe(f'J4_{i}', [(x, 0.40, 1.10), (x, 0.43, 1.45), (x * 1.3, 0.44, 1.95)], 0.010, cresce(F('J4', 0.05 + 0.08 * i), F('J4', 0.55)), onda=7)
        curvas['uTrab'] = [[F('J4', 0.0), 1], [F('J4', 0.85), 1], [F('J4', 1.0), 0]]
    else:
        raise SystemExit(f'plano sem definição: {pid}')
    # ---------------- curvas globais
    if termico is not None: curvas['uTermico'] = termico
    curvas['uRevela'] = revela if isinstance(revela, list) else [[0, revela]]
    if corte_gab and 'corte' not in curvas: curvas['corte'] = [[0, 0.0]]
    if garrafa_T: M.ajustar(lib._MATS['garrafa_pet'], curvas=dict(temp=garrafa_T)); M.ajustar(lib._MATS['garrafa_agua'], curvas=dict(temp=garrafa_T)); M.ajustar(lib._MATS['garrafa_rotulo'], curvas=dict(temp=garrafa_T))
    if seq in 'CDEFGHJ' and 'uTrab' not in curvas and revela: curvas['uTrab'] = [[0, 1]]
    planos_cam = [(g0 - 1, [(t, p_, a_, l_) for (t, p_, a_, l_) in cam_k])]
    piv = obj['porta']
    def anim(g):
        piv.rotation_euler = (0, 0, math.radians(porta(g)))
        if theta: CM.posicionar(mec, theta(g), tab)
        else: CM.posicionar(mec, 2 * math.pi * 0.8 * g, tab)
        B.camera_planos(cam, planos_cam, g); bpy.context.view_layer.update(); man.registrar(g)
        return g
    meta = C.meta_comum(curvas, dict(corte=dict(n=[-1, 0, 0]), plano=pid, seq=seq, g0p=p['t0'], g1p=p['t1']))
    meta.update(extra)
    pasta = os.path.join(SAIDA, pid); os.makedirs(pasta, exist_ok=True)
    B.exportar_seg(pasta, g0, g1, anim, rot=rot, extra=meta)
    n = int(round((g1 - g0) * B.FPS)) + 1
    json.dump(dict(g0=g0, fps=B.FPS, quadros=man.quadros[:n]), open(os.path.join(pasta, 'manometros2d.json'), 'w'), ensure_ascii=False)


if __name__ == '__main__':
    ids = sys.argv[1:] or [x for k in PL for x in ([k, k + 'b'] if k in ('A4', 'J1') else [k])]   # v2: inclui as metades da tela dividida
    for pid in ids: plano(pid)
