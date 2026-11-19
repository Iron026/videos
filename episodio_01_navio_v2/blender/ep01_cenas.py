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
from ep_base import (FPS, suave, suave5, lerp, V, camera_em, trilha, surge, oclusor, Rotulos, exportar_seg, camera_planos)

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
        # afastado do casco o bastante para a curvatura da proa (flare) não cortar os algarismos largos ('10M', '11M')
        b = max(navio.meia_boca(x + dx, z + dz) for dx in (-0.24, 0.0, 0.24) for dz in (0.0, 0.07, 0.14)) + 0.03
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
def espuma(raiz, T, L=104.0, vel=6.0):
    """Onda de proa, crista na roda de proa, faixa de espuma ao longo do costado e esteira — espuma PROCEDURAL do motor
    (material 'espuma': ruído que escorre para ré na velocidade do navio, máscaras pela geometria da proa e pelo ângulo
    de Kelvin, desenhada sobre a água). Malhas no espaço do navio (superfície em z = T)."""
    zt = T + 0.06; objs = []
    def grade(nome, x0, x1, y0, y1, nx, ny, mat):
        vs = [(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny, zt) for i in range(nx + 1) for j in range(ny + 1)]
        fs = [(i * (ny + 1) + j, (i + 1) * (ny + 1) + j, (i + 1) * (ny + 1) + j + 1, i * (ny + 1) + j + 1) for i in range(nx) for j in range(ny)]
        return lib.malha(nome, vs, fs, mat)
    objs.append(grade('espuma_proa', L - 75, L + 3, -30, 30, 60, 30, lib.mat_espuma('espuma_proa', 0, x0=L - 0.5, vel=vel, decai=26, larg=navio.MEIA_BOCA, abre=19.0, dens=1.0, escala=0.2)))
    for s_ in (1, -1):
        objs.append(grade('espuma_costado', -88, 58, s_ * (navio.MEIA_BOCA - 0.4), s_ * (navio.MEIA_BOCA + 6), 70, 8,
                          lib.mat_espuma('espuma_costado', 2, x0=58, vel=vel, decai=120, larg=navio.MEIA_BOCA, dens=0.8, escala=0.22)))
        for (nome_, afast, inc, alt_, dec_, xmax) in (('crista_proa', 0.35, 0.25, 2.4, 13, 40), ('borrifo_proa', 2.2, 0.9, 1.3, 16, 46)):
            xs_ = np.linspace(L - 0.6, L - xmax, 40); zs_ = np.linspace(T - 0.6, T + alt_ + 0.6, 8); vs, fs = [], []
            for x in xs_:
                b = navio.meia_boca(x, T) + afast + 0.18 * (L - x) * (afast > 1)      # a lâmina externa abre com a onda
                for z in zs_: vs.append((x, s_ * (b + inc * max(z - T, 0)), z))
            nz = len(zs_)
            for a in range(len(xs_) - 1):
                for k in range(nz - 1): fs.append((a * nz + k, (a + 1) * nz + k, (a + 1) * nz + k + 1, a * nz + k + 1))
            objs.append(lib.malha(nome_, vs, fs, lib.mat_espuma(nome_, 3, x0=L - 0.5, vel=vel, decai=dec_, z0=T, alt=alt_, dens=1.0, escala=0.32)))
    objs.append(grade('esteira', navio.POPA - 260, navio.POPA + 4, -90, 90, 80, 45, lib.mat_espuma('esteira', 1, x0=navio.POPA + 2, vel=vel, decai=70, larg=5.0, dens=0.85, escala=0.12)))
    for o in objs: o.parent = raiz; o.visible_shadow = False
    return objs


