"""Exportador v2 para o motor em tempo real (Three.js): mesma geometria, câmera, sol e céu do Blender,
agora com os METADADOS de cada material (m['rt']) para o shader reproduzir ruído, relevo, faixas, água etc.
Uso: python3 exportar_rt2.py <quadro> <pasta_saida>
Cada grupo (material) vira um .bin float32 com 12 valores por vértice:
  posição xyz (mundo) · normal xyz (mundo) · coordenada local do objeto xyz · coordenada gerada 0–1 xyz (caixa do objeto)
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector
import lib, quadros


def lin_hex(v):
    """Cor do metadado ('#rrggbb', tupla 0-255 ou RGBA linear) → RGB linear."""
    if isinstance(v, str) or (isinstance(v, (list, tuple)) and len(v) == 3 and max(v) > 1.0):
        return list(lib.srgb(tuple(v) if not isinstance(v, str) else v)[:3])
    return [float(x) for x in v[:3]]


def meta_material(m, obj):
    rt = json.loads(m['rt']) if (m is not None and 'rt' in m.keys()) else {'tipo': 'generico'}
    t = rt['tipo']
    for k in ('cor', 'acima', 'abaixo', 'linha', 'cor_esp'):
        if k in rt and rt[k] is not None and not (k == 'cor' and t in ('aco', 'concreto', 'areia') and isinstance(rt[k], list) and max(rt[k]) <= 1):
            rt[k] = lin_hex(rt[k])
    if t in ('aco', 'concreto', 'areia') and isinstance(rt.get('cor'), list) and max(rt['cor']) > 1: rt['cor'] = lin_hex(rt['cor'])
    if t == 'faixas_z': rt['faixas'] = [[float(z), lin_hex(c)] for z, c in rt['faixas']]
    if t == 'corte_ld' and isinstance(rt.get('casca'), dict): rt['casca']['cor'] = lin_hex(rt['casca']['cor'])
    if t == 'conteiner': rt['cor'] = [float(c) for c in obj.color[:3]]
    if t == 'generico' and m is not None and m.node_tree:
        p = m.node_tree.nodes.get('Principled BSDF')
        if p and not p.inputs['Base Color'].is_linked: rt['cor'] = [float(c) for c in p.inputs['Base Color'].default_value[:3]]
        if p: rt['rug'] = float(p.inputs['Roughness'].default_value); rt['metal'] = float(p.inputs['Metallic'].default_value)
    return rt


def exportar(quadro, pasta):
    os.makedirs(pasta, exist_ok=True)
    quadros.QUADROS[quadro]()
    s = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
    grupos, metas = {}, {}
    for o in s.objects:
        if o.type not in ('MESH', 'CURVE', 'FONT') or o.hide_render: continue
        if any(c.hide_render for c in o.users_collection if c != s.collection): continue
        oe = o.evaluated_get(dg)
        try: me = oe.to_mesh()
        except RuntimeError: continue
        if me is None or len(me.polygons) == 0: oe.to_mesh_clear(); continue
        me.calc_loop_triangles()
        nt = len(me.loop_triangles)
        tri_loops = np.empty(nt * 3, dtype=np.int64); me.loop_triangles.foreach_get('loops', tri_loops)
        tri_mat = np.empty(nt, dtype=np.int64); me.loop_triangles.foreach_get('material_index', tri_mat)
        loop_v = np.empty(len(me.loops), dtype=np.int64); me.loops.foreach_get('vertex_index', loop_v)
        co = np.empty(len(me.vertices) * 3, dtype=np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        nrm = np.empty(len(me.loops) * 3, dtype=np.float32); me.corner_normals.foreach_get('vector', nrm); nrm = nrm.reshape(-1, 3)
        M = np.array(o.matrix_world); N = np.array(o.matrix_world.to_3x3().inverted().transposed())
        P = co @ M[:3, :3].T + M[:3, 3]
        Nw = nrm @ N.T; Nw /= np.maximum(np.linalg.norm(Nw, axis=1, keepdims=True), 1e-8)
        lo, hi = co.min(0), co.max(0); G = (co - lo) / np.maximum(hi - lo, 1e-6)
        for mi in np.unique(tri_mat):
            mat = o.material_slots[mi].material if mi < len(o.material_slots) else None
            rt = meta_material(mat, o)
            chave = (mat.name if mat else 'sem') + (('_' + '_'.join(f'{c:.3f}' for c in rt['cor'])) if rt['tipo'] == 'conteiner' else '')
            metas[chave] = rt
            loops = tri_loops[np.repeat(tri_mat == mi, 3)]; vid = loop_v[loops]
            g = grupos.setdefault(chave, [])
            g.append(np.concatenate([P[vid], Nw[loops], co[vid], G[vid]], axis=1).astype(np.float32))
        oe.to_mesh_clear()
    lista = []
    for i, (k, partes) in enumerate(grupos.items()):
        arr = np.concatenate(partes); arq = f'm{i:03d}.bin'; arr.tofile(os.path.join(pasta, arq))
        lista.append(dict(metas[k], arquivo=arq, vertices=int(len(arr)), chave=k))
    cam = s.camera; cd = cam.data
    sh = cd.sensor_height if cd.sensor_fit == 'VERTICAL' else cd.sensor_width * s.render.resolution_y / s.render.resolution_x
    fov_v = math.degrees(2 * math.atan(sh / 2 / cd.lens))
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1)); up = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    sol = next(o for o in s.objects if o.type == 'LIGHT' and o.data.type == 'SUN')
    luzes = [dict(tipo=o.data.type, pos=list(o.matrix_world.translation), alvo=list(o.matrix_world.translation + o.matrix_world.to_3x3() @ Vector((0, 0, -1))),
                  cor=list(o.data.color), energia=o.data.energy, tam=getattr(o.data, 'size', 0.0))
             for o in s.objects if o.type == 'LIGHT' and o.data.type != 'SUN']
    ceu = json.loads(s.world['rt']) if 'rt' in s.world.keys() else {}
    for k in ('zenite', 'meio', 'horizonte', 'abaixo'):
        if k in ceu: ceu[k] = lin_hex(ceu[k])
    meta = dict(quadro=quadro, materiais=lista,
                camera=dict(pos=list(cam.matrix_world.translation), dir=list(fwd), up=list(up), fov=fov_v,
                            largura=s.render.resolution_x, altura=s.render.resolution_y),
                sol=dict(dir=list(sol.matrix_world.to_3x3() @ Vector((0, 0, -1))), cor=list(sol.data.color), energia=sol.data.energy,
                         angulo=sol.data.angle), luzes=luzes, ceu=ceu, rotulos=list(lib.ROTULOS))
    json.dump(meta, open(os.path.join(pasta, 'cena.json'), 'w'), indent=1)
    tot = sum(m['vertices'] for m in lista) // 3
    tipos = sorted({m['tipo'] for m in lista})
    print(f'EXPORTADO {len(lista)} materiais, {tot} triângulos, tipos {tipos} -> {pasta}')


if __name__ == '__main__':
    exportar(int(sys.argv[1]), sys.argv[2])


# ---------------------------------------------------------------- animação
def _animado(o):
    while o is not None:
        if o.get('anim'): return True
        o = o.parent
    return False


def _mat_coluna(M):
    """Matriz do Blender (linhas) → array de 16 floats na ordem por colunas do Three.js."""
    return [float(M[r][c]) for c in range(4) for r in range(4)]


def exportar_atual(pasta, n=0, anim=None, fps=30, extra_meta=None):
    """Exporta a cena JÁ MONTADA. Objetos com a propriedade 'anim' (ou filhos deles) vão em coordenadas locais,
    um grupo por objeto, e recebem uma matriz de mundo por quadro; anim(f) posiciona a cena no quadro f."""
    os.makedirs(pasta, exist_ok=True)
    s = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
    grupos, metas, anim_objs = {}, {}, {}
    for o in s.objects:
        if o.type not in ('MESH', 'CURVE', 'FONT') or o.hide_render: continue
        if any(c.hide_render for c in o.users_collection if c != s.collection): continue
        mov = _animado(o)
        oe = o.evaluated_get(dg)
        try: me = oe.to_mesh()
        except RuntimeError: continue
        if me is None or len(me.polygons) == 0: oe.to_mesh_clear(); continue
        me.calc_loop_triangles(); nt = len(me.loop_triangles)
        tri_loops = np.empty(nt * 3, dtype=np.int64); me.loop_triangles.foreach_get('loops', tri_loops)
        tri_mat = np.empty(nt, dtype=np.int64); me.loop_triangles.foreach_get('material_index', tri_mat)
        loop_v = np.empty(len(me.loops), dtype=np.int64); me.loops.foreach_get('vertex_index', loop_v)
        co = np.empty(len(me.vertices) * 3, dtype=np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        nrm = np.empty(len(me.loops) * 3, dtype=np.float32); me.corner_normals.foreach_get('vector', nrm); nrm = nrm.reshape(-1, 3)
        if mov:
            P, Nw = co, nrm
        else:
            M = np.array(o.matrix_world); N = np.array(o.matrix_world.to_3x3().inverted().transposed())
            P = co @ M[:3, :3].T + M[:3, 3]; Nw = nrm @ N.T
        Nw = Nw / np.maximum(np.linalg.norm(Nw, axis=1, keepdims=True), 1e-8)
        lo, hi = co.min(0), co.max(0); G = (co - lo) / np.maximum(hi - lo, 1e-6)
        for mi in np.unique(tri_mat):
            mat = o.material_slots[mi].material if mi < len(o.material_slots) else None
            rt = meta_material(mat, o)
            chave = (mat.name if mat else 'sem') + (('_' + '_'.join(f'{c:.3f}' for c in rt['cor'])) if rt['tipo'] == 'conteiner' else '')
            if mov: chave = 'ANIM|' + o.name + '|' + chave; anim_objs[o.name] = o
            metas[chave] = dict(rt, objeto=o.name if mov else None)
            loops = tri_loops[np.repeat(tri_mat == mi, 3)]; vid = loop_v[loops]
            grupos.setdefault(chave, []).append(np.concatenate([P[vid], Nw[loops], co[vid], G[vid]], axis=1).astype(np.float32))
        oe.to_mesh_clear()
    lista = []
    for i, (k, partes) in enumerate(grupos.items()):
        arr = np.concatenate(partes); arq = f'm{i:03d}.bin'; arr.tofile(os.path.join(pasta, arq))
        lista.append(dict(metas[k], arquivo=arq, vertices=int(len(arr)), chave=k))
    def cam_estado():
        cam = s.camera; cd = cam.data
        sh = cd.sensor_height if cd.sensor_fit == 'VERTICAL' else cd.sensor_width * s.render.resolution_y / s.render.resolution_x
        return dict(pos=list(cam.matrix_world.translation), dir=list(cam.matrix_world.to_3x3() @ Vector((0, 0, -1))),
                    up=list(cam.matrix_world.to_3x3() @ Vector((0, 1, 0))), fov=math.degrees(2 * math.atan(sh / 2 / cd.lens)))
    quadros_anim = []
    for f in range(n):
        tc = anim(f) if anim else None   # anim pode devolver o tempo de CENA do quadro (câmera lenta / remapeamento)
        bpy.context.view_layer.update()
        q = dict(camera=cam_estado(), objetos={nm: _mat_coluna(ob.matrix_world) for nm, ob in anim_objs.items()})
        if tc is not None: q['t'] = float(tc)
        quadros_anim.append(q)
    if n: (anim(0) if anim else None); bpy.context.view_layer.update()
    cam = s.camera
    sol = next(o for o in s.objects if o.type == 'LIGHT' and o.data.type == 'SUN')
    luzes = [dict(tipo=o.data.type, pos=list(o.matrix_world.translation), alvo=list(o.matrix_world.translation + o.matrix_world.to_3x3() @ Vector((0, 0, -1))),
                  cor=list(o.data.color), energia=o.data.energy, tam=getattr(o.data, 'size', 0.0))
             for o in s.objects if o.type == 'LIGHT' and o.data.type != 'SUN']
    ceu = json.loads(s.world['rt']) if 'rt' in s.world.keys() else {}
    for k in ('zenite', 'meio', 'horizonte', 'abaixo'):
        if k in ceu: ceu[k] = lin_hex(ceu[k])
    c0 = cam_estado()
    meta = dict(materiais=lista, camera=dict(c0, largura=s.render.resolution_x, altura=s.render.resolution_y),
                sol=dict(dir=list(sol.matrix_world.to_3x3() @ Vector((0, 0, -1))), cor=list(sol.data.color), energia=sol.data.energy, angulo=sol.data.angle),
                luzes=luzes, ceu=ceu, rotulos=list(lib.ROTULOS), animacao=dict(fps=fps, quadros=quadros_anim) if n else None)
    if extra_meta: meta.update(extra_meta)
    json.dump(meta, open(os.path.join(pasta, 'cena.json'), 'w'))
    print(f'EXPORTADO {len(lista)} grupos ({len(anim_objs)} objetos animados), {sum(m["vertices"] for m in lista)//3} triângulos, {n} quadros -> {pasta}')
