"""Exporta a cena de um quadro (geometria avaliada, materiais simplificados, câmera, sol e céu) para o
renderizador em tempo real (Three.js). Garante a MESMA câmera/modelo/composição nos dois motores.
Uso: python3 exportar_tempo_real.py <quadro> <pasta_saida>
Saída: cena.json + um .bin por material (float32: posição xyz, normal xyz; opcional cor rgb por vértice).
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import numpy as np
from mathutils import Vector
import lib, quadros


def lin(c): return [float(c[0]), float(c[1]), float(c[2])]


def descrever_material(m, obj):
    """Cor base / rugosidade / metalicidade / emissão representativas do material procedural."""
    d = dict(cor=[0.8, 0.8, 0.8], rug=0.5, metal=0.0, emis=[0, 0, 0], emis_forca=0.0, transm=0.0)
    if m is None or not m.node_tree: return d
    nt = m.node_tree; p = nt.nodes.get('Principled BSDF')
    if m.name.startswith('conteiner'):
        d['cor'] = lin(obj.color); d['rug'] = 0.55; return d
    if p is None:
        em = next((n for n in nt.nodes if n.type == 'EMISSION'), None)
        if em: d['emis'] = lin(em.inputs['Color'].default_value); d['emis_forca'] = 1.0
        return d
    bc = p.inputs['Base Color']
    if bc.is_linked:
        src = bc.links[0].from_node
        if src.type == 'MIX':           # pintura: cor × variação de ruído
            d['cor'] = lin(src.inputs[6].default_value) if not src.inputs[6].is_linked else d['cor']
        elif src.type == 'VALTORGB':    # concreto / areia: média da rampa
            els = src.color_ramp.elements
            d['cor'] = [float(np.mean([e.color[i] for e in els])) for i in range(3)]
    else:
        d['cor'] = lin(bc.default_value)
    r = p.inputs['Roughness']
    if r.is_linked:
        src = r.links[0].from_node
        if src.type == 'MAP_RANGE': d['rug'] = float((src.inputs['To Min'].default_value + src.inputs['To Max'].default_value) / 2)
    else: d['rug'] = float(r.default_value)
    d['metal'] = float(p.inputs['Metallic'].default_value)
    d['transm'] = float(p.inputs['Transmission Weight'].default_value)
    es = p.inputs['Emission Strength']
    if not es.is_linked and es.default_value > 0:
        d['emis'] = lin(p.inputs['Emission Color'].default_value); d['emis_forca'] = float(es.default_value)
    return d


def exportar(quadro, pasta):
    os.makedirs(pasta, exist_ok=True)
    quadros.QUADROS[quadro]()
    s = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
    grupos = {}   # chave do material -> listas
    mats = {}
    for o in s.objects:
        if o.type not in ('MESH', 'CURVE') or o.hide_render: continue
        if any(c.hide_render for c in o.users_collection if c != s.collection): continue
        oe = o.evaluated_get(dg)
        try: me = oe.to_mesh()
        except RuntimeError: continue
        if me is None or len(me.polygons) == 0: oe.to_mesh_clear(); continue
        me.calc_loop_triangles()
        mw = o.matrix_world; nm = mw.to_3x3().inverted().transposed()
        cn = me.corner_normals
        nt = len(me.loop_triangles)
        tri_loops = np.empty(nt * 3, dtype=np.int64); me.loop_triangles.foreach_get('loops', tri_loops)
        tri_mat = np.empty(nt, dtype=np.int64); me.loop_triangles.foreach_get('material_index', tri_mat)
        loop_v = np.empty(len(me.loops), dtype=np.int64); me.loops.foreach_get('vertex_index', loop_v)
        co = np.empty(len(me.vertices) * 3, dtype=np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        nrm = np.empty(len(me.loops) * 3, dtype=np.float32); cn.foreach_get('vector', nrm); nrm = nrm.reshape(-1, 3)
        M = np.array(mw); N = np.array(nm)
        P = co @ M[:3, :3].T + M[:3, 3]
        Nw = nrm @ N.T; Nw /= np.maximum(np.linalg.norm(Nw, axis=1, keepdims=True), 1e-8)
        for mi in np.unique(tri_mat):
            mat = o.material_slots[mi].material if mi < len(o.material_slots) else None
            desc = descrever_material(mat, o)
            chave = (mat.name if mat else 'sem') + ('_' + '_'.join(f'{c:.3f}' for c in desc['cor']) if mat and mat.name.startswith('conteiner') else '')
            mats[chave] = desc
            sel = np.repeat(tri_mat == mi, 3)
            loops = tri_loops[sel]
            g = grupos.setdefault(chave, [[], []])
            g[0].append(P[loop_v[loops]]); g[1].append(Nw[loops])
        oe.to_mesh_clear()
    lista = []
    for i, (k, (ps, ns)) in enumerate(grupos.items()):
        P = np.concatenate(ps).astype(np.float32); Nn = np.concatenate(ns).astype(np.float32)
        arq = f'm{i:03d}.bin'; np.concatenate([P, Nn], axis=1).astype(np.float32).tofile(os.path.join(pasta, arq))
        lista.append(dict(arquivo=arq, vertices=int(len(P)), nome=k, **mats[k]))
    cam = s.camera; cd = cam.data
    sh = cd.sensor_height if cd.sensor_fit == 'VERTICAL' else cd.sensor_width * s.render.resolution_y / s.render.resolution_x
    fov_v = math.degrees(2 * math.atan(sh / 2 / cd.lens))
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1)); up = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    sol = next(o for o in s.objects if o.type == 'LIGHT' and o.data.type == 'SUN')
    dir_sol = sol.matrix_world.to_3x3() @ Vector((0, 0, -1))
    luzes = [dict(tipo=o.data.type, pos=list(o.matrix_world.translation), cor=list(o.data.color), energia=o.data.energy)
             for o in s.objects if o.type == 'LIGHT' and o.data.type != 'SUN']
    w = s.world.node_tree; rmp = next(n for n in w.nodes if n.type == 'VALTORGB')
    ceu = [dict(pos=e.position, cor=list(e.color)[:3]) for e in rmp.color_ramp.elements]
    meta = dict(quadro=quadro, materiais=lista, camera=dict(pos=list(cam.matrix_world.translation), dir=list(fwd), up=list(up), fov=fov_v,
                largura=s.render.resolution_x, altura=s.render.resolution_y, foco=cd.dof.focus_distance, fstop=cd.dof.aperture_fstop),
                sol=dict(dir=list(dir_sol), cor=list(sol.data.color), energia=sol.data.energy, angulo=sol.data.angle),
                luzes=luzes, ceu=ceu, ceu_forca=next(n for n in w.nodes if n.type == 'BACKGROUND').inputs[1].default_value)
    json.dump(meta, open(os.path.join(pasta, 'cena.json'), 'w'), indent=1)
    tot = sum(m['vertices'] for m in lista) // 3
    print(f'EXPORTADO {len(lista)} materiais, {tot} triângulos -> {pasta}')


if __name__ == '__main__':
    exportar(int(sys.argv[1]), sys.argv[2])
