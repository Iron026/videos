"""Navio porta-contêineres (v2): casco, estrutura interna, superestrutura, carga.

A forma do casco (meia_boca) é a mesma do projeto v1 (src/casco.js), validada na hidrostática:
V(8 m) ≈ 38.689 m³. Acrescentamos bulbo de proa, leme, hélice e detalhes de convés.
Coordenadas do navio: origem na quilha a meia-nau; Z = 0 na quilha, PONTAL no convés.
"""
import math, random
import numpy as np
from mathutils import Vector
import lib

POPA, PROA, MEIA_BOCA, PONTAL, RAIO_BOJO = -100.0, 104.0, 16.0, 18.0, 2.6
CALADO_LEVE, CALADO_CARGA = 8.0, 10.6
CONT = (12.19, 2.44, 2.59)  # contêiner de 40 pés

COR = dict(costado='#1f2a55', antiincrustante='#b0392e', bota='#2b2f36', faixa='#f6f4ec', conves='#5c7366',
           super='#f2efe6', chamine='#202b57', amarelo='#f3b544', primer='#8f8f8a', primer_verm='#9b4a35')
PALETA_CONT = ['#2f5d8a', '#c8442f', '#e0a33a', '#3f7f6e', '#e9e6dc', '#7a8a94', '#8c3b2e', '#2e3f6b', '#d86f2b', '#4f6f3a', '#b9b3a3', '#1f6f8b']


def clamp(v, a, b): return min(b, max(a, v))


def quilha(x):
    v = clamp((-58 - x) / 42, 0, 1); b = clamp((x - 88) / 16, 0, 1)
    return 8.0 * v ** 1.7 + 3.0 * b * b


def limite_proa(z): return 97 + 7 * clamp(z / PONTAL, 0, 1) ** 1.4


def meia_boca(x, z):
    k = quilha(x)
    if z < k - 1e-6 or z > PONTAL + 1e-6 or x < POPA or x > PROA: return 0.0
    xe = limite_proa(z)
    if x >= xe: return 0.0
    u = clamp((x - 38) / (xe - 38), 0, 1); v = clamp((-62 - x) / 38, 0, 1)
    bc = MEIA_BOCA * (1 - u ** 2.1) ** 0.62 * (1 - 0.2 * v * v)
    ub = clamp((x - 28) / (xe - 28), 0, 1)
    bf = MEIA_BOCA * max(1 - ub ** 1.5, 0) ** 0.85 * (1 - clamp((-48 - x) / 52, 0, 1) ** 1.25)
    s = clamp((z - k) / max(PONTAL - k, 1e-3), 0, 1)
    b = bf + (bc - bf) * (1 - (1 - s) ** 2.2)
    r = min(RAIO_BOJO, b * 0.5); h = z - k
    if h < r: b -= r - math.sqrt(max(0, r * r - (r - h) ** 2))
    return max(0.0, b)


def volume_ate(calado, nx=240, nz=60):
    V = 0; dx = (PROA - POPA) / nx
    for i in range(nx):
        x = POPA + (i + 0.5) * dx; k = quilha(x); top = min(calado, PONTAL)
        if top <= k: continue
        dz = (top - k) / nz
        V += sum(2 * meia_boca(x, k + (j + 0.5) * dz) * dz for j in range(nz)) * dx
    return V


# ---------------------------------------------------------------- malha do casco
def _estacoes(n=150, x0=POPA, x1=PROA):
    u = np.linspace(0, 1, n)
    u = 0.5 - 0.5 * np.cos(np.pi * u) * 0.35 + (u - 0.5) * 0.65  # adensa nas extremidades
    return x0 + (x1 - x0) * np.clip(u, 0, 1)


