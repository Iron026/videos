"""Benchmark curto do Cycles (CPU) no Quadro 2, com o mesmo deslocamento de câmera do benchmark em tempo real.
Uso: python3 bench_cycles.py <pct> <amostras> <n_quadros> <saida_png>
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import lib, quadros

pct, am, n, saida = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
t0 = time.time(); quadros.quadro2(); montagem = time.time() - t0
s = bpy.context.scene; cam = s.camera; base = cam.location.copy()
s.render.resolution_percentage = pct; s.cycles.samples = am
tempos = []
for i in range(n):
    cam.location = base + Vector((-0.8 * i, 0.5 * i, 0.1 * i))
    s.render.filepath = saida if i == 0 else saida.replace('.png', f'_{i}.png')
    t = time.time(); bpy.ops.render.render(write_still=True); tempos.append(time.time() - t)
print('BENCH ' + json.dumps(dict(pct=pct, amostras=am, W=s.render.resolution_x * pct // 100, H=s.render.resolution_y * pct // 100,
                                  montagem_s=round(montagem, 2), tempos_s=[round(x, 2) for x in tempos])))
