"""Rodada 9: decide, com prova, quais planos podem REAPROVEITAR os quadros da V8 depois das mudanças de modelagem.
Para cada plano compara a cena da V8 (cenas/<id>) com a exportação da rodada 9 (cenas/<id>_r9):
 1. cena.json sem a lista de materiais/arquivos: câmera, animação (porta, personagem, mecanismo), curvas, luzes e demais
    parâmetros precisam ser IDÊNTICOS; qualquer diferença → plano afetado;
 2. malhas: por material (chave), o conjunto de triângulos (12 campos por vértice, 4 casas, ordem ignorada); os triângulos
    que entram, saem ou mudam são as "diferenças";
 3. visibilidade: os vértices das diferenças são projetados pela câmera de CADA quadro; se algum cai num quadro ampliado em
    25 % (margem para sombras e reflexos de algo logo fora da tela) e na frente da câmera → plano afetado. Sem oclusão:
    o critério é conservador (pode mandar re-renderizar algo que estava escondido, nunca o contrário).
Malhas animadas (objeto não nulo) são comparadas no espaço local; se a animação do objeto for a mesma, só a geometria conta.
Uso: python3 comparar_cenas_r9.py [planos...] → relatorios/comparacao_cenas_r9.json"""
import os, sys, json, math
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(A, 'cenas')
MARGEM = 0.25
def carregar(d):
    c = json.load(open(os.path.join(d, 'cena.json'))); mats = {}
    for m in c['materiais']:
        if not m.get('arquivo'): continue
        k = (m.get('chave') or m.get('nome'), m.get('objeto'))
        a = np.fromfile(os.path.join(d, m['arquivo']), np.float32).reshape(-1, 3, 12)
        mats.setdefault(k, []).append(a)
    return c, {k: np.concatenate(v) for k, v in mats.items()}
def tris(a): return set(tuple(sorted(map(tuple, t))) for t in np.round(a[:, :, :3], 4))   # posições (a exportação varia o pareamento das normais)
def verts(a):
    v = np.round(a.reshape(-1, 12), 4); u, c = np.unique(v, axis=0, return_counts=True); return {tuple(x): n for x, n in zip(map(tuple, u), c)}
def proj(cam, P):
    pos = np.array(cam['pos']); f = np.array(cam['dir'], float); f /= np.linalg.norm(f); r = np.cross(f, cam['up']); r /= np.linalg.norm(r); u = np.cross(r, f)
    d = P - pos; z = d @ f; t = math.tan(math.radians(cam['fov'] / 2)); asp = 1080 / 1920
    with np.errstate(divide='ignore', invalid='ignore'):
        x = (d @ r / z) / (t * asp); y = (d @ u / z) / t
    return x, y, z
def mat4(m): return np.array(m, float).reshape(4, 4).T     # coluna-maior (Blender → three)
ids = sys.argv[1:] or sorted(p[:-3] for p in os.listdir(C) if p.endswith('_r9') and os.path.isdir(os.path.join(C, p[:-3])) and not p.startswith(('C4_', 'H2_')))
saida = os.path.join(A, '..', 'relatorios', 'comparacao_cenas_r9.json')
res = json.load(open(saida)) if os.path.exists(saida) else {}
for pid in ids:
    a, b = os.path.join(C, pid), os.path.join(C, pid + '_r9')
    if not os.path.isdir(b): continue
    ca, ma = carregar(a); cb, mb = carregar(b)
    sem = lambda c: {k: v for k, v in c.items() if k != 'materiais'}
    difs_json = sorted(k for k in set(sem(ca)) | set(sem(cb)) if sem(ca).get(k) != sem(cb).get(k))
    # materiais: parâmetros (cor, temperatura...) de materiais que existem nos dois
    pa = {(m.get('chave') or m.get('nome'), m.get('objeto')): {k: v for k, v in m.items() if k not in ('arquivo', 'vertices')} for m in ca['materiais']}
    pb = {(m.get('chave') or m.get('nome'), m.get('objeto')): {k: v for k, v in m.items() if k not in ('arquivo', 'vertices')} for m in cb['materiais']}
    mat_dif = sorted(str(k) for k in set(pa) & set(pb) if pa[k] != pb[k])
    novos, sumidos, mudados, pts = [], [], [], []
    for k in set(ma) | set(mb):
        ta = tris(ma[k]) if k in ma else set(); tb = tris(mb[k]) if k in mb else set()
        d = (ta ^ tb)
        if not d and k in ma and k in mb and verts(ma[k]) == verts(mb[k]): continue   # mesma geometria e mesmos atributos
        if not d: d = ta   # atributos diferentes na mesma geometria: a malha inteira conta
        (novos if k not in ma else sumidos if k not in mb else mudados).append(f'{k[0]}' + (f' @{k[1]}' if k[1] else ''))
        P = np.array([v[:3] for t in d for v in t], float)
        pts.append((k[1], P))
    visiveis = 0; quadros = cb['animacao']['quadros']
    if pts and 'animacao' not in difs_json:
        for q in quadros:
            cam = q['camera']; vis_q = False
            for obj, P in pts:
                if obj:   # malha animada: espaço local → mundo pela matriz do objeto no quadro
                    M = mat4(q['objetos'][obj]) if obj in q['objetos'] else np.eye(4)
                    W = (np.c_[P, np.ones(len(P))] @ M.T)[:, :3]
                else: W = P
                x, y, z = proj(cam, W); lim = 1 + 2 * MARGEM
                vis_q = vis_q or bool(np.sum((z > 0.01) & (np.abs(x) <= lim) & (np.abs(y) <= lim)) > 0)
            visiveis += vis_q
    afetado = bool(difs_json) or bool(mat_dif) or visiveis > 0
    res[pid] = dict(afetado=afetado, cena_json_difere=difs_json, materiais_com_parametro_diferente=mat_dif, malhas_novas=sorted(novos), malhas_removidas=sorted(sumidos),
                    malhas_mudadas=sorted(mudados), quadros_com_diferenca_no_quadro_ampliado=visiveis, quadros=len(quadros),
                    motivo=('cena.json: ' + ', '.join(difs_json)) if difs_json else ('parâmetros de material' if mat_dif else (f'{visiveis} quadros com geometria alterada no quadro' if visiveis else 'nenhuma diferença visível (reaproveitar com prova)')))
    print(pid, 'AFETADO' if afetado else 'reaproveita', '·', res[pid]['motivo'], flush=True)
    json.dump(res, open(saida, 'w'), ensure_ascii=False, indent=1)