def _secao(x, nz=30, folga=0.0, topo=PONTAL):
    """Pontos (y, z) do anel da seção: bombordo (convés→fundo), quilha, boreste (fundo→convés)."""
    k = quilha(x) + folga; top = topo - (0 if folga == 0 else 0)
    if top <= k + 0.05: return None
    t = np.linspace(0, 1, nz) ** 1.6  # mais pontos perto do fundo (bojo)
    zs = k + (top - k) * t
    lado = [(max(meia_boca(x, z) - folga, 0.0), z) for z in zs]
    if lado[0][0] <= 0.02 and all(p[0] <= 0.02 for p in lado): return None
    port = [(y, z) for y, z in reversed(lado)]
    star = [(-y, z) for y, z in lado]
    return port + [(0.0, k)] + star


def malha_casco(nome, mat, x0=POPA, x1=PROA, folga=0.0, topo=PONTAL, n=150, nz=30):
    """Sólido fechado do casco entre x0 e x1 (folga>0: casco interno, p/ porões)."""
    xs = _estacoes(n, x0, x1); verts, faces, aneis = [], [], []
    for x in xs:
        sec = _secao(x, nz, folga, topo)
        if sec is None: continue
        base = len(verts); verts += [(x, y, z) for y, z in sec]; aneis.append((base, len(sec)))
    m = aneis[0][1]
    for (a, _), (b, _) in zip(aneis, aneis[1:]):
        for j in range(m):
            jj = (j + 1) % m; faces.append((a + j, a + jj, b + jj, b + j))
    a0 = aneis[0][0]; faces.append(tuple(a0 + j for j in range(m)))
    a1 = aneis[-1][0]; faces.append(tuple(a1 + j for j in range(m))[::-1])
    o = lib.malha(nome, verts, faces, mat, suave=True, angulo=32)
    import bpy, bmesh
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.02)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data); bm.free()
    return o


def bulbo(nome, mat, xa=84.0, xn=105.5, W=2.25, Hh=2.9, zc0=3.3, n_sec=40, n_ang=28, expo=2.6):
    """Bulbo de proa fusiforme (não uma esfera): seção superelíptica mais alta que larga, corpo constante
    embutido no casco e nariz elíptico projetando ~8 m à frente da roda de proa, levemente erguido."""
    import bpy
    vs, fs = [], []
    for i in range(n_sec + 1):
        t = i / n_sec; x = xa + (xn - xa) * t
        f = 1.0 if t < 0.5 else math.sqrt(max(0.0, 1 - ((t - 0.5) / 0.5) ** 2.2))
        f = max(f, 0.0)
        w, h = W * f, Hh * (f ** 0.85)
        zc = zc0 + 0.35 * t ** 2                       # nariz ligeiramente erguido
        for j in range(n_ang):
            a = 2 * math.pi * j / n_ang
            c, s_ = math.cos(a), math.sin(a)
            yy = w * math.copysign(abs(c) ** (2 / expo), c)
            zz = h * math.copysign(abs(s_) ** (2 / expo), s_)
            if zz > 0: zz *= 1.0 + 0.25 * (1 - t)        # topo mais cheio, fundindo-se à roda de proa
            vs.append((x, yy, zc + zz))
    for i in range(n_sec):
        for j in range(n_ang):
            a0 = i * n_ang + j; a1 = i * n_ang + (j + 1) % n_ang
            fs.append((a0, a1, a1 + n_ang, a0 + n_ang))
    fs.append(tuple(range(n_ang))[::-1])
    o = lib.malha(nome, vs, fs, mat, suave=True, angulo=60)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
    for pg in o.data.polygons: pg.use_smooth = True
    return o


def mat_casco():
    return lib.mat_faixas_z('casco', [(CALADO_LEVE - 0.2, COR['antiincrustante']), (CALADO_CARGA + 0.9, COR['bota']),
                                      (PONTAL - 1.0, COR['costado']), (PONTAL - 0.55, COR['faixa']), (1e9, COR['costado'])], rug=0.38)