def seg02(pasta):
    """OUTRO porta-contêineres (pintura cinza e verde, 5 camadas), navegando a 6 m/s: plano geral de escala →
    pilhas de carga → travelling ao longo do costado → linha d'água com a onda de proa → o costado deslizando."""
    lib.nova_cena()
    lib.ceu_estilizado(**CEU_DIA)
    raiz, conts, _ = navio_completo(0.0, pintura=PINTURA_OUTRO, niveis=5, semente=8, raiz_nome='navio_outro')
    n_total = len(conts); T = calado_com(n_total); raiz.location.z = -T
    espuma(raiz, T)
    mar_aberto(ext=900)
    VEL, X0 = 6.0, -60.0
    def xs(g): return X0 + VEL * (g - 4.40)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    P = [(4.40, [(4.40, (240, -250, 96), lambda g: V(xs(g) + 10, 0, 4), 26), (6.40, (232, -238, 88), lambda g: V(xs(g) + 14, 0, 4), 27)]),
         (6.40, [(6.40, lambda g: V(xs(g) + 30, -52, 34), lambda g: V(xs(g) - 4, 0, 22), 26), (8.70, lambda g: V(xs(g) + 16, -40, 29), lambda g: V(xs(g) - 10, 0, 21), 27)]),
         (8.70, [(8.70, lambda g: V(xs(8.70) + 40 - 6.0 * (g - 8.7), -36, 9), lambda g: V(xs(8.70) + 40 - 6.0 * (g - 8.7) - 14, 0, 9), 24),
                 (11.0, lambda g: V(xs(8.70) + 40 - 6.0 * (g - 8.7), -36, 9), lambda g: V(xs(8.70) + 40 - 6.0 * (g - 8.7) - 14, 0, 9), 24)]),
         (11.0, [(11.0, (xs(11.0) + 158, -58, 2.2), lambda g: V(xs(g) + 100, -4, 3.0), 30), (13.4, (xs(11.0) + 150, -54, 2.0), lambda g: V(xs(g) + 98, -4, 3.0), 30)]),
         (13.4, [(13.4, (xs(13.4) - 170, -78, 7), lambda g: V(xs(g) - 10, 0, 6), 26), (15.1, (xs(13.4) - 166, -76, 6.5), lambda g: V(xs(g) - 6, 0, 6), 26)])]
    def anim(g):
        raiz.location = (xs(g), 0, -T + 0.10 * math.sin(2 * math.pi * g / 9.0)); raiz.rotation_euler = (0.006 * math.sin(2 * math.pi * g / 11.0), 0.002 * math.sin(2 * math.pi * g / 8.0), 0)
        camera_planos(cam, P, g)
    exportar_seg(pasta, 4.40, 15.10, anim, extra=dict(segmento='02', calado=T, n_cont=n_total, velocidade=VEL))
    print('CALADO_OUTRO', T, 'CONTEINERES', n_total)


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
        # REFINAMENTO · solda: arco branco-azulado (núcleo + halo) tremulando a 30 Hz, luz do arco refletida nas chapas vizinhas
        # (brilho aditivo com queda radial, sem luz dinâmica no motor) e faíscas alaranjadas BALÍSTICAS (gravidade), de vida
        # curta, com trajetórias variadas; o arco abre em cordões (liga, pausa curta, liga de novo).
        Z0 = raiz.location.z
        focos = [(Vector((74.0, navio.meia_boca(74.0, 7.6) + 0.2, Z0 + 7.6)), [(23.75, 24.55), (24.68, 25.25)], 34),
                 (Vector((70.2, navio.meia_boca(70.2, 12.0) + 0.2, Z0 + 12.0)), [(24.0, 24.7), (24.85, 25.4)], 16),
                 (Vector((38.0, navio.meia_boca(38.0, 1.0) + 0.25, Z0 + 1.0)), [(24.9, 26.4)], 10),
                 (Vector((22.0, navio.meia_boca(22.0, 1.0) + 0.25, Z0 + 1.0)), [(25.1, 26.4)], 10)]
        def disco(nome, c, nrm, raio, mat, desloc, nseg=28):
            vs = [(0.0, 0.0, 0.0)] + [(raio * math.cos(2 * math.pi * q_ / nseg), 0.0, raio * math.sin(2 * math.pi * q_ / nseg)) for q_ in range(nseg)]
            o = lib.malha(nome, vs, [(0, 1 + q_, 1 + (q_ + 1) % nseg) for q_ in range(nseg)], mat)
            o.location = c + nrm * desloc; o.visible_shadow = False; return o
        mf = lib.mat_brilho('faisca_brilho', '#ff7412', forca=2.6, raio=1.05, queda=0.9, tremor=0.15); mnuc = lib.mat_emissivo('arco_nucleo', '#f2f8ff', 60.0)
        faiscas = []
        for k_, (c, cordoes, nf) in enumerate(focos):
            nrm = Vector((0, 1 if c.y > 0 else -1, 0))
            for q_, (ta, tb) in enumerate(cordoes):
                sem = 3.0 * k_ + q_
                luz = disco('luz_chapa', c, nrm, 3.4, lib.mat_brilho(f'luz_chapa{k_}{q_}', '#d6e4ff', forca=0.55, raio=3.4, queda=2.4, tremor=0.45, semente=sem), 0.05)
                halo = disco('arco_halo', c, nrm, 0.95, lib.mat_brilho(f'arco_halo{k_}{q_}', '#a8d2ff', forca=2.4, raio=0.95, queda=1.8, tremor=0.55, semente=sem + 0.5), 0.22)
                nuc = disco('arco_luz', c, nrm, 0.38, lib.mat_brilho(f'arco_luz{k_}{q_}', '#ffffff', forca=4.5, raio=0.38, queda=1.2, tremor=0.5, semente=sem + 0.25), 0.26)
                for o_ in (luz, halo, nuc): surge(o_, ta, dur=0.06, t1=tb, dur1=0.12)
                ponto = lib.cilindro('arco_ponto', 0.07, 0.05, tuple(c + nrm * 0.24), mnuc, rot=(math.pi / 2, 0, 0), lados=12); ponto.visible_shadow = False
                surge(ponto, ta, dur=0.03, t1=tb, dur1=0.05)
            for i_ in range(nf):                       # cada faísca renasce várias vezes durante os cordões
                o = lib.tubo('faisca', [(0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)], r=0.03, mat=mf); o['anim'] = 1; o.visible_shadow = False
                vidas = []
                for (ta, tb) in cordoes:
                    t_ = ta + rnd.uniform(0.0, 0.25)
                    while t_ < tb - 0.05:
                        v0 = nrm * rnd.uniform(1.2, 4.8) + Vector((rnd.uniform(-3.2, 3.2), 0, rnd.uniform(-1.2, 3.6)))
                        vida = rnd.uniform(0.16, 0.55); vidas.append((t_, vida, v0)); t_ += vida + rnd.uniform(0.02, 0.35)
                faiscas.append((o, c + nrm * 0.26, vidas))
        GV = Vector((0, 0, -9.81))
        def anim_faiscas(g):
            for (o, p0, vidas) in faiscas:
                viva = next(((t_, v0) for (t_, vd, v0) in vidas if t_ <= g < t_ + vd), None)
                if viva is None: o.scale = (1e-4, 1e-4, 1e-4); o.location = p0; continue
                tau = g - viva[0]; vel = viva[1] + GV * tau
                o.location = p0 + viva[1] * tau + 0.5 * GV * tau * tau
                o.rotation_euler = vel.to_track_quat('X', 'Z').to_euler()
                o.scale = (max(0.12, vel.length * 0.045), 1.0, 1.0)            # rastro ~ velocidade × obturador (borrão de movimento)
        foco_macro = focos[0][0]
        def tguind(g): return float(np.interp(g, [15.10, 20.70, 21.70, 23.60, 31.0], [5.60, 11.50, 12.50, 14.40, 15.0]))
        def painel_z(tc):
            if tc < 11.5: return lerp(13.0, 1.2, suave((tc - 5.6) / 5.9))
            if tc < 12.5: return lerp(1.2, 0.0, suave5((tc - 11.5) / 1.0))
            return 0.0
        xg = ctx['xg']; foco = foco_macro
        def alvo_3a(g): return V(73.5, 14.5, 16.5 + 3.0 + max(0.0, painel_z(tguind(g)) - 3.0) * 0.30)
        P = [(15.10, [(15.10, (236, 142, 96), (34, 0, 6), 24), (17.20, (198, 104, 66), (52, 2, 10), 24)]),                       # 8 aérea
             (17.20, [(17.20, (xg + 24, 34, 3.5), (xg, 9, 40), 20), (19.00, (xg + 20, 31, 4.5), (xg, 9, 34), 20)]),                # 9 carro e guincho (contra-plongée)
             (19.00, [(19.00, (101, 39, 15), alvo_3a, 26), (21.40, (98, 36, 19), alvo_3a, 26)]),                                     # 10 chapa desce (aprovado)
             (21.40, [(21.40, (97, 35, 25), (73, 14.5, 16.5), 30), (23.80, (94.2, 33.3, 23.6), (73.4, 14.5, 15.8), 30)]),          # 11 encaixe (aprovado)
             (23.80, [(23.80, tuple(foco + V(8.0, 8.5, 2.4)), tuple(foco + V(-1.0, 0, 0.6)), 30), (25.30, tuple(foco + V(6.2, 6.8, 1.8)), tuple(foco + V(-1.0, 0, 0.4)), 32)]),  # 12 macro solda
             (25.30, [(25.30, (70, 41, 23), (52, 0, 9), 22), (27.00, (76, 38, 20), (56, 0, 9), 22)]),                             # 13 laterais
             (27.00, [(27.00, (120, 34, 3.0), (88, 0, 12), 22), (28.50, (114, 30, 4.0), (86, 0, 12), 22)]),                         # 14 proa, de baixo
             (28.50, [(28.50, (175, 138, 82), (10, 0, 8), 24), (30.30, (166, 128, 74), (10, 0, 8), 24)])]                           # 15 geral heroico
        def anim(g):
            posicionar(tguind(g)); anim_faiscas(g); camera_planos(cam, P, g)
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
        surge(quad('d_cel_f', yc - 1.3, yc + 1.3, 0.4, 1.6, am), 35.9 + 0.05 * (yc + 12.6), dur=0.3, t1=37.6, dur1=0.5)
    for s_ in (-1, 1):
        for (za, zb) in ((2.6, 6.0), (6.45, 9.85), (10.3, 13.7), (14.15, 17.0)):
            surge(quad('d_cel_l', s_ * 15.0 - 0.65, s_ * 15.0 + 0.65, za, zb, am), 36.2 + 0.12 * za, dur=0.3, t1=37.6, dur1=0.5)
    ar_v = lib.caixa('ar_porao', (XC + 8.9, 24.6, navio.PONTAL - 2.6), ((XC - 9.9) / 2 + 0.05, 0, Z0 + 2.3 + (navio.PONTAL - 2.6) / 2),
                     lib.mat_fantasma('ar_interno', '#e6f6ff', alfa=0.17, brilho=1.15))
    ar_v.visible_shadow = False; surge(ar_v, 39.35, dur=0.7)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    rot = Rotulos()
    rot.add('Corte ilustrativo', (XC, -14.0, Z0 + navio.PONTAL + 0.5), 33.9, 41.4, dx=0.05, dy=-0.07)
    rot.add('Compartimentos', (XC, -15.0, Z0 + 8.0), 35.9, 37.2, dx=0.06, dy=0.06)
    rot.add('Ar: espaço interno seco', (XC, 0.0, Z0 + 9.5), 39.2, 41.4, dx=0.04, dy=0.08)
    zf = Z0
    P = [(30.30, [(30.30, (150, -132, 52), (6, 0, 9), 26), (32.60, (112, -102, 40), (6, 0, 9), 26)]),                         # 16 casco pronto
         (32.60, [(32.60, (64, -74, 19), (22, 0, 9), 24), (35.30, (54, -64, 17), (14, 0, 9), 24)]),                              # 17 a proa se afasta
         (35.30, [(35.30, (40, -8, zf + 9), (XC - 4, 0, zf + 8), 24), (37.20, (36, -5, zf + 9), (XC - 4, 0, zf + 8), 24)]),       # 18 compartimentos
         (37.20, [(37.20, (XC - 1.5, -7.0, zf + 3.2), (XC - 9, 4, zf + 13), 18), (39.20, (XC - 1.0, -5.5, zf + 2.8), (XC - 9, 2, zf + 14), 18)]),  # 19 dentro do porão
         (39.20, [(39.20, (XC + 6, -9, zf + 9), (-4, 0, zf + 8), 22), (41.55, (34, -24, zf + 19), (-4, 0, zf + 8), 22)])]          # 20 ar seco, recuo
    def anim(g):
        frente.location.x = 70.0 * suave5((g - 33.0) / 1.9)
        camera_planos(cam, P, g)
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
    lib.caixa('parede', (X1 - X0 + 12, 6.0, 16.0 + 3.0), ((X0 + X1) / 2, YD + 3.0, (Z_PISO + 3.0) / 2), mc)
    # parede próxima: some durante o corte ilustrativo (44,55–47,0 s) para mostrar quilha × picadeiros debaixo d'água
    pa = lib.caixa('parede_prox_a', (X1 - X0 + 12, 6.0, 16.0 + 3.0), ((X0 + X1) / 2, -(YD + 3.0), (Z_PISO + 3.0) / 2), mc); surge(pa, -100.0, dur=0.01, t1=44.55, dur1=0.01)
    pb = lib.caixa('parede_prox_b', (X1 - X0 + 12, 6.0, 16.0 + 3.0), ((X0 + X1) / 2, -(YD + 3.0), (Z_PISO + 3.0) / 2), mc); surge(pb, 47.0, dur=0.01)
    lib.caixa('cabeceira', (6.0, 2 * YD + 12, 19.0), (X0 - 3.0, 0, (Z_PISO + 3.0) / 2), mc)
    lib.caixa('cais_lado', (900, 300, 2.0), (0, YD + 6.0 + 150, 2.0), mcp)
    ga = lib.caixa('cais_prox_a', (900, 300, 2.0), (0, -(YD + 6.0 + 150), 2.0), mcp); surge(ga, -100.0, dur=0.01, t1=44.55, dur1=0.01)
    gb = lib.caixa('cais_prox_b', (900, 300, 2.0), (0, -(YD + 6.0 + 150), 2.0), mcp); surge(gb, 47.0, dur=0.01)
    lib.caixa('solo', (X1 - X0 + 40, 2 * YD + 40, 46.0), ((X0 + X1) / 2, 0, Z_PISO - 2.0 - 23.0), lib.mat_concreto('solo', (112, 98, 80), escala=0.08))
    lib.caixa('cais_fundo', (300, 2 * YD + 12, 2.0), (X0 - 6.0 - 150, 0, 2.0), mcp)
    # comporta (caixão flutuante) com aberturas de alagamento e o mar do lado de fora
    mporta = lib.mat_pintura('comporta', '#5a6470', rug=0.5, metal=0.2)
    lib.caixa('comporta', (4.0, 2 * YD, 16.4), (X1 + 2.0, 0, Z_PISO + 8.2), mporta, bisel=0.2)
    mam = lib.mat_pintura('amarelo', '#f3b544', rug=0.42)
    lib.caixa('passarela_comp', (4.4, 2 * YD + 2, 0.6), (X1 + 2.0, 0, Z_PISO + 16.7), mam)
    magua = lib.mat_agua('agua_dique', espalha=0.0, rug=0.05, **dict(AGUA_MAR, densidade=0.16))   # água de dique: mais turva (lê-se o nível no corte)
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
        lib.caixa('picad_m', (1.6, 2.4, 0.3), (x, 0, Z_PISO + h + 0.15), lib.mat_emissivo('picad_topo', '#f3b544', 1.2), bisel=0.03)
    raiz, _, _ = navio_completo(0.0, com_carga=False); raiz.location.z = Z_QUILHA0
    # jatos de entrada pelas aberturas da comporta (só enquanto o nível de dentro está abaixo do de fora)
    mj = lib.mat_fantasma('jato_dique', '#eef9ff', alfa=0.55, brilho=1.4)
    for yy in (-16, -6, 6, 16):
        j = lib.malha('jato', [(X1, yy - 1.2, Z_PISO + 2.5), (X1, yy + 1.2, Z_PISO + 2.5), (X1 - 9, yy + 2.2, Z_PISO + 0.3), (X1 - 9, yy - 2.2, Z_PISO + 0.3)],
                      [(0, 1, 2, 3)], mj)
        surge(j, 41.7, dur=0.3, t1=43.6, dur1=0.6)
    def nivel(g): return float(np.interp(g, [41.55, 42.25, 46.10, 47.00, 48.00], [Z_PISO + 0.15, Z_QUILHA0, Z_QUILHA0 + T_EQ, Z_QUILHA0 + T_EQ + 2.5, 0.0]))
    def quilha_z(g): return max(Z_QUILHA0, nivel(g) - T_EQ)          # apoiado até flutuar; depois acompanha o nível
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    xm = 91.0; yb = -navio.meia_boca(xm, 8.0)
    def anim(g):
        L = nivel(g); adq.scale = (1, 1, max(0.01, (L - Z_PISO) / H0)); raiz.location.z = quilha_z(g)
        if g < 43.2:            # 21 comporta aberta, jatos entrando (geral alto)
            p, a, l = trilha([(41.55, (150, -128, 98), (40, 0, -8), 24), (43.2, (138, -112, 84), (52, 0, -8), 24)], g)
        elif g < 44.55:         # 22 rente à água, subindo com o nível junto aos picadeiros da proa
            p = Vector((104 - 2.0 * (g - 43.2), -21.5, L + 1.4)); a = Vector((80, 0, L - 2.0)); l = 22
        elif g < 47.0:          # 23 corte ilustrativo: a quilha deixa os picadeiros e acompanha o nível
            k = suave((g - 44.55) / 2.45); p = Vector((60, -46, -9.5)).lerp(Vector((58, -42, -9.2)), k); a = Vector((54, 0, -10.6)); l = 40
        else:                   # 24 marcas de calado: linha d'água parada em 8M enquanto o dique enche
            alvo = Vector((xm + 0.3, yb, L + 0.2)); p = alvo + Vector((-4.5, -6.0, 1.0)); a = alvo; l = 33
        camera_em(cam, p, a, l)
    rot = Rotulos()
    rot.add('Corte ilustrativo', (50, -27, 2.0), 44.7, 46.9, dx=0.04, dy=-0.06)
    rot.add('Picadeiros', (50, 0, Z_PISO + 1.0), 44.8, 46.3, dx=0.06, dy=0.07)
    rot.add('Começa a flutuar', lambda g: Vector((50, -14, quilha_z(g) + 1.0)), 46.15, 46.95, dx=0.05, dy=-0.07)
    rot.add('Calado: 8 m', lambda g: Vector((xm, yb, quilha_z(g) + T_EQ)), 47.05, 48.0, dx=-0.10, dy=-0.06)
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
    """Sequência de descobertas (planos 25–32 da decupagem): mergulho → mapa de pressão no casco 3D submerso (cor ∝
    profundidade) → setas no contorno da seção, maiores com a profundidade → pares horizontais se anulam; no bojo fica
    só a componente vertical → TODAS as componentes verticais (fundo e bojo) se somam no empuxo, em B → o volume submerso
    se enche de ciano (medida) → peso da água deslocada = empuxo → peso do navio = empuxo (equilíbrio)."""
    XC, T, raiz, solido, KB = cena_secao()
    rot = Rotulos(); xs = XC + 0.9; zB = KB - T
    # mapa de pressão: casca do volume submerso pintada em faixas por profundidade (clara na superfície, escura no fundo)
    # REFINAMENTO: evolução contínua (nada some de uma vez). Setas e mapa desbotam por opacidade (materiais fade=True):
    # pressões no contorno → os pares laterais se empurram e se anulam (deslizam um para o outro e desbotam) → no bojo a seta
    # oblíqua dá lugar à sua componente vertical (fusão cruzada) → todas as verticais convergem para B e se fundem no empuxo.
    mapa_m = lib.mat_faixas_z('mapa_pressao', [(1.4, '#0b3366'), (2.8, '#174a8c'), (4.2, '#2b67ad'), (5.6, '#4a8cc8'), (6.8, '#79b3e0'), (1e9, '#b9e2f7')], rug=0.5, fade=True)
    mapa = volume_submerso('mapa_pressao', T, x0=-70.0, x1=XC - 0.08, mat=mapa_m, infla=0.10); mapa.parent = raiz
    surge(mapa, 50.75, dur=0.5, t1=59.0, dur1=1.3)
    def seta(nome, ponto, n_out, L, cor, t0, t1, dur1=0.8, pai=None):
        o = lib.seta3d(nome, tuple(Vector(ponto) + n_out * (L + 0.25)), tuple(-n_out), L, r=0.5, mat=lib.mat_emissivo('p_' + nome, cor, 2.0, fade=True), cabeca=2.3)
        o.visible_shadow = False
        if pai is not None: o.parent = pai
        surge(o, t0, dur=0.45, t1=t1, dur1=dur1); return o
    k = 0.55                                          # comprimento ∝ profundidade (m de seta por m de profundidade)
    lados = {}
    for s_ in (1, -1):                                # costado: rasa e funda (componentes só horizontais: se anulam em pares)
        anc = bpy.data.objects.new(f'lat_anc{s_}', None); lib.ligar(anc); anc['anim'] = 1; lados[s_] = anc
        for (prof, cor, t0) in ((2.0, '#cdeefa', 51.0), (5.0, '#7fd3f5', 51.7)):
            b = navio.meia_boca(XC, T - prof); seta(f'lat{s_}_{prof}', (xs, s_ * (b + 0.1), -prof), Vector((0, s_, 0)), k * prof, cor, t0, 58.35, 0.85, pai=anc)
    r = navio.RAIO_BOJO; c45 = math.sqrt(0.5)
    yb_ = navio.meia_boca(XC, 6.0) - r + r * c45; zb_ = r - r * c45; prof_b = T - zb_
    for s_ in (1, -1):                                # bojo a 45°: dá lugar à componente vertical (fusão cruzada 58,6–59,5)
        seta(f'bojo{s_}', (xs, s_ * (yb_ + 0.1), zb_ - T - 0.1), Vector((0, s_ * c45, -c45)), k * prof_b, '#4fc0f0', 52.4, 58.6, 0.9)
    verticais = []                                    # componentes verticais (bojo) + fundo: âncoras que convergem para B
    for (y0, L, t0, dur) in ((yb_ * 1, k * prof_b * c45, 58.6, 0.9), (-yb_, k * prof_b * c45, 58.6, 0.9), (3.5, k * T, 52.9, 0.45), (-3.5, k * T, 52.9, 0.45), (9.0, k * T, 52.9, 0.45), (-9.0, k * T, 52.9, 0.45)):
        anc = bpy.data.objects.new('vert_anc', None); lib.ligar(anc); anc['anim'] = 1
        sv = lib.seta3d('vert', (0, 0, -L - 0.25), (0, 0, 1), L, r=0.5, mat=lib.mat_emissivo('p_vert', '#2fb6ee', 2.0, fade=True), cabeca=2.3); sv.parent = anc
        sv.visible_shadow = False; surge(sv, t0, dur=dur, t1=61.25, dur1=0.75)          # desbotam enquanto o empuxo cresce
        verticais.append((anc, y0, t0, L))
    B, Wn, pB, pG, xs_, zB_, zG = _setas_forcas(XC, T, KB)
    surge(B, 61.3, dur=0.75, escala=True); surge(pB, 61.25, dur=0.4)          # cresce no lugar onde as verticais se fundem
    surge(Wn, 71.15, dur=0.6, escala=True); surge(pG, 71.05, dur=0.3)
    # peso da água deslocada: seta ciano para baixo, ao lado do empuxo, mesmo tamanho (65,8–70,8 s)
    pa = lib.seta3d('peso_agua', (xs, 3.4, zB + 4.0), (0, 0, -1), 4.0, r=1.6, mat=lib.mat_emissivo('seta_peso_agua', COR_EMPUXO, 1.8), cabeca=2.0)
    pa.visible_shadow = False; surge(pa, 67.2, dur=0.5, escala=True, t1=70.8, dur1=0.4)
    # volume deslocado se enche de baixo para cima (medida), depois a área da seção acende
    vol = volume_submerso('vol_deslocado', T, x0=-70.0, x1=XC - 0.05, infla=0.12); vol['anim'] = 1; vol.parent = raiz
    _area_deslocada(XC, T, 65.6)
    rot.add('Pressão da água', (xs, -navio.meia_boca(XC, T - 5.0) - 2.0, -5.0), 51.2, 56.4, dx=0.05, dy=0.10)
    rot.add('Laterais se anulam', lambda g: lados[1].matrix_world @ Vector((xs, navio.meia_boca(XC, T - 3.5) + 1.2, -3.5)), 57.2, 59.0, dx=-0.30, dy=-0.12)
    rot.add('Só a parte vertical sobra', (xs, 0, -T - 3.0), 59.1, 61.6, dx=0.05, dy=0.09)
    rot.add('Empuxo', (xs, 0, zB + 3.2), 62.0, 67.0, dx=0.08, dy=0.02)
    rot.add('Água deslocada', (XC, -8.0, -4.5), 64.6, 67.0, dx=0.06, dy=0.10)
    rot.add('Peso da água deslocada', (xs, 3.4, zB + 1.5), 67.4, 70.8, dx=0.06, dy=0.06)
    rot.add('Peso do navio', (xs, 0, zG - 2.0), 71.3, 74.85, dx=0.06, dy=-0.06)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    P = [(48.00, [(48.00, (XC + 34, -27, 6.5), (XC - 10, -10, 2.5), 24), (50.60, (XC + 28, -24, -5.0), (XC - 10, -8, -5.0), 24)]),          # 25 mergulho
         (50.60, [(50.60, (XC + 42, -62, -9), (XC - 50, 0, -5), 24), (53.70, (XC + 38, -56, -10), (XC - 46, 0, -5), 24)]),                     # 26 mapa de pressão
         (53.70, [(53.70, (XC + 16, -25, -0.5), (XC, -16.5, -1.0), 26), (56.60, (XC + 16, -24, -9.5), (XC, -14, -8.6), 26)]),                  # 27 mais fundo
         # ajustes finais (28–29, 31–32): 3/4 elevado quase frontal — a seção maior, o convés e o navio preenchem o topo do quadro
         (56.60, [(56.60, (XC + 52, -10, 14), (XC - 3, 0, -5), 19), (58.30, (XC + 51, -10, 14), (XC - 3, 0, -5), 19),                         # 28 compensam (setas laterais inteiras)
                  (59.60, (XC + 49, -11, 14.5), (XC - 3, 0, -5), 20.8), (62.90, (XC + 46, -11, 13), (XC - 3, 0, -4.5), 22.5)]),     # 29 empuxo: mesmo movimento, sem corte
         (63.10, [(63.10, (XC + 42, -48, -8), (XC - 40, 0, -4), 24), (65.80, (XC + 38, -44, -7), (XC - 36, 0, -4), 24)]),                       # 30 volume se enche
         (65.80, [(65.80, (XC + 44, -28, 11), (XC - 6, -1, -3), 24), (70.60, (XC + 46, -30, 12), (XC - 6, -1, -3), 24)]),                       # 31 empuxo = peso da água
         (70.60, [(70.60, (XC + 48, -31, 12), (XC - 6, -1, -2.5), 24), (74.85, (XC + 60, -36, 14), (XC - 6, -1, -2), 24)])]                    # 32 equilíbrio
    def anim(g):
        for s_, anc in lados.items():                 # os dois lados se empurram (57,3–57,9) e depois deslizam um para o outro
            emp = math.sin(math.pi * min(max((g - 57.3) / 0.6, 0.0), 1.0)) * 0.45 + suave((g - 58.35) / 0.85) * 1.6
            anc.location = (0, -s_ * emp, 0)
        for (anc, y0, t0, L) in verticais:            # convergem para B (59,8–61,6) e se fundem no empuxo
            kc = suave((g - 59.8) / 1.8)
            anc.location = Vector((xs, y0 * (1 - kc), -T)).lerp(Vector((xs, 0, zB - L * 0.2)), kc); anc.scale = (1, 1, 1)
        kv = suave((g - 63.2) / 2.3)
        vol.scale = (1, 1, max(kv, 1e-4)) if g >= 63.2 else (1e-4, 1e-4, 1e-4)
        camera_planos(cam, P, g)
    exportar_seg(pasta, 48.00, 74.85, anim, rot, extra=dict(segmento='0607', KB=KB, T=T))


