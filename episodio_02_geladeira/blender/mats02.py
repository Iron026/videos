"""Materiais e geometria próprios do Ep. 02 (sobre a base lib.py do Ep. 01).

Novos tipos de material para o motor (motor/render3.js):
  circuito  tubo do circuito de refrigeração. Aparência normal (cobre, aço pintado de preto, alumínio) e, quando a curva
            'revela' sobe, o FLUIDO: cor = temperatura (tabela do modelo científico, pela posição s no circuito), aparência
            = fase (líquido contínuo, mistura com bolhas, vapor ralo) e padrão que se move no sentido do fluxo.
  calor     feixe de calor (energia transferida): faixa âmbar contínua com ondas que andam no sentido do quente → frio.
            NUNCA partículas. Visível entre p0 e p1 (curvas no tempo) ao longo do percurso do feixe.
  trabalho  pulsos violeta (energia elétrica / trabalho) correndo ao longo do cabo.
Qualquer material pode ter 'temp' (°C, constante) ou curvas {'temp': [[t, °C], ...]} para a VISÃO TÉRMICA.
Geometria: varrer() cria tubos/faixas com o atributo de vértice 'par' = (s ao longo do percurso, coordenada transversal).
"""
import json, math
import bpy
import numpy as np
from mathutils import Vector
import lib

AMBIENTE_C = 25.0


def ajustar(m, **kv):
    """Acrescenta/atualiza metadados do material para o motor (temp, curvas, alfa…)."""
    rt = json.loads(m['rt']) if 'rt' in m.keys() else dict(tipo='generico')
    for k, v in kv.items():
        if k == 'curvas': rt.setdefault('curvas', {}).update(v)
        else: rt[k] = v
    m['rt'] = json.dumps(rt); return m


def _novo(nome, tipo, cor='#888888', **kv):
    if nome in lib._MATS: return lib._MATS[nome]
    m, nt, p = lib._mat(nome); p.inputs['Base Color'].default_value = lib.srgb(cor)
    m['rt'] = json.dumps(dict(tipo=tipo, cor=cor, **kv)); lib._MATS[nome] = m; return m


def pintura(nome, cor, rug=0.45, temp=None, coat=0.0, variacao=0.04, escala_var=2.0, alfa=1.0, metal=0.0):
    m = lib.mat_pintura(nome, cor, rug=rug, coat=coat, variacao=variacao, escala_var=escala_var, metal=metal)
    kv = {}
    if temp is not None: kv['temp'] = temp
    if alfa < 1: kv['alfa'] = alfa
    return ajustar(m, **kv) if kv else m


def circuito(nome, base='cobre', temp=None):
    """base: cobre | preto (aço pintado, condensador) | aluminio (evaporador) | latao."""
    cores = dict(cobre=('#b87348', 0.32, 1.0), preto=('#1c1d20', 0.55, 0.0), aluminio=('#c9ccd1', 0.38, 1.0), latao=('#a88a4a', 0.35, 1.0))
    c, rug, met = cores[base]
    return _novo(nome, 'circuito', cor=c, rug=rug, metal=met, base=base, **({} if temp is None else dict(temp=temp)))


def calor(nome, cor='#ffc24a', largura=1.0, onda=6.0, vel=0.6, forca=1.0):
    """onda: ondas por unidade de s; vel: deslocamento de s por segundo (sentido quente → frio)."""
    return _novo(nome, 'calor', cor=cor, largura=largura, onda=onda, vel=vel, forca=forca)


def trabalho(nome, cor='#9a6bff', onda=10.0, vel=1.2, forca=1.2):
    return _novo(nome, 'trabalho', cor=cor, onda=onda, vel=vel, forca=forca)


# ------------------------------------------------------------------ geometria com parâmetro de percurso
def comprimento(pts):
    return sum((Vector(pts[i + 1]) - Vector(pts[i])).length for i in range(len(pts) - 1))