# ---------------------------------------------------------------- partes do navio pronto
def superestrutura(col=None):
    import bpy
    ms = lib.mat_pintura('super', COR['super'], rug=0.4); mj = lib.mat_vidro_escuro()
    mc = lib.mat_pintura('chamine', COR['chamine'], rug=0.4); ma = lib.mat_pintura('amarelo', COR['amarelo'], rug=0.42)
    mp = lib.mat_pintura('preto', '#1b1c20', rug=0.6)
    objs = []
    x0, z0 = -79.0, PONTAL
    andares = [(15.0, 26.0, 2.9), (14.0, 25.0, 2.9), (13.0, 24.0, 2.9), (12.5, 23.0, 2.9), (12.0, 22.0, 2.9)]
    z = z0
    for i, (lx, ly, h) in enumerate(andares):
        objs.append(lib.caixa(f'super{i}', (lx, ly, h), (x0, 0, z + h / 2), ms, bisel=0.12))
        # faixa de janelas (frente e laterais)
        objs.append(lib.caixa(f'jan{i}', (lx + 0.12, ly * 0.86, 0.95), (x0, 0, z + h * 0.58), mj, bisel=0.05))
        objs.append(lib.caixa(f'janL{i}', (lx * 0.82, ly + 0.12, 0.95), (x0, 0, z + h * 0.58), mj, bisel=0.05))
        z += h
    # passadiço com asas
    objs.append(lib.caixa('passadico', (11.0, 2 * MEIA_BOCA + 1.6, 3.0), (x0 + 0.5, 0, z + 1.5), ms, bisel=0.12))
    objs.append(lib.caixa('jan_pass', (11.15, 2 * MEIA_BOCA, 1.3), (x0 + 0.5, 0, z + 1.7), mj, bisel=0.05))
    objs.append(lib.caixa('teto', (11.6, 2 * MEIA_BOCA + 2.0, 0.35), (x0 + 0.5, 0, z + 3.15), ms, bisel=0.08))
    # mastro de radar
    objs.append(lib.caixa('mastro', (1.0, 1.0, 6.0), (x0 - 1, 0, z + 6.2), ma, bisel=0.06))
    objs.append(lib.caixa('radar', (0.6, 6.0, 0.35), (x0 - 1, 0, z + 8.6), mp, bisel=0.05))
    # chaminé
    xc = x0 - 13.5
    objs.append(lib.caixa('chamine', (7.5, 6.5, 11.0), (xc, 0, z0 + 15.0), mc, bisel=0.5, seg=3))
    objs.append(lib.caixa('chamine_faixa', (7.6, 6.6, 1.8), (xc, 0, z0 + 17.2), ma, bisel=0.5, seg=3))
    objs.append(lib.caixa('chamine_topo', (7.0, 6.0, 0.8), (xc, 0, z0 + 20.7), mp, bisel=0.3))
    # baleeira de queda livre (laranja) na popa
    ml = lib.mat_pintura('baleeira', '#ef6c22', rug=0.35)
    b = lib.caixa('baleeira', (8.0, 3.0, 3.0), (-96.0, 0, PONTAL + 4.2), ml, bisel=0.9, seg=3, rot=(0, math.radians(-14), 0))
    objs.append(b)
    objs.append(lib.caixa('rampa', (9.0, 3.6, 0.4), (-96.0, 0, PONTAL + 2.4), ma, bisel=0.08, rot=(0, math.radians(-14), 0)))
    if col:
        for o in objs:
            for c in o.users_collection: c.objects.unlink(o)
            col.objects.link(o)
    return objs


