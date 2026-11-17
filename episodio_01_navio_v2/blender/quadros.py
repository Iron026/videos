"""Quadros de referência da Etapa B. Uso:
  python3 quadros.py <n> [pct=100] [amostras=128] [saida.png]
Requer o módulo bpy (Blender 5.1) no PYTHONPATH.
"""
import sys, os, math, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector
import lib, navio, cenario


def grade(nome, x0, x1, y0, y1, fz, mat, res=0.5, fundo=None, suave=True):
    """Terreno por função de altura; fecha as laterais até 'fundo' (para cortes de diorama)."""
    nx = int((x1 - x0) / res) + 1; ny = int((y1 - y0) / res) + 1
    xs = np.linspace(x0, x1, nx); ys = np.linspace(y0, y1, ny)
    X, Y = np.meshgrid(xs, ys, indexing='ij'); Z = fz(X, Y)
    v = [(X[i, j], Y[i, j], Z[i, j]) for i in range(nx) for j in range(ny)]
    idx = lambda i, j: i * ny + j
    f = [(idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)) for i in range(nx - 1) for j in range(ny - 1)]
    if fundo is not None:
        borda = [idx(i, 0) for i in range(nx)] + [idx(nx - 1, j) for j in range(1, ny)] + \
                [idx(i, ny - 1) for i in range(nx - 2, -1, -1)] + [idx(0, j) for j in range(ny - 2, 0, -1)]
        b0 = len(v)
        for k in borda: v.append((v[k][0], v[k][1], fundo))
        n = len(borda)
        for a in range(n): f.append((borda[(a + 1) % n], borda[a], b0 + a, b0 + (a + 1) % n))
        f.append(tuple(b0 + a for a in range(n)))
    return lib.malha(nome, v, f, mat, suave=suave, angulo=60)


