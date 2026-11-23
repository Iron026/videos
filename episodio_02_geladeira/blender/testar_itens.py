"""Rodada 9: teste geométrico dos ALIMENTOS da geladeira (antes de qualquer render), com a porta FECHADA (planos em corte)
e ABERTA a 100° (sequência I):
 · invasão: caixa (AABB do mundo) de cada item × caixas das peças da geladeira e dos outros itens (volume > 1 cm³·10⁻³);
 · apoio: o fundo do item × o topo do apoio logo abaixo — coplanar (|Δ| < 0,05 mm, z-fighting visto pelo vidro) ou flutuando
   (> 2 mm); a folga certa é ~0,5 mm;
 · itens da porta: o alto do item × o fundo da prateleira/borda interna acima (porta fechada).
AABB é conservador para cilindros (acusa a mais, nunca a menos). Uso:
PYTHONPATH=<bpy> python3 testar_itens.py [r9] → ../relatorios/teste_itens[_r9].json"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import geladeira as G
R9 = len(sys.argv) > 1 and sys.argv[1] == 'r9'
if R9: G.ITENS_R9 = True
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
obj = G.montar(parede_traseira=True); bpy.context.view_layer.update()
ITENS = ('leite', 'pote', 'garrafa', 'tomate', 'iogurte', 'suco', 'pote_baixo', 'forma_gelo', 'congelados', 'molho', 'item_')
APOIOS = ('prat_vidro', 'gaveta', 'evap_base', 'porta_prat', 'forro_b')
eh_item = lambda n: n.startswith(ITENS)
def aabb(o):
    M = o.matrix_world; vs = [M @ v.co for v in o.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)] + [max(v[i] for v in vs) for i in range(3)]
def vol(a, b):
    d = [min(a[3 + i], b[3 + i]) - max(a[i], b[i]) for i in range(3)]
    return d[0] * d[1] * d[2] if all(x > 0 for x in d) else 0.0
def medir(rotulo):
    bpy.context.view_layer.update()
    ms = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render and not o.name.startswith(('tubo', 'feixe', 'arame', 'pers_', 'mec_', 'cozinha', 'parede', 'piso', 'armario', 'bancada'))]
    caixas = {o.name: aabb(o) for o in ms}; out = dict(invasoes=[], apoio=[])
    for n, a in caixas.items():
        if not eh_item(n): continue
        for m, b in caixas.items():
            if m == n or (eh_item(m) and m < n): continue
            if (m.startswith(n) or n.startswith(m)) and ('_rot' in m + n or '_tampa' in m + n or '_vol' in m + n): continue   # partes do mesmo item
            if m.startswith('gaveta') and n.startswith('tomate'): continue      # tomates DENTRO da gaveta (caixa de vidro): a AABB da gaveta os contém
            v = vol(a, b)
            if v > 1e-6: out['invasoes'].append(dict(item=n, peca=m, cm3=round(v * 1e6, 2)))
        # apoio: maior topo de apoio abaixo do fundo do item, sobrepondo em x/y
        tops = [b[5] for m, b in caixas.items() if m.startswith(APOIOS) and b[5] <= a[2] + 1e-4 and min(a[3], b[3]) > max(a[0], b[0]) and min(a[4], b[4]) > max(a[1], b[1])]
        if tops and not ('_tampa' in n or '_rot' in n or '_vol' in n):
            gap = a[2] - max(tops)
            if abs(gap) < 5e-5 or gap > 0.002: out['apoio'].append(dict(item=n, folga_mm=round(gap * 1000, 2), tipo='coplanar' if abs(gap) < 5e-5 else 'flutuando'))
    print(rotulo, 'invasões', len(out['invasoes']), 'apoio', len(out['apoio']))
    for x in out['invasoes'][:30]: print('  ', x)
    for x in out['apoio'][:30]: print('  ', x)
    return out
piv = obj['porta']; res = {}
piv.rotation_euler = (0, 0, 0); res['porta_fechada'] = medir('porta fechada')
piv.rotation_euler = (0, 0, math.radians(100)); res['porta_aberta_100'] = medir('porta aberta 100°')
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'relatorios', 'teste_itens' + ('_r9' if R9 else '') + '.json'), 'w'), ensure_ascii=False, indent=1)
