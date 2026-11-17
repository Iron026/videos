"""Estudo de redução de tempo do Cycles: renderiza um quadro com várias configurações e mede o tempo.
Uso: python3 bench_cycles2.py <quadro> <pct> <pasta_saida> <variantes(json)>
Cada variante: {"nome": str, "amostras": int, "limiar": float, "saltos": [max, difuso, brilho, transm] | null,
                "pct": int (opcional, sobrescreve), "quadros": int (opcional, p/ dados persistentes), "persistente": bool}
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import lib, quadros

q, pct, pasta, variantes = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])
os.makedirs(pasta, exist_ok=True)
res = []
for v in variantes:
    quadros.QUADROS[q]()
    s = bpy.context.scene; c = s.cycles; cam = s.camera; base = cam.location.copy()
    s.render.resolution_percentage = v.get('pct', pct)
    c.samples = v['amostras']; c.adaptive_threshold = v.get('limiar', 0.02)
    if v.get('saltos'):
        c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces = v['saltos']
        c.transparent_max_bounces = max(4, v['saltos'][3])
    s.render.use_persistent_data = bool(v.get('persistente', False))
    tempos = []
    for i in range(v.get('quadros', 1)):
        cam.location = base + Vector((-0.8 * i, 0.5 * i, 0.1 * i))
        s.render.filepath = os.path.join(pasta, f"{v['nome']}{'' if i == 0 else '_' + str(i)}.png")
        t = time.time(); bpy.ops.render.render(write_still=True); tempos.append(round(time.time() - t, 2))
    r = dict(v, tempos_s=tempos, W=s.render.resolution_x * s.render.resolution_percentage // 100, H=s.render.resolution_y * s.render.resolution_percentage // 100)
    res.append(r); print('VAR ' + json.dumps(r), flush=True)
json.dump(res, open(os.path.join(pasta, 'cycles.json'), 'w'), indent=1)
