"""Rodada 12: prova de reuso dos quadros ANTERIORES à troca de ordem dos transparentes, para os planos que passam a usar
ordemtransp=1 (motor congela a ordem do quadro 0). Num quadro i, a correção não muda nada se a ordem de TODOS os pares de
malhas com alfa < 1 for a mesma do quadro 0 (mesma regra do three: profundidade NDC do centro da esfera envolvente).
Grava quadros_<perfil>/<plano>/_prova_reuso_config.json (lido por render_definitivo.py).
Uso: python3 provar_ordem_reuso.py <perfil> PLANO [PLANO ...]"""
import os, sys, json, hashlib, time
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(A, '..'); sys.path.insert(0, A)
from varrer_ordem_transparentes import vista, proj
PERFIL, ids = sys.argv[1], sys.argv[2:]
CFG = json.load(open(os.path.join(RAIZ, 'config', 'producao.json'))); P = CFG['perfis'][PERFIL]; OBT = CFG.get('obturador', {})
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
MOT = sha(os.path.join(RAIZ, 'motor', 'render3.js'))[:16] + sha(os.path.join(RAIZ, 'motor', 'render_anim.mjs'))[:8]
def hcena(pid):
    h = hashlib.sha256(); d = os.path.join(A, 'cenas', pid)
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
for pid in ids:
    c = json.load(open(os.path.join(A, 'cenas', pid, 'cena.json'))); perto, longe = c.get('perto', 0.5), c.get('longe', 8000)
    tr = []
    for k, m in enumerate(c['materiais']):
        if m.get('tipo') == 'agua' or (m.get('alfa') if m.get('alfa') is not None else 1) >= 1: continue
        b = np.fromfile(os.path.join(A, 'cenas', pid, m['arquivo']), np.float32).reshape(-1, 12)[:, :3]; lo, hi = b.min(0), b.max(0)
        tr.append((k, m['nome'], m.get('objeto'), (lo + hi) / 2))
    def ordem(q):
        M = vista(q['camera'], perto, longe); z = []
        for k, nome, obj, cen in tr:
            T = np.array(q['objetos'][obj], float).reshape(4, 4).T if obj and obj in q['objetos'] else np.eye(4)
            z.append(proj(M, (T @ np.r_[cen, 1])[:3][None])[0][0, 2])
        return tuple(z[a] > z[b] for a in range(len(z)) for b in range(a + 1, len(z)))
    Q = c['animacao']['quadros']; o0 = ordem(Q[0]); iguais = []
    for i, q in enumerate(Q):
        if ordem(q) != o0: break
        iguais.append(i)
    # obturador: os sub-quadros dos quadros reaproveitados também precisam manter a ordem
    if pid in OBT and os.path.isdir(os.path.join(A, 'cenas', pid + '_obt')):
        co = json.load(open(os.path.join(A, 'cenas', pid + '_obt', 'cena.json'))); m_ = OBT[pid]['sub']; fx = OBT[pid].get('quadros')
        ok = []
        for i in iguais:
            if fx is None or fx[0] <= i <= fx[1]:
                if any(ordem(co['animacao']['quadros'][i * m_ + j]) != o0 for j in range(m_)): break
            ok.append(i)
        iguais = ok
    d = os.path.join(A, f'quadros_{PERFIL}', pid); man = json.load(open(os.path.join(d, '_manifesto_quadros.json')))
    q = f"cena=/episodio_02_geladeira/episodio/cenas/{pid}/&escala={P['escala']}&{P['consulta']}{CFG['por_plano'].get(pid, '')}"
    assert 'ordemtransp=1' in q, f'{pid}: por_plano sem ordemtransp=1'
    reg = dict(consulta=q, perfil=PERFIL, motor=MOT, cena=hcena(pid))
    if pid in OBT: reg['obturador'] = dict(graus=OBT[pid]['graus'], sub=OBT[pid]['sub'], cena_sub=hcena(pid + '_obt'), **({'quadros': OBT[pid]['quadros']} if 'quadros' in OBT[pid] else {}))
    prova = dict(valida=True, quando=time.strftime('%Y-%m-%dT%H:%M:%S'), motivo='ordem dos transparentes congelada no quadro 0 (ordemtransp=1, rodada 12)',
                 criterio='quadros em que a ordem de todos os pares de malhas com alfa < 1 é a do quadro 0 (a opção não muda nada neles)',
                 transparentes=[f'{n}#{k}' for k, n, _, _ in tr], primeiro_quadro_diferente=len(iguais) if len(iguais) < len(Q) else None,
                 quadros_iguais=iguais, reg_anterior=man['reg'], reg_novo=reg)
    json.dump(prova, open(os.path.join(d, '_prova_reuso_config.json'), 'w'), ensure_ascii=False, indent=1)
    print(pid, f'{len(iguais)} de {len(Q)} quadros reaproveitáveis; primeiro diferente:', prova['primeiro_quadro_diferente'])
