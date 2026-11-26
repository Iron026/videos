"""Rodada 9: auditoria rótulo × narração na versão MONTADA (os dados que a montagem realmente usa: rotulos_r9/<plano>.json
quando existe, senão cenas/<plano>/rotulos2d.json). Para cada rótulo da lista de referência (rotulos_x_narracao_r8.json):
instante em que fica visível (opacidade > 0,02) × início da palavra que ele nomeia; "antes da palavra" se entrar mais de
0,25 s antes. Também: âncora dentro do quadro e linha de chamada só com âncora visível.
Uso: python3 auditar_rotulos.py [saida.json]"""
import os, sys, json
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..', 'relatorios')
ref = json.load(open(os.path.join(R, 'rotulos_x_narracao_r8.json'))); out = []
for x in ref:
    p9 = os.path.join(A, 'rotulos_r9', x['plano'] + '.json'); f = p9 if os.path.exists(p9) else os.path.join(A, 'cenas', x['plano'], 'rotulos2d.json')
    r = json.load(open(f)); g0, fps = r['g0'], r['fps']
    vis = [(i, it) for i, q in enumerate(r['quadros']) for it in q if it[0] == x['rotulo'] and it[3] > 0.02]
    ap = round(g0 + vis[0][0] / fps, 2) if vis else None
    fora = sum(1 for _, it in vis if not (0 <= it[1] <= 1 and 0 <= it[2] <= 1))
    linha_fora = sum(1 for _, it in vis if (len(it) < 7 or it[6]) and not (0 <= it[1] <= 1 and 0 <= it[2] <= 1))
    out.append(dict(plano=x['plano'], rotulo=x['rotulo'], palavra=x['palavra'], fala_em=x['fala_em'], aparece=ap, fonte=os.path.relpath(f, A),
                    antes_da_palavra=ap is not None and ap < x['fala_em'] - 0.25, quadros=len(vis), ancora_fora=fora, linha_para_fora=linha_fora))
res = dict(rotulos=len(out), antes_da_palavra=sum(o['antes_da_palavra'] for o in out), com_ancora_fora=sum(o['ancora_fora'] > 0 for o in out),
           linhas_para_fora=sum(o['linha_para_fora'] for o in out), detalhe=out)
print(json.dumps({k: v for k, v in res.items() if k != 'detalhe'}, ensure_ascii=False))
for o in out:
    if o['ancora_fora'] or o['antes_da_palavra']: print('  ', o['plano'], o['rotulo'], 'fora', o['ancora_fora'], 'antes', o['antes_da_palavra'])
json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(R, 'rotulos_x_narracao_v9.json'), 'w'), ensure_ascii=False, indent=1)
