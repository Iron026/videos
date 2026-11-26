"""Rodada 9: teste numérico do A1 (abertura da porta), mesmo método do testar_leite.py: alcance da mão até o puxador (alvo do
IK × onde a mão chega), braço direito × porta/gabinete, tronco × porta, por quadro (30 fps), de −0,25 s ao fim do A2.
Uso: PYTHONPATH=<bpy> python3 testar_a1.py [r9] → ../relatorios/teste_a1[_r9].json"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
R9 = len(sys.argv) > 1 and sys.argv[1] == 'r9'
if R9: os.environ['CENA_R9'] = '1'
import geladeira as G, encenacao02 as E, personagem as PE
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
obj = G.montar(parede_traseira=True); pers = PE.montar(); bpy.context.view_layer.update()
piv = obj['porta']; ang = E.porta_ang(0.20)
def aabb(o):
    M = o.matrix_world; vs = [M @ v.co for v in o.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)] + [max(v[i] for v in vs) for i in range(3)]
piv.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
ESTAT = {o.name: aabb(o) for o in bpy.data.objects if o.type == 'MESH' and o.parent is None and o.name.startswith(('gab_', 'forro', 'prat_'))}
PORTA = {o.name: aabb(o) for o in bpy.data.objects if o.type == 'MESH' and o.parent == piv}
def dist_caixa(p, b):
    d = [max(b[i] - p[i], 0, p[i] - b[3 + i]) for i in range(3)]
    if any(d): return math.sqrt(sum(x * x for x in d))
    return -min(min(p[i] - b[i], b[3 + i] - p[i]) for i in range(3))
def para_porta(p, a):
    r = -math.radians(a); x, y = p[0] - G.GX, p[1] - G.GY0
    return Vector((G.GX + x * math.cos(r) - y * math.sin(r), G.GY0 + x * math.sin(r) + y * math.cos(r), p[2]))
res = dict(quadros=[]); pior = dict(alcance=0.0, braco=1.0, tronco=1.0)
for i in range(int(round(-0.25 * 30)), int(round(2.73 * 30)) + 1):
    g = i / 30; a = ang(g); piv.rotation_euler = (0, 0, math.radians(a))
    e = E.est_abertura(g); PE.posar(pers, e); bpy.context.view_layer.update()
    mao = pers['mao_d'].matrix_world; alvo = Vector(e['braco_d'][1]) if e['braco_d'][0] == 'ik' else None
    alc = (alvo - mao.translation).length if alvo is not None else 0.0
    alvo_e = Vector(e['braco_e'][1]) if e['braco_e'][0] == 'ik' else None; alc_e = (alvo_e - pers['mao_e'].matrix_world.translation).length if alvo_e is not None else 0.0
    segurando = g < 0.20 + (E.SOLTA_R9 if E.R9 else 0.46) * 1.1   # mão no puxador (contato esperado com o puxador)
    ba, an = pers['braco_d'].matrix_world, pers['antebraco_d'].matrix_world
    pts = [ba @ Vector((0, 0, -PE.BRACO * k / 6)) for k in range(7)] + [an @ Vector((0, 0, -PE.ANTEBRACO * k / 6)) for k in range(7)]
    fb, fbp = 1.0, None
    for p in pts:
        for n, b in ESTAT.items():
            d = dist_caixa(p, b) - 0.045
            if d < fb: fb, fbp = d, n
        for n, b in PORTA.items():
            if segurando and n == 'puxador': continue
            d = dist_caixa(para_porta(p, a), b) - 0.045
            if d < fb: fb, fbp = d, 'porta:' + n
    tr = pers['tronco'].matrix_world.translation; ft = min(dist_caixa(para_porta(Vector((tr.x, tr.y, z)), a), b) - 0.17 for n, b in PORTA.items() for z in (0.9, 1.2))
    q = dict(g=round(g, 3), porta_graus=round(a, 1), alcance_mm=round(alc * 1000, 1), alcance_mao_e_mm=round(alc_e * 1000, 1), segurando=segurando, folga_braco_mm=round(fb * 1000, 1), braco_peca=fbp, folga_tronco_porta_mm=round(ft * 1000, 1))
    res['quadros'].append(q)
    if segurando and alc > pior['alcance']: pior['alcance'], pior['alcance_g'] = alc, g
    if fb < pior['braco']: pior['braco'], pior['braco_peca'], pior['braco_g'] = fb, fbp, g
    if ft < pior['tronco']: pior['tronco'], pior['tronco_g'] = ft, g
res['resumo'] = {k: (round(v * 1000, 1) if isinstance(v, float) and k in ('alcance', 'braco', 'tronco') else v) for k, v in pior.items()}
print(json.dumps(res['resumo'], ensure_ascii=False))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios', 'teste_a1' + ('_r9' if R9 else '') + '.json'), 'w'), ensure_ascii=False, indent=1)
