"""Verificação científica do G3 (capilar + lupa) contra o MODELO e a NARRAÇÃO, a partir do que foi EXPORTADO (não do código):
 · marcador do plano principal (manometros2d.json do G3): valor de pressão → s no perfil do capilar; dentro do quadro?
 · lupa (cena G3z): câmera → ponto do canal no centro da lupa e faixa visível; rótulos ativos → estado do fluido ali;
 · palavras da narração (roteiro/palavras.json) × instantes dos eventos (início da evaporação, mistura fria).
Saída: ciencia/verificacao_g3.json  (código 1 se algum critério falhar)"""
import os, json, math, sys
import numpy as np
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(A, '..')
M = json.load(open(os.path.join(A, 'ciclo_modelo.json'))); cap = next(t for t in M['circuito'] if t['id'] == 'capilar')['perfil']
PB, PA = M['pressoes']['baixa_bar'], M['pressoes']['alta_bar']
S = np.array([q['s'] for q in cap]); P = np.array([q['P_bar'] for q in cap]); T = np.array([q['T_C'] for q in cap]); X = np.array([q['x'] for q in cap])
s_flash = float(S[np.argmax(X > 0)])                       # primeiro ponto com vapor no perfil
def em(s, arr): return float(np.interp(min(max(s, 0.0), 1.0), S, arr))
def s_de_p(p): return float(np.interp(-p, -P, S))           # P decresce com s
man = json.load(open(os.path.join(R, 'episodio', 'cenas', 'G3', 'manometros2d.json')))
rz = json.load(open(os.path.join(R, 'episodio', 'cenas', 'G3z', 'rotulos2d.json')))
cz = json.load(open(os.path.join(R, 'episodio', 'cenas', 'G3z', 'cena.json')))
pal = json.load(open(os.path.join(R, 'roteiro', 'palavras.json')))
g0 = man['g0']; fps = man['fps']
def palavra(w, apos):
    return next(p['inicio'] for p in pal if p['palavra'].strip('.,!?').lower() == w and p['inicio'] >= apos)
W = {w: palavra(w, g0 - 0.5) for w in ('pressão', 'cai', 'parte', 'evapora', 'resfriando', 'mistura')}
X0, X1 = -0.30, 0.30; SS = np.linspace(-0.2, 1.2, 2801)   # além das pontas: detecta a lupa mostrando o fim do tubo
fov = cz['camera'].get('fov', 35.0); asp = cz['camera']['largura'] / cz['camera']['altura']
falhas = []; linhas = []
quadros = cz['animacao']['quadros']
for i, q in enumerate(man['quadros']):
    g = g0 + i / fps
    if not q: continue
    nome, u, v, a, val = q[0]
    if a < 0.5: continue
    s = s_de_p(PB + val * (PA - PB))
    # lupa: centro e meia-largura visível (recorte quadrado W×W no centro do quadro)
    cq = quadros[min(i, len(quadros) - 1)]['camera'] if i < len(quadros) else None
    if cq:
        # projeção em perspectiva REAL (a câmera da lupa olha o tubo em diagonal): u, v de cada ponto do eixo do tubo (z do
        # eixo + raio, onde ficam as âncoras dos rótulos); faixa visível = pontos dentro do recorte quadrado central
        pos, f = np.array(cq['pos']), np.array(cq['dir']); f = f / np.linalg.norm(f); rr = np.cross(f, [0, 0, 1]); rr /= np.linalg.norm(rr); up = np.cross(rr, f)
        tt = math.tan(math.radians(fov / 2))
        pts = np.stack([X0 + (X1 - X0) * SS, np.full_like(SS, -1.30), np.full_like(SS, 1.25 + 0.020)], 1) - pos
        zc = pts @ f; uu = 0.5 + (pts @ rr / zc) / (tt * asp) / 2; vv = 0.5 - (pts @ up / zc) / tt / 2
        H_W = cz['camera']['altura'] / cz['camera']['largura']
        dentro = (uu - 0.5) ** 2 + ((vv - 0.5) * H_W) ** 2 < 0.25
        s_ini, s_fim = (float(SS[dentro].min()), float(SS[dentro].max())) if dentro.any() else (float('nan'),) * 2
        alvo = pos + f * ((-1.30 - pos[1]) / f[1]); s_c = (alvo[0] - X0) / (X1 - X0)
        s_em_u = lambda u_: float(SS[np.argmin(np.abs(uu - u_))])
    else: s_c = s_ini = s_fim = float('nan')
    # rótulos VISÍVEIS: ativos e dentro do círculo da lupa (a montagem só desenha esses); s no ponto do rótulo
    H_W = cz['camera']['altura'] / cz['camera']['largura']
    rot = {r[0]: round(s_em_u(r[1]), 3) for r in (rz['quadros'][i] if i < len(rz['quadros']) else [])
           if r[3] >= 0.5 and (r[1] - 0.5) ** 2 + ((r[2] - 0.5) * H_W) ** 2 < 0.25}
    linhas.append(dict(t=round(g, 2), s_marcador=round(s, 3), P_bar=round(em(s, P), 2), T_C=round(em(s, T), 1), x=round(em(s, X), 3),
                       marcador_no_quadro=bool(0 <= u <= 1 and 0 <= v <= 1), lupa_centro_s=round(s_c, 3), lupa_faixa_s=[round(s_ini, 3), round(s_fim, 3)],
                       T_centro_lupa=round(em(min(max(s_c, 0), 1), T), 1), x_centro_lupa=round(em(min(max(s_c, 0), 1), X), 3), rotulos=rot))
