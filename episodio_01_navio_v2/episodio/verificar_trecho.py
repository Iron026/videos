"""Verificação quadro a quadro de um trecho re-renderizado: antes × depois (mesmos índices de quadro).
Pontos isolados: pixels > 14 níveis da mediana 3×3. Cintilação: |q[i+1] − 2q[i] + q[i−1]| média e local (máximo em blocos de 20×20 px:
pega piscadas pequenas que a média esconde). Uso: python3 episodio/verificar_trecho.py <dir_antes> <dir_depois> <q0> <q1> <g0> <saida.json>"""
import sys, json, numpy as np
from PIL import Image
from scipy.ndimage import median_filter
da, dd, q0, q1, g0, saida = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
L = lambda d, q: np.asarray(Image.open(f'{d}/q{q:04d}.jpg').convert('L')).astype(np.float32)
P = lambda x: int((np.abs(x - median_filter(x, 3)) > 14).sum())
res, A, B = [], [], []
for q in range(q0, q1 + 1):
    a, b = L(da, q), L(dd, q); A.append(a); B.append(b)
    res.append(dict(q=q, t=round(g0 + q / 30, 3), pontos_antes=P(a), pontos_depois=P(b), px_alterados=int((np.abs(a - b) > 20).sum())))
seg = lambda s, i: np.abs(s[i + 1] - 2 * s[i] + s[i - 1])
H, W = A[0].shape; h, w = H // 20 * 20, W // 20 * 20
loc = lambda s: [float(seg(s, i)[:h, :w].reshape(h // 20, 20, w // 20, 20).mean((1, 3)).max()) for i in range(1, len(s) - 1)]
ca = [float(seg(A, i).mean()) for i in range(1, len(A) - 1)]; cb = [float(seg(B, i).mean()) for i in range(1, len(B) - 1)]; la, lb = loc(A), loc(B)
pa = np.array([r['pontos_antes'] for r in res]); pb = np.array([r['pontos_depois'] for r in res])
r = dict(quadros=len(res), trecho_s=[res[0]['t'], res[-1]['t']], pontos_media=dict(antes=int(pa.mean()), depois=int(pb.mean())),
         quadros_com_menos_pontos=int((pb < pa).sum()), quadros_com_mais_pontos=[x['t'] for x in res if x['pontos_depois'] > x['pontos_antes'] * 1.1 + 20],
         cintilacao_media=dict(antes=round(float(np.mean(ca)), 3), depois=round(float(np.mean(cb)), 3)),
         cintilacao_local_max=dict(antes=round(max(la), 2), depois=round(max(lb), 2)), cintilacao_local_p95=dict(antes=round(float(np.percentile(la, 95)), 2), depois=round(float(np.percentile(lb, 95)), 2)),
         piscadas_locais_novas=[res[i + 1]['t'] for i in range(len(lb)) if lb[i] > la[i] * 1.5 + 2])
json.dump(dict(resumo=r, quadros=res), open(saida, 'w'), ensure_ascii=False, indent=0); print(json.dumps(r, ensure_ascii=False, indent=1))
