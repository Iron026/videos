"""Episódio 01 completo — cenas por segmento, no tempo GLOBAL da narração real (voz/narracao_ep01).
Uso: python3 ep01_cenas.py <segmento> <pasta_saida>
Cada segmento monta a cena no Blender (reaproveitando quadros.py / navio.py / animatic.py), define câmera e
ações no tempo da fala e exporta para o motor em tempo real v2 (exportar_rt2.exportar_atual, agrupar=True)."""
import sys, os, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler
import lib, navio, cenario, quadros, hidro
from ep_base import (FPS, suave, suave5, lerp, V, camera_em, trilha, surge, oclusor, Rotulos, exportar_seg)

G = 9.81
M_CONT = 20.0                       # massa média adotada por contêiner de 40 pés (t)
T_VERAO = 10.0                      # calado de verão (linha de carga S / centro do disco)
# padronização (acabamento): mesmo céu diurno e mesma água de mar aberto em todos os segmentos de mar
CEU_DIA = dict(sol_elev=36, sol_rot=300, sol_forca=4.3, nuvens=0.5, zenite='#3a7bd0', meio='#8cc2ee', horizonte='#f6e2c4')
AGUA_MAR = dict(absorcao=(0.27, 0.68, 0.80), densidade=0.05, marola=0.40, escala_marola=0.25)
COR_EMPUXO, COR_PESO = '#2fc4ff', '#3b55c9'      # empuxo = água deslocada (ciano); peso (azul-marinho claro)


# =====================================================================================  navio
_FONTE = {}
def texto3d(body, tam, pos, rot, mat, extrude=0.004, alinhar='LEFT'):
    if 'f' not in _FONTE:   # algarismos legíveis (a fonte padrão do Blender confunde 9/0 em tamanhos pequenos)
        _FONTE['f'] = bpy.data.fonts.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fontes', 'Montserrat-700.ttf'))
    cu = bpy.data.curves.new('txt', 'FONT'); cu.body = body; cu.size = tam; cu.extrude = extrude; cu.font = _FONTE['f']
    cu.align_x = alinhar; cu.align_y = 'BOTTOM'
    o = lib.ligar(bpy.data.objects.new('txt', cu)); cu.materials.append(mat)
    o.location = pos; o.rotation_euler = rot
    return o


def escala_calado(x, lado, mat, z0=2.0, z1=14.0):
    """Marcas de calado métricas reais: algarismos de 10 cm a cada 20 cm, base do algarismo = calado;
    metros inteiros com 'M' (ex.: 9M). Pintadas no costado (coordenadas do navio)."""
    objs = []
    rot = (math.pi / 2, 0, math.pi if lado > 0 else 0)
    for i in range(int(round((z1 - z0) / 0.2)) + 1):
        z = z0 + i * 0.2; dm = int(round(z * 10)) % 10
        txt = f'{int(round(z))}M' if dm == 0 else str(dm)
        b = navio.meia_boca(x, z + 0.05) + 0.02
        o = texto3d(txt, 0.135, (x, lado * b, z), rot, mat, alinhar='CENTER'); objs.append(o)
    return objs


def marca_linha_carga(x, lado, mat):
    """Marca de borda livre (linha de carga) em proporções reais: anel Ø300 mm × 25 mm cortado por linha de 450 mm
    com o centro no calado de verão; linha de convés de 300 mm; a 540 mm a vante, linha vertical e linhas de 230 mm:
    S (verão), T = S + T/48 (tropical), W = S − T/48 (inverno) para vante; F = S + FWA e TF = T + FWA para ré."""
    objs = []; e = 0.025; zS = T_VERAO; d48 = T_VERAO / 48.0
    TPC = hidro.RHO * hidro.area_flutuacao(T_VERAO) / 100.0; FWA = hidro.RHO * hidro.carena(T_VERAO)[0] / (4 * TPC) / 1000.0
    y = lambda z: lado * (navio.meia_boca(x, z) + 0.012)
    pts = [(x + 0.1375 * math.cos(a), y(zS), zS + 0.1375 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 48)]
    objs.append(lib.tubo('ll_anel', pts, r=e / 2, mat=mat, lados=6))
    objs.append(lib.caixa('ll_disco', (0.45, 0.01, e), (x, y(zS), zS), mat))
    objs.append(lib.caixa('ll_conves', (0.30, 0.01, e), (x, y(navio.PONTAL - 0.05), navio.PONTAL - 0.05 - e / 2), mat))
    xv = x + 0.54                                                # vertical a vante do disco
    zs = dict(S=zS, T=zS + d48, W=zS - d48, F=zS + FWA, TF=zS + d48 + FWA)
    objs.append(lib.caixa('ll_vert', (e, 0.01, zs['TF'] - zs['W'] + 0.05), (xv, y(zS), (zs['TF'] + zs['W']) / 2), mat))
    rot = (math.pi / 2, 0, math.pi if lado > 0 else 0)
    for k, z in zs.items():
        sentido = 1 if k in ('S', 'T', 'W') else -1                # S/T/W para vante, F/TF para ré
        xm = xv + sentido * (0.115 + e / 2)
        objs.append(lib.caixa('ll_' + k, (0.23, 0.01, e), (xm, y(z), z - e / 2), mat))   # borda superior = nível da marca
        objs.append(texto3d(k, 0.10, (xm + sentido * 0.20, y(z), z - 0.05), rot, mat, alinhar='CENTER'))
    return objs, zs, FWA


PINTURA_OUTRO = dict(casco=[(navio.CALADO_LEVE - 0.2, '#6b2a2a'), (navio.CALADO_CARGA + 0.9, '#2b2f36'), (navio.PONTAL - 1.0, '#c3c8cc'),
                             (navio.PONTAL - 0.55, '#2f6f62'), (1e9, '#c3c8cc')],
                     super='#dfe5e8', chamine='#2f6f62', amarelo='#8d959c', conves='#6d6f6a')


def repintar(objs, p):
    """Troca os materiais do navio pela pintura p (casco em faixas, superestrutura, chaminé, estruturas amarelas, convés)."""
    mats = dict(casco=lib.mat_faixas_z('casco_outro', p['casco'], rug=0.38), super=lib.mat_pintura('super_outro', p['super'], rug=0.4),
                chamine=lib.mat_pintura('chamine_outro', p['chamine'], rug=0.4), amarelo=lib.mat_pintura('cinza_outro', p['amarelo'], rug=0.45),
                conves=lib.mat_pintura('conves_outro', p['conves'], rug=0.7))
    for o in objs:
        if not hasattr(o.data, 'materials'): continue
        for i, m in enumerate(o.data.materials):
            if m and m.name.split('.')[0] in mats: o.data.materials[i] = mats[m.name.split('.')[0]]


def navio_completo(T, com_carga=True, filtro=None, marcas=True, raiz_nome='navio', pintura=None, niveis=4, semente=3):
    """Navio pronto (casco + superestrutura + convés + carga opcional) preso a uma âncora animada."""
    raiz = bpy.data.objects.new(raiz_nome, None); lib.ligar(raiz); raiz['anim'] = 1
    objs = navio.navio_pronto(nivel_carga=4, com_carga=False)
    if pintura: repintar(objs, pintura)
    conts = navio.carga(niveis, semente=semente, filtro=filtro) if com_carga else []
    info = {}
    if marcas:
        mb = lib.mat_pintura('tinta_branca', '#f6f4ec', rug=0.5)
        for lado in (1, -1):
            for xm in (91.0, 0.6, -90.0): objs += escala_calado(xm, lado, mb)
            ll, zs, fwa = marca_linha_carga(-4.0, lado, mb); objs += ll; info['linhas'] = zs; info['FWA'] = fwa
    for o in objs + conts:
        if o.parent is None: o.parent = raiz
    raiz.location = (0, 0, -T)
    return raiz, conts, info


def calado_com(n_cont):
    """Calado de equilíbrio com n contêineres de M_CONT t sobre o navio leve (T = 8,0 m)."""
    V0 = hidro.carena(navio.CALADO_LEVE)[0]
    return hidro.calado_para(V0 + n_cont * M_CONT / hidro.RHO)


def volume_submerso(nome, T, x0=navio.POPA, x1=navio.PROA, mat=None, n=120, nz=24, infla=0.0):
    """Sólido fantasma do volume de água deslocado (casco abaixo de z = T, coordenadas do navio), fechado no topo."""
    xs = np.linspace(x0 + 0.05, x1 - 0.05, n); vs, fs = [], []
    secs = []
    for x in xs:
        k = navio.quilha(x)
        if T <= k + 0.05: secs.append(None); continue
        zs = np.linspace(k, T, nz); pts = [(navio.meia_boca(x, z) + infla, z - (infla if j == 0 else 0.0)) for j, z in enumerate(zs)]
        anel = [(x, -b, z) for b, z in pts[::-1]] + [(x, b, z) for b, z in pts]
        secs.append(len(vs)); vs += anel
    m = 2 * nz
    val = [s for s in secs if s is not None]
    for a, b in zip(val, val[1:]):
        for j in range(m - 1): fs.append((a + j, a + j + 1, b + j + 1, b + j))
        fs.append((a + m - 1, a, b, b + m - 1))           # tampa da linha d'água entre seções
    fs.append(tuple(range(val[0], val[0] + m))[::-1]); fs.append(tuple(range(val[-1], val[-1] + m)))
    o = lib.malha(nome, vs, fs, mat or lib.mat_fantasma('deslocado', COR_EMPUXO, alfa=0.34, brilho=1.2), suave=True, angulo=60)
    o.visible_shadow = False
    return o


def mar_aberto(ext=700, res=4.0, fundo=-70):
    magua = lib.mat_agua('agua_mar', espalha=0.0, rug=0.05, **AGUA_MAR)
    agua = lib.bloco_agua('agua', -ext, ext, -ext, ext, fundo, magua, res=res, amp=0.22, escala=1.0)
    mlonge = lib.mat_pintura('mar_longe', '#2c78a0', rug=0.1, variacao=0.06, escala_var=0.02)
    for (a0, a1, b0, b1) in ((-4000, -ext, -4000, 4000), (ext, 4000, -4000, 4000), (-ext, ext, ext, 4000), (-ext, ext, -4000, -ext)):
        lib.bloco_agua('longe', a0, a1, b0, b1, -30, mlonge, res=400, amp=0.0, so_superficie=True)
    return agua