def suavizar(pts, raio=0.02, n=4):
    """Arredonda as quinas de uma poligonal (curvas de tubo com raio ~'raio')."""
    P = [Vector(p) for p in pts]; out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        u, v = (a - b), (c - b)
        if u.length < 1e-6 or v.length < 1e-6: continue
        r = min(raio, u.length * 0.45, v.length * 0.45)
        p0, p1 = b + u.normalized() * r, b + v.normalized() * r
        for k in range(n + 1):
            t = k / n; out.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * b + t * t * p1)
    out.append(P[-1])
    return [tuple(p) for p in out]


def reamostrar(pts, passo):
    P = [Vector(p) for p in pts]; out = [P[0]]
    for i in range(len(P) - 1):
        d = P[i + 1] - P[i]; n = max(1, int(math.ceil(d.length / passo)))
        for k in range(1, n + 1): out.append(P[i] + d * (k / n))
    return [tuple(p) for p in out]


def varrer(nome, pts, r, mat, s0=0.0, s1=1.0, lados=10, achatar=1.0, faixa=False, colecao=None, tampa=False, fluxo=None, passo=None):
    """Tubo (ou faixa plana se faixa=True) ao longo da poligonal pts. Atributo 'par' = (s, ângulo/coord. transversal),
    com s indo de s0 a s1 proporcional ao comprimento. Moldura de referência por transporte paralelo (sem torções)."""
    if passo: pts = reamostrar(pts, passo)
    P = [Vector(p) for p in pts]
    L = [0.0]
    for i in range(len(P) - 1): L.append(L[-1] + (P[i + 1] - P[i]).length)
    tot = max(L[-1], 1e-9)
    T = []
    for i in range(len(P)):
        a = P[max(i - 1, 0)]; b = P[min(i + 1, len(P) - 1)]; T.append((b - a).normalized())
    ref = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    N = [(ref - T[0] * ref.dot(T[0])).normalized()]
    for i in range(1, len(P)):
        n = N[-1] - T[i] * N[-1].dot(T[i]); N.append(n.normalized() if n.length > 1e-8 else N[-1])
    verts, faces, par = [], [], []
    k = 2 if faixa else lados
    for i, p in enumerate(P):
        B = T[i].cross(N[i])
        s = s0 + (s1 - s0) * L[i] / tot
        for j in range(k):
            if faixa:
                w = (j * 2 - 1) * r; verts.append(tuple(p + B * w)); par.append((s, float(j)))
            else:
                a = 2 * math.pi * j / k
                verts.append(tuple(p + (N[i] * math.cos(a) * achatar + B * math.sin(a)) * r)); par.append((s, a / (2 * math.pi)))
    for i in range(len(P) - 1):
        if faixa: faces.append((i * 2, i * 2 + 1, i * 2 + 3, i * 2 + 2))
        else:
            for j in range(k):
                j2 = (j + 1) % k; faces.append((i * k + j, i * k + j2, (i + 1) * k + j2, (i + 1) * k + j))
    if tampa and not faixa:
        for e, i in ((0, 0), (1, len(P) - 1)):
            c = len(verts); verts.append(tuple(P[i])); par.append(((s0, s1)[e], 0.0))
            for j in range(k):
                j2 = (j + 1) % k
                faces.append((c, i * k + j2, i * k + j) if e == 0 else (c, i * k + j, i * k + j2))
    o = lib.malha(nome, verts, faces, mat, suave=not faixa, angulo=70)
    at = o.data.attributes.new('par', 'FLOAT2', 'POINT'); at.data.foreach_set('vector', np.array(par, np.float32).ravel())
    if colecao: (bpy.context.scene.collection.objects.unlink(o), colecao.objects.link(o))
    if fluxo is not None:   # coordenada de fluxo u(s) por vértice (fluido no circuito): exportada em aGen.z
        pz = o.data.attributes.new('parz', 'FLOAT', 'POINT'); pz.data.foreach_set('value', np.array([fluxo(p[0]) for p in par], np.float32))
    o['comprimento'] = tot
    return o


def helice(c, r, z0, z1, voltas, n=24, eixo='z'):
    pts = []
    for i in range(int(voltas * n) + 1):
        a = 2 * math.pi * i / n; t = i / (voltas * n); z = z0 + (z1 - z0) * t
        pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), z) if eixo == 'z' else (c[0] + r * math.cos(a), z, c[2] + r * math.sin(a)))
    return pts
