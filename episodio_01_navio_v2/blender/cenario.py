"""Elementos de cenário reutilizáveis: cais, guindastes, chapas, operários, cabeços, defensas, algas, peixes."""
import math, random
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
import lib

AMARELO = '#f3b544'


def cais(x0, x1, y0, y1, topo=2.0, fundo=-12.0, juntas=True, col=None):
    """Muralha de cais em concreto (face voltada para -y em y0) com juntas e capeamento."""
    mc = lib.mat_concreto('concreto_cais', (152, 148, 138))
    mcap = lib.mat_concreto('concreto_cap', (176, 172, 162), escala=0.6)
    objs = [lib.caixa('cais', (x1 - x0, y1 - y0, topo - fundo), ((x0 + x1) / 2, (y0 + y1) / 2, (topo + fundo) / 2), mc, bisel=0.04)]
    objs.append(lib.caixa('cais_cap', (x1 - x0, 1.4, 0.5), ((x0 + x1) / 2, y0 + 0.6, topo + 0.05), mcap, bisel=0.06))
    if juntas:
        mj = lib.mat_pintura('junta', '#6c6a64', rug=0.9)
        z = topo - 1.6
        while z > fundo:
            objs.append(lib.caixa('junta', (x1 - x0, 0.06, 0.08), ((x0 + x1) / 2, y0 - 0.01, z), mj)); z -= 1.6
        x = x0 + 3.0
        while x < x1:
            objs.append(lib.caixa('juntav', (0.08, 0.06, topo - fundo), (x, y0 - 0.01, (topo + fundo) / 2), mj)); x += 6.0
    return objs


def cabeco(pos, escala=1.0):
    my = lib.mat_pintura('cabeco', '#2b2b2e', rug=0.5, metal=0.3)
    ma = lib.mat_pintura('amarelo', AMARELO, rug=0.42)
    x, y, z = pos; e = escala
    return [lib.cilindro('cabeco_b', 0.42 * e, 0.25 * e, (x, y, z + 0.12 * e), ma, lados=20),
            lib.cilindro('cabeco', 0.3 * e, 0.75 * e, (x, y, z + 0.5 * e), my, lados=20),
            lib.cilindro('cabeco_t', 0.42 * e, 0.16 * e, (x, y, z + 0.9 * e), my, lados=20)]


