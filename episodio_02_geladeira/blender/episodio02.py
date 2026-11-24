"""Linha do tempo do Ep. 02: os 40 planos da decupagem (decupagem/planos.py) sobre UM modelo mestre (geladeira.py).
Cada plano é exportado como um segmento próprio (com margem para as fusões) → re-render só do que mudar.
Tempos: âncoras em palavras (narração aprovada quando existir; senão, tempos provisórios). Câmeras por frações do plano.
Uso: PYTHONPATH=<bpy> python3 episodio02.py [planos...]   (sem argumentos: todos)"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import lib, mats02 as M, geladeira as G, ep_base as B, cenas02 as C, compressor_mec as CM, personagem as PE, encenacao02 as E
COND_Y = G.COND_Y

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(AQUI, '..')
SAIDA = os.path.join(RAIZ, 'episodio', 'cenas')
PL = C.PLANOS
R9 = os.environ.get('CENA_R9', '0') == '1'
def LEITE_TOPO(): return (G.LEITE_POS[0], G.LEITE_POS[1], 1.03)   # feixes de calor que saem do leite seguem a posição dele (V8: (0,12; −0,08))
CORRECAO_PORTA = {'G3', 'J3', 'C4', 'H1', 'H2'}   # folga porta × vedação (z-fighting): G3 (rodada 5, regressão da câmera nova); J3 (rodada 6, defeito antigo, autorizado);
# C4, H1, H2 (rodada 8: o mesmo defeito antigo, achado pelo detector sensível e confirmado na V6; a junção só fica à vista pelo corte
# nesses 5 planos — verificação geométrica em relatorios/porta_vedacao_r8.json). Reverter: tirar os três ids do conjunto.
CORRECAO_DEGRAU = {'E2'}   # rodada 8: folga degrau × fundo traseiro (defeito antigo; só no E2 a junta pisca à vista — relatorios/juntas_gabinete_r8.json)
CORRECAO_GAB = set(os.environ.get('CORRECAO_GAB', '').split(',')) - {''}   # rodada 7: folga topo/base × laterais (teste; vazio = aprovado)
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


def s_capilar(g):
    """Polimento (G3): posição ao longo do capilar (0 = entrada, 1 = saída) mostrada pela lupa e pelo marcador, ancorada
    nas palavras: o trecho líquido em "A pressão cai bruscamente", o início da evaporação (s = 0,53 no modelo) em
    "parte do líquido evapora" e a saída fria em "resfriando a mistura"."""
    t0 = T0('G3') - 0.5; W_ = lambda w: E.T(w, apos=t0)
    # rodada 8: a lupa demora no início da evaporação durante "evapora" (o rótulo entra na palavra); o marcador continua
    # chegando a s = 0,532 entre "parte" e "evapora"
    return E_trilha([(W_('pressão') - 0.15, 0.0), (W_('parte') - 0.2, 0.45), (W_('evapora') + 0.7, 0.58),
                     (W_('resfriando') + 0.3, 0.80), (W_('mistura') + 0.15, 1.0)], g)


def E_trilha(ch, g): return PE.trilha(ch, g)


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
    base = dict(evaporador='aluminio', condensador='preto', capilar='cobre')[trecho]
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
    parede = pid in ('A1', 'A2', 'A4', 'J1', 'C1', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'I1', 'I2', 'I3', 'I4', 'J2', 'J4')   # v2: I3/I4 com a parede (cômodo fechado)
    s, cam = C.nova(); C.luzes_cozinha(); C.lampada_interna()
    G.FOLGA_PORTA = 0.0005 if pid in CORRECAO_PORTA else 0.0
    if os.environ.get('FOLGA_PORTA_TESTE') and pid in CORRECAO_PORTA: G.FOLGA_PORTA = float(os.environ['FOLGA_PORTA_TESTE'])   # rodada 9 (teste): negativo = sobreposição painel × vedação
    corte_gab = seq in 'CDEGH' or pid in ('J3',)   # v2: F sem corte do gabinete (a serpentina é externa; o corte poluía o fundo)
    CORTE_REAL = corte_gab and pid != 'C1'           # C1: corte desligado (cozinha por fora)
    # rodada 8 (aprovado para validação): folga de 0,5 mm nas peças que ENCOSTAM nas laterais (topo, fundo, base, degraus,
    # contraporta — ver relatorios/coplanares_*.json), só onde o corte expõe essas faces
    G.FOLGA_GAB = 0.0005 if (CORTE_REAL or pid in CORRECAO_GAB) else 0.0
    G.FOLGA_DEGRAU = 0.0005 if pid in CORRECAO_DEGRAU else 0.0
    if R9:   # rodada 9: itens novos + correções de apoio, leite na posição única (prévias; desligado = V8)
        G.ITENS_R9 = True; G.LEITE_POS = tuple(E.LEITE_R9)
    obj = G.montar(parede_traseira=parede)
    mec = CM.montar(); tab = CM.ciclo()
    # garrafa extra sobre a bancada (B4: "Imagine uma garrafa...")
    if pid == 'B4':   # v2: na beira da bancada, ao lado da geladeira aberta; a garrafa de dentro some (é a mesma que vai entrar em B5)
        for nm in ('garrafa', 'garrafa_tampa', 'garrafa_agua_vol', 'garrafa_rot'): bpy.data.objects[nm].hide_render = True
        G.garrafa_agua(obj['mt'], (-0.50, -0.11, 0.90))
    if corte_gab:   # gabinete, forro e porta entram no corte ilustrativo (metade x > 0 removida)
        nomes = ('gab_', 'forro', 'porta_', 'prat_', 'gaveta')
        for o in bpy.data.objects:
            if o.type == 'MESH' and o.name.startswith(nomes):
                for ms in o.material_slots: M.ajustar(ms.material, corte=True)
    if pid in ('E3',):
        M.ajustar(obj['mt']['compressor'], corte=2)
    curvas = {}; rot = B.Rotulos(); man = Manometros(); extra = {}
    # v3: personagem só onde ele é VISTO agindo: A1 (abre), A2 (olha o interior), A4 (reage à pergunta), I1 (deixa aberta).
    # Em A3 ele estaria escondido atrás da geladeira e em I2–I4 já saiu de quadro: esses planos ficam como na v2.
    PERS = {'A1': E.est_abertura, 'A2': E.est_abertura, 'A4': E.est_abertura, 'I1': E.est_porta_aberta}
    pers = PE.montar() if pid in PERS else None
    porta = lambda g: 0.0
    termico = None; revela = 0.0; theta = None
    garrafa_T = None
    # ---------------- câmeras e eventos
    K = lambda *ks: [(F(pid, f), pos, alvo, lente) for (f, pos, alvo, lente) in ks]
    janela_corte = None   # rodada 10: (g0, g1) de uma troca de câmera mais curta que 1 quadro: dentro dela, câmera do fim
    if pid == 'A1':
        # v3: o personagem abre a porta (a mão segue o puxador); plano médio que inclui ele e a geladeira
        cam_k = K((0, (-0.22, -3.10, 1.40), (-0.28, -0.48, 0.98), 28), (1, (-0.20, -2.85, 1.38), (-0.27, -0.48, 0.98), 28))
        porta = E.porta_ang(0.20)
    elif pid == 'A2':
        # v3: por cima do ombro do personagem, olhando o interior que a varredura térmica revela frio
        cam_k = K((0, (-0.55, -2.00, 1.70), (0.0, -0.15, 1.00), 32), (1, (-0.50, -1.88, 1.68), (0.0, -0.15, 0.99), 32))
        porta = (E.porta_ang(0.20) if R9 else (lambda g: 100)); termico = [[F('A2', 0.0), 0], [F('A2', 0.05), 1]]; curvas['uVarre'] = [[F('A2', 0.05), 0.0], [F('A2', 0.75), 1.0]]
    elif pid == 'A3':
        # v2: 3/4 traseiro quase fixo (a órbita de 1,2 s da v1 passava rente à lateral: quadro tomado pela parede cinza)
        cam_k = K((0, (1.30, 1.95, 1.38), (0.0, 0.30, 0.88), 30), (1, (1.22, 1.85, 1.36), (0.0, 0.30, 0.88), 30))
        porta = lambda g: 100; termico = [[0, 1]]
        calor_traseira(pid, F('A3', 0.0), F('A3', 0.8))
    elif pid in ('A4', 'J1'):   # tela dividida, metade da FRENTE: interior frio
        cam_k = K((0, (0.12, -1.95, 1.18), (0.0, -0.15, 0.88), 30), (1, (0.10, -2.15, 1.20), (0.0, -0.15, 0.88), 30))
        if pid == 'A4':   # v3: aberto (personagem + geladeira) quando a tela está inteira; centrado no interior durante a divisão
            # contraplano de DENTRO da geladeira para o rosto do personagem (tela inteira: início e fim); interior centrado
            # durante a divisão. As trocas de câmera acontecem enquanto a divisória desliza (corte disfarçado pelo movimento).
            reac = lambda k: ((0.06, -0.42 - 0.04 * k, 1.42), (-0.80, -1.18, 1.50 - 0.02 * k), 30)
            centro = ((0.10, -2.05, 1.20), (0.0, -0.15, 0.88), 30)
            cam_k = K((0,) + reac(0), (0.165,) + reac(0.3), (0.17,) + centro, (0.80,) + centro, (0.805,) + reac(0.5), (1,) + reac(1))
            H_A4 = os.environ.get('HANDLE_A4')   # rodada 11 (teste de transição): quadros-ponte — rosto continuado depois do corte / interior antes dele
            if H_A4 == 'rosto': cam_k = K((0,) + reac(0), (0.165,) + reac(0.3), (0.30,) + reac(0.32), (1,) + reac(0.34))
            elif H_A4 == 'interior': cam_k = K((0,) + centro, (1,) + centro)
            if os.environ.get('CAM_A4_R10', '1') == '1' and not H_A4:   # rodada 10: o quadro 34 caía ENTRE as chaves 0,165 e 0,17 (troca em 26 ms < 1 quadro): câmera
                janela_corte = (F('A4', 0.165), F('A4', 0.17))   # interpolada = parede vazia. Dentro da janela usa a câmera do FIM dela (mesma trilha, chaves iguais)
        porta = lambda g: 100; termico = [[0, 1]] if pid == 'J1' else [[0, 0]] if (pid == 'A4' and os.environ.get('HANDLE_A4') == 'rosto') else [[0, 1]] if (pid == 'A4' and os.environ.get('HANDLE_A4') == 'interior') else ([[F('A4', 0.1675), 0], [F('A4', 0.16752), 1]] if os.environ.get('CAM_A4_R10', '1') == '1' else [[F('A4', 0.165), 0], [F('A4', 0.17), 1]]) + [[F('A4', 0.80), 1], [F('A4', 0.805), 0]]
        # v4: em A4 a visão térmica só existe durante a tela dividida; o contraplano do rosto (início e fim) é imagem normal
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
        rot.add('calor', lambda g: Vector((0.0, 0.40, 1.25)), E.T('calor', apos=T0(pid) - 0.5), T1(pid), linha=False) if pid == 'B3' else None
    elif pid == 'B4':
        # v2: a garrafa (temperatura ambiente) recortada contra o interior frio da geladeira aberta, ao fundo
        cam_k = K((0, (-0.40, -1.62, 1.14), (-0.36, -0.12, 1.00), 34), (1, (-0.40, -1.50, 1.13), (-0.36, -0.12, 1.00), 34))
        porta = lambda g: 100
        rot.add('temperatura ambiente', lambda g: Vector((-0.50, -0.11, 1.12)), E.T('temperatura', apos=T0('B4') - 0.5), T1('B4'), dx=-0.06, linha=False)
        termico = [[F('B4', 0.25), 0], [F('B4', 0.45), 1]]
    elif pid in ('B5', 'B6', 'B7'):
        alvo0 = {'B5': (-0.12, -0.10, 0.66), 'B6': (-0.10, -0.08, 0.86), 'B7': (-0.06, -0.04, 1.08)}[pid]
        alvo1 = {'B5': (-0.12, -0.10, 0.70), 'B6': (-0.08, -0.06, 0.98), 'B7': (-0.02, -0.02, 1.18)}[pid]
        z0 = {'B5': 0.70, 'B6': 0.78, 'B7': 0.90}[pid]; z1 = {'B5': 0.72, 'B6': 0.88, 'B7': 0.98}[pid]
        cam_k = K((0, (0.10, -0.62, z0), alvo0, 28), (1, (0.08, -0.60, z1), alvo1, 28))
        if pid == 'B7':   # v2: plano mais aberto, com a caixa do congelador inteira recebendo os feixes
            # v4: de frente e abaixo do congelador: a caixa (−18 °C, azul-profundo) ocupa o alto do quadro, o interior (+5 °C,
            # azul-gelo) em volta, e os feixes sobem até ela
            cam_k = K((0, (0.06, -0.86, 0.92), (0.0, -0.05, 1.20), 30), (1, (0.05, -0.80, 0.96), (0.0, -0.05, 1.23), 30))
        porta = lambda g: 100; termico = [[0, 1]]
        garrafa_T = [[T0('B5'), 25.0], [T1('B7'), 9.0]]
        # feixes saem da garrafa, sobem com o ar morno e chegam ao evaporador
        for i, (dx, dy) in enumerate([(-0.03, 0.0), (0.03, 0.01), (0.0, -0.03)]):
            pts = [(-0.12 + dx, -0.10 + dy, 0.62), (-0.12 + dx * 1.6, -0.08 + dy, 0.80), (-0.06 + dx * 2, -0.04, 1.00), (-0.02 + dx * 2.5, 0.0, 1.17)]
            feixe(f'{pid}_{i}', pts, 0.006, dict(p0=[[0, 0]], p1=[[T0('B5') + 0.3 * i, 0], [T1('B7') - 0.4 + 0.2 * i, 1.0]], forca=[[0, 1]]), onda=9)
    elif pid == 'C1':
        # v3: EXTERNO, com a cozinha: a porta fecha e a câmera contorna pela frente; nada é cortado ainda (o corte vem em
        # "Escondido", no plano seguinte, de outro ângulo)
        # aberto (geladeira inteira + cozinha) e aproximação lenta até o canto traseiro, onde a borda da serpentina aparece:
        # antecipa "atrás das paredes" sem mostrar nada por dentro
        cam_k = K((0, (0.08, -3.05, 1.40), (0.0, -0.10, 0.82), 28), (0.25, (0.25, -3.05, 1.42), (0.02, -0.05, 0.82), 28),
                  (1, (2.35, -2.50, 1.62), (0.10, 0.12, 0.80), 26))
        porta = lambda g: 100 * (1 - B.suave((g - F('C1', 0.02)) / 1.0))
        curvas['corte'] = [[0, 99.0]]
    elif pid == 'C2':
        # v3: REVELAÇÃO em "Escondido" (corte seco no ataque da palavra): ângulo traseiro-lateral, onde compressor e
        # condensador já estão à vista (são externos); o corte varre a lateral e expõe o que estava escondido — a linha de
        # sucção dentro da parede traseira e o evaporador no congelador. Um pulso parte do compressor e percorre o circuito
        # inteiro; a câmera acompanha o pulso (condensador → capilar → evaporador → sucção) e se afasta até o circuito todo.
        bpy.data.objects['parede_fundo_d'].hide_render = True      # corte ilustrativo também na parede da cozinha
        s_c = next(t for t in obj['tracado'] if t['id'] == 'compressor')['s0']
        cam_k = K((0.00, (1.30, 1.25, 0.88), (0.00, 0.30, 0.55), 28), (0.26, (1.30, 1.30, 1.30), (0.00, 0.33, 0.95), 28),
                  (0.56, (1.42, 1.05, 1.45), (0.05, 0.25, 1.00), 28), (0.70, (1.62, 0.25, 1.70), (0.00, 0.05, 1.25), 28),
                  (0.92, (1.15, 1.62, 1.82), (0.00, 0.14, 0.80), 26), (1.00, (1.20, 1.68, 1.85), (0.00, 0.14, 0.80), 26))
        # v4: termina em 3/4 traseiro alto — condensador de frente, corte lateral com evaporador e sucção, compressor e
        # capilar embaixo: o circuito inteiro e fechado num só quadro
        curvas['corte'] = [[F('C2', 0.08), 0.34], [F('C2', 0.40), 0.0]]
        revela = [[F('C2', 0.10), 0], [F('C2', 0.35), 1]]
        curvas['uPulso'] = [[F('C2', 0.20), s_c], [F('C2', 0.96), s_c + 1.0]]
        # polimento: hierarquia — enquanto o corte abre, o entorno recua (−27 % de luz); circuito e componentes não
        curvas['uFoco'] = [[F('C2', 0.10), 0.0], [F('C2', 0.40), 0.6]]
        for k in ('compressor', 'aluminio', 'arame', 'latao'): M.ajustar(obj['mt'][k], destaque=True)
    elif pid == 'C3':
        zp = 1.425 - 5 * 0.072   # 6º passe do condensador (escoa para −x): condensando, líquido embaixo e vapor em cima
        cam_k = K((0, (0.16, 0.44, zp + 0.035), (0.10, COND_Y, zp), 40), (1, (-0.06, 0.44, zp + 0.035), (-0.12, COND_Y, zp), 40))
        revela = 1.0; rot.add('fluido refrigerante', lambda g: Vector((0.0, COND_Y, zp)), E.T('fluido', apos=T0('C3') - 0.5), T1('C3'), linha=False)   # rodada 8: no ataque de "fluido"
        bpy.data.objects['pote'].hide_render = True   # v2: defeito da v1 — o pote tapava metade do quadro no início do plano
        if R9:   # rodada 9: na posição única, o leite apareceria grande atrás do tubo de cobre (mesmo motivo do pote): close técnico
            for n_ in ('leite', 'leite_rot'): bpy.data.objects[n_].hide_render = True
    elif pid == 'C4':
        cam_k = K((0, (1.65, -1.05, 1.50), (0.0, 0.10, 0.76), 30), (0.75, (1.75, 0.10, 1.55), (0.0, 0.15, 0.76), 30), (1, (1.25, 0.30, 1.35), (0.0, 0.22, 0.70), 32))
        if R9:   # rodada 9: no fim do C4 a câmera sobe e se aproxima do EVAPORADOR (no último quadro da V8 ele estava fora do quadro e o
            # D1 o mostrava ocupando 75 % da tela — salto medido em relatorios/escala_cortes_r9.json). Mesmo início e mesmo meio.
            cam_k = K((0, (1.65, -1.05, 1.50), (0.0, 0.10, 0.76), 30), (0.75, (1.75, 0.10, 1.55), (0.0, 0.15, 0.76), 30), (1, (1.32, -0.05, 1.52), (0.0, 0.0, 1.12), 32))
        revela = 1.0
        fim_man = (E.T('físico') + 0.18) if R9 else T1('C4')   # R9: some com a palavra "físico", antes de a câmera subir ao evaporador (âncoras saem embaixo em 48,09 s)
        man.add('baixa', (0.205, 0.287, 0.70), F('C4', 0.18), fim_man, 0.0)
        man.add('alta', (-0.284, 0.345, 0.70), F('C4', 0.18), fim_man, 1.0)
    elif pid == 'D1':
        cam_k = K((0, (0.48, -0.60, 1.48), (0.0, 0.0, 1.29), 35), (1, (0.36, -0.42, 1.36), (0.0, 0.0, 1.29), 35))
        revela = 1.0; rot.add('Evaporador', lambda g: Vector((0.219, -0.10, 1.30)), E.T('evaporador', apos=T0('D1') - 0.5), T1('D1'), linha=False)
    elif pid == 'D2':
        cam_k = K((0, (0.10, 0.11, 1.440), (-0.15, 0.215, 1.412), 45), (1, (0.02, 0.11, 1.436), (-0.17, 0.205, 1.408), 45))
        revela = 1.0; man.add('baixa', (-0.15, 0.235, 1.43), F('D2', 0.3), T1('D2'), 0.0)
    elif pid == 'D3':
        cam_k = K((0, (0.50, -0.30, 0.95), (0.0, -0.02, 0.95), 30), (1, (0.46, -0.25, 1.00), (0.0, -0.02, 1.00), 30))
        revela = 1.0
        for i, (x, y, z) in enumerate([(-0.10, 0.05, 0.93), LEITE_TOPO(), (-0.12, -0.10, 0.80), (0.0, -0.18, 0.18)]):
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
        rot.add('entra: líquido + vapor', lambda g: Vector((-0.27, Y, Z + r_c)), F('D4', 0.05), F('D4', 0.50), linha=False)
        rot.add('sai: só vapor', lambda g: Vector((0.29, Y, Z + r_c)), E.T('evapora', apos=T0('D4')), T1('D4'), linha=False)   # rodada 8: em "evapora"
        revela = 1.0
    elif pid == 'D5':
        # v2: começa num plano médio do interior (a v1 começava no macro da v1 de D4); o calor dos alimentos já está no evaporador
        cam_k = K((0, (0.46, -0.28, 1.04), (0.0, -0.02, 1.12), 30), (1, (0.85, -0.85, 1.20), (0.0, 0.0, 1.05), 30))
        for i, (x, y, z) in enumerate([(-0.10, 0.05, 0.93), LEITE_TOPO(), (-0.12, -0.10, 0.80)]):
            feixe(f'D5_{i}', [(x, y, z), (x * 0.8, y * 0.7, (z + 1.17) / 2), (x * 0.5, y * 0.4, 1.17)], 0.006,
                  dict(p0=[[0, 0]], p1=[[0, 1.0]], forca=[[F('D5', 0.55), 1], [F('D5', 0.85), 0]]), onda=9)
        revela = 1.0
    elif pid == 'E1':
        # v4: pelo lado em corte (sem os arames do condensador entre a câmera e a linha de sucção); desce com o vapor
        cam_k = K((0, (0.66, 0.02, 1.32), (0.205, 0.287, 1.22), 35), (1, (0.66, 0.02, 0.47), (0.205, 0.287, 0.37), 35))
        revela = 1.0
    elif pid == 'E2':
        cam_k = K((0, (0.48, 0.80, 0.26), (0.0, 0.18, 0.14), 35), (1, (0.34, 0.62, 0.23), (0.0, 0.18, 0.14), 35))
        revela = 1.0; curvas['uTrab'] = [[F('E2', 0.30), 0], [F('E2', 0.45), 1]]
        rot.add('Compressor', lambda g: Vector((0.0, 0.22, 0.26)), E.T('compressor', apos=T0('E2') - 0.5), T1('E2'), linha=False)
    elif pid == 'E3':
        cam_k = K((0, (0.07, 0.42, 0.34), (-0.03, 0.18, 0.18), 40), (1, (0.05, 0.36, 0.30), (-0.035, 0.18, 0.18), 40))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]; curvas['corte2'] = [[0, 0.18]]; extra['corte2'] = dict(n=[0, -1, 0])
        theta = lambda g: 2 * math.pi * 0.8 * (g - T0('E3')) + math.radians(200)
        man.add('cilindro', (-0.045, 0.18, 0.215), F('E3', 0.1), T1('E3'), lambda g: p_rel(tab[int(((theta(g) % (2 * math.pi)) / (2 * math.pi)) * len(tab)) % len(tab)]['p']))
    elif pid == 'E4':
        cam_k = K((0, (-0.10, 0.80, 0.52), (-0.284, 0.345, 0.44), 40), (1, (-0.12, 0.76, 0.54), (-0.284, 0.345, 0.47), 40))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
        rot.add('fluido: mais quente', lambda g: Vector((-0.284, 0.345, 0.50)), E.T('quente', apos=T0('E4') - 0.5), T1('E4'))
        rot.add('ar da cozinha', lambda g: Vector((-0.55, 0.40, 0.70)), E.T('cozinha', apos=T0('E4') - 0.5), T1('E4'), dx=-0.06, linha=False)
    elif pid == 'F1':
        cam_k = K((0, (0.95, 1.50, 0.85), (0.0, 0.345, 0.85), 30), (1, (0.95, 1.50, 1.20), (0.0, 0.345, 1.10), 30))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
        for i, z in enumerate([0.55, 0.85, 1.15]):
            for j, x in enumerate([-0.15, 0.15]):
                pts = [(x, 0.35, z), (x, 0.40, z + 0.10), (x * 1.2, 0.43, z + 0.35), (x * 1.4, 0.44, z + 0.65)]
                feixe(f'F1_{i}{j}', pts, 0.007, dict(p0=[[0, 0]], p1=[[F('F1', 0.10 + 0.1 * i), 0], [F('F1', 0.75 + 0.05 * i), 1.0]], forca=[[0, 1]]), onda=8)
        rot.add('Condensador', lambda g: Vector((0.262, 0.345, 0.70)), E.T('condensador', apos=T0('F1') - 0.5), T1('F1'), linha=False)
    elif pid == 'F2':
        # v2: canal do condensador esticado e ampliado (os arames tapavam os tubos na v1): vapor quente → gotas → líquido
        Y, Z = 1.30, 1.00; r_c = 0.022
        canal_esticado(pid, 'condensador', (-0.30, Y, Z), (0.30, Y, Z), r_c, Y + 0.28)
        pc = lambda xt: (xt - 0.15, Y - 0.215, Z + 0.004)
        cam_k = K((0, pc(-0.27), (-0.27 + 0.10, Y, Z - 0.002), 35), (1, pc(0.19), (0.19 + 0.10, Y, Z - 0.002), 35))
        for i, x in enumerate([-0.26, -0.16, -0.06, 0.04, 0.14, 0.24]):   # calor saindo pela parede do canal para o ar
            feixe(f'F2_{i}', [(x, Y, Z + r_c + 0.002), (x + 0.01, Y, Z + 0.10), (x, Y + 0.01, Z + 0.22)], 0.0045,
                  dict(p0=[[0, 0]], p1=[[F('F2', 0.02 + 0.07 * i) - 0.4, 0], [F('F2', 0.25 + 0.07 * i), 1.0]], forca=[[0, 1]]), onda=11)
        rot.add('entra: vapor quente', lambda g: Vector((-0.27, Y, Z - r_c)), E.T('vapor', apos=T0('F2') - 0.5), E.T('líquido', apos=T0('F2') - 0.5) - 0.3, dy=0.06, linha=False)
        rot.add('sai: líquido', lambda g: Vector((0.29, Y, Z - r_c)), E.T('líquido', apos=T0('F2') - 0.5), T1('F2'), dy=0.06, linha=False)
        revela = 1.0
    elif pid == 'G1':
        cam_k = K((0, (0.48, 0.66, 0.36), (0.245, 0.30, 0.27), 40), (1, (0.42, 0.60, 0.31), (0.245, 0.30, 0.25), 40))
        revela = 1.0
    elif pid == 'G2':
        cam_k = K((0, (0.36, 0.58, 0.26), (0.205, 0.255, 0.22), 50), (1, (0.33, 0.55, 0.25), (0.205, 0.255, 0.22), 50))
        revela = 1.0; rot.add('Capilar', lambda g: Vector((0.235, 0.255, 0.24)), E.T('capilar', apos=T0('G2') - 0.5), T1('G2'))
    elif pid == 'G3':
        # polimento: CONTEXTO — o capilar real inteiro (enrolado junto ao compressor e subindo pela parede até o
        # evaporador), visto pelo lado em corte. O manômetro é um MARCADOR que percorre o capilar real no mesmo ponto s(g)
        # mostrado pela lupa (plano G3z, composto na montagem). Pressão = perfil do modelo naquele s.
        # o capilar inteiro (z 0,2–1,42) ocupa a metade de BAIXO do quadro; a lupa fica sobre a área acima da geladeira
        # rodada 5 (verificação): com a câmera a 1,8 m o trecho ENROLADO junto ao compressor (z 0,17–0,27 m, onde o marcador
        # está durante "A pressão cai bruscamente") ficava abaixo da borda do quadro (v = 1,19). Mesma direção de olhar, 1,6×
        # mais longe: capilar inteiro entre v = 0,44 e 0,93, abaixo da lupa (que cobre v 0,08–0,43).
        cam_k = K((0, (2.38, -1.57, 1.26), (0.13, 0.28, 1.26), 26), (1, (2.33, -1.52, 1.26), (0.13, 0.28, 1.26), 26))
        revela = 1.0
        cap = next(t for t in MOD['circuito'] if t['id'] == 'capilar')['perfil']
        tr = {t['id']: t for t in obj['tracado']}['capilar']; pts = [Vector(q) for q in tr['pts']]
        Ls = [0.0]
        for a_, b_ in zip(pts, pts[1:]): Ls.append(Ls[-1] + (b_ - a_).length)
        def ponto(sl):
            alvo = sl * Ls[-1]
            for k in range(len(pts) - 1):
                if Ls[k + 1] >= alvo: return pts[k].lerp(pts[k + 1], (alvo - Ls[k]) / max(Ls[k + 1] - Ls[k], 1e-9))
            return pts[-1]
        def P_s(sl):
            f = sl * (len(cap) - 1); k = min(int(f), len(cap) - 2); a_ = f - k
            return cap[k]['P_bar'] * (1 - a_) + cap[k + 1]['P_bar'] * a_
        man.add('capilar', lambda g: ponto(s_capilar(g)), F('G3', 0.03), T1('G3'), lambda g: p_rel(P_s(s_capilar(g))))
        bpy.data.objects['pote'].hide_render = True
    elif pid == 'G3z':
        # polimento: LUPA (ampliação didática localizada, corte ilustrativo): o capilar esticado e ampliado; o fluido vem da
        # MESMA tabela do modelo, ponto a ponto (líquido a 33 °C → primeiro vapor em s = 0,53 → mistura a −20 °C, x = 0,33).
        # A câmera percorre o canal no mesmo s(g) do marcador do plano principal. Sem feixes de calor: o capilar não troca
        # calor no modelo (expansão sem troca de energia).
        Y, Z = -1.30, 1.25; r_c = 0.020; X0, X1 = -0.30, 0.30
        canal_esticado(pid, 'capilar', (X0, Y, Z), (X1, Y, Z), r_c, -1.02)
        # rodada 5 (verificação ciencia/verificar_g3.py): o centro da lupa É o ponto do marcador (antes mirava 0,083 em s à
        # frente, e "líquido" chegou a apontar fluido com 1,5 % de vapor). Trava em s = 0,885 (perspectiva oblíqua: a borda direita chega a ~1,0),
        # então a parte abaixo de 0 °C entra na lupa sem passar da ponta do tubo.
        xt = lambda g: X0 + (X1 - X0) * min(s_capilar(g), 0.885)
        cam_k = [(T0('G3'), lambda g: Vector((xt(g) - 0.16, Y - 0.17, Z + 0.006)), lambda g: Vector((xt(g), Y, Z)), 35),
                 (T1('G3'), lambda g: Vector((xt(g) - 0.16, Y - 0.17, Z + 0.006)), lambda g: Vector((xt(g), Y, Z)), 35)]
        sx = lambda sl: X0 + (X1 - X0) * sl
        cap_ = next(t for t in MOD['circuito'] if t['id'] == 'capilar')['perfil']
        s_flash = next(q['s'] for q in cap_ if q['x'] > 0)                     # primeiro vapor no modelo (0,532)
        # cada rótulo preso ao PONTO FÍSICO que descreve (a lupa só desenha os que estão dentro do círculo)
        liq = lambda g: Vector((sx(min(s_capilar(g), s_flash - 0.04)), Y, Z + r_c))
        # rodada 8: rótulos só quando a narração fala ("evapora", "mistura"); "líquido" saiu (a fala diz "parte do líquido evapora")
        rot.add('começa a evaporar', Vector((sx(s_flash), Y, Z + r_c)), E.T('evapora', apos=T0('G3') - 0.5), E.T('resfriando', apos=T0('G3') - 0.5) + 0.15)
        rot.add('mistura fria', Vector((sx(0.96), Y, Z + r_c)), E.T('mistura', apos=T0('G3') - 0.5), T1('G3'))
        revela = 1.0
    elif pid == 'H1':
        cam_k = K((0, (0.40, -0.50, 1.42), (0.0, 0.02, 1.29), 35), (0.35, (0.70, -0.75, 1.45), (0.0, 0.05, 1.18), 33), (1, (1.70, -0.90, 1.60), (0.0, 0.10, 0.78), 30))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
    elif pid == 'H2':
        cam_k = K((0, (1.70, -0.90, 1.60), (0.0, 0.10, 0.78), 30), (1, (1.80, -0.45, 1.62), (0.0, 0.12, 0.78), 30))
        revela = 1.0; curvas['uTrab'] = [[0, 1]]
        for i, (x, y, z) in enumerate([(-0.10, 0.05, 0.93), LEITE_TOPO()]):
            feixe(f'H2_in{i}', [(x, y, z), (x * 0.6, y * 0.5, 1.05), (x * 0.4, y * 0.3, 1.17)], 0.008, cresce(F('H2', 0.05), F('H2', 0.6)), onda=9)
        for i, z in enumerate([0.65, 1.05]):
            feixe(f'H2_out{i}', [(0.0, 0.35, z), (0.0, 0.42, z + 0.15), (0.0, 0.44, z + 0.55)], 0.010, cresce(F('H2', 0.15), F('H2', 0.7)), onda=8)
        # v2: rótulos afastados entre si (na v1 "Compressor" e "Capilar" se sobrepunham e um manômetro cobria "Condensador")
        for nome, anc, dx, dy in [('Evaporador', (0.219, -0.10, 1.30), 0.06, -0.05), ('Compressor', (-0.02, 0.20, 0.24), -0.10, 0.03),
                                  ('Condensador', (0.262, 0.345, 1.20), 0.04, -0.06), ('Capilar', (0.235, 0.255, 0.24), 0.05, 0.06)]:
            rot.add(nome, (lambda a: lambda g: Vector(a))(anc), F('H2', 0.2), T1('H2'), dx=dx, dy=dy, linha=(nome == 'Capilar'))   # rodada 8
        man.add('baixa', (0.205, 0.287, 0.70), F('H2', 0.1), T1('H2'), 0.0); man.add('alta', (-0.284, 0.345, 0.70), F('H2', 0.1), T1('H2'), 1.0)
    elif pid == 'I1':
        # v3: rima com A1 — o personagem entra, abre e DEIXA a porta aberta
        cam_k = K((0, (-0.30, -3.15, 1.40), (-0.34, -0.50, 0.98), 28), (1, (-0.24, -2.90, 1.38), (-0.30, -0.48, 0.98), 28))
        if R9:   # rodada 9: enquanto ele sai pela esquerda com o leite, a câmera devolve a atenção à geladeira ABERTA (prepara o I2)
            cam_k = K((0, (-0.30, -3.15, 1.40), (-0.34, -0.50, 0.98), 28), (0.80, (-0.252, -2.95, 1.384), (-0.308, -0.484, 0.98), 28),
                      (1, (-0.15, -2.84, 1.37), (-0.05, -0.32, 0.96), 28))
        porta = E.porta_ang(E.T('deixa') - 0.13)
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
            rot.add('o calor volta para a mesma cozinha', lambda g: Vector((X, -0.80, 1.95)), F('I3', 0.55), T1('I3'), dx=0.04, dy=-0.06, linha=False)
        else:   # balanço: entrada (Q̇_abs), trabalho (Ẇ, violeta) e saída mais larga (Q̇_abs + Ẇ) — larguras proporcionais
            E_ = MOD['energia_W']; r_in = 0.026; r_out = r_in * E_['Q_rej_total'] / E_['Q_abs_total']; r_w = r_in * E_['W_eletrico'] / E_['Q_abs_total']
            feixe('I4_in', [(X, -1.25, 1.10), (X, -0.70, 1.05), (X, -0.10, 1.00)], r_in, cresce(F('I4', 0.03), F('I4', 0.30)), sobre=True, onda=10)
            feixe('I4_w', [(-0.55, 0.44, 0.32), (-0.40, 0.40, 0.12), (-0.05, 0.22, 0.12)], r_w, cresce(F('I4', 0.33), F('I4', 0.55)), sobre=True, onda=10, cor='#9a6bff')
            feixe('I4_out', [(X, 0.39, 0.95), (X, 0.41, 1.45), (X, 0.38, 2.05)], r_out, cresce(F('I4', 0.58), F('I4', 0.85)), sobre=True, onda=10)
            rot.add('calor retirado', lambda g: Vector((X, -0.95, 1.08)), E.T('retirou', apos=T0('I4')), T1('I4'), dx=0.06, dy=0.05, linha=False)
            rot.add('energia elétrica', lambda g: Vector((-0.45, 0.42, 0.20)), E.T('energia', apos=T0('I4')), T1('I4'), dx=-0.08, dy=0.05)
            rot.add('calor liberado = retirado + elétrica', lambda g: Vector((X, 0.38, 1.95)), E.T('usada', apos=T0('I4')), T1('I4'), dx=0.03, dy=-0.05, linha=False)
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
    # rodada 8: no I1 o personagem PEGA o leite e sai com ele; de I2 a I4 a caixa não está mais na prateleira
    leite = [bpy.data.objects[n] for n in ('leite', 'leite_rot') if n in bpy.data.objects]
    if pid in ('I2', 'I3', 'I4') or (R9 and pid in ('J1', 'J1b', 'J2', 'J3')):   # R9: levado no I1, não volta sem explicação
        for o in leite: o.hide_render = True
    leite_rel = {}
    if pid == 'I1':
        for o in leite: o['anim'] = 1; o.location = o.location - Vector(G.LEITE_POS) + E.LEITE_I1   # R9: deslocamento zero (mesma posição)
        bpy.context.view_layer.update(); leite_base = {o.name: o.matrix_world.copy() for o in leite}
    def anim(g):
        piv.rotation_euler = (0, 0, math.radians(porta(g)))
        if pers: PE.posar(pers, PERS[pid](g))
        if pid == 'I1':
            mao = pers['mao_d'].matrix_world if g < E.T_PEGA else (pers['maof_d'].matrix_world if 'maof_d' in pers else pers['mao_d'].matrix_world)
            if g >= E.T_PEGA and not leite_rel:   # no instante da pega, a caixa passa a seguir a mão (sem salto)
                for o in leite: leite_rel[o.name] = mao.inverted() @ leite_base[o.name]
            for o in leite: o.matrix_world = (mao @ leite_rel[o.name]) if leite_rel else leite_base[o.name]
        if theta: CM.posicionar(mec, theta(g), tab)
        else: CM.posicionar(mec, 2 * math.pi * 0.8 * g, tab)
        B.camera_planos(cam, planos_cam, janela_corte[1] if janela_corte and janela_corte[0] < g < janela_corte[1] else g); bpy.context.view_layer.update(); man.registrar(g)
        return g
    meta = C.meta_comum(curvas, dict(corte=dict(n=[-1, 0, 0]), plano=pid, seq=seq, g0p=p['t0'], g1p=p['t1']))
    # polimento: planos TÉCNICOS (corte ilustrativo, canais ampliados) mantêm a iluminação de leitura da V4 (céu como
    # ambiente, luzes internas sem sombra) — reflexos da cozinha escureciam metais e as sombras apagavam o interior cortado
    if (corte_gab and pid != 'C1') or pid in ('F2', 'G3z'):   # C1 é a cozinha por fora (nada cortado)
        for k in ('env_pos', 'env_cena', 'sombra_areas'): meta.pop(k, None)
        meta['modo_luz'] = 'tecnico'
    else: meta['modo_luz'] = 'cozinha'
    if CORTE_REAL: meta.update(ao_corte=True, ao_tampa=True)   # rodada 8: AO coerente com o corte + tampas sem AO (máscara suavizada)
    meta.update(extra)
    pasta = os.path.join(SAIDA, pid + os.environ.get('SUFIXO_PASTA', '')); os.makedirs(pasta, exist_ok=True)   # rodada 7: variantes de teste em pasta própria
    B.exportar_seg(pasta, g0, g1, anim, rot=rot, extra=meta)
    n = int(round((g1 - g0) * B.FPS)) + 1
    json.dump(dict(g0=g0, fps=B.FPS, quadros=man.quadros[:n]), open(os.path.join(pasta, 'manometros2d.json'), 'w'), ensure_ascii=False)


if __name__ == '__main__':
    if os.environ.get('SUBQUADROS'): B.FPS = 30 * int(os.environ['SUBQUADROS'])   # rodada 7: exportação com sub-quadros (desfoque de movimento)
    ids = sys.argv[1:] or [x for k in PL for x in ([k, k + 'b'] if k in ('A4', 'J1') else [k, 'G3z'] if k == 'G3' else [k])]   # metades da tela dividida e a lupa de G3
    for pid in ids: plano(pid)
