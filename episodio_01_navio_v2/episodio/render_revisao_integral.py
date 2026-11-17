"""Render de REVISÃO integral (540×960, GTAO 4, sem MSAA, 30 fps reais), segmento por segmento, renderizando só os quadros
que ainda não existem em quadros_revisao/ (aproveita os testes de validação). Retomável.
Uso: python3 episodio/render_revisao_integral.py [segmentos...]"""
import os, sys, json, subprocess, time

A = os.path.dirname(os.path.abspath(__file__)); MOTOR = os.path.join(A, '..', 'motores', 'tempo_real_v2')
SEGS = sys.argv[1:] or ['02', '03', '04', '05', '0607', '0607b', '08a', '08b', '09', '10', '11', '12x', '12', '13']
Q = 'escala=0.5&aoamostras=4&msaa=0'
t0 = time.time(); total = 0
for s in SEGS:
    n = len(json.load(open(os.path.join(A, 'cenas', f's{s}', 'cena.json')))['animacao']['quadros'])
    d = os.path.join(A, 'quadros_revisao', f's{s}'); os.makedirs(d, exist_ok=True)
    tem = {int(f[1:5]) for f in os.listdir(d) if f.endswith('.jpg')}
    faltam = [i for i in range(n) if i not in tem]
    faixas = []
    for i in faltam:
        if faixas and i == faixas[-1][1] + 1: faixas[-1][1] = i
        else: faixas.append([i, i])
    for a, b in faixas:
        r = subprocess.run(['node', 'render_anim.mjs', f'cena=../../episodio/cenas/s{s}/&{Q}', f'../../episodio/quadros_revisao/s{s}', '1', str(a), str(b)],
                           cwd=MOTOR, capture_output=True, text=True)
        print(s, a, b, [l for l in r.stdout.splitlines() if 'FIM' in l or 'rror' in l][-1:], flush=True)
    total += len(faltam)
    print(f'SEG {s}: {n} quadros ({len(faltam)} novos) · {time.time() - t0:.0f} s acumulados', flush=True)
print(f'FIM_REVISAO {total} quadros novos em {time.time() - t0:.0f} s')
