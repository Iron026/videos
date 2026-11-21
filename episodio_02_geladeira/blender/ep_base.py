"""[Ep. 02 · fork de episodio_01_navio_v2/blender/ep_base.py] Base do episódio: tempo GLOBAL da narração real (s), trilhas de câmera, objetos que surgem,
oclusor de água, rótulos 2D (projetados por quadro e desenhados na montagem) e exportação por segmento."""
import os, json, math
import bpy
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import lib, exportar as exportar_rt2

FPS = 30
AQUI = os.path.dirname(os.path.abspath(__file__))
PALAVRAS = os.path.join(AQUI, '..', 'roteiro', 'palavras.json')   # narração aprovada; sem ela, os tempos provisórios
if not os.path.exists(PALAVRAS): PALAVRAS = os.path.join(AQUI, '..', 'roteiro', 'palavras_provisorio.json')


def suave(t): t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)
def suave5(t): t = min(max(t, 0.0), 1.0); return t * t * t * (t * (6 * t - 15) + 10)
def lerp(a, b, t): return a + (b - a) * t
def V(*a): return Vector(a)


def camera_em(cam, pos, alvo, lente=None):
    cam.location = pos; cam.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    if lente: cam.data.lens = lente


def _cr(p0, p1, p2, p3, u):
    u2, u3 = u * u, u * u * u
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u3)


def trilha(chaves, t):
    """Câmera por chaves [(t, pos, alvo, lente), ...]: Catmull-Rom (movimento contínuo, sem paradas nas chaves),
    com aceleração suave no primeiro trecho e desaceleração no último. Fora do intervalo: segura a chave extrema."""
    if t <= chaves[0][0]: k = chaves[0]; return Vector(k[1]), Vector(k[2]), k[3]
    if t >= chaves[-1][0]: k = chaves[-1]; return Vector(k[1]), Vector(k[2]), k[3]
    i = max(j for j in range(len(chaves) - 1) if chaves[j][0] <= t)
    u = (t - chaves[i][0]) / (chaves[i + 1][0] - chaves[i][0])
    if len(chaves) == 2: u = suave(u)
    elif i == 0: u = u * u * (2 - u)                                                    # sai do repouso
    elif i == len(chaves) - 2: u = u * (1 + u * (1 - u))                              # chega ao repouso
    g = lambda j: chaves[min(max(j, 0), len(chaves) - 1)]
    out = []
    for c in (1, 2):
        p0, p1, p2, p3 = (Vector(g(i - 1)[c]), Vector(g(i)[c]), Vector(g(i + 1)[c]), Vector(g(i + 2)[c]))
        out.append(_cr(p0, p1, p2, p3, u))
    l0, l1, l2, l3 = (g(i - 1)[3], g(i)[3], g(i + 1)[3], g(i + 2)[3])
    return out[0], out[1], _cr(l0, l1, l2, l3, u)


def surge(o, t0, dur=0.4, d=(0, 0, 0), t1=None, dur1=0.4, escala=False):
    """O objeto aparece em t0 (tempo global), vindo de 'd' (deslocamento inicial, m) e/ou crescendo; some em t1."""
    o['surge'] = json.dumps(dict(t0=t0, dur=dur, d=list(d), t1=t1, dur1=dur1, escala=escala))
    return o


def oclusor(o):
    o['oclusor'] = 1; return o


def carregar_frases():
    p = json.load(open(PALAVRAS)); p = p['palavras'] if isinstance(p, dict) else p; fr, cur, ini = [], [], None
    for w in p:
        if ini is None: ini = w['inicio']
        cur.append(w['palavra'])
        if w['palavra'][-1] in '.?!:': fr.append((ini, w['fim'], ' '.join(cur))); cur, ini = [], None
    return fr


class Rotulos:
    """Rótulos da marca desenhados na montagem: âncora 3D (fixa ou função do tempo) projetada a cada quadro."""
    def __init__(self): self.itens = []; self.quadros = []
    def add(self, texto, ancora, t0, t1, dx=0.06, dy=-0.05):
        self.itens.append((texto, ancora, t0, t1, dx, dy))
    def registrar(self, g):
        s = bpy.context.scene; cam = s.camera; q = []
        for (txt, anc, t0, t1, dx, dy) in self.itens:
            if not (t0 - 0.01 <= g <= t1 + 0.35): continue
            p = anc(g) if callable(anc) else Vector(anc)
            u, v, z = world_to_camera_view(s, cam, p)
            a = min(suave((g - t0) / 0.3), 1 - suave((g - t1) / 0.3))
            if z > 0: q.append([txt, round(u, 4), round(1 - v, 4), round(a, 3), dx, dy])
        self.quadros.append(q)


def exportar_seg(pasta, g0, g1, anim, rot=None, extra=None):
    """Exporta o segmento [g0, g1] (tempo global). anim(g) posiciona tudo no tempo global g."""
    n = int(round((g1 - g0) * FPS)) + 1
    rot = rot or Rotulos()
    def af(f):
        g = g0 + f / FPS
        anim(g); bpy.context.view_layer.update(); rot.registrar(g)
        return g
    exportar_rt2.exportar_atual(pasta, n=n, anim=af, fps=FPS, extra_meta=dict(extra or {}, g0=g0, g1=g1), agrupar=True)
    json.dump(dict(g0=g0, fps=FPS, quadros=rot.quadros[:n]), open(os.path.join(pasta, 'rotulos2d.json'), 'w'), ensure_ascii=False)
    print('SEGMENTO', pasta, g0, g1, n, 'quadros')


def camera_planos(cam, planos, g):
    """Decupagem: planos = [(t_inicio, chaves), ...]; corte seco entre planos; dentro do plano, trilha(chaves).
    As chaves podem ser funções do tempo (para acompanhar objetos em movimento): (t, pos, alvo, lente) com pos/alvo
    sendo tuplas ou callables g -> Vector."""
    ativo = [p for p in planos if p[0] <= g + 1e-6]
    chaves = (ativo[-1] if ativo else planos[0])[1]
    ch = [(t, (p(g) if callable(p) else p), (a(g) if callable(a) else a), l) for (t, p, a, l) in chaves]
    p, a, l = trilha(ch, g); camera_em(cam, p, a, l)
