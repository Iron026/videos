"""Rodada 9: teste da COMPOSIÇÃO (legendas, rótulos, cartões de pressão, avisos, lupa) em TODOS os quadros (ou a cada
`passo`), composta em 1080 × 1920 com a montagem real (COMPOSICAO_R9=1) sobre o fundo da revisão ampliado. Mede, por quadro:
 · sobreposições entre legenda, rótulos, cartões, avisos e lupa (e entre rótulos);
 · caixas cortadas pela borda; linha de ligação passando sobre texto;
 · elementos dentro das zonas de interface (topo 250 px, base 340 px, coluna direita 120 px abaixo de 40 %);
 · ponteiros: valor desenhado = valor de manometros2d.json e ângulo = 180 + 180·valor (a física não muda);
 · legenda sobre o rosto do personagem.
Uso: python3 testar_composicao_r9.py [passo] → relatorios/teste_composicao_r9.json"""
import os, sys, json, collections
PASSO = int(sys.argv[1]) if len(sys.argv) > 1 else 2
sys.argv = [sys.argv[0], 'final']; os.environ['CAIXAS_EP02'] = '1'; os.environ['COMPOSICAO_R9'] = '1'
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A)
import montar_ep02 as M
M.pasta = lambda pid: os.path.join(A, 'quadros_revisao', pid)      # fundo da revisão ampliado; camadas desenhadas em 1080
W, H = M.W, M.H; Z = M.ZONA
def inter(a, b, f=0.0): return not (a[2] + f <= b[0] or b[2] + f <= a[0] or a[3] + f <= b[1] or b[3] + f <= a[1])
def seg(p, q, c):
    for k in range(41):
        t = k / 40; x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        if c[0] + 2 < x < c[2] - 2 and c[1] + 2 < y < c[3] - 2: return True
    return False
prob = collections.defaultdict(list); n = 0; ponteiros = [0, 0]
TEXTO = ('legenda', 'rotulo', 'mostrador', 'aviso', 'lupa', 'aviso_lupa')
for i in range(0, int(round(M.DUR * M.FPS)), PASSO):
    g = i / M.FPS; M.CAIXAS.clear(); M.compor(g); n += 1; cx = list(M.CAIXAS); tag = f'{g:.2f}s'
    caixas = [(t, nm, b) for (t, nm, b) in cx if t in TEXTO]
    for a in range(len(caixas)):
        for b in range(a + 1, len(caixas)):
            (ta, na, ba), (tb, nb, bb) = caixas[a], caixas[b]
            if ta == 'lupa' and tb == 'rotulo' or tb == 'lupa' and ta == 'rotulo': continue   # rótulos do canal ficam DENTRO da lupa
            if ta == tb == 'aviso' or {ta, tb} == {'lupa', 'aviso_lupa'}: continue   # o selo da lupa fica de propósito sobre o anel
            if ta == 'lupa' or tb == 'lupa':
                c = ba if ta == 'lupa' else bb; o = bb if ta == 'lupa' else ba; r = (c[2] - c[0]) / 2; ccx, ccy = c[0] + r, c[1] + r
                nx, ny = min(max(ccx, o[0]), o[2]), min(max(ccy, o[1]), o[3])
                if (nx - ccx) ** 2 + (ny - ccy) ** 2 < r * r: prob[f'{ta} × {tb}'].append(f'{tag} {na}|{nb}')
                continue
            if inter(ba, bb): prob[f'{ta} × {tb}'].append(f'{tag} {na}|{nb}')
    for (t, nm, b) in caixas:
        if t == 'lupa': continue
        if b[0] < 0 or b[1] < 0 or b[2] > W or b[3] > H: prob['cortado na borda'].append(f'{tag} {t}:{nm}')
        if b[1] < Z['topo'] - 1: prob['zona superior'].append(f'{tag} {t}:{nm}')
        if b[3] > H - Z['base'] + 1: prob['zona inferior'].append(f'{tag} {t}:{nm}')
        if b[2] > W - Z['direita'] + 1 and b[3] > Z['direita_desde'] * H: prob['coluna direita'].append(f'{tag} {t}:{nm}')
    for (t, nm, l) in cx:
        if t in ('ligacao_rotulo_trecho', 'ligacao_man_trecho', 'ligacao_lupa_trecho') or (t in ('ligacao_rotulo', 'ligacao_man', 'ligacao_lupa') and not any(x[0] == t + '_trecho' and x[1] == nm for x in cx)):   # R9: trechos realmente desenhados
            for (t2, nm2, b) in caixas:
                if t2 in ('legenda', 'aviso') or (t2 == 'rotulo' and nm2 != nm and t.startswith('ligacao_rotulo')) or (t2 == 'mostrador' and nm2 != nm and t.startswith('ligacao_man')):
                    if seg(l[:2], l[2:4], b): prob['linha sobre texto'].append(f'{tag} {t}:{nm} × {t2}:{nm2}')
    vivos = [p['id'] for p in M.PLANOS if p['t0'] - 0.3 <= g < p['t1'] + 0.3]   # inclui o plano que sai na fusão
    for (t, nm, l) in cx:
        if t == 'ponteiro':
            ponteiros[0] += 1
            ok = any(abs(l[0] - val) < 1e-9 for pid in vivos for (n_, u, v, a, val) in M.dados(pid, 'manometros2d.json', g) if n_ == nm) and abs(l[1] - (180 + 180 * max(0.0, min(1.0, l[0])))) < 1e-9
            ponteiros[1] += ok
            if not ok: prob['ponteiro diferente do modelo'].append(f'{tag} {nm}')
    leg = [b for (t, nm, b) in caixas if t == 'legenda']
    for pid in vivos:
        r = M.rosto(pid, g)
        if r and any(inter(b, r) for b in leg): prob['legenda sobre o rosto'].append(f'{tag} {pid}')
    if i % 300 == 0: print(f'{g:7.2f} s', {k: len(v) for k, v in prob.items()}, flush=True)
res = dict(quadros_testados=n, passo=PASSO, ponteiros=dict(desenhados=ponteiros[0], iguais_ao_modelo=ponteiros[1]),
           resumo={k: len(v) for k, v in prob.items()}, exemplos={k: v[:12] for k, v in prob.items()})
json.dump(res, open(os.path.join(A, '..', 'relatorios', 'teste_composicao_r9.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'exemplos'}, ensure_ascii=False))