def defensa(pos, r=0.55, rot=0.0):
    """Pneu/defensa de borracha pendurado."""
    mb = lib.mat_pintura('borracha', '#1c1c1e', rug=0.85)
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, radius=r, segments=24)
    me = bpy.data.meshes.new('def'); bm.to_mesh(me); bm.free()
    o = lib.ligar(bpy.data.objects.new('defensa', me)); o.data.materials.append(mb)
    sk = o.modifiers.new('esp', 'SCREW'); sk.steps = 2
    # mais simples: toro via primitiva
    bpy.data.objects.remove(o)
    bm = bmesh.new()
    seg, segm = 24, 10
    verts = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(segm):
            b = 2 * math.pi * j / segm
            rr = r + 0.22 * r * math.cos(b)
            verts.append(bm.verts.new((rr * math.cos(a), 0.45 * r * math.sin(b), rr * math.sin(a))))
    for i in range(seg):
        for j in range(segm):
            a, b2 = verts[i * segm + j], verts[i * segm + (j + 1) % segm]
            c, d = verts[((i + 1) % seg) * segm + (j + 1) % segm], verts[((i + 1) % seg) * segm + j]
            bm.faces.new((a, b2, c, d))
    me = bpy.data.meshes.new('def'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = lib.ligar(bpy.data.objects.new('defensa', me)); o.data.materials.append(mb)
    o.location = pos; o.rotation_euler = (0, 0, rot)
    return o


def pilha_chapas(pos, n=8, tam=(6.0, 2.0, 0.12), rot=0.0, semente=0, mat=None):
    rnd = random.Random(semente)
    m = mat or lib.mat_aco('chapa', (128, 130, 134), rug=0.45)
    ms = lib.mat_pintura('calco', '#7a5a3a', rug=0.9)
    objs = []
    x, y, z = pos
    for k in (-1, 1):
        objs.append(lib.caixa('calco', (0.25, tam[1] + 0.3, 0.25), (x + k * tam[0] * 0.3, y, z + 0.125), ms, rot=(0, 0, rot)))
    z += 0.25
    for i in range(n):
        dx, dy, dr = rnd.uniform(-0.08, 0.08), rnd.uniform(-0.06, 0.06), rnd.uniform(-0.02, 0.02)
        objs.append(lib.caixa('chapa', tam, (x + dx, y + dy, z + tam[2] / 2), m, bisel=0.015, seg=1, rot=(0, 0, rot + dr)))
        z += tam[2] + 0.005
    return objs


def operario(pos, rot=0.0, colete='#f08a24', capacete='#f3b544', escala=1.0):
    """Figura estilizada (escala humana ~1,75 m) para dar escala às cenas."""
    mc = lib.mat_pintura('colete' + colete, colete, rug=0.6); mk = lib.mat_pintura('capacete' + capacete, capacete, rug=0.35)
    mp = lib.mat_pintura('calca', '#2d3a55', rug=0.8); ml = lib.mat_pintura('pele', '#c58c62', rug=0.6)
    x, y, z = pos; e = escala; objs = []
    for s in (-1, 1):
        objs.append(lib.caixa('perna', (0.2 * e, 0.22 * e, 0.85 * e), (x, y + s * 0.13 * e, z + 0.43 * e), mp, bisel=0.06 * e))
    objs.append(lib.caixa('tronco', (0.32 * e, 0.52 * e, 0.62 * e), (x, y, z + 1.17 * e), mc, bisel=0.1 * e))
    for s in (-1, 1):
        objs.append(lib.caixa('braco', (0.16 * e, 0.16 * e, 0.6 * e), (x, y + s * 0.33 * e, z + 1.12 * e), mc, bisel=0.06 * e))
    objs.append(lib.cilindro('cabeca', 0.13 * e, 0.24 * e, (x, y, z + 1.6 * e), ml, lados=14))
    objs.append(lib.cilindro('capacete', 0.17 * e, 0.12 * e, (x, y, z + 1.74 * e), mk, lados=16, r2=0.12 * e))
    for o in objs:
        o.rotation_euler.z = rot
        d = Vector(o.location) - Vector(pos); d.rotate(Matrix.Rotation(rot, 3, 'Z')); o.location = Vector(pos) + d
    return objs


def treliça(nome, p0, p1, largura, altura, mat, n=None, r=0.12):
    """Viga treliçada retangular entre p0 e p1 (banzos + diagonais) — usada nos guindastes."""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length; ex = d.normalized()
    ey = ex.cross(Vector((0, 0, 1)));
    if ey.length < 1e-3: ey = Vector((0, 1, 0))
    ey.normalize(); ez = ey.cross(ex)
    n = n or max(2, int(L / max(altura, 1.0)))
    objs = []
    cantos = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    pts = lambda i, c: p0 + ex * (L * i / n) + ey * (c[0] * largura / 2) + ez * (c[1] * altura / 2)
    for c in cantos: objs.append(lib.tubo(nome + 'b', [tuple(pts(0, c)), tuple(pts(n, c))], r=r * 1.6, mat=mat))
    for i in range(n):
        for a, b in ((0, 3), (1, 2), (0, 1), (3, 2)):
            objs.append(lib.tubo(nome + 'd', [tuple(pts(i, cantos[a])), tuple(pts(i + 1, cantos[b]))], r=r, mat=mat))
        for a, b in ((0, 3), (1, 2), (0, 1), (3, 2)):
            objs.append(lib.tubo(nome + 'v', [tuple(pts(i, cantos[a])), tuple(pts(i, cantos[b]))], r=r, mat=mat))
    return objs


def guindaste_portico(x, vao, altura, y_c=0.0, gancho=None, carga=None, mat=None):
    """Pórtico (goliath) de estaleiro: duas pernas em trilhos, viga-caixão dupla, carro e gancho.
    Vão ao longo de Y, centrado em y_c, posicionado em X = x."""
    ma = mat or lib.mat_pintura('guindaste', AMARELO, rug=0.4, metal=0.1)
    mb = lib.mat_pintura('cabine', '#f6f4ec', rug=0.4); mp = lib.mat_pintura('preto', '#1b1c20', rug=0.6)
    mcabo = lib.mat_aco('cabo', (60, 60, 64), rug=0.4, escovado=False)
    objs = []
    y0, y1 = y_c - vao / 2, y_c + vao / 2
    for y in (y0, y1):
        # pernas em "A" (duas colunas inclinadas) + sapata com rodas
        for dx in (-1, 1):
            p = (x + dx * 5.0, y, altura / 2)
            objs.append(lib.caixa('perna', (1.6, 2.2, altura + 1.0), p, ma, bisel=0.15, rot=(0, math.radians(-dx * 6.5), 0)))
        objs.append(lib.caixa('sapata', (14.0, 2.8, 1.6), (x, y, 0.8), ma, bisel=0.15))
        for dx in (-5.5, -2.5, 2.5, 5.5):
            objs.append(lib.cilindro('roda', 0.55, 0.6, (x + dx, y, 0.45), mp, rot=(math.pi / 2, 0, 0)))
        objs.append(lib.caixa('trilho', (60.0, 0.5, 0.25), (x, y, 0.12), lib.mat_aco('trilho', (110, 110, 112))))
    # vigas-caixão duplas
    for dx in (-2.4, 2.4):
        objs.append(lib.caixa('viga', (2.4, vao + 10, 3.6), (x + dx, y_c, altura + 1.8), ma, bisel=0.18))
    objs.append(lib.caixa('corrimao', (7.5, vao + 10, 0.25), (x, y_c, altura + 3.8), ma, bisel=0.05))
    # cabine do operador
    objs.append(lib.caixa('cabine', (3.0, 3.0, 3.0), (x + 4.2, y0 + 6, altura - 2.0), mb, bisel=0.2))
    objs.append(lib.caixa('vidro', (3.1, 2.6, 1.3), (x + 4.2, y0 + 6, altura - 1.6), lib.mat_vidro_escuro(), bisel=0.08))
    # carro e moitão
    yc = gancho[1] if gancho else y_c
    objs.append(lib.caixa('carro', (7.0, 5.0, 2.2), (x, yc, altura + 4.6), ma, bisel=0.2))
    objs.append(lib.caixa('guincho', (3.0, 3.6, 1.6), (x, yc, altura + 6.4), mb, bisel=0.15))
    zg = gancho[2] if gancho else altura * 0.5
    for dx in (-0.6, 0.6):
        objs.append(lib.tubo('cabo', [(x + dx, yc, altura + 3.5), (x + dx * 0.5, yc, zg + 1.2)], r=0.07, mat=mcabo))
    objs.append(lib.caixa('moitao', (1.4, 1.0, 1.6), (x, yc, zg + 0.8), ma, bisel=0.15))
    objs.append(lib.cilindro('gancho', 0.25, 1.0, (x, yc, zg - 0.3), mp))
    return objs


def guindaste_sts(x, y_trilho_mar, y_trilho_terra, altura=42.0, alcance=48.0, trolley_y=None, z_spreader=30.0, mat=None):
    """Guindaste de cais (STS / portêiner): pórtico com lança sobre o navio (-y = mar)."""
    ma = mat or lib.mat_pintura('sts', AMARELO, rug=0.4, metal=0.1)
    mb = lib.mat_pintura('sts_branco', '#f6f4ec', rug=0.4); mp = lib.mat_pintura('preto', '#1b1c20', rug=0.6)
    mcabo = lib.mat_aco('cabo', (60, 60, 64), rug=0.4, escovado=False)
    objs = []
    for y in (y_trilho_mar, y_trilho_terra):
        for dx in (-9.0, 9.0):
            objs.append(lib.caixa('perna', (1.8, 1.8, altura), (x + dx, y, altura / 2), ma, bisel=0.15))
            objs.append(lib.caixa('truque', (5.0, 2.4, 1.4), (x + dx, y, 0.7), ma, bisel=0.12))
            for k in (-1.5, 1.5):
                objs.append(lib.cilindro('roda', 0.5, 0.5, (x + dx + k, y, 0.45), mp, rot=(math.pi / 2, 0, 0)))
        objs.append(lib.caixa('travessa', (19.8, 1.6, 2.2), (x, y, altura * 0.42), ma, bisel=0.12))
        objs.append(lib.caixa('travessa2', (19.8, 1.6, 2.2), (x, y, altura - 1.1), ma, bisel=0.12))
    for dx in (-9.0, 9.0):
        objs.append(lib.caixa('long', (1.6, abs(y_trilho_terra - y_trilho_mar) + 1.8, 2.0), (x + dx, (y_trilho_mar + y_trilho_terra) / 2, altura * 0.42), ma, bisel=0.12))
    # lança (sobre o mar) e contra-lança (sobre o cais)
    y_ponta = y_trilho_mar - alcance; y_tras = y_trilho_terra + 22
    for dx in (-2.6, 2.6):
        objs.append(lib.caixa('lanca', (1.6, y_tras - y_ponta, 2.8), (x + dx, (y_ponta + y_tras) / 2, altura + 1.4), ma, bisel=0.15))
    # torre (A-frame) e tirantes
    for dx in (-9.0, 9.0):
        objs.append(lib.tubo('torreA', [(x + dx, y_trilho_mar, altura), (x + dx * 0.4, (y_trilho_mar + y_trilho_terra) / 2, altura + 20)], r=0.7, mat=ma))
        objs.append(lib.tubo('torreB', [(x + dx, y_trilho_terra, altura), (x + dx * 0.4, (y_trilho_mar + y_trilho_terra) / 2, altura + 20)], r=0.7, mat=ma))
    topo = (x, (y_trilho_mar + y_trilho_terra) / 2, altura + 20)
    for dx in (-2.6, 2.6):
        for yy in (y_ponta + 4, y_trilho_mar - alcance * 0.45, y_tras - 2):
            objs.append(lib.tubo('tirante', [(topo[0] + dx * 0.6, topo[1], topo[2]), (x + dx, yy, altura + 2.8)], r=0.16, mat=mb))
    # casa de máquinas
    objs.append(lib.caixa('casa_maq', (9.0, 12.0, 5.0), (x, y_tras - 7, altura + 5.3), mb, bisel=0.2))
    # carro, cabine, cabos e spreader
    ty = trolley_y if trolley_y is not None else y_trilho_mar - alcance * 0.5
    objs.append(lib.caixa('carro', (7.0, 5.0, 1.6), (x, ty, altura - 0.2), ma, bisel=0.15))
    objs.append(lib.caixa('cabine', (2.6, 3.0, 2.8), (x + 2.0, ty - 1.0, altura - 2.6), mb, bisel=0.18))
    objs.append(lib.caixa('cabine_v', (2.7, 2.6, 1.2), (x + 2.0, ty - 1.0, altura - 2.3), lib.mat_vidro_escuro(), bisel=0.06))
    for dx in (-2.4, 2.4):
        for dy in (-1.0, 1.0):
            objs.append(lib.tubo('cabo', [(x + dx * 0.4, ty + dy * 0.5, altura - 1.0), (x + dx, ty + dy, z_spreader + 1.2)], r=0.05, mat=mcabo))
    objs.append(lib.caixa('spreader', (12.4, 2.6, 0.7), (x, ty, z_spreader + 0.95), ma, bisel=0.1))
    objs.append(lib.caixa('spreader_c', (3.0, 2.0, 0.8), (x, ty, z_spreader + 1.6), mp, bisel=0.1))
    return objs


def alga(nome, base, altura, mat, semente=0, curva=0.6):
    rnd = random.Random(semente); pts = []
    x, y, z = base
    for i in range(9):
        t = i / 8
        pts.append((x + curva * math.sin(t * 2.4 + rnd.uniform(0, 1)) * t, y + 0.3 * math.sin(t * 3 + semente), z + altura * t))
    o = lib.tubo(nome, pts, r=0.11, mat=mat)
    o.data.bevel_resolution = 1
    # afinar no topo
    o.data.splines[0].points[-1].radius = 0.2
    for i, p in enumerate(o.data.splines[0].points): p.radius = 1.6 - 1.4 * i / 8
    return o


def peixe(pos, tam, rot, mat):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * 1.0, v.co.y * 0.32, v.co.z * 0.45))
    # cauda
    a = bm.verts.new((-0.9, 0, 0)); b = bm.verts.new((-1.6, 0, 0.45)); c = bm.verts.new((-1.6, 0, -0.45))
    bm.faces.new((a, b, c))
    me = bpy.data.meshes.new('peixe'); bm.to_mesh(me); bm.free()
    o = lib.ligar(bpy.data.objects.new('peixe', me)); o.data.materials.append(mat)
    o.location = pos; o.scale = (tam, tam, tam); o.rotation_euler = rot
    return o