def seg0607b(pasta):
    """Respiro de perspectiva no meio do empuxo (63,1–65,8 s, "Foi Arquimedes quem explicou o princípio"): o navio
    vazio INTEIRO flutuando (corte na água a 8 m do costado); o volume de água deslocada se enche da quilha à linha d'água."""
    lib.nova_cena()
    lib.ceu_estilizado(**CEU_DIA)
    T = navio.CALADO_LEVE
    raiz, _, _ = navio_completo(0.0, com_carga=False); raiz.location.z = -T
    Y0 = -navio.MEIA_BOCA - 8.0
    magua = lib.mat_agua('agua_fim', espalha=0.0, rug=0.05, **dict(AGUA_MAR, densidade=0.03))
    lib.bloco_agua('agua', -600, 600, Y0, 600, -80, magua, res=3.0, amp=0.2)
    mlonge = lib.mat_pintura('mar_longe', '#2c78a0', rug=0.1, variacao=0.06, escala_var=0.02)
    for (a0, a1, b0, b1) in ((-4000, -600, -4000, 4000), (600, 4000, -4000, 4000), (-600, 600, 600, 4000)):
        lib.bloco_agua('longe', a0, a1, b0, b1, -30, mlonge, res=400, amp=0.0, so_superficie=True)
    vol = volume_submerso('vol_desl_inteiro', T, infla=0.18); vol['anim'] = 1; vol.parent = raiz
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    rot = Rotulos(); rot.add('Água deslocada', (-20, -navio.MEIA_BOCA, -T * 0.5), 64.9, 65.8, dx=0.05, dy=0.08)
    def anim(g):
        k = suave((g - 63.25) / 2.2); vol.scale = (1, 1, max(k, 1e-4))
        p, a, l = trilha([(63.1, (150, -118, 2.0), (0, 0, -2.5), 24), (65.8, (136, -108, 1.0), (0, 0, -3.0), 24)], g); camera_em(cam, p, a, l)
    exportar_seg(pasta, 63.10, 65.80, anim, rot, extra=dict(segmento='0607b', calado=T))


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
        # REFINAMENTO · retomada do experimento da abertura: o MESMO bloco, no mesmo cais, é empurrado e cai em tempo real;
        # logo depois do impacto a velocidade da cena desce suavemente até a câmera lenta (sem saltos de posição ou de ritmo).
        _gg = np.linspace(74.85, 82.0, 4001)
        _v = np.where(_gg < 75.75, 1.0, np.where(_gg < 76.35, 1.0 - (1.0 - 0.085) * np.array([suave((x - 75.75) / 0.6) for x in _gg]), 0.085))
        _s = np.concatenate([[0.0], np.cumsum(0.5 * (_v[1:] + _v[:-1]) * np.diff(_gg))]); _s = _s - _s[-1] + 3.65
        def ts(g):
            if g <= 82.0: return float(np.interp(g, _gg, _s))
            return float(np.interp(g, [82.0, 82.12, 90.0], [3.65, 3.80, 3.85]))
        t_imp = float(np.interp(ctx['t_agua'], _s, _gg))           # instante global do impacto (ondas na superfície)
        ta_, tf_ = ctx['t_agua'], ctx['t_fundo']
        def cam_abertura(t, b):                                   # mesma câmera do plano de abertura (animatic r2), em tempo de cena
            kz = suave((t - 2.45) / (ta_ + 0.10 - 2.45)); ks = suave((t - ta_) / (tf_ + 0.25 - ta_))
            z = lerp(1.65, 0.12, kz) + lerp(0.0, -1.45, ks); y = lerp(-1.6, -0.5, suave((t - 2.4) / 1.6)); x = lerp(1.15, 1.45, suave((t - 1.0) / 3.0))
            alvo = Vector((lerp(5.5, 3.6, suave((t - 1.2) / 1.7)), 6.5, lerp(2.7, 0.0, kz)))
            alvo.z += lerp(0.0, max(b.z, -4.2) + 0.3 - alvo.z, suave((t - ta_ - 0.05) / 0.55))
            dt = t - ta_; tr = 0.05 * math.exp(-dt / 0.13) * math.sin(dt * 55) if dt > 0 else 0.0
            return Vector((x, y, z + tr)), alvo, lerp(30, 34, suave((t - 2.5) / 1.4))
        pf, _ = est(3.80); rs = random.Random(31); msed = lib.mat_fantasma('sedimento', '#c9b48a', alfa=0.55, brilho=1.0)
        for i in range(26):                                  # nuvem de sedimento levantada pelo bloco ao tocar o leito
            ang = rs.uniform(0, 2 * math.pi); rr = rs.uniform(0.9, 2.2)
            o = lib.esfera_simples('sed', rs.uniform(0.18, 0.45), msed) if hasattr(lib, 'esfera_simples') else lib.caixa('sed', (0.5, 0.5, 0.35), (0, 0, 0), msed, bisel=0.2)
            o.location = (pf.x + rr * math.cos(ang), pf.y + rr * math.sin(ang), pf.z - 0.6 + rs.uniform(0, 0.7)); o.visible_shadow = False
            surge(o, 82.12 + rs.uniform(0, 0.15), dur=0.5, escala=True, d=(-0.5 * math.cos(ang), -0.5 * math.sin(ang), -0.3), t1=83.2 + rs.uniform(0, 0.5), dur1=0.6)
        estado_p = {}
        def anim(g):
            p = posicionar(ts(g)); estado_p['p'] = p
            vis = max(suave((g - 76.3) / 0.45), 1e-4)          # as forças crescem depois que o bloco já está na água
            aw.location = p; ab.location = p; aw.scale = ab.scale = (vis, vis, vis)
            kg = suave((g - 77.6) / 1.0); vg = 1.0 if 77.6 <= g <= 82.0 else 1e-4
            gh.location = p + Vector((-1.7 * kg, 0, 0)); gh.scale = (vg, vg, vg); gh.rotation_euler = ctx['bloco'].rotation_euler
            if g < 76.4:                                   # 33 retomada: o enquadramento da abertura (cais → linha d'água → mergulho)
                pos, alvo, l = cam_abertura(ts(g), p)
            elif g < 78.6:                                 # 34 close no bloco: peso longo × empuxo curto (chega sem corte)
                pos = p + V(-1.8, -5.6, 0.2); alvo = p + V(0, -0.9, -0.6); l = 30
                kb = suave((g - 76.4) / 0.7)
                if kb < 1:
                    p0, a0, l0 = cam_abertura(ts(g), p); pos = p0.lerp(pos, kb); alvo = a0.lerp(alvo, kb); l = lerp(l0, l, kb)
            elif g < 81.5:                                 # 35 lado a lado: bloco e a água que ele desloca (mesmo tamanho)
                k = suave((g - 78.6) / 2.9); pos = p + V(-0.6, -7.4, 0.4).lerp(V(-0.9, -7.4, 0.3), k); alvo = p + V(-0.9, 0, 0); l = 28.5
                pos.y = min(pos.y, -0.9)   # correção 1:19: a câmera fica SEMPRE ≥ 0,9 m da face de corte da água (y = 0); antes chegava
                                           # a 0,1 m e o plano próximo da câmera (0,5 m) recortava a face — a água 'sumia' a partir de 79,8 s
            else:                                          # 36 do leito, olhando para cima: o bloco chega e levanta sedimento
                k = suave((g - 81.5) / 2.35); pos = V(pf.x - 3.4, 1.2, -6.3).lerp(V(pf.x - 3.0, 1.6, -6.1), k); alvo = V(pf.x, 6.5, -4.6); l = 24
            camera_em(cam, pos, alvo, l)
        # (sem rótulo de retomada: o mesmo cais, o mesmo bloco e o mesmo enquadramento da abertura bastam)
        rot.add('Peso', lambda g: estado_p.get('p', V(0, 0, 0)) + Vector((0, -0.9, -2.0)), 76.4, 83.6, dx=0.07, dy=0.04)
        rot.add('Empuxo', lambda g: estado_p.get('p', V(0, 0, 0)) + Vector((0, -0.9, 0.35)), 76.6, 83.6, dx=0.07, dy=-0.05)
        rot.add('Água deslocada', lambda g: estado_p.get("p", V(0, 0, 0)) + Vector((-1.7, 0, 0.8)), 78.3, 82.0, dx=-0.05, dy=-0.07)
        exportar_seg(pasta, 74.85, 83.85, anim, rot, extra=dict(segmento='08a', ondas=[dict(x=ctx['x_imp'], y=ctx['by'], t0=t_imp)]))
    A.plano1(pasta, exportador=exportador)


