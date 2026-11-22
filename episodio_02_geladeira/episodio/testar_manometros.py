"""Rodada 7: teste dos manômetros em TODOS os quadros dos planos que os têm, compostos em 1080 × 1920 com a montagem real
(rótulos, legendas, avisos, lupa), nas duas versões: atual (aprovada) e MANOMETRO_LEGIVEL. Mede, por quadro:
 · texto cortado pela borda do quadro · texto dentro/encostando no anel (versão atual) · sobreposição de texto/mostrador com
   legenda, avisos, rótulos, lupa ou o outro manômetro · linha de ligação passando sobre texto · ponteiro idêntico nas duas
   versões (o valor vem do mesmo manometros2d.json: a ciência não pode mudar).
Uso: python3 testar_manometros.py [passo]  → relatorios/teste_manometros.json"""
import os, sys, json, math
sys.argv = [sys.argv[0], 'final'] + sys.argv[1:2]; os.environ['CAIXAS_EP02'] = '1'
A = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, A)
import montar_ep02 as M
M.pasta = lambda pid: os.path.join(A, 'quadros_animatic', pid)      # fundo da prévia ampliado; camadas desenhadas em 1080
PASSO = int(sys.argv[2]) if len(sys.argv) > 2 else 2
PLANOS = {'C4', 'D2', 'E3', 'G3', 'H2'}
def inter(a, b, folga=0.0):
    return not (a[2] + folga <= b[0] or b[2] + folga <= a[0] or a[3] + folga <= b[1] or b[3] + folga <= a[1])
def seg_caixa(p, q, c):
    for k in range(41):
        t = k / 40; x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        if c[0] < x < c[2] and c[1] < y < c[3]: return True
    return False
def caixa_no_circulo(c, cx, cy, r):
    return all((x - cx) ** 2 + (y - cy) ** 2 <= r * r for x in (c[0], c[2]) for y in (c[1], c[3]))
def circ_inter(c, box):
    cx, cy, r = (c[0] + c[2]) / 2, (c[1] + c[3]) / 2, (c[2] - c[0]) / 2
    nx, ny = min(max(cx, box[0]), box[2]), min(max(cy, box[1]), box[3]); return (nx - cx) ** 2 + (ny - cy) ** 2 < r * r
res = {}
for modo in (False, True):
    M.MAN_LEG = modo; chave = 'proposta' if modo else 'atual'; R = res[chave] = dict(quadros=0, problemas={}, ponteiros={}, alturas_texto_px=set())
    for p in M.PLANOS:
        if p['id'] not in PLANOS: continue
        for i in range(int(round(p['t0'] * 30)), int(round(p['t1'] * 30)), PASSO):
            g = i / 30
            if not any(m[3] > 0.5 for m in M.dados(p['id'], 'manometros2d.json', g)): continue
            M.CAIXAS.clear(); M.compor(g); C = list(M.CAIXAS); R['quadros'] += 1
            def prob(tipo, det): R['problemas'].setdefault(tipo, []).append(f"{p['id']} {g:.2f}s: {det}")
            textos = [c for c in C if c[0] in ('texto_man', 'texto_man_interno')]; most = {c[1]: c[2] for c in C if c[0] == 'mostrador'}
            for (t, n, c) in textos:
                R['alturas_texto_px'].add(round(c[3] - c[1]))
                if c[0] < 2 or c[1] < 2 or c[2] > M.W - 2 or c[3] > M.H - 2: prob('texto cortado pela borda', n)
                if t == 'texto_man_interno':
                    m = most[n.split(':')[0]]; cx, cy, r = (m[0] + m[2]) / 2, (m[1] + m[3]) / 2, (m[2] - m[0]) / 2 - 5 * M.ESC
                    if not caixa_no_circulo(c, cx, cy, r): prob('texto encosta ou sai do anel', n)
                else:
                    for nm, m in most.items():
                        if circ_inter(m, c): prob('texto sobre um mostrador', f'{n} × {nm}')
                for (t2, n2, c2) in C:
                    if t2 in ('legenda', 'aviso', 'rotulo') and inter(c, c2): prob(f'texto do manômetro × {t2}', f'{n} × {n2}')
                    if t2 == 'lupa' and circ_inter(c2, c): prob('texto do manômetro × lupa', n)
                    if t2 in ('ligacao_man', 'ligacao_lupa', 'ligacao_rotulo') and seg_caixa(c2[:2], c2[2:], c) and not (t2 == 'ligacao_man' and n2 == n.split(':')[0] and t == 'texto_man_interno'):
                        prob('linha sobre texto', f'{t2} {n2} × {n}')
                for (t3, n3, c3) in textos:
                    if n3 != n and n3.split(':')[0] != n.split(':')[0] and inter(c, c3): prob('texto × texto do outro manômetro', f'{n} × {n3}')
            for nm, m in most.items():
                for (t2, n2, c2) in C:
                    if t2 in ('legenda', 'aviso', 'rotulo') and circ_inter(m, c2): prob(f'mostrador × {t2}', f'{nm} × {n2}')
                    if t2 == 'lupa' and inter(m, c2) and math.hypot((m[0] + m[2] - c2[0] - c2[2]) / 2, (m[1] + m[3] - c2[1] - c2[3]) / 2) < (m[2] - m[0] + c2[2] - c2[0]) / 2: prob('mostrador × lupa', nm)
                for nm2, m2 in most.items():
                    if nm2 > nm and circ_inter(m, m2): prob('mostrador × mostrador', f'{nm} × {nm2}')
            for (t, n, c) in C:
                if t == 'ponteiro': R['ponteiros'][f"{p['id']}:{n}:{g:.3f}"] = round(c[1], 4)
    R['alturas_texto_px'] = sorted(R['alturas_texto_px'])
    R['resumo'] = {k: len(v) for k, v in R['problemas'].items()}
    R['problemas'] = {k: v[:6] + ([f'… +{len(v) - 6}'] if len(v) > 6 else []) for k, v in R['problemas'].items()}
pa, pp = res['atual'].pop('ponteiros'), res['proposta'].pop('ponteiros')
res['ponteiros_identicos'] = dict(comparados=len(pa), iguais=sum(1 for k in pa if pp.get(k) == pa[k]))
json.dump(res, open(os.path.join(A, '..', 'relatorios', 'teste_manometros.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: (v['quadros'], v['resumo'], v['alturas_texto_px']) if isinstance(v, dict) and 'resumo' in v else v for k, v in res.items()}, ensure_ascii=False, indent=1))