def conves_e_tampas(col=None, com_tampas=True):
    """Convés (castelo de proa, tampas de escotilha, pontes de peação, guinchos)."""
    mc = lib.mat_pintura('conves', COR['conves'], rug=0.7); ma = lib.mat_pintura('amarelo', COR['amarelo'], rug=0.42)
    mt = lib.mat_pintura('tampa', '#3d4a52', rug=0.6); mh = lib.mat_pintura('costado', COR['costado'], rug=0.38)
    objs = []
    # castelo de proa (borda falsa)
    for s in (1, -1):
        pts = []
        for i in range(14):
            x = 74 + i * 2.2
            pts.append((x, s * max(meia_boca(x, PONTAL) - 0.2, 0.3)))
        for i, ((xa, ya), (xb, yb)) in enumerate(zip(pts, pts[1:])):
            L = math.hypot(xb - xa, yb - ya); ang = math.atan2(yb - ya, xb - xa)
            objs.append(lib.caixa(f'borda{s}{i}', (L + 0.1, 0.35, 2.2), ((xa + xb) / 2, (ya + yb) / 2, PONTAL + 1.1), mh, rot=(0, 0, ang)))
    for i, x in enumerate((84, 88)):
        for s in (1, -1):
            objs.append(lib.cilindro(f'guincho{i}{s}', 0.9, 2.2, (x, s * 4.5, PONTAL + 1.0), ma, rot=(math.pi / 2, 0, 0), bisel=0.05))
    objs.append(lib.caixa('mastro_proa', (0.6, 0.6, 9.0), (95.5, 0, PONTAL + 4.5), ma, bisel=0.05))
    if com_tampas:
        for k, xb in enumerate(BAIAS):
            objs.append(lib.caixa(f'tampa{k}', (CONT[0] + 0.6, 2 * MEIA_BOCA - 3.0, 0.9), (xb, 0, PONTAL + 0.45), mt, bisel=0.12))
            # ponte de peação: estrutura aberta (montantes + passarela), não uma parede
            xp = xb + CONT[0] / 2 + 0.8; larg = 2 * MEIA_BOCA - 2.0
            for yy in np.linspace(-larg / 2, larg / 2, 7):
                objs.append(lib.caixa(f'ponte_m{k}', (0.35, 0.35, 4.4), (xp, yy, PONTAL + 2.2), ma, bisel=0.04))
            objs.append(lib.caixa(f'ponte_p{k}', (1.0, larg, 0.25), (xp, 0, PONTAL + 4.4), ma, bisel=0.04))
            objs.append(lib.caixa(f'ponte_c{k}', (0.12, larg, 0.12), (xp + 0.45, 0, PONTAL + 5.3), ma))
    if col:
        for o in objs:
            for c in o.users_collection: c.objects.unlink(o)
            col.objects.link(o)
    return objs


BAIAS = [-58 + i * 13.6 for i in range(10)]  # centros das baías (x)


def carga(nivel_max=4, semente=3, col=None, faltando=0.0, filtro=None):
    """Pilhas de contêineres no convés. faltando: fração de pilhas vazias (para cenas de carregamento)."""
    import bpy
    rnd = random.Random(semente); mat = lib.mat_conteiner()
    sx, sy, sz = CONT
    me = bpy.data.meshes.new('cont'); v = [(-sx / 2, -sy / 2, 0), (sx / 2, -sy / 2, 0), (sx / 2, sy / 2, 0), (-sx / 2, sy / 2, 0),
                                            (-sx / 2, -sy / 2, sz), (sx / 2, -sy / 2, sz), (sx / 2, sy / 2, sz), (-sx / 2, sy / 2, sz)]
    me.from_pydata(v, [], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]); me.materials.append(mat)
    objs = []; nfil = 11
    for k, xb in enumerate(BAIAS):
        for j in range(nfil):
            y = (j - (nfil - 1) / 2) * (sy + 0.08)
            if abs(y) + sy / 2 > meia_boca(xb, PONTAL) - 0.8: continue
            if rnd.random() < faltando: continue
            alt = nivel_max - (1 if rnd.random() < 0.25 else 0) - (1 if abs(j - 5) >= 5 and rnd.random() < 0.5 else 0)
            for n in range(alt):
                if filtro and not filtro(k, j, n): continue
                o = lib.caixa(f'c{k}_{j}_{n}', CONT, (xb, y, PONTAL + 0.9 + n * (sz + 0.03)), dados=me, colecao=col)
                o.color = lib.srgb(rnd.choice(PALETA_CONT))
                lib.chanfro(o, 0.06, 1)
                objs.append(o)
    return objs