# =====================================================================================  SEG08b · experimento: mesma massa, volumes diferentes (83,85–94,55)
def cena_secao_movel(T):
    """Seção a meia-nau com o casco MÓVEL: a água não é furada (booleana); um oclusor (sólido do casco até x = XC)
    impede a água de aparecer dentro do casco, e o casco pode entrar na água."""
    lib.nova_cena(amostras=128)
    lib.ceu_estilizado(sol_elev=50, sol_rot=120, sol_forca=4.4, nuvens=0.4, zenite='#3a7bd0', meio='#8cc2ee')
    XC = 3.2
    raiz, solido = quadros.navio_em_corte(XC, T, carga_porao=False, porao_aberto=False, filtro_conves=lambda k, j, n: False, esp_linha=0.0)
    raiz['anim'] = 1
    oc = volume_submerso('oclusor_secao', navio.PONTAL - 0.05, x0=navio.POPA + 0.5, x1=XC + 0.05, mat=lib.mat_pintura('oc', '#000000'), infla=0.02)
    oclusor(oc); oc.parent = raiz; oc.location.z = 0.0
    magua = lib.mat_agua('agua_prof', absorcao=(0.30, 0.74, 0.84), densidade=0.012, espalha=0.0, marola=0.4, escala_marola=0.25)
    lib.bloco_agua('agua', -260.0, XC, -150, 150, -160, magua, res=2.0, amp=0.3, escala=1.0)
    mlonge = lib.mat_pintura('mar_longe', '#2c78a0', rug=0.1, variacao=0.06, escala_var=0.02)
    for (a0, a1, b0, b1) in ((-1500, -260.0, -1500, 1500), (-260.0, XC, 150, 1500), (-260.0, XC, -1500, -150)):
        lib.bloco_agua('longe', a0, a1, b0, b1, -30, mlonge, res=60, amp=0.0, so_superficie=True)
    return XC, raiz


