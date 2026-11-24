"""Rodada 10: análise do teste CONTÍNUO do C4 em 1080 (q120–184) com o obturador de 180° só em 126–178.
 · estabilidade dos arames: pixels que vão e voltam (|Δ| > 30, sinais opostos) por quadro, na faixa da grade (x > 85 %
   da largura) e no quadro todo; obturador (R10) × sem obturador (rodada 9, mesmos quadros 155–184);
 · legibilidade do evaporador: nitidez (gradiente médio) na caixa do evaporador projetada, R10 ÷ R9 (1 = igual);
 · continuidade nas bordas da faixa (125→126 e 178→179): salto de imagem comparado aos saltos vizinhos;
 · z-fighting: alternância sensível (|Δ| > 12) em blocos 16×16, contando só blocos que alternam em ≥ 3 trios seguidos;
 · transição C4 → D1: último quadro do C4 × primeiros do D1 (mesma coluna do evaporador).
Uso: python3 analisar_c4_1080_r10.py → relatorios/testes_r10/c4_1080_obturador.json + folhas em relatorios/comparativos_r10/"""
import os, json
import numpy as np
from PIL import Image
A = os.path.dirname(os.path.abspath(__file__)); N10 = os.path.join(A, 'quadros_final_r10', 'C4'); N9 = os.path.join(A, 'quadros_final_r9v', 'C4')
OUTC = os.path.join(A, '..', 'relatorios', 'comparativos_r10'); os.makedirs(OUTC, exist_ok=True)
L = lambda d, k: np.asarray(Image.open(os.path.join(d, f'q{k:04d}.jpg')).convert('L'), np.float32)
def alterna(d, k, lim=30, x0=0.0):
    a, b, c = L(d, k - 1), L(d, k), L(d, k + 1); d1, d2 = b - a, c - b; m = (np.abs(d1) > lim) & (np.abs(d2) > lim) & (np.sign(d1) != np.sign(d2))
    return m[:, int(x0 * m.shape[1]):]
res = dict(grade_px_alternando={}, todo_px_alternando={})
for nome, d, ks in (('r10_obturador', N10, range(156, 184)), ('r9_sem_obturador', N9, range(156, 184))):
    g = [int(alterna(d, k, x0=0.85).sum()) for k in ks]; t = [int(alterna(d, k).sum()) for k in ks]
    res['grade_px_alternando'][nome] = dict(total=sum(g), pior=max(g), por_quadro=g); res['todo_px_alternando'][nome] = dict(total=sum(t), pior=max(t))
# nitidez do evaporador (caixa fixa no terço superior, onde ele está no fim do C4) — R10 ÷ R9
def grad(a): return float(np.abs(np.diff(a, axis=0)).mean() + np.abs(np.diff(a, axis=1)).mean())
cx = (slice(int(0.12 * 1920), int(0.50 * 1920)), slice(0, int(0.95 * 1080)))
res['nitidez_evaporador_r10_sobre_r9'] = {k: round(grad(L(N10, k)[cx]) / grad(L(N9, k)[cx]), 3) for k in (156, 160, 165, 170, 175, 178, 179, 184)}
# continuidade nas bordas da faixa
salto = lambda k: float(np.abs(L(N10, k) - L(N10, k - 1)).mean())
res['salto_medio_por_quadro'] = {k: round(salto(k), 2) for k in range(121, 185)}
res['bordas_da_faixa'] = {'125→126': dict(salto=round(salto(126), 2), vizinhos=[round(salto(125), 2), round(salto(127), 2)]),
                          '178→179': dict(salto=round(salto(179), 2), vizinhos=[round(salto(178), 2), round(salto(180), 2)])}
# z-fighting: blocos que alternam (sensível) em >= 3 trios seguidos
def blocos(d, k):
    m = alterna(d, k, 12); H, W = m.shape; return m[:H // 16 * 16, :W // 16 * 16].reshape(H // 16, 16, W // 16, 16).mean((1, 3)) >= 0.25
seq = None; pers = 0
for k in range(121, 184):
    b = blocos(N10, k); seq = (seq + 1) * b if seq is not None else b.astype(int); pers = max(pers, int((seq >= 3).sum()))
res['zfighting_blocos_persistentes_max'] = pers
# folhas: 1) bordas da faixa e meio da aproximação, R9 × R10 ; 2) transição C4 → D1
def folha(pares, nome):
    ims = [Image.open(p).convert('RGB').resize((360, 640)) for p in pares]; s = Image.new('RGB', (360 * len(ims), 640))
    [s.paste(im, (i * 360, 0)) for i, im in enumerate(ims)]; s.save(os.path.join(OUTC, nome), quality=90)
folha([os.path.join(N9, 'q0160.jpg'), os.path.join(N10, 'q0160.jpg'), os.path.join(N9, 'q0170.jpg'), os.path.join(N10, 'q0170.jpg')], 'c4_1080_r9_x_r10_q160_q170.jpg')
folha([os.path.join(N10, f'q{k:04d}.jpg') for k in (125, 126, 178, 179)], 'c4_1080_bordas_da_faixa.jpg')
D1 = os.path.join(A, 'quadros_final_r10', 'D1')
if os.path.isdir(D1): folha([os.path.join(N10, 'q0184.jpg')] + [os.path.join(D1, f'q{k:04d}.jpg') for k in (0, 4, 9)], 'c4_d1_1080.jpg')
json.dump(res, open(os.path.join(A, '..', 'relatorios', 'testes_r10', 'c4_1080_obturador.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'salto_medio_por_quadro'}, ensure_ascii=False)[:1500])