# =====================================================================================
def quadro1():
    """Bloco de aço afundando junto ao cais do estaleiro (corte meio acima/meio abaixo d'água)."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=38, sol_rot=150, sol_forca=3.8, nuvens=0.45)
    bx, by = 1.2, 6.5
    def aneis(X, Y):
        r = np.hypot(X - bx, Y - by)
        return 0.16 * np.sin(r * 2.3) * np.exp(-r / 3.2) * (1 - np.exp(-r * 1.5))
    magua = lib.mat_agua('agua1', absorcao=(0.30, 0.74, 0.76), densidade=0.06, espalha=0.008, cor_esp=(0.55, 0.85, 0.9), marola=0.35, escala_marola=0.9)
    lib.bloco_agua('agua', -16, 5.0, 0, 120, -9.0, magua, res=0.35, amp=0.12, escala=0.35, extra=aneis)
    lib.bloco_agua('mar_longe', -400, 5.0, 120, 900, -9.0, magua, res=6.0, amp=0.3, so_superficie=True)
    # leito marinho (corte de areia com estratos)
    def leito(X, Y):
        return -6.8 + 0.35 * np.sin(X * 0.45) * np.cos(Y * 0.3) + 0.18 * np.sin(X * 1.3 + Y * 0.7) + 0.0 * Y
    ma = lib.mat_areia('areia1', causticas=0.22)
    grade('leito', -16, 5.0, -0.03, 120, leito, ma, res=0.4, fundo=-12)
    lib.caixa('estrato', (23.0, 0.02, 0.18), (-4.5, -0.05, -8.4), lib.mat_pintura('estrato', '#9a7f58', rug=0.95))
    lib.caixa('estrato2', (23.0, 0.02, 0.12), (-4.5, -0.05, -10.1), lib.mat_pintura('estrato2', '#8a6f4c', rug=0.95))
    mr = lib.mat_pintura('rocha', '#6d7275', rug=0.85, variacao=0.15)
    rnd = random.Random(4)
    for i in range(16):
        x = rnd.uniform(-15, 4); y = rnd.uniform(1.0, 30)
        lib.rocha('rocha', (x, y, leito(np.array(x), np.array(y)) + 0.05), rnd.uniform(0.25, 0.8), mr, semente=i)
    # conchas e seixos pequenos (sem 'algas-palito')
    mcon = lib.mat_pintura('concha', '#e8dcc4', rug=0.5, variacao=0.1)
    for i in range(40):
        x = rnd.uniform(-8, 4); y = rnd.uniform(0.8, 12)
        lib.rocha('seixo', (x, y, float(leito(np.array(x), np.array(y))) + 0.02), rnd.uniform(0.06, 0.16), mcon if i % 3 == 0 else mr, semente=100 + i, achatar=0.45)
    # muralha do cais (à direita) e terreno do estaleiro ao fundo
    mc = lib.mat_concreto('concreto_cais', (156, 151, 140))
    lib.caixa('cais', (9.0, 120.0, 14.2), (9.5, 60.0, -4.9), mc, bisel=0.05)
    lib.caixa('cais_cap', (1.2, 120.0, 0.45), (5.55, 60.0, 2.35), lib.mat_concreto('cap', (182, 178, 166), escala=0.6), bisel=0.06)
    mj = lib.mat_pintura('junta', '#77746c', rug=0.9)
    for z in np.arange(1.0, -9, -1.5): lib.caixa('junta', (0.06, 120, 0.07), (4.99, 60, z), mj)
    # crustas/limo na zona de variação da maré
    lib.caixa('limo', (0.04, 120, 1.1), (4.985, 60, -0.35), lib.mat_pintura('limo', '#3c5a45', rug=0.9, variacao=0.25))
    for y in (3.0, 15.0):
        cenario.defensa((4.6, y, 0.6), r=0.6, rot=math.pi / 2)
        lib.tubo('corrente', [(4.95, y, 2.4), (4.7, y, 1.2)], r=0.04, mat=lib.mat_aco('corr', (70, 70, 72)))
    for o in cenario.cabeco((7.0, 6.0, 2.6), 1.0): pass
    cenario.pilha_chapas((9.5, 13.0, 2.6), n=7, tam=(6.0, 2.2, 0.12), rot=math.radians(80), semente=2)
    lib.caixa('bloco_resto', (1.6, 1.6, 1.6), (8.8, 4.5, 3.4), lib.mat_aco('aco_bloco', (170, 172, 176), rug=0.2), bisel=0.08, seg=3, rot=(0, 0, 0.3))
    # estaleiro ao fundo (fora de foco)
    mg = lib.mat_concreto('chao', (150, 146, 136), escala=0.05)
    lib.caixa('terreno', (900, 700, 2), (0, 470, 1.2), mg)
    lib.caixa('muralha_fundo', (900, 2, 12), (0, 120.5, -3.5), mc)
    cenario.guindaste_portico(-28, 70, 52, y_c=230, gancho=(0, 222, 34))
    for i, (x, y, w) in enumerate([(60, 320, 60), (-120, 360, 80), (140, 300, 50)]):
        cenario.galpao((x, y, 2.2), (w, 36, 18), cor=['#c9ccc8', '#b8c4cc', '#d8d2c4'][i])
    # o bloco de aço afundando
    maco = lib.mat_aco('aco_bloco', (170, 172, 176), rug=0.2)
    lib.raios_luz(9, -9, 4, 2, 30, 0.2, 9.0, 1.4, inclinacao=(0.32, 0.12), semente=5)
    bloco = lib.caixa('bloco', (1.6, 1.6, 1.6), (bx, by, -3.7), maco, bisel=0.08, seg=3, rot=(0.22, 0.35, 0.5))
    lib.bolhas('bolhas', (bx + 0.2, by, -2.9), 0.28, 2.9, 70, lib.mat_bolha(), semente=3, tam=(0.03, 0.11))
    lib.bolhas('bolhas2', (bx, by, -3.2), 0.12, 0.8, 25, lib.mat_bolha(), semente=8, tam=(0.02, 0.06))
    # câmera: nível d'água, olhando o corte
    lib.camera((0.6, -16.5, -0.6), (0.9, 6.0, -1.25), lente=40, foco=(bx, by, -3.7), fstop=5.6)
    return 'quadro1'


# =====================================================================================
def andaime(x0, x1, y, z1, mat, mplat, passo=2.5, nivel=2.0):
    objs = []
    x = x0
    while x <= x1 + 1e-6:
        for dy in (0, 1.2):
            objs.append(lib.tubo('and_v', [(x, y + dy, 0), (x, y + dy, z1)], r=0.05, mat=mat))
        x += passo
    z = nivel
    while z <= z1 + 1e-6:
        for dy in (0, 1.2):
            objs.append(lib.tubo('and_h', [(x0, y + dy, z), (x1, y + dy, z)], r=0.045, mat=mat))
        objs.append(lib.caixa('and_p', (x1 - x0, 1.2, 0.08), ((x0 + x1) / 2, y + 0.6, z - 0.05), mplat))
        z += nivel
    return objs


def quadro2():
    """Estaleiro (v3): navio em construção por blocos, já reconhecível; o pórtico iça o painel que falta."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=30, sol_rot=70, sol_forca=4.4, nuvens=0.5, zenite='#3a7bd0', meio='#8cc2ee', horizonte='#f7dcb4', sol_cor=(1.0, 0.88, 0.70))
    mg = lib.mat_concreto('chao', (162, 158, 148), escala=0.04)
    lib.caixa('chao', (1400, 860, 2), (0, 270, -1.0), mg)
    ml = lib.mat_pintura('linha', '#e9b545', rug=0.6)
    for y in (-30, 30): lib.caixa('faixa', (320, 0.45, 0.02), (0, y, 0.01), ml)
    mz = lib.mat_pintura('zona', '#5d7f9c', rug=0.8)
    lib.caixa('zona_pintada', (60, 24, 0.02), (95, 46, 0.01), mz)
    lib.bloco_agua('mar', -900, 900, -1200, -158, -20, lib.mat_pintura('mar_longe', '#2c78a0', rug=0.12, variacao=0.08, escala_var=0.02), res=20, amp=0.0, so_superficie=True)
    for o in bpy.data.objects:
        if o.name.startswith('mar'): o.location.z = -1.2
    lib.caixa('borda_cais', (1800, 4, 6), (0, -158, -3.0), lib.mat_concreto('concreto_cais', (156, 151, 140)))
    Z0 = 1.6
    mm = lib.mat_pintura('picadeiro', '#6a4f35', rug=0.9); mbl = lib.mat_concreto('picad_conc', (140, 136, 128))
    for x in np.arange(-92, 96, 7.0):
        k = navio.quilha(x)
        lib.caixa('picad', (1.4, 2.2, Z0 + k - 0.3), (x, 0, (Z0 + k - 0.3) / 2), mbl, bisel=0.05)
        lib.caixa('picad_m', (1.6, 2.4, 0.3), (x, 0, Z0 + k - 0.15), mm, bisel=0.03)
        if -40 < x < 70:
            for s_ in (-1, 1): lib.caixa('picad_l', (1.2, 1.6, Z0 - 0.3), (x, s_ * 9.0, (Z0 - 0.3) / 2), mbl, bisel=0.05)
    raiz = bpy.data.objects.new('navio', None); lib.ligar(raiz)
    objs, faltantes = navio.construcao_em_blocos(semente=4, faltam={(1, 13, 2), (1, 13, 3)}, vao_cinta=(69.5, 78.5),
                                                    forcar={(1, 12, 2), (1, 12, 3), (1, 14, 2), (1, 14, 3)})   # vizinhos chapeados: o vão fica legível
    for o in objs:
        if o.parent is None: o.parent = raiz
    raiz.location = (0, 0, Z0)
    # andaimes ao longo do costado (bombordo)
    mand = lib.mat_aco('andaime', (150, 152, 156), rug=0.4, escovado=False); mplat = lib.mat_pintura('plataforma', '#8a6a44', rug=0.9)
    for (x0, x1) in ((-74, -50), (-28, -4), (18, 40)):
        b = navio.meia_boca((x0 + x1) / 2, 12)
        andaime(x0, x1, b + 1.2, 19.5, mand, mplat)
    # pórtico sobre a proa içando o painel de costado que falta (bombordo, x 70–78, z 7,5–18).
    # Ligação física: olhais soldados na borda superior do painel, lingas do gancho até os olhais,
    # gancho exatamente na vertical do centro de massa da peça (estática de corpo suspenso).
    hg = 46.0
    zlev = 13.0; ydes = 8.0
    pv = bpy.data.objects.new('painel_icado', None); lib.ligar(pv)
    mazul = lib.mat_pintura('primer_azul', '#4f6f8f', rug=0.55, metal=0.15, variacao=0.08)
    pn = navio.painel_costado('painel_icado_m', 70.0, 78.0, 7.5, navio.PONTAL, 1, mazul, folga=0.04)
    pn.parent = pv
    ma = lib.mat_aco('aco_estrut', (120, 122, 126), rug=0.4, escovado=False)
    for xx in (71.5, 74.0, 76.5):
        pts = [(xx, navio.meia_boca(xx, z) - 0.35, z) for z in np.linspace(7.7, 17.6, 9)]
        lib.tubo('reforco', pts, r=0.22, mat=ma).parent = pv
    pv.location = (0, ydes, Z0 + zlev)
    # centro de massa da chapa (média sobre a superfície) e posição dos olhais (mundo)
    amostras = [(x, navio.meia_boca(x, z) + 0.03 - 0.07 + ydes, Z0 + zlev + z) for x in np.linspace(70.2, 77.8, 12) for z in np.linspace(7.6, 17.9, 14)]
    cg = Vector(np.mean(np.array(amostras), axis=0))
    ztopo = Z0 + zlev + navio.PONTAL - 0.04
    olhais = [Vector((xx, navio.meia_boca(xx, navio.PONTAL - 0.04) + 0.03 - 0.07 + ydes, ztopo + 0.35)) for xx in (71.2, 76.8)]
    mol = lib.mat_pintura('olhal', '#f3b544', rug=0.4, metal=0.3)
    for o_ in olhais:
        lib.caixa('olhal', (0.7, 0.16, 0.8), tuple(o_ - Vector((0, 0, 0.15))), mol, bisel=0.06)
        lib.cilindro('manilha', 0.16, 0.36, tuple(o_ + Vector((0, 0, 0.12))), lib.mat_pintura('preto', '#1b1c20', rug=0.6), rot=(math.pi / 2, 0, 0), lados=12)
    xg, yc = cg.x, cg.y                       # gancho na vertical do centro de massa
    zg = ztopo + 6.2
    cenario.guindaste_portico(xg, 88, hg, y_c=0.0, gancho=(xg, yc, zg))
    mcabo = lib.mat_aco('cabo', (60, 60, 64), rug=0.4, escovado=False)
    ponta_gancho = Vector((xg, yc, zg - 0.78))
    lib.tubo('anel_gancho', [tuple(ponta_gancho + Vector((0.28 * math.cos(t), 0, 0.28 * math.sin(t)))) for t in np.linspace(0, 2 * math.pi, 17)], r=0.07, mat=mcabo)
    for o_ in olhais:
        lib.tubo('linga', [tuple(ponta_gancho), tuple(o_ + Vector((0, 0, 0.2)))], r=0.07, mat=mcabo)
    # equipe e logística no pátio
    for i, (x, y, r) in enumerate([(70, 24, 1.2), (73, 25.5, 3.6), (64, 21, 2.4), (40, 23, 0.4), (88, 30, 2.0), (52, 19, 3.0),
                                   (100, 36, 1.0), (104, 34, 2.8), (28, 26, 1.6), (-10, 24, 0.2)]):
        cenario.operario((x, y, 0), rot=r, colete=['#f08a24', '#e9e6dc', '#f08a24', '#3a7bd0'][i % 4])
    cenario.empilhadeira((112, 30, 0), rot=2.6)
    cenario.pilha_chapas((118, 16, 0), n=9, tam=(9.0, 2.6, 0.18), rot=0.35, semente=7)
    for (x, y, r, c) in ((122, 22, 2.6, '#3a7bd0'), (114, 21, 0.4, '#f08a24'), (131, 13, 3.4, '#e9e6dc')):
        cenario.operario((x, y, 0), rot=r, colete=c)
    mr = lib.mat_pintura('primer_verm', navio.COR['primer_verm'], rug=0.6, metal=0.15)
    mcz = lib.mat_pintura('primer', navio.COR['primer'], rug=0.55, metal=0.2)
    for i, (x, y, r) in enumerate([(78, 50, 0.1), (94, 48, 0.0), (66, 56, 0.15)]):
        cenario.pilha_chapas((x, y, 0), n=6 + i, tam=(9.0, 2.6, 0.18), rot=r, semente=i, mat=mcz if i % 2 else None)
    for i, (x, y, sx, sy, sz) in enumerate([(60, 66, 12, 9, 6), (40, 52, 10, 8, 5)]):
        lib.caixa('prefab', (sx, sy, sz), (x, y, sz / 2 + 0.3), mr if i == 0 else mcz, bisel=0.12)
        for k in range(4):
            lib.caixa('prefab_nerv', (0.35, sy + 0.1, sz + 0.1), (x - sx / 2 + (k + 0.5) * sx / 4, y, sz / 2 + 0.3), mcz if i == 0 else mr)
    # faíscas de solda nas costuras do bloco de vante
    mf = lib.mat_emissivo('faisca', '#ffcf7a', 40.0); rnd = random.Random(2)
    for (xs_, zs_) in ((46.0, 7.5), (30.0, 12.0)):
        b = navio.meia_boca(xs_, zs_); c = Vector((xs_, b + 0.15, Z0 + zs_))
        luz = bpy.data.lights.new('solda', 'POINT'); luz.energy = 1800; luz.color = (1.0, 0.75, 0.45); luz.shadow_soft_size = 0.2
        o = bpy.data.objects.new('solda', luz); lib.ligar(o); o.location = c + Vector((0.4, 0.8, 0))
        for i in range(16):
            d = Vector((rnd.uniform(-0.6, 1.2), rnd.uniform(0.2, 1.6), rnd.uniform(-1.8, 0.4)))
            lib.tubo('faisca', [tuple(c), tuple(c + d * 0.7)], r=0.03, mat=mf)
    # entorno vivo: galpões, árvores, bandeiras, outro pórtico
    for i, (x, y, w, d, h) in enumerate([(-150, -95, 90, 46, 26), (-40, -110, 70, 40, 22), (70, -105, 110, 44, 30), (190, -95, 70, 40, 20)]):
        cenario.galpao((x, y, 0), (w, d, h), cor=['#e4ddd0', '#b9cde0', '#f0e6d2', '#c8d8c4'][i])
    cenario.guindaste_portico(-150, 70, 50, y_c=10.0, gancho=(-150, 0, 25))
    for i, x in enumerate(np.arange(-210, 260, 14.0)):
        cenario.arvore((x + (i % 3) * 3, -70 + (i % 2) * 4, 0), altura=7 + (i % 4), semente=i)
    for i, x in enumerate((130, 136, 142)):
        cenario.bandeira((x, 70, 0), cor=['#202b57', '#f3b544', '#f6f4ec'][i], altura=10)
    lib.camera((156, 32, 10), (87, 6, 17), lente=24, foco=(96, 4, 10), fstop=11)
    return 'quadro2'