def cardume(centro, raio, n, tam, mat, semente=0, direcao=0.0):
    rnd = random.Random(semente); objs = []
    for i in range(n):
        p = Vector(centro) + Vector((rnd.gauss(0, raio), rnd.gauss(0, raio * 0.6), rnd.gauss(0, raio * 0.35)))
        objs.append(peixe(tuple(p), tam * rnd.uniform(0.8, 1.2), (0, rnd.uniform(-0.15, 0.15), direcao + rnd.uniform(-0.25, 0.25)), mat))
    return objs


def galpao(pos, tam, cor='#c9ccc8', rot=0.0):
    """Galpão industrial com telhado em duas águas."""
    m = lib.mat_pintura('galpao' + cor, cor, rug=0.6, metal=0.2); mt = lib.mat_pintura('telhado', '#6f7a80', rug=0.5, metal=0.3)
    x, y, z = pos; lx, ly, lz = tam
    objs = [lib.caixa('galpao', tam, (x, y, z + lz / 2), m, bisel=0.1, rot=(0, 0, rot))]
    # portões de enrolar, faixa de janelas e frisos na fachada voltada para +y
    mp = lib.mat_pintura('portao', '#5d6870', rug=0.5, metal=0.3); mj = lib.mat_vidro_escuro()
    mf = lib.mat_pintura('friso', '#202b57', rug=0.5)
    n = max(1, int(lx / 30))
    for k in range(n):
        xx = x - lx / 2 + (k + 0.5) * lx / n
        objs.append(lib.caixa('portao', (min(12, lx / n * 0.6), 0.2, lz * 0.55), (xx, y + ly / 2 + 0.05, z + lz * 0.275), mp))
    objs.append(lib.caixa('janelas', (lx * 0.92, 0.2, 1.4), (x, y + ly / 2 + 0.05, z + lz * 0.78), mj))
    objs.append(lib.caixa('friso', (lx + 0.1, 0.25, 0.8), (x, y + ly / 2 + 0.06, z + lz - 0.6), mf))
    for s in (-1, 1):
        objs.append(lib.caixa('telhado', (lx + 0.6, ly / 2 / math.cos(0.25) + 0.4, 0.3),
                              (x, y + s * ly / 4, z + lz + ly / 4 * math.tan(0.25)), mt, rot=(-s * 0.25, 0, rot)))
    return objs


