"""Animatic do Episódio 01 (≈19 s): monta as cenas no Blender, define a animação quadro a quadro e exporta
para o motor em tempo real (Three.js v2).  Uso: python3 animatic.py <plano: 1|23> <pasta_saida>

Linha do tempo GLOBAL (s, 30 fps) — narração provisória medida no ritmo da amostra Will - Deep (~140 pal/min):
  Plano 1   0,00–5,60  "Se eu jogar este bloco de aço na água, ele afunda."
  Plano 2   5,25–11,50 "Mas e se eu usar toneladas do mesmo aço para construir um navio?"  (fusão 5,25–5,60)
  Plano 3  11,50–15,15 "Parece impossível. Então vamos montar um."
  Plano 4  14,80–19,50 assinatura com a amostra REAL "De Olho no Invisível. O invisível ganha forma." (HTML)
"""
import sys, os, math, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector, Matrix, Euler
import lib, navio, cenario, quadros, exportar_rt2

FPS = 30
PLANOS = {1: (0.00, 5.60), 23: (5.25, 15.15)}
G = 9.81


def suave(t): t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)
def suave5(t): t = min(max(t, 0.0), 1.0); return t * t * t * (t * (6 * t - 15) + 10)
def lerp(a, b, t): return a + (b - a) * t
def lerpv(a, b, t): return Vector(a).lerp(Vector(b), t)


def remover(nomes_prefixo):
    for o in list(bpy.data.objects):
        if any(o.name.startswith(p) for p in nomes_prefixo): bpy.data.objects.remove(o, do_unlink=True)


def camera_em(cam, pos, alvo, lente=None):
    cam.location = pos; cam.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    if lente: cam.data.lens = lente


# =====================================================================================
# PLANO 1 — o bloco desliza no cais, tomba, cai na água e afunda (física com empuxo, massa adicional e arrasto)
def bloco_trajetoria(by=6.5):
    """Integra o movimento do bloco (aresta 1,6 m, aço 7850 kg/m³) em ar e água. Retorna f(t)->(pos, ângulo)."""
    a = 1.6; V = a ** 3; A = a * a; rs, rw, Cd, Ca = 7850.0, 1025.0, 1.05, 0.5
    z_cais = 2.575 + a / 2
    def leito(x, y): return -6.8 + 0.35 * math.sin(x * 0.45) * math.cos(y * 0.3) + 0.18 * math.sin(x * 1.3 + y * 0.7)
    T_EMP, T_QUEDA = 1.40, 2.30          # empurrado ("jogar") e sai da borda
    x0, x1 = 6.3, 5.15                   # desliza até o centro de massa passar da borda (x = 4,95)
    dt = 1 / 600.0; t = T_QUEDA; x, z, vx, vz = x1, z_cais, -2.3, 0.0; hist = [(t, x, z)]; t_agua = t_fundo = None   # empurrão: sai da borda sem raspar a muralha
    while t < 8.0:
        dentro = z < 0.0
        if dentro and t_agua is None: t_agua = t
        if dentro:
            m = (rs + Ca * rw) * V
            Fz = -(rs - rw) * V * G - 0.5 * rw * Cd * A * vz * abs(vz)
            Fx = -0.5 * rw * Cd * A * vx * abs(vx)
        else:
            m = rs * V; Fz = -rs * V * G; Fx = 0.0
        vz += Fz / m * dt; vx += Fx / m * dt; x += vx * dt; z += vz * dt; t += dt
        zf = leito(x, by) + a / 2 - 0.06
        if z <= zf: z = zf; t_fundo = t; hist.append((t, x, z)); break
        hist.append((t, x, z))
    H = np.array(hist)
    def estado(tt):
        if tt < T_EMP: return Vector((x0, by, z_cais)), 0.0
        if tt < T_QUEDA: return Vector((lerp(x0, x1, suave((tt - T_EMP) / (T_QUEDA - T_EMP))), by, z_cais)), 0.0
        if tt >= t_fundo: return Vector((H[-1, 1], by, H[-1, 2])), math.pi / 2
        xx = float(np.interp(tt, H[:, 0], H[:, 1])); zz = float(np.interp(tt, H[:, 0], H[:, 2]))
        ang = (math.pi / 2) * suave((tt - T_QUEDA) / (t_fundo - T_QUEDA)) ** 0.8   # tomba 90° e pousa numa face
        return Vector((xx, by, zz)), ang
    return estado, t_agua, t_fundo


