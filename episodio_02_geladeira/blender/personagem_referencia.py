"""Folha de referência do personagem do Ep. 02 (mesmo motor e mesma luz da cozinha, em estúdio neutro).
Cada QUADRO do segmento exportado é uma vista: 0–3 corpo inteiro (frente, 3/4, perfil, costas), 4–6 close de expressão
(neutro, atento olhando o interior, curioso), 7 corpo inteiro na visão térmica (pele 33 °C, roupa 30 °C).
Uso: PYTHONPATH=<bpy> python3 personagem_referencia.py  → episodio/cenas/REF_PERS/"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import lib, mats02 as M, ep_base as B, cenas02 as C, personagem as PE

AQUI = os.path.dirname(os.path.abspath(__file__)); SAIDA = os.path.join(AQUI, '..', 'episodio', 'cenas', 'REF_PERS')
s, cam = C.nova(); C.luzes_cozinha()
fundo = M.pintura('estudio', '#b9b4ab', rug=0.95, temp=25.0)
lib.caixa('estudio_piso', (8, 8, 0.02), (0, 0, -0.01), fundo); lib.caixa('estudio_fundo', (8, 0.02, 4), (0, 3.0, 2.0), fundo)
P = PE.montar()
VISTAS = [  # (yaw do personagem, câmera pos, alvo, lente, estado extra)
    (180, (0, -3.4, 1.0), (0, 0, 0.84), 40, {}),
    (180 - 35, (0, -3.4, 1.0), (0, 0, 0.84), 40, {}),
    (180 - 90, (0, -3.4, 1.0), (0, 0, 0.84), 40, {}),
    (0, (0, -3.4, 1.0), (0, 0, 0.84), 40, {}),
    (180 - 15, (0, -1.05, 1.55), (0, 0, 1.53), 50, {}),
    (180 - 15, (0, -1.05, 1.55), (0, 0, 1.53), 50, dict(cab=(28, -6, 0), olhar=(18, -6), sobr=(0.25, 0.1), incl=4)),
    (180 - 15, (0, -1.05, 1.55), (0, 0, 1.53), 50, dict(cab=(-10, 8, -9), olhar=(-12, 10), sobr=(0.9, 0.55))),
    (180 - 25, (0, -3.4, 1.0), (0, 0, 0.84), 40, dict(braco_d=('fk', 35, 10, 60))),
]
def anim(g):
    i = min(int(round((g - 0.0) * B.FPS)), len(VISTAS) - 1)
    yaw, cp, ca, l, ex = VISTAS[i]
    PE.posar(P, dict(dict(yaw=yaw, braco_d=('fk', 6, 7, 14), braco_e=('fk', 6, 7, 14)), **ex)); B.camera_em(cam, cp, ca, l)
    return g
curvas = dict(uTermico=[[6.5 / B.FPS, 0], [6.6 / B.FPS, 1]], uRevela=[[0, 0]])
meta = C.meta_comum(curvas, dict(plano='REF_PERS', seq='R', g0p=0.0, g1p=(len(VISTAS) - 1) / B.FPS))
os.makedirs(SAIDA, exist_ok=True)
B.exportar_seg(SAIDA, 0.0, (len(VISTAS) - 1) / B.FPS, anim, extra=meta)
print('ok', SAIDA)
