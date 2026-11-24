"""Rodada 10: prova, QUADRO A QUADRO, de que uma reexportação localizada só muda os quadros que deveria mudar.
Compara a cena atual (cenas/<plano>) com a nova (cenas/<plano><sufixo>):
 · cena.json sem 'animacao', 'curvas' e 'materiais' (câmera fixa, luzes, corte, ambiente...) → precisa ser IDÊNTICO;
 · materiais (parâmetros) e malhas (triângulos sem ordem + multiconjunto de vértices) → precisam ser IDÊNTICOS;
 · por quadro: câmera, matrizes dos objetos e o VALOR de cada curva no instante do quadro (mesma interpolação do motor);
 · rótulos 2D e manômetros 2D por quadro (dados da montagem).
Saída: quadros iguais (reaproveitáveis) × diferentes (a renderizar) em <plano>/_prova_reuso_quadros.json da pasta de
quadros indicada, com os hashes das duas cenas. Uso: python3 provar_quadros_iguais.py <plano> <sufixo> [pasta_quadros...]"""
import os, sys, json, hashlib
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(A, 'cenas')
pid, suf = sys.argv[1], sys.argv[2]; pastas = sys.argv[3:] or ['quadros_revisao']
a, b = os.path.join(C, pid), os.path.join(C, pid + suf)
ca, cb = json.load(open(os.path.join(a, 'cena.json'))), json.load(open(os.path.join(b, 'cena.json')))
def hcena(d):
    h = hashlib.sha256()
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
sem = lambda c: {k: v for k, v in c.items() if k not in ('animacao', 'curvas', 'materiais')}
difs_fixas = sorted(k for k in set(sem(ca)) | set(sem(cb)) if sem(ca).get(k) != sem(cb).get(k))
def malhas(d, c):
    out = {}
    for m in c['materiais']:
        if not m.get('arquivo'): continue
        k = (m.get('chave') or m.get('nome'), m.get('objeto')); x = np.fromfile(os.path.join(d, m['arquivo']), np.float32).reshape(-1, 3, 12)
        out.setdefault(k, []).append(x)
    return {k: np.concatenate(v) for k, v in out.items()}
ma, mb = malhas(a, ca), malhas(b, cb)
tris = lambda x: set(tuple(sorted(map(tuple, t))) for t in np.round(x[:, :, :3], 4))
def verts(x):
    v = np.round(x.reshape(-1, 12), 4); u, n = np.unique(v, axis=0, return_counts=True); return {tuple(r): c for r, c in zip(map(tuple, u), n)}
malhas_dif = sorted(str(k) for k in set(ma) | set(mb) if k not in ma or k not in mb or tris(ma[k]) != tris(mb[k]) or verts(ma[k]) != verts(mb[k]))
par = lambda c: {(m.get('chave') or m.get('nome'), m.get('objeto')): {k: v for k, v in m.items() if k not in ('arquivo', 'vertices')} for m in c['materiais']}
mat_dif = sorted(str(k) for k in set(par(ca)) | set(par(cb)) if par(ca).get(k) != par(cb).get(k))
def curva(cv, nome, g):
    k = cv[nome]
    if g <= k[0][0]: return k[0][1]
    for (t0, v0), (t1, v1) in zip(k, k[1:]):
        if g <= t1: u = (g - t0) / max(t1 - t0, 1e-6); return v0 + (v1 - v0) * u * u * (3 - 2 * u)
    return k[-1][1]
qa, qb = ca['animacao']['quadros'], cb['animacao']['quadros']; n = len(qa)
ra = json.load(open(os.path.join(a, 'rotulos2d.json')))['quadros'] if os.path.exists(os.path.join(a, 'rotulos2d.json')) else []
rb = json.load(open(os.path.join(b, 'rotulos2d.json')))['quadros'] if os.path.exists(os.path.join(b, 'rotulos2d.json')) else []
def man(d):
    f = os.path.join(d, 'manometros2d.json'); return json.load(open(f)) if os.path.exists(f) else None
iguais, difs = [], {}
for k in range(n):
    g = ca['g0'] + k / 30; motivo = []
    if qa[k] != qb[k]: motivo.append('câmera/objetos')
    for nome in set(ca.get('curvas', {})) | set(cb.get('curvas', {})):
        va = curva(ca['curvas'], nome, g) if nome in ca.get('curvas', {}) else None; vb = curva(cb['curvas'], nome, g) if nome in cb.get('curvas', {}) else None
        if va is None or vb is None or abs(va - vb) > 1e-9: motivo.append(f'curva {nome}: {va} → {vb}')
    if (ra[k] if k < len(ra) else None) != (rb[k] if k < len(rb) else None): motivo.append('rótulos 2D')
    (difs.__setitem__(k, motivo) if motivo else iguais.append(k))
res = dict(plano=pid, cena_atual=hcena(a), cena_nova=hcena(b), fixos_diferentes=difs_fixas, malhas_diferentes=malhas_dif, materiais_diferentes=mat_dif,
           manometros_iguais=man(a) == man(b), quadros=n, iguais=len(iguais), diferentes={str(k): v for k, v in difs.items()},
           valida=not (difs_fixas or malhas_dif or mat_dif) and man(a) == man(b))
print(json.dumps({k: v for k, v in res.items()}, ensure_ascii=False))
if res['valida']:
    res['quadros_iguais'] = iguais
    for p in pastas:
        d = os.path.join(A, p, pid); os.makedirs(d, exist_ok=True)
        json.dump(res, open(os.path.join(d, '_prova_reuso_quadros.json'), 'w'), ensure_ascii=False, indent=1)