def leme_e_helice(col=None):
    mb = lib.mat_aco('bronze', (178, 132, 70), rug=0.25, escovado=False); mh = lib.mat_pintura('antiincrustante', COR['antiincrustante'], rug=0.45)
    objs = [lib.caixa('leme', (5.5, 0.9, 8.0), (-98.0, 0, 4.6), mh, bisel=0.3)]
    hub = lib.cilindro('cubo', 1.0, 1.6, (-93.2, 0, 3.6), mb, rot=(0, math.pi / 2, 0))
    objs.append(hub)
    for i in range(5):
        a = 2 * math.pi * i / 5
        p = lib.caixa(f'pa{i}', (0.35, 1.6, 3.1), (-93.2, 2.0 * math.sin(a), 3.6 + 2.0 * math.cos(a)), mb, bisel=0.15,
                      rot=(a, math.radians(25), 0))
        objs.append(p)
    return objs


# ---------------------------------------------------------------- em construção
def estrutura_construcao(x_chapa=-10.0, mat_casco_primer=None, col=None, passo=3.4):
    """Casco em construção: popa chapeada (primer); vante só com cavernas, longarinas, duplo fundo e anteparas."""
    import bpy
    mp = mat_casco_primer or lib.mat_pintura('primer', COR['primer'], rug=0.55, metal=0.2)
    mr = lib.mat_pintura('primer_verm', COR['primer_verm'], rug=0.6, metal=0.15)
    ma = lib.mat_aco('aco_estrut', (120, 122, 126), rug=0.4, escovado=False)
    objs = []
    casco = malha_casco('casco_chapeado', mp, POPA, x_chapa, n=80)
    objs.append(casco)
    # cavernas: anéis com perfil "L" (aba de 0,8 m), só costado e fundo
    x = x_chapa + passo * 0.5
    i = 0
    while x < 97:
        sec = _secao(x, 22)
        if sec is not None:
            ext = sec; inn = []
            for y, z in ext:
                yi = y - math.copysign(0.75, y) if abs(y) > 0.75 else 0.0
                zi = z + 0.75 if z < quilha(x) + 1.0 else z
                inn.append((yi, zi))
            verts, faces = [], []
            n = len(ext)
            for (y, z) in ext: verts += [(x - 0.18, y, z), (x + 0.18, y, z)]
            for (y, z) in inn: verts += [(x - 0.18, y, z), (x + 0.18, y, z)]
            def V(a, s, j): return a * 2 * n + 2 * j + s
            for j in range(n - 1):
                faces.append((V(0, 0, j), V(0, 0, j + 1), V(1, 0, j + 1), V(1, 0, j)))
                faces.append((V(0, 1, j), V(1, 1, j), V(1, 1, j + 1), V(0, 1, j + 1)))
                faces.append((V(0, 0, j), V(0, 1, j), V(0, 1, j + 1), V(0, 0, j + 1)))
                faces.append((V(1, 0, j), V(1, 0, j + 1), V(1, 1, j + 1), V(1, 1, j)))
            for j in (0, n - 1):
                faces.append((V(0, 0, j), V(1, 0, j), V(1, 1, j), V(0, 1, j)))
            o = lib.malha(f'caverna{i}', verts, faces, mr if i % 6 == 0 else ma, suave=True, angulo=40)
            objs.append(o)
        x += passo; i += 1
    # longarinas (perfis longitudinais) em algumas alturas do costado
    for zl in (4.0, 8.5, 13.0, PONTAL - 0.2):
        for s in (1, -1):
            pts = []
            xx = x_chapa
            while xx < limite_proa(zl) - 1.0:
                b = meia_boca(xx, zl)
                if b > 0.8: pts.append((xx, s * (b - 0.5), zl))
                xx += 2.0
            if len(pts) > 2: objs.append(lib.tubo(f'long{zl}{s}', pts, r=0.28, mat=ma))
    # duplo fundo já chapeado (os blocos de fundo são os primeiros a serem montados)
    df = malha_casco('duplo_fundo', mr, x_chapa, 86.0, topo=2.2, n=70, nz=8)
    objs.append(df)
    pts = [(xx, 0, 2.6) for xx in np.arange(x_chapa, 86, 2.0)]
    objs.append(lib.tubo('quilha_v', pts, r=0.35, mat=ma))
    # anteparas transversais (uma inteira, outra em montagem)
    for xa, completa in ((22.0, True), (48.0, False)):
        sec = _secao(xa, 26)
        if completa:
            vs = [(xa, y, z) for y, z in sec]
            a = lib.malha(f'antepara{xa}', vs, [tuple(range(len(vs)))], mr)
            s = a.modifiers.new('esp', 'SOLIDIFY'); s.thickness = 0.3
            objs.append(a)
    if col:
        for o in objs:
            for c in o.users_collection: c.objects.unlink(o)
            col.objects.link(o)
    return objs