def arvore(pos, altura=8.0, semente=0):
    """Árvore low-poly facetada (copa em icosfera deformada)."""
    rnd = random.Random(semente)
    mt = lib.mat_pintura('tronco', '#6b4a32', rug=0.9)
    mc = lib.mat_pintura('copa' + str(semente % 3), ['#4f8a3c', '#5f9a45', '#3f7a3a'][semente % 3], rug=0.8, variacao=0.12)
    x, y, z = pos; objs = [lib.cilindro('tronco', 0.25 * altura / 8, altura * 0.45, (x, y, z + altura * 0.22), mt, lados=7, suave=False)]
    for k in range(rnd.randint(1, 3)):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        for v in bm.verts: v.co *= 1 + rnd.uniform(-0.18, 0.18)
        me = bpy.data.meshes.new('copa'); bm.to_mesh(me); bm.free()
        o = lib.ligar(bpy.data.objects.new('copa', me)); o.data.materials.append(mc)
        r = altura * rnd.uniform(0.26, 0.36)
        o.location = (x + rnd.uniform(-0.3, 0.3) * r, y + rnd.uniform(-0.3, 0.3) * r, z + altura * 0.62 + k * r * 0.5); o.scale = (r, r, r * 1.1)
        objs.append(o)
    return objs


def empilhadeira(pos, rot=0.0):
    ma = lib.mat_pintura('empilhadeira', '#f3b544', rug=0.45); mp = lib.mat_pintura('preto', '#1b1c20', rug=0.6)
    x, y, z = pos; objs = []
    objs.append(lib.caixa('emp_corpo', (3.0, 1.6, 1.4), (x, y, z + 1.1), ma, bisel=0.15))
    objs.append(lib.caixa('emp_cabine', (1.2, 1.5, 1.6), (x - 0.4, y, z + 2.6), mp, bisel=0.05))
    objs.append(lib.caixa('emp_torre', (0.25, 1.2, 3.6), (x + 1.6, y, z + 1.9), mp))
    for dy in (-0.4, 0.4): objs.append(lib.caixa('emp_garfo', (1.6, 0.15, 0.1), (x + 2.4, y + dy, z + 0.3), mp))
    for dx in (-1.0, 1.0):
        for dy in (-0.8, 0.8): objs.append(lib.cilindro('emp_roda', 0.4, 0.3, (x + dx, y + dy, z + 0.4), mp, rot=(math.pi / 2, 0, 0)))
    for o in objs:
        d = Vector(o.location) - Vector(pos); d.rotate(Matrix.Rotation(rot, 3, 'Z')); o.location = Vector(pos) + d; o.rotation_euler.z += rot
    return objs


def bandeira(pos, cor='#202b57', altura=8.0):
    mm = lib.mat_aco('mastro', (190, 192, 196), rug=0.3, escovado=False); mb = lib.mat_pintura('bandeira' + cor, cor, rug=0.7)
    x, y, z = pos
    o = [lib.cilindro('mastro', 0.07, altura, (x, y, z + altura / 2), mm, lados=8)]
    vs, fs = [], []
    for i in range(7):
        for j in range(2):
            vs.append((x + i * 0.4, y + 0.25 * math.sin(i * 0.9), z + altura - 0.2 - j * 1.4))
    for i in range(6): fs.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    o.append(lib.malha('bandeira', vs, fs, mb, suave=True))
    return o
