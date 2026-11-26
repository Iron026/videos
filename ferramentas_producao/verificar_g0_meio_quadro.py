"""Verificação preventiva (montagem): cenas cujo g0 cai a MEIO quadro. Com round() do Python (empate → par), esses planos
mostram cada quadro duas vezes (15 qps efetivos). A montagem deve usar floor(x + 0,5) — ver Ep. 02, ARRED_QUADROS.
Uso: python3 verificar_g0_meio_quadro.py <pasta_cenas> [fps=30]"""
import json, sys, os
d = sys.argv[1]; fps = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0; n = 0
for c in sorted(os.listdir(d)):
    p = os.path.join(d, c, 'cena.json')
    if not os.path.exists(p): continue
    g0 = json.load(open(p)).get('g0')
    if g0 is None: continue
    fr = (g0 * fps) % 1
    if abs(fr - 0.5) < 1e-3: print(f'{c}: g0 = {g0} → {g0 * fps:.3f} quadros (meio quadro: EMPATE em todo instante)'); n += 1
print(f'{n} cena(s) com g0 a meio quadro')
