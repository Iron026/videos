"""Biblioteca de cena do Episódio 01 (v2) — Blender/Cycles por código.

Convenções: metros, Z para cima, X = popa(-) → proa(+), Y = través (bombordo +).
Tudo é determinístico (sementes fixas) para que cada quadro possa ser refeito idêntico.
"""
import bpy, bmesh, math, random, os
import numpy as np
from mathutils import Vector, Matrix, Euler

AQUI = os.path.dirname(os.path.abspath(__file__))
MARCA = dict(azul=(0x20, 0x2B, 0x57), branco=(0xF6, 0xF4, 0xEC), amarelo=(0xF3, 0xB5, 0x44))


def srgb(h):
    """'#rrggbb' ou tupla 0-255 → RGBA linear."""
    if isinstance(h, str):
        h = h.lstrip('#'); h = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    def c(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return (c(h[0]), c(h[1]), c(h[2]), 1.0)


# ---------------------------------------------------------------- cena
def nova_cena(amostras=128, luz_rapida=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()   # materiais da cena anterior deixam de existir
    ROTULOS.clear()
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    c = s.cycles
    c.device = 'CPU'; c.samples = amostras; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02
    c.use_denoising = True
    try: c.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    c.max_bounces = 8; c.diffuse_bounces = 3; c.glossy_bounces = 3; c.transmission_bounces = 8
    c.volume_bounces = 1; c.transparent_max_bounces = 8
    c.caustics_reflective = False; c.caustics_refractive = False; c.blur_glossy = 1.0
    c.sample_clamp_indirect = 6.0
    if luz_rapida:
        c.use_fast_gi = True
    s.render.resolution_x, s.render.resolution_y = 1080, 1920
    s.render.film_transparent = False
    # Khronos PBR Neutral: comprime altas luzes sem desviar matiz/saturação (cores da marca preservadas)
    s.view_settings.view_transform = 'Khronos PBR Neutral'; s.view_settings.look = 'None'
    s.render.image_settings.file_format = 'PNG'
    s.render.threads_mode = 'AUTO'
    return s


def renderizar(caminho, pct=100, amostras=None):
    s = bpy.context.scene
    s.render.resolution_percentage = pct
    if amostras: s.cycles.samples = amostras
    s.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


def ceu(sol_elev=28, sol_rot=200, forca=0.14, aerossol=0.9, sol_forca=4.2):
    """Céu físico + sol. sol_rot em graus (azimute)."""
    w = bpy.data.worlds.new('mundo'); bpy.context.scene.world = w
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    sky = nt.nodes.new('ShaderNodeTexSky')
    try: sky.sky_type = 'MULTIPLE_SCATTERING'
    except Exception: sky.sky_type = 'SINGLE_SCATTERING'
    sky.sun_elevation = math.radians(sol_elev); sky.sun_rotation = math.radians(sol_rot)
    sky.sun_disc = False
    try: sky.air_density = 1.0; sky.aerosol_density = aerossol
    except Exception: pass
    nt.links.new(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = forca
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
    # sol como lâmpada (sombras suaves controláveis)
    d = bpy.data.lights.new('sol', 'SUN'); d.energy = sol_forca; d.angle = math.radians(2.2)
    d.color = (1.0, 0.93, 0.84)
    o = bpy.data.objects.new('sol', d); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = Euler((math.radians(90 - sol_elev), 0, math.radians(sol_rot + 90)))
    return o


def fundo_gradiente(topo, base, forca=1.0):
    """Mundo em degradê (para cenas subaquáticas/diorama)."""
    w = bpy.data.worlds.new('grad'); bpy.context.scene.world = w
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.color_ramp.elements[0].position = 0.35; rmp.color_ramp.elements[0].color = srgb(base)
    rmp.color_ramp.elements[1].position = 0.75; rmp.color_ramp.elements[1].color = srgb(topo)
    mp = nt.nodes.new('ShaderNodeMapRange'); mp.inputs['From Min'].default_value = -1; mp.inputs['From Max'].default_value = 1
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], mp.inputs[0])
    nt.links.new(mp.outputs[0], rmp.inputs[0]); nt.links.new(rmp.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = forca
    nt.links.new(bg.outputs[0], out.inputs['Surface'])


def camera(pos, alvo, lente=35, foco=None, fstop=8.0, sensor=36):
    cd = bpy.data.cameras.new('cam'); cd.lens = lente; cd.sensor_width = sensor; cd.sensor_fit = 'VERTICAL'
    cd.clip_start = 0.1; cd.clip_end = 6000
    o = bpy.data.objects.new('cam', cd); bpy.context.scene.collection.objects.link(o)
    o.location = pos
    d = Vector(alvo) - Vector(pos)
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if foco is not None:
        cd.dof.use_dof = True; cd.dof.focus_distance = foco if isinstance(foco, (int, float)) else (Vector(foco) - Vector(pos)).length
        cd.dof.aperture_fstop = fstop
    bpy.context.scene.camera = o
    return o


def luz_area(pos, alvo, tam=10, energia=1000, cor=(1, 1, 1)):
    d = bpy.data.lights.new('area', 'AREA'); d.size = tam; d.energy = energia; d.color = cor
    o = bpy.data.objects.new('area', d); bpy.context.scene.collection.objects.link(o)
    o.location = pos; o.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    o.visible_camera = False; o.visible_glossy = False; o.visible_transmission = False   # preenchimento: não aparece nem em reflexos
    return o


# ---------------------------------------------------------------- materiais
_MATS = {}
ROTULOS = []   # rótulos 2D ancorados em pontos 3D (exportados para o motor em tempo real)

def _mat(nome):
    m = bpy.data.materials.new(nome)
    try: m.use_nodes = True
    except Exception: pass
    return m, m.node_tree, m.node_tree.nodes['Principled BSDF']


def _ruido(nt, escala=4.0, det=6.0, coord='Object'):
    tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = escala; n.inputs['Detail'].default_value = det
    nt.links.new(tc.outputs[coord], n.inputs['Vector'])
    return n


def mat_pintura(nome, cor, rug=0.45, metal=0.0, variacao=0.06, escala_var=0.6, coat=0.0, bump=0.0):
    """Tinta com leve variação de tom/rugosidade (evita aspecto de plástico chapado)."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    n = _ruido(nt, escala_var, 5.0)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    base = srgb(cor) if not (isinstance(cor, tuple) and len(cor) == 4) else cor
    mix.inputs[6].default_value = base
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1 - variacao; mr.inputs['To Max'].default_value = 1 + variacao
    nt.links.new(n.outputs['Fac'], mr.inputs[0])
    cmb = nt.nodes.new('ShaderNodeCombineColor')
    for i in range(3): nt.links.new(mr.outputs[0], cmb.inputs[i])
    nt.links.new(cmb.outputs[0], mix.inputs[7]); mix.inputs[0].default_value = 1.0
    nt.links.new(mix.outputs[2], p.inputs['Base Color'])
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rug * 0.8; rr.inputs['To Max'].default_value = min(1, rug * 1.2)
    nt.links.new(n.outputs['Fac'], rr.inputs[0]); nt.links.new(rr.outputs[0], p.inputs['Roughness'])
    p.inputs['Metallic'].default_value = metal
    p.inputs['Coat Weight'].default_value = coat
    if bump > 0:
        n2 = _ruido(nt, 18.0, 8.0); b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump
        nt.links.new(n2.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs[0], p.inputs['Normal'])
    _MATS[nome] = m; return m


def mat_aco(nome='aco', cor=(150, 152, 156), rug=0.32, escovado=True, macico=False, manchas=0.0, escala_var=0.9):
    """Aço nu: metálico, com riscos de escovação e manchas de laminação. macico=True: aço maciço (bloco) — sem escovação,
    manchas largas e suaves (±manchas), rugosidade pouco variável e grão fino antisserrilhado no motor em tempo real."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    p.inputs['Metallic'].default_value = 1.0
    p.inputs['Base Color'].default_value = srgb(cor)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    # manchas de laminação
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2.2; n.inputs['Detail'].default_value = 8
    nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rug * 0.65; rr.inputs['To Max'].default_value = rug * 1.45
    nt.links.new(n.outputs['Fac'], rr.inputs[0]); nt.links.new(rr.outputs[0], p.inputs['Roughness'])
    if escovado:
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 60, 60)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 12; n2.inputs['Detail'].default_value = 3
        nt.links.new(mp.outputs[0], n2.inputs['Vector'])
        b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.06
        nt.links.new(n2.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs[0], p.inputs['Normal'])
    p.inputs['Anisotropic'].default_value = 0.35
    _MATS[nome] = m; return m


def mat_emissivo(nome, cor, forca=6.0, fade=False):
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    p.inputs['Base Color'].default_value = srgb(cor); p.inputs['Emission Color'].default_value = srgb(cor)
    p.inputs['Emission Strength'].default_value = forca
    _MATS[nome] = m; return m


def mat_concreto(nome='concreto', cor=(150, 146, 136), escala=0.35):
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    n = _ruido(nt, escala, 8.0)
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    c = srgb(cor); rmp.color_ramp.elements[0].color = tuple(v * 0.78 for v in c[:3]) + (1,)
    rmp.color_ramp.elements[1].color = tuple(min(1, v * 1.08) for v in c[:3]) + (1,)
    rmp.color_ramp.elements[0].position = 0.35; rmp.color_ramp.elements[1].position = 0.7
    nt.links.new(n.outputs['Fac'], rmp.inputs[0]); nt.links.new(rmp.outputs[0], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = 0.88
    n2 = _ruido(nt, 9.0, 10.0); b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.25; b.inputs['Distance'].default_value = 0.02
    nt.links.new(n2.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs[0], p.inputs['Normal'])
    _MATS[nome] = m; return m


def mat_areia(nome='areia', cor=(196, 172, 128), causticas=0.0, escala_caustica=0.9):
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    n = _ruido(nt, 0.25, 6.0)
    rmp = nt.nodes.new('ShaderNodeValToRGB'); c = srgb(cor)
    rmp.color_ramp.elements[0].color = tuple(v * 0.7 for v in c[:3]) + (1,); rmp.color_ramp.elements[1].color = c
    nt.links.new(n.outputs['Fac'], rmp.inputs[0]); nt.links.new(rmp.outputs[0], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = 0.95
    tc = nt.nodes.new('ShaderNodeTexCoord'); w = nt.nodes.new('ShaderNodeTexWave'); w.inputs['Scale'].default_value = 0.9
    w.inputs['Distortion'].default_value = 6; w.inputs['Detail'].default_value = 3
    nt.links.new(tc.outputs['Object'], w.inputs['Vector'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.35
    nt.links.new(w.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs[0], p.inputs['Normal'])
    if causticas > 0: caustica(nt, p, escala=escala_caustica, forca=causticas)
    _MATS[nome] = m; return m


def mat_agua(nome='agua', absorcao=(0.28, 0.72, 0.78), densidade=0.05, espalha=0.0, cor_esp=(0.5, 0.8, 0.9), rug=0.04,
             marola=0.25, escala_marola=0.35):
    """Água: superfície refrativa + volume (absorção e, opcionalmente, espalhamento para raios de luz)."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    p.inputs['Base Color'].default_value = (0.92, 0.98, 1.0, 1)
    p.inputs['Transmission Weight'].default_value = 1.0; p.inputs['IOR'].default_value = 1.333
    p.inputs['Roughness'].default_value = rug
    if marola > 0:  # marolas finas por relevo (sem custo de geometria)
        n = _ruido(nt, escala_marola, 6.0); n.inputs['Roughness'].default_value = 0.6
        n2 = _ruido(nt, escala_marola * 4.0, 4.0)
        ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'
        nt.links.new(n.outputs['Fac'], ad.inputs[0]); nt.links.new(n2.outputs['Fac'], ad.inputs[1])
        b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = marola
        nt.links.new(ad.outputs[0], b.inputs['Height']); nt.links.new(b.outputs[0], p.inputs['Normal'])
    out = nt.nodes['Material Output']
    # raios de sombra atravessam a superfície (luz do sol chega ao fundo sem depender de cáusticas)
    lp = nt.nodes.new('ShaderNodeLightPath'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs[0]); nt.links.new(p.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    ab = nt.nodes.new('ShaderNodeVolumeAbsorption'); ab.inputs['Color'].default_value = (*absorcao, 1); ab.inputs['Density'].default_value = densidade
    if espalha > 0:
        sc = nt.nodes.new('ShaderNodeVolumeScatter'); sc.inputs['Color'].default_value = (*cor_esp, 1); sc.inputs['Density'].default_value = espalha
        sc.inputs['Anisotropy'].default_value = 0.75
        ad = nt.nodes.new('ShaderNodeAddShader'); nt.links.new(ab.outputs[0], ad.inputs[0]); nt.links.new(sc.outputs[0], ad.inputs[1])
        nt.links.new(ad.outputs[0], out.inputs['Volume'])
    else:
        nt.links.new(ab.outputs[0], out.inputs['Volume'])
    _MATS[nome] = m; return m


def mat_vidro_escuro(nome='janela'):
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    p.inputs['Base Color'].default_value = srgb((28, 40, 58)); p.inputs['Roughness'].default_value = 0.08
    p.inputs['Metallic'].default_value = 0.4; p.inputs['Coat Weight'].default_value = 0.6
    _MATS[nome] = m; return m


def mat_conteiner(nome='conteiner'):
    """Cor por objeto (Object Info → Color) + corrugação em relevo + leve sujeira."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    n = _ruido(nt, 1.5, 6.0)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.82; mr.inputs['To Max'].default_value = 1.05
    nt.links.new(n.outputs['Fac'], mr.inputs[0])
    cmb = nt.nodes.new('ShaderNodeCombineColor')
    for i in range(3): nt.links.new(mr.outputs[0], cmb.inputs[i])
    mix.inputs[0].default_value = 1.0
    nt.links.new(oi.outputs['Color'], mix.inputs[6]); nt.links.new(cmb.outputs[0], mix.inputs[7])
    nt.links.new(mix.outputs[2], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = 0.55
    tc = nt.nodes.new('ShaderNodeTexCoord'); w = nt.nodes.new('ShaderNodeTexWave')
    w.wave_type = 'BANDS'; w.bands_direction = 'X'; w.wave_profile = 'TRI'
    w.inputs['Scale'].default_value = 1.0; w.inputs['Distortion'].default_value = 0
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (3.6, 3.6, 3.6)
    nt.links.new(tc.outputs['Object'], mp.inputs[0]); nt.links.new(mp.outputs[0], w.inputs['Vector'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.55; b.inputs['Distance'].default_value = 0.05
    nt.links.new(w.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs[0], p.inputs['Normal'])
    _MATS[nome] = m; return m


def mat_faixas_z(nome, faixas, rug=0.42, fade=False):
    """Pintura em faixas por altura (coordenadas do objeto): faixas = [(z_limite, cor), ..., (inf, cor)]."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    cor_atual = None
    for i in range(len(faixas) - 1, -1, -1):
        z, cor = faixas[i]
        if cor_atual is None:
            cor_atual = ('val', srgb(cor)); continue
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        cmp = nt.nodes.new('ShaderNodeMath'); cmp.operation = 'LESS_THAN'; cmp.inputs[1].default_value = z
        nt.links.new(sep.outputs['Z'], cmp.inputs[0]); nt.links.new(cmp.outputs[0], mx.inputs[0])
        if cor_atual[0] == 'val': mx.inputs[6].default_value = cor_atual[1]
        else: nt.links.new(cor_atual[1], mx.inputs[6])
        mx.inputs[7].default_value = srgb(cor)
        cor_atual = ('sock', mx.outputs[2])
    n = _ruido(nt, 0.08, 6.0)
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.9; mr.inputs['To Max'].default_value = 1.06
    nt.links.new(n.outputs['Fac'], mr.inputs[0]); cmb = nt.nodes.new('ShaderNodeCombineColor')
    for i in range(3): nt.links.new(mr.outputs[0], cmb.inputs[i])
    nt.links.new(cor_atual[1], mul.inputs[6]); nt.links.new(cmb.outputs[0], mul.inputs[7])
    nt.links.new(mul.outputs[2], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = rug; p.inputs['Coat Weight'].default_value = 0.15
    _MATS[nome] = m; return m


# ---------------------------------------------------------------- geometria
def ligar(o, colecao=None):
    (colecao or bpy.context.scene.collection).objects.link(o); return o


def malha(nome, verts, faces, mat=None, suave=False, angulo=35):
    me = bpy.data.meshes.new(nome); me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces]); me.validate()
    o = ligar(bpy.data.objects.new(nome, me))
    if mat: o.data.materials.append(mat)
    if suave:
        for pg in me.polygons: pg.use_smooth = True
        try: me.set_sharp_from_angle(angle=math.radians(angulo))
        except Exception: pass
    return o


def chanfro(o, largura=0.05, segmentos=2, angulo=40):
    b = o.modifiers.new('chanfro', 'BEVEL'); b.width = largura; b.segments = segmentos
    b.limit_method = 'ANGLE'; b.angle_limit = math.radians(angulo); b.harden_normals = False
    return b


def caixa(nome, tam, pos=(0, 0, 0), mat=None, bisel=0.0, rot=(0, 0, 0), seg=2, colecao=None, dados=None):
    """Caixa com origem no centro. dados: reutiliza malha (cópia ligada)."""
    if dados is None:
        sx, sy, sz = [t / 2 for t in tam]
        v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        me = bpy.data.meshes.new(nome); me.from_pydata(v, [], f)
        if mat: me.materials.append(mat)
    else:
        me = dados
    o = bpy.data.objects.new(nome, me); ligar(o, colecao)
    o.location = pos; o.rotation_euler = rot
    if bisel > 0 and dados is None: chanfro(o, bisel, seg)
    elif bisel > 0: chanfro(o, bisel, seg)
    return o


def cilindro(nome, r, h, pos=(0, 0, 0), mat=None, lados=24, rot=(0, 0, 0), bisel=0.0, suave=True, r2=None):
    r2 = r if r2 is None else r2
    v, f = [], []
    for i in range(lados):
        a = 2 * math.pi * i / lados
        v.append((r * math.cos(a), r * math.sin(a), -h / 2)); v.append((r2 * math.cos(a), r2 * math.sin(a), h / 2))
    for i in range(lados):
        j = (i + 1) % lados; f.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    f.append(tuple(2 * i for i in range(lados))[::-1]); f.append(tuple(2 * i + 1 for i in range(lados)))
    o = malha(nome, v, f, mat, suave=suave, angulo=40)
    o.location = pos; o.rotation_euler = rot
    if bisel > 0: chanfro(o, bisel, 2)
    return o


def tubo(nome, pontos, r=0.05, mat=None, lados=8):
    """Tubo (cabo, mangueira) por curva bezier com bisel."""
    cu = bpy.data.curves.new(nome, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); sp.points.add(len(pontos) - 1)
    for i, p in enumerate(pontos): sp.points[i].co = (*p, 1)
    o = ligar(bpy.data.objects.new(nome, cu))
    if mat: cu.materials.append(mat)
    return o


def seta3d(nome, base, direcao, comp, r=0.6, mat=None, cabeca=2.6, lados=16):
    """Seta sólida (haste + ponta cônica), orientada de 'base' na 'direcao'."""
    d = Vector(direcao).normalized(); hc = min(cabeca * r * 1.6, comp * 0.45); hs = comp - hc
    v, f = [], []
    anel = lambda z, rr: [(rr * math.cos(2 * math.pi * i / lados), rr * math.sin(2 * math.pi * i / lados), z) for i in range(lados)]
    for z, rr in ((0, r), (hs, r), (hs, r * cabeca)):
        v += anel(z, rr)
    v.append((0, 0, comp)); v.append((0, 0, 0))
    for a in range(2):
        for i in range(lados):
            j = (i + 1) % lados; f.append((a * lados + i, a * lados + j, (a + 1) * lados + j, (a + 1) * lados + i))
    tip = 3 * lados
    for i in range(lados): f.append((2 * lados + i, 2 * lados + (i + 1) % lados, tip))
    f.append(tuple(range(lados))[::-1])
    o = malha(nome, v, f, mat, suave=True, angulo=50)
    o.location = base; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def rocha(nome, pos, tam, mat, semente=0, achatar=0.55):
    rnd = random.Random(semente)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    for v in bm.verts:
        v.co *= 1 + rnd.uniform(-0.28, 0.22); v.co.z *= achatar
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    o = ligar(bpy.data.objects.new(nome, me)); o.data.materials.append(mat)
    o.location = pos; o.scale = (tam * rnd.uniform(0.8, 1.2), tam * rnd.uniform(0.8, 1.2), tam); o.rotation_euler = (0, 0, rnd.uniform(0, 6.3))
    return o


def booleana(o, cortador, op='DIFFERENCE', transfere=True):
    m = o.modifiers.new('bool', 'BOOLEAN'); m.operation = op
    if isinstance(cortador, bpy.types.Collection): m.operand_type = 'COLLECTION'; m.collection = cortador
    else: m.object = cortador
    m.solver = 'EXACT'
    try: m.material_mode = 'TRANSFER' if transfere else 'INDEX'
    except Exception: pass
    return m


def aplicar(o):
    dg = bpy.context.evaluated_depsgraph_get(); oe = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(oe); o.modifiers.clear(); o.data = me
    return o


def ocultar(o):
    o.hide_render = True; o.hide_viewport = True; return o


def colecao(nome):
    c = bpy.data.collections.new(nome); bpy.context.scene.collection.children.link(c); return c


# ---------------------------------------------------------------- água
def ondas(x, y, t=0.0, amp=1.0, escala=1.0):
    """Ondas analíticas (soma de senos direcionais), em metros. escala<1 = ondas menores/curtas."""
    comps = [(0.9, 38, 0.3, 0.0), (0.5, 21, 1.1, 1.3), (0.32, 13, -0.6, 2.1), (0.18, 7.5, 2.0, 0.7), (0.1, 4.2, -1.4, 4.0), (0.06, 2.6, 0.5, 2.9)]
    h = np.zeros_like(x)
    for a, L, ang, fase in comps:
        L *= escala; k = 2 * math.pi / L; w = math.sqrt(9.81 * k)
        h += a * escala * np.sin(k * (x * math.cos(ang) + y * math.sin(ang)) - w * t + fase)
    return h * amp


def bloco_agua(nome, x0, x1, y0, y1, fundo, mat, res=1.0, amp=0.6, escala=1.0, t=0.0, so_superficie=False, extra=None):
    """Bloco de água fechado (diorama): superfície ondulada + paredes laterais + fundo plano em z=fundo."""
    nx = max(2, int((x1 - x0) / res) + 1); ny = max(2, int((y1 - y0) / res) + 1)
    xs = np.linspace(x0, x1, nx); ys = np.linspace(y0, y1, ny)
    X, Y = np.meshgrid(xs, ys, indexing='ij'); Z = ondas(X, Y, t, amp, escala)
    if extra is not None: Z = Z + extra(X, Y)
    verts = [(X[i, j], Y[i, j], Z[i, j]) for i in range(nx) for j in range(ny)]
    idx = lambda i, j: i * ny + j
    faces = [(idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)) for i in range(nx - 1) for j in range(ny - 1)]
    if not so_superficie:
        # contorno (sentido anti-horário visto de cima) e paredes
        borda = [idx(i, 0) for i in range(nx)] + [idx(nx - 1, j) for j in range(1, ny)] + \
                [idx(i, ny - 1) for i in range(nx - 2, -1, -1)] + [idx(0, j) for j in range(ny - 2, 0, -1)]
        base0 = len(verts)
        for k in borda:
            x, y, _ = verts[k]; verts.append((x, y, fundo))
        n = len(borda)
        for a in range(n):
            b = (a + 1) % n; faces.append((borda[b], borda[a], base0 + a, base0 + b))
        faces.append(tuple(base0 + a for a in range(n)))
    o = malha(nome, verts, faces, mat, suave=True, angulo=80)
    return o


def bolhas(nome, centro, raio, altura, n, mat, semente=1, tam=(0.03, 0.12)):
    rnd = random.Random(semente); objs = []
    bm = bmesh.new()
    for i in range(n):
        r = rnd.uniform(*tam); p = Vector((centro[0] + rnd.gauss(0, raio), centro[1] + rnd.gauss(0, raio), centro[2] + rnd.uniform(0, altura) ** 1.0))
        m = Matrix.Translation(p) @ Matrix.Diagonal((r, r, r * 0.8, 1))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=m)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for pg in me.polygons: pg.use_smooth = True
    o = ligar(bpy.data.objects.new(nome, me)); o.data.materials.append(mat)
    return o


def mat_bolha(nome='bolha'):
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    p.inputs['Base Color'].default_value = (1, 1, 1, 1); p.inputs['Transmission Weight'].default_value = 1.0
    p.inputs['IOR'].default_value = 0.76; p.inputs['Roughness'].default_value = 0.0
    _MATS[nome] = m; return m


def ceu_estilizado(sol_elev=28, sol_rot=200, zenite='#3d78c2', meio='#8fbde6', horizonte='#f3e7d3', abaixo='#2a4d70',
                   forca=1.0, sol_forca=3.6, nuvens=0.35, sol_cor=(1.0, 0.92, 0.80)):
    """Céu em degradê controlado (direção de arte) + nuvens suaves + sol como lâmpada."""
    w = bpy.data.worlds.new('ceu'); bpy.context.scene.world = w
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    rmp = nt.nodes.new('ShaderNodeValToRGB'); cr = rmp.color_ramp
    cr.elements[0].position = 0.0; cr.elements[0].color = srgb(abaixo)
    cr.elements[1].position = 1.0; cr.elements[1].color = srgb(zenite)
    e = cr.elements.new(0.495); e.color = srgb(horizonte)
    e = cr.elements.new(0.505); e.color = srgb(horizonte)
    e = cr.elements.new(0.62); e.color = srgb(meio)
    mp = nt.nodes.new('ShaderNodeMapRange'); mp.inputs['From Min'].default_value = -1; mp.inputs['From Max'].default_value = 1
    nt.links.new(sep.outputs['Z'], mp.inputs[0]); nt.links.new(mp.outputs[0], rmp.inputs[0])
    cor = rmp.outputs[0]
    if nuvens > 0:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2.2; n.inputs['Detail'].default_value = 6
        n.inputs['Roughness'].default_value = 0.55
        vm = nt.nodes.new('ShaderNodeMapping'); vm.inputs['Scale'].default_value = (1.0, 1.0, 4.0)
        nt.links.new(tc.outputs['Generated'], vm.inputs[0]); nt.links.new(vm.outputs[0], n.inputs['Vector'])
        cl = nt.nodes.new('ShaderNodeMapRange'); cl.inputs['From Min'].default_value = 0.52; cl.inputs['From Max'].default_value = 0.72
        nt.links.new(n.outputs['Fac'], cl.inputs[0])
        # só acima do horizonte, mais densas perto dele
        hz = nt.nodes.new('ShaderNodeMapRange'); hz.inputs['From Min'].default_value = 0.02; hz.inputs['From Max'].default_value = 0.10
        hz2 = nt.nodes.new('ShaderNodeMapRange'); hz2.inputs['From Min'].default_value = 0.55; hz2.inputs['From Max'].default_value = 0.2
        nt.links.new(sep.outputs['Z'], hz.inputs[0]); nt.links.new(sep.outputs['Z'], hz2.inputs[0])
        m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; nt.links.new(cl.outputs[0], m1.inputs[0]); nt.links.new(hz.outputs[0], m1.inputs[1])
        m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; nt.links.new(m1.outputs[0], m2.inputs[0]); nt.links.new(hz2.outputs[0], m2.inputs[1])
        m3 = nt.nodes.new('ShaderNodeMath'); m3.operation = 'MULTIPLY'; m3.inputs[1].default_value = nuvens; nt.links.new(m2.outputs[0], m3.inputs[0])
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs[7].default_value = srgb('#fbf7ef')
        nt.links.new(m3.outputs[0], mx.inputs[0]); nt.links.new(cor, mx.inputs[6]); cor = mx.outputs[2]
    nt.links.new(cor, bg.inputs[0]); bg.inputs[1].default_value = forca
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
    d = bpy.data.lights.new('sol', 'SUN'); d.energy = sol_forca; d.angle = math.radians(2.5); d.color = sol_cor
    o = bpy.data.objects.new('sol', d); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = Euler((math.radians(90 - sol_elev), 0, math.radians(sol_rot + 90)))
    return o


def caustica(nt, p, escala=0.9, forca=0.6, z_max=0.0, cor=(1.0, 0.98, 0.9)):
    """Cáusticas estilizadas: linhas de Voronoi (distância à borda) somadas à cor base abaixo de z_max."""
    tc = nt.nodes.new('ShaderNodeTexCoord')
    vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.feature = 'DISTANCE_TO_EDGE'; vor.inputs['Scale'].default_value = escala
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, 0.3)
    # distorção de alta frequência: bordas onduladas (rede de cáusticas, não células poligonais)
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 1.6; n.inputs['Detail'].default_value = 2
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    nt.links.new(geo.outputs['Position'], mp.inputs[0]); nt.links.new(geo.outputs['Position'], n.inputs['Vector'])
    sc = nt.nodes.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'; sc.inputs['Scale'].default_value = 0.45
    nt.links.new(n.outputs['Color'], sc.inputs[0])
    ad = nt.nodes.new('ShaderNodeVectorMath'); ad.operation = 'ADD'
    nt.links.new(mp.outputs[0], ad.inputs[0]); nt.links.new(sc.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], vor.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.045
    mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    nt.links.new(vor.outputs['Distance'], mr.inputs[0])
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs[0])
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = z_max
    nt.links.new(sep.outputs['Z'], lt.inputs[0])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; nt.links.new(mr.outputs[0], m1.inputs[0]); nt.links.new(lt.outputs[0], m1.inputs[1])
    sn = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Normal'], sn.inputs[0])
    nz = nt.nodes.new('ShaderNodeMapRange'); nz.inputs['From Min'].default_value = 0.4; nz.inputs['From Max'].default_value = 0.8
    nt.links.new(sn.outputs['Z'], nz.inputs[0])
    m1b = nt.nodes.new('ShaderNodeMath'); m1b.operation = 'MULTIPLY'; nt.links.new(m1.outputs[0], m1b.inputs[0]); nt.links.new(nz.outputs[0], m1b.inputs[1])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = forca; nt.links.new(m1b.outputs[0], m2.inputs[0])
    nt.links.new(m2.outputs[0], p.inputs['Emission Strength']); p.inputs['Emission Color'].default_value = (*cor, 1)


def mat_raio_luz(nome='raio_luz', forca=0.35, cor=(0.85, 0.97, 1.0)):
    """Feixe de luz subaquático estilizado: emissão aditiva que esmaece com a profundidade (coord. geradas)."""
    if nome in _MATS: return _MATS[nome]
    m = bpy.data.materials.new(nome)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    ad = nt.nodes.new('ShaderNodeAddShader')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    # Z gerado: 0 embaixo → 1 em cima; X gerado: borda suave
    pz = nt.nodes.new('ShaderNodeMath'); pz.operation = 'POWER'; pz.inputs[1].default_value = 1.8; nt.links.new(sep.outputs['Z'], pz.inputs[0])
    bx = nt.nodes.new('ShaderNodeMapRange'); bx.inputs['From Min'].default_value = 0; bx.inputs['From Max'].default_value = 1
    bx.inputs['To Min'].default_value = -1; bx.inputs['To Max'].default_value = 1; nt.links.new(sep.outputs['X'], bx.inputs[0])
    ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; nt.links.new(bx.outputs[0], ab.inputs[0])
    sx = nt.nodes.new('ShaderNodeMath'); sx.operation = 'SUBTRACT'; sx.inputs[0].default_value = 1.0; nt.links.new(ab.outputs[0], sx.inputs[1])
    sm = nt.nodes.new('ShaderNodeMath'); sm.operation = 'POWER'; sm.inputs[1].default_value = 1.5; nt.links.new(sx.outputs[0], sm.inputs[0])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; nt.links.new(pz.outputs[0], m1.inputs[0]); nt.links.new(sm.outputs[0], m1.inputs[1])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = forca; nt.links.new(m1.outputs[0], m2.inputs[0])
    em.inputs['Color'].default_value = (*cor, 1); nt.links.new(m2.outputs[0], em.inputs['Strength'])
    nt.links.new(tr.outputs[0], ad.inputs[0]); nt.links.new(em.outputs[0], ad.inputs[1]); nt.links.new(ad.outputs[0], out.inputs['Surface'])
    _MATS[nome] = m; return m


def raios_luz(n, x0, x1, y0, y1, z_topo, comp, larg, inclinacao=(0.35, 0.15), semente=0, mat=None, camera_pos=None):
    """Planos de feixe de luz voltados para a câmera (billboards fixos), inclinados como o sol."""
    rnd = random.Random(semente); mat = mat or mat_raio_luz(); objs = []
    for i in range(n):
        w = larg * rnd.uniform(0.5, 1.4); L = comp * rnd.uniform(0.7, 1.1)
        v = [(0, 0, 0), (w, 0, 0), (w, 0, L), (0, 0, L)]
        me = bpy.data.meshes.new('raio'); me.from_pydata(v, [], [(0, 1, 2, 3)]); me.materials.append(mat)
        o = ligar(bpy.data.objects.new('raio', me))
        o.location = (rnd.uniform(x0, x1), rnd.uniform(y0, y1), z_topo - L)
        o.rotation_euler = (inclinacao[1], inclinacao[0], 0)
        o.visible_shadow = False
        objs.append(o)
    return objs



def mat_corte_linha_dagua(nome='corte_ld', acima='#efe9da', abaixo='#cfe6ee', linha='#202b57', z0=0.0, esp=0.18, casca=None):
    """Face de corte: tom quente acima da linha d'água, tom frio abaixo (parte submersa) e linha na flutuação."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs[0])
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = z0; nt.links.new(sep.outputs['Z'], lt.inputs[0])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs[6].default_value = srgb(acima); mx.inputs[7].default_value = srgb(abaixo)
    nt.links.new(lt.outputs[0], mx.inputs[0])
    d = nt.nodes.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; d.inputs[1].default_value = z0; nt.links.new(sep.outputs['Z'], d.inputs[0])
    ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; nt.links.new(d.outputs[0], ab.inputs[0])
    ln = nt.nodes.new('ShaderNodeMath'); ln.operation = 'LESS_THAN'; ln.inputs[1].default_value = esp; nt.links.new(ab.outputs[0], ln.inputs[0])
    mx2 = nt.nodes.new('ShaderNodeMix'); mx2.data_type = 'RGBA'; mx2.inputs[7].default_value = srgb(linha)
    nt.links.new(ln.outputs[0], mx2.inputs[0]); nt.links.new(mx.outputs[2], mx2.inputs[6])
    nt.links.new(mx2.outputs[2], p.inputs['Base Color']); p.inputs['Roughness'].default_value = 0.55
    _MATS[nome] = m; return m


def mat_fantasma(nome='fantasma', cor='#3cc6ff', alfa=0.32, brilho=0.9):
    """Volume translúcido (volume deslocado): transparência + emissão suave, bordas mais claras (Fresnel)."""
    if nome in _MATS: return _MATS[nome]
    m = bpy.data.materials.new(nome)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    fr = nt.nodes.new('ShaderNodeLayerWeight'); fr.inputs['Blend'].default_value = 0.35
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = alfa; mr.inputs['To Max'].default_value = min(1, alfa * 2.2)
    nt.links.new(fr.outputs['Facing'], mr.inputs[0])
    mx = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(mr.outputs[0], mx.inputs[0])
    em.inputs['Color'].default_value = srgb(cor); em.inputs['Strength'].default_value = brilho
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
    _MATS[nome] = m; return m


# ---------------------------------------------------------------- metadados para o motor em tempo real
# Cada construtor de material grava seus parâmetros em m['rt'] (JSON). O exportador lê esses metadados
# e o renderizador Three.js reproduz o mesmo material (ruído de cor/rugosidade, relevo, faixas, água...).
import json as _json, inspect as _inspect


def _jsonavel(v):
    if isinstance(v, dict): return {k: _jsonavel(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)): return [_jsonavel(x) for x in v]
    if isinstance(v, (int, float, str, bool)) or v is None: return v
    return str(v)


def _rotular(f, tipo):
    sig = _inspect.signature(f)
    def g(*a, **k):
        m = f(*a, **k)
        try:
            if 'rt' not in m.keys():
                b = sig.bind(*a, **k); b.apply_defaults()
                m['rt'] = _json.dumps(dict(tipo=tipo, **{kk: _jsonavel(v) for kk, v in b.arguments.items()}))
        except Exception:
            pass
        return m
    g.__wrapped__ = f
    return g


def mat_espuma(nome, forma=0, x0=0.0, vel=6.0, decai=20.0, larg=2.0, abre=0.35, z0=0.0, alt=1.5, dens=0.9, escala=0.5, cor='#eef6fa'):
    """Espuma procedural (motor em tempo real): forma 0 onda de proa, 1 esteira, 2 faixa do costado, 3 crista na roda de proa."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome); p.inputs['Base Color'].default_value = srgb(cor); p.inputs['Alpha'].default_value = 0.6
    _MATS[nome] = m; return m


def mat_brilho(nome, cor='#ffffff', forca=1.5, raio=1.0, queda=2.0, tremor=0.3, semente=0.0):
    """Brilho aditivo localizado (motor em tempo real): intensidade cai do centro (origem do objeto) até 'raio' e tremula por
    quadro. Simula o arco de solda e a luz que ele joga nas chapas próximas, sem luz dinâmica."""
    if nome in _MATS: return _MATS[nome]
    m, nt, p = _mat(nome)
    p.inputs['Base Color'].default_value = srgb(cor); p.inputs['Emission Color'].default_value = srgb(cor)
    p.inputs['Emission Strength'].default_value = forca; p.inputs['Alpha'].default_value = 0.3
    _MATS[nome] = m; return m


for _nome, _tipo in [('mat_pintura', 'pintura'), ('mat_brilho', 'brilho'), ('mat_espuma', 'espuma'), ('mat_aco', 'aco'), ('mat_emissivo', 'emissivo'), ('mat_concreto', 'concreto'),
                     ('mat_areia', 'areia'), ('mat_agua', 'agua'), ('mat_vidro_escuro', 'vidro'), ('mat_conteiner', 'conteiner'),
                     ('mat_faixas_z', 'faixas_z'), ('mat_bolha', 'bolha'), ('mat_raio_luz', 'raio_luz'),
                     ('mat_corte_linha_dagua', 'corte_ld'), ('mat_fantasma', 'fantasma')]:
    globals()[_nome] = _rotular(globals()[_nome], _tipo)

_ceu_original = ceu_estilizado
def ceu_estilizado(*a, **k):
    o = _ceu_original(*a, **k)
    b = _inspect.signature(_ceu_original).bind(*a, **k); b.apply_defaults()
    bpy.context.scene.world['rt'] = _json.dumps({kk: _jsonavel(v) for kk, v in b.arguments.items()})
    return o



def rotulo(texto, ancora, dx=0.0, dy=-0.06, alinhar='esq'):
    """Rótulo na identidade da marca, desenhado pelo motor em tempo real: ponto na âncora 3D,
    linha-guia e pílula deslocada (dx, dy em fração da largura/altura da tela)."""
    ROTULOS.append(dict(texto=texto, ancora=[float(v) for v in ancora], dx=dx, dy=dy, alinhar=alinhar))


def tracejado(nome, p0, p1, mat, traco=1.4, vao=0.9, r=0.12):
    """Linha tracejada 3D entre p0 e p1 (cilindros curtos)."""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length; u = d.normalized(); objs = []; t = 0.0
    while t < L - 1e-3:
        a = p0 + u * t; b = p0 + u * min(t + traco, L)
        objs.append(tubo(nome, [tuple(a), tuple(b)], r=r, mat=mat)); t += traco + vao
    return objs
