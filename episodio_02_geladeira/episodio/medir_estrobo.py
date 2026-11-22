"""Risco de estroboscopia da grade de arames do condensador (medido, não assistido): para cada quadro de um plano, projeta os
arames reais (mesma geometria de geladeira.condensador_arames) com a câmera EXPORTADA e mede, em 1080 px:
 · passo: distância na tela entre arames vizinhos;  · deslocamento: quanto cada arame anda até o quadro seguinte.
razão = deslocamento / passo. Com razão ≥ 0,5 o olho não distingue o sentido do movimento (efeito roda-de-carroça);
abaixo de ~0,3 o movimento é lido sem ambiguidade. Uso: python3 medir_estrobo.py <pasta_cena> [rótulo]"""
import sys, json, math
import numpy as np
c = json.load(open(sys.argv[1].rstrip('/') + '/cena.json')); W, H = 1080, 1920
COND_Y = 0.345; xs = [-0.250 + 0.025 * i for i in range(21)]                   # = geladeira.condensador_arames (25 mm)
def proj(cam, p):
    pos, d, up = np.array(cam['pos']), np.array(cam['dir']), np.array(cam['up']); d = d / np.linalg.norm(d)
    r = np.cross(d, up); r /= np.linalg.norm(r); u = np.cross(r, d); v = np.array(p) - pos; z = v @ d
    t = math.tan(math.radians(cam['fov'] / 2)); return (0.5 + (v @ r) / z / (t * W / H) / 2) * W, (0.5 - (v @ u) / z / t / 2) * H, z
Q = c['animacao']['quadros']; g0 = c['g0']; linhas = []
for i in range(len(Q) - 1):
    a, b = Q[i]['camera'], Q[i + 1]['camera']; rs = []
    for z in (0.7, 1.0, 1.3):
        P0 = [proj(a, (x, COND_Y, z)) for x in xs]; P1 = [proj(b, (x, COND_Y, z)) for x in xs]
        for k in range(1, len(xs) - 1):
            x0, y0, zz = P0[k]
            if zz <= 0 or not (0 <= x0 < W and 0 <= y0 < H): continue
            passo = abs(P0[k + 1][0] - P0[k - 1][0]) / 2; desl = abs(P1[k][0] - x0)
            if passo > 0.5: rs.append((desl / passo, desl, passo))
    if rs:
        r = max(rs); linhas.append(dict(t=round(g0 + i / 30, 3), razao_max=round(r[0], 2), desloc_px=round(r[1], 1), passo_px=round(r[2], 1)))
rot = sys.argv[2] if len(sys.argv) > 2 else ''
ris = [l for l in linhas if l['razao_max'] >= 0.5]
print(json.dumps(dict(cena=rot, quadros_com_grade=len(linhas), razao_max=max((l['razao_max'] for l in linhas), default=0),
                      quadros_razao_maior_0_5=len(ris), trecho_risco=[ris[0]['t'], ris[-1]['t']] if ris else None,
                      quadros_razao_maior_0_3=sum(1 for l in linhas if l['razao_max'] >= 0.3)), ensure_ascii=False))
json.dump(linhas, open(f'/tmp/claude-0/-home-user-videos/fc269869-cbe6-57c4-9d94-8aed391cf2cc/scratchpad/estrobo_{rot}.json', 'w'))