def plano1(pasta, n=None, tempo=None, camera=None, exportador=None):
    """tempo(f) -> tempo de CENA do quadro f (padrão: tempo real); camera(cam, t_cena, f, info) substitui a câmera v1."""
    quadros.quadro1()
    remover(['bloco', 'bolhas', 'bolhas2', 'bloco_resto'])
    # água sem os anéis estáticos (as ondas do impacto são animadas no shader)
    agua = bpy.data.objects['agua']; bpy.data.objects.remove(agua, do_unlink=True)
    magua = bpy.data.materials['agua1']
    lib.bloco_agua('agua', -16, 5.0, 0, 120, -9.0, magua, res=0.35, amp=0.12, escala=0.35)
    by = 6.5
    estado, t_agua, t_fundo = bloco_trajetoria(by)
    maco = bpy.data.materials['aco_bloco']
    bloco = lib.caixa('bloco_anim', (1.6, 1.6, 1.6), (0, 0, 0), maco, bisel=0.08, seg=3); bloco['anim'] = 1
    # bolhas (sobem a 0,5–1,0 m/s com oscilação) e respingos balísticos no impacto
    rnd = random.Random(7); mb = lib.mat_bolha(); mg = lib.mat_pintura('gota', '#e6f6ff', rug=0.08)
    bolhas = []
    for i in range(46):
        r = rnd.uniform(0.035, 0.12); t0 = t_agua + rnd.uniform(0.0, 1.9) ** 1.3
        o = lib.esfera_simples(f'bolha_{i}', r, mb) if hasattr(lib, 'esfera_simples') else None
        if o is None:
            import bmesh
            bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
            me = bpy.data.meshes.new(f'bolha_{i}'); bm.to_mesh(me); bm.free()
            for pg in me.polygons: pg.use_smooth = True
            o = lib.ligar(bpy.data.objects.new(f'bolha_{i}', me)); o.data.materials.append(mb)
        o['anim'] = 1; bolhas.append((o, t0, rnd.uniform(0.5, 1.0), rnd.uniform(0, 6.28), rnd.uniform(-0.5, 0.5), rnd.uniform(-0.4, 0.4)))
    gotas = []
    p_imp, _ = estado(t_agua)
    for i in range(26):
        import bmesh
        r = rnd.uniform(0.04, 0.09); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        me = bpy.data.meshes.new(f'gota_{i}'); bm.to_mesh(me); bm.free()
        o = lib.ligar(bpy.data.objects.new(f'gota_{i}', me)); o.data.materials.append(mg); o['anim'] = 1
        ang = rnd.uniform(0, 2 * math.pi); vh = rnd.uniform(1.0, 2.8); vz = rnd.uniform(2.5, 5.0)
        gotas.append((o, Vector((p_imp.x + 0.8 * math.cos(ang), by + 0.8 * math.sin(ang), 0.05)), Vector((vh * math.cos(ang), vh * math.sin(ang), vz))))
    cam = bpy.context.scene.camera
    t0p, t1p = PLANOS[1]

    def posicionar(t):                # bloco, bolhas e respingos no tempo de cena t
        p, ang = estado(t)
        bloco.location = p; bloco.rotation_euler = Euler((0.0, -ang, 0.0))
        bpos = p
        for (o, ts, v, fase, ox, oy) in bolhas:
            if t < ts: o.scale = (0, 0, 0); o.location = bpos; continue
            pb, _ = estado(ts); dz = v * (t - ts); zz = pb.z + 0.5 + dz
            if zz > -0.06: o.scale = (0, 0, 0); o.location = (pb.x, by, -0.1); continue
            o.scale = (1, 1, 1); o.location = (pb.x + ox * 0.6 + 0.12 * math.sin(fase + 6 * (t - ts)), by + oy * 0.6, zz)
        for (o, p0, v0) in gotas:
            dtg = t - t_agua
            if dtg < 0: o.scale = (0, 0, 0); o.location = p0; continue
            pp = p0 + v0 * dtg + Vector((0, 0, -0.5 * G * dtg * dtg))
            if pp.z < 0.0 and dtg > 0.05: o.scale = (0, 0, 0)
            else: o.scale = (1, 1, 1)
            o.location = pp
        return p

    if exportador: return exportador(posicionar, cam, dict(bloco=bloco, estado=estado, t_agua=t_agua, t_fundo=t_fundo, by=by, x_imp=p_imp.x))

    def anim(f):
        t = tempo(f) if tempo else t0p + f / FPS
        p = posicionar(t)
        if camera: camera(cam, t, f, dict(bloco=p, t_agua=t_agua, t_fundo=t_fundo, by=by)); return t
        # câmera: meio dentro, meio fora d'água; leve aproximação e inclinação acompanhando a queda
        k = suave5((t - 0.0) / 5.6)
        camera_em(cam, lerpv((2.9, -18.0, 0.9), (2.4, -14.4, -0.9), k), lerpv((3.7, 6.0, 1.0), (2.7, 6.0, -2.6), suave((t - 1.9) / 2.6)), 40)
    exportar_rt2.exportar_atual(pasta, n=n or int(round((t1p - t0p) * FPS)) + 1, anim=anim, fps=FPS,
                                extra_meta=dict(plano=1, t_inicio=t0p, ondas=[dict(x=p_imp.x, y=by, t0=t_agua - t0p)],
                                                eventos=dict(t_agua=t_agua, t_fundo=t_fundo)))
    print('EVENTOS', json.dumps(dict(t_agua=round(t_agua, 3), t_fundo=round(t_fundo, 3), x_imp=round(p_imp.x, 2))))


