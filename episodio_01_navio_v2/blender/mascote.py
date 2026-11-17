"""Protótipo 3D do mascote oficial (busto) — ETAPA SEPARADA, não usar no vídeo sem aprovação.
Construído a partir da imagem oficial (referencias/mascote_oficial.png): menino explorador, cabelo castanho
espetado, olhos grandes castanhos, sorriso aberto, óculos de exploração com lentes âmbar e tira amarela na cabeça,
casaco azul-marinho com capuz, lenço amarelo e alças marrons de mochila com fivelas amarelas.

Uso: python3 mascote.py [pct=50] [amostras=96] [vista=34|frente|perfil|todas]
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler
import lib

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(os.path.dirname(AQUI), 'mascote')
C = dict(pele='#f2a774', pele_sombra='#d9845a', cabelo='#5b3322', cabelo_claro='#7a4a2c', olho='#4a2716', marinho='#232a6b',
         marinho_claro='#2f3a8c', amarelo='#f5b52e', alca='#4a3b36', oculos='#3c3b42', lente='#f2b21c', boca='#5a1a1f',
         lingua='#e0636a', dente='#fbf8f2', ziper='#c9cbd2')


# ---------------------------------------------------------------- materiais
def mat_pele():
    m, nt, p = lib._mat('pele')
    p.inputs['Base Color'].default_value = lib.srgb(C['pele']); p.inputs['Roughness'].default_value = 0.48
    p.inputs['Subsurface Weight'].default_value = 0.18; p.inputs['Subsurface Radius'].default_value = (1.0, 0.45, 0.3)
    p.inputs['Subsurface Scale'].default_value = 0.04
    p.inputs['Coat Weight'].default_value = 0.08
    return m


def mat(nome, cor, rug=0.5, metal=0.0, coat=0.0, emis=0.0):
    m, nt, p = lib._mat(nome)
    p.inputs['Base Color'].default_value = lib.srgb(cor); p.inputs['Roughness'].default_value = rug
    p.inputs['Metallic'].default_value = metal; p.inputs['Coat Weight'].default_value = coat
    if emis > 0:
        p.inputs['Emission Color'].default_value = lib.srgb(cor); p.inputs['Emission Strength'].default_value = emis
    return m


def mat_tecido(nome, cor, rug=0.75):
    m = lib.mat_pintura(nome, cor, rug=rug, variacao=0.05, escala_var=6.0, bump=0.08)
    return m


# ---------------------------------------------------------------- geometria auxiliar
def esfera(nome, centro, raios, material, seg=40, aneis=24, suave=True, subdiv=0, pai=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=aneis, radius=1.0)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = suave
    o = lib.ligar(bpy.data.objects.new(nome, me)); o.data.materials.append(material)
    o.location = centro; o.scale = raios; o.rotation_euler = rot
    if subdiv: o.modifiers.new('sub', 'SUBSURF').levels = subdiv
    if pai: o.parent = pai
    return o


def deformar(o, f):
    for v in o.data.vertices: v.co = Vector(f(Vector(v.co)))
    o.data.update()


def cone(nome, base, direcao, comp, raio, material, lados=4, pai=None, torcao=0.0):
    d = Vector(direcao).normalized()
    v = [(raio * math.cos(2 * math.pi * i / lados + torcao), raio * math.sin(2 * math.pi * i / lados + torcao), 0) for i in range(lados)]
    v.append((0, 0, comp))
    f = [(i, (i + 1) % lados, lados) for i in range(lados)] + [tuple(range(lados))[::-1]]
    o = lib.malha(nome, v, f, material, suave=False)
    o.location = base; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    if pai: o.parent = pai
    return o


def encolher_sobre(o, alvo, desloc=0.004):
    sw = o.modifiers.new('cola', 'SHRINKWRAP'); sw.target = alvo; sw.wrap_method = 'NEAREST_SURFACEPOINT'; sw.offset = desloc
    sw.wrap_mode = 'OUTSIDE_SURFACE'
    return sw


def decalque(nome, contorno, centro, material, pai, alvo, desloc=0.004, sub=2):
    """Polígono plano (contorno 2D em x,z no plano frontal) colado na superfície do rosto (shrinkwrap)."""
    vs = [(centro[0] + x, centro[1], centro[2] + z) for x, z in contorno]
    o = lib.malha(nome, vs, [tuple(range(len(vs)))], material)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=sub, use_grid_fill=True)
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = True
    o.parent = pai
    encolher_sobre(o, alvo, desloc)
    return o


# ---------------------------------------------------------------- personagem
def construir():
    mpele = mat_pele(); mcab = mat('cabelo', C['cabelo'], rug=0.55); mcab2 = mat('cabelo2', C['cabelo_claro'], rug=0.55)
    mmar = mat_tecido('casaco', C['marinho'], rug=0.7); mmar2 = mat_tecido('casaco2', C['marinho_claro'], rug=0.7)
    mama = mat_tecido('lenco', C['amarelo'], rug=0.65); malca = mat('alca', C['alca'], rug=0.6)
    mfiv = mat('fivela', C['amarelo'], rug=0.35, metal=0.3); moc = mat('oculos', C['oculos'], rug=0.35, metal=0.4)
    mlen = mat('lente', C['lente'], rug=0.08, coat=1.0, emis=0.35); mbr = mat('olho_branco', '#fbfaf6', rug=0.25, coat=0.6)
    miris = mat('iris', C['olho'], rug=0.2, coat=1.0); mpup = mat('pupila', '#120806', rug=0.2, coat=1.0)
    mbrilho = mat('brilho', '#ffffff', rug=0.1, emis=6.0); mboca = mat('boca', C['boca'], rug=0.6)
    mling = mat('lingua', C['lingua'], rug=0.45); mdente = mat('dente', C['dente'], rug=0.3, coat=0.4)
    mziper = mat('ziper', C['ziper'], rug=0.3, metal=0.6); mbrow = mat('sobrancelha', '#3b1f14', rug=0.7)
    msomb = mat('pele_sombra', C['pele_sombra'], rug=0.6)

    # --- cabeça quase esférica (rosto para -Y); proporções medidas na arte oficial (R = 0,47)
    R = 0.47
    cab = bpy.data.objects.new('cabeca', None); lib.ligar(cab); cab.location = (0, 0, 1.48)
    head = esfera('rosto', (0, 0, 0), (1, 1, 1), mpele, seg=64, aneis=40, subdiv=1, pai=cab)
    def forma(v):
        x, y, z = v
        sx = R * (1.0 + 0.06 * math.exp(-((z + 0.35) / 0.35) ** 2))     # bochechas cheias
        sz = R * (0.98 if z > 0 else 0.93)                              # queixo curto e arredondado
        sy = R * 0.97
        return (x * sx, y * sy, z * sz)
    deformar(head, forma)
    for s in (1, -1):
        esfera('orelha', (s * 0.465, 0.03, -0.07), (0.065, 0.11, 0.14), mpele, pai=cab, rot=(0, 0, math.radians(-s * 18)), subdiv=1)
        esfera('orelha_in', (s * 0.505, 0.0, -0.07), (0.02, 0.065, 0.085), msomb, pai=cab)
    esfera('nariz', (0.0, -0.47, -0.17), (0.06, 0.05, 0.05), mpele, pai=cab, subdiv=1)
    # olhos grandes, olhar para cima e para a direita do observador
    for s in (1, -1):
        c = Vector((s * 0.185, -0.395, -0.04))
        esfera('esclera', tuple(c), (0.105, 0.07, 0.118), mbr, pai=cab, subdiv=1)
        fr = c + Vector((0.03, -0.062, 0.03))
        esfera('iris', tuple(fr), (0.07, 0.022, 0.08), miris, pai=cab)
        esfera('pupila', tuple(fr + Vector((0.004, -0.013, 0.004))), (0.036, 0.012, 0.042), mpup, pai=cab)
        esfera('brilho', tuple(fr + Vector((0.026, -0.024, 0.032))), (0.018, 0.008, 0.018), mbrilho, pai=cab)
        pts = [(c.x + t * 0.105, c.y - 0.055 + 0.03 * t * t, c.z + 0.105 - 0.025 * t * t) for t in np.linspace(-1, 1, 9)]
        pl = lib.tubo('palpebra', pts, r=0.016, mat=mbrow); pl.parent = cab
        pts = [(c.x + t * 0.125, c.y - 0.05 + 0.04 * t * t, c.z + 0.2 + 0.04 * (1 - t * t) - 0.012 * s * t) for t in np.linspace(-1, 1, 9)]
        sb = lib.tubo('sobrancelha', pts, r=0.036, mat=mbrow); sb.parent = cab
        for i, p in enumerate(sb.data.splines[0].points): p.radius = 0.55 + 0.6 * math.sin(math.pi * i / 8)
    # boca aberta em sorriso: cavidade larga embutida no rosto, cantos elevados, dentes superiores e língua
    esfera('boca', (0.03, -0.395, -0.27), (0.17, 0.06, 0.085), mboca, pai=cab, subdiv=1, rot=(math.radians(-10), 0, 0))
    for s_ in (1, -1):
        esfera('canto', (0.03 + s_ * 0.155, -0.395, -0.235), (0.035, 0.05, 0.03), mboca, pai=cab, subdiv=1)
    esfera('dentes', (0.03, -0.437, -0.232), (0.135, 0.028, 0.03), mdente, pai=cab, subdiv=1)
    esfera('lingua', (0.03, -0.42, -0.305), (0.09, 0.035, 0.04), mling, pai=cab, subdiv=1)
    # cabelo volumoso facetado
    calota = esfera('calota', (0, 0.05, 0.08), (0.56, 0.56, 0.58), mcab, seg=14, aneis=9, suave=False, pai=cab)
    bm = bmesh.new(); bm.from_mesh(calota.data)
    apagar = [v for v in bm.verts if (v.co.z < 0.20 and v.co.y < -0.30) or v.co.z < -0.40]
    bmesh.ops.delete(bm, geom=apagar, context='VERTS'); bm.to_mesh(calota.data); bm.free()
    rnd = random.Random(11)
    def ponto(th, ph, r=0.52):
        n = Vector((math.sin(ph) * math.sin(th), -math.sin(ph) * math.cos(th), math.cos(ph)))
        return Vector((0, 0.03, 0.05)) + n * r, n
    for i in range(110):
        th = rnd.uniform(-math.pi, math.pi); ph = rnd.uniform(0.0, 1.9)
        if ph > 0.95 and abs(th) < 1.3: continue
        p, n = ponto(th, ph, 0.54)
        d = (n + Vector((0, 0.45, 0.6))).normalized()
        L = rnd.uniform(0.18, 0.34) * (1.0 if ph < 1.2 else 0.7)
        cone('mecha', tuple(p), tuple(d), L * 0.85, rnd.uniform(0.13, 0.19), mcab if i % 3 else mcab2, lados=rnd.choice((3, 4)), pai=cab, torcao=rnd.uniform(0, 1))
    # franja: tufos largos nascendo à frente da tira e caindo sobre a testa até as sobrancelhas
    for i, xf in enumerate(np.linspace(-0.34, 0.34, 9)):
        zf = 0.40 - 0.05 * (xf / 0.34) ** 2
        yf = -math.sqrt(max(0.0, 0.5 ** 2 - xf ** 2 - (zf - 0.05) ** 2)) - 0.035
        d = Vector((0.25 * xf / 0.34 + 0.12 * math.sin(i * 1.7), -0.35, -1.0)).normalized()
        cone('franja', (xf, yf, zf), tuple(d), 0.2 + 0.05 * ((i * 7) % 3), 0.11 + 0.02 * (i % 2), mcab if i % 2 else mcab2, lados=3, pai=cab, torcao=0.6 * i)
    for s in (1, -1):
        p, n = ponto(s * 1.45, 1.35, 0.5)
        cone('costeleta', tuple(p), tuple((n * 0.2 + Vector((0, 0.15, -1))).normalized()), 0.16, 0.07, mcab, lados=3, pai=cab)
    # óculos sobre o cabelo e tira amarela ao redor da cabeça
    pts = []
    for a in np.linspace(0, 2 * math.pi, 49):
        pts.append((0.53 * math.sin(a), 0.03 - 0.53 * math.cos(a), 0.30 + 0.10 * math.cos(a)))
    t = lib.tubo('tira', pts, r=0.032, mat=mama); t.data.bevel_resolution = 1; t.parent = cab
    for s in (1, -1):
        piv = bpy.data.objects.new('oculos_piv', None); lib.ligar(piv); piv.parent = cab
        piv.location = (s * 0.16, -0.40, 0.50); piv.rotation_euler = (math.radians(-45), 0, math.radians(s * 20))
        lib.caixa('aro', (0.27, 0.1, 0.18), (0, 0, 0), moc, bisel=0.055, seg=4).parent = piv
        lib.caixa('lente', (0.2, 0.03, 0.12), (0, -0.05, 0), mlen, bisel=0.04, seg=3).parent = piv
    pb = lib.caixa('ponte', (0.1, 0.06, 0.06), (0, -0.44, 0.52), moc, bisel=0.02); pb.parent = cab; pb.rotation_euler = (math.radians(-40), 0, 0)
    # pescoço curto, casaco, capuz, lenço e alças
    esfera('pescoco', (0, 0.03, 1.02), (0.13, 0.13, 0.12), mpele, subdiv=1)
    tronco = esfera('tronco', (0, 0.06, 0.55), (1, 1, 1), mmar, seg=48, aneis=28, subdiv=1)
    deformar(tronco, lambda v: (v.x * 0.62 * (1 + 0.1 * max(0, v.z)), v.y * 0.38, v.z * 0.5))
    for s in (1, -1): esfera('ombro', (s * 0.5, 0.08, 0.84), (0.22, 0.24, 0.18), mmar, subdiv=1)
    cap_pts = [(0.33 * math.sin(a), 0.08 + 0.24 * math.cos(a) * (1.0 if math.cos(a) > 0 else 0.5), 0.98 + 0.12 * max(0, math.cos(a))) for a in np.linspace(-2.25, 2.25, 32)]
    capuz = lib.tubo('capuz', cap_pts, r=0.13, mat=mmar2); capuz.data.bevel_resolution = 4
    for i, p in enumerate(capuz.data.splines[0].points): p.radius = 0.8 + 0.7 * math.sin(math.pi * i / 31)
    gola = [(0.2 * math.sin(a), 0.03 - 0.18 * math.cos(a), 0.97 - 0.03 * math.cos(a)) for a in np.linspace(0, 2 * math.pi, 33)]
    g = lib.tubo('lenco_gola', gola, r=0.09, mat=mama); g.data.bevel_resolution = 3
    pon = lib.malha('lenco_ponta', [(0.0, -0.2, 0.97), (0.25, -0.26, 0.9), (0.0, -0.37, 0.5), (-0.25, -0.26, 0.9)], [(0, 1, 2, 3)], mama)
    pon.modifiers.new('esp', 'SOLIDIFY').thickness = 0.035; pon.modifiers.new('sub', 'SUBSURF').levels = 2
    for z in np.arange(0.12, 0.52, 0.035): lib.caixa('ziper', (0.022, 0.012, 0.012), (0.0, -0.385, z), mziper)
    for s in (1, -1):
        pts = [Vector(p) for p in ((s * 0.33, 0.24, 0.93), (s * 0.36, -0.05, 1.0), (s * 0.33, -0.33, 0.82), (s * 0.3, -0.4, 0.45), (s * 0.29, -0.38, 0.05))]
        for a_, b_ in zip(pts, pts[1:]):
            d = b_ - a_; L = d.length
            o = lib.caixa('alca', (0.12, 0.035, L + 0.02), tuple((a_ + b_) / 2), malca, bisel=0.01)
            o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        lib.caixa('fivela', (0.15, 0.03, 0.09), (s * 0.31, -0.43, 0.6), mfiv, bisel=0.014)
        lib.caixa('fivela_in', (0.09, 0.035, 0.045), (s * 0.31, -0.436, 0.6), malca, bisel=0.008)
    cab.rotation_euler = (math.radians(-11), 0, math.radians(30))
    return cab


def cena(vista='34'):
    s = lib.nova_cena(amostras=96)
    s.render.resolution_x, s.render.resolution_y = 1080, 1080
    lib.fundo_gradiente('#1f5fe0', '#06103a', forca=1.0)
    construir()
    # luz principal quente (cima/esquerda), preenchimento suave e contraluz azul (recorte, como na arte oficial)
    lib.luz_area((-1.6, -2.6, 3.2), (0, 0, 1.4), tam=1.6, energia=260, cor=(1.0, 0.94, 0.86))
    lib.luz_area((2.4, -2.2, 1.4), (0, 0, 1.3), tam=2.5, energia=90, cor=(0.9, 0.93, 1.0))
    lib.luz_area((1.4, 1.8, 2.4), (0, 0, 1.5), tam=1.2, energia=320, cor=(0.35, 0.55, 1.0))
    lib.luz_area((-1.6, 1.6, 1.8), (0, 0, 1.4), tam=1.2, energia=160, cor=(0.35, 0.55, 1.0))
    alvo = (0.03, 0, 1.36)
    pos = {'34': (0.3, -2.5, 1.2), 'frente': (0.0, -2.5, 1.3), 'perfil': (2.5, -0.1, 1.3)}[vista]
    c = lib.camera(pos, alvo, lente=40); c.data.sensor_height = 36
    return s


if __name__ == '__main__':
    pct = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    am = int(sys.argv[2]) if len(sys.argv) > 2 else 96
    vista = sys.argv[3] if len(sys.argv) > 3 else '34'
    os.makedirs(SAIDA, exist_ok=True)
    for v in (['34', 'frente', 'perfil'] if vista == 'todas' else [vista]):
        cena(v)
        lib.renderizar(os.path.join(SAIDA, f'mascote_{v}_{pct}.png'), pct, am)
        print('OK', v)
