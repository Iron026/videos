"""Rodada 9: teste numérico da ação do leite no I1 (antes de renderizar), quadro a quadro (30 fps) no intervalo do plano:
 · alcance: distância entre o alvo da mão (IK) e onde a mão realmente chega (braço esticado não alcança → mão longe da caixa);
 · contato: na pega e depois dela, distância mão × caixa constante (a caixa segue a matriz da mão);
 · colisões da CAIXA (8 cantos, orientada) com prateleiras, bordas, paredes internas, outros itens e a PORTA (no referencial
   da porta, que gira); folga mínima por quadro;
 · colisões do BRAÇO direito (segmentos ombro→cotovelo→punho, raio 4,5 cm) e do TRONCO (cilindro r 0,17 m) com a porta e o
   gabinete;
 · etapas: instantes de aproximar, abrir, pegar, retirar (caixa fora do gabinete), sair (fora do quadro da câmera do I1).
Uso: PYTHONPATH=<bpy> python3 testar_leite.py [r9] → ../relatorios/teste_leite[_r9].json"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
R9 = len(sys.argv) > 1 and sys.argv[1] == 'r9'
if R9: os.environ['CENA_R9'] = '1'
import geladeira as G, encenacao02 as E, personagem as PE
G.ITENS_R9 = R9
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
obj = G.montar(parede_traseira=True); pers = PE.montar(); bpy.context.view_layer.update()
piv = obj['porta']; t_puxa = E.T('deixa') - 0.13; ang = E.porta_ang(t_puxa)
leite = [bpy.data.objects[n] for n in ('leite', 'leite_rot')]
base0 = Vector((0.12, -0.08, 0.84 + 0.098)); alvo_leite = E.LEITE_I1
for o in leite: o.location = o.location - base0 + alvo_leite
bpy.context.view_layer.update(); leite_base = {o.name: o.matrix_world.copy() for o in leite}
def aabb(o):
    M = o.matrix_world; vs = [M @ v.co for v in o.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)] + [max(v[i] for v in vs) for i in range(3)]
piv.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
ESTAT = {o.name: aabb(o) for o in bpy.data.objects if o.type == 'MESH' and o.parent is None and not o.name.startswith(('leite', 'pers_', 'tubo', 'feixe', 'arame', 'mec_', 'piso', 'parede', 'armario', 'bancada', 'cozinha', 'janela', 'rodape', 'teto'))
         and (o.name.startswith(('prat_', 'gab_', 'forro', 'gaveta', 'evap', 'bandeja', 'iogurte', 'pote', 'suco', 'garrafa', 'item_', 'tomate')))}
PORTA = {o.name: aabb(o) for o in bpy.data.objects if o.type == 'MESH' and o.parent == piv}   # no referencial da porta (fechada)
def dist_caixa(p, b):   # distância de um ponto a uma AABB (negativa = dentro: profundidade)
    d = [max(b[i] - p[i], 0, p[i] - b[3 + i]) for i in range(3)]
    if any(d): return math.sqrt(sum(x * x for x in d))
    return -min(min(p[i] - b[i], b[3 + i] - p[i]) for i in range(3))
def para_porta(p, a): # ponto do mundo → referencial da porta fechada (rotação inversa em torno do pivô)
    r = -math.radians(a); x, y = p[0] - G.GX, p[1] - G.GY0
    return Vector((G.GX + x * math.cos(r) - y * math.sin(r), G.GY0 + x * math.sin(r) + y * math.cos(r), p[2]))
P0 = E.PL_T('I1') if hasattr(E, 'PL_T') else None
import importlib; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'decupagem')); import planos as PL
t0, t1 = [(p['t0'], p['t1']) for p in PL.resolvidos()['planos'] if p['id'] == 'I1'][0]
res = dict(quadros=[], resumo={}); rel = {}
pior = dict(alcance=0.0, caixa=1.0, caixa_peca=None, braco=1.0, braco_peca=None, tronco=1.0)
for i in range(int(round((t0 - 0.25) * 30)), int(round((t1 + 0.25) * 30)) + 1):
    g = i / 30; a = ang(g); piv.rotation_euler = (0, 0, math.radians(a))
    e = E.est_porta_aberta(g); PE.posar(pers, e); bpy.context.view_layer.update()
    mao = pers['mao_d'].matrix_world if g < E.T_PEGA else (pers['maof_d'].matrix_world if 'maof_d' in pers else pers['mao_d'].matrix_world)
    if g >= E.T_PEGA and not rel: rel = {o.name: mao.inverted() @ leite_base[o.name] for o in leite}
    for o in leite: o.matrix_world = (mao @ rel[o.name]) if rel else leite_base[o.name]
    bpy.context.view_layer.update()
    alvo = Vector(e['braco_d'][1]) if e['braco_d'][0] == 'ik' else None; mao_p = mao.translation
    alc = (alvo - mao_p).length if alvo is not None else 0.0
    # caixa: 8 cantos do 'leite'
    L = bpy.data.objects['leite']; cs = [L.matrix_world @ Vector((sx * 0.035, sy * 0.035, sz * 0.095)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    fc, fcp = 1.0, None
    for n, b in ESTAT.items():
        if g < E.T_PEGA - 0.05 and n.startswith('prat_vidro_0.84'): continue        # apoiada na prateleira antes da pega
        d = min(dist_caixa(c, b) for c in cs)
        if d < fc: fc, fcp = d, n
    for n, b in PORTA.items():
        d = min(dist_caixa(para_porta(c, a), b) for c in cs)
        if d < fc: fc, fcp = d, 'porta:' + n
    # braço direito: pontos ao longo de ombro→cotovelo→punho
    ba, an = pers['braco_d'].matrix_world, pers['antebraco_d'].matrix_world
    pts = [ba @ Vector((0, 0, -PE.BRACO * k / 6)) for k in range(7)] + [an @ Vector((0, 0, -PE.ANTEBRACO * k / 6)) for k in range(7)]
    fb, fbp = 1.0, None
    for p in pts:
        for n, b in ESTAT.items():
            d = dist_caixa(p, b) - 0.045
            if d < fb: fb, fbp = d, n
        for n, b in PORTA.items():
            d = dist_caixa(para_porta(p, a), b) - 0.045
            if d < fb: fb, fbp = d, 'porta:' + n
    tr = pers['tronco'].matrix_world.translation; ft = min(dist_caixa(para_porta(Vector((tr.x, tr.y, z)), a), b) - 0.17 for n, b in PORTA.items() for z in (0.9, 1.2))
    # contato: menor distância entre os vértices da mão VISÍVEL e a caixa (no referencial da caixa)
    mv = pers['maof_d'] if (g >= E.T_PEGA - 0.04 and 'maof_d' in pers) else pers['mao_d']; Li = L.matrix_world.inverted()
    vs = [Li @ (mv.matrix_world @ v.co) for v in mv.data.vertices]
    cont = min(dist_caixa(v, (-0.035, -0.035, -0.095, 0.035, 0.035, 0.095)) for v in vs)
    q = dict(g=round(g, 3), contato_mao_caixa_mm=round(cont * 1000, 1), porta_graus=round(a, 1), alcance_mm=round(alc * 1000, 1), folga_caixa_mm=round(fc * 1000, 1), caixa_peca=fcp,
             folga_braco_mm=round(fb * 1000, 1), braco_peca=fbp, folga_tronco_porta_mm=round(ft * 1000, 1), caixa_centro=[round(x, 3) for x in L.matrix_world.translation])
    res['quadros'].append(q)
    if alc > pior['alcance']: pior['alcance'] = alc
    if fc < pior['caixa']: pior['caixa'], pior['caixa_peca'], pior['caixa_g'] = fc, fcp, g
    if fb < pior['braco']: pior['braco'], pior['braco_peca'], pior['braco_g'] = fb, fbp, g
    if ft < pior['tronco']: pior['tronco'], pior['tronco_g'] = ft, g
fora = next((q['g'] for q in res['quadros'] if q['g'] > E.T_PEGA and q['caixa_centro'][1] < G.GY0 - 0.06), None)
na_pega = [q for q in res['quadros'] if E.T_PEGA - 0.001 <= q['g'] <= E.T_PEGA + 0.45]
res['resumo'] = dict(contato_mao_caixa_mm_depois_da_pega=[min(q['contato_mao_caixa_mm'] for q in na_pega), max(q['contato_mao_caixa_mm'] for q in na_pega)] if na_pega else None, alcance_max_mm=round(pior['alcance'] * 1000, 1), folga_min_caixa_mm=round(pior['caixa'] * 1000, 1), caixa_peca=pior['caixa_peca'], caixa_g=pior.get('caixa_g'),
                     folga_min_braco_mm=round(pior['braco'] * 1000, 1), braco_peca=pior['braco_peca'], braco_g=pior.get('braco_g'), folga_min_tronco_porta_mm=round(pior['tronco'] * 1000, 1),
                     etapas=dict(porta_comeca=round(t_puxa, 2), pega=E.T_PEGA, caixa_fora_do_gabinete=fora, sai=E.T_SAI, fim_do_plano=t1),
                     leite=[round(x, 3) for x in alvo_leite])
print(json.dumps(res['resumo'], ensure_ascii=False))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios', 'teste_leite' + ('_r9' if R9 else '') + '.json'), 'w'), ensure_ascii=False, indent=1)