# =====================================================================================
def pintar_face_corte(o, x_corte, mat, eixo=0, tol=0.02):
    me = o.data
    if mat.name not in [m.name for m in me.materials if m]: me.materials.append(mat)
    idx = [m.name for m in me.materials].index(mat.name)
    mw = o.matrix_world
    for pg in me.polygons:
        c = mw @ pg.center; nrm = (mw.to_3x3() @ pg.normal).normalized()
        if abs(c[eixo] - x_corte) < tol and nrm[eixo] > 0.95: pg.material_index = idx


def navio_em_corte(XC, calado, col_cortadores=None, carga_porao=True, porao_aberto=False, filtro_conves=None, esp_linha=0.45, casca=False):
    """Navio pronto cortado no plano x = XC (coordenadas do navio); retorna (raiz, casco_solido_oculto).
    porao_aberto: sem tampa de escotilha na baía cortada (o vão do porão fica à vista, com braçolas e cavernas)."""
    raiz = bpy.data.objects.new('navio', None); lib.ligar(raiz)
    mh = navio.mat_casco()
    k = navio.quilha(XC)
    meta_casca = dict(b=[navio.meia_boca(XC, k + (navio.PONTAL - k) * i / 63) for i in range(64)], k=k, cal=calado,
                      topo=navio.PONTAL, esp=0.38, cor='#f3b544') if casca else None
    mcorte = lib.mat_corte_linha_dagua(z0=0.0, abaixo='#a9d8e8', esp=esp_linha, casca=meta_casca)  # linha d'água do mundo em z = 0
    mporao = lib.mat_pintura('porao', '#a9aca6', rug=0.6)
    mtanque = lib.mat_pintura('primer_verm', navio.COR['primer_verm'], rug=0.6, metal=0.15)
    casco = navio.malha_casco('casco', mh, navio.POPA, XC, n=110)
    cort = lib.colecao('cortadores')
    interno = navio.malha_casco('interno', mporao, -58.5, XC + 2.0, folga=2.0, topo=navio.PONTAL - 0.6, n=50)
    for c in interno.users_collection: c.objects.unlink(interno)
    cort.objects.link(interno)
    # células do duplo fundo e dos tanques laterais (estrutura visível no corte)
    x0c = -40.0
    for yc in np.arange(-12.6, 12.61, 3.15):
        o = lib.caixa('cel_f', (XC + 2 - x0c, 2.75, 1.35), ((x0c + XC + 2) / 2, yc, 1.0), mtanque, colecao=cort)
    for s_ in (-1, 1):
        for (za, zb) in ((2.6, 6.0), (6.45, 9.85), (10.3, 13.7), (14.15, 17.0)):
            lib.caixa('cel_l', (XC + 2 - x0c, 1.4, zb - za), ((x0c + XC + 2) / 2, s_ * 15.0, (za + zb) / 2), mtanque, colecao=cort)
    if porao_aberto:  # abertura da escotilha da baía cortada (o porão fica aberto para cima)
        lib.caixa('escotilha', (XC + 2 + 9.9, 25.0, 4.0), ((XC + 2 - 9.9) / 2, 0, navio.PONTAL + 1.0), mporao, colecao=cort)
    cort.hide_render = True; cort.hide_viewport = True
    lib.booleana(casco, cort, 'DIFFERENCE'); lib.aplicar(casco)
    pintar_face_corte(casco, XC, mcorte)
    casco.parent = raiz
    objs = navio.leme_e_helice() + navio.superestrutura()
    for o in navio.conves_e_tampas():
        if o.location.x < XC - 0.5 and not (porao_aberto and o.name.startswith('tampa') and o.location.x > -10): objs.append(o)
        else: bpy.data.objects.remove(o)
    if porao_aberto:
        ma = lib.mat_aco('aco_estrut', (120, 122, 126), rug=0.4, escovado=False)
        mbr = lib.mat_pintura('bracola', navio.COR['amarelo'], rug=0.45)
        # braçolas da escotilha
        for s_ in (-1, 1):
            objs.append(lib.caixa('bracola', (XC + 9.9, 0.35, 1.6), ((XC - 9.9) / 2, s_ * 12.65, navio.PONTAL + 0.8), mbr, bisel=0.05))
        objs.append(lib.caixa('bracola_t', (0.35, 25.6, 1.6), (-9.9, 0, navio.PONTAL + 0.8), mbr, bisel=0.05))
        # cavernas reforçadas nas paredes internas do porão + longitudinais
        for xw in np.arange(-8.5, XC - 0.3, 3.4):
            for s_ in (-1, 1):
                yi = s_ * (navio.meia_boca(xw, 10) - 2.0)
                objs.append(lib.caixa('caverna_p', (0.25, 1.0, navio.PONTAL - 2.8), (xw, yi - s_ * 0.5, (navio.PONTAL + 2.2) / 2 + 0.2), mporao))
        for zl in (5.0, 8.5, 12.0, 15.5):
            for s_ in (-1, 1):
                yi = s_ * (navio.meia_boca(-3, zl) - 2.0)
                objs.append(lib.caixa('long_p', (XC + 10.0, 0.6, 0.2), ((XC - 10.6) / 2, yi - s_ * 0.3, zl), mporao))
        # guias de célula dos contêineres (cantoneiras verticais) e escada
        for yg in np.arange(-11.0, 11.01, 2.75):
            objs.append(lib.caixa('guia', (0.22, 0.22, navio.PONTAL - 2.2), (-10.3, yg, (navio.PONTAL + 2.2) / 2), ma))
        for dy in (-0.3, 0.3):
            objs.append(lib.caixa('escada', (0.08, 0.08, navio.PONTAL - 2.2), (-10.2, 11.8 + dy, (navio.PONTAL + 2.2) / 2), ma))
        for zz in np.arange(2.6, navio.PONTAL, 0.6):
            objs.append(lib.caixa('degrau', (0.06, 0.6, 0.05), (-10.2, 11.8, zz), ma))
    mc = lib.mat_pintura('conves', navio.COR['conves'], rug=0.7)
    # antepara transversal atrás da baía cortada
    xa = -10.6
    sec = navio._secao(xa, 26, folga=2.0, topo=navio.PONTAL - 0.6)
    ant = lib.malha('antepara', [(xa, y, z) for y, z in sec], [tuple(range(len(sec)))], mtanque)
    objs.append(ant)
    # contêineres no porão da baía em corte (5 camadas) e no convés
    rnd = random.Random(11); matc = lib.mat_conteiner()
    sx, sy, sz = navio.CONT; xb = -3.6
    for j in (range(10) if carga_porao else []):
        y = (j - 4.5) * (sy + 0.2)
        for n in range(5):
            if rnd.random() < 0.06: continue
            o = lib.caixa('cp', navio.CONT, (xb, y, 2.25 + sz / 2 + n * (sz + 0.05)), matc, bisel=0.06, seg=1)
            o.color = lib.srgb(rnd.choice(navio.PALETA_CONT)); objs.append(o)
    objs += navio.carga(4, filtro=filtro_conves or (lambda k, j, n: navio.BAIAS[k] < XC - 6.2))
    for o in objs:
        if o.parent is None: o.parent = raiz
    # casco sólido inteiro (oculto) para escavar a água
    solido = navio.malha_casco('casco_solido', mh); b2 = navio.bulbo('bulbo_s', mh)
    lib.booleana(solido, b2, 'UNION'); lib.aplicar(solido); lib.ocultar(b2)
    solido.parent = raiz; lib.ocultar(solido)
    raiz.location = (0, 0, -calado)
    return raiz, solido