# =====================================================================================
# PLANOS 2 e 3 — o mesmo estaleiro: vista ampla → close do encaixe do painel
def plano23(pasta, n=None, tempo=None, camera=None, exportador=None):
    """tempo(f) -> (t_global, t_guindaste): remapeia o MESMO movimento do pórtico; camera(cam, t_global, t_guindaste) substitui a v1."""
    quadros.quadro2(off_painel=0.12)
    s = bpy.context.scene
    painel = bpy.data.objects['painel_icado']
    gancho = bpy.data.objects['gancho']; xg = gancho.location.x; yg = gancho.location.y
    def perto(o, r=6.0): return abs(o.location.x - xg) < r or (o.type == 'CURVE')
    # grupo da carga: painel + olhais + manilhas + anel + lingas + moitão + gancho
    grupo = bpy.data.objects.new('grupo_carga', None); lib.ligar(grupo); grupo.location = (xg, yg, gancho.location.z); grupo['anim'] = 1
    bpy.context.view_layer.update()
    membros = [painel] + [o for o in bpy.data.objects if o.name.split('.')[0] in ('olhal', 'manilha', 'anel_gancho', 'linga')] + \
              [o for o in bpy.data.objects if o.name.split('.')[0] in ('moitao', 'gancho') and abs(o.location.x - xg) < 3]
    for o in membros:
        mw = o.matrix_world.copy(); o.parent = grupo; o.matrix_world = mw
    # carro do pórtico (anda em y) e cabos de içamento refeitos como objetos animados (comprimento variável)
    carro = [o for o in bpy.data.objects if o.name.split('.')[0] in ('carro', 'guincho') and abs(o.location.x - xg) < 3]
    for o in carro: o['anim'] = 1
    base_carro = {o.name: o.location.copy() for o in carro}
    for o in list(bpy.data.objects):     # cabos originais (fixos) do pórtico principal
        if o.name.split('.')[0] == 'cabo' and o.type == 'CURVE':
            pts = o.data.splines[0].points
            if abs(pts[0].co.x - xg) < 2.0: bpy.data.objects.remove(o, do_unlink=True)
    mcabo = bpy.data.materials['cabo']
    cabos = []
    for dx in (-0.45, 0.45):
        c = lib.tubo(f'cabo_icamento{dx}', [(0, 0, 0), (0, 0, -1.0)], r=0.07, mat=mcabo); c['anim'] = 1; cabos.append((c, dx))
    moitao = next(o for o in membros if o.name.split('.')[0] == 'moitao')
    z_topo_cabo = 46.0 + 3.5
    g0 = grupo.location.copy(); ydes, zlev = 8.0, 13.0
    # braço do pêndulo: do ponto de giro (gancho) até a borda inferior da chapa
    pm = [o for o in painel.children_recursive if o.type == 'MESH'] + ([painel] if painel.type == 'MESH' else [])
    Lb = g0.z - min((o.matrix_world @ v.co).z for o in pm for v in o.data.vertices)
    cam = s.camera
    t0p, t1p = PLANOS[23]

    def deslocamento(t):
        """(dy, dz, balanço). dy/dz = afastamento do painel em relação à posição final montada.
        Como no estaleiro real: a peça desce POR FORA do casco até a altura final e só então o carro do pórtico
        a leva horizontalmente para dentro do vão (perto da proa o costado é abaulado: descer já no plano do casco
        faria a chapa atravessar as cavernas). A carga inclina como um pêndulo conforme a aceleração do carro."""
        D0 = 2.2   # folga lateral durante a descida (a folga mínima calculada com a forma do casco é ≤ 1,9 m)
        def dy_slide(tt): return D0 * (1 - suave5((tt - 12.5) / 1.9))
        if t < 11.5: dy, dz = (lerp(ydes, D0, suave((t - 5.6) / 3.0)), lerp(zlev, 1.2, suave((t - 5.6) / 5.9)))
        elif t < 12.5: dy, dz = D0, lerp(1.2, 0.0, suave5((t - 11.5) / 1.0))
        else: dy, dz = dy_slide(t), 0.0
        bal = 0.0
        if 12.5 <= t <= 14.4:
            h = 1 / 240.0; acel = (dy_slide(t + h) - 2 * dy_slide(t) + dy_slide(t - h)) / (h * h)
            bal = max(-0.035, min(0.035, -acel / G))   # pêndulo ≈ −a/g, contido pelos cabos-guia (±2°)
            # na frenagem a base balança PARA o casco: os cabos-guia limitam o giro à folga que ainda resta
            # (sem isso a borda inferior atravessaria as cavernas nos últimos centímetros do encaixe)
            if bal < 0: bal = max(bal, -max(0.0, dy - 0.03) / Lb)
        return dy, dz, bal

    def posicionar(t):              # estado do pórtico/carga no tempo do guindaste t
        dy, dz, bal = deslocamento(t)
        grupo.location = g0 + Vector((0, dy - ydes, dz - zlev)); grupo.rotation_euler = (bal, 0, 0)
        for o in carro: o.location = base_carro[o.name] + Vector((0, dy - ydes, 0))
        bpy.context.view_layer.update()
        topo_moitao = moitao.matrix_world @ Vector((0, 0, 0.8))
        for (c, dx) in cabos:
            topo = Vector((xg + dx, topo_moitao.y, z_topo_cabo)); L = topo.z - topo_moitao.z
            c.location = topo; c.scale = (1, 1, L); c.rotation_euler = (0, 0, 0)

    if exportador: return exportador(posicionar, cam, dict(grupo=grupo, painel=painel, xg=xg))

    def anim(f):
        tg, t = tempo(f) if tempo else (None, t0p + f / FPS)
        posicionar(t)
        if camera: camera(cam, tg, t); return None
        if t < 11.5:   # plano 2: vista aérea ampla do estaleiro → aproximação até o enquadramento aprovado
            k = suave5((t - 5.25) / 6.25)
            camera_em(cam, lerpv((232, 138, 92), (158, 34, 11), k), lerpv((30, 0, 6), (87, 6, 17), k), lerp(24, 24, k))
        else:          # plano 3: close no vão do costado, leve aproximação
            k = suave((t - 11.5) / 3.65)
            camera_em(cam, lerpv((97, 35, 25), (93, 32.5, 23), k), lerpv((73, 14.5, 16.5), (73.5, 14.5, 15.5), k), 30)
    exportar_rt2.exportar_atual(pasta, n=n or int(round((t1p - t0p) * FPS)) + 1, anim=anim, fps=FPS, extra_meta=dict(plano=23, t_inicio=t0p))


if __name__ == '__main__':
    p, pasta = int(sys.argv[1]), sys.argv[2]
    {1: plano1, 23: plano23}[p](pasta)
