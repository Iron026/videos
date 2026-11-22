"""Rodada 8: faces COINCIDENTES entre peças cortadas (z-fighting pelo corte): para cada par de malhas com material de corte,
faces alinhadas aos eixos no MESMO plano (|Δ| < 0,05 mm) com área de sobreposição > 1 mm². Faces de sentidos opostos
(encostadas) brigam quando o corte expõe a tampa de uma diante da face da outra; mesmo sentido = z-fighting direto.
Uso: PYTHONPATH=<bpy> python3 coplanares.py [FOLGA_GAB] → imprime os pares e grava ../relatorios/coplanares.json"""
import sys, json, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import geladeira as G
G.FOLGA_GAB = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0; G.FOLGA_PORTA = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
G.montar(parede_traseira=True); bpy.context.view_layer.update()
CORTE = {'gab_branco', 'forro', 'vedacao', 'plast_cinza', 'porta_int', 'prateleira_vidro', 'armario', 'plastico_cinza'}
faces = []
for o in bpy.data.objects:
    if o.type != 'MESH' or not o.data.materials or not any(m and m.name.split('.')[0] in CORTE for m in o.data.materials): continue
    M = o.matrix_world; R = M.to_3x3()
    for p in o.data.polygons:
        n = (R @ p.normal).normalized(); ax = max(range(3), key=lambda i: abs(n[i]))
        if abs(n[ax]) < 0.999: continue
        vs = [M @ o.data.vertices[i].co for i in p.vertices]; c = sum(v[ax] for v in vs) / len(vs)
        o1, o2 = [i for i in range(3) if i != ax]
        r = (min(v[o1] for v in vs), min(v[o2] for v in vs), max(v[o1] for v in vs), max(v[o2] for v in vs))
        faces.append((o.name, ax, c, 1 if n[ax] > 0 else -1, r))
pares = {}
porplano = {}
for f in faces: porplano.setdefault((f[1], round(f[2] / 5e-5)), []).append(f)
for k, fs in porplano.items():
    for a, b in itertools.combinations(fs, 2):
        if a[0] == b[0]: continue
        r1, r2 = a[4], b[4]; w = min(r1[2], r2[2]) - max(r1[0], r2[0]); h = min(r1[3], r2[3]) - max(r1[1], r2[1])
        if w > 1e-3 and h > 1e-3:
            ch = tuple(sorted((a[0], b[0])))
            tipo = 'encostadas' if a[3] != b[3] else 'mesmo sentido'
            e = pares.setdefault(ch, dict(area_mm2=0.0, tipo=tipo, eixo='xyz'[a[1]], plano_m=round(a[2], 4)))
            e['area_mm2'] = round(e['area_mm2'] + w * h * 1e6, 1)
for (a, b), e in sorted(pares.items(), key=lambda kv: -kv[1]['area_mm2']):
    print(f"{a:22s} × {b:22s} {e['tipo']:13s} plano {e['eixo']}={e['plano_m']:+.4f}  área {e['area_mm2']:9.1f} mm²")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios', f"coplanares_folga{G.FOLGA_GAB}.json")
json.dump([dict(a=a, b=b, **e) for (a, b), e in pares.items()], open(out, 'w'), ensure_ascii=False, indent=1); print('pares', len(pares))
