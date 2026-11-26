"""Rodada 12: varre TODOS os planos atrás de inversões da ordem de desenho entre malhas transparentes (alfa < 1) que se
sobrepõem na tela. O three.js (r170) ordena os transparentes pela profundidade (NDC z) do CENTRO DA ESFERA ENVOLVENTE de
cada malha (centro da caixa da geometria × matrixWorld), do mais longe para o mais perto; empate → ordem de criação.
Quando essa ordem troca dentro de um plano, a mistura muda de uma vez (ex.: H2 1:53, garrafa × prateleira de vidro).
Uso: python3 varrer_ordem_transparentes.py [PLANO ...] → relatorios/testes_r10/ordem_transparentes.json"""
import os, sys, json
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(A, 'cenas')
W, H = 1080, 1920


def vista(cam, perto, longe):
    p, d, u = (np.array(cam[k], float) for k in ('pos', 'dir', 'up'))
    z = -d / np.linalg.norm(d); x = np.cross(u, z); x /= np.linalg.norm(x); y = np.cross(z, x)
    V = np.eye(4); V[:3, :3] = np.stack([x, y, z]); V[:3, 3] = -V[:3, :3] @ p
    f = 1 / np.tan(np.radians(cam['fov']) / 2); a = W / H
    P = np.zeros((4, 4)); P[0, 0] = f / a; P[1, 1] = f; P[2, 2] = (longe + perto) / (perto - longe); P[2, 3] = 2 * longe * perto / (perto - longe); P[3, 2] = -1
    return P @ V


def proj(M, pts):
    h = np.c_[pts, np.ones(len(pts))] @ M.T; w = h[:, 3:4]
    return h[:, :3] / w, w[:, 0]


if __name__ == '__main__':
    ids = sys.argv[1:] or sorted(d for d in os.listdir(C) if os.path.isfile(os.path.join(C, d, 'cena.json')) and not d.startswith('_'))
    res = {}
    for pid in ids:
        c = json.load(open(os.path.join(C, pid, 'cena.json'))); perto, longe = c.get('perto', 0.5), c.get('longe', 8000)
        tr = []
        for k, m in enumerate(c['materiais']):
            if m.get('tipo') == 'agua' or (m.get('alfa') if m.get('alfa') is not None else 1) >= 1: continue
            b = np.fromfile(os.path.join(C, pid, m['arquivo']), np.float32).reshape(-1, 12)[:, :3]
            lo, hi = b.min(0), b.max(0); cantos = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
            tr.append(dict(k=k, nome=m['nome'], obj=m.get('objeto'), centro=(lo + hi) / 2, cantos=cantos))
        Q = c['animacao']['quadros']; ordem_prev = {}; trocas = []
        for i, q in enumerate(Q):
            M = vista(q['camera'], perto, longe); info = []
            for t in tr:
                T = np.eye(4)
                if t['obj'] and t['obj'] in q['objetos']: T = np.array(q['objetos'][t['obj']], float).reshape(4, 4).T
                cen = (T @ np.r_[t['centro'], 1])[:3]; zc = proj(M, cen[None])[0][0, 2]
                cn, w = proj(M, (np.c_[t['cantos'], np.ones(8)] @ T.T)[:, :3])
                vis = (w > 0).all()
                caixa = (cn[:, 0].min(), cn[:, 0].max(), cn[:, 1].min(), cn[:, 1].max()) if vis else None
                info.append((t, zc, caixa))
            for a in range(len(info)):
                for b in range(a + 1, len(info)):
                    (ta, za, ca), (tb, zb, cb) = info[a], info[b]
                    if ca is None or cb is None: continue
                    sob = ca[0] < cb[1] and cb[0] < ca[1] and ca[2] < cb[3] and cb[2] < ca[3] and max(ca[0], cb[0]) < 1 and min(ca[1], cb[1]) > -1 and max(ca[2], cb[2]) < 1 and min(ca[3], cb[3]) > -1
                    chave = (ta['k'], tb['k']); s = za > zb   # True: a mais longe → a desenhado antes
                    if chave in ordem_prev and ordem_prev[chave][0] != s and (sob or ordem_prev[chave][1]):
                        trocas.append(dict(quadro=i, t=round(c['g0'] + i / 30, 3), a=f"{ta['nome']}#{ta['k']}", b=f"{tb['nome']}#{tb['k']}", sobrepostos=bool(sob),
                                           antes=f"{'a' if ordem_prev[chave][0] else 'b'} primeiro", depois=f"{'a' if s else 'b'} primeiro"))
                    ordem_prev[chave] = (s, sob)
        res[pid] = dict(transparentes=[f"{t['nome']}#{t['k']}" for t in tr], trocas=trocas)
        print(pid, len(tr), 'transparentes;', len(trocas), 'trocas', [(x['quadro'], x['a'], x['b']) for x in trocas][:6], flush=True)
    json.dump(res, open(os.path.join(A, '..', 'relatorios', 'testes_r10', 'ordem_transparentes.json' if len(sys.argv) == 1 else 'ordem_transparentes_parcial.json'), 'w'), ensure_ascii=False, indent=1)