def seg08b(pasta):
    """Experimento (planos 37–40): bloco maciço de aço com a MESMA MASSA do navio vazio (39.657 t → 5.052 m³ → aresta
    17,2 m) e o casco, lado a lado acima da água. Soltos juntos: o bloco desloca só o próprio volume (empuxo = 13% do
    peso) e afunda; o casco afunda até 8,0 m, onde desloca 38.690 m³ (empuxo = peso), e para (arfagem amortecida)."""
    T = navio.CALADO_LEVE
    XC, raiz = cena_secao_movel(T)
    rot = Rotulos()
    _, _, KB = hidro.carena(T)
    D = hidro.RHO * hidro.carena(T)[0]; a = (D / 7.85) ** (1 / 3)
    yc = -(navio.MEIA_BOCA + 5.0 + a / 2); xc = XC - a / 2          # 5 m entre os dois (era 7): par mais compacto no quadro vertical
    cubo = bpy.data.objects.new('cubo_aco', None); lib.ligar(cubo); cubo['anim'] = 1
    lib.caixa('cubo_aco_m', (a, a, a), (0, 0, 0), lib.mat_aco('aco_bloco', (158, 161, 166), rug=0.3, escovado=False, macico=True, manchas=0.07, escala_var=0.9), bisel=0.12).parent = cubo
    mw = lib.mat_emissivo('seta_peso', COR_PESO, 2.0); me = lib.mat_emissivo('seta_empuxo_c', '#a6f0ff', 2.6)
    L = 4.0
    wc = lib.seta3d('peso_cubo', (a / 2 + 0.9, 0, 0), (0, 0, -1), L, r=1.6, mat=mw, cabeca=2.0); wc.parent = cubo
    bc = lib.seta3d('empuxo_cubo', (a / 2 + 0.9, 0, 0), (0, 0, 1), L * 1025 / 7850, r=1.6, mat=me, cabeca=1.2); bc.parent = cubo
    for o in (wc, bc): o.visible_shadow = False
    surge(wc, 84.2, dur=0.5, escala=True); surge(bc, 86.6, dur=0.4, escala=True)
    xs = XC + 0.9; zB, zG = KB, 12.5                               # em coordenadas do NAVIO (as setas vão presas ao casco)
    Bh = lib.seta3d('empuxo', (xs, 0, zB), (0, 0, 1), L, r=1.6, mat=me, cabeca=2.0)
    Wh = lib.seta3d('peso', (xs, 0, zG), (0, 0, -1), L, r=1.6, mat=mw, cabeca=2.0)
    for o in (Bh, Wh): o.visible_shadow = False; o.parent = raiz
    surge(Wh, 84.2, dur=0.5, escala=True); surge(Bh, 87.9, dur=0.5, escala=True)
    ar = lib.malha('ar_casco', [(XC + 0.09, -12.4, 2.3), (XC + 0.09, 12.4, 2.3), (XC + 0.09, 12.4, navio.PONTAL - 0.8), (XC + 0.09, -12.4, navio.PONTAL - 0.8)],
                   [(0, 1, 2, 3)], lib.mat_fantasma('ar_interno', '#eef9ff', alfa=0.40, brilho=1.3))
    ar.visible_shadow = False; ar.parent = raiz; surge(ar, 88.5, dur=0.6)
    vol = volume_submerso('vol_deslocado', T, x0=-70.0, x1=XC - 0.05, infla=0.12); vol.parent = raiz; surge(vol, 89.9, dur=0.8)
    Z0 = 2.0; TS = 85.6                                             # ambos suspensos com a base 2 m acima d'água; soltos em 85,6 s
    def quilha(g):                                                  # casco: desce e oscila até o calado de equilíbrio (8,0 m)
        if g < TS: return Z0
        t = g - TS; w = 2 * math.pi / 3.2; z_ = 0.32; wd = w * math.sqrt(1 - z_ * z_)
        return -T + (Z0 + T) * math.exp(-z_ * w * t) * (math.cos(wd * t) + z_ / math.sqrt(1 - z_ * z_) * math.sin(wd * t))
    def base_cubo(g):                                               # bloco: queda livre até a água, depois afunda acelerando (~8 m/s²)
        if g < TS: return Z0
        t = g - TS; t_ag = math.sqrt(2 * Z0 / G)
        if t < t_ag: return Z0 - 0.5 * G * t * t
        v0 = G * t_ag; tt = t - t_ag; return -v0 * tt - 0.5 * 7.9 * tt * tt
    rot.add('Mesma massa do navio vazio', lambda g: Vector((XC, yc, base_cubo(g) + a)), 84.0, 86.6, dx=0.03, dy=-0.09)
    rot.add('Aço maciço: 17 m', lambda g: Vector((XC, yc, base_cubo(g) + a / 2)), 84.5, 87.0, dx=0.05, dy=0.08)
    rot.add('Navio vazio', lambda g: Vector((XC, 14.0, quilha(g) + navio.PONTAL - 2.0)), 84.0, 86.6, dx=0.05, dy=0.02)
    rot.add('Ar', lambda g: Vector((XC, 4.0, quilha(g) + 9.0)), 88.7, 89.7, dx=0.07, dy=0.09)
    rot.add('Água deslocada', (XC, -8.0, -4.5), 90.2, 94.5, dx=0.06, dy=0.10)
    rot.add('Empuxo = peso', lambda g: Vector((xs, 0, quilha(g) + zB + 3.2)), 91.0, 94.5, dx=0.06, dy=0.04)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    # ajustes finais: 3/4 elevado e próximo (os dois grandes no quadro; o casco mostra o comprimento = volume), um só
    # movimento que acompanha a queda simultânea; depois o corte frontal (ar) e a síntese em 3/4 rente à linha d'água
    P = [(83.85, [(83.85, (XC + 59, -48, 21), (XC - 9, -16.5, 6.5), 26), (85.60, (XC + 55, -46, 19), (XC - 9, -16.5, 5.5), 26),   # 37 suspensos
                  (86.40, (XC + 55, -46, 16), (XC - 9, -16, 1.0), 26), (88.60, (XC + 51, -44, 6), (XC - 9, -15, -8.5), 24)]),   # 38 soltos: bloco afunda, casco para
         (88.60, [(88.60, (XC + 41, -4, 1), (XC - 3, -1, -0.5), 22), (89.70, (XC + 39, -4, 1), (XC - 3, -1, -0.5), 22)]),        # 39 ar
         (89.70, [(89.70, (XC + 38, -24, -2), (XC - 11, -3, -3.5), 25), (94.55, (XC + 43, -27, 0), (XC - 11, -3, -3.0), 25)])]   # 40 síntese
    def anim(g):
        raiz.location = (0, 0, quilha(g))
        sc = 1.0 if 83.95 <= g <= 89.0 else 1e-4; k = suave((g - 83.95) / 0.5)
        cubo.location = (xc, yc, base_cubo(g) + a / 2); cubo.scale = (sc * max(k, 1e-3),) * 3
        camera_planos(cam, P, g)
    t_ag = TS + math.sqrt(2 * Z0 / G)
    exportar_seg(pasta, 83.85, 94.55, anim, rot, extra=dict(segmento='08b', aresta_cubo=a, massa_t=D, ondas=[dict(x=xc, y=yc, t0=t_ag), dict(x=XC - 30, y=0.0, t0=t_ag)]))


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
    def pouso(i): return (P['raiz'].matrix_world @ P['gru'][i]['Mloc']).translation
    def anim(g):
        _posicionar_porto(P, g); barras(g, 1.0 if g >= 112.6 else 1e-4)
        if g < 97.6: p, a, l = trilha([(94.55, (176, -160, 74), (0, -20, 6), 24), (97.6, (150, -136, 60), (4, -20, 6), 24)], g)       # 41 vazio
        elif g < 100.1: p, a, l = trilha([(97.6, (xa + 20, -40, 13), (xa - 2, 14, 17), 26), (98.9, (xa + 20, -40, 13), (xa - 2, 16, 26), 26),   # 42 do convés do navio:
                                          (99.6, (xa + 20, -41, 13), (xa - 1, 2, 28), 26), (100.1, (xa + 20, -42, 14), (xa - 1, -12, 27), 26)], g)  # o contêiner sobe e vem sobre o navio
        elif g < 101.9:                                                                                                                 # 43 pouso do 1º (do convés, baía vizinha)
            q = pouso(0); p, a, l = trilha([(100.1, tuple(q + V(-17, -13, 10.0)), tuple(q + V(0, 0, 4.5)), 30), (101.9, tuple(q + V(-15, -12, 8.5)), tuple(q + V(0, 0, 1.6)), 30)], g)
        elif g < 103.2:                                                                                                                 # 44 pouso do 2º
            q = pouso(1); p, a, l = trilha([(101.9, tuple(q + V(-17, -14, 10.0)), tuple(q + V(0, 0, 4.5)), 30), (103.2, tuple(q + V(-15, -13, 8.5)), tuple(q + V(0, 0, 1.6)), 30)], g)
        elif g < 104.9:                                                                                                                 # 45 pouso do 3º (do lado da proa)
            q = pouso(2); p, a, l = trilha([(103.2, tuple(q + V(17, -14, 10.0)), tuple(q + V(0, 0, 4.5)), 30), (104.9, tuple(q + V(15, -13, 8.5)), tuple(q + V(0, 0, 1.6)), 30)], g)
        elif g < 109.6: p, a, l = trilha(K4, g)                                                                                         # 46 linha d'água
        elif g < 112.6:                                                                                                                 # 47 zenital: o convés enche
            k = suave((g - 109.6) / 3.0); cam.location = (2 * k, YN, lerp(190, 176, k)); cam.rotation_euler = (0, 0, -math.pi / 2); cam.data.lens = 24
            return
        else: p, a, l = trilha([(112.6, (112, -104, 22), (34, -20, 7), 24), (117.2, (104, -96, 18), (34, -20, 6), 24)], g)             # 48 equilíbrio
        camera_em(cam, p, a, l)
    rot.add('Navio vazio', (0, YN, 18 - navio.CALADO_LEVE + 2), 95.0, 97.4, dx=0.06, dy=-0.06)
    rot.add('Linha d\'água', (xm + 0.6, yb, 0.0), 105.4, 109.4, dx=-0.08, dy=0.07)
    rot.add('Peso', (67.0, YN - navio.MEIA_BOCA - 9.0, 13.0), 112.8, 117.2, dx=0.05, dy=-0.04)
    rot.add('Empuxo', (62.0, YN - navio.MEIA_BOCA - 9.0, 8.0), 112.8, 117.2, dx=-0.08, dy=0.04)
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
    def anim(g):
        _posicionar_porto(P, g); T = P['Tf'](g)
        k = suave((g - 119.0) / 2.1)
        cota.location = (0, yc, -T); cota.scale = (1, 1, max(1e-3, T * k)) if g >= 118.9 else (1e-4, 1e-4, 1e-4)
        if g < 119.0:            # 49 corte ilustrativo a meia-nau (geral)
            p, a, l = trilha([(117.2, (40, YN - 80, 4), (0, yc, -3), 26), (119.0, (34, YN - 72, 2), (0, yc, -3.5), 26)], g)
        elif g < 121.2:          # 50 a câmera acompanha a ponta da cota, da quilha à superfície
            zt = -T + T * k; p = Vector((14, yc - 26, zt + 0.5)); a = Vector((0, yc, zt)); l = 30
        else:                    # 51 cota inteira: "calado"
            p, a, l = trilha([(121.2, (24, YN - 58, -2.0), (0, yc, -4.6), 28), (123.65, (20, YN - 52, -2.4), (0, yc, -4.6), 28)], g)
        camera_em(cam, p, a, l)
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
            k = suave((g - 123.65) / 1.75); alvo = pmundo(xm, 8.4)
            pos = Vector((40, YN - 30, 1.2)).lerp(alvo + Vector((-2.0, -2.7, 0.25)), k); a = Vector((60, YN - 14, 2)).lerp(alvo, k); l = lerp(26, 32, k)
        elif g < 127.6:    # "algumas indicam o calado": sobe pela escala até a linha d'água
            k = suave((g - 125.8) / 1.8); zl = lerp(8.4, 10.2, k); alvo = pmundo(xm, zl)      # close: algarismos legíveis no celular
            pos = alvo + Vector((-2.0 + 0.5 * k, -2.7 + 0.2 * k, 0.25)); a = alvo; l = 32
        elif g < 128.8:    # "outras…": desliza rente ao costado até a meia-nau
            k = suave5((g - 127.6) / 1.2); x = lerp(xm - 3.8, -5.9, k); zl = lerp(10.2, zs['S'] + 0.05, k)
            alvo = pmundo(x + 3.0 - 0.95 * k * 3.0 + 0.0, zl); alvo.x = lerp(xm, -3.85, k) + 0.2 * k
            pos = pmundo(x, zl) + Vector((0, -4.5 + 0.5 * k, 0.4 - 0.1 * k)); a = alvo; l = 34
        else:              # marca de linha de carga: aproxima e acompanha cada linha que acende
            k = suave((g - 128.8) / 1.6); k2 = suave((g - 130.3) / 1.0)
            zc = zs['S'] + 0.1; alvo = pmundo(-3.74, zc + 0.35 * (z_linha(g) - zc))        # a marca inteira (disco, TF…W) no quadro
            pos = alvo + Vector((-1.7, -5.0, 0.3)).lerp(Vector((-1.0, -3.4, 0.15)), k).lerp(Vector((-0.45, -2.95, 0.1)), k2); a = alvo; l = 30
        pos.z = max(pos.z, 0.55)                                              # nunca abaixo da superfície (cena sem corte)
        camera_em(cam, pos, a, l)
    rot.add('Marcas de calado', lambda g: pmundo(xm, 10.6), 125.9, 127.9, dx=-0.42, dy=0.02)
    rot.add('Marca de linha de carga', lambda g: pmundo(-4.1, zs['TF'] + 0.1), 128.3, 133.9, dx=0.0, dy=-0.07)
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
    surge(rasgo, 136.0, dur=0.2); surge(jato, 136.9, dur=0.3, t1=145.6, dur1=0.8)
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
        M = raiz.matrix_world
        if g < 139.4:            # 57 dentro do porão: jato pelo rombo, água espalhando no piso
            p = M @ Vector((xcm - 3.0, -15.0, 7.5)); a = M @ Vector((xcm + 4.0, ybr - 1.0, 5.2)); l = 24
        elif g < 141.8:          # 58 o nível sobe na parede do porão
            p = M @ Vector((xcm - 6.0, -13.0, lv + 2.0)); a = M @ Vector((xcm + 2.0, bhi - 1.0, lv)); l = 24
        else:
            K = [(141.8, (26, -150, 6), (22, 30, -1), 32), (144.6, (24, -136, 4), (23, 30, -1), 32),       # 59 o porão enche; o navio afunda
                 # 60 calado e trim, legível no vertical: perto da PROA a linha d'água antiga (amarela) fica 2,6 m abaixo do
                 # nível do mar (branca); perto da POPA as duas quase coincidem — o ângulo real (0,71°), sem exagero
                 (144.61, (88, -62, 0.5), (88, 40, -1.2), 30), (146.2, (86, -58, 0.4), (88, 40, -1.2), 30),          # 60a proa
                 (146.21, (-70, -50, 0.0), (-70, 40, -2.2), 34), (147.8, (-68, -47, 0.0), (-70, 40, -2.2), 34),      # 60b popa (sem a superestrutura no quadro)
                 (147.81, (110, -190, 38), (0, 0, -3), 26), (150.6, (104, -180, 35), (0, 0, -3), 26),                # 61 hipótese grave (3/4 elevado)
                 (150.61, (34, -64, 4), (24, 20, 0), 30), (152.6, (32, -60, 4), (24, 20, 0), 30),          # 62a anteparas (close)
                 (152.61, (24, -150, 4), (23, 30, -1), 32), (154.6, (24, -136, 3), (23, 30, -1), 32)]      # 62b geral
            cortes = [141.8, 144.6, 146.2, 147.8, 150.6, 152.6]
            i = max(j for j in range(len(cortes)) if cortes[j] <= g + 1e-6)
            p, a, l = trilha(K[2 * i:2 * i + 2], g)
        camera_em(cam, p, a, l)
    rot = Rotulos()
    rot.add('Corte ilustrativo', lambda g: raiz.matrix_world @ Vector((xcm - 6, 0, 17.0)), 137.1, 139.3, dx=0.05, dy=-0.06)
    rot.add('Duplo fundo (estanque)', lambda g: raiz.matrix_world @ Vector((xcm - 30, 0, 1.1)), 141.9, 143.3, dx=0.05, dy=0.08)
    rot.add('Tanque lateral (estanque)', lambda g: raiz.matrix_world @ Vector((xcm - 8, navio.meia_boca(xcm - 8, 6.0) - 1.2, 6.0)), 139.7, 143.6, dx=-0.05, dy=0.08)
    rot.add('Linha d\'água antes', lambda g: raiz.matrix_world @ Vector((8, -0.35, T0)), 143.4, 144.55, dx=0.04, dy=0.07)
    rot.add('Nível do mar', (30, -0.6, 0.02), 143.4, 144.55, dx=0.04, dy=-0.07)
    rot.add('Linha d\'água antes', lambda g: raiz.matrix_world @ Vector((84, -0.35, T0)), 144.75, 145.45, dx=-0.30, dy=0.09)   # plano da proa
    rot.add('Nível do mar', (84, -0.6, 0.02), 144.75, 145.45, dx=-0.30, dy=-0.09)
    dproa = R['proa'] - T0; dpopa = R['popa'] - T0
    rot.add(f'Proa: +{dproa:.1f} m'.replace('.', ','), lambda g: raiz.matrix_world @ Vector((88, -0.35, T0)), 145.5, 146.1, dx=0.06, dy=0.10)
    rot.add(f'Popa: +{dpopa:.1f} m'.replace('.', ','), lambda g: raiz.matrix_world @ Vector((-86, -0.35, T0)), 146.35, 147.75, dx=0.06, dy=0.10)
    rot.add('Hipótese: sem divisórias', (-40, 0, -4), 148.0, 150.6, dx=0.04, dy=0.10)
    rot.add('Divisórias estanques', lambda g: raiz.matrix_world @ Vector((COMP_AVARIA[1], 0, 12.0)), 151.2, 154.6, dx=0.05, dy=-0.07)
    exportar_seg(pasta, 137.00, 154.60, anim, rot, extra=dict(segmento='12', hidrostatica=R, compartimento=COMP_AVARIA))
    print('AVARIA', json.dumps({k: round(v, 3) for k, v in R.items()}))