# =====================================================================================  SEG02 · o gigante (4,40–15,10)
def seg02(pasta):
    lib.nova_cena()
    lib.ceu_estilizado(**CEU_DIA)
    # OUTRO navio (não é o que será construído): pintura cinza e verde, chaminé verde, 5 camadas de contêineres
    raiz, conts, _ = navio_completo(0.0, pintura=PINTURA_OUTRO, niveis=5, semente=8, raiz_nome='navio_outro')
    n_total = len(conts); T = calado_com(n_total); raiz.location.z = -T
    mar_aberto()
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    # câmera rente à água junto ao costado olhando para cima (escala do gigante) → sobe revelando a carga →
    # abre para o navio inteiro flutuando → aproxima da linha d'água ("Como isso é possível?")
    K = [(4.40, (36, -25.5, 0.9), (20, -8, 15), 17),
         (6.50, (30, -31, 4.0), (8, 0, 17), 18),
         (8.60, (16, -48, 13), (-6, 0, 16), 21),
         (10.7, (44, -84, 24), (0, 0, 9), 23),
         (12.7, (178, -96, 30), (8, 0, 4), 26),
         (15.1, (150, -66, 12), (22, 0, 2), 30)]
    def anim(g):
        p, a, l = trilha(K, g); camera_em(cam, p, a, l)
        raiz.location.z = -T + 0.12 * math.sin(2 * math.pi * g / 9.0); raiz.rotation_euler = (0.004 * math.sin(2 * math.pi * g / 11.0), 0, 0)
    exportar_seg(pasta, 4.40, 15.10, anim, extra=dict(segmento='02', calado=T, n_cont=n_total))
    print('CALADO_CARREGADO', T, 'CONTEINERES', n_total)


# =====================================================================================  SEG03 · estaleiro (15,10–30,30)
def seg03(pasta):
    """Mesmo estaleiro, pórtico e içamento aprovados (animatic.plano23). Tempo do guindaste remapeado para a fala:
    descida 5,6→11,5 em 15,1→20,7 s; descida final e deslize em tempo real (balanço e limite de folga intactos);
    encaixe em 23,6 s ("soldadas"); depois as chapas que faltam chegam ao costado e à proa (peça por peça)."""
    import animatic as A
    rot = Rotulos()

    def exportador(posicionar, cam, ctx):
        raiz = bpy.data.objects['navio']; rnd = random.Random(9)
        existentes = {o.name.split('.')[0] for o in bpy.data.objects if o.name.startswith('painel') and o.name[6:7] in '-1'}
        mverm = bpy.data.materials['primer_verm']; mcinza = bpy.data.materials['primer']; mazul = bpy.data.materials['primer_azul']
        xs = list(np.arange(-34.0, 98.0, 8.0)); zs = [0.0, 3.0, 7.5, 12.0, navio.PONTAL]
        novos = []
        for lado in (1, -1):
            for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
                for j, (za, zb) in enumerate(zip(zs, zs[1:])):
                    if xa >= navio.limite_proa(za) - 1.0: continue
                    nome = f'painel{lado}_{i}_{j}'
                    if nome in existentes or (lado, i, j) in ((1, 13, 2), (1, 13, 3)): continue
                    cor = mverm if j <= 1 else (mazul if (i + j) % 3 == 0 else mcinza)
                    o = navio.painel_costado('novo' + nome[6:], xa, xb, za, zb, lado, cor, folga=0.04); o.parent = raiz
                    novos.append((o, lado, xa, j))
        lat = sorted([n for n in novos if n[2] < 62.0], key=lambda n: (n[3], n[2]))
        pro = sorted([n for n in novos if n[2] >= 62.0], key=lambda n: (n[3], n[2]))
        for k, (o, lado, xa, j) in enumerate(lat):
            surge(o, 25.55 + 1.35 * k / max(1, len(lat) - 1), dur=0.45, d=(0, lado * 2.5, 4.0))
        for k, (o, lado, xa, j) in enumerate(pro):
            surge(o, 27.05 + 1.15 * k / max(1, len(pro) - 1), dur=0.45, d=(0, lado * 2.5, 4.0))
        # faíscas de solda: na costura do painel recém-encaixado e no fundo (bojo), piscando
        mf = lib.mat_emissivo('faisca_ep', '#ffcf7a', 30.0)
        Z0 = raiz.location.z
        focos = [(Vector((74.0, navio.meia_boca(74.0, 7.6) + 0.2, Z0 + 7.6)), 23.75, 25.2),
                 (Vector((70.2, navio.meia_boca(70.2, 12.0) + 0.2, Z0 + 12.0)), 24.0, 25.4),
                 (Vector((38.0, navio.meia_boca(38.0, 1.0) + 0.25, Z0 + 1.0)), 24.9, 26.4),
                 (Vector((22.0, navio.meia_boca(22.0, 1.0) + 0.25, Z0 + 1.0)), 25.1, 26.4)]
        for (c, ta, tb) in focos:
            for i in range(14):
                d = Vector((rnd.uniform(-0.6, 1.0), (1 if c.y > 0 else -1) * rnd.uniform(0.2, 1.4), rnd.uniform(-1.6, 0.4)))
                f = lib.tubo('faisca', [tuple(c), tuple(c + d * 0.6)], r=0.03, mat=mf)
                t0 = rnd.uniform(ta, tb - 0.2); surge(f, t0, dur=0.02, t1=t0 + rnd.uniform(0.08, 0.25), dur1=0.02)
        def tguind(g): return float(np.interp(g, [15.10, 20.70, 21.70, 23.60, 31.0], [5.60, 11.50, 12.50, 14.40, 15.0]))
        def painel_z(tc):
            if tc < 11.5: return lerp(13.0, 1.2, suave((tc - 5.6) / 5.9))
            if tc < 12.5: return lerp(1.2, 0.0, suave5((tc - 11.5) / 1.0))
            return 0.0
        KA = [(15.10, (236, 142, 96), (34, 0, 6), 24), (18.50, (176, 66, 38), (66, 4, 14), 24)]
        # bombordo (y < 0), dentro do vão do pórtico (pernas em y = ±44): fundo → costado → proa, sem obstruções
        # lado iluminado (+y), entre o costado e as pernas do pórtico (y = 44): fundo → costado → proa
        KD = [(24.80, (30, 31, 2.6), (34, 0, 2.2), 21), (26.40, (50, 34, 9), (56, 0, 9), 21), (28.40, (104, 36, 15), (84, 0, 11), 21)]
        KE = [(28.40, (175, 138, 82), (10, 0, 8), 24), (30.30, (166, 128, 74), (10, 0, 8), 24)]
        def anim(g):
            tc = tguind(g); posicionar(tc)
            if g < 18.50: p, a, l = trilha(KA, g)
            elif g < 21.40:
                k = suave((g - 18.5) / 2.9); p = V(101, 39, 15).lerp(V(98, 36, 19), k)
                a = V(73.5, 14.5, 16.5 + 3.0 + max(0.0, painel_z(tc) - 3.0) * 0.30); l = 26
            elif g < 24.80:
                k = suave((g - 21.4) / 3.4); p = V(97, 35, 25).lerp(V(93, 32.5, 23), k); a = V(73, 14.5, 16.5).lerp(V(73.5, 14.5, 15.5), k); l = 30
            elif g < 28.40: p, a, l = trilha(KD, g)
            else: p, a, l = trilha(KE, g)
            camera_em(cam, p, a, l)
        exportar_seg(pasta, 15.10, 30.30, anim, rot, extra=dict(segmento='03'))
    A.plano23(pasta, exportador=exportador)