def navio_pronto(col=None, nivel_carga=4, faltando=0.0, carga_filtro=None, com_carga=True):
    mh = mat_casco()
    objs = [malha_casco('casco', mh), bulbo('bulbo', mh)]
    objs += leme_e_helice(); objs += superestrutura(); objs += conves_e_tampas()
    # convés (tampa superior do casco já fechada pelo anel → pinta de verde com uma placa fina)
    mc = lib.mat_pintura('conves', COR['conves'], rug=0.7)
    vs, fs = [], []
    for x in np.arange(POPA + 0.5, 103.5, 1.0):
        b = meia_boca(x, PONTAL)
        if b < 0.2: continue
        vs += [(x, -b + 0.05, PONTAL + 0.02), (x, b - 0.05, PONTAL + 0.02)]
    for j in range(len(vs) // 2 - 1): fs.append((2 * j, 2 * j + 2, 2 * j + 3, 2 * j + 1))
    objs.append(lib.malha('conves', vs, fs, mc))
    if com_carga: objs += carga(nivel_carga, faltando=faltando, filtro=carga_filtro)
    return objs



def marcas_calado(x, lado=1, z_min=5, z_max=14, mat=None):
    """Escala de calado pintada no costado (traços a cada 0,2 m e números a cada metro), coordenadas do navio."""
    import bpy
    mat = mat or lib.mat_pintura('tinta_branca', '#f6f4ec', rug=0.5)
    objs = []
    for i in range(int((z_max - z_min) / 0.2) + 1):
        z = z_min + i * 0.2
        b = meia_boca(x, z) + 0.03
        larg = 0.9 if i % 5 == 0 else 0.45
        objs.append(lib.caixa('traco', (larg, 0.04, 0.1), (x + larg / 2, lado * b, z), mat))
        if i % 5 == 0 and abs(z - round(z)) < 1e-6 and int(round(z)) % 2 == 0:
            cu = bpy.data.curves.new('num', 'FONT'); cu.body = f'{int(round(z))}M'; cu.size = 0.9; cu.extrude = 0.02
            cu.align_y = 'CENTER'
            o = lib.ligar(bpy.data.objects.new('num', cu)); cu.materials.append(mat)
            o.location = (x + 1.2, lado * (b + 0.02), z); o.rotation_euler = (math.pi / 2, 0, 0 if lado < 0 else math.pi)
            if lado > 0: o.location.x = x + 1.2 + 2.0
            objs.append(o)
    return objs


def disco_plimsoll(x, lado=1, mat=None):
    """Marca de borda livre (disco de Plimsoll): centro do disco na linha de carga de verão."""
    mat = mat or lib.mat_pintura('tinta_branca', '#f6f4ec', rug=0.5)
    z0 = CALADO_CARGA; objs = []
    b = lambda z: lado * (meia_boca(x, z) + 0.03)
    pts = [(x + 1.5 * math.cos(a), b(z0 + 1.5 * math.sin(a)), z0 + 1.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
    objs.append(lib.tubo('disco', pts, r=0.09, mat=mat))
    objs.append(lib.caixa('barra', (4.6, 0.04, 0.22), (x, b(z0), z0), mat))
    objs.append(lib.caixa('linha_conves', (3.0, 0.04, 0.22), (x, b(PONTAL - 1.4), PONTAL - 1.4), mat))
    return objs


# ---------------------------------------------------------------- construção em blocos (v3)
def painel_costado(nome, x0, x1, z0, z1, lado, mat, folga=0.0, desloc=0.0, nx=None, nz=None, esp=0.14):
    """Chapa de costado curva entre x0..x1 e z0..z1 (segue a forma real do casco).
    desloc: afasta a chapa do casco (para o bloco içado); folga: recuo nas bordas (costura visível)."""
    import bpy
    x0 += folga; x1 -= folga; z0 += folga; z1 -= folga
    nx = nx or max(2, int((x1 - x0) / 0.8) + 1); nz = nz or max(2, int((z1 - z0) / 0.4) + 1)
    vs, fs = [], []
    for i in range(nx):
        for j in range(nz):
            z = z0 + (z1 - z0) * j / (nz - 1)
            xe = min(x1, limite_proa(z) - 0.05)
            x = x0 + (xe - x0) * i / (nx - 1)
            b = meia_boca(x, z)
            vs.append((x, lado * (b + 0.03 + desloc), z))
    for i in range(nx - 1):
        for j in range(nz - 1):
            a = i * nz + j
            f = (a, a + nz, a + nz + 1, a + 1) if lado > 0 else (a, a + 1, a + nz + 1, a + nz)
            fs.append(f)
    o = lib.malha(nome, vs, fs, mat, suave=True, angulo=50)
    sd = o.modifiers.new('esp', 'SOLIDIFY'); sd.thickness = esp; sd.offset = -1
    return o


def painel_fundo(nome, x0, x1, mat, folga=0.0):
    """Chapeamento do fundo plano (dos dois bordos), do eixo até o início do bojo."""
    vs, fs = [], []
    xs = np.arange(x0 + folga, x1 - folga + 1e-6, 1.0)
    for x in xs:
        k = quilha(x); b = max(meia_boca(x, k + 0.02) - 0.1, 0.0)
        vs += [(x, -b, k - 0.02), (x, b, k - 0.02)]
    for i in range(len(xs) - 1):
        fs.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    o = lib.malha(nome, vs, fs, mat)
    sd = o.modifiers.new('esp', 'SOLIDIFY'); sd.thickness = 0.14
    return o


def construcao_em_blocos(semente=4, faltam=None, vao_cinta=None, forcar=None):
    """Casco em construção por blocos: popa chapeada, meia-nau com painéis faltando, proa em cavernas
    com bulbo e pé de proa chapeados. Retorna (objs, lista_de_painéis_faltantes)."""
    import bpy
    rnd = random.Random(semente)
    mcinza = lib.mat_pintura('primer', COR['primer'], rug=0.55, metal=0.2, variacao=0.08)
    mverm = lib.mat_pintura('primer_verm', COR['primer_verm'], rug=0.6, metal=0.15, variacao=0.08)
    mazul = lib.mat_pintura('primer_azul', '#4f6f8f', rug=0.55, metal=0.15, variacao=0.08)
    ma = lib.mat_aco('aco_estrut', (120, 122, 126), rug=0.4, escovado=False)
    objs = []
    # cavernas (esqueleto) da meia-nau à proa: aparecem através dos vãos e na proa aberta
    for o in estrutura_construcao(x_chapa=-34.0, col=None, passo=3.4):
        if o.name.startswith('casco_chapeado'): bpy.data.objects.remove(o); continue
        objs.append(o)
    # popa (x < -34): bloco inteiro chapeado
    objs.append(malha_casco('popa_chapeada', mcinza, POPA, -34.0, n=70))
    # grade de painéis do costado (blocos de 8 m × ~4,5 m), dos dois bordos
    xs = list(np.arange(-34.0, 98.0, 8.0)); zs = [0.0, 3.0, 7.5, 12.0, PONTAL]
    faltantes = []
    for lado in (1, -1):
        for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
            for j, (za, zb) in enumerate(zip(zs, zs[1:])):
                if xa >= limite_proa(za) - 1.0: continue
                proa = 62.0 <= xa < 82.0
                # regra de montagem: fundo e bojo completos; bloco de proa (x ≥ 82) inteiro;
                # costado alto vai rareando entre a meia-nau e o bloco de proa
                if j == 0 or xa >= 82.0: tem = True
                elif proa: tem = (j == 1)
                else:
                    p = 0.92 - 0.11 * j - 0.010 * max(0, xa)
                    tem = rnd.random() < p
                if forcar is not None and (lado, i, j) in forcar: tem = True
                if faltam is not None and (lado, i, j) in faltam: tem = False
                if not tem:
                    if lado == 1: faltantes.append((xa, xb, za, zb))
                    continue
                cor = mverm if j <= 1 else (mazul if (i + j) % 3 == 0 else mcinza)
                objs.append(painel_costado(f'painel{lado}_{i}_{j}', xa, xb, max(za, quilha(xa) if j == 0 else za), zb, lado, cor, folga=0.04))
    objs.append(painel_fundo('fundo', -34.0, 92.0, mverm))
    # bulbo e pé de proa chapeados (silhueta da proa desde já)
    bb = bulbo('bulbo_c', mverm); objs.append(bb)
    # roda de proa (barra curva) e cinta do convés na proa
    pts = [(limite_proa(z) - 0.15, 0, z) for z in np.linspace(2.5, PONTAL + 0.6, 18)]
    objs.append(lib.tubo('roda_proa', pts, r=0.42, mat=ma))
    for lado in (1, -1):
        xs_c = np.arange(-34, limite_proa(PONTAL) - 0.3, 1.5)
        trechos = [xs_c] if not (vao_cinta and lado == 1) else [xs_c[xs_c < vao_cinta[0]], xs_c[xs_c > vao_cinta[1]]]
        for tr in trechos:   # cinta do convés interrompida sobre o vão do bloco ainda não montado
            if len(tr) > 1: objs.append(lib.tubo('cinta', [(x, lado * (meia_boca(x, PONTAL) - 0.1), PONTAL) for x in tr], r=0.3, mat=ma))
    # convés montado só na popa e em parte da meia-nau
    mc = lib.mat_pintura('conves_primer', '#7d8a86', rug=0.7)
    vs, fs = [], []
    for x in np.arange(POPA + 0.5, -6.0, 1.0):
        b = meia_boca(x, PONTAL)
        if b < 0.2: continue
        vs += [(x, -b + 0.05, PONTAL + 0.02), (x, b - 0.05, PONTAL + 0.02)]
    for j in range(len(vs) // 2 - 1): fs.append((2 * j, 2 * j + 2, 2 * j + 3, 2 * j + 1))
    objs.append(lib.malha('conves_c', vs, fs, mc))
    # superestrutura em montagem (dois pavimentos) e leme
    objs.append(lib.caixa('super_ini', (15, 26, 5.8), (-79, 0, PONTAL + 2.9), mcinza, bisel=0.1))
    objs.append(lib.caixa('super_ini2', (14, 25, 2.9), (-79, 0, PONTAL + 7.25), mazul, bisel=0.1))
    objs.append(lib.caixa('leme_c', (5.5, 0.9, 8.0), (-98.0, 0, 4.6), mverm, bisel=0.3))
    return objs, faltantes