def quadro3():
    """Corte (v3c): porão aberto e vazio. O casco é uma casca de aço fina e contínua (destacada) envolvendo um grande
    volume de ar; o nível da água lá fora (tracejado) passa ACIMA do piso do porão, que continua seco porque o casco
    real é fechado e estanque. Água profunda: sem leito à vista."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=46, sol_rot=120, sol_forca=4.4, nuvens=0.45, zenite='#3a7bd0', meio='#8cc2ee')
    XC, calado = 3.2, 9.0
    raiz, solido = navio_em_corte(XC, calado, carga_porao=False, porao_aberto=True, filtro_conves=lambda k, j, n: False,
                                  esp_linha=0.0, casca=True)
    for (x, y, z, r) in ((-1.5, 2.0, 2.2, 1.9), (-4.0, -3.5, 2.2, 0.6), (0.5, 14.4, navio.PONTAL + 0.02, 2.4)):
        for o in cenario.operario((x, y, z), rot=r, colete='#f08a24'):
            o.parent = raiz
    # nível da água lá fora: tracejado atravessando a seção (o piso do porão fica ~7 m abaixo dele)
    b = navio.meia_boca(XC, calado)
    lib.tracejado('nivel_agua', (XC + 0.25, -b - 2.5, 0.02), (XC + 0.25, b + 2.5, 0.02), lib.mat_emissivo('nivel', '#dff6ff', 2.2), traco=1.3, vao=0.8, r=0.16)
    lib.rotulo('Nível da água lá fora', (XC + 0.25, b - 4.5, 0.02), dx=-0.02, dy=-0.075)
    lib.rotulo('Casco fechado e estanque', (XC, -b + 1.2, navio.quilha(XC) - calado + 0.1), dx=-0.03, dy=0.07)
    bpy.context.view_layer.update()
    oceano_profundo(XC, solido, absorcao=(0.22, 0.62, 0.78), densidade=0.03)
    lib.raios_luz(10, -50, XC - 4, -40, 40, 0.0, 30.0, 4.0, inclinacao=(0.3, 0.1), semente=2, mat=lib.mat_raio_luz('raio3', forca=0.12))
    mp = lib.mat_pintura('peixe', '#c9d6dd', rug=0.3, metal=0.5)
    cenario.cardume((XC - 6, 24, -20), 5.0, 20, 0.55, mp, semente=1, direcao=math.radians(100))
    lib.camera((XC + 58, 4, 26), (XC - 7, 0, -0.5), lente=21, foco=(XC - 4, 0, 0), fstop=16)
    return 'quadro3'


def oceano_profundo(XC, solido, absorcao, densidade, x0=-260.0):
    """Mar em diorama cortado no plano x = XC, profundo (sem leito à vista): o motor em tempo real escurece a água
    com a profundidade (absorção + espalhamento), como mar aberto."""
    magua = lib.mat_agua('agua_prof', absorcao=absorcao, densidade=densidade, espalha=0.0, marola=0.4, escala_marola=0.25)
    agua = lib.bloco_agua('agua', x0, XC, -150, 150, -160, magua, res=2.0, amp=0.3, escala=1.0)
    lib.booleana(agua, solido, 'DIFFERENCE'); lib.aplicar(agua)
    mlonge = lib.mat_pintura('mar_longe', '#2c78a0', rug=0.1, variacao=0.06, escala_var=0.02)
    for (a0, a1, b0, b1) in ((-1500, x0, -1500, 1500), (x0, XC, 150, 1500), (x0, XC, -1500, -150)):
        lib.bloco_agua('longe', a0, a1, b0, b1, -30, mlonge, res=60, amp=0.0, so_superficie=True)
    return agua



# =====================================================================================
def setas_pressao(x0, calado, mat, escala=0.32, n=17, r=0.32, pular_centro=0.0, x_secao=None,
                  prof_costado=(1.2, 3.2, 5.2), ang_bojo=(22.5, 45.0, 67.5), fundo_y=(4.4, 7.2, 10.0)):
    """Setas de pressão hidrostática na seção (mundo: linha d'água em z = 0).
    Cada seta é perpendicular à superfície local do casco e aponta PARA o casco (compressão);
    comprimento ∝ profundidade (p = ρ·g·h). Pontos escolhidos para mostrar os três regimes:
    costado vertical (setas horizontais, crescendo com a profundidade), bojo curvo (a direção gira
    continuamente de horizontal para vertical) e fundo plano (setas verticais, todas iguais).
    Verificação numérica (seção a meia-nau, calado 9 m): ∮p·n ds horizontal = 0; vertical = área submersa."""
    sec = navio._secao(x_secao if x_secao is not None else x0, 400)
    pts = [(y, z - calado) for y, z in sec if z - calado < -0.05]
    amostras = []                     # (y, z, normal_para_fora)
    for (ya, za), (yb, zb) in zip(pts, pts[1:]):
        ds = math.hypot(yb - ya, zb - za)
        if ds < 1e-6: continue
        nrm = Vector((0, (zb - za) / ds, -(yb - ya) / ds))
        ym, zm = (ya + yb) / 2, (za + zb) / 2
        if Vector((0, ym, zm + calado * 0.5)).dot(nrm) < 0: nrm = -nrm
        amostras.append((ym, zm, nrm))
    def mais_perto(cond, chave):
        cand = [a for a in amostras if cond(a)]
        return min(cand, key=chave) if cand else None
    escolhidos = []
    for lado in (1, -1):
        for h in prof_costado:          # costado vertical
            a = mais_perto(lambda a: a[0] * lado > 0 and abs(a[2].y) > 0.995, lambda a: abs(-a[1] - h))
            if a: escolhidos.append(a)
        for ang in ang_bojo:            # bojo: ângulo da normal medido a partir da horizontal
            a = mais_perto(lambda a: a[0] * lado > 0, lambda a: abs(math.degrees(math.atan2(-a[2].z, abs(a[2].y))) - ang))
            if a: escolhidos.append(a)
    zf = min(a[1] for a in amostras)                                 # fundo plano (z constante)
    yplano = max(abs(a[0]) for a in amostras if a[2].z < -0.999 and abs(a[1] - zf) < 1e-3) * 2  # segmento único: ponto médio = metade
    for yy in [s_ * v for v in fundo_y for s_ in (1, -1)]:
        if abs(yy) < pular_centro or abs(yy) > yplano: continue
        escolhidos.append((yy, zf, Vector((0, 0, -1))))
    objs = []
    for (y, z, nrm) in escolhidos:
        comp = -z * escala * 1.5
        ponta = Vector((x0, y, z)) + nrm * 0.25
        base = ponta + nrm * comp
        objs.append(lib.seta3d('pressao', tuple(base), tuple(-nrm), comp, r=r, mat=mat, cabeca=2.4))
    return objs


def quadro4():
    """Empuxo (v4c): corte a meia-nau, navio flutuando em água profunda (sem leito à vista).
    Ciano = volume deslocado (área submersa da seção). Poucas setas de pressão, mas nos três regimes
    (costado, bojo, fundo), perpendiculares ao casco e ∝ profundidade. Peso aplicado em G e empuxo aplicado em B,
    mesmo módulo, sentidos opostos, na mesma vertical (linha de ação tracejada): equilíbrio estático."""
    lib.nova_cena(amostras=128)
    lib.ceu_estilizado(sol_elev=50, sol_rot=120, sol_forca=4.4, nuvens=0.4, zenite='#3a7bd0', meio='#8cc2ee')
    XC, calado = 3.2, 9.0
    raiz, solido = navio_em_corte(XC, calado, carga_porao=False, porao_aberto=False,
                                  filtro_conves=lambda k, j, n: navio.BAIAS[k] < XC - 6.2 and n < 3, esp_linha=0.0)
    bpy.context.view_layer.update()
    sec = navio._secao(XC, 80)
    pts = [(y, z - calado) for y, z in sec if z <= calado]
    b = navio.meia_boca(XC, calado)
    poly = [(b, 0.0)] + pts + [(-b, 0.0)]
    vs = [(XC + 0.06, y, z) for y, z in poly]
    area = lib.malha('area_deslocada', vs, [tuple(range(len(vs)))], lib.mat_fantasma('volume_deslocado', '#2fc4ff', alfa=0.55, brilho=1.3))
    area.visible_shadow = False
    oceano_profundo(XC, solido, absorcao=(0.30, 0.74, 0.84), densidade=0.012)
    # pressão: 2 setas no costado, 1 no bojo e 2 no fundo, por bordo (10 no total)
    mseta = lib.mat_emissivo('seta_pressao', '#eaf7ff', 1.8)
    setas = setas_pressao(XC + 0.9, calado, mseta, escala=0.32, r=0.40, x_secao=XC,
                          prof_costado=(2.2, 5.6), ang_bojo=(45.0,), fundo_y=(5.0, 10.5))
    # G e B (coordenadas do mundo; linha d'água em z = 0)
    KB = 4.72      # centro de carena calculado com a forma real do casco (calado 9 m): V = 44.125 m³, x = 0,4 m
    KG = 12.5      # centro de gravidade: estimativa didática de navio porta-contêineres carregado (KG ≈ 0,7 × pontal)
    zB, zG = KB - calado, KG - calado; L = 3.5; xs = XC + 0.9
    setas.append(lib.seta3d('empuxo', (xs, 0, zB), (0, 0, 1), L, r=1.0, mat=lib.mat_emissivo('seta_empuxo', '#f3b544', 1.4), cabeca=2.2))
    setas.append(lib.seta3d('peso', (xs, 0, zG), (0, 0, -1), L, r=1.0, mat=lib.mat_emissivo('seta_peso', '#4a63c8', 1.8), cabeca=2.2))
    lib.cilindro('ponto_B', 0.75, 0.3, (xs, 0, zB), lib.mat_emissivo('ponto_B', '#f3b544', 2.0), rot=(0, math.pi / 2, 0), lados=24)
    lib.cilindro('ponto_G', 0.75, 0.3, (xs, 0, zG), lib.mat_emissivo('ponto_G', '#6f86e6', 2.0), rot=(0, math.pi / 2, 0), lados=24)
    linha = lib.tracejado('linha_acao', (xs - 0.05, 0, -calado - 2.0), (xs - 0.05, 0, navio.PONTAL - calado + 4.0), lib.mat_emissivo('linha_acao', '#f6f4ec', 1.4), traco=0.9, vao=0.6, r=0.07)
    for o in setas + linha: o.visible_glossy = False; o.visible_shadow = False
    lib.rotulo('Peso (G)', (xs, 0, zG), dx=0.05, dy=-0.05)
    lib.rotulo('Empuxo (B)', (xs, 0, zB), dx=0.05, dy=0.05)
    mp = lib.mat_pintura('peixe', '#c9d6dd', rug=0.3, metal=0.5)
    cenario.cardume((XC - 10, 26, -18), 4.0, 16, 0.5, mp, semente=4, direcao=math.radians(100))
    lib.camera((XC + 84, 10, 3.0), (XC - 6, 0, 0.0), lente=22, foco=(XC, 0, -2), fstop=22)
    return 'quadro4'



# =====================================================================================
def quadro5():
    """Porto: portêiner (STS) baixando um contêiner no navio atracado; calado aumentando com a carga."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=30, sol_rot=60, sol_forca=4.2, nuvens=0.5, horizonte='#f6e6cc', sol_cor=(1.0, 0.9, 0.76))
    calado = 9.2
    # navio atracado: costado de boreste (y<0... aqui o navio fica em y<0 e o cais em y>0)
    yn = -(navio.MEIA_BOCA + 4.5)
    raiz = bpy.data.objects.new('navio', None); lib.ligar(raiz)
    rnd = random.Random(5)
    def filtro(k, j, n):
        if k >= 6: return n < 1 and j % 3 == 0     # baías de vante ainda quase vazias
        if k == 5: return n < 2 or j > 6
        return True
    for o in navio.navio_pronto(nivel_carga=4, carga_filtro=filtro) + navio.marcas_calado(44.0, 1) + navio.disco_plimsoll(0.0, 1):
        if o.parent is None: o.parent = raiz
    raiz.location = (0, yn, -calado)
    magua = lib.mat_agua('agua5', absorcao=(0.25, 0.62, 0.72), densidade=0.05, marola=0.45, escala_marola=0.3, rug=0.05)
    lib.bloco_agua('agua', -500, 500, -900, -2.0, -30, magua, res=3.0, amp=0.18, so_superficie=False)
    # cais
    for o in cenario.cais(-500, 500, -2.0, 140.0, topo=3.0, fundo=-30.0): pass
    for x in np.arange(-90, 120, 22.0):
        cenario.cabeco((x, 0.2, 3.0), 1.2)
        cenario.defensa((x + 11, -2.6, 1.2), r=1.1, rot=0.0)
    # amarras (catenárias) do navio aos cabeços
    mcorda = lib.mat_pintura('corda', '#e9d8a8', rug=0.8)
    for (xs, xc) in ((-92, -90), (-80, -68), (92, 98), (80, 76)):
        b = navio.meia_boca(xs, navio.PONTAL)
        p0 = Vector((xs, yn + b, navio.PONTAL - calado + 0.5)); p1 = Vector((xc, 0.2, 3.9))
        pts = [tuple(p0.lerp(p1, t) - Vector((0, 0, 2.2 * math.sin(math.pi * t)))) for t in np.linspace(0, 1, 14)]
        lib.tubo('amarra', pts, r=0.12, mat=mcorda)
    # pátio: pilhas de contêineres e trilhos do portêiner
    matc = lib.mat_conteiner()
    for i, x0 in enumerate((-120, -60, 40, 100)):
        for j in range(6):
            for n in range(rnd.randint(1, 4)):
                o = lib.caixa('pilha', navio.CONT, (x0 + (j % 3) * 0.0, 46 + j * 2.6, 3.0 + 1.3 + n * 2.62), matc, bisel=0.05)
                o.color = lib.srgb(rnd.choice(navio.PALETA_CONT))
    ml = lib.mat_pintura('linha', '#e9b545', rug=0.6)
    for y in (12.0, 40.0): lib.caixa('faixa', (1000, 0.3, 0.02), (0, y, 3.01), ml)
    # portêineres: o principal trabalhando na baía 5, outros dois ao fundo
    xb = navio.BAIAS[5]
    z_alvo = navio.PONTAL - calado + 0.9 + 2 * 2.62   # topo da pilha onde o contêiner vai pousar
    zs = z_alvo + 7.5
    yb = yn + 4 * (navio.CONT[1] + 0.08) * -0.5
    cenario.guindaste_sts(xb, 8.0, 38.0, altura=44.0, alcance=50.0, trolley_y=yb, z_spreader=zs)
    o = lib.caixa('suspenso', navio.CONT, (xb, yb, zs - 0.15), matc, bisel=0.05); o.color = lib.srgb('#c8442f')
    cenario.guindaste_sts(xb - 62, 8.0, 38.0, altura=44.0, alcance=50.0, trolley_y=yn + 6, z_spreader=26.0)
    cenario.guindaste_sts(xb + 70, 8.0, 38.0, altura=44.0, alcance=50.0, trolley_y=20, z_spreader=20.0)
    # caminhão com chassi sob o portêiner
    mcam = lib.mat_pintura('caminhao', '#2e3f6b', rug=0.45)
    lib.caixa('cab', (2.6, 2.5, 3.0), (xb + 10, 22, 4.8), mcam, bisel=0.25)
    lib.caixa('chassi', (13, 2.4, 0.5), (xb + 2.5, 22, 4.1), lib.mat_pintura('preto', '#1b1c20', rug=0.6), bisel=0.05)
    oc = lib.caixa('cont_cam', navio.CONT, (xb + 2.5, 22, 4.35 + 1.3), matc, bisel=0.05); oc.color = lib.srgb('#e0a33a')
    for i, (x, y, r) in enumerate([(xb + 6, 16, 2.0), (xb - 8, 13, 0.5)]):
        cenario.operario((x, y, 3.0), rot=r)
    # ilhas/colinas ao longe para fechar o horizonte
    mcol = lib.mat_pintura('colina', '#6f8f86', rug=0.9, variacao=0.1)
    for (x, y, r, h) in ((-700, -1400, 260, 70), (-300, -1600, 340, 110), (500, -1500, 300, 80)):
        cc = lib.cilindro('colina', r, h, (x, y, h / 2 - 20), mcol, lados=10, r2=r * 0.35, suave=False)
    lib.bloco_agua('longe', -3000, 3000, -3000, -900, -30, lib.mat_pintura('mar_longe', '#2c6f8f', rug=0.1, variacao=0.06, escala_var=0.02), res=200, amp=0, so_superficie=True)
    lib.camera((128, -2.0, 15), (12, -15, 21), lente=33, foco=(60, -6, 5), fstop=16)
    return 'quadro5'


QUADROS = {1: quadro1, 2: quadro2, 3: quadro3, 4: quadro4, 5: quadro5}

if __name__ == '__main__':
    n = int(sys.argv[1]); pct = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    amostras = int(sys.argv[3]) if len(sys.argv) > 3 else 128
    saida = sys.argv[4] if len(sys.argv) > 4 else None
    t = time.time(); nome = QUADROS[n](); tm = time.time() - t
    saida = saida or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'etapa_b', 'previas', f'{nome}_{pct}.png')
    t = time.time(); lib.renderizar(saida, pct, amostras)
    print(f'MONTAGEM {tm:.1f}s RENDER {time.time() - t:.1f}s -> {saida}')
