"""Verificação quadro a quadro do segmento s12 (137,0–154,6 s): antes (quadros_revisao_antes7/s12) × depois (quadros_s12_novo).
Pontos isolados: pixels que diferem > 14 níveis da mediana 3×3 vizinha (o padrão do mar vazando é feito disso).
Cintilação: |q[i+1] − 2q[i] + q[i−1]| médio (mudança que vai e volta entre quadros). Saída: validacao_s12_quadros.json"""
import os, sys, json, numpy as np
from PIL import Image
from scipy.ndimage import median_filter
A = os.path.dirname(os.path.abspath(__file__)); D0, D1 = os.path.join(A, 'quadros_revisao_antes7', 's12'), os.path.join(A, sys.argv[1] if len(sys.argv) > 1 else 'quadros_s12_novo')
n = len([f for f in os.listdir(D1) if f.endswith('.jpg')]); g0 = 137.0
ld = lambda d, i: np.asarray(Image.open(os.path.join(d, f'q{i:04d}.jpg')).convert('L')).astype(np.float32)
def pontos(x): return int((np.abs(x - median_filter(x, 3)) > 14).sum())
res = []; prev = {0: [], 1: []}
for i in range(n):
    a, b = ld(D0, i), ld(D1, i); r = dict(q=i, t=round(g0 + i / 30, 3), pontos_antes=pontos(a), pontos_depois=pontos(b), dif_media=round(float(np.abs(a - b).mean()), 2))
    for k, x in ((0, a), (1, b)):
        prev[k].append(x); prev[k] = prev[k][-3:]
        if len(prev[k]) == 3: r['cintil_' + ('antes' if k == 0 else 'depois')] = round(float(np.abs(prev[k][2] - 2 * prev[k][1] + prev[k][0]).mean()), 3)
    res.append(r)
pa = np.array([r['pontos_antes'] for r in res]); pd = np.array([r['pontos_depois'] for r in res])
ca = np.array([r.get('cintil_antes', 0) for r in res[2:]]); cd = np.array([r.get('cintil_depois', 0) for r in res[2:]])
resumo = dict(quadros=n, pontos_isolados_media=dict(antes=round(float(pa.mean())), depois=round(float(pd.mean()))), pontos_isolados_max=dict(antes=int(pa.max()), depois=int(pd.max())),
              quadros_com_menos_pontos=int((pd < pa).sum()), quadros_com_mais_pontos_que_antes=[r['t'] for r in res if r['pontos_depois'] > r['pontos_antes'] * 1.1 + 20],
              cintilacao_media=dict(antes=round(float(ca.mean()), 3), depois=round(float(cd.mean()), 3)), cintilacao_p99=dict(antes=round(float(np.percentile(ca, 99)), 3), depois=round(float(np.percentile(cd, 99)), 3)),
              dif_media_max=max(r['dif_media'] for r in res))
json.dump(dict(resumo=resumo, quadros=res), open(os.path.join(A, 'validacao_s12_quadros.json'), 'w'), ensure_ascii=False, indent=0)
print(json.dumps(resumo, ensure_ascii=False, indent=1))
