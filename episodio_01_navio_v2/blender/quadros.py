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
    """Estaleiro: casco em construção — popa chapeada, proa em cavernas; pórtico içando um bloco."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=30, sol_rot=100, sol_forca=4.2, nuvens=0.5, horizonte='#f5dfc0', meio='#9cc4e6', sol_cor=(1.0, 0.88, 0.72))
    mg = lib.mat_concreto('chao', (158, 154, 144), escala=0.04)
    lib.caixa('chao', (1400, 860, 2), (0, 270, -1.0), mg)
    ml = lib.mat_pintura('linha', '#e9b545', rug=0.6)
    for y in (-30, 30):
        lib.caixa('faixa', (300, 0.4, 0.02), (0, y, 0.01), ml)
    # mar ao fundo (lado -y) com cais
    magua = lib.mat_agua('agua2', absorcao=(0.25, 0.65, 0.75), densidade=0.04, marola=0.5, rug=0.06)
    lib.bloco_agua('mar', -900, 900, -1200, -158, -20, lib.mat_pintura('mar_longe', '#2c6f8f', rug=0.12, variacao=0.08, escala_var=0.02), res=20, amp=0.0, so_superficie=True)
    for o in bpy.data.objects:
        if o.name.startswith('mar'): o.location.z = -1.2
    lib.caixa('borda_cais', (1800, 4, 6), (0, -158, -3.0), lib.mat_concreto('concreto_cais', (156, 151, 140)))
    Z0 = 1.6
    # picadeiros (blocos de apoio)
    mm = lib.mat_pintura('picadeiro', '#6a4f35', rug=0.9)
    mbl = lib.mat_concreto('picad_conc', (140, 136, 128))
    for x in np.arange(-92, 92, 7.0):
        k = navio.quilha(x)
        lib.caixa('picad', (1.4, 2.2, Z0 + k - 0.3), (x, 0, (Z0 + k - 0.3) / 2), mbl, bisel=0.05)
        lib.caixa('picad_m', (1.6, 2.4, 0.3), (x, 0, Z0 + k - 0.15), mm, bisel=0.03)
        if -40 < x < 60:
            for s in (-1, 1):
                lib.caixa('picad_l', (1.2, 1.6, Z0 - 0.3), (x, s * 9.0, (Z0 - 0.3) / 2), mbl, bisel=0.05)
    raiz = bpy.data.objects.new('navio', None); lib.ligar(raiz)
    for o in navio.estrutura_construcao(x_chapa=-6.0):
        if o.parent is None: o.parent = raiz
    raiz.location = (0, 0, Z0)
    # convés provisório na parte chapeada + superestrutura só iniciada (primer)
    mp = lib.mat_pintura('primer', navio.COR['primer'], rug=0.55, metal=0.2)
    lib.caixa('super_ini', (15, 26, 5.8), (-79, 0, Z0 + navio.PONTAL + 2.9), mp, bisel=0.1)
    # andaimes ao longo do costado chapeado (bombordo, lado da câmera)
    mand = lib.mat_aco('andaime', (150, 152, 156), rug=0.4, escovado=False)
    mplat = lib.mat_pintura('plataforma', '#8a6a44', rug=0.9)
    for (x0, x1) in ((-70, -45), (-38, -12)):
        b = max(navio.meia_boca((x0 + x1) / 2, 12), 10)
        andaime(x0, x1, b + 1.0, 19.5, mand, mplat)
    # pórtico (goliath) sobre a proa, içando um bloco pré-fabricado de costado
    xg = 46.0; hg = 58.0; zb = 27.0
    cenario.guindaste_portico(xg, 84, hg, y_c=0.0, gancho=(xg, 6.0, zb + 8.5))
    # bloco de costado: chapa curva com cavernas e longarinas soldadas
    mr = lib.mat_pintura('primer_verm', navio.COR['primer_verm'], rug=0.6, metal=0.15)
    xs = np.linspace(0, 12, 7); zs = np.linspace(0, 9, 7)
    v = []; f = []
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            v.append((x - 6, 0.6 * math.sin(z / 9 * math.pi) * 0 + 0.9 * (z / 9) ** 2, z - 4.5))
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            a = i * len(zs) + j; f.append((a, a + len(zs), a + len(zs) + 1, a + 1))
    bl = lib.malha('bloco_costado', v, f, mp, suave=True)
    sd = bl.modifiers.new('esp', 'SOLIDIFY'); sd.thickness = 0.25
    blocos = [bl]
    for x in np.linspace(-5.4, 5.4, 5):
        pts = [(x, 0.9 * (z / 9) ** 2 + 0.45, z - 4.5) for z in np.linspace(0, 9, 8)]
        blocos.append(lib.tubo('cav_bloco', pts, r=0.3, mat=mr))
    for z in (-2.0, 1.0, 3.5):
        zz = z + 4.5; blocos.append(lib.tubo('lng_bloco', [(-6, 0.9 * (zz / 9) ** 2 + 0.4, z), (6, 0.9 * (zz / 9) ** 2 + 0.4, z)], r=0.22, mat=mr))
    piv = bpy.data.objects.new('bloco', None); lib.ligar(piv)
    for o in blocos: o.parent = piv
    piv.location = (xg, 6.0, zb); piv.rotation_euler = (0, 0, math.radians(8))
    mcabo = lib.mat_aco('cabo', (60, 60, 64), rug=0.4, escovado=False)
    for dx in (-5.5, 5.5):
        lib.tubo('linga', [(xg, 6.0, zb + 8.0), (xg + dx * math.cos(0.14), 6.0 + dx * math.sin(0.14) + 0.5, zb + 4.6)], r=0.06, mat=mcabo)
    # chapas, perfis e operários no pátio
    for i, (x, y, r) in enumerate([(70, 34, 0.1), (84, 30, 0.0), (58, 40, 0.15), (-20, 40, 0.0)]):
        cenario.pilha_chapas((x, y, 0), n=6 + i, tam=(9.0, 2.6, 0.18), rot=r, semente=i, mat=mp if i % 2 else None)
    for i, (x, y, r) in enumerate([(62, 26, 1.2), (66, 27.5, 3.6), (75, 22, 2.4), (30, 22, 0.4), (-5, 24, 2.0), (52, 18, 3.0)]):
        cenario.operario((x, y, 0), rot=r, colete=['#f08a24', '#e9e6dc', '#f08a24'][i % 3])
    # faíscas de solda na emenda chapeado/estrutura
    mf = lib.mat_emissivo('faisca', '#ffcf7a', 40.0)
    rnd = random.Random(2)
    for k, (zs_, ys_) in enumerate([(9.0, 1), (14.0, 1), (5.0, 1)]):
        b = navio.meia_boca(-6.0, zs_)
        c = Vector((-6.0, ys_ * (b + 0.1), Z0 + zs_))
        luz = bpy.data.lights.new('solda', 'POINT'); luz.energy = 1500; luz.color = (1.0, 0.75, 0.45); luz.shadow_soft_size = 0.2
        o = bpy.data.objects.new('solda', luz); lib.ligar(o); o.location = c + Vector((0.5, 0.6, 0))
        for i in range(14):
            d = Vector((rnd.uniform(0.2, 1.2), rnd.uniform(0.2, 1.5), rnd.uniform(-1.6, 0.4)))
            lib.tubo('faisca', [tuple(c), tuple(c + d * 0.6)], r=0.03, mat=mf)
    # galpões e outro guindaste ao fundo
    for i, (x, y, w, d, h) in enumerate([(-150, -95, 90, 46, 26), (-40, -110, 70, 40, 22), (70, -105, 110, 44, 30), (190, -95, 70, 40, 20)]):
        cenario.galpao((x, y, 0), (w, d, h), cor=['#c9ccc8', '#b9c6cf', '#d9d2c3', '#c4c9c0'][i])
    cenario.guindaste_portico(-150, 70, 50, y_c=10.0, gancho=(-150, 0, 25))
    # blocos pré-fabricados aguardando montagem e contêineres-escritório
    mcz = lib.mat_pintura('primer', navio.COR['primer'], rug=0.55, metal=0.2)
    for i, (x, y, sx, sy, sz, r) in enumerate([(62, 52, 14, 10, 6, 0.0), (80, 46, 12, 9, 5, 0.1), (40, 58, 12, 12, 7, 0.0), (22, 44, 10, 8, 4, 0.2)]):
        b = lib.caixa('prefab', (sx, sy, sz), (x, y, sz / 2 + 0.3), mr if i % 2 == 0 else mcz, bisel=0.12, rot=(0, 0, r))
        for k in range(4):
            lib.caixa('prefab_nerv', (0.35, sy + 0.1, sz + 0.1), (x - sx / 2 + (k + 0.5) * sx / 4, y, sz / 2 + 0.3), mcz if i % 2 == 0 else mr, rot=(0, 0, r))
    for i, (x, y, cor) in enumerate([(-8, 52, '#2f5d8a'), (-8, 55, '#e9e6dc'), (5, 60, '#3f7f6e')]):
        o = lib.caixa('escritorio', navio.CONT, (x, y, navio.CONT[2] / 2), lib.mat_conteiner(), bisel=0.05)
        o.color = lib.srgb(cor)
    lib.camera((128, 88, 64), (22, -6, 10), lente=26, foco=(46, 6, 27), fstop=11)
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


def navio_em_corte(XC, calado, col_cortadores=None):
    """Navio pronto cortado no plano x = XC (coordenadas do navio); retorna (raiz, casco_solido_oculto)."""
    raiz = bpy.data.objects.new('navio', None); lib.ligar(raiz)
    mh = navio.mat_casco()
    mcorte = lib.mat_corte_linha_dagua(z0=0.0, abaixo='#a9d8e8', esp=0.28)  # coordenada do mundo: linha d'água em z = 0
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
    cort.hide_render = True; cort.hide_viewport = True
    lib.booleana(casco, cort, 'DIFFERENCE'); lib.aplicar(casco)
    pintar_face_corte(casco, XC, mcorte)
    casco.parent = raiz
    objs = navio.leme_e_helice() + navio.superestrutura()
    for o in navio.conves_e_tampas():
        if o.location.x < XC - 0.5: objs.append(o)
        else: bpy.data.objects.remove(o)
    mc = lib.mat_pintura('conves', navio.COR['conves'], rug=0.7)
    # antepara transversal atrás da baía cortada
    xa = -10.6
    sec = navio._secao(xa, 26, folga=2.0, topo=navio.PONTAL - 0.6)
    ant = lib.malha('antepara', [(xa, y, z) for y, z in sec], [tuple(range(len(sec)))], mtanque)
    objs.append(ant)
    # contêineres no porão da baía em corte (5 camadas) e no convés
    rnd = random.Random(11); matc = lib.mat_conteiner()
    sx, sy, sz = navio.CONT; xb = -3.6
    for j in range(10):
        y = (j - 4.5) * (sy + 0.2)
        for n in range(5):
            if rnd.random() < 0.06: continue
            o = lib.caixa('cp', navio.CONT, (xb, y, 2.25 + sz / 2 + n * (sz + 0.05)), matc, bisel=0.06, seg=1)
            o.color = lib.srgb(rnd.choice(navio.PALETA_CONT)); objs.append(o)
    objs += navio.carga(4, filtro=lambda k, j, n: navio.BAIAS[k] < XC - 6.2)
    for o in objs:
        if o.parent is None: o.parent = raiz
    # casco sólido inteiro (oculto) para escavar a água
    solido = navio.malha_casco('casco_solido', mh); b2 = navio.bulbo('bulbo_s', mh)
    lib.booleana(solido, b2, 'UNION'); lib.aplicar(solido); lib.ocultar(b2)
    solido.parent = raiz; lib.ocultar(solido)
    raiz.location = (0, 0, -calado)
    return raiz, solido


def quadro3():
    """Corte transversal a meia-nau do navio carregado, flutuando (água e leito também em corte)."""
    lib.nova_cena()
    lib.ceu_estilizado(sol_elev=34, sol_rot=150, sol_forca=4.0, nuvens=0.45)
    XC, calado = 3.2, 10.0
    raiz, solido = navio_em_corte(XC, calado)
    bpy.context.view_layer.update()
    magua = lib.mat_agua('agua3', absorcao=(0.22, 0.62, 0.78), densidade=0.035, espalha=0.0, marola=0.4, escala_marola=0.25)
    agua = lib.bloco_agua('agua', -220, XC, -150, 150, -42, magua, res=2.0, amp=0.35, escala=1.0)
    lib.booleana(agua, solido, 'DIFFERENCE'); lib.aplicar(agua)
    mlonge = lib.mat_pintura('mar_longe', '#2c6f8f', rug=0.1, variacao=0.06, escala_var=0.02)
    for (x0, x1, y0, y1) in ((-1500, -220, -1500, 1500), (-220, XC, 150, 1500), (-220, XC, -1500, -150)):
        lib.bloco_agua('longe', x0, x1, y0, y1, -40, mlonge, res=60, amp=0.0, so_superficie=True)
    def leito(X, Y): return -40 + 0.8 * np.sin(Y * 0.05) + 0.5 * np.sin(X * 0.08 + 1.0)
    grade('leito', -220, XC + 0.05, -150, 150, leito, lib.mat_areia('areia3'), res=3.0, fundo=-55)
    mr = lib.mat_pintura('rocha', '#6d7275', rug=0.85, variacao=0.15)
    rnd = random.Random(3)
    for i in range(10):
        x, y = rnd.uniform(-60, XC - 3), rnd.uniform(-60, 60)
        lib.rocha('rocha', (x, y, float(leito(np.array(x), np.array(y)))), rnd.uniform(1.0, 2.6), mr, semente=i)
    lib.raios_luz(10, -60, XC - 4, -60, 60, 0.0, 30.0, 4.0, inclinacao=(0.3, 0.1), semente=2, mat=lib.mat_raio_luz('raio3', forca=0.12))
    mp = lib.mat_pintura('peixe', '#c9d6dd', rug=0.3, metal=0.5)
    cenario.cardume((XC - 6, 30, -24), 6.0, 26, 0.55, mp, semente=1, direcao=math.radians(100))
    lib.camera((XC + 70, 48, 4), (XC - 12, -1, -8), lente=27, foco=(XC, 0, -2), fstop=16)
    return 'quadro3'


# =====================================================================================
def setas_pressao(x0, calado, mat, escala=0.32, n=17, r=0.32):
    """Setas de pressão hidrostática normais ao casco na seção x0 (coordenadas do mundo: linha d'água z=0).
    Comprimento ∝ profundidade (p = ρ·g·h): curtas perto da superfície, máximas no fundo."""
    sec = navio._secao(x0, 60)
    pts = [(y, z - calado) for y, z in sec if z - calado < -3.0]
    objs = []
    # reamostra uniformemente pelo perímetro molhado
    L = [0.0]
    for (ya, za), (yb, zb) in zip(pts, pts[1:]): L.append(L[-1] + math.hypot(yb - ya, zb - za))
    alvo = np.linspace(0, L[-1], n)
    for t in alvo:
        i = max(0, min(len(pts) - 2, int(np.searchsorted(L, t)) - 1))
        f = (t - L[i]) / max(L[i + 1] - L[i], 1e-6)
        y = pts[i][0] + f * (pts[i + 1][0] - pts[i][0]); z = pts[i][1] + f * (pts[i + 1][1] - pts[i][1])
        ty, tz = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        nrm = Vector((0, tz, -ty)).normalized()      # normal (orientação conferida abaixo)
        if Vector((0, y, z + calado * 0.5)).dot(nrm) < 0: nrm = -nrm   # aponta para fora do casco
        comp = -z * escala * 1.5
        ponta = Vector((x0, y, z)) + nrm * 0.25
        base = ponta + nrm * comp
        objs.append(lib.seta3d('pressao', tuple(base), tuple(-nrm), comp, r=r, mat=mat, cabeca=2.4))
    return objs


def quadro4():
    """Vista subaquática: casco visto de baixo, setas de pressão e a resultante (empuxo)."""
    lib.nova_cena(amostras=128)
    lib.ceu_estilizado(sol_elev=55, sol_rot=150, sol_forca=4.5, nuvens=0.3)
    calado = 10.0
    raiz = bpy.data.objects.new('navio', None); lib.ligar(raiz)
    for o in navio.navio_pronto(nivel_carga=4):
        if o.parent is None: o.parent = raiz
    raiz.location = (0, 0, -calado)
    magua = lib.mat_agua('agua4', absorcao=(0.25, 0.66, 0.80), densidade=0.016, espalha=0.007, cor_esp=(0.5, 0.8, 0.95),
                         marola=0.5, escala_marola=0.3)
    lib.bloco_agua('agua', -320, 320, -260, 260, -400, magua, res=2.5, amp=0.45)
    lib.luz_area((10, -10, -90), (10, 0, -10), tam=80, energia=2.4e5, cor=(0.72, 0.88, 1.0))  # retorno difuso vindo do fundo
    mseta = lib.mat_emissivo('seta_pressao', '#e6f6ff', 2.4)
    mres = lib.mat_emissivo('seta_empuxo', '#f3b544', 2.2)
    setas = setas_pressao(10.0, calado, mseta, escala=0.36, n=15, r=0.5)
    setas.append(lib.seta3d('empuxo', (10.0, 0, -calado - 30), (0, 0, 1), 19.0, r=1.7, mat=mres, cabeca=2.5))
    for o in setas:   # setas são diagrama: não refletem no casco nem projetam sombra (evita "setas fantasma")
        o.visible_glossy = False; o.visible_shadow = False; o.visible_transmission = False
    mc = bpy.data.materials.get('casco')
    if mc: mc.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 0.0; mc.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.6
    lib.raios_luz(16, -80, 90, -70, 20, 0.0, 55.0, 6.0, inclinacao=(0.22, 0.25), semente=7, mat=lib.mat_raio_luz('raio4', forca=0.08))
    mp = lib.mat_pintura('peixe', '#c9d6dd', rug=0.3, metal=0.5)
    cenario.cardume((52, -30, -40), 3.5, 24, 0.5, mp, semente=4, direcao=math.radians(200))
    cenario.cardume((-30, -40, -18), 7.0, 22, 0.5, mp, semente=9, direcao=math.radians(170))
    lib.camera((78, -36, -30), (8, 0, -13), lente=22, foco=(10, 0, -12), fstop=22)
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
