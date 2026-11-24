"""Rodada 11: verificação da transição aprovada (Opção C, empurrão lateral de 0,3 s com desfoque de 180°) no A4, 5,737 s.
Roda NA COMPOSIÇÃO (montar_ep02.py importado), sem render 3D. Uso:
  python3 verificar_transicao_a4.py <perfil> transicao   → medidas da janela (fluidez, procedência dos pixels, rastro, bordas)
  python3 verificar_transicao_a4.py <perfil> hashes t0 t1 <saida.json>   → SHA-256 de cada quadro composto (para provar
      que fora da janela a composição é idêntica ao corte seco; rodar com TRANSICAO_A4_INTERNA=corte e =empurrao)"""
import os, sys, json, hashlib
import numpy as np
PERFIL, MODO = sys.argv[1], sys.argv[2]; ARGS = sys.argv[3:]
sys.argv = ['montar_ep02.py', PERFIL, '/dev/null']; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar_ep02 as M
from scipy.ndimage import uniform_filter1d
FPS, W, H, TC = M.FPS, M.W, M.H, M.TC_A4I

if MODO == 'hashes':
    t0, t1, saida = float(ARGS[0]), float(ARGS[1]), ARGS[2]; out = {}
    for i in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        out[i] = hashlib.sha256(np.asarray(M.compor(i / FPS)).tobytes()).hexdigest()
    json.dump(dict(perfil=PERFIL, transicao=M.TRANS_A4I, quadros=out), open(saida, 'w')); print('ok', len(out), 'quadros'); sys.exit()

assert M.TRANS_A4I == 'empurrao'
meia = 0.15; janela = [i for i in range(int(TC * FPS) - 8, int(TC * FPS) + 9)]
res = dict(perfil=PERFIL, W=W, H=H, instante_corte_s=round(TC, 4), duracao_s=2 * meia, quadros=[])
cinza = lambda im: np.asarray(im, np.float32).mean(2)
alvo_it = {}; prev_dx = None
for i in janela:
    g = i / FPS; dentro = abs(g - TC) < meia
    q = M.quadro_simples('A4', g)          # imagem 3D da composição (antes das camadas 2D)
    r = dict(quadro=i, t=round(g, 4), na_transicao=bool(dentro))
    if dentro:
        u = (g - (TC - meia)) / (2 * meia); p = u * u * (3 - 2 * u); dx = int(W * p); v = abs(6 * u * (1 - u)) * W / (2 * meia * FPS); n = int(v * 0.5)
        ro, it = M._ponte('rosto', g), M._ponte('interior', g)
        cru = np.zeros((H, W, 3), np.float32); cru[:, :W - dx] = np.asarray(ro, np.float32)[:, dx:]; cru[:, W - dx:] = np.asarray(it, np.float32)[:, :dx]
        esperado = uniform_filter1d(cru, size=n, axis=1, mode='nearest').clip(0, 255).astype(np.uint8) if n >= 2 else cru.astype(np.uint8)
        a = np.asarray(q)
        # procedência: a imagem composta é EXATAMENTE o empurrão das duas imagens + desfoque horizontal (sem transparência entre elas)
        r['igual_ao_empurrao_puro'] = bool(np.array_equal(a, esperado))
        # faixa onde há pixels das DUAS imagens (só o desfoque atravessando a emenda): largura em px e % da largura
        r['faixa_mistura_px'] = int(n) if n >= 2 else 0; r['faixa_mistura_pct_largura'] = round(100 * (n if n >= 2 else 0) / W, 2)
        r['emenda_x'] = W - dx; r['deslocamento_desde_quadro_anterior_px'] = (dx - prev_dx) if prev_dx is not None else dx
        r['rastro_px'] = int(n); r['rastro_sobre_deslocamento'] = round(n / max(1, v), 3); prev_dx = dx
        # posição MEDIDA do interior (correlação dos perfis de coluna) × posição teórica da emenda: o desfoque centrado não desloca
        perfil_q = cinza(q)[H // 4: 3 * H // 4].mean(0); perfil_it = cinza(it)[H // 4: 3 * H // 4].mean(0)
        if dx > W * 0.15:
            seg = perfil_it[: dx - n] - perfil_it[: dx - n].mean(); best = None
            for s in range(-60, 61):
                x0 = W - dx + s
                if x0 < 0 or x0 + len(seg) > W: continue
                b = perfil_q[x0: x0 + len(seg)] - perfil_q[x0: x0 + len(seg)].mean(); c = float((seg * b).sum() / (np.linalg.norm(seg) * np.linalg.norm(b) + 1e-9))
                if best is None or c > best[1]: best = (s, c)
            r['erro_posicao_interior_px'] = best[0]; r['correlacao'] = round(best[1], 3)
    else:
        prev_dx = 0 if g < TC else None
        base = M._quadro_simples('A4', g); r['identico_ao_corte'] = bool(np.array_equal(np.asarray(q), np.asarray(base)))
    res['quadros'].append(r)
# continuidade nas junções com os quadros-ponte (render separado): diferença média entre quadros vizinhos de cada sequência
def seq(lado, f0, f1):
    out = []
    for f in range(f0, f1 + 1):
        g = M.meta('A4') + f / FPS; out.append(cinza(M._ponte(lado, g)))
    return [round(float(np.abs(out[k] - out[k - 1]).mean()), 2) for k in range(1, len(out))]
res['continuidade_rosto_q30_a_q40'] = dict(saltos=seq('rosto', 30, 40), nota='q≤33 = A4 aprovado; q≥34 = quadro-ponte (rosto continuado). Junção = 4º valor (q33→q34)')
res['continuidade_interior_q27_a_q37'] = dict(saltos=seq('interior', 27, 37), nota='q≤33 = quadro-ponte (interior antes do corte); q≥34 = A4 aprovado. Junção = 7º valor (q33→q34)')
json.dump(res, open(os.path.join(M.A, '..', 'relatorios', 'testes_r10', f'transicao_a4_c_{PERFIL}.json'), 'w'), ensure_ascii=False, indent=1)
for r in res['quadros']: print(r)
print('rosto', res['continuidade_rosto_q30_a_q40']['saltos']); print('interior', res['continuidade_interior_q27_a_q37']['saltos'])