# critérios
fora = [l['t'] for l in linhas if not l['marcador_no_quadro']]
if fora: falhas.append(f'marcador fora do quadro em {len(fora)} quadros ({fora[0]}–{fora[-1]} s)')
mono = all(b['s_marcador'] >= a['s_marcador'] - 1e-3 for a, b in zip(linhas, linhas[1:]))
if not mono: falhas.append('o marcador volta no capilar (s não monotônico)')
if any(abs(l['lupa_centro_s'] - min(l['s_marcador'], 0.885)) > 0.01 for l in linhas): falhas.append('centro da lupa diferente do ponto do marcador')
if max(l['lupa_faixa_s'][1] for l in linhas) > 1.005: falhas.append('a lupa passa da ponta do tubo')
for l in linhas:
    r = l['rotulos']
    if 'líquido' in r and em(r['líquido'], X) > 0.0: falhas.append(f"'líquido' aponta fluido com vapor em {l['t']} s (x = {em(r['líquido'], X):.3f})")
    if 'começa a evaporar' in r and abs(r['começa a evaporar'] - s_flash) > 0.02: falhas.append(f"'começa a evaporar' longe do início da evaporação em {l['t']} s (s = {r['começa a evaporar']})")
    if 'mistura fria' in r and em(r['mistura fria'], T) > 0.0: falhas.append(f"'mistura fria' aponta fluido acima de 0 °C em {l['t']} s ({em(r['mistura fria'], T):.1f} °C)")
vis = lambda nome: [l['t'] for l in linhas if nome in l['rotulos']]
res_rot = {n: dict(visivel_s=[vis(n)[0], vis(n)[-1]] if vis(n) else None) for n in ('líquido', 'começa a evaporar', 'mistura fria')}
for n, (arr, k) in {'líquido': (X, 'x'), 'começa a evaporar': (X, 'x'), 'mistura fria': (T, 'T_C')}.items():
    v_ = [em(l['rotulos'][n], arr) for l in linhas if n in l['rotulos']]
    if v_: res_rot[n][k + '_no_ponto'] = [round(min(v_), 3), round(max(v_), 3)]
    else: falhas.append(f"rótulo '{n}' nunca aparece dentro da lupa")
t_flash = next((l['t'] for l in linhas if l['s_marcador'] >= s_flash), None)
t_fim = next((l['t'] for l in linhas if l['s_marcador'] >= 0.999), None)
sinc = dict(palavras=W, marcador_chega_ao_inicio_da_evaporacao=t_flash, atraso_em_relacao_a_evapora_s=round(t_flash - W['evapora'], 2) if t_flash else None,
            marcador_chega_a_saida=t_fim, atraso_em_relacao_a_mistura_s=round(t_fim - W['mistura'], 2) if t_fim else None)
if t_flash is None or not (W['parte'] - 0.3 <= t_flash <= W['evapora'] + 0.6): falhas.append(f'início da evaporação no marcador ({t_flash}) fora da janela "parte … evapora"')
res = dict(modelo=dict(s_inicio_evaporacao=s_flash, entrada=dict(P_bar=round(P[0], 2), T_C=round(T[0], 1), x=X[0]), saida=dict(P_bar=round(P[-1], 3), T_C=round(T[-1], 1), x=X[-1]),
                       entalpia_constante=bool(np.ptp([q['h_kJkg'] for q in cap]) < 0.01)),
           sincronia=sinc, rotulos_lupa=res_rot,
           falhas=falhas, aprovado=not falhas, amostras=linhas[::6])
json.dump(res, open(os.path.join(A, 'verificacao_g3.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'amostras'}, ensure_ascii=False, indent=1)); sys.exit(0 if not falhas else 1)