def seg12x(pasta):
    """Plano 56: exterior. O navio carregado em mar aberto; rombo no costado ~2 m abaixo da linha d'água, a água entra
    (bolhas e partículas sendo sugadas). Mesma posição e altura do rombo do corte (SEG12)."""
    lib.nova_cena()
    lib.ceu_estilizado(**CEU_DIA)
    raiz, conts, _ = navio_completo(0.0)
    T0 = calado_com(len(conts)); raiz.location.z = -T0
    mar_aberto(ext=600)
    ca, cb = COMP_AVARIA; xcm = 0.5 * (ca + cb); z_r = 7.4; xr = xcm + 4.0
    yr = -(navio.meia_boca(xr, z_r) + 0.03)
    rasgo = lib.caixa('rasgo_ext', (3.0, 0.25, 1.0), (xr, yr, z_r), lib.mat_pintura('rasgo', '#0b0d12', rug=0.9)); rasgo.parent = raiz
    surge(rasgo, 134.9, dur=0.15)
    mb = lib.mat_bolha(); rs = random.Random(41)
    import bmesh
    for i in range(36):                     # bolhas e partículas puxadas para dentro do rombo (escoamento para o porão)
        r = rs.uniform(0.04, 0.12); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        me = bpy.data.meshes.new('bolha'); bm.to_mesh(me); bm.free()
        o = lib.ligar(bpy.data.objects.new('bolha_ext', me)); o.data.materials.append(mb)
        o.location = (xr + rs.uniform(-0.8, 0.8), yr + 0.15, z_r + rs.uniform(-0.3, 0.3)); o.parent = raiz
        t0 = 135.0 + rs.uniform(0, 1.8)
        surge(o, t0, dur=0.45, d=(rs.uniform(-2.5, 2.5), -rs.uniform(1.5, 3.5), rs.uniform(-1.2, 1.2)), t1=t0 + 0.45, dur1=0.05)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    def anim(g):
        raiz.location.z = -T0 + 0.06 * math.sin(2 * math.pi * g / 8.0)
        if g < 135.4:            # aproximação rente à água, de ré, ao longo do costado
            p, a, l = trilha([(134.0, (xr - 70, -46, 2.5), (xr, -16, 0), 26), (135.4, (xr - 30, -34, 2.0), (xr, -17, -1), 28)], g)
        else:                    # close: o rombo debaixo d'água, a água entrando
            p, a, l = trilha([(135.4, (xr - 6, yr - 7.5, 1.2), (xr, yr, -1.8), 32), (137.0, (xr - 4.5, yr - 6.0, 0.9), (xr, yr, -1.9), 34)], g)
        camera_em(cam, p, a, l)
    rot = Rotulos()
    rot.add('Avaria', lambda g: raiz.matrix_world @ Vector((xr, yr, z_r)), 135.5, 137.0, dx=0.06, dy=-0.08)
    exportar_seg(pasta, 134.00, 137.00, anim, rot, extra=dict(segmento='12x', calado=T0))


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
    vol = volume_submerso('vol_desl_fim', T, infla=0.18, mat=lib.mat_fantasma('deslocado_fim', COR_EMPUXO, alfa=0.52, brilho=1.5))
    vol.parent = raiz; surge(vol, 159.6, dur=1.0)
    # plano final (164,35 s): o mar volta a ser contínuo (sem o corte do diorama) para a aérea do navio inteiro
    fim = lib.bloco_agua('mar_final', -4000, 4000, -4000, Y0 + 0.05, -30, magua, res=40, amp=0.0, so_superficie=True); surge(fim, 164.35, dur=0.04)
    me = lib.mat_emissivo('seta_empuxo', '#a6f0ff', 2.6); mw = lib.mat_emissivo('seta_peso', COR_PESO, 2.0)
    _, _, KB = hidro.carena(T)
    yb = -navio.MEIA_BOCA - 3.5
    B = lib.seta3d('empuxo_f', (0, yb, KB - T), (0, 0, 1), 9.0, r=1.8, mat=me, cabeca=2.2)
    W = lib.seta3d('peso_f', (8, yb, 12.5 - T + 9.0), (0, 0, -1), 9.0, r=1.8, mat=mw, cabeca=2.2)
    for o, t0 in ((B, 161.4), (W, 161.4)): o.visible_shadow = False; surge(o, t0, dur=0.7, escala=True, t1=164.3, dur1=0.05)
    cam = bpy.context.scene.camera or lib.camera((0, -50, 0), (0, 0, 0))
    rot = Rotulos()
    rot.add('Água deslocada', (-30, -navio.MEIA_BOCA, -T * 0.55), 160.2, 163.95, dx=0.05, dy=0.08)
    rot.add('Empuxo', (0, yb, KB - T + 7.5), 161.8, 163.95, dx=-0.10, dy=0.02)
    rot.add('Peso', (8, yb, 12.5 - T + 4.0), 161.8, 163.95, dx=0.06, dy=-0.02)
    # 63 retomada do contraste: um bloco maciço de aço cai ao lado (à frente da proa) e afunda; o navio continua flutuando
    a = (hidro.RHO * hidro.carena(navio.CALADO_LEVE)[0] / 7.85) ** (1 / 3)
    cubo = bpy.data.objects.new('cubo_fim', None); lib.ligar(cubo); cubo['anim'] = 1
    lib.caixa('cubo_fim_m', (a, a, a), (0, 0, 0), lib.mat_aco('aco_bloco', (158, 161, 166), rug=0.3, escovado=False, macico=True, manchas=0.07, escala_var=0.9), bisel=0.12).parent = cubo
    XB, TS = 126.0, 155.2
    def zc(g):
        if g < TS: return a / 2 + 2.0
        t = g - TS; t_ag = math.sqrt(4.0 / G)
        if t < t_ag: return a / 2 + 2.0 - 0.5 * G * t * t
        v0 = G * t_ag; tt = t - t_ag; return a / 2 - v0 * tt - 0.5 * 7.9 * tt * tt
    rot.add('Aço maciço', lambda g: Vector((XB, -a / 2, zc(g) + a / 2)), 154.8, 156.8, dx=-0.08, dy=-0.07)
    # ajustes finais: 63 bloco em primeiro plano → cai e afunda (a câmera desce com ele) com o navio flutuando atrás;
    # 64 revelação da parte submersa ao longo do casco (o volume deslocado acende); 65 peso = empuxo, setas grandes;
    # 66 aérea 3/4 do navio inteiro (mar contínuo) antes da assinatura
    P = [(154.6, [(154.6, (178, -60, 9), (118, -6, 3), 24), (155.5, (176, -59, 8), (118, -6, 1), 24), (156.6, (174, -58, 4), (118, -6, -6), 24),
                  (157.6, (172, -58, -2), (116, -6, -14), 24), (158.7, (170, -58, -5), (112, -6, -18), 24)]),
         (158.7, [(158.7, (115, -58, -2), (70, -16, 0), 22), (162.4, (45, -54, -2), (5, -16, 0), 22)]),
         (162.4, [(162.4, (30, -52, -2.5), (3, -17, -1), 24), (164.35, (28, -50, -2), (3, -17, -0.5), 24)]),
         (164.35, [(164.35, (146, -124, 30), (5, 0, 2), 22), (166.3, (158, -136, 34.5), (4, 0, 2), 22),             # 66 navio inteiro: o movimento conclui
                   (168.0, (163, -141, 36.5), (3, 0, 2), 22)])]                                                          # e o vídeo termina aqui
    def anim(g):
        raiz.location.z = -T + 0.08 * math.sin(2 * math.pi * g / 9.0)
        sc = 1.0 if g <= 158.6 else 1e-4
        cubo.location = (XB, 0, zc(g)); cubo.scale = (sc,) * 3
        camera_planos(cam, P, g)
    exportar_seg(pasta, 154.60, 168.00, anim, rot, extra=dict(segmento='13', calado=T))


SEGMENTOS = {'0607b': seg0607b, '12x': seg12x, '12': seg12, '13': seg13, '09': seg09, '10': seg10, '11': seg11, '02': seg02, '03': seg03, '04': seg04, '05': seg05, '0607': seg0607, '08a': seg08a, '08b': seg08b}

if __name__ == '__main__':
    SEGMENTOS[sys.argv[1]](sys.argv[2])
