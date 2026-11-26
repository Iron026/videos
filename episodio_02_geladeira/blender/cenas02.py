"""Cenas do Ep. 02: montagem (geladeira.montar), luz de interior, câmera por planos (ep_base) e exportação por segmento
para o motor (motor/render3.js). Tempo GLOBAL do episódio (s); os tempos dos planos vêm de decupagem/planos.py (âncoras
em palavras: trocar a narração recalcula tudo).
Uso: PYTHONPATH=<bpy> python3 cenas02.py <cena|teste> [pasta_saida]"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import lib, mats02 as M, geladeira as G, ep_base as B

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, '..')
sys.path.insert(0, os.path.join(RAIZ, 'decupagem'))
import planos as PL
PLANOS = {p['id']: p for p in PL.resolvidos()['planos']}


def luzes_cozinha():
    """Fim de tarde: sol quente entrando pela janela da parede esquerda + céu suave + luminária de teto (preenchimento)."""
    lib.ceu_estilizado(sol_elev=20, sol_rot=190, zenite='#7a9cc4', meio='#b9cde0', horizonte='#efe3d0', abaixo='#8a8178',
                       forca=1.0, sol_forca=4.2, nuvens=0.0, sol_cor=(1.0, 0.84, 0.64))
    lib.luz_area((-0.4, -1.6, 2.6), (-0.2, -0.6, 0.0), tam=1.2, energia=140, cor=(1.0, 0.93, 0.84))
    lib.luz_area((1.4, -2.6, 1.8), (0.0, 0.0, 0.8), tam=1.5, energia=60, cor=(0.88, 0.92, 1.0))


def lampada_interna():
    d = bpy.data.lights.new('lampada', 'POINT'); d.energy = 6.0; d.color = (1.0, 0.96, 0.9)
    o = bpy.data.objects.new('lampada', d); bpy.context.scene.collection.objects.link(o); o.location = (0.0, -0.12, 1.12)
    return o


def nova(lente=30):
    s = lib.nova_cena(); s.render.resolution_x, s.render.resolution_y = 1080, 1920
    cam = lib.camera((0.35, -2.4, 1.15), (0, -0.1, 0.8), lente=lente)
    return s, cam


def meta_comum(curvas, extra=None):
    m = dict(fluido=G.tabela_fluido(), curvas=curvas, env=0.35, perto=0.01, longe=60,
             # polimento: reflexos da própria cozinha, sombras das luzes internas, oclusão na escala da cozinha
             env_pos=[-0.35, -1.55, 1.35], env_cena=1.0, sombra_areas=True, ao_raio=0.35, ao_espessura=0.5)
    if extra: m.update(extra)
    return m


def teste(pasta):
    """Três quadros de estilo: (0) cozinha, porta aberta; (1) visão térmica; (2) circuito revelado com corte."""
    s, cam = nova(); luzes_cozinha(); lampada_interna()
    obj = G.montar(parede_traseira=True)
    for o in list(obj['gab'].values()):
        for ms in o.material_slots: M.ajustar(ms.material, corte=True)
    for o in bpy.data.objects:
        if o.name.startswith('porta_') and o.type == 'MESH':
            for ms in o.material_slots: M.ajustar(ms.material, corte=True)
    piv = obj['porta']
    chaves = [(0.0, (0.55, -2.25, 1.12), (-0.05, -0.15, 0.80), 30), (1.0, (0.55, -2.25, 1.12), (-0.05, -0.15, 0.80), 30),
              (2.0, (1.25, -1.15, 1.30), (0.0, 0.05, 0.78), 30)]
    def anim(g):
        piv.rotation_euler = (0, 0, math.radians(100))
        B.camera_planos(cam, [(0.0, [chaves[0], chaves[0]]), (0.99, [chaves[1], chaves[1]]), (1.99, [chaves[2], chaves[2]])], g)
    curvas = dict(uTermico=[[0, 0], [0.9, 0], [1.0, 1], [1.9, 1], [1.95, 0]], uRevela=[[0, 0], [1.9, 0], [2.0, 1]],
                  uTrab=[[0, 0.6]])
    extra = meta_comum(curvas, dict(corte=dict(n=[-1, 0, 0])))
    extra['curvas']['corte'] = [[0, 99], [1.9, 99], [2.0, 0.0]]
    B.exportar_seg(pasta, 0.0, 2.0, anim, extra=extra)
    # inclui os quadros 0, 30 e 60 (t = 0, 1, 2)


if __name__ == '__main__':
    qual = sys.argv[1]; pasta = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RAIZ, 'episodio', 'cenas', qual)
    {'teste': teste}[qual](pasta)