# =====================================================================================  SEG04 · não é um bloco maciço (30,30–41,55)
def seg04(pasta):
    """Casco pronto sobre os picadeiros. Corte ilustrativo a meia-nau: a parte de vante se afasta (vista explodida)
    e revela o duplo fundo, os tanques laterais (compartimentos) e o porão vazio e seco."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=36, sol_rot=70, sol_forca=4.4, nuvens=0.5, zenite='#3a7bd0', meio='#8cc2ee', horizonte='#f7dcb4', sol_cor=(1.0, 0.9, 0.74))
    lib.caixa('chao', (900, 600, 2), (0, 0, -1.0), lib.mat_concreto('chao', (162, 158, 148), escala=0.04))
    Z0 = 1.6; XC = 3.2
    mbl = lib.mat_concreto('picad_conc', (140, 136, 128))
    for x in np.arange(-92, 96, 7.0):
        k = navio.quilha(x); lib.caixa('picad', (1.4, 2.2, Z0 + k - 0.3), (x, 0, (Z0 + k - 0.3) / 2), mbl, bisel=0.05)
    raiz, solido = quadros.navio_em_corte(XC, -Z0, carga_porao=False, porao_aberto=True, filtro_conves=lambda k, j, n: False,
                                          esp_linha=0.0, casca=True)
    lib.ocultar(solido)
    for (x, y, z, r) in ((-1.5, 2.0, 2.2, 1.9), (-4.0, -3.5, 2.2, 0.6), (0.5, 14.4, navio.PONTAL + 0.02, 2.4)):
        for o in cenario.operario((x, y, z), rot=r, colete='#f08a24'): o.parent = raiz
    # parte de vante (x > XC): casco, bulbo e convés, numa âncora que se afasta
    frente = bpy.data.objects.new('frente', None); lib.ligar(frente); frente['anim'] = 1; frente.location = (0, 0, Z0)
    mh = navio.mat_casco()
    pf = [navio.malha_casco('frente_casco', mh, XC, navio.PROA, n=70), navio.bulbo('frente_bulbo', mh)]
    mc = lib.mat_pintura('conves', navio.COR['conves'], rug=0.7); vs, fs = [], []
    for x in np.arange(XC + 0.05, 103.5, 1.0):
        b = navio.meia_boca(x, navio.PONTAL)
        if b < 0.2: continue
        vs += [(x, -b + 0.05, navio.PONTAL + 0.02), (x, b - 0.05, navio.PONTAL + 0.02)]
    for j in range(len(vs) // 2 - 1): fs.append((2 * j, 2 * j + 2, 2 * j + 3, 2 * j + 1))
    pf.append(lib.malha('frente_conves', vs, fs, mc))
    for o in pf: o.parent = frente
    # destaques (fantasmas planos rente à face de corte): compartimentos (células) e o grande volume de ar do porão
    am = lib.mat_fantasma('destaque_comp', '#f3b544', alfa=0.55, brilho=1.2); ar = lib.mat_fantasma('destaque_ar', '#bfeaff', alfa=0.28, brilho=1.1)
    xq = XC + 0.10; zq = Z0
    def quad(nome, y0, y1, z0, z1, mat):
        return lib.malha(nome, [(xq, y0, zq + z0), (xq, y1, zq + z0), (xq, y1, zq + z1), (xq, y0, zq + z1)], [(0, 1, 2, 3)], mat)
    for yc in np.arange(-12.6, 12.61, 3.15):
        surge(quad('d_cel_f', yc - 1.3, yc + 1.3, 0.4, 1.6, am), 36.95, dur=0.3, t1=39.6, dur1=0.5)
    for s_ in (-1, 1):
        for (za, zb) in ((2.6, 6.0), (6.45, 9.85), (10.3, 13.7), (14.15, 17.0)):
            surge(quad('d_cel_l', s_ * 15.0 - 0.65, s_ * 15.0 + 0.65, za, zb, am), 37.1, dur=0.3, t1=39.6, dur1=0.5)
    ar_v = lib.caixa('ar_porao', (XC + 8.9, 24.6, navio.PONTAL - 2.6), ((XC - 9.9) / 2 + 0.05, 0, Z0 + 2.3 + (navio.PONTAL - 2.6) / 2),
                     lib.mat_fantasma('ar_interno', '#e6f6ff', alfa=0.17, brilho=1.15))
    ar_v.visible_shadow = False; surge(ar_v, 39.0, dur=0.7)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    rot = Rotulos()
    rot.add('Corte ilustrativo', (XC, -14.0, Z0 + navio.PONTAL + 0.5), 33.9, 41.4, dx=0.05, dy=-0.07)
    rot.add('Compartimentos', (XC, -15.0, Z0 + 8.0), 37.0, 39.4, dx=0.06, dy=0.06)
    rot.add('Ar: espaço interno seco', (XC, 0.0, Z0 + 9.5), 39.2, 41.4, dx=0.04, dy=0.08)
    K = [(30.30, (150, -132, 52), (6, 0, 9), 26), (33.00, (78, -74, 28), (6, 0, 9), 25), (35.30, (48, -44, 17), (0, 0, 8), 23),
         (37.20, (36, -28, 13), (0, 0, 7.5), 22), (39.20, (30, -19, 20), (-6, 0, 7), 22), (41.55, (26, -15, 20.5), (-10, 0, 6.5), 22)]
    def anim(g):
        frente.location.x = 70.0 * suave5((g - 33.15) / 1.7)
        p, a, l = trilha(K, g); camera_em(cam, p, a, l)
    exportar_seg(pasta, 30.30, 41.55, anim, rot, extra=dict(segmento='04'))


# =====================================================================================  SEG05 · dique seco inundado (41,55–48,00)
def seg05(pasta):
    """Dique seco: o casco pronto está apoiado nos picadeiros (quilha a −11,4 m). A comporta deixa a água entrar
    (tempo acelerado). A água sobe pelo casco; quando a profundidade sobre a quilha chega ao calado de equilíbrio do
    navio leve (8,0 m), o empuxo iguala o peso: o casco deixa os picadeiros e passa a acompanhar o nível, mantendo
    o calado (a linha d'água fica parada na marca 8M enquanto o dique continua enchendo)."""
    lib.nova_cena()
    lib.ceu_estilizado(**CEU_DIA)
    T_EQ = navio.CALADO_LEVE; Z_PISO = -13.0; Z_QUILHA0 = Z_PISO + 1.6
    X0, X1, YD = -112.0, 116.0, 27.0
    mc = lib.mat_concreto('concreto_dique', (158, 153, 142)); mcp = lib.mat_concreto('chao', (162, 158, 148), escala=0.04)
    lib.caixa('piso_dique', (X1 - X0 + 12, 2 * YD + 12, 2.0), ((X0 + X1) / 2, 0, Z_PISO - 1.0), lib.mat_concreto('piso', (128, 124, 116)))
    for sy in (-1, 1): lib.caixa('parede', (X1 - X0 + 12, 6.0, 16.0 + 3.0), ((X0 + X1) / 2, sy * (YD + 3.0), (Z_PISO + 3.0) / 2), mc)
    lib.caixa('cabeceira', (6.0, 2 * YD + 12, 19.0), (X0 - 3.0, 0, (Z_PISO + 3.0) / 2), mc)
    for sy in (-1, 1): lib.caixa('cais_lado', (900, 300, 2.0), (0, sy * (YD + 6.0 + 150), 2.0), mcp)
    lib.caixa('cais_fundo', (300, 2 * YD + 12, 2.0), (X0 - 6.0 - 150, 0, 2.0), mcp)
    # comporta (caixão flutuante) com aberturas de alagamento e o mar do lado de fora
    mporta = lib.mat_pintura('comporta', '#5a6470', rug=0.5, metal=0.2)
    lib.caixa('comporta', (4.0, 2 * YD, 16.4), (X1 + 2.0, 0, Z_PISO + 8.2), mporta, bisel=0.2)
    mam = lib.mat_pintura('amarelo', '#f3b544', rug=0.42)
    lib.caixa('passarela_comp', (4.4, 2 * YD + 2, 0.6), (X1 + 2.0, 0, Z_PISO + 16.7), mam)
    magua = lib.mat_agua('agua_mar', espalha=0.0, rug=0.05, **AGUA_MAR)
    lib.bloco_agua('mar', X1 + 4.0, 900, -900, 900, -30, magua, res=4.0, amp=0.2)
    mlonge = lib.mat_pintura('mar_longe', '#2c78a0', rug=0.1, variacao=0.06, escala_var=0.02)
    lib.bloco_agua('longe', 900, 4000, -4000, 4000, -30, mlonge, res=400, amp=0.0, so_superficie=True)
    # água do dique: bloco com origem no piso; o nível sobe por escala vertical (água animada)
    adq = lib.bloco_agua('agua_dique', X0 + 0.3, X1 - 0.3, -YD + 0.3, YD - 0.3, -(0.0 - Z_PISO), magua, res=1.5, amp=0.08)
    adq.data.transform(Matrix.Translation((0, 0, -Z_PISO))); adq.location.z = Z_PISO; adq['anim'] = 1
    H0 = -Z_PISO                       # altura da água do bloco na escala 1 (até z = 0)
    # picadeiros
    mbl = lib.mat_concreto('picad_conc', (140, 136, 128)); mm = lib.mat_pintura('picadeiro', '#6a4f35', rug=0.9)
    for x in np.arange(-92, 96, 7.0):
        k = navio.quilha(x); h = 1.6 + k - 0.3
        lib.caixa('picad', (1.4, 2.2, h), (x, 0, Z_PISO + h / 2), mbl, bisel=0.05)
        lib.caixa('picad_m', (1.6, 2.4, 0.3), (x, 0, Z_PISO + h + 0.15), mm, bisel=0.03)
    raiz, _, _ = navio_completo(0.0, com_carga=False); raiz.location.z = Z_QUILHA0
    # jatos de entrada pelas aberturas da comporta (só enquanto o nível de dentro está abaixo do de fora)
    mj = lib.mat_fantasma('jato_dique', '#eef9ff', alfa=0.55, brilho=1.4)
    for yy in (-16, -6, 6, 16):
        j = lib.malha('jato', [(X1, yy - 1.2, Z_PISO + 2.5), (X1, yy + 1.2, Z_PISO + 2.5), (X1 - 9, yy + 2.2, Z_PISO + 0.3), (X1 - 9, yy - 2.2, Z_PISO + 0.3)],
                      [(0, 1, 2, 3)], mj)
        surge(j, 41.7, dur=0.3, t1=43.6, dur1=0.6)
    def nivel(g): return float(np.interp(g, [41.55, 42.25, 46.10, 48.00], [Z_PISO + 0.15, Z_QUILHA0, Z_QUILHA0 + T_EQ, Z_QUILHA0 + T_EQ + 1.9]))
    def quilha_z(g): return max(Z_QUILHA0, nivel(g) - T_EQ)          # apoiado até flutuar; depois acompanha o nível
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    xm = 91.0; yb = -navio.meia_boca(xm, 8.0)
    def anim(g):
        L = nivel(g); adq.scale = (1, 1, max(0.01, (L - Z_PISO) / H0)); raiz.location.z = quilha_z(g)
        if g < 45.6:
            K = [(41.55, (150, -128, 98), (22, 0, -8), 24), (43.6, (118, -64, 42), (70, 0, -9), 24), (45.6, (104, -36, 12), (86, -8, -6), 26)]
            p, a, l = trilha(K, g)
        else:                                                         # close nas marcas de calado da proa, subindo com o nível
            k = suave((g - 45.6) / 0.8)
            alvo = Vector((xm + 0.3, yb, L + 0.2)); p0 = Vector((104, -36, 12))
            p = p0.lerp(alvo + Vector((-4.5, -6.0, 1.0)), k); a = Vector((86, -8, -6)).lerp(alvo, k); l = lerp(26, 33, k)
        camera_em(cam, p, a, l)
    rot = Rotulos()
    rot.add('Picadeiros', (60, 0, Z_PISO + 2.2), 42.5, 45.0, dx=0.06, dy=0.06)
    rot.add('Começa a flutuar', lambda g: Vector((xm, yb, quilha_z(g) + T_EQ + 1.4)), 46.15, 48.0, dx=-0.10, dy=-0.06)
    exportar_seg(pasta, 41.55, 48.00, anim, rot, extra=dict(segmento='05', nivel_flutua=Z_QUILHA0 + T_EQ, calado=T_EQ))


# =====================================================================================  SEG06/07 · pressão, empuxo, Arquimedes (48,00–74,85) e casco × bloco (83,85–94,55)
def cena_secao(T=None):
    lib.nova_cena(amostras=128)
    lib.ceu_estilizado(sol_elev=50, sol_rot=120, sol_forca=4.4, nuvens=0.4, zenite='#3a7bd0', meio='#8cc2ee')
    XC = 3.2; T = T or navio.CALADO_LEVE
    raiz, solido = quadros.navio_em_corte(XC, T, carga_porao=False, porao_aberto=False, filtro_conves=lambda k, j, n: False, esp_linha=0.0)
    bpy.context.view_layer.update()
    quadros.oceano_profundo(XC, solido, absorcao=(0.30, 0.74, 0.84), densidade=0.012)
    mp = lib.mat_pintura('peixe', '#c9d6dd', rug=0.3, metal=0.5)
    cenario.cardume((XC - 12, 30, -20), 4.0, 16, 0.5, mp, semente=4, direcao=math.radians(100))
    V0, _, KB = hidro.carena(T)
    return XC, T, raiz, solido, KB


def _setas_forcas(XC, T, KB, L=4.0):
    """Empuxo (ciano, mesma cor da água deslocada) em B e peso (azul-marinho) em G: iguais, opostos, mesma vertical."""
    xs = XC + 0.9; zB, zG = KB - T, 12.5 - T
    me = lib.mat_emissivo('seta_empuxo', '#a6f0ff', 2.6); mw = lib.mat_emissivo('seta_peso', COR_PESO, 2.0)   # ciano claro: destaca dentro do volume ciano
    B = lib.seta3d('empuxo', (xs, 0, zB), (0, 0, 1), L, r=1.6, mat=me, cabeca=2.0)
    Wn = lib.seta3d('peso', (xs, 0, zG), (0, 0, -1), L, r=1.6, mat=mw, cabeca=2.0)
    pB = lib.cilindro('ponto_B', 0.95, 0.3, (xs, 0, zB), lib.mat_emissivo('ponto_B', COR_EMPUXO, 2.2), rot=(0, math.pi / 2, 0), lados=24)
    pG = lib.cilindro('ponto_G', 0.95, 0.3, (xs, 0, zG), lib.mat_emissivo('ponto_G', COR_PESO, 2.2), rot=(0, math.pi / 2, 0), lados=24)
    for o in (B, Wn, pB, pG): o.visible_shadow = False
    return B, Wn, pB, pG, xs, zB, zG


def _area_deslocada(XC, T, t0):
    sec = navio._secao(XC, 80); pts = [(y, z - T) for y, z in sec if z <= T]; b = navio.meia_boca(XC, T)
    poly = [(b, 0.0)] + pts + [(-b, 0.0)]
    area = lib.malha('area_deslocada', [(XC + 0.06, y, z) for y, z in poly], [tuple(range(len(poly)))], lib.mat_fantasma('area_desl', COR_EMPUXO, alfa=0.42, brilho=1.2))
    area.visible_shadow = False; surge(area, t0, dur=0.6)
    return area


def seg0607(pasta):
    """Pressão → empuxo → Arquimedes, com poucos elementos por vez (legível no celular):
    6 setas de pressão (rasas e fundas nos costados, 2 no fundo), cor e tamanho ∝ profundidade; as laterais se
    compensam e somem; as do fundo convergem para B e viram UMA seta: o empuxo (ciano, a cor da água deslocada).
    Depois: volume deslocado (ciano) e peso do navio (azul-marinho), iguais e opostos."""
    XC, T, raiz, solido, KB = cena_secao()
    rot = Rotulos(); xs = XC + 0.9
    def seta_p(nome, ponto, n_out, prof, cor, t0, t1):
        L = 0.55 * prof
        o = lib.seta3d(nome, tuple(Vector(ponto) + n_out * (L + 0.25)), tuple(-n_out), L, r=0.55, mat=lib.mat_emissivo('p_' + nome, cor, 1.9), cabeca=2.3)
        o.visible_shadow = False; surge(o, t0, dur=0.45, escala=True, t1=t1, dur1=0.6); return o
    for s_ in (1, -1):
        for (prof, cor, t0) in ((2.0, '#cdeefa', 50.9), (6.0, '#6fd0f5', 52.0)):
            b = navio.meia_boca(XC, T - prof); seta_p(f'lat{s_}_{prof}', (xs, s_ * (b + 0.1), -prof), Vector((0, s_, 0)), prof, cor, t0, 58.6)
    # fundo: âncoras animadas (convergem para a linha de centro e se fundem no empuxo)
    fundo = []
    for s_ in (1, -1):
        anc = bpy.data.objects.new(f'fundo_anc{s_}', None); lib.ligar(anc); anc['anim'] = 1
        L = 0.55 * T
        lib.seta3d(f'fundo{s_}', (0, 0, -L - 0.25), (0, 0, 1), L, r=0.55, mat=lib.mat_emissivo('p_fundo', '#2fb6ee', 2.0), cabeca=2.3).parent = anc
        fundo.append((anc, s_))
    B, Wn, pB, pG, xs, zB, zG = _setas_forcas(XC, T, KB)
    surge(B, 61.45, dur=0.6, escala=True); surge(pB, 61.4, dur=0.3)
    surge(Wn, 71.2, dur=0.6, escala=True); surge(pG, 71.1, dur=0.3)
    _area_deslocada(XC, T, 66.4)
    vol = volume_submerso('vol_deslocado', T, x0=-70.0, x1=XC - 0.05, infla=0.12); vol.parent = raiz; surge(vol, 66.6, dur=0.8)
    rot.add('Pressão da água', (xs, -navio.meia_boca(XC, T - 6.0) - 2.0, -6.0), 51.4, 56.6, dx=0.05, dy=0.10)
    rot.add('Empuxo', (xs, 0, zB + 3.2), 62.0, 66.4, dx=0.08, dy=0.02)
    rot.add('Água deslocada', (XC, -8.0, -4.5), 66.6, 68.8, dx=0.06, dy=0.10)
    rot.add('Empuxo = peso da água deslocada', (xs, 0, zB + 3.2), 68.8, 74.85, dx=0.05, dy=0.06)
    rot.add('Peso do navio', (xs, 0, zG - 2.0), 71.4, 74.85, dx=0.06, dy=-0.06)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    K = [(48.00, (XC + 92, -26, 4), (XC - 6, 0, -3), 22), (50.8, (XC + 50, -16, -3), (XC, -6, -4), 22),
         (54.5, (XC + 44, -14, -6), (XC, -7, -6), 22), (57.5, (XC + 56, 0, -2), (XC - 2, 0, -3), 22),
         (61.5, (XC + 52, 0, 0), (XC - 3, 0, -1.5), 22), (66.0, (XC + 58, -6, 2), (XC - 4, 0, -1), 22),
         (74.85, (XC + 54, -4, 1), (XC - 4, 0, -1), 22)]
    yb = navio.meia_boca(XC, 0.5) - 1.0
    def anim(g):
        for (anc, s_) in fundo:
            k = suave((g - 60.3) / 1.1)                          # convergem para a linha de centro
            y = s_ * lerp(6.0, 0.4, k)
            vis = (g >= 52.9) and (g <= 61.6)
            e = min(suave((g - 52.9) / 0.45), 1 - suave((g - 61.3) / 0.3)) if vis else 1e-4
            anc.location = (xs, y, -T); anc.scale = (max(e, 1e-4),) * 3
        p, a, l = trilha(K, g); camera_em(cam, p, a, l)
    exportar_seg(pasta, 48.00, 74.85, anim, rot, extra=dict(segmento='0607', KB=KB, T=T))


# =====================================================================================  SEG08a · compare com o bloco (74,85–83,85)
def seg08a(pasta):
    """O mesmo bloco do início, já submerso, em câmera lenta (tempo de cena 3,22→3,65 s em 7 s de tela), com o peso
    e o empuxo em escala: E/P = ρ_água/ρ_aço = 1025/7850 = 0,13. A água que ele desloca é só o próprio volume (cubo
    ciano). Em "Por isso, afunda" o tempo volta ao normal e ele toca o leito."""
    import animatic as A
    def exportador(posicionar, cam, ctx):
        rot = Rotulos(); est = ctx['estado']
        LW = 3.0; LB = LW * 1025.0 / 7850.0
        mw = lib.mat_emissivo('seta_peso_b', COR_PESO, 2.4); me = lib.mat_emissivo('seta_empuxo_b', '#a6f0ff', 2.6)
        aw = bpy.data.objects.new('ancW', None); lib.ligar(aw); aw['anim'] = 1
        ab = bpy.data.objects.new('ancB', None); lib.ligar(ab); ab['anim'] = 1
        lib.seta3d('pesoB', (0, -0.9, 0), (0, 0, -1), LW, r=0.17, mat=mw, cabeca=2.2).parent = aw
        lib.seta3d('empuxoB', (0, -0.9, 0), (0, 0, 1), LB, r=0.17, mat=me, cabeca=2.2).parent = ab
        gh = bpy.data.objects.new('ancAgua', None); lib.ligar(gh); gh['anim'] = 1
        cubo = lib.caixa('agua_desl_bloco', (1.6, 1.6, 1.6), (0, 0, 0), lib.mat_fantasma('desl_bloco', COR_EMPUXO, alfa=0.45, brilho=1.25), bisel=0.05)
        cubo.parent = gh; cubo.visible_shadow = False
        def ts(g): return float(np.interp(g, [74.85, 82.0, 82.12, 90.0], [3.22, 3.65, 3.80, 3.85]))
        estado_p = {}
        def anim(g):
            p = posicionar(ts(g)); estado_p['p'] = p
            vis = 1.0 if g >= 76.2 else 1e-4
            aw.location = p; ab.location = p; aw.scale = ab.scale = (vis, vis, vis)
            kg = suave((g - 77.6) / 1.0); vg = 1.0 if 77.6 <= g <= 82.0 else 1e-4
            gh.location = p + Vector((-1.7 * kg, 0, 0)); gh.scale = (vg, vg, vg); gh.rotation_euler = ctx['bloco'].rotation_euler
            k = suave((g - 74.85) / 9.0)
            camera_em(cam, V(1.3, -8.4, -2.4).lerp(V(1.7, -7.4, -2.9), k), V(2.9, 6.5, -3.2).lerp(V(2.9, 6.5, -3.9), k), 30)
        rot.add('Peso', lambda g: estado_p.get('p', V(0, 0, 0)) + Vector((0, -0.9, -2.0)), 76.4, 83.6, dx=0.07, dy=0.04)
        rot.add('Empuxo', lambda g: estado_p.get('p', V(0, 0, 0)) + Vector((0, -0.9, 0.35)), 76.6, 83.6, dx=0.07, dy=-0.05)
        rot.add('Água deslocada', lambda g: estado_p.get("p", V(0, 0, 0)) + Vector((-1.7, 0, 0.8)), 78.3, 82.0, dx=-0.05, dy=-0.07)
        exportar_seg(pasta, 74.85, 83.85, anim, rot, extra=dict(segmento='08a', ondas=[dict(x=ctx['x_imp'], y=ctx['by'], t0=-50.0)]))
    A.plano1(pasta, exportador=exportador)


# =====================================================================================  SEG08b · bloco maciço × casco (83,85–94,55)
def seg08b(pasta):
    """Lado a lado no mesmo corte: um bloco maciço de aço com a MESMA MASSA do navio vazio (Δ(8,0 m) = 39.657 t →
    5.052 m³ → aresta de 17,2 m) e o casco, cujo interior é ar. Mesmo peso (setas iguais). O bloco desloca só o próprio
    volume: empuxo = 13% do peso → afunda. O casco desloca 38.690 m³: empuxo = peso → flutua."""
    XC, T, raiz, solido, KB = cena_secao()
    rot = Rotulos()
    D = hidro.RHO * hidro.carena(T)[0]; a = (D / 7.85) ** (1 / 3)
    yc = -(navio.MEIA_BOCA + 6.0 + a / 2); xc = XC - a / 2
    cubo = bpy.data.objects.new('cubo_aco', None); lib.ligar(cubo); cubo['anim'] = 1
    lib.caixa('cubo_aco_m', (a, a, a), (0, 0, 0), lib.mat_pintura('aco_macico', '#7b8087', rug=0.35, metal=0.6, variacao=0.05), bisel=0.12).parent = cubo
    mw = lib.mat_emissivo('seta_peso', COR_PESO, 2.0); me = lib.mat_emissivo('seta_empuxo_c', '#a6f0ff', 2.6)
    L = 4.0
    wc = lib.seta3d('peso_cubo', (a / 2 + 0.9, 0, 0), (0, 0, -1), L, r=1.6, mat=mw, cabeca=2.0); wc.parent = cubo
    bc = lib.seta3d('empuxo_cubo', (a / 2 + 0.9, 0, 0), (0, 0, 1), L * 1025 / 7850, r=1.6, mat=me, cabeca=1.2); bc.parent = cubo
    for o in (wc, bc): o.visible_shadow = False
    surge(wc, 84.4, dur=0.5, escala=True); surge(bc, 85.0, dur=0.4, escala=True)
    B, Wn, pB, pG, xs, zB, zG = _setas_forcas(XC, T, KB)
    surge(Wn, 84.4, dur=0.5, escala=True); surge(pG, 84.3, dur=0.3); surge(B, 85.0, dur=0.5, escala=True); surge(pB, 84.9, dur=0.3)
    # ar dentro do casco (porão) destacado na face de corte
    ar = lib.malha('ar_casco', [(XC + 0.09, -12.4, 2.3 - T), (XC + 0.09, 12.4, 2.3 - T), (XC + 0.09, 12.4, navio.PONTAL - 0.8 - T), (XC + 0.09, -12.4, navio.PONTAL - 0.8 - T)],
                   [(0, 1, 2, 3)], lib.mat_fantasma('ar_interno', '#eef9ff', alfa=0.40, brilho=1.3))
    ar.visible_shadow = False; surge(ar, 84.6, dur=0.6)
    _area_deslocada(XC, T, 89.9)
    vol = volume_submerso('vol_deslocado', T, x0=-70.0, x1=XC - 0.05, infla=0.12); vol.parent = raiz; surge(vol, 90.0, dur=0.8)
    def zc(g):
        if g < 85.6: return -a / 2 - 0.4
        return -a / 2 - 0.4 - 1.5 * (g - 85.6) ** 2 - 2.0 * (g - 85.6)
    rot.add('Mesma massa do navio vazio', lambda g: Vector((XC, yc, zc(g) + a / 2)), 83.95, 87.8, dx=0.03, dy=-0.09)
    rot.add('Aço maciço', lambda g: Vector((XC, yc, zc(g))), 84.3, 87.8, dx=0.05, dy=0.08)
    rot.add('Ar', (XC, 4.0, 4.0 - T + 3.0), 84.8, 89.6, dx=0.07, dy=0.09)
    rot.add('Água deslocada', (XC, -8.0, -4.5), 90.2, 94.5, dx=0.06, dy=0.10)
    rot.add('Empuxo = peso', (xs, 0, zB + 3.2), 91.0, 94.5, dx=0.06, dy=0.04)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    K = [(83.85, (XC + 96, -22, 3), (XC - 6, -14, -4), 22), (88.4, (XC + 96, -22, -2), (XC - 6, -14, -8), 22),
         (90.0, (XC + 62, -2, 1), (XC - 4, 0, -1.5), 22), (94.55, (XC + 56, 0, 1), (XC - 4, 0, -1.5), 22)]
    def anim(g):
        s_ = 1.0 if 83.95 <= g <= 89.4 else 1e-4
        k = suave((g - 83.95) / 0.5)
        cubo.location = (xc, yc, zc(g)); cubo.scale = (s_ * max(k, 1e-3),) * 3
        p, a_, l = trilha(K, g); camera_em(cam, p, a_, l)
    exportar_seg(pasta, 83.85, 94.55, anim, rot, extra=dict(segmento='08b', aresta_cubo=a, massa_t=D))


# =====================================================================================  SEG09–11 · porto: carregamento, calado e marcas (94,55–134,00)
YN = -(navio.MEIA_BOCA + 4.5)          # linha de centro do navio atracado (cais em y > −2)
GUINDASTES = [  # (baía, instante de pouso no navio) — cada pouso no momento da fala
    (5, 101.60), (3, 102.95), (7, 104.45)]
LOTES = [105.45, 106.95, 108.45, 110.15, 111.85, 113.55, 115.05]   # cargas do time-lapse (uma baía por vez, em pares)


def carregamento(conts):
    """Instante em que cada contêiner pousa: os 3 levados pelos portêineres e o resto em lotes (time-lapse)."""
    rest = list(conts); t = {}
    especiais = []
    for (k, tl) in GUINDASTES:
        c = min((o for o in rest if o.name.startswith(f'c{k}_')), key=lambda o: (o.location.z, abs(o.location.y)))
        rest.remove(c); t[c.name] = tl; especiais.append((c, k, tl))
    rest.sort(key=lambda o: (int(o.name[1:].split('_')[0]), o.location.z, o.location.y))
    nb = len(LOTES)
    for i, o in enumerate(rest):
        lote = min(nb - 1, i * nb // len(rest)); dentro = (i - lote * len(rest) / nb) / (len(rest) / nb)
        t[o.name] = LOTES[lote] + 0.9 * max(0.0, dentro)
    return t, especiais


def dinamica_calado(tempos, g0=94.0, g1=135.0, dt=1 / 120):
    """Arfagem do navio a cada carga (tempo comprimido): T'' = ω²(T_eq(m) − T) − 2ζωT'. Retorna T(g) e T_eq(g)."""
    ts = np.sort(np.array(list(tempos.values())))
    n_eq = np.arange(len(ts) + 1); Teq_tab = np.array([calado_com(n) for n in range(0, len(ts) + 1, 8)])
    def Teq(n): return float(np.interp(n, np.arange(0, len(ts) + 1, 8), Teq_tab))
    w, z = 2 * math.pi / 1.7, 0.45
    T, v = navio.CALADO_LEVE, 0.0; G_, TT, TE = [], [], []
    g = g0
    while g <= g1:
        n = int(np.searchsorted(ts, g, side='right')); te = Teq(n)
        a = w * w * (te - T) - 2 * z * w * v; v += a * dt; T += v * dt
        G_.append(g); TT.append(T); TE.append(te); g += dt
    G_, TT, TE = np.array(G_), np.array(TT), np.array(TE)
    return (lambda g: float(np.interp(g, G_, TT))), (lambda g: float(np.interp(g, G_, TE)))


def cena_porto(diorama=False):
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=34, sol_rot=240, sol_forca=4.2, nuvens=0.5, horizonte='#f6e6cc', sol_cor=(1.0, 0.9, 0.76))
    raiz, conts, info = navio_completo(navio.CALADO_LEVE)
    raiz.location.y = YN
    tempos, especiais = carregamento(conts)
    Tf, Teq = dinamica_calado(tempos)
    for o in conts:
        if any(o is e[0] for e in especiais): continue
        surge(o, tempos[o.name] - 0.35, dur=0.35, d=(0, 0, 7.0))   # time-lapse: cada contêiner desce até a pilha
    y_corte = YN - navio.MEIA_BOCA - 6.0
    magua = lib.mat_agua('agua5', absorcao=(0.25, 0.62, 0.72), densidade=0.15, marola=0.25, escala_marola=0.3, rug=0.05)
    if diorama:
        lib.bloco_agua('agua', -400, 400, y_corte, -2.0, -30, magua, res=1.5, amp=0.12, so_superficie=False)
        lib.caixa('fundo_porto', (800, 40, 2), (0, (y_corte - 2) / 2, -31), lib.mat_areia('areia_p', causticas=0.0))
    else:
        lib.bloco_agua('agua', -500, 500, -700, -2.0, -30, magua, res=2.5, amp=0.16, so_superficie=False)
        lib.bloco_agua('longe', -3000, 3000, -3000, -700, -30, lib.mat_pintura('mar_longe', '#2c6f8f', rug=0.1, variacao=0.06, escala_var=0.02), res=200, amp=0, so_superficie=True)
    for o in cenario.cais(-500, 500, -2.0, 140.0, topo=3.0, fundo=-30.0): pass
    for x in np.arange(-90, 120, 22.0):
        cenario.cabeco((x, 0.2, 3.0), 1.2); cenario.defensa((x + 11, -2.6, 1.2), r=1.1, rot=0.0)
    ml = lib.mat_pintura('linha', '#e9b545', rug=0.6)
    for y in (12.0, 40.0): lib.caixa('faixa', (1000, 0.3, 0.02), (0, y, 3.01), ml)
    rnd = random.Random(5); matc = lib.mat_conteiner()
    for x0 in (-120, -60, 60, 100):
        for j in range(6):
            for n in range(rnd.randint(1, 4)):
                o = lib.caixa('pilha', navio.CONT, (x0, 46 + j * 2.6, 3.0 + 1.3 + n * 2.62), matc, bisel=0.05); o.color = lib.srgb(rnd.choice(navio.PALETA_CONT))
    mcol = lib.mat_pintura('colina', '#6f8f86', rug=0.9, variacao=0.1)
    for (x, y, r, h) in ((-700, -1400, 260, 70), (-300, -1600, 340, 110), (500, -1500, 300, 80)):
        lib.cilindro('colina', r, h, (x, y, h / 2 - 20), mcol, lados=10, r2=r * 0.35, suave=False)
    # portêineres: carro e spreader animados; cabos refeitos (comprimento variável); contêiner levado do caminhão ao navio
    mcabo = lib.mat_aco('cabo', (60, 60, 64), rug=0.4, escovado=False); AL = 44.0
    gru = []
    for (c, k, tl) in especiais:
        xb = navio.BAIAS[k]
        objs = cenario.guindaste_sts(xb, 8.0, 38.0, altura=AL, alcance=50.0, trolley_y=22.0, z_spreader=6.0)
        carro = bpy.data.objects.new(f'carro_anc{k}', None); lib.ligar(carro); carro['anim'] = 1
        spr = bpy.data.objects.new(f'spreader_anc{k}', None); lib.ligar(spr); spr['anim'] = 1
        for o in objs:
            nm = o.name.split('.')[0]
            if nm == 'cabo': bpy.data.objects.remove(o); continue
            if nm in ('carro', 'cabine', 'cabine_v'): o.location -= Vector((xb, 22.0, 0)); o.parent = carro
            if nm in ('spreader', 'spreader_c'): o.location -= Vector((xb, 22.0, 6.0)); o.parent = spr
        cabos = []
        for dx in (-2.4, 2.4):
            for dy in (-1.0, 1.0):
                cb = lib.tubo(f'cabo_sts{k}', [(0, 0, 0), (0, 0, -1.0)], r=0.05, mat=mcabo); cb['anim'] = 1; cabos.append((cb, dx, dy))
        # caminhão com o contêiner sob o portêiner
        mcam = lib.mat_pintura('caminhao', '#2e3f6b', rug=0.45)
        lib.caixa('cab', (2.6, 2.5, 3.0), (xb + 8.6, 22, 4.8), mcam, bisel=0.25)
        lib.caixa('chassi', (13, 2.4, 0.5), (xb + 1.0, 22, 4.1), lib.mat_pintura('preto', '#1b1c20', rug=0.6), bisel=0.05)
        c['anim'] = 1; Mloc = c.matrix_basis.copy(); c.parent = None
        gru.append(dict(k=k, xb=xb, tl=tl, carro=carro, spr=spr, cabos=cabos, cont=c, Mloc=Mloc))
    return dict(raiz=raiz, conts=conts, tempos=tempos, Tf=Tf, Teq=Teq, gru=gru, AL=AL, info=info, y_corte=y_corte)


def _posicionar_porto(P, g):
    raiz = P['raiz']; T = P['Tf'](g); raiz.location = (0, YN, -T)
    bpy.context.view_layer.update()
    for G in P['gru']:
        xb, tl = G['xb'], G['tl']
        alvo = raiz.matrix_world @ G['Mloc']                       # pouso no navio (local da pilha)
        pa = alvo.translation.copy()
        t_ini = tl - 4.0                                             # ciclo: 4 s do caminhão ao navio (tempo de tela)
        u = (g - t_ini) / 4.0
        ycam, zcam = 22.0, 4.35
        if u <= 0: y, z = ycam, zcam
        elif u < 1:
            # sobe (0–0,3), translada para o mar (0,25–0,7), desce até o pouso (0,65–1)
            ky = suave5((u - 0.25) / 0.45); kz_sobe = suave((u) / 0.3); kz_desce = suave5((u - 0.62) / 0.38)
            y = lerp(ycam, pa.y, ky); zt = 34.0
            z = lerp(zcam, zt, kz_sobe) if u < 0.62 else lerp(zt, pa.z, kz_desce)
        else: y, z = pa.y, pa.z
        c = G['cont']
        if u < 1: c.matrix_world = Matrix.Translation((xb, y, z))
        else: c.matrix_world = alvo
        bpy.context.view_layer.update()
        ytr = c.matrix_world.translation.y if u < 1.6 else lerp(pa.y, 22.0, suave((g - tl - 0.6) / 3.0))
        zsp = c.matrix_world.translation.z + navio.CONT[2] if u < 1.0 else lerp(pa.z + navio.CONT[2], 30.0, suave((g - tl) / 2.5))
        G['carro'].location = (xb, ytr, 0.0); G['spr'].location = (xb, ytr, zsp - 6.0 - 0.95 + 0.95)
        for (cb, dx, dy) in G['cabos']:
            topo = Vector((xb + dx * 0.4, ytr + dy * 0.5, P['AL'] - 1.0)); fim = Vector((xb + dx, ytr + dy, zsp + 1.2 + 0.0))
            d = fim - topo; cb.location = topo; cb.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cb.scale = (1, 1, d.length)


def _setas_carga(P, x0=62.0):
    """Barras de força ao lado do casco (lado do mar): peso total (azul, ↓) e empuxo (amarelo, ↑), ∝ deslocamento."""
    D0 = hidro.RHO * hidro.carena(navio.CALADO_LEVE)[0]; Df = D0 + len(P['conts']) * M_CONT
    me = lib.mat_emissivo('seta_empuxo', '#f3b544', 1.6); mw = lib.mat_emissivo('seta_peso', '#4a63c8', 2.0)
    y0 = YN - navio.MEIA_BOCA - 9.0; L = 15.0
    aB = bpy.data.objects.new('barra_B', None); lib.ligar(aB); aB['anim'] = 1
    aW = bpy.data.objects.new('barra_W', None); lib.ligar(aW); aW['anim'] = 1
    lib.seta3d('empuxo_c', (0, 0, 0), (0, 0, 1), L, r=1.3, mat=me, cabeca=2.2).parent = aB
    lib.seta3d('peso_c', (0, 0, 0), (0, 0, -1), L, r=1.3, mat=mw, cabeca=2.2).parent = aW
    def pos(g, vis):
        T = P['Tf'](g); n = sum(1 for t in P['tempos'].values() if t <= g)
        DB = hidro.RHO * float(np.interp(T, TAB_T, TAB_V)); DW = D0 + n * M_CONT
        kB, kW = DB / Df, DW / Df
        aB.location = (x0, y0, 1.0); aB.scale = (vis, vis, max(1e-3, kB) * vis)
        aW.location = (x0 + 5.0, y0, 1.0 + L * kW); aW.scale = (vis, vis, max(1e-3, kW) * vis)
    return pos


TAB_T = np.linspace(7.0, 12.0, 26); TAB_V = None


def seg09(pasta):
    global TAB_V
    TAB_V = np.array([hidro.carena(t)[0] for t in TAB_T])
    P = cena_porto(); raiz = P['raiz']; rot = Rotulos()
    barras = _setas_carga(P)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    xm = 91.0; bm = lambda z: navio.meia_boca(xm, z)
    yb = YN - bm(8.0)
    xa, xb_, xc = navio.BAIAS[5], navio.BAIAS[3], navio.BAIAS[7]
    K1 = [(94.55, (176, -160, 74), (0, -20, 6), 24), (97.6, (118, -104, 44), (xa + 10, -4, 18), 24), (101.9, (56, -58, 24), (xa + 2, -12, 14), 24)]
    K2 = [(101.9, (xb_ - 34, -66, 30), (xb_, -14, 12), 24), (103.2, (xb_ - 26, -60, 26), (xb_, -14, 11), 24)]
    K3 = [(103.2, (xc + 6, -104, 30), (xc, -16, 13), 24), (104.9, (xc + 4, -96, 27), (xc, -16, 12), 24)]
    # "Observe a linha d'água": a câmera desce do convés até a linha d'água junto às marcas de calado da proa
    K4 = [(104.9, (xm - 14, yb - 26, 20), (xm, yb, 8), 26), (106.3, (xm - 3.5, yb - 5.6, 0.75), (xm + 0.2, yb, 0.15), 34),
          (109.6, (xm - 3.0, yb - 4.8, 0.55), (xm + 0.2, yb, 0.0), 36)]
    K5 = [(109.6, (112, -104, 22), (34, -20, 7), 24), (117.2, (104, -96, 18), (34, -20, 6), 24)]
    def anim(g):
        _posicionar_porto(P, g); barras(g, 1.0 if g >= 109.6 else 1e-4)
        if g < 101.9: p, a, l = trilha(K1, g)
        elif g < 103.2: p, a, l = trilha(K2, g)
        elif g < 104.9: p, a, l = trilha(K3, g)
        elif g < 109.6: p, a, l = trilha(K4, g)
        else: p, a, l = trilha(K5, g)
        camera_em(cam, p, a, l)
    rot.add('Navio vazio', (0, YN, 18 - navio.CALADO_LEVE + 2), 95.0, 97.4, dx=0.06, dy=-0.06)
    rot.add('Linha d\'água', (xm + 0.6, yb, 0.0), 105.4, 109.4, dx=-0.08, dy=0.07)
    rot.add('Peso', (67.0, YN - navio.MEIA_BOCA - 9.0, 13.0), 110.0, 117.2, dx=0.05, dy=-0.04)
    rot.add('Empuxo', (62.0, YN - navio.MEIA_BOCA - 9.0, 8.0), 110.0, 117.2, dx=-0.08, dy=0.04)
    exportar_seg(pasta, 94.55, 117.20, anim, rot, extra=dict(segmento='09', calado_final=P['Tf'](134.0), n_cont=len(P['conts'])))


def seg10(pasta):
    """Calado: diorama cortado na água a meia-nau; cota da quilha até a superfície."""
    P = cena_porto(diorama=True); rot = Rotulos()
    Tfin = P['Tf'](120.0)
    yc = YN - navio.meia_boca(0.0, 6.0) - 2.2
    cota = bpy.data.objects.new('cota', None); lib.ligar(cota); cota['anim'] = 1
    mc = lib.mat_emissivo('cota', '#f3b544', 2.2)
    lib.caixa('cota_haste', (0.35, 0.35, 1.0), (0, 0, 0.5), mc).parent = cota
    for z_, s_ in ((0.0, 1), (1.0, -1)):
        lib.caixa('cota_trava', (2.4, 0.35, 0.25), (0, 0, z_), mc).parent = cota
    q = bpy.data.objects.new('quilha_ref', None); lib.ligar(q)
    lib.tracejado('quilha_linha', (-14, yc, -Tfin), (14, yc, -Tfin), mc, traco=1.0, vao=0.6, r=0.12)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    K = [(117.2, (36, YN - 70, 2.5), (0, yc, -3.5), 26), (123.65, (22, YN - 56, -0.6), (0, yc, -4.5), 26)]
    def anim(g):
        _posicionar_porto(P, g); T = P['Tf'](g)
        k = suave((g - 118.9) / 2.0)
        cota.location = (0, yc, -T); cota.scale = (1, 1, max(1e-3, T * k)) if g >= 118.7 else (1e-4, 1e-4, 1e-4)
        p, a, l = trilha(K, g); camera_em(cam, p, a, l)
    rot.add('Quilha', (0, yc, -Tfin), 119.0, 123.6, dx=0.07, dy=0.05)
    rot.add('Superfície da água', (0, yc, 0.0), 120.6, 123.6, dx=0.07, dy=-0.05)
    rot.add('Calado', (0, yc, -Tfin / 2), 122.55, 123.65, dx=-0.10, dy=0.0)
    exportar_seg(pasta, 117.20, 123.65, anim, rot, extra=dict(segmento='10', calado=Tfin))


def seg11(pasta):
    """Marcas no costado: escala de calado (proa) e marca de linha de carga (meia-nau), em tamanho real."""
    P = cena_porto(); rot = Rotulos(); raiz = P['raiz']
    mh = lib.mat_emissivo('realce', '#f3b544', 2.6)
    # realces: moldura na escala de calado e barras amarelas sobre cada linha de carga, em sequência
    xm = 91.0
    zs = P['info']['linhas']
    def ys(x, z): return -(navio.meia_boca(x, z) + 0.03)
    xv = -4.0 + 0.54; ordem = ['S', 'T', 'W', 'F', 'TF']
    for i, k in enumerate(ordem):
        z = zs[k]; sentido = 1 if k in ('S', 'T', 'W') else -1
        o = lib.caixa('realce_' + k, (0.25, 0.02, 0.035), (xv + sentido * 0.125, ys(-4.0, z) - 0.01, z - 0.0125), mh); o.parent = raiz
        surge(o, 130.5 + 0.55 * i, dur=0.15, t1=133.9, dur1=0.3)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    def pmundo(x, z): return raiz.matrix_world @ Vector((x, ys(x, z), z))
    TL = [130.5 + 0.55 * i for i in range(5)]
    def z_linha(g):    # a câmera acompanha a linha de carga que acende (S → T → W → F → TF)
        return float(np.interp(g, [128.8] + TL, [zs['S']] + [zs[k] for k in ordem]))
    def anim(g):
        _posicionar_porto(P, g)
        P['raiz'].location.z += 0.05 * math.sin(2 * math.pi * g / 6.0)       # navio atracado: arfagem leve com a marola
        bpy.context.view_layer.update()
        if g < 125.8:      # do nível da água, ao longo do costado, até a proa
            k = suave((g - 123.65) / 2.15); alvo = pmundo(xm, 8.4)
            pos = Vector((40, YN - 30, 1.2)).lerp(alvo + Vector((-5.0, -6.5, 0.4)), k); a = Vector((60, YN - 14, 2)).lerp(alvo, k); l = lerp(26, 32, k)
        elif g < 127.6:    # "algumas indicam o calado": sobe pela escala até a linha d'água
            k = suave((g - 125.8) / 1.8); zl = lerp(8.4, 10.2, k); alvo = pmundo(xm, zl)
            pos = alvo + Vector((-5.0 + 1.2 * k, -6.5 + 2.0 * k, 0.4)); a = alvo; l = lerp(32, 34, k)
        elif g < 128.8:    # "outras…": desliza rente ao costado até a meia-nau
            k = suave5((g - 127.6) / 1.2); x = lerp(xm - 3.8, -5.9, k); zl = lerp(10.2, zs['S'] + 0.05, k)
            alvo = pmundo(x + 3.0 - 0.95 * k * 3.0 + 0.0, zl); alvo.x = lerp(xm, -3.85, k) + 0.2 * k
            pos = pmundo(x, zl) + Vector((0, -4.5 + 0.5 * k, 0.4 - 0.1 * k)); a = alvo; l = 34
        else:              # marca de linha de carga: aproxima e acompanha cada linha que acende
            k = suave((g - 128.8) / 5.2); alvo = pmundo(-3.65, z_linha(g))
            pos = alvo + Vector((-1.7, -5.0, 0.3)).lerp(Vector((-1.1, -3.6, 0.15)), k); a = alvo; l = 32
        pos.z = max(pos.z, 0.55)                                              # nunca abaixo da superfície (cena sem corte)
        camera_em(cam, pos, a, l)
    rot.add('Marcas de calado', lambda g: pmundo(xm, 10.6), 125.9, 127.9, dx=0.07, dy=-0.06)
    rot.add('Marca de linha de carga', lambda g: pmundo(-4.0, zs['S'] + 0.15), 128.3, 133.9, dx=0.05, dy=-0.10)
    exportar_seg(pasta, 123.65, 134.00, anim, rot, extra=dict(segmento='11'))


# =====================================================================================  SEG12 · avaria e compartimentos (134,00–154,60)
ANTEPARAS = [-71.0, -44.4, -17.2, 10.0, 37.2, 64.4, 84.0]
COMP_AVARIA = (10.0, 37.2)


def meia_casca(nome, mat, recuo=0.0, z_base=None, n=150, nz=26):
    """Costado + fundo SÓ do bordo y ≥ 0 (corte longitudinal no plano y = 0), opcionalmente recuado para dentro."""
    xs = np.linspace(navio.POPA + 0.2, navio.PROA - 0.2, n); vs, fs, secs = [], [], []
    for x in xs:
        k = navio.quilha(x) + (0.0 if callable(recuo) else recuo); zb = max(k, z_base) if z_base is not None else k
        if navio.PONTAL - zb < 0.5: secs.append(None); continue
        zs = np.linspace(zb, navio.PONTAL, nz)
        pts = [(x, 0.0, zb)] + [(x, max(navio.meia_boca(x, z) - (recuo(z) if callable(recuo) else recuo), 0.05), z) for z in zs]
        secs.append(len(vs)); vs += pts
    m = nz + 1; val = [i for i in secs if i is not None]
    for a, b in zip(val, val[1:]):
        for j in range(m - 1): fs.append((a + j, a + j + 1, b + j + 1, b + j))
    return lib.malha(nome, vs, fs, mat, suave=True, angulo=50)


def faixa_corte(nome, mat, z0f, z1f, n=160):
    """Faixa no plano y = 0 entre duas curvas z0f(x) e z1f(x) (face cortada do duplo fundo / convés)."""
    xs = np.linspace(navio.POPA + 0.3, navio.PROA - 0.6, n); vs, fs = [], []
    for x in xs: vs += [(x, -0.03, z0f(x)), (x, -0.03, z1f(x))]
    for i in range(n - 1): fs.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    return lib.malha(nome, vs, fs, mat)


def antepara(nome, x, mat, z0=2.2, z1=None, recuo=0.4):
    z1 = z1 or navio.PONTAL; zs = np.linspace(z0, z1, 20)
    pts = [(x, 0.0, z0)] + [(x, max(navio.meia_boca(x, z) - recuo, 0.05), z) for z in zs] + [(x, 0.0, z1)]
    return lib.malha(nome, pts, [tuple(range(len(pts)))], mat)


def seg12(pasta):
    """Avaria (corte longitudinal ilustrativo). Hipóteses: hidro.py (duplo fundo 2,2 m e tanques laterais até z = 6 m
    estanques; rombo no costado simples acima dos tanques e abaixo da linha d'água; porão vazio μ = 0,95; método da
    perda de flutuabilidade). Resultado: +1,27 m a meia-nau, trim 0,71° pela proa, GM 1,50 → 0,74 m (positivo)."""
    lib.nova_cena()
    lib.ceu_estilizado(**CEU_DIA)
    T0 = calado_com(398)
    R = hidro.estabilidade_avaria(T0, COMP_AVARIA); T1, th1 = R['T1'], math.radians(R['trim_graus'])
    raiz = bpy.data.objects.new('navio', None); lib.ligar(raiz); raiz['anim'] = 1
    mh = navio.mat_casco(); mi = lib.mat_pintura('interno', '#9a9d97', rug=0.6, metal=0.15)
    mcorte = lib.mat_pintura('corte', '#f3b544', rug=0.5); mant = lib.mat_pintura('antepara', navio.COR['primer_verm'], rug=0.6, metal=0.15)
    mtq = lib.mat_pintura('tanque', '#7f8a8f', rug=0.6, metal=0.15)
    rec = lambda z: hidro.L_TANQUE if z < hidro.Z_TANQUE else hidro.CASCO
    partes = [meia_casca('casco_meio', mh), meia_casca('casco_int', mi, recuo=rec, z_base=2.2)]
    partes.append(faixa_corte('corte_fundo', mcorte, lambda x: navio.quilha(x), lambda x: navio.quilha(x) + 2.2))
    partes.append(faixa_corte('corte_conves', mcorte, lambda x: navio.PONTAL - 0.35, lambda x: navio.PONTAL + 0.05))
    # teto dos tanques laterais (degrau a z = 6 m) e fundo interno
    vs, fs = [], []
    for x in np.arange(-60, 84, 2.0):
        b = navio.meia_boca(x, hidro.Z_TANQUE)
        if b < 3: continue
        vs += [(x, b - hidro.L_TANQUE, hidro.Z_TANQUE), (x, b - hidro.CASCO, hidro.Z_TANQUE)]
    for j in range(len(vs) // 2 - 1): fs.append((2 * j, 2 * j + 2, 2 * j + 3, 2 * j + 1))
    partes.append(lib.malha('teto_tanque', vs, fs, mtq))
    vs, fs = [], []
    for x in np.arange(navio.POPA + 6, 92, 2.0):
        b = navio.meia_boca(x, 2.4) - hidro.L_TANQUE
        if b < 0.3: continue
        vs += [(x, 0.0, navio.quilha(x) + 2.2), (x, b, navio.quilha(x) + 2.2)]
    for j in range(len(vs) // 2 - 1): fs.append((2 * j, 2 * j + 2, 2 * j + 3, 2 * j + 1))
    partes.append(lib.malha('fundo_int', vs, fs, mi))
    vs, fs = [], []
    for x in np.arange(navio.POPA + 0.5, 103.5, 1.0):
        b = navio.meia_boca(x, navio.PONTAL)
        if b < 0.2: continue
        vs += [(x, 0.0, navio.PONTAL + 0.02), (x, b - 0.05, navio.PONTAL + 0.02)]
    for j in range(len(vs) // 2 - 1): fs.append((2 * j, 2 * j + 2, 2 * j + 3, 2 * j + 1))
    partes.append(lib.malha('conves_meio', vs, fs, lib.mat_pintura('conves', navio.COR['conves'], rug=0.7)))
    for x in ANTEPARAS: partes.append(antepara('antepara', x, mant))
    sup = navio.superestrutura() + navio.leme_e_helice()
    bpy.context.view_layer.update()
    for o in sup:
        dy = o.dimensions.y
        if abs(o.location.y) < 0.5 and o.name.split('.')[0] not in ('leme', 'cubo') and not o.name.startswith('pa'):
            o.scale.y *= 0.5; o.location.y += dy / 4
    partes += sup
    partes += navio.carga(4, semente=3, filtro=lambda k, j, n: j > 5)
    # linha d'água ANTES da avaria, pintada no navio (acompanha o afundamento e o trim) — referência visual
    mref = lib.mat_emissivo('linha_antes', '#f3b544', 2.4)
    partes += lib.tracejado('linha_antes', (-98, -0.35, T0), (100, -0.35, T0), mref, traco=2.0, vao=1.2, r=0.20) or []
    # oclusor: sólido do meio casco (impede a água de aparecer dentro do casco cortado)
    xs = np.linspace(navio.POPA + 0.2, navio.PROA - 0.2, 90); vs, fs = [], []; secs = []
    for x in xs:
        k = navio.quilha(x)
        if navio.PONTAL - k < 0.5: continue
        zs = np.linspace(k, navio.PONTAL, 16)
        anel = [(x, -0.05, k)] + [(x, navio.meia_boca(x, z) + 0.02, z) for z in zs] + [(x, -0.05, navio.PONTAL)]
        secs.append(len(vs)); vs += anel
    m = len(zs) + 2
    for a_, b_ in zip(secs, secs[1:]):
        for j in range(m): fs.append((a_ + j, a_ + (j + 1) % m, b_ + (j + 1) % m, b_ + j))
    fs.append(tuple(range(secs[0], secs[0] + m))[::-1]); fs.append(tuple(range(secs[-1], secs[-1] + m)))
    partes.append(oclusor(lib.malha('oclusor_casco', vs, fs, lib.mat_pintura('oc', '#000000'))))
    for o in partes:
        if o.parent is None: o.parent = raiz
    ca, cb = COMP_AVARIA; xcm = 0.5 * (ca + cb)
    # água no porão: parte baixa (entre os tanques laterais) e parte alta (até o costado simples); superfície
    # sempre horizontal no mundo (contra-rotação do trim); sobe até o nível do mar lá fora
    malag = lib.mat_fantasma('alagado', '#2a8fd6', alfa=0.62, brilho=1.15)
    blo = navio.meia_boca(xcm, 4.0) - hidro.L_TANQUE; bhi = navio.meia_boca(xcm, 8.0) - hidro.CASCO
    ag_lo = bpy.data.objects.new('agua_lo', None); lib.ligar(ag_lo); ag_lo['anim'] = 1; ag_lo.parent = raiz
    ag_hi = bpy.data.objects.new('agua_hi', None); lib.ligar(ag_hi); ag_hi['anim'] = 1; ag_hi.parent = raiz
    lib.caixa('agua_lo_m', (cb - ca - 0.8, blo - 0.1, 1.0), (0, (blo + 0.1) / 2, 0.5), malag).parent = ag_lo
    lib.caixa('agua_hi_m', (cb - ca - 0.8, bhi - 0.1, 1.0), (0, (bhi + 0.1) / 2, 0.5), malag).parent = ag_hi
    z_rombo = 7.4; ybr = navio.meia_boca(xcm + 4, z_rombo) - hidro.CASCO - 0.02
    rasgo = lib.caixa('rasgo', (3.0, 0.3, 1.0), (xcm + 4.0, ybr, z_rombo), lib.mat_pintura('rasgo', '#0b0d12', rug=0.9)); rasgo.parent = raiz
    jato = lib.malha('jato', [(xcm + 2.7, ybr - 0.2, z_rombo + 0.3), (xcm + 5.3, ybr - 0.2, z_rombo + 0.3), (xcm + 4.9, ybr - 5.5, 2.4), (xcm + 3.1, ybr - 5.5, 2.4)],
                     [(0, 1, 2, 3)], lib.mat_fantasma('jato', '#dff6ff', alfa=0.6, brilho=1.4)); jato.parent = raiz
    surge(rasgo, 136.6, dur=0.2); surge(jato, 136.9, dur=0.3, t1=145.6, dur1=0.8)
    # hipótese grave: SEM divisórias a água avançaria porão a porão (vermelho), depois volta ao caso real
    mred = lib.mat_fantasma('hipotese', '#e2483a', alfa=0.45, brilho=1.1)
    vizinhos = sorted([(a_, b_) for (a_, b_) in zip(ANTEPARAS, ANTEPARAS[1:]) if (a_, b_) != COMP_AVARIA], key=lambda c: abs(0.5 * (c[0] + c[1]) - xcm))
    for i, (a_, b_) in enumerate(vizinhos):
        xm = 0.5 * (a_ + b_); bb = navio.meia_boca(xm, 8.0) - hidro.CASCO
        hh = min(T1 + 2.0, navio.PONTAL - 0.5) - 2.2
        o = lib.caixa('hip', (b_ - a_ - 0.8, bb - 0.1, hh), (xm, (bb + 0.1) / 2, 2.2 + hh / 2), mred); o.parent = raiz
        surge(o, 147.9 + 0.45 * i, dur=0.4, t1=150.6, dur1=0.5)
    mam = lib.mat_fantasma('destaque_ant', '#f3b544', alfa=0.75, brilho=1.5)
    for x in COMP_AVARIA:
        o = antepara('antepara_dest', x + 0.08, mam, z0=2.2, recuo=0.5); o.parent = raiz; surge(o, 151.05, dur=0.4)
    # mar em diorama (corte no plano y = 0) + nível do mar tracejado
    magua = lib.mat_agua('agua_av', espalha=0.0, rug=0.05, **AGUA_MAR)
    lib.bloco_agua('agua', -420, 420, 0.0, 420, -220, magua, res=2.5, amp=0.2)
    mlonge = lib.mat_pintura('mar_longe', '#2c78a0', rug=0.1, variacao=0.06, escala_var=0.02)
    for (a0, a1, b0, b1) in ((-3000, -420, 0, 3000), (420, 3000, 0, 3000), (-420, 420, 420, 3000)):
        lib.bloco_agua('longe', a0, a1, b0, b1, -30, mlonge, res=300, amp=0.0, so_superficie=True)
    lib.tracejado('nivel_fora', (-112, -0.6, 0.02), (114, -0.6, 0.02), lib.mat_emissivo('nivel', '#dff6ff', 2.2), traco=2.2, vao=1.4, r=0.22)
    def estado(g):
        f = suave((g - 137.2) / 8.6)
        return f, T0 + (T1 - T0) * f, th1 * f
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    def anim(g):
        f, T, th = estado(g)
        raiz.location = (0, 0, -T); raiz.rotation_euler = (0, th, 0)
        nivel_loc = T + xcm * math.tan(th)                         # nível do mar na posição do porão (coord. do navio)
        lv = 2.2 + (nivel_loc - 2.2) * suave((g - 137.0) / 7.6) if g >= 137.0 else 2.2
        for anc, z0, z1 in ((ag_lo, 2.2, hidro.Z_TANQUE), (ag_hi, hidro.Z_TANQUE, navio.PONTAL)):
            h = max(0.0, min(lv, z1) - z0)
            anc.location = (xcm, 0, z0); anc.rotation_euler = (0, -th, 0); anc.scale = (1, 1, h) if h > 0.01 else (1e-4, 1e-4, 1e-4)
        K = [(134.0, (0, -330, 22), (4, 40, -1), 28), (137.0, (26, -150, 6), (22, 30, -1), 32), (141.5, (24, -128, 3), (23, 30, -1), 32),
             (145.5, (4, -300, 5), (4, 40, -1.5), 28), (149.0, (4, -300, 5), (4, 40, -1.5), 28), (151.0, (24, -150, 4), (23, 30, -1), 32),
             (154.6, (24, -136, 3), (23, 30, -1), 32)]
        p, a, l = trilha(K, g); camera_em(cam, p, a, l)
    rot = Rotulos()
    rot.add('Corte ilustrativo', (-60, 0, 22 - T0), 134.4, 139.6, dx=0.05, dy=-0.06)
    rot.add('Duplo fundo (estanque)', lambda g: raiz.matrix_world @ Vector((-30, 0, 1.1)), 134.8, 139.4, dx=0.05, dy=0.08)
    rot.add('Avaria', lambda g: raiz.matrix_world @ Vector((xcm + 4.0, ybr, z_rombo)), 136.8, 140.5, dx=0.06, dy=-0.07)
    rot.add('Tanque lateral (estanque)', lambda g: raiz.matrix_world @ Vector((xcm - 8, navio.meia_boca(xcm - 8, 6.0) - 1.2, 6.0)), 139.7, 143.6, dx=-0.05, dy=0.08)
    rot.add('Linha d\'água antes', lambda g: raiz.matrix_world @ Vector((-30, -0.35, T0)), 143.4, 145.6, dx=0.04, dy=0.07)
    rot.add('Nível do mar', (30, -0.6, 0.02), 143.4, 145.6, dx=0.04, dy=-0.07)
    dproa = R['proa'] - T0; dpopa = R['popa'] - T0
    rot.add(f'Proa: +{dproa:.1f} m'.replace('.', ','), lambda g: raiz.matrix_world @ Vector((96, -0.35, T0)), 145.7, 147.8, dx=-0.08, dy=0.09)
    rot.add(f'Popa: +{dpopa:.1f} m'.replace('.', ','), lambda g: raiz.matrix_world @ Vector((-92, -0.35, T0)), 145.7, 147.8, dx=0.05, dy=0.09)
    rot.add('Hipótese: sem divisórias', (-40, 0, -4), 148.0, 150.6, dx=0.04, dy=0.10)
    rot.add('Divisórias estanques', lambda g: raiz.matrix_world @ Vector((COMP_AVARIA[1], 0, 12.0)), 151.2, 154.6, dx=0.05, dy=-0.07)
    exportar_seg(pasta, 134.00, 154.60, anim, rot, extra=dict(segmento='12', hidrostatica=R, compartimento=COMP_AVARIA))
    print('AVARIA', json.dumps({k: round(v, 3) for k, v in R.items()}))


# =====================================================================================  SEG13 · conclusão (154,60–166,30)
def seg13(pasta):
    """Mar aberto em diorama (corte na água a 8 m do costado): navio carregado; o volume de água deslocado aparece sob o
    casco e as forças peso e empuxo, iguais e opostas, fecham a explicação."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=18, sol_rot=300, sol_forca=4.0, nuvens=0.5, zenite='#3570c4', meio='#8cbbe6', horizonte='#f7cf9a', sol_cor=(1.0, 0.82, 0.62))
    raiz, conts, _ = navio_completo(0.0)
    T = calado_com(len(conts)); raiz.location.z = -T
    Y0 = -navio.MEIA_BOCA - 8.0
    magua = lib.mat_agua('agua_fim', espalha=0.0, rug=0.05, **dict(AGUA_MAR, densidade=0.03))
    lib.bloco_agua('agua', -600, 600, Y0, 600, -80, magua, res=3.0, amp=0.2)
    mlonge = lib.mat_pintura('mar_longe', '#2c78a0', rug=0.1, variacao=0.06, escala_var=0.02)
    for (a0, a1, b0, b1) in ((-4000, -600, -4000, 4000), (600, 4000, -4000, 4000), (-600, 600, 600, 4000)):
        lib.bloco_agua('longe', a0, a1, b0, b1, -30, mlonge, res=400, amp=0.0, so_superficie=True)
    vol = volume_submerso('vol_desl_fim', T, infla=0.18); vol.parent = raiz; surge(vol, 159.6, dur=1.0)
    me = lib.mat_emissivo('seta_empuxo', '#a6f0ff', 2.6); mw = lib.mat_emissivo('seta_peso', COR_PESO, 2.0)
    _, _, KB = hidro.carena(T)
    yb = -navio.MEIA_BOCA - 3.5
    B = lib.seta3d('empuxo_f', (0, yb, KB - T), (0, 0, 1), 9.0, r=1.8, mat=me, cabeca=2.2)
    W = lib.seta3d('peso_f', (8, yb, 12.5 - T + 9.0), (0, 0, -1), 9.0, r=1.8, mat=mw, cabeca=2.2)
    for o, t0 in ((B, 161.4), (W, 161.4)): o.visible_shadow = False; surge(o, t0, dur=0.7, escala=True)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    rot = Rotulos()
    rot.add('Água deslocada', (-30, -navio.MEIA_BOCA, -T * 0.55), 160.2, 166.0, dx=0.05, dy=0.08)
    rot.add('Empuxo', (0, yb, KB - T + 7.5), 161.8, 166.0, dx=-0.10, dy=0.02)
    rot.add('Peso', (8, yb, 12.5 - T + 4.0), 161.8, 166.0, dx=0.06, dy=-0.02)
    K = [(154.6, (150, -118, 7.0), (10, 0, 3), 26), (158.7, (112, -96, 3.0), (2, 0, 0), 25), (162.0, (70, -82, 0.6), (0, 0, -2.5), 24),
         (166.3, (58, -76, 0.4), (0, 0, -3.0), 24)]
    def anim(g):
        raiz.location.z = -T + 0.08 * math.sin(2 * math.pi * g / 9.0)
        p, a, l = trilha(K, g); camera_em(cam, p, a, l)
    exportar_seg(pasta, 154.60, 166.30, anim, rot, extra=dict(segmento='13', calado=T))


SEGMENTOS = {'12': seg12, '13': seg13, '09': seg09, '10': seg10, '11': seg11, '02': seg02, '03': seg03, '04': seg04, '05': seg05, '0607': seg0607, '08a': seg08a, '08b': seg08b}

if __name__ == '__main__':
    SEGMENTOS[sys.argv[1]](sys.argv[2])
